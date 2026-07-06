import os
import polars as pl
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import PGVector
from langchain_ollama import OllamaEmbeddings

# =====================================================================
# SCRIPT D'INGESTION VECTORIELLE (À LANCER UNE SEULE FOIS)
# =====================================================================


def main():
    print("=" * 50)
    print("🧠 DÉMARRAGE DE L'INGESTION VECTORIELLE (PGVECTOR) 🧠")
    print("=" * 50)

    # 1. Configuration de la connexion
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    if not SUPABASE_URL:
        raise ValueError("⚠️ Variable SUPABASE_URL introuvable dans le .env")

    # LangChain exige le driver psycopg2
    conn_string = SUPABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    if conn_string.startswith("postgres://"):
        conn_string = conn_string.replace("postgres://", "postgresql+psycopg2://")

    # 2. Chargement du modèle d'Embeddings
    print("⚙️ Initialisation du modèle d'Embeddings (nomic-embed-text)...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # 3. Chargement des données Parquet
    fichier_donnees = "horragor_final_data.parquet"
    if not os.path.exists(fichier_donnees):
        print(f"❌ Fichier {fichier_donnees} introuvable.")
        return

    print(f"📖 Lecture de {fichier_donnees}...")
    df = pl.read_parquet(fichier_donnees)

    # On filtre les films qui n'ont pas de synopsis (inutile de vectoriser du vide)
    df_valide = df.filter(
        pl.col("overview").is_not_null() & (pl.col("overview").str.len_chars() > 10)
    )
    print(f"📊 {len(df_valide)} films avec synopsis trouvés sur {len(df)} au total.")

    # 4. Préparation des Documents pour LangChain
    print("📦 Création des paquets (Documents LangChain)...")
    docs_to_insert = []

    # On itère sur les lignes de notre DataFrame Polars
    for row in df_valide.iter_rows(named=True):
        # Le contenu principal du vecteur, c'est le synopsis (et le titre pour aider sémantiquement)
        texte_a_vectoriser = f"Titre: {row['title']}\nSynopsis: {row['overview']}"

        # On attache nos métadonnées cruciales (notamment l'horragor_id pour faire le lien plus tard !)
        metadata = {
            "horragor_id": row["horragor_id"],
            "title": row["title"],
            "category": row.get("source_universe", "Inconnu"),
        }

        doc = Document(page_content=texte_a_vectoriser, metadata=metadata)
        docs_to_insert.append(doc)

    # 5. Injection dans Supabase PGVector
    print("\n🚀 Lancement de l'injection vectorielle vers Supabase !")
    print(
        "⚠️ ATTENTION : Calculer des milliers d'embeddings localement via Ollama prend du temps."
    )
    print("Allez vous faire un café, le monstre digère...\n")

    try:
        # La fonction magique qui calcule les vecteurs ET crée les tables Supabase !
        vectorstore = PGVector.from_documents(
            documents=docs_to_insert,
            embedding=embeddings,
            connection_string=conn_string,
            collection_name="horragor_vectors",  # Le nom exact que notre Agent va chercher
            use_jsonb=True,  # Format moderne et optimisé pour Postgres
        )
        print(
            "\n✅ SUCCESS ! Tous les vecteurs ont été enregistrés dans Supabase (PGVector)."
        )
        print(
            "Votre Agent HorRAGor peut désormais utiliser le Tool 2 (Recommandations) ! 🎉"
        )

    except Exception as e:
        print(f"\n❌ Erreur fatale lors de l'injection PGVector : {e}")


if __name__ == "__main__":
    main()
