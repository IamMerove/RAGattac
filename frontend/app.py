import requests
import streamlit as st

# URL de l'API FastAPI de ton binôme (à adapter selon son port)
BACKEND_URL = "http://localhost:8000/chat"

# Configuration de la page principale
st.set_page_config(page_title="HorRAGor BOT", page_icon="🧛‍♂️", layout="centered")

# --- TITRE ET PRÉSENTATION DE L'INTERFACE (Le début de ton code) ---
st.title("🧛‍♂️ HorRAGor BOT")
st.subheader("Votre guide dans les abysses de l'horreur et l'immensité du cosmos...")
st.write("Cinéma 🎬 · Littérature 📚 · Jeux Vidéo 🎮")
st.markdown("---")

# 1. Initialisation des états de session pour le chat et le blocage
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False


# 2. Fonction de callback pour figer l'input dès qu'on valide
def disable_input():
    st.session_state.processing = True


# 3. Zone de saisie (Désactivée si l'assistant réfléchit)
prompt = st.chat_input(
    "Qu'est-ce qui vous fait peur et/ou voyager dans les etoiles?",
    disabled=st.session_state.processing,
    on_submit=disable_input,
)

# 4. Affichage de tout l'historique des discussions (Bulles de chat)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Traitement immédiat de la saisie utilisateur
if prompt:
    # On affiche la bulle de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    # On l'enregistre dans l'historique global
    st.session_state.messages.append({"role": "user", "content": prompt})

    # On relance Streamlit pour appliquer instantanément le mode "disabled" (grisé) sur l'input
    st.rerun()

# 6. Logique d'appel vers FastAPI (S'active après le rerun si processing est True)
if st.session_state.processing and st.session_state.messages:
    # On récupère la question tout juste posée
    last_user_message = st.session_state.messages[-1]["content"]

    # On crée la bulle de l'assistant avec le spinner animé
    with st.chat_message("assistant"):
        with st.spinner("HorRAGor rassemble ses esprits... 🩸"):
            try:
                # Requête POST stricte vers le backend
                response = requests.post(
                    BACKEND_URL, json={"question": last_user_message}, timeout=45
                )

                if response.status_code == 200:
                    answer = response.json().get("response", "Le bot est resté muet...")
                else:
                    answer = (
                        f"⚠️ Erreur du serveur d'horreur (Code {response.status_code})"
                    )

            except requests.exceptions.ConnectionError:
                answer = "🔌 Impossible de joindre le cerveau de l'agent. Le Backend (FastAPI) est-il bien démarré ?"
            except Exception as e:
                answer = f"💥 Une erreur inattendue est survenue : {str(e)}"

            # Affichage du texte ou de l'erreur dans la bulle
            st.markdown(answer)

    # On enregistre la réponse de l'assistant dans l'historique
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Le traitement est fini : on débloque l'interface et on rafraîchit pour le prochain message
    st.session_state.processing = False
    st.rerun()
