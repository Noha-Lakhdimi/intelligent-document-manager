from datetime import datetime
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Optional
import os
from starlette.responses import FileResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
METADATA_FILE = "documents_metadata.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class MetadataResponse(BaseModel):
    """Modèle Pydantic pour la réponse des métadonnées.

        Attributes:
            metadata (Dict[str, str]): Dictionnaire des métadonnées extraites
            success (bool): Indique si l'opération a réussi
            message (Optional[str]): Message d'information supplémentaire
    """
    metadata: Dict[str, str]
    success: bool
    message: Optional[str]


@router.get("/")
async def explore_directory(path: str = "", metadata: str = ""):
    """Liste le contenu d'un dossier avec filtrage optionnel par métadonnées.

        Args:
            path (str): Chemin relatif du dossier à explorer (depuis UPLOAD_DIR)
            metadata (str): Liste de clés de métadonnées séparées par des virgules pour filtrer

        Returns:
            dict: Dictionnaire contenant :
                - items: Liste des fichiers/dossiers
                - current_path: Chemin actuel exploré

        Raises:
            HTTPException: 404 si le dossier n'existe pas
    """
    base_path = os.path.join(UPLOAD_DIR, path)

    if not os.path.exists(base_path):
        raise HTTPException(status_code=404, detail="Dossier non trouvé")

    metadata_filters = metadata.split(',') if metadata else []
    file_metadata = {}

    if metadata_filters:
        if not os.path.exists(METADATA_FILE):
            return {"items": [], "current_path": path}

        with open(METADATA_FILE) as f:
            file_metadata = json.load(f)

    items = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        rel_path = os.path.join(path, item) if path else item

        if os.path.isdir(item_path):
            items.append({
                "name": item,
                "path": rel_path,
                "is_dir": True,
                "size": "",
                "creation_date": ""
            })
        else:
            include_file = True
            if metadata_filters and item in file_metadata:
                file_meta = file_metadata[item]
                for filter_key in metadata_filters:
                    if filter_key not in file_meta:
                        include_file = False
                        break

            if include_file:
                items.append({
                    "name": item,
                    "path": rel_path,
                    "is_dir": False,
                    "size": f"{os.path.getsize(item_path) / 1024:.1f} Ko",
                    "creation_date": datetime.fromtimestamp(
                        os.path.getctime(item_path)
                    ).strftime('%Y-%m-%d %H:%M')
                })

    return {"items": items, "current_path": path}

@router.post("/files")
async def upload_file(file: UploadFile = File(...)):
    """Upload un fichier unique dans le dossier d'uploads.

        Args:
            file (UploadFile): Fichier à uploader

        Returns:
            dict: Dictionnaire avec le nom du fichier uploadé
    """
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    return {"filename": file.filename}

@router.post("/folder")
async def upload_folder(
        file: UploadFile = File(...),
        relative_path: str = Form(default="")
):
    """Upload un fichier en conservant une structure de dossier relative.

        Args:
            file (UploadFile): Fichier à uploader
            relative_path (str): Chemin relatif où stocker le fichier

        Returns:
            dict: Dictionnaire avec le chemin relatif du fichier

        Raises:
            HTTPException: 400 si le chemin relatif est manquant

    """
    if not relative_path:
        raise HTTPException(status_code=400, detail="Le chemin relatif est manquant")

    full_dir = os.path.join(UPLOAD_DIR, os.path.dirname(relative_path))
    os.makedirs(full_dir, exist_ok=True)

    file_location = os.path.join(UPLOAD_DIR, relative_path)
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {"relative_path": relative_path}


@router.get("/existing_files")
async def get_existing_files():
    """Récupère la liste de tous les fichiers dans l'arborescence d'uploads.

        Returns:
            list: Liste des chemins relatifs de tous les fichiers
    """
    existing_files = []
    for root, _, files in os.walk(UPLOAD_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), UPLOAD_DIR)
            existing_files.append(rel_path.replace("\\", "/"))
    return existing_files


