import math

def appliquer_shrinkage(valeur_equipe, n_matchs, moyenne_ligue, k=5):
    """
    Ajuste la statistique de l'équipe vers la moyenne de la ligue si l'échantillon est petit.
    w = n / (n + k)
    """
    if n_matchs <= 0:
        return moyenne_ligue
    w = n_matchs / (n_matchs + k)
    return (w * valeur_equipe) + ((1 - w) * moyenne_ligue)

def calculer_lambda(moyenne_buts_equipe, moyenne_buts_encaisses_adversaire, moyenne_ligue, beta=0.5):
    if moyenne_buts_equipe <= 0 or moyenne_buts_encaisses_adversaire <= 0 or moyenne_ligue <= 0:
        return 1.0  
    ratio_attaque = moyenne_buts_equipe / moyenne_ligue
    ratio_defense = moyenne_buts_encaisses_adversaire / moyenne_ligue
    lambda_val = moyenne_ligue * (ratio_attaque ** beta) * (ratio_defense ** beta)
    return lambda_val

def proba_poisson(k, lam):
    if k < 0:
        return 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def proba_over_under(lam_A, lam_B, ligne=2.5):
    lam_totale = lam_A + lam_B
    proba_under = 0.0
    proba_push = 0.0
    
    if ligne % 1 == 0:
        limite = int(ligne)
        proba_under = sum(proba_poisson(k, lam_totale) for k in range(0, limite))
        proba_push = proba_poisson(limite, lam_totale)
        proba_over = 1 - proba_under - proba_push
    else:
        limite = int(ligne)
        proba_under = sum(proba_poisson(k, lam_totale) for k in range(0, limite + 1))
        proba_over = 1 - proba_under
        
    return proba_over, proba_under, proba_push

def calculer_score_exact(lam_A, lam_B, score_A, score_B):
    proba_A = proba_poisson(score_A, lam_A)
    proba_B = proba_poisson(score_B, lam_B)
    return proba_A * proba_B
