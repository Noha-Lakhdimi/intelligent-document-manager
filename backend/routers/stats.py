from fastapi import APIRouter
from datetime import datetime, timedelta
import os

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.get("/")
def get_stats():
    """Calcule et retourne les statistiques d'utilisation des uploads.

        Parcourt récursivement le dossier d'uploads pour calculer :
        - Le nombre total de documents
        - Le nombre de documents ajoutés cette semaine
        - Le dernier fichier modifié
        - L'espace disque utilisé

        Returns:
            dict: Dictionnaire contenant les statistiques :
                - total_documents (int): Nombre total de fichiers
                - added_this_week (int): Nombre de fichiers ajoutés dans les 7 derniers jours
                - last_modified_file (str): Chemin du dernier fichier modifié
                - used_space (str): Espace disque utilisé formaté en Ko
    """
    total_files = 0
    total_size = 0
    last_modified_file = None
    last_modified_time = datetime.fromtimestamp(0)
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)
    added_this_week = 0

    for root, _, filenames in os.walk(UPLOAD_DIR):
        for filename in filenames:
            path = os.path.join(root, filename)
            stat = os.stat(path)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size

            total_files += 1
            total_size += size

            if mtime > last_modified_time:
                last_modified_time = mtime
                last_modified_file = os.path.relpath(path, UPLOAD_DIR).replace("\\", "/")

            if mtime > one_week_ago:
                added_this_week += 1

    used_space_str = f"{total_size // 1024} Ko"

    return {
        "total_documents": total_files,
        "added_this_week": added_this_week,
        "last_modified_file": last_modified_file or "Aucun fichier",
        "used_space": used_space_str,
    }