@router.get("/file/{filename}")
async def serve_file(filename: str):
    """Télécharge un fichier PDF spécifique.

        Args:
            filename (str): Nom du fichier à télécharger

        Returns:
            FileResponse: Réponse avec le fichier PDF en ligne

        Raises:
            HTTPException: 404 si le fichier n'existe pas
            HTTPException: 400 si le fichier n'est pas un PDF

    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    if not filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are downloadable")

    return FileResponse(
        file_path,
        media_type='application/pdf',
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@router.get("/metadata/{filename}", response_model=MetadataResponse)
async def get_file_metadata(filename: str):
    """Récupère les métadonnées générées par le watcher pour un fichier spécifique.

        Args:
            filename (str): Nom du fichier

        Returns:
            MetadataResponse: Réponse standardisée avec les métadonnées

        Raises:
            HTTPException: 404 si le fichier n'existe pas
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

    if not os.path.exists(METADATA_FILE):
        return MetadataResponse(
            metadata={},
            success=False,
            message="Aucune métadonnée disponible"
        )

    with open(METADATA_FILE) as f:
        all_metadata = json.load(f)
        file_metadata = all_metadata.get(filename, {})

        if not file_metadata:
            return MetadataResponse(
                metadata={},
                success=False,
                message="Le fichier est en cours de traitement"
            )

        return MetadataResponse(
            metadata=file_metadata,
            success=True,
            message="Métadonnées disponibles"
        )


@router.get("/status/{filename}")
async def check_processing_status(filename: str):
    """Vérifie l'état de traitement d'un fichier.

    Args:
        filename (str): Nom du fichier à vérifier

    Returns:
        dict: Dictionnaire avec :
            - filename: Nom du fichier
            - exists: Si le fichier existe
            - processed: Si le fichier a été traité
            - status: Statut détaillé
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    metadata_path = f"{file_path}.metadata.json"

    exists = os.path.exists(file_path)
    processed = os.path.exists(metadata_path) if exists else False

    return {
        "filename": filename,
        "exists": exists,
        "processed": processed,
        "status": "processed" if processed else "processing" if exists else "not_found"
    }


@router.get("/metadata_keys")
async def get_metadata_keys():
    """Retourne les clés de métadonnées disponibles dans le système.

       Returns:
           dict: Dictionnaire avec la liste des clés autorisées
    """
    allowed_keys = {"marche", "nature du document", "region", "societe", "version"}  # Set pour des recherches plus rapides

    if not os.path.exists(METADATA_FILE):
        return {"keys": sorted(list(allowed_keys))}  # Retourne les clés autorisées même si vide

    with open(METADATA_FILE) as f:
        all_metadata = json.load(f)

    keys = set()
    for metadata in all_metadata.values():
        for key in metadata.keys():
            if key in allowed_keys:
                keys.add(key)

    keys.update(allowed_keys)

    return {"keys": sorted(list(keys))}


@router.get("/batch_metadata")
async def batch_metadata(filenames: str):
    """Récupère les métadonnées pour plusieurs fichiers en une seule requête.

        Args:
            filenames (str): Liste de noms de fichiers séparés par des virgules

        Returns:
            dict: Dictionnaire avec les métadonnées pour chaque fichier

        Example:
            GET /explorer/batch_metadata?filenames=doc1.pdf,doc2.pdf
    """
    if not os.path.exists(METADATA_FILE):
        return {}

    filename_list = filenames.split(',')

    with open(METADATA_FILE) as f:
        all_metadata = json.load(f)

    result = {
        filename: all_metadata.get(filename, {})
        for filename in filename_list
    }

    return result


@router.put("/metadata/{filename}")
async def update_file_metadata(
        filename: str,
        metadata: Dict[str, str] = Body(...)
):
    """Met à jour manuellement les métadonnées d'un fichier.

        Args:
            filename (str): Nom du fichier à mettre à jour
            metadata (Dict[str, str]): Nouvelles métadonnées

        Returns:
            dict: Dictionnaire avec le statut de l'opération

        Raises:
            HTTPException: 404 si le fichier n'existe pas
            HTTPException: 500 en cas d'erreur d'écriture
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r') as f:
                all_metadata = json.load(f)
        else:
            all_metadata = {}

        all_metadata[filename] = metadata

        with open(METADATA_FILE, 'w') as f:
            json.dump(all_metadata, f, indent=2)

        return {"success": True, "message": "Métadonnées mises à jour"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour : {str(e)}"
        )