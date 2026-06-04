import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

@tool
def scrape_detailed_synopsis(titre_film: str) -> str:
    """
    Recherche et extrait le synopsis complet et détaillé d'un film sur Wikipédia 
    lorsque l'utilisateur demande des détails approfondis ou des anecdotes 
    qui ne sont pas présents dans la base de données principale.
    """
    print(f"🕵️‍♂️ [AGENT] Activation du Scraping Wikipédia pour : {titre_film}")
    
    # 1. Formatage du titre pour l'URL Wikipédia (ex: "The Shining" -> "The_Shining")
    # On capitalise la première lettre car Wikipédia y est très sensible
    titre_formate = titre_film.strip().replace(" ", "_")
    url = f"https://fr.wikipedia.org/wiki/{titre_formate}"
    
    # Simuler un navigateur classique pour éviter d'être bloqué
    headers = {
        "User-Agent": "HorRAGorBot/1.0 (Contact: etudiant@ecole.com) Python-Requests/2.31"
    }
    
    try:
        # 2. Requête HTTP pour récupérer la page
        response = requests.get(url, headers=headers, timeout=10)
        
        # Si Wikipédia renvoie une erreur (ex: page non trouvée)
        if response.status_code == 404:
            return f"Je n'ai pas trouvé de page Wikipédia spécifique pour le film '{titre_film}'. Vérifiez l'orthographe."
        elif response.status_code != 200:
            return f"Impossible d'accéder à Wikipédia pour le moment (Code erreur : {response.status_code})."
            
        # 3. Analyse du code HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Sur Wikipédia FR, la section s'appelle souvent "Synopsis" ou "Intrigue"
        section_cible = soup.find(id="Synopsis") or soup.find(id="Intrigue")
        
        if not section_cible:
            return f"J'ai trouvé la page de '{titre_film}' sur Wikipédia, mais aucune section dédiée au 'Synopsis' n'a pu être extraite automatiquement."
            
        # 4. Extraction des paragraphes de texte sous le titre de la section
        synopsis_paragraphes = []
        # On remonte au parent (h2) pour naviguer entre les balises suivantes
        element_courant = section_cible.find_parent().find_next_sibling()
        
        while element_courant:
            # Si on croise un autre titre h2 ou h3, c'est qu'on a changé de section (ex: "Fiche technique") -> On s'arrête
            if element_courant.name in ["h2", "h3"]:
                break
                
            # Si c'est un paragraphe de texte, on le garde
            if element_courant.name == "p":
                texte = element_courant.get_text().strip()
                if texte: # On évite les paragraphes vides
                    synopsis_paragraphes.append(texte)
                    
            element_courant = element_courant.find_next_sibling()
            
        # 5. On rassemble le tout proprement
        if synopsis_paragraphes:
            synopsis_complet = "\n\n".join(synopsis_paragraphes)
            # Sécurité pour ne pas saturer le contexte du LLM (max ~2500 caractères)
            return synopsis_complet[:2500] + "..." if len(synopsis_complet) > 2500 else synopsis_complet
        else:
            return f"La section Synopsis de '{titre_film}' existe sur Wikipédia mais elle semble vide."
            
    except requests.exceptions.Timeout:
        return "Le serveur Wikipédia a mis trop de temps à répondre. Tentative abandonnée."
    except Exception as e:
        return f"Une erreur technique est survenue lors du scraping : {str(e)}"