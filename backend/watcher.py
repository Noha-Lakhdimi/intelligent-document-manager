import os
import asyncio
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
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
import spacy
from langchain_community.llms.ollama import Ollama
from extractors import extract_metadata_from_pdf

# ----------------- CONFIGURATION -----------------

UPLOAD_DIR = "uploads"
CHROMA_PATH = "chroma_uploads"
METADATA_FILE = "documents_metadata.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)

embedding_function = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

nlp_model = spacy.load("./modele_ner_doc")
llama_model = Ollama(model="llama3.2:3b-instruct-q4_K_M")

# ----------------- UTILITAIRES -----------------

def load_documents_by_extension(file_path: str) -> list[Document]:
    """Charge un document en fonction de son extension.

        Args:
            file_path (str): Chemin vers le fichier à charger

        Returns:
            list[Document]: Liste des documents chargés

        Raises:
            Exception: Si le format de fichier n'est pas supporté

        Supported Formats:
            - PDF (.pdf)
            - Word (.docx)
            - Excel (.xls, .xlsx)
            - PowerPoint (.pptx)
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
        raise Exception(f"Format de fichier non supporté : {ext}")

def calculate_chunk_ids(chunks: list[Document]) -> list[Document]:
    """Calcule des IDs uniques pour chaque chunk basés sur la source et la page.

        Args:
            chunks (list[Document]): Liste de chunks à traiter

        Returns:
            list[Document]: Chunks avec leurs métadonnées ID mises à jour

        Example:
            Un ID généré aura le format: "chemin/vers/fichier.pdf:3:1"
            (source:page:chunk_index)
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

