import time
from contextlib import asynccontextmanager

# --- NOUVEAUX IMPORTS : Connexion à TA base Supabase ---
# On importe la configuration DB et le modèle Media de ton pipeline horRAGore
from app.database import SessionLocal
from app.models.core import Media
from fastapi import Depends, FastAPI, HTTPException

# Import de nos contrats de models définis dans models.py (le code de tes amis)
from models import ChatRequest, ChatResponse
from sqlalchemy.orm import Session


def get_db():
    """
    Dépendance FastAPI (Best Practice).
    Ouvre une session base de données pour chaque requête utilisateur
    et la referme proprement à la fin, pour éviter les fuites de mémoire.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'API.
    C'est ici que nous testons la connexion à Supabase au démarrage du serveur.
    """
    print("🚀 Démarrage du serveur FastAPI...")
    print("🔌 Tentative de ping sur la base de données Supabase (Gold)...")

    try:
        # Test simple pour voir si la BDD répond et compter les films
        db = SessionLocal()
        movie_count = db.query(Media).count()
        print(
            f"✅ Connexion réussie ! {movie_count} films trouvés dans la table 'medias'."
        )
        app.state.db_status = "Connecté à Supabase"
        db.close()
    except Exception as e:
        print(f"❌ Erreur critique lors de la connexion à la BDD : {e}")
        app.state.db_status = "Erreur de connexion"

    yield  # Le serveur tourne et écoute les requêtes

    print("🛑 Arrêt du serveur FastAPI.")


app = FastAPI(
    title="HorRAGor BOT API",
    description="API REST asynchrone branchée sur la base Supabase 3NF",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint unique réceptionnant les questions de l'interface utilisateur.
    """
    start_time = time.time()

    try:
        # --- PREUVE DE CONCEPT ---
        # On va chercher le tout premier film de TA base de données pour
        # prouver au front-end que la connexion API <-> Supabase fonctionne.
        sample_movie = db.query(Media).first()
        movie_title = sample_movie.title if sample_movie else "Aucun film trouvé"

        # On construit une fausse réponse en attendant le vrai moteur RAG
        simulated_answer = (
            f"Message reçu : '{request.question}'.\n"
            f"Test DB : Je vois bien la base de données ! "
            f"Par exemple, le premier film en base est '{movie_title}'."
        )

        return ChatResponse(
            answer=simulated_answer,
            sources=["Supabase PostgreSQL (via SQLAlchemy)"],
            needs_ui_feedback=False,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
