import unicodedata
import re
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

DEFAULT_PREAMBLE_KEYWORDS = [
    "préambule", "preambule",
    "introduction",
    "objectifs"
]

def strip_last_lines(text: str, n: int = 1) -> str:
    """Supprime les n dernières lignes non vides d'un texte.

    Les lignes vides en fin de texte sont ignorées avant le décompte.

    Args:
        text (str): Texte d'entrée à traiter
        n (int, optional): Nombre de lignes à supprimer. Defaults to 1.

    Returns:
        str: Texte avec les n dernières lignes supprimées
    """
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    for _ in range(n):
        if lines:
            lines.pop()
    return "\n".join(lines)

def normalize_text(text: str) -> str:
    """Normalise un texte pour l'analyse.

        Effectue les opérations suivantes:
        - Mise en minuscules
        - Normalisation Unicode (NFD)
        - Suppression des diacritiques

        Args:
            text (str): Texte à normaliser

        Returns:
            str: Texte normalisé
    """
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text

def clean_line_for_toc_detection(line: str) -> str:
    """Nettoie une ligne pour la détection de table des matières.

        Args:
            line (str): Ligne à nettoyer

        Returns:
            str: Ligne nettoyée (espaces normalisés, caractères spéciaux supprimés)
    """
    clean = line.replace("\xa0", " ")
    clean = re.sub(r"[ \t]+", " ", clean)
    return clean.strip()

def is_toc_line(line: str) -> bool:
    """Détermine si une ligne fait partie d'une table des matières.

        Args:
            line (str): Ligne à analyser

        Returns:
            bool: True si la ligne correspond au motif d'une entrée de table des matières

        Note:
            Une ligne est considérée comme faisant partie d'une table des matières si:
            - Elle contient des numéros en fin de ligne
            - Elle contient des points de suite (...)
    """
    clean = clean_line_for_toc_detection(line)
    if not re.search(r"\d{1,4}\s*$", clean):
        return False
    if not re.search(r"\.{3,}", clean):
        return False
    return True

def is_toc_page(text: str) -> bool:
    """Détecte si une page est une table des matières.

        Args:
            text (str): Texte de la page à analyser

        Returns:
            bool: True si la page est identifiée comme une table des matières

        Note:
            La détection se base sur:
            - La présence du mot "sommaire"
            - Au moins deux lignes correspondant au motif de table des matières
    """
    norm = normalize_text(text)
    if "sommaire" in norm:
        return True
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return False
    toc_line_count = 0
    for line in lines:
        if is_toc_line(line):
            toc_line_count += 1
    return toc_line_count >= 2

def extract_after_preamble(text: str, keywords=None) -> str:
    """Extrait le texte après le premier mot-clé significatif trouvé.

    Ignore les occurrences qui sont dans une table des matières et supprime
    les dernières lignes non vides.

    Args:
        text (str): Texte complet à analyser
        keywords (list, optional): Liste de mots-clés à rechercher.
            Defaults to DEFAULT_PREAMBLE_KEYWORDS.

    Returns:
        str: Texte extrait à partir du premier mot-clé valide trouvé
    """
    if keywords is None:
        keywords = DEFAULT_PREAMBLE_KEYWORDS

    norm_text = normalize_text(text)
    escaped = [re.escape(normalize_text(k)) for k in keywords]
    pattern = re.compile(r"\b(" + "|".join(escaped) + r")\b")

    extracted = None
    for match in pattern.finditer(norm_text):
        keyword_norm = match.group(1)
        candidate_line = None
        for line in text.splitlines(keepends=True):
            if normalize_text(keyword_norm) in normalize_text(line):
                if is_toc_line(line):
                    continue
                candidate_line = line
                break

        if not candidate_line:
            continue

        lowered_text = text.lower()
        lowered_line = candidate_line.lower()
        idx = lowered_text.find(lowered_line)
        if idx != -1:
            original_window = text[idx: idx + len(candidate_line)]
            norm_line = normalize_text(original_window)
            pos_in_line = norm_line.find(keyword_norm)
            if pos_in_line != -1:
                extracted = text[idx + pos_in_line:]
            else:
                extracted = text[idx:]
        else:
            for i in range(len(text)):
                window = text[i : i + 100]
                if keyword_norm in normalize_text(window):
                    extracted = text[i:]
        if extracted:
            break

    if not extracted:
        extracted = text

    return strip_last_lines(extracted, 1)

def detect_preamble_page(filepath: str, max_search_pages: int = 10, keywords=None) -> int:
    """Détecte la page contenant le préambule dans un PDF.

        Args:
            filepath (str): Chemin vers le fichier PDF
            max_search_pages (int, optional): Nombre max de pages à analyser. Defaults to 10.
            keywords (list, optional): Mots-clés à rechercher. Defaults to DEFAULT_PREAMBLE_KEYWORDS.

        Returns:
            int: Numéro de page (0-based) ou -1 si non trouvé

        Note:
            Utilise d'abord pdfplumber, puis une méthode OCR de secours si nécessaire
    """
    if keywords is None:
        keywords = DEFAULT_PREAMBLE_KEYWORDS
    try:
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages[:max_search_pages]):
                text = page.extract_text()
                if not text or is_toc_page(text):
                    continue
                norm_text = normalize_text(text)
                escaped = [re.escape(normalize_text(k)) for k in keywords]
                pattern = re.compile(r"\b(" + "|".join(escaped) + r")\b")
                if pattern.search(norm_text):
                    return i
    except Exception:
        pass
    return -1

