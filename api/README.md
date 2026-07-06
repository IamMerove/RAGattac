# API de RAGattac

### Structure

```bash
ragattac/
├── .git/
├── data/
│   └── livrable_scifigrag_gold.parquet  # base de données temporaire
└── api/ # Périmètre Anna
    ├── .venv/
    ├── .python-version # La version de Python verrouillée pour l'API
    ├── pyproject.toml # Dépendances (FastAPI, LangGraph, FAISS...)
    ├── __init__.py
    ├── models.py # Contrats Pydantic (ChatRequest, ChatResponse)
    ├── main.py # Le futur serveur FastAPI (Endpoint POST /chat)
    └── agent/ # Le "Cerveau" de l'application
        ├── __init__.py
        ├── graph.py # L'orchestration du flux ReAct via LangGraph
        ├── state.py   # La définition de la mémoire/état de l'agent
        └── tools.py  # L'implémentation des 5 outils exigés
```