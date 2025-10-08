import time
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from fastapi.responses import StreamingResponse
import httpx
from fastapi import Body
import re

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from transformers import AutoTokenizer
from sentence_transformers import CrossEncoder

CHROMA_UPLOADS_PATH = "chroma_uploads"
DATA_PATH = "data"
CONV_FILE = "conversations.json"
METADATA_FILE = "documents_metadata.json"

UPLOAD_DIR = "uploads"

os.makedirs(DATA_PATH, exist_ok=True)

PROMPT_TEMPLATE = """
Tu es un assistant documentaire. Si la réponse ne se trouve pas dans le contexte, réponds : "Je ne sais pas."

Utilise uniquement le contexte ci-dessous pour répondre à la question de l'utilisateur.

Contexte :
{context}

Question : {question}
Réponse :
"""

def get_embedding_model():
    """Initialise et retourne le modèle d'embedding Ollama.

        Returns:
            OllamaEmbeddings: Modèle d'embedding configuré
    """
    return OllamaEmbeddings(model="nomic-embed-text")

# Initialisation des modèles
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
router = APIRouter()
embedding_function = get_embedding_model()
db_permanent = Chroma(persist_directory=CHROMA_UPLOADS_PATH, embedding_function=embedding_function)
model = Ollama(model="llama3.2:3b-instruct-q4_K_M")

# ----------------- MODÈLES PYDANTIC -----------------
class Source(BaseModel):
    """Modèle pour représenter la source d'un document.

        Attributes:
            source (str): Chemin du fichier source
            page (Optional[int]): Numéro de page
            id (Optional[str]): Identifiant unique du chunk
            score (Optional[float]): Score de pertinence
    """
    source: str
    page: Optional[int] = None
    id: Optional[str] = None
    score: Optional[float] = None

class Message(BaseModel):
    """Modèle pour représenter un message dans une conversation.

        Attributes:
            id (int): Identifiant unique du message
            sender (str): Expéditeur ('user' ou 'bot')
            text (Optional[str]): Contenu textuel
            type (Optional[str]): Type de message
            fileName (Optional[str]): Nom de fichier joint
            fileUrl (Optional[str]): URL du fichier joint
            sources (Optional[List[Source]]): Sources documentaires
    """
    id: int
    sender: str
    text: Optional[str] = None
    type: Optional[str] = None
    fileName: Optional[str] = None
    fileUrl: Optional[str] = None
    sources: Optional[List[Source]] = None

class MessageUpdate(BaseModel):
    """Modèle pour mettre à jour un message existant.

        Attributes:
            id (int): Identifiant du message à mettre à jour
            sender (Optional[str]): Nouvel expéditeur
            text (Optional[str]): Nouveau contenu
            type (Optional[str]): Nouveau type
            fileName (Optional[str]): Nouveau nom de fichier
            fileUrl (Optional[str]): Nouvelle URL de fichier
            sources (Optional[List[Source]]): Nouvelles sources
            isLoading (Optional[bool]): Indicateur de chargement
            delete (Optional[bool]): Si True, supprime le message
    """
    id: int
    sender: Optional[str] = None
    text: Optional[str] = None
    type: Optional[str] = None
    fileName: Optional[str] = None
    fileUrl: Optional[str] = None
    sources: Optional[List[Source]] = None
    isLoading: Optional[bool] = None
    delete: Optional[bool] = False

class Conversation(BaseModel):
    """Modèle pour représenter une conversation.

        Attributes:
            id (str): Identifiant unique
            name (str): Nom de la conversation
            mode (str): Mode de fonctionnement
            messages (List[Message]): Liste des messages
    """
    id: str
    name: str
    mode: str
    messages: List[Message]

class FileCopyRequest(BaseModel):
    """Modèle pour une requête de copie de fichier.

        Attributes:
            file_name (str): Nom du fichier à copier
    """
    file_name: str

class QueryRequest(BaseModel):
    """Modèle pour une requête de recherche.

        Attributes:
            query_text (str): Texte de la requête
            conversation_id (Optional[str]): ID de conversation associée
    """
    query_text: str
    conversation_id: Optional[str] = None

