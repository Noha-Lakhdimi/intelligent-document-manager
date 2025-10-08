from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.get("/")
def get_history():
    """Récupère l'historique des fichiers uploadés.

        Parcourt récursivement le dossier d'uploads et retourne les métadonnées
        des fichiers sous forme de liste triée par date de modification (récent en premier).
        Seulement les 6 fichiers les plus récents sont retournés.

        Returns:
            list: Liste de dictionnaires contenant pour chaque fichier :
                - name: Chemin relatif du fichier
                - size_kb: Taille en kilo-octets
                - added_at: Date/heure de modification (ISO format)
                - info: Placeholder pour informations supplémentaires
    """
    files = []

    for root, _, filenames in os.walk(UPLOAD_DIR):
        for filename in filenames:
            path = os.path.join(root, filename)
            stat = os.stat(path)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size // 1024
            rel_path = os.path.relpath(path, UPLOAD_DIR).replace("\\", "/")

            files.append({
                "name": rel_path,
                "size_kb": size_kb,
                "added_at": mtime.isoformat(),
                "info": "..."
            })

    files = sorted(files, key=lambda x: x["added_at"], reverse=True)

    return files[:6]
