import requests
import streamlit as st
from datetime import datetime, timedelta
import math

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
    score = match_data.get("score", {})
    
    def est_valide(val):
        return val is not None and not (isinstance(val, float) and math.isnan(val))
    
    rt = score.get("regularTime", {}) or {}
    if est_valide(rt.get("home")) and est_valide(rt.get("away")):
        return rt["home"], rt["away"]
    
    ft = score.get("fullTime", {}) or {}
    if est_valide(ft.get("home")) and est_valide(ft.get("away")):
        return ft["home"], ft["away"]
    
    et = score.get("extraTime", {}) or {}
    if est_valide(et.get("home")) and est_valide(et.get("away")):
        return et["home"], et["away"]
    
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
        
        url_matchs = f"https://api.football-data.org/v4/teams/{equipe_id}/matches?status=FINISHED&limit=40"
        matchs = requests.get(url_matchs, headers=headers).json().get("matches", [])
        
        if not matchs: 
            return {"erreur": "Aucun match terminé trouvé pour cette équipe."}
        
        bm, be = 0, 0
        matchs_valides = 0
        
        for m in matchs:
            home_score, away_score = extraire_score_valide(m)
            
            if home_score is None or away_score is None:
                continue
            
            if m["homeTeam"]["id"] == equipe_id:
                bm += home_score
                be += away_score
            else:
                bm += away_score
                be += home_score
            
            matchs_valides += 1
            
            if matchs_valides >= 15:
                break
        
        if matchs_valides == 0:
            return {"erreur": "Aucun match avec score valide trouvé."}
        
        moy_marques = round(bm / matchs_valides, 2)
        moy_encaisses = round(be / matchs_valides, 2)
        
        if math.isnan(moy_marques): moy_marques = 0.0
        if math.isnan(moy_encaisses): moy_encaisses = 0.0
        
        return {
            "nom": nom_officiel, 
            "matchs": matchs_valides, 
            "moy_marques": moy_marques, 
            "moy_encaisses": moy_encaisses
        }
        
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

@st.cache_data(ttl=3600)
def recuperer_classement_ligue(code_ligue, api_key):
    """Récupère le classement complet d'une ligue avec les stats par équipe."""
    if code_ligue not in CODES_LIGUES:
        return {}
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    try:
        url = f"https://api.football-data.org/v4/competitions/{code_api}/standings"
        reponse = requests.get(url, headers=headers)
        if reponse.status_code != 200:
            return {}
        
        standings = reponse.json().get("standings", [])
        if not standings:
            return {}
        
        resultat = {}
        for groupe in standings:
            for eq in groupe["table"]:
                nom = eq["team"]["name"]
                resultat[nom] = {
                    "buts_marques": eq["goalsFor"],
                    "buts_encaisses": eq["goalsAgainst"],
                    "matchs": eq["playedGames"],
                    "points": eq["points"],
                    "difference": eq["goalDifference"]
                }
        return resultat
    except Exception:
        return {}
