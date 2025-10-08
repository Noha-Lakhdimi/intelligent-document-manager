import os, shutil, uuid, json
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body

router = APIRouter(prefix="/trash", tags=["trash"])

BASE_DIR = os.path.abspath("uploads")
CORBEILLE_DIR = os.path.abspath("Corbeille")
METADATA_FILE = os.path.join(CORBEILLE_DIR, "metadata.json")

def human_readable_size(size, decimal_places=2):
    """Convertit une taille en octets en une chaîne lisible.

        Args:
            size (int): Taille en octets
            decimal_places (int): Nombre de décimales à afficher

        Returns:
            str: Taille formatée (ex: "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024.0
    return f"{size:.{decimal_places}f} TB"

def get_size(path):
    """Calcule la taille totale d'un fichier ou dossier.

        Args:
            path (str): Chemin vers le fichier/dossier

        Returns:
            int: Taille en octets
    """
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

def format_datetime(ts):
    """Formate un timestamp en chaîne de date lisible.

        Args:
            ts (float): Timestamp Unix

        Returns:
            str: Date formatée (ex: "2023-05-15 14:30:22")
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def get_creation_date(path):
    try:
        return datetime.fromtimestamp(os.path.getctime(path)).isoformat()
    except:
        return None

def load_metadata():
    """Charge les métadonnées de la corbeille depuis le fichier.

        Returns:
            list: Liste des éléments dans la corbeille
    """
    if not os.path.exists(METADATA_FILE):
        return []
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_metadata(data):
    """Sauvegarde les métadonnées de la corbeille dans le fichier.

        Args:
            data (list): Liste des éléments à sauvegarder
    """
    os.makedirs(CORBEILLE_DIR, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@router.get("/")
def list_trash():
    """Retourne la liste des éléments dans la corbeille avec leurs métadonnées.

        Returns:
            list: Liste des éléments avec :
                - id: Identifiant unique
                - original_path: Chemin d'origine
                - name: Nom de l'élément
                - is_dir: True si c'est un dossier
                - deleted_at: Date de suppression
                - creation_date: Date de création
                - size: Taille formatée
    """
    metadata = load_metadata()
    return metadata


@router.post("/move")
def move_to_corbeille(data: dict = Body(...)):
    """Déplace un fichier/dossier vers la corbeille et enregistre ses métadonnées.

        Args:
            data (dict): Doit contenir :
                - old_path: Chemin relatif de l'élément depuis BASE_DIR

        Returns:
            dict: Message de confirmation

        Raises:
            HTTPException: 400 si le chemin est manquant
            HTTPException: 404 si l'élément n'existe pas
    """
    old_rel_path = data.get("old_path", "").strip()
    if not old_rel_path:
        raise HTTPException(status_code=400, detail="Chemin source manquant")

    src = os.path.join(BASE_DIR, old_rel_path)
    if not os.path.exists(src):
        raise HTTPException(status_code=404, detail="Source introuvable")

    item_id = str(uuid.uuid4())
    item_name = os.path.basename(src)
    is_dir = os.path.isdir(src)

    os.makedirs(CORBEILLE_DIR, exist_ok=True)
    corbeille_item_path = os.path.join(CORBEILLE_DIR, item_id)

    shutil.move(src, corbeille_item_path)

    metadata = load_metadata()
    metadata.append({
        "id": item_id,
        "original_path": old_rel_path,
        "name": item_name,
        "is_dir": is_dir,
        "deleted_at": format_datetime(time.time()),
        "creation_date": format_datetime(os.path.getctime(corbeille_item_path)),
        "size": human_readable_size(get_size(corbeille_item_path)),
    })
    save_metadata(metadata)

    return {"message": "Déplacé vers la Corbeille"}

#Restaurer depuis la corbeille
@router.post("/restore")
def restore_from_corbeille(data: dict = Body(...)):
    """Restaurer un élément depuis la corbeille vers son emplacement d'origine.

        Args:
            data (dict): Doit contenir :
                - id: Identifiant de l'élément à restaurer

        Returns:
            dict: Message de confirmation

        Raises:
            HTTPException: 400 si l'ID est manquant ou si la destination existe déjà
            HTTPException: 404 si l'élément n'est pas dans la corbeille
    """
    item_id = data.get("id")
    if not item_id:
        raise HTTPException(status_code=400, detail="ID manquant")

    metadata = load_metadata()
    item = next((m for m in metadata if m["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Élément non trouvé dans la Corbeille")

    corbeille_item_path = os.path.join(CORBEILLE_DIR, item_id)
    restore_path = os.path.join(BASE_DIR, item["original_path"])

    if os.path.exists(restore_path):
        raise HTTPException(status_code=400, detail="Un élément existe déjà à l'endroit de restauration")

    os.makedirs(os.path.dirname(restore_path), exist_ok=True)
    shutil.move(corbeille_item_path, restore_path)

    new_metadata = [m for m in metadata if m["id"] != item_id]
    save_metadata(new_metadata)
    return {"message": "Restauré avec succès"}

@router.post("/delete")
def delete_forever(data: dict = Body(...)):
    """Supprime définitivement un élément de la corbeille.

        Args:
            data (dict): Doit contenir :
                - id: Identifiant de l'élément à supprimer

        Returns:
            dict: Message de confirmation

        Raises:
            HTTPException: 400 si l'ID est manquant
            HTTPException: 404 si l'élément n'est pas dans la corbeille
    """
    item_id = data.get("id")
    if not item_id:
        raise HTTPException(status_code=400, detail="ID manquant")

    corbeille_item_path = os.path.join(CORBEILLE_DIR, item_id)
    if not os.path.exists(corbeille_item_path):
        raise HTTPException(status_code=404, detail="Élément non trouvé dans la Corbeille")

    if os.path.isdir(corbeille_item_path):
        shutil.rmtree(corbeille_item_path)
    else:
        os.remove(corbeille_item_path)

    metadata = load_metadata()
    new_metadata = [m for m in metadata if m["id"] != item_id]
    save_metadata(new_metadata)

    return {"message": "Supprimé définitivement"}

@router.post("/empty")
def empty_trash():
    """Vide complètement la corbeille et supprime toutes les métadonnées.

        Returns:
            dict: Message de confirmation
    """
    if not os.path.exists(CORBEILLE_DIR):
        return {"message": "Déjà vide"}

    for item in os.listdir(CORBEILLE_DIR):
        item_path = os.path.join(CORBEILLE_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    save_metadata([])
    return {"message": "Corbeille vidée"}
