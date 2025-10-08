from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import upload, history, stats, explorer, trash, chat
from watcher import watch_uploads
import asyncio

app = FastAPI(
    title="API de Gestion de Fichiers",
    description="""
    API complète pour la gestion de fichiers avec les fonctionnalités suivantes :
    - Upload de fichiers
    - Historique
    - Statistiques d'utilisation
    - Exploration de fichiers
    - Corbeille
    - Chat intégré
    """,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def startup_event():
    """Initialise les tâches en arrière-plan au démarrage de l'application.

    Lance le watcher de fichiers qui surveille le dossier des uploads pour détecter
    les nouvelles modifications et déclencher les traitements associés.

    Returns:
        None: Cette fonction ne retourne rien directement mais lance une tâche asynchrone.

    Note:
        La tâche créée tournera en continu jusqu'à l'arrêt de l'application.
    """
    asyncio.create_task(watch_uploads())

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(history.router, prefix="/history", tags=["Historique"])
app.include_router(stats.router, prefix="/stats", tags=["Statistiques"])
app.include_router(explorer.router, prefix="/explorer", tags=["Explorer"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(trash.router)
