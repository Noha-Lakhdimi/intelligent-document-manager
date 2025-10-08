import time
from fastapi import APIRouter, HTTPException, Body, Form, File, UploadFile, Query
import os, shutil

router = APIRouter()
BASE_DIR = os.path.abspath("uploads")

@router.get("/")
def list_items(path: str = ""):
    """Liste les éléments (fichiers et dossiers) dans un chemin spécifié.

        Args:
            path (str): Chemin relatif depuis le dossier de base (uploads)

        Returns:
            dict: Dictionnaire contenant :
                - items: Liste des éléments avec leurs métadonnées
                - current_path: Chemin actuel exploré

        Raises:
            HTTPException: 404 si le chemin n'existe pas
    """
    base_path = os.path.join(BASE_DIR, path)
    items = []
    for entry in os.scandir(base_path):
        info = entry.stat()
        size = info.st_size
        creation_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.st_ctime))

        if entry.is_dir():
            size = get_dir_size(entry.path)

        items.append({
            "name": entry.name,
            "path": os.path.relpath(entry.path, BASE_DIR),
            "is_dir": entry.is_dir(),
            "size": sizeof_fmt(size),
            "creation_date": creation_time,
        })
    return {"items": items, "current_path": path}

def get_dir_size(start_path):
    """Calcule la taille totale d'un dossier en octets.

        Args:
            start_path (str): Chemin vers le dossier

        Returns:
            int: Taille totale en octets
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

def sizeof_fmt(num, suffix="B"):
    """Formate une taille en octets en une chaîne lisible.

        Args:
            num (float): Taille en octets
            suffix (str): Suffixe d'unité (par défaut "B")

        Returns:
            str: Taille formatée (ex: "1.5KB")
    """
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"

@router.post("/rename")
def rename_item(data: dict = Body(...)):
    """Renomme un fichier ou dossier.

        Args:
            data (dict): Doit contenir :
                - old_path: Chemin relatif actuel
                - new_name: Nouveau nom

        Returns:
            dict: Message de confirmation

        Raises:
            HTTPException: 404 si l'élément n'existe pas
            HTTPException: 400 si le nouveau nom est invalide ou existe déjà

        Example:
            POST /explorer/rename
            Body: {"old_path": "doc.txt", "new_name": "document.txt"}
    """
    old_path = os.path.join(BASE_DIR, data.get("old_path", ""))
    new_name = data.get("new_name", "").strip()
    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail="Fichier/dossier introuvable")
    if not new_name:
        raise HTTPException(status_code=400, detail="Nouveau nom requis")
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    if os.path.exists(new_path):
        raise HTTPException(status_code=400, detail="Un fichier ou dossier avec ce nom existe déjà")
    os.rename(old_path, new_path)
    return {"message": "Renommé avec succès"}


@router.get("/search")
def search_files(query: str = Query(..., min_length=1)):
    """Recherche des fichiers/dossiers contenant la requête dans leur nom.

        Args:
            query (str): Terme de recherche (1 caractère minimum)

        Returns:
            list: Liste des éléments correspondants

        Example:
            GET /explorer/search?query=document
    """
    results = []
    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            if query.lower() in d.lower():
                full_path = os.path.join(root, d)
                rel_path = os.path.relpath(full_path, BASE_DIR).replace("\\", "/")
                results.append({"name": d, "path": rel_path, "is_dir": True})

        for f in files:
            if query.lower() in f.lower():
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, BASE_DIR).replace("\\", "/")
                results.append({"name": f, "path": rel_path, "is_dir": False})

    return results

@router.post("/create_folder")
async def create_folder(
        path: str = Form(...),
        folder_name: str = Form(...),
        action: str = Form('create')
):
    """Crée un nouveau dossier avec options de remplacement.

        Args:
            path (str): Chemin parent relatif
            folder_name (str): Nom du nouveau dossier
            action (str): 'create' (par défaut) ou 'replace'

        Returns:
            dict: Statut de l'opération

        Raises:
            HTTPException: 400 pour chemin non autorisé
            HTTPException: 500 pour erreur de création
    """
    try:
        full_path = os.path.join(BASE_DIR, path, folder_name)

        if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
            raise HTTPException(status_code=400, detail="Chemin non autorisé")

        if action == 'replace':
            if os.path.exists(full_path):
                shutil.rmtree(full_path)
            os.makedirs(full_path)
        else:
            os.makedirs(full_path, exist_ok=True)

        return {"success": True, "folder": folder_name}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'opération: {str(e)}"
        )

@router.post("/delete_folder")
async def delete_folder(data: dict = Body(...)):
    """Supprime récursivement un dossier.

        Args:
            data (dict): Doit contenir "path" (chemin relatif)

        Returns:
            dict: Statut de l'opération

        Raises:
            HTTPException: 400 pour chemin non autorisé
            HTTPException: 404 si le dossier n'existe pas
            HTTPException: 500 pour erreur de suppression
    """
    try:
        path = os.path.join(BASE_DIR, data.get("path", ""))

        if not os.path.abspath(path).startswith(os.path.abspath(BASE_DIR)):
            raise HTTPException(status_code=400, detail="Chemin non autorisé")

        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Dossier introuvable")

        shutil.rmtree(path)
        return {"success": True}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(""),
    relative_path: str = Form("")
):
    """Upload un fichier avec options de chemin.

        Args:
            file (UploadFile): Fichier à uploader
            path (str): Chemin parent relatif
            relative_path (str): Chemin relatif complet (alternative)

        Returns:
            dict: Nom du fichier uploadé
    """
    target_dir = os.path.join(BASE_DIR, path, os.path.dirname(relative_path))  # correction ici
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, file.filename)

    with open(target_file, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {"filename": relative_path or file.filename}

@router.post("/folder")
async def upload_folder(
        file: UploadFile = File(...),
        relative_path: str = Form(...),
        path: str = Form("")
):
    """Upload un fichier en conservant la structure de dossier.

        Args:
            file (UploadFile): Fichier à uploader
            relative_path (str): Chemin relatif complet
            path (str): Chemin parent relatif (optionnel)

        Returns:
            dict: Statut et chemin du fichier
    """
    target_dir = os.path.join(BASE_DIR, path, os.path.dirname(relative_path))
    os.makedirs(target_dir, exist_ok=True)

    target_file_path = os.path.join(target_dir, os.path.basename(relative_path))
    with open(target_file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"status": "uploaded", "path": target_file_path}


@router.post("/move_item")
def move_item(data: dict = Body(...)):
    """Déplace ou renomme un fichier/dossier.

        Args:
            data (dict): Doit contenir :
                - source: Chemin source relatif
                - destination: Chemin destination relatif
                - new_name: Nouveau nom (optionnel)
                - overwrite: Écraser si existe (défaut: False)

        Returns:
            dict: Message et nouveau chemin

        Raises:
            HTTPException: 404 si source introuvable
            HTTPException: 400 si destination occupée
            HTTPException: 500 pour erreur de déplacement

        Example:
            POST /explorer/move_item
            Body: {"source": "old.txt", "destination": "subfolder", "overwrite": true}
    """
    old_path = os.path.join(BASE_DIR, data["source"])

    new_name = data.get("new_name", os.path.basename(old_path))

    new_path = os.path.join(BASE_DIR, data["destination"], new_name)

    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail="Source introuvable")

    if os.path.exists(new_path):
        if data.get("overwrite", False):
            try:
                if os.path.isdir(new_path):
                    shutil.rmtree(new_path)
                else:
                    os.remove(new_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Échec de la suppression de l'élément existant: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Destination déjà occupée et overwrite=False"
            )

    os.makedirs(os.path.dirname(new_path), exist_ok=True)

    try:
        shutil.move(old_path, new_path)
        return {
            "message": "Déplacement réussi",
            "new_path": os.path.relpath(new_path, BASE_DIR)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du déplacement: {str(e)}"
        )

@router.post("/copy_item")
def copy_item(data: dict = Body(...)):
    """Copie un fichier/dossier avec gestion des conflits.

        Args:
            data (dict): Doit contenir :
                - source: Chemin source relatif
                - destination: Chemin destination relatif

        Returns:
            dict: Message et chemin de destination

        Raises:
            HTTPException: 404 si source introuvable
            HTTPException: 500 pour erreur de copie

        Example:
            POST /explorer/copy_item
            Body: {"source": "doc.txt", "destination": "backup"}
    """
    source_path = os.path.join(BASE_DIR, data["source"])
    dest_dir = os.path.join(BASE_DIR, data["destination"])
    dest_name = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, dest_name)

    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail="Source introuvable")

    name, ext = os.path.splitext(dest_name)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_dir, f"{name}({counter}){ext}")
        counter += 1

    os.makedirs(dest_dir, exist_ok=True)
    if os.path.isdir(source_path):
        shutil.copytree(source_path, dest_path)
    else:
        shutil.copy2(source_path, dest_path)

    return {"message": "Copie réussie", "copied_to": dest_path}

