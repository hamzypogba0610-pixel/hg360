import requests

# On fait le lien entre nos menus et les codes du site de l'API
CODES_LIGUES = {
    "EPL": "PL",
    "LALIGA": "PD",
    "SERIEA": "SA",
    "BUNDES": "BL1",
    "LIGUE1": "FL1",
    "UCL": "CL"
}

def recuperer_stats_equipe(nom_equipe, code_ligue, api_key):
    # Si c'est une coupe qu'on n'a pas dans la liste, on s'arrête
    if code_ligue not in CODES_LIGUES:
        return {"erreur": "Cette compétition n'est pas disponible avec l'API gratuite."}
        
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    
    try:
        # 1. On cherche l'ID de l'équipe sur le site
        url_equipes = f"https://api.football-data.org/v4/competitions/{code_api}/teams"
        reponse = requests.get(url_equipes, headers=headers)
        
        if reponse.status_code != 200:
            return {"erreur": f"Clé invalide ou erreur de connexion (Code {reponse.status_code})."}
            
        equipes = reponse.json().get("teams", [])
        equipe_id = None
        nom_officiel = nom_equipe
        
        # On cherche l'équipe (ex: si tu tapes "Arsenal", il trouve "Arsenal FC")
        for eq in equipes:
            if nom_equipe.lower() in eq["name"].lower() or nom_equipe.lower() in eq.get("shortName", "").lower() or nom_equipe.lower() in eq.get("tla", "").lower():
                equipe_id = eq["id"]
                nom_officiel = eq["name"]
                break
                
        if not equipe_id:
            return {"erreur": f"Équipe '{nom_equipe}' introuvable dans cette compétition."}
            
        # 2. On récupère les 15 derniers matchs terminés
        url_matchs = f"https://api.football-data.org/v4/teams/{equipe_id}/matches?status=FINISHED&limit=15"
        reponse_matchs = requests.get(url_matchs, headers=headers)
        matchs = reponse_matchs.json().get("matches", [])
        
        if not matchs:
            return {"erreur": "Pas assez de matchs terminés pour cette équipe."}
            
        buts_marques = 0
        buts_encaisses = 0
        nb_matchs = len(matchs)
        
        # 3. On calcule les moyennes
        for m in matchs:
            if m["homeTeam"]["id"] == equipe_id:
                buts_marques += m["score"]["fullTime"]["home"]
                buts_encaisses += m["score"]["fullTime"]["away"]
            else:
                buts_marques += m["score"]["fullTime"]["away"]
                buts_encaisses += m["score"]["fullTime"]["home"]
                
        # On renvoie les résultats
        return {
            "nom": nom_officiel,
            "matchs": nb_matchs,
            "moy_marques": round(buts_marques / nb_matchs, 2),
            "moy_encaisses": round(buts_encaisses / nb_matchs, 2)
        }
        
    except Exception as e:
        return {"erreur": f"Problème de connexion internet : {str(e)}"}
