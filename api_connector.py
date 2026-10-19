import requests

CODES_LIGUES = {
    "EPL": "PL", "CHAMPIONSHIP": "ELC", "BUNDES": "BL1", "SERIEA": "SA",
    "LALIGA": "PD", "LIGUE1": "FL1", "DED": "DED", "PPL": "PPL",
    "BSA": "BSA", "UCL": "CL", "EURO": "EC", "WORLD_CUP": "WC"
}

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
            
        url_matchs = f"https://api.football-data.org/v4/teams/{equipe_id}/matches?status=FINISHED&limit=15"
        matchs = requests.get(url_matchs, headers=headers).json().get("matches", [])
        if not matchs: return {"erreur": "Pas assez de matchs."}
        
        bm, be = 0, 0
        for m in matchs:
            if m["homeTeam"]["id"] == equipe_id:
                bm += m["score"]["fullTime"]["home"]; be += m["score"]["fullTime"]["away"]
            else:
                bm += m["score"]["fullTime"]["away"]; be += m["score"]["fullTime"]["home"]
                
        return {"nom": nom_officiel, "matchs": len(matchs), "moy_marques": round(bm/len(matchs), 2), "moy_encaisses": round(be/len(matchs), 2)}
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

# --- NOUVELLE FONCTION : RADAR DES MATCHS ---
def recuperer_prochains_matchs(code_ligue, api_key, limite=5):
    """Récupère les prochains matchs programmés d'une ligue (max 5 pour l'API)"""
    if code_ligue not in CODES_LIGUES:
        return []
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    try:
        url = f"https://api.football-data.org/v4/competitions/{code_api}/matches?status=SCHEDULED"
        reponse = requests.get(url, headers=headers)
        if reponse.status_code != 200: return []
        
        matchs = reponse.json().get("matches", [])
        # On ne garde que les X premiers pour ne pas exploser la limite de l'API
        matchs = matchs[:limite]
        
        resultats = []
        for m in matchs:
            resultats.append({
                "equipe_A": m["homeTeam"].get("name", m["homeTeam"].get("shortName")),
                "equipe_B": m["awayTeam"].get("name", m["awayTeam"].get("shortName")),
                "date": m["utcDate"][:10] # Garde juste la date AAAA-MM-JJ
            })
        return resultats
    except Exception:
        return []