def load_conversations():
    """Charge les conversations depuis le fichier de stockage.

        Returns:
            List[dict]: Liste des conversations
    """
    if not os.path.exists(CONV_FILE):
        return []
    try:
        with open(CONV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_conversations(convs):
    """Sauvegarde les conversations dans le fichier de stockage.

        Args:
            convs (List[dict]): Liste des conversations à sauvegarder
    """
    with open(CONV_FILE, "w", encoding="utf-8") as f:
        json.dump(convs, f, indent=2, ensure_ascii=False)

def save_context_docs_to_message(conv_id: str, message_id: int, docs_with_sources: List[dict]):
    """Sauvegarde les sources documentaires dans un message spécifique.

        Args:
            conv_id (str): ID de la conversation
            message_id (int): ID du message
            docs_with_sources (List[dict]): Documents avec métadonnées

        Returns:
            bool: True si la sauvegarde a réussi
    """
    convs = load_conversations()
    for conv in convs:
        if conv["id"] == conv_id:
            for message in conv["messages"]:
                if message["id"] == message_id:
                    sources = []
                    for doc in docs_with_sources:
                        meta = doc["metadata"]
                        sources.append({
                            "source": meta.get("source"),
                            "page": meta.get("page"),
                            "id": meta.get("id"),
                            "score": doc["score"]
                        })
                    message["sources"] = sources
                    save_conversations(convs)
                    return True
    return False

@router.get("/conversations", response_model=List[Conversation])
def get_conversations():
    """Récupère toutes les conversations.

        Returns:
            List[Conversation]: Liste des conversations
    """
    return load_conversations()

@router.post("/conversations", response_model=Conversation)
def create_conversation(conv: Conversation):
    """Crée une nouvelle conversation.

        Args:
            conv (Conversation): Conversation à créer

        Returns:
            Conversation: Conversation créée
    """
    conv_dict = conv.dict()
    conv_dict["mode"] = conv_dict.get("mode", "classic")

    convs = load_conversations()
    convs.insert(0, conv_dict)
    save_conversations(convs)
    return conv_dict

@router.put("/conversations/{conv_id}", response_model=Conversation)
def update_conversation(conv_id: str, conv: Conversation):
    """Met à jour une conversation existante.

        Args:
            conv_id (str): ID de la conversation
            conv (Conversation): Nouvelles données

        Returns:
            Conversation: Conversation mise à jour

        Raises:
            HTTPException: Si la conversation n'existe pas
    """
    convs = load_conversations()
    for i, c in enumerate(convs):
        if c["id"] == conv_id:
            convs[i] = conv.dict()
            save_conversations(convs)
            return conv
    raise HTTPException(status_code=404, detail="Conversation not found")

@router.delete("/conversations/{conv_id}", status_code=204)
def delete_conversation(conv_id: str):
    """Supprime une conversation.

        Args:
            conv_id (str): ID de la conversation à supprimer

        Raises:
            HTTPException: Si la conversation n'existe pas
    """
    convs = load_conversations()
    updated_convs = [conv for conv in convs if conv["id"] != conv_id]
    if len(convs) == len(updated_convs):
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    save_conversations(updated_convs)
    return

@router.post("/conversations/{conv_id}/messages")
def update_message(conv_id: str, message: MessageUpdate = Body(...)):
    """Met à jour ou supprime un message.

        Args:
            conv_id (str): ID de la conversation
            message (MessageUpdate): Données de mise à jour

        Returns:
            dict: Statut de l'opération

        Raises:
            HTTPException: Si la conversation n'existe pas
    """
    convs = load_conversations()
    for i, conv in enumerate(convs):
        if conv["id"] == conv_id:
            messages = conv.get("messages", [])

            if message.delete:
                new_messages = [m for m in messages if m["id"] != message.id]
                convs[i]["messages"] = new_messages
                save_conversations(convs)
                return {"status": "deleted", "message_id": message.id}

            found = False
            for j, m in enumerate(messages):
                if m["id"] == message.id:
                    updated_msg = m.copy()
                    if message.sender is not None:
                        updated_msg["sender"] = message.sender
                    if message.text is not None:
                        updated_msg["text"] = message.text
                    if message.type is not None:
                        updated_msg["type"] = message.type
                    if message.fileName is not None:
                        updated_msg["fileName"] = message.fileName
                    if message.fileUrl is not None:
                        updated_msg["fileUrl"] = message.fileUrl
                    if message.sources is not None:
                        updated_msg["sources"] = [s.dict() if isinstance(s, Source) else s for s in message.sources]
                    if message.isLoading is not None:
                        updated_msg["isLoading"] = message.isLoading
                    convs[i]["messages"][j] = updated_msg
                    found = True
                    break

            if not found:
                new_msg = message.dict(exclude={"delete"})
                convs[i]["messages"].append(new_msg)

            save_conversations(convs)
            return {"status": "updated_or_added", "message_id": message.id}

    raise HTTPException(status_code=404, detail="Conversation not found")

def load_documents_by_extension(file_path: str) -> List[Document]:
    """Charge des documents selon leur extension.

        Args:
            file_path (str): Chemin du fichier

        Returns:
            List[Document]: Documents chargés

        Raises:
            HTTPException: Si le format n'est pas supporté
    """
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path).load()
    elif ext == ".docx":
        return UnstructuredWordDocumentLoader(file_path).load()
    elif ext in [".xls", ".xlsx"]:
        return UnstructuredExcelLoader(file_path).load()
    elif ext == ".pptx":
        return UnstructuredPowerPointLoader(file_path).load()
    else:
        raise HTTPException(status_code=400, detail=f"Format de fichier non supporté : {ext}")

