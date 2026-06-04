import streamlit as st
import requests

# URL de l'API FastAPI de ton binôme (à adapter selon ses réglages de port)
BACKEND_URL = "http://localhost:8000/chat"

# Configuration de la page
st.set_page_config(page_title="HorRAGor BOT", page_icon="🧛‍♂️", layout="centered")

st.title("🧛‍♂️ HorRAGor BOT")
st.subheader("Votre guide dans les abysses de l'horreur...")
st.write("Cinéma 🎬 · Littérature 📚 · Jeux Vidéo 🎮")
st.markdown("---")

# 1. Initialisation de l'historique des messages dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Affichage des messages de l'historique sous forme de bulles
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Zone de saisie utilisateur (Input)
if prompt := st.chat_input("Qu'est-ce qui vous fait peur ?"):
    
    # Affichage immédiat du message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Sauvegarde dans l'historique de session
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 4. Envoi de la requête au Backend (FastAPI) avec un Loader visuel
    with st.chat_message("assistant"):
        with st.spinner("HorRAGor rassemble ses esprits... 🩸"):
            try:
                # Structure JSON stricte envoyée au backend (Modèle Pydantic attendu côté API)
                payload = {"question": prompt}
                
                response = requests.post(
                    BACKEND_URL, 
                    json=payload, 
                    timeout=45  # Temps de réponse large (le RAG et le Juge peuvent prendre du temps)
                )
                
                if response.status_code == 200:
                    # Extraction de la réponse validée par le Juge du backend
                    data = response.json()
                    answer = data.get("response", "Le bot est resté muet...")
                    
                    # Affichage et sauvegarde du résultat
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"⚠️ Erreur du serveur d'horreur (Code {response.status_code})")
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 Impossible de joindre le cerveau de l'agent. Le Backend (FastAPI) est-il bien démarré ?")
            except Exception as e:
                st.error(f"💥 Une erreur inattendue est survenue : {str(e)}")