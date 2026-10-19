import requests

# Correspondance entre nos menus et les codes du site de l'API
CODES_LIGUES = {
    "EPL": "PL",
    "CHAMPIONSHIP": "ELC",
    "BUNDES": "BL1",
    "SERIEA": "SA",
    "LALIGA": "PD",
    "LIGUE1": "FL1",
    "DED": "DED",
    "PPL": "PPL",
    "BSA": "BSA",
    "UCL": "CL",
    "EURO": "EC",
    "WORLD_CUP": "WC"
}

def recuperer_stats_equipe(nom_equipe, code_ligue, api_key):
    if code_ligue not in CODES_LIGUES:
        return {"erreur": "Cette compétition n'est pas disponible avec l'API."}
        
    code_api = CODES_LIGUES[code_ligue]
    headers = {"X-Auth-Token": api_key}
    
    try:
        # 1. On cherche la liste des équipes de la compétition
        url_equipes = f"https://api.football-data.org/v4/competitions/{code_api}/teams"
        reponse = requests.get(url_equipes, headers=headers)
        
        if reponse.status_code != 200:
            return {"erreur": f"Erreur API (Code {reponse.status_code}). Vérifie ta clé."}
            
        equipes = reponse.json().get("teams", [])
        equipe_id = None
        nom_officiel = nom_equipe
        
        # On nettoie le nom tapé (minuscules, sans espaces superflus)
        recherche = nom_equipe.lower().strip()
        
        # 2. On cherche l'équipe (nom complet, nom court ou abréviation)
        for eq in equipes:
            nom_api = eq.get("name", "").lower()
            nom_court = eq.get("shortName", "").lower()
            abreviation = eq.get("tla", "").lower()
            
            if recherche in nom_api or recherche in nom_court or recherche == abreviation:
                equipe_id = eq["id"]
                nom_officiel = eq["name"]
                break
                
        # 3. Si l'équipe n'est pas trouvée, on affiche la liste des équipes disponibles
        if not equipe_id:
            liste_dispo = [eq.get("name") for eq in equipes]
            return {"erreur": f"Équipe '{nom_equipe}' introuvable. Voici les équipes disponibles dans cette compétition : {', '.join(liste_dispo)}"}
            
        # 4. On récupère les 15 derniers matchs terminés
        url_matchs = f"https://api.football-data.org/v4/teams/{equipe_id}/matches?status=FINISHED&limit=15"
        reponse_matchs = requests.get(url_matchs, headers=headers)
        matchs = reponse_matchs.json().get("matches", [])
        
        if not matchs:
            return {"erreur": "Pas assez de matchs terminés pour cette équipe."}
            
        buts_marques = 0
        buts_encaisses = 0
        nb_matchs = len(matchs)
        
        # 5. On calcule les moyennes de buts
        for m in matchs:
            if m["homeTeam"]["id"] == equipe_id:
                buts_marques += m["score"]["fullTime"]["home"]
                buts_encaisses += m["score"]["fullTime"]["away"]
            else:
                buts_marques += m["score"]["fullTime"]["away"]
                buts_encaisses += m["score"]["fullTime"]["home"]
                
        return {
            "nom": nom_officiel,
            "matchs": nb_matchs,
            "moy_marques": round(buts_marques / nb_matchs, 2),
            "moy_encaisses": round(buts_encaisses / nb_matchs, 2)
        }
        
    except Exception as e:
        return {"erreur": f"Problème de connexion internet : {str(e)}"}
