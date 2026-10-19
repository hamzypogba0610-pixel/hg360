import requests

CODES_LIGUES = {
    "EPL": "PL", "CHAMPIONSHIP": "ELC", "BUNDES": "BL1", "SERIEA": "SA",
    "LALIGA": "PD", "LIGUE1": "FL1", "DED": "DED", "PPL": "PPL",
    "BSA": "BSA", "UCL": "CL", "EURO": "EC", "WORLD_CUP": "WC"
}

def recuperer_stats_equipe(nom_equipe, code_ligue, api_key):
    # (Le code précédent reste identique)
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

# --- NOUVELLE FONCTION : MOYENNE DE LA LIGUE ---
def recuperer_moyenne_ligue(code_ligue, api_key):
    if code_ligue not in CODES_LIGUES:
        return 2.5 # Valeur par défaut
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    
    try:
        # On récupère le classement (qui contient les stats de toutes les équipes)
        url = f"https://api.football-data.org/v4/competitions/{code_api}/standings"
        reponse = requests.get(url, headers=headers)
        if reponse.status_code != 200:
            return 2.5
            
        standings = reponse.json().get("standings", [])
        if not standings: return 2.5
        
        # On additionne tous les buts marqués et encaissés par toutes les équipes
        buts_total = 0
        matchs_total = 0
        for groupe in standings:
            for eq in groupe["table"]:
                buts_total += eq["goalsFor"]
                matchs_total += eq["playedGames"]
                
        if matchs_total == 0: return 2.5
        
        # Chaque match est compté deux fois (une fois pour l'équipe A, une fois pour l'équipe B)
        # Donc la moyenne de buts par match = total_buts / (total_matchs_joues_par_les_equipes / 2)
        moyenne = buts_total / (matchs_total / 2)
        return round(moyenne, 2)
        
    except Exception:
        return 2.5