def process_documents(documents: list[Document]):
    """Traite une liste de documents en chunks et les ajoute à la base vectorielle.

        Args:
            documents (list[Document]): Documents à traiter

        Returns:
            str: Message de résultat indiquant le nombre de chunks ajoutés
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    chunks = calculate_chunk_ids(chunks)

    existing = db.get(include=[])
    existing_ids = set(existing.get("ids", []))

    new_chunks = [chunk for chunk in chunks if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=ids)
        return f"{len(new_chunks)} nouveau(x) chunk(s) ajouté(s)."
    else:
        return "Aucun nouveau chunk à ajouter."


def delete_chunks_by_source(source_path: str):
    """Supprime les chunks associés à un fichier source.

        Args:
            source_path (str): Chemin vers le fichier source

        Returns:
            str: Message de résultat indiquant le nombre de chunks supprimés
    """
    abs_path = os.path.abspath(source_path)
    filename = os.path.basename(source_path)

    all_docs = db.get(include=["metadatas", "documents"])
    ids_to_delete = [
        all_docs["ids"][idx]
        for idx, metadata in enumerate(all_docs["metadatas"])
        if metadata.get("source") and os.path.abspath(metadata["source"]) == abs_path
    ]

    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r+') as f:
                all_metadata = json.load(f)
                if filename in all_metadata:
                    del all_metadata[filename]
                    f.seek(0)
                    f.truncate()
                    json.dump(all_metadata, f, indent=2)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERROR] Erreur lors de la mise à jour du fichier de métadonnées: {e}")

    if ids_to_delete:
        db.delete(ids_to_delete)
        return f"{len(ids_to_delete)} chunk(s) supprimé(s) pour le fichier {filename}."

    return f"Aucun chunk à supprimer pour le fichier {filename}."

def delete_chunks_by_source_prefix(prefix_path: str):
    """Supprime les chunks associés à tous les fichiers d'un dossier.

        Args:
            prefix_path (str): Chemin vers le dossier source

        Returns:
            str: Message de résultat indiquant le nombre de chunks supprimés
    """
    abs_prefix = os.path.abspath(prefix_path)
    all_docs = db.get(include=["metadatas", "documents"])
    ids_to_delete = []

    for idx, metadata in enumerate(all_docs["metadatas"]):
        source = metadata.get("source")
        if source:
            abs_source = os.path.abspath(source)
            if abs_source.startswith(abs_prefix):
                ids_to_delete.append(all_docs["ids"][idx])

    if ids_to_delete:
        db.delete(ids_to_delete)
        return f"{len(ids_to_delete)} chunk(s) supprimé(s) pour le dossier."
    return "Aucun chunk à supprimer pour le dossier."

# ----------------- WATCHER -----------------

class UploadsHandler(FileSystemEventHandler):
    """Gestionnaire d'événements pour surveiller les modifications dans le dossier d'uploads.

        Attributes:
            processing_files (set): Ensemble des fichiers en cours de traitement
            loop (asyncio.AbstractEventLoop): Boucle d'événements asyncio
            last_events (dict): Derniers événements traités avec leur taille
    """
    def __init__(self, loop):
        """Initialise le gestionnaire.

            Args:
                loop (asyncio.AbstractEventLoop): Boucle d'événements asyncio
        """
        self.processing_files = set()
        self.loop = loop
        self.last_events = {}

    def should_ignore_event(self, src_path):
        """Détermine si un événement doit être ignoré.

        Args:
            src_path (str): Chemin du fichier concerné par l'événement

        Returns:
            bool: True si l'événement doit être ignoré
        """
        filename = os.path.basename(src_path)
        if filename.startswith(('.', '~$', '~')) or filename.endswith('.tmp'):
            return True

        now = time.time()
        if src_path in self.last_events:
            last_event_time, last_size = self.last_events[src_path]

            try:
                current_size = os.path.getsize(src_path)
                if now - last_event_time < 5.0 and current_size == last_size:
                    return True
            except OSError:
                pass

        try:
            current_size = os.path.getsize(src_path)
            self.last_events[src_path] = (now, current_size)
        except OSError:
            self.last_events[src_path] = (now, 0)

        return False
    def on_modified(self, event):
        """Gère les événements de modification de fichier.

            Args:
                event (FileSystemEvent): Événement de modification
        """
        if event.is_directory or self.should_ignore_event(event.src_path):
            return

        print(f"[Watcher] Fichier modifié : {event.src_path}")
        asyncio.run_coroutine_threadsafe(
            self.handle_file(event.src_path), self.loop
        )

    def on_created(self, event):
        """Gère les événements de création de fichier.

            Args:
                event (FileSystemEvent): Événement de création
        """
        if event.is_directory:
            print(f"[Watcher] Dossier créé : {event.src_path}")
            return
        else:
            print(f"[Watcher] Fichier créé : {event.src_path}")
            asyncio.run_coroutine_threadsafe(
                self.handle_file(event.src_path), self.loop
            )

    def on_deleted(self, event):
        """Gère les événements de suppression de fichier/dossier.

            Args:
                event (FileSystemEvent): Événement de suppression
        """
        if event.is_directory:
            print(f"[Watcher] Dossier supprimé : {event.src_path}")
            result = delete_chunks_by_source_prefix(event.src_path)
            print(f"[Watcher] {result}")
        else:
            print(f"[Watcher] Fichier supprimé : {event.src_path}")
            result = delete_chunks_by_source(event.src_path)
            print(f"[Watcher] {result}")

    def on_moved(self, event):
        """Gère les événements de déplacement/renommage de fichier/dossier.

            Args:
                event (FileSystemEvent): Événement de déplacement
        """
        if event.is_directory:
            print(f"[Watcher] Dossier déplacé : {event.src_path} → {event.dest_path}")
            deleted = delete_chunks_by_source_prefix(event.src_path)
            print(f"[Watcher] {deleted}")

        else:
            print(f"[Watcher] Fichier déplacé : {event.src_path} → {event.dest_path}")
            deleted = delete_chunks_by_source(event.src_path)
            print(f"[Watcher] {deleted}")

            asyncio.run_coroutine_threadsafe(
                self.handle_file(event.dest_path), self.loop
            )

    async def handle_file(self, file_path):
        """Traite un fichier en l'indexant dans la base vectorielle.

            Args:
                file_path (str): Chemin vers le fichier à traiter
        """
        abs_path = os.path.abspath(file_path)
        if not abs_path.startswith(os.path.abspath(UPLOAD_DIR)):
            print(f"[Watcher] Ignoré hors uploads : {file_path}")
            return

        filename = os.path.basename(file_path)
        if filename.startswith(".~") or filename.endswith(".tmp"):
            print(f"[Watcher] Ignoré fichier temporaire : {file_path}")
            return

        current_size = os.path.getsize(file_path)
        if file_path in self.last_events:
            _, last_size = self.last_events[file_path]
            if current_size == last_size:
                print(f"[Watcher] Fichier non modifié (même taille) : {file_path}")
                return

        await asyncio.sleep(0.5)
        if file_path in self.processing_files:
            return
        self.processing_files.add(file_path)

        try:
            print(f"[Watcher] Traitement complet du fichier : {file_path}")
            documents = load_documents_by_extension(file_path)

            metadata_extra = {}
            if file_path.lower().endswith(".pdf"):
                metadata_extra = extract_metadata_from_pdf(file_path, nlp_model, llama_model)
                print(f"[Watcher] Métadonnées extraites : {metadata_extra}")

                all_metadata = {}
                if os.path.exists(METADATA_FILE):
                    with open(METADATA_FILE, 'r') as f:
                        all_metadata = json.load(f)

                filename = os.path.basename(file_path)
                all_metadata[filename] = metadata_extra

                with open(METADATA_FILE, 'w') as f:
                    json.dump(all_metadata, f, indent=2)

            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(documents)
            chunks = calculate_chunk_ids(chunks)

            existing = db.get(include=[])
            existing_ids = set(existing.get("ids", []))

            new_chunks = []
            for chunk in chunks:
                chunk_id = chunk.metadata.get("id")
                if chunk_id not in existing_ids:
                    if metadata_extra:
                        chunk.metadata.update(metadata_extra)
                    new_chunks.append(chunk)

            if new_chunks:
                ids = [chunk.metadata["id"] for chunk in new_chunks]
                db.add_documents(new_chunks, ids=ids)
                print(f"[Watcher] {len(new_chunks)} chunk(s) ajouté(s)")
            else:
                print("[Watcher] Aucun nouveau chunk à ajouter.")

        except Exception as e:
            print(f"[Watcher] Erreur traitement fichier {file_path} : {e}")
        finally:
            self.processing_files.remove(file_path)


async def watch_uploads():
    """Lance la surveillance du dossier d'uploads.

        Cette fonction crée un observateur qui surveille en permanence
        le dossier UPLOAD_DIR pour détecter les modifications.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    loop = asyncio.get_running_loop()
    handler = UploadsHandler(loop)

    observer = Observer()
    observer.schedule(handler, UPLOAD_DIR, recursive=True)
    observer.start()
    print(f"[Watcher] Surveillance du dossier '{UPLOAD_DIR}' démarrée...")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("[Watcher] Arrêt du watcher.")
        observer.stop()
        observer.join()