def extract_metadata_from_pdf(filepath: str, nlp_model, llama_model) -> dict:
    """Extrait les métadonnées d'un document PDF en combinant plusieurs techniques.

        Args:
            filepath (str): Chemin vers le fichier PDF
            nlp_model: Modèle NLP pour l'extraction d'entités (ex: spaCy)
            llama_model: Modèle LLM pour l'analyse sémantique

        Returns:
            dict: Dictionnaire des métadonnées extraites

        Note:
            Combine:
            - Extraction directe du texte (pdfplumber)
            - OCR de secours (pytesseract)
            - Analyse NLP des entités nommées
            - Analyse sémantique avec LLM
    """
    try:
        preamble_page = detect_preamble_page(filepath, max_search_pages=20)
        source = "pdfplumber"

        if preamble_page == -1:
            keywords = DEFAULT_PREAMBLE_KEYWORDS
            try:
                images = convert_from_path(filepath, dpi=300, first_page=1, last_page=20)
                for i, img in enumerate(images):
                    ocr_text_candidate = pytesseract.image_to_string(img, lang="fra", config="--psm 3") or ""
                    if is_toc_page(ocr_text_candidate):
                        continue
                    norm = normalize_text(ocr_text_candidate)
                    found = any(re.search(r"\b" + re.escape(normalize_text(kw)) + r"\b", norm) for kw in keywords)
                    if found:
                        preamble_page = i
                        source = "ocr"
                        break
            except Exception:
                pass

        if preamble_page == -1:
            preamble_page = 0
            source = "ocr_fallback"

        if source == "pdfplumber":
            with pdfplumber.open(filepath) as pdf:
                page_text = pdf.pages[preamble_page].extract_text() or ""
            extracted_text = extract_after_preamble(page_text)
        else:
            img = convert_from_path(filepath, dpi=300, first_page=preamble_page+1, last_page=preamble_page+1)[0]
            ocr_text = pytesseract.image_to_string(img, lang="fra", config="--psm 3") or ""
            extracted_text = extract_after_preamble(ocr_text)

        doc = nlp_model(extracted_text)
        label_map = {
            "LABEL_ORG": "societe",
            "LABEL_MARCHE": "marche",
            "LABEL_LOC": "region",
            "LABEL_VERSION": "version"
        }

        collected = {}
        for ent in doc.ents:
            human_label = label_map.get(ent.label_)
            if human_label and human_label not in collected:
                collected[human_label] = ent.text.strip()

        if source in ("pdfplumber", "ocr"):
            prompt_text = f"""
            Tu es un assistant intelligent chargé d'analyser un document administratif, technique ou institutionnel, même si le texte contient du bruit, des répétitions ou des incohérences.

            Voici le contenu du document :
            \"\"\"{extracted_text}\"\"\"

            Lis attentivement ce texte et extrait uniquement les trois informations suivantes, si elles sont présentes :

            - **Objet** : extrait l'objet principal de l'étude ou du document. Format attendu : `Objet : [contenu]`
            - **Mission** : extrait la mission principale concernée. Format attendu : `mission : Mission X : [intitulé complet]`
            - **Nature du document** : type du document. Format attendu : `Nature du document : [type]`

            Consignes :
            - Une seule ligne par champ.
            - Pas de reformulation, copie exactement.
            - Si absent, mets `Non trouvé`.

            Réponds uniquement avec ces trois lignes formatées :
            objet : ...
            mission : ...
            nature : ...
            """
        else:
            prompt_text = f"""
            Tu es un assistant intelligent chargé d'analyser un document administratif, technique ou institutionnel, même si le texte contient du bruit, des erreurs OCR ou des répétitions.

            Voici le contenu du document :
            \"\"\"{extracted_text}\"\"\"

            Lis attentivement ce texte et extrais uniquement les quatre informations suivantes, si elles sont présentes :

            - **Objet** : extrait l'objet principal de l'étude ou du document. Format attendu : `Objet : [contenu]`
            - **Mission** : extrait la mission principale concernée. Format attendu : `mission : Mission X : [intitulé complet]`
            - **Nature du document** : type du document (ex. : note de synthèse, rapport, contrat, etc.). Format attendu : `Nature du document : [type]`
            - **Région** : indique la région concernée par le document. Format attendu : `Région : [nom de la région]`

            Consignes importantes :
            - Sois **concise** : une seule ligne par champ.
            - Ne fais **aucune reformulation**, copie exactement les expressions du texte.
            - Si une information est absente, indique `Non trouvé`.

            Réponds uniquement avec ces quatre lignes formatées :
            objet : ...
            mission : ...
            nature du document : ...
            région : ...
            """

        result = llama_model.invoke(prompt_text)
        for line in result.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                collected[key.strip().lower()] = value.strip()

        return collected
    except Exception as e:
        print(f"[MetadataExtractor] Erreur : {e}")
        return {}
