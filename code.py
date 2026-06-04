import os
import faiss
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


def main():
    print("=" * 50)
    print("RAG MULTISUPPORT AVEC LLAMA INDEX & FAISS")
    print("=" * 50)

    # 1. Vérification du dossier contenant le référentiel Microsoft/Simplon
    data_dir = "./data_referentiel"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"⚠️ Le dossier '{data_dir}' n'existait pas. Je viens de le créer.")
        print(
            "Veuillez y glisser vos fichiers (IA-E1.pdf, IA-E2-E3.md, IA-E4-E5.txt) et relancer le script."
        )
        return

    if len(os.listdir(data_dir)) == 0:
        print(
            f"⚠️ Le dossier '{data_dir}' est vide. Mettez-y vos fichiers de référentiel !"
        )
        return

    print("\n⚙️ 1. Configuration des modèles locaux (Ollama)...")
    # Dans les versions modernes de Llama Index (>v0.10), on configure les modèles
    # de manière globale via l'objet 'Settings'.
    model_name = "llama3.2:3b"
    embed_model_name = "nomic-embed-text"  # <-- NOUVEAU : Un modèle ultra-léger dédié à 100% aux vecteurs !

    # On bride volontairement la fenêtre de contexte à 4096 tokens pour éviter
    # qu'Ollama ne réserve 10 Go de RAM inutilement pour son "KV Cache".
    Settings.llm = Ollama(
        model=model_name, temperature=0, request_timeout=120.0, context_window=4096
    )
    Settings.embed_model = OllamaEmbedding(model_name=embed_model_name)

    print("📂 2. Chargement automatique des documents (PDF, TXT, MD)...")
    # C'est la force de Llama Index : un seul objet gère tous les formats !
    documents = SimpleDirectoryReader(data_dir).load_data()
    print(f"   -> Succès : {len(documents)} pages/morceaux extraits.")

    print("⚡ 3. Initialisation de la base vectorielle FAISS (En RAM)...")
    # ⚠️ ATTENTION : La dimension dépend strictement de votre modèle d'Embedding !
    # Le modèle 'nomic-embed-text' génère des vecteurs de taille 768 (et non plus 3072 comme Llama 3.2).
    # Si on laisse 3072, FAISS plantera avec une erreur 'Dimension mismatch'.
    d = 768
    faiss_index = faiss.IndexFlatL2(d)

    # On encapsule l'index FAISS natif dans la structure Llama Index
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("🧠 4. Création de l'Index (Calcul des Embeddings)...")
    # Llama Index va "chunker" (découper) automatiquement les documents
    # et calculer les embeddings via Ollama avant de les stocker dans FAISS.
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    print("✅ Indexation terminée !")

    # 5. Création du Query Engine (Le Moteur de Recherche / Chatbot)
    # Llama Index crée automatiquement le prompt optimal sous le capot.
    query_engine = index.as_query_engine(
        similarity_top_k=3  # On limite aux 3 meilleurs morceaux (chunks) pour ne pas noyer le LLM
    )

    print("\n" + "=" * 50)
    print("🎓 EXAMINATEUR DU RÉFÉRENTIEL MICROSOFT/SIMPLON PRÊT !")
    print("Posez vos questions sur les compétences E1, E2, E3, E4, E5.")
    print("Tapez 'exit', 'stop' ou 'fin' pour quitter.")
    print("=" * 50 + "\n")

    # Boucle de conversation
    while True:
        user_input = input("Candidat : ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "stop", "fin"]:
            print("Examinateur : Fin de l'évaluation. Au revoir !")
            break

        try:
            print("⏳ Recherche dans le référentiel et réflexion en cours...")
            # Une seule ligne suffit : 'query' fait le retrieval ET la génération
            response = query_engine.query(user_input)

            print(f"\n🤖 Llama-Index : {response}\n")

            # --- ASTUCE DEBUG : Afficher les sources ---
            # Décommentez les lignes ci-dessous pour voir d'où le LLM a tiré sa réponse
            # print("   [Sources utilisées :]")
            # for source in response.source_nodes:
            #     fichier = source.metadata.get('file_name', 'Inconnu')
            #     print(f"   - Fichier : {fichier}")
            # ------------------------------------------

        except Exception as e:
            print(f"❌ Erreur lors de l'interrogation : {e}\n")


if __name__ == "__main__":
    main()