def calculate_chunk_ids(chunks: List[Document]) -> List[Document]:
    """Calcule des IDs uniques pour chaque chunk.

        Args:
            chunks (List[Document]): Chunks à traiter

        Returns:
            List[Document]: Chunks avec IDs ajoutés
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

    return chunks

def process_documents(documents: List[Document], db: Chroma):
    """Traite et indexe des documents dans ChromaDB.

        Args:
            documents (List[Document]): Documents à traiter
            db (Chroma): Base de données cible

        Returns:
            dict: Résultat du traitement
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=lambda text: len(tokenizer.encode(text)),
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]  # Better sentence splitting
    )

    chunks = splitter.split_documents(documents)
    chunks = calculate_chunk_ids(chunks)
    existing = db.get(include=[])
    existing_ids = set(existing["ids"])
    new_chunks = [chunk for chunk in chunks if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=ids)
        db.persist()
        return {"message": f"{len(new_chunks)} new chunks added."}
    else:
        return {"message": "No new chunks to add."}

@router.post("/query-by-filename")
async def query_by_filename(request: QueryRequest):
    """Effectue une recherche dans un fichier spécifique.

        Args:
            request (QueryRequest): Requête de recherche

        Returns:
            StreamingResponse: Flux de réponse

        Raises:
            HTTPException: En cas d'erreur
    """
    total_start = time.time()

    if not request.query_text or not request.conversation_id:
        raise HTTPException(status_code=400, detail="Incomplete request")

    convs = load_conversations()
    last_file = None
    for conv in convs:
        if conv["id"] == request.conversation_id:
            for msg in reversed(conv["messages"]):
                if msg.get("fileUrl"):
                    last_file = msg["fileUrl"].split("/")[-1]
                    break

    if not last_file:
        raise HTTPException(status_code=400, detail="No file selected")

    try:
        chroma_start = time.time()
        chroma_filter = {"source": {"$eq": f"uploads\{last_file}"}}
        docs_with_scores = db_permanent.similarity_search_with_score(
            request.query_text,
            k=10,
            filter=chroma_filter
        )

        print(f"[CHROMA] Recherche filtrée terminée en {time.time() - chroma_start:.2f}s - {len(docs_with_scores)} résultats trouvés")

        rerank_start = time.time()
        if docs_with_scores:
            pairs = [(request.query_text, doc.page_content) for doc, _ in docs_with_scores]
            rerank_scores = cross_encoder.predict(pairs)

            combined_results = list(zip(
                [doc for doc, _ in docs_with_scores],
                rerank_scores,
                [score for _, score in docs_with_scores]
            ))

            combined_results.sort(key=lambda x: x[1], reverse=True)
            top_results = combined_results[:5]
        else:
            top_results = []

        print(f"[RERANK] Terminé en {time.time() - rerank_start:.2f}s - {len(top_results)} résultats retenus")

        context_start = time.time()
        docs_with_sources = []
        context_tokens = 0
        context_texts = []

        for doc, rerank_score, original_score in top_results:
            doc_tokens = len(tokenizer.encode(doc.page_content))
            if context_tokens + doc_tokens <= 1500:
                context_texts.append(doc.page_content)
                context_tokens += doc_tokens
                docs_with_sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(rerank_score),
                    "original_score": float(original_score)
                })

        print("\n=========== CHUNKS UTILISÉS DANS LE CONTEXTE ===========")
        for doc in docs_with_sources:
            print(f"Page: {doc['metadata'].get('page')} - Score: {doc['score']:.4f}")
            print(doc['content'])
            print("---")
        print("=========== FIN DES CHUNKS ===========\n")

        print(f"[CTX] Construit avec {context_tokens} tokens en {time.time() - context_start:.2f}s")

        context_text = "\n\n---\n\n".join(context_texts)
        prompt = PROMPT_TEMPLATE.format(context=context_text, question=request.query_text)

        async def event_stream():
            llm_start = time.time()
            response_started = False
            message_id = None

            if request.conversation_id:
                for conv in convs:
                    if conv["id"] == request.conversation_id:
                        for msg in reversed(conv["messages"]):
                            if msg["sender"] == "bot" and msg.get("isLoading", False):
                                message_id = msg["id"]
                                break

            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    async with client.stream(
                        "POST",
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.2:3b-instruct-q4_K_M",
                            "prompt": prompt,
                            "stream": True,
                            "options": {
                                "num_ctx": 2048,
                                "temperature": 0.3,
                                "top_k": 20,
                                "num_predict": 300
                            }
                        }
                    ) as response:
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    data = json.loads(line)
                                    if "response" in data:
                                        yield json.dumps({"response": data["response"]}) + "\n"
                                        response_started = True
                                except json.JSONDecodeError:
                                    continue

                    if response_started and docs_with_sources:
                        sources = [{
                            "source": os.path.basename(doc["metadata"].get("source", "")),
                            "page": doc["metadata"].get("page"),
                            "id": doc["metadata"].get("id"),
                            "score": doc["score"],
                            "original_score": doc.get("original_score", 0)
                        } for doc in docs_with_sources]

                        yield json.dumps({"sources": sources}) + "\n"

                        if request.conversation_id and message_id:
                            save_context_docs_to_message(
                                request.conversation_id,
                                message_id,
                                docs_with_sources
                            )

                finally:
                    print(f"[TOTAL] Temps total : {time.time() - total_start:.2f}s")

        return StreamingResponse(event_stream(), media_type="text/plain")

    except Exception:
        print(f"[ERROR] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.post("/stream-query")
async def stream_query(request: QueryRequest):
    """Effectue une recherche dans la base permanente.

        Args:
            request (QueryRequest): Requête de recherche

        Returns:
            StreamingResponse: Flux de réponse
    """
    return await stream_query_with_db(request, db_permanent)

def extract_metadata_from_query(query: str, llama_model: Ollama) -> dict:
    """Extrait les métadonnées potentielles d'une requête utilisateur.

        Args:
            query (str): Requête utilisateur
            llama_model (Ollama): Modèle LLM pour l'extraction

        Returns:
            dict: Métadonnées extraites
    """
    prompt = f"""
    Analyse cette question et extrait les informations pertinentes EXACTEMENT telles qu'elles apparaissent dans la question,
    sans interprétation, généralisation ou remplacement, sous forme de clés-valeurs.

    Question : "{query}"

    Cherche exclusivement ces informations (si présentes) :
    - marche : numéro ou référence de marché (ex: 1235/E/DPL/2018)
    - region : nom exact de région ou ville mentionné dans la question (ex: Agadir, Rabat)
    - societe : nom exact d'entreprise ou organisation (ex: ADI, NOVEC)
    - version : version exacte du document (ex: définitif, provisoire)

    Réponds UNIQUEMENT au format JSON suivant (mets null si information absente) :
    {{
        "marche": "valeur ou null",
        "region": "valeur ou null",
        "societe": "valeur ou null",
        "version": "valeur ou null"
    }}

    Ne complète pas les informations manquantes et ne modifie pas les valeurs extraites.

    Exemples :
    Pour la question "Donne-moi les documents du marché 1208/E/DPL/2008 à Agadir",
    la réponse serait : 
    {{
        "marche": "1208/E/DPL/2008",
        "region": "Agadir",
        "societe": null,
        "version": null
    }}

    Pour la question "Je cherche les rapports définitifs d'ADI",
    la réponse serait :
    {{
        "marche": null,
        "region": null,
        "societe": "ADI",
        "version": "définitif"
    }}
    """

    try:
        response = llama_model.invoke(prompt)
        start = response.find('{')
        end = response.rfind('}') + 1
        json_str = response[start:end]
        return json.loads(json_str)
    except Exception as e:
        print(f"Erreur extraction métadonnées: {e}")
        return {
            "marche": None,
            "region": None,
            "societe": None,
            "version": None
        }


def filtrer_documents_par_metadonnees(documents, metadata):
    """Filtre les documents selon leurs métadonnées.

        Args:
            documents (List[tuple]): Liste de (filename, metadata)
            metadata (dict): Critères de filtrage

        Returns:
            List[str]: Chemins des documents correspondants
    """
    print("[FILTER] Filtrage avec métadonnées :", metadata)

    metadata_filtree = {k: v for k, v in metadata.items() if v and str(v).lower() != 'null'}

    if not metadata_filtree:
        print("[FILTER] Aucune métadonnée valide → retour de tous les documents")
        return documents

    documents_filtrés = []
    for doc in documents:
        filename, meta = doc
        match_trouve = False
        for key, value in metadata_filtree.items():
            if key in meta and value.lower() in str(meta[key]).lower():
                match_trouve = True
                break
        if match_trouve:
            documents_filtrés.append(os.path.join("uploads", filename))

    print(f"[FILTER] Documents correspondants : {len(documents_filtrés)}")
    return documents_filtrés


def remove_metadata_keywords_from_query(query: str, query_metadata: dict) -> str:
    """Nettoie une requête en supprimant les termes de métadonnées.

        Args:
            query (str): Requête originale
            query_metadata (dict): Métadonnées extraites

        Returns:
            str: Requête nettoyée
    """
    print(f"[CLEAN] Requête avant nettoyage : {query}")
    clean_query = query
    for value in query_metadata.values():
        if value and str(value).lower() != 'null':
            clean_query = re.sub(re.escape(str(value)), '', clean_query, flags=re.IGNORECASE)
    clean_query = clean_query.strip()
    print(f"[CLEAN] Requête après suppression des mots-clés métadonnées : {clean_query}\n")
    return clean_query


async def stream_query_with_db(request: QueryRequest, db: Chroma):
    """Fonction utilitaire pour les requêtes de recherche.

        Args:
            request (QueryRequest): Requête de recherche
            db (Chroma): Base de données à interroger

        Returns:
            StreamingResponse: Flux de réponse

        Raises:
            HTTPException: En cas d'erreur
    """
    total_start = time.time()
    print(f"\n[START] Traitement de la requête : {request.query_text}")

    metadata_start = time.time()
    query_metadata = extract_metadata_from_query(request.query_text, model) if db == db_permanent else None
    print(f"[META] Extraction terminée en {time.time() - metadata_start:.2f}s → {query_metadata}")

    filtered_files = []
    if query_metadata:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            DOC_METADATA = json.load(f)
        filtered_files = filtrer_documents_par_metadonnees(DOC_METADATA.items(), query_metadata)

    search_query = remove_metadata_keywords_from_query(request.query_text, query_metadata or {})

    chroma_start = time.time()
    k_initial = 20

    chroma_filter = {}
    if filtered_files:
        chroma_filter = {"source": {"$in": filtered_files}}
        print(f"[META] Recherche limitée à {len(filtered_files)} document(s).")
    else:
        print("[META] ⚠ Aucun document trouvé avec ces métadonnées, recherche sur toute la base.")

    print(f"[CHROMA] Recherche vectorielle (k={k_initial}) avec filtre : {chroma_filter}")

    try:
        results = db.similarity_search_with_score(
            search_query,
            k=k_initial,
            filter=chroma_filter if chroma_filter else None  # Utilisez 'filter' au lieu de 'where'
        )
    except Exception as e:
        print(f"[ERROR] Erreur lors de la recherche Chroma: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche dans la base de données")

    print(f"[CHROMA] Recherche terminée en {time.time() - chroma_start:.2f}s - {len(results)} résultats trouvés.")

    rerank_start = time.time()
    pairs = [(search_query, doc.page_content) for doc, _ in results]
    print(f"[RERANK] {len(pairs)} paires préparées pour reranking.")

    if pairs:
        rerank_scores = cross_encoder.predict(pairs)
        combined_results = list(zip(
            [doc for doc, _ in results],
            rerank_scores,
            [score for _, score in results]
        ))
        combined_results.sort(key=lambda x: x[1], reverse=True)
        top_results = combined_results[:5]
    else:
        top_results = []
    print(f"[RERANK] Reranking terminé en {time.time() - rerank_start:.2f}s - {len(top_results)} résultats retenus.")

    context_start = time.time()
    docs_with_sources = []
    context_tokens = 0
    context_texts = []

    PROMPT_TEMPLATE = """
    Tu es un expert en analyse de documents techniques. 
    Voici des extraits pertinents :

    {context}

    Question : {question}

    Consignes :
    - Réponds de manière précise et technique
    - Si l'information exacte n'est pas dans les extraits, dis simplement "Je n'ai pas trouvé l'information dans les documents"
    - Ne fais pas référence aux métadonnées ou aux scores

    Réponse :
    """

    for doc, rerank_score, original_score in top_results:
        doc_tokens = len(tokenizer.encode(doc.page_content))
        if context_tokens + doc_tokens <= 1500:
            context_texts.append(doc.page_content)
            context_tokens += doc_tokens
            docs_with_sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(rerank_score),
                "original_score": float(original_score)
            })
    print(f"[CONTEXT] Contexte construit avec {len(context_texts)} chunks ({context_tokens} tokens).")

    print(f"[DEBUG] Chunks sélectionnés pour le contexte ({len(context_texts)}):")
    for i, chunk in enumerate(context_texts):
        print(f"--- Chunk #{i + 1} ---\n{chunk[:500]}...\n")

    context_text = "\n\n---\n\n".join(context_texts)
    prompt = PROMPT_TEMPLATE.format(context=context_text, question=request.query_text)

    print(f"[DEBUG] Prompt complet envoyé au LLM :\n{prompt[:1500]}\n")

    async def event_stream():
        llm_start = time.time()
        print(f"[LLM] Envoi du prompt au modèle (streaming)...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream(
                        "POST",
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.2:3b-instruct-q4_K_M",
                            "prompt": prompt,
                            "stream": True,
                            "options": {
                                "temperature": 0.3,
                                "num_ctx": 2048,
                                "top_k": 20,
                                "num_predict": 300
                            }
                        }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield json.dumps({"response": data["response"]}) + "\n"
                            except json.JSONDecodeError:
                                continue

                if docs_with_sources:
                    sources = []
                    for doc in docs_with_sources:
                        meta = doc["metadata"]
                        sources.append({
                            "source": os.path.basename(meta.get("source", "")),
                            "page": meta.get("page"),
                            "id": meta.get("id"),
                            "score": doc["score"],
                            "original_score": doc["original_score"]
                        })
                    print(f"[SOURCES] Sources envoyées : {sources}")
                    yield json.dumps({"sources": sources}) + "\n"

            except Exception as e:
                print(f"[ERROR] {str(e)}")
                yield json.dumps({"error": f"Erreur: {str(e)}"}) + "\n"
            finally:
                print(f"[END] Temps total de traitement : {time.time() - total_start:.2f}s")

    return StreamingResponse(event_stream(), media_type="text/plain")

