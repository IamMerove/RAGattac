import time
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

# Import de nos contrats de models définit dans models.py
from models import ChatRequest, ChatResponse

# Définition robuste des chemins
API_DIR = Path(__file__).resolve().parent
DATA_DIR = API_DIR.parent / "data"
PARQUET_FILE = DATA_DIR / "horror.parquet"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'API.
    Tout le code avant le 'yield" s'exécute au démarrage du serveur.
    C'est ici que nous chargerons le fichier Parquet et l'index FAISS en RAM
    """
    print("Démarrage du serveur...")
    print(f"Recherche du fichier de données : {PARQUET_FILE}")

    if not PARQUET_FILE.exists():
        print("AVERTISSEMENT : Fichier Parquet introuvable. L'index FAISS sera vide.")
        app.state.vector_index = None
    else:
        try:
            # Lecture du fichier Parquet
            df = pd.read_parquet(PARQUET_FILE)
            print(f"Données chargées avec succès : {len(df)} films trouvés.")

            # TODO: Construction du routeur FAISS (Nom -> ID)
            # TODO: 2. Vectorisation des titres et création de l'index FAISS
            # Pour l'instant, on stocke juste le DataFrame en mémoire brute
        except Exception as e:
            print(f"Erreur critique lors du chargement des données : {e}")
            app.state.vector_index = None

    yield  # Le serveur tourne et écoute les requêtes

    print("Arrêt du serveur : Libération de la mémoire RAM.")
    app.state.movies_db = None


app = FastAPI(
    title="HorRAGor BOT API",
    description="API REST asynchrone orchestrant l'agent conversationnel",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint unque réceptionnant les questions de l'interface utilisateur.
    Initialise le graphe LangGraph et retourne le verdict final.
    """
    start_time = time.time()

    try:
        # Test temporaire pour vérifier que la donnée est bien en RAM
        db_status = (
            "Données en RAM" if hasattr(app.state, "movies_db") else "Pas de données"
        )

        simulated_answer = f"Message reçu '{request.user_id}'. Question: '{request.question}'. Statut DB: {db_status}"
        execution_time = int((time.time() - start_time) * 1000)

        return ChatResponse(
            answer=simulated_answer,
            sources=["Mock API"],
            needs_ui_feedback=False,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
