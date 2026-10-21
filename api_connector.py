import requests
import streamlit as st
from datetime import datetime, timedelta

CODES_LIGUES = {
    "EPL": "PL", "CHAMPIONSHIP": "ELC", "BUNDES": "BL1", "SERIEA": "SA",
    "LALIGA": "PD", "LIGUE1": "FL1", "DED": "DED", "PPL": "PPL",
    "BSA": "BSA", "UCL": "CL", "EURO": "EC", "WORLD_CUP": "WC"
}

@st.cache_data(ttl=3600)
def recuperer_liste_equipes(code_ligue, api_key):
    if code_ligue not in CODES_LIGUES:
        return []
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    try:
        url = f"https://api.football-data.org/v4/competitions/{code_api}/teams"
        reponse = requests.get(url, headers=headers)
        if reponse.status_code == 200:
            equipes = reponse.json().get("teams", [])
            return sorted([eq.get("name") for eq in equipes])
        return []
    except Exception:
        return []

def extraire_score_valide(match_data):
    """
    Extrait le score d'un match en essayant plusieurs sources.
    Ordre de priorité : regularTime (90 min) -> fullTime -> extraTime
    Retourne (home_score, away_score) ou (None, None) si aucun score valide.
    """
    score = match_data.get("score", {})
    
    # Essai 1 : regularTime (score à la fin du temps réglementaire)
    rt = score.get("regularTime", {}) or {}
    if rt.get("home") is not None and rt.get("away") is not None:
        return rt["home"], rt["away"]
    
    # Essai 2 : fullTime (score à la fin du match, peut inclure prolongations)
    ft = score.get("fullTime", {}) or {}
    if ft.get("home") is not None and ft.get("away") is not None:
        return ft["home"], ft["away"]
    
    # Essai 3 : extraTime (score après prolongations)
    et = score.get("extraTime", {}) or {}
    if et.get("home") is not None and et.get("away") is not None:
        return et["home"], et["away"]
    
    # Aucun score disponible
    return None, None

def recuperer_stats_equipe(nom_equipe, code_ligue, api_key):
    if code_ligue not in CODES_LIGUES:
        return {"erreur": "Compétition non disponible."}
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    try:
        url_equipes = f"https://api.football-data.org/v4/competitions/{code_api}/teams"
        reponse = requests.get(url_equipes, headers=headers)
        if reponse.status_code != 200:
            return {"erreur": f"Erreur API ({reponse.status_code})."}
        equipes = reponse.json().get("teams", [])
        equipe_id = None
        nom_officiel = nom_equipe
        recherche = nom_equipe.lower().strip()
        
        for eq in equipes:
            if recherche in eq.get("name", "").lower() or recherche in eq.get("shortName", "").lower() or recherche == eq.get("tla", "").lower():
                equipe_id = eq["id"]
                nom_officiel = eq["name"]
                break
                
        if not equipe_id:
            liste_dispo = [eq.get("name") for eq in equipes]
            return {"erreur": f"Introuvable. Équipes dispos : {', '.join(liste_dispo)}"}
        
        # NOUVEAU : On récupère 40 matchs au lieu de 15 (pour compenser les scores vides en UCL)
        url_matchs = f"https://api.football-data.org/v4/teams/{equipe_id}/matches?status=FINISHED&limit=40"
        matchs = requests.get(url_matchs, headers=headers).json().get("matches", [])
        
        if not matchs: 
            return {"erreur": "Aucun match terminé trouvé pour cette équipe."}
        
        bm, be = 0, 0
        matchs_valides = 0
        
        # On parcourt les matchs et on essaie plusieurs sources de score
        for m in matchs:
            home_score, away_score = extraire_score_valide(m)
            
            if home_score is None or away_score is None:
                continue  # Match vraiment vide (forfait, annulé, données manquantes)
            
            if m["homeTeam"]["id"] == equipe_id:
                bm += home_score
                be += away_score
            else:
                bm += away_score
                be += home_score
            
            matchs_valides += 1
            
            # On s'arrête dès qu'on a 15 matchs valides (comme la fenêtre standard)
            if matchs_valides >= 15:
                break
        
        # Vérification de la qualité de l'échantillon
        if matchs_valides == 0:
            return {"erreur": "Aucun match avec score valide trouvé (données API incomplètes)."}
        
        # Calcul des moyennes
        moy_marques = round(bm / matchs_valides, 2)
        moy_encaisses = round(be / matchs_valides, 2)
        
        # On retourne les stats avec un avertissement si l'échantillon est petit
        result = {
            "nom": nom_officiel, 
            "matchs": matchs_valides, 
            "moy_marques": moy_marques, 
            "moy_encaisses": moy_encaisses
        }
        
        # Alerte si on a moins de 10 matchs valides (données peu fiables)
        if matchs_valides < 10:
            result["alerte"] = f"⚠️ Seulement {matchs_valides} matchs valides trouvés (données incomplètes sur cette compétition)."
        
        return result
        
    except Exception as e:
        return {"erreur": f"Erreur : {str(e)}"}

def recuperer_moyenne_ligue(code_ligue, api_key):
    if code_ligue not in CODES_LIGUES:
        return 2.5
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    try:
        url = f"https://api.football-data.org/v4/competitions/{code_api}/standings"
        reponse = requests.get(url, headers=headers)
        if reponse.status_code != 200: return 2.5
        standings = reponse.json().get("standings", [])
        if not standings: return 2.5
        
        buts_total = 0
        matchs_total = 0
        for groupe in standings:
            for eq in groupe["table"]:
                buts_total += eq["goalsFor"]
                matchs_total += eq["playedGames"]
                
        if matchs_total == 0: return 2.5
        return round(buts_total / (matchs_total / 2), 2)
    except Exception:
        return 2.5

def recuperer_prochains_matchs(code_ligue, api_key, limite=5, jours_max=None):
    if code_ligue not in CODES_LIGUES:
        return []
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    
    try:
        url = f"https://api.football-data.org/v4/competitions/{code_api}/matches?status=SCHEDULED"
        reponse = requests.get(url, headers=headers)
        if reponse.status_code != 200: 
            return []
        
        matchs_api = reponse.json().get("matches", [])
        aujourd_hui = datetime.now().date()
        
        matchs_filtres = []
        for m in matchs_api:
            date_match_str = m["utcDate"][:10]
            date_match = datetime.strptime(date_match_str, "%Y-%m-%d").date()
            
            if jours_max is not None:
                limite_date = aujourd_hui + timedelta(days=jours_max)
                if aujourd_hui <= date_match <= limite_date:
                    matchs_filtres.append(m)
            else:
                matchs_filtres.append(m)
        
        matchs_filtres = matchs_filtres[:limite]
        
        resultats = []
        for m in matchs_filtres:
            resultats.append({
                "equipe_A": m["homeTeam"].get("name", m["homeTeam"].get("shortName")),
                "equipe_B": m["awayTeam"].get("name", m["awayTeam"].get("shortName")),
                "date": m["utcDate"][:10]
            })
        return resultats
    except Exception:
        return []
