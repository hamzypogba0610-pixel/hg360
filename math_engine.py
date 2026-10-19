import math

def calculer_lambda(moyenne_buts_equipe, moyenne_buts_encaisses_adversaire, moyenne_ligue, beta=0.5):
    """
    Calcule les buts attendus (lambda) en utilisant la formule log-ratio.
    Si beta=0.5, cela équivaut exactement à la moyenne géométrique de notre modèle HBP-360.
    """
    # Sécurité : si une moyenne est à 0 ou négative, on évite de planter
    if moyenne_buts_equipe <= 0 or moyenne_buts_encaisses_adversaire <= 0 or moyenne_ligue <= 0:
        return 1.0  
        
    # Formule mathématique du modèle
    ratio_attaque = moyenne_buts_equipe / moyenne_ligue
    ratio_defense = moyenne_buts_encaisses_adversaire / moyenne_ligue
    
    lambda_val = moyenne_ligue * (ratio_attaque ** beta) * (ratio_defense ** beta)
    return lambda_val

def proba_poisson(k, lam):
    """
    Calcule la probabilité d'avoir exactement 'k' buts sachant la moyenne 'lam' (Loi de Poisson).
    """
    if k < 0:
        return 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def proba_over_under(lam_A, lam_B, ligne=2.5):
    """
    Calcule les probabilités Over et Under pour une ligne de buts (par défaut 2.5).
    """
    lam_totale = lam_A + lam_B
    
    # Pour une ligne de 2.5 : Under = 0, 1 ou 2 buts. Over = 3 buts ou plus.
    if ligne == 2.5:
        proba_under = sum(proba_poisson(k, lam_totale) for k in range(0, 3))
        proba_over = 1 - proba_under
        return proba_over, proba_under
        
    # Pour les autres lignes entières (ex: 1.5, 3.5)
    limite = int(ligne)
    proba_under = sum(proba_poisson(k, lam_totale) for k in range(0, limite + 1))
    proba_over = 1 - proba_under
    return proba_over, proba_under

def calculer_score_exact(lam_A, lam_B, score_A, score_B):
    """
    Calcule la probabilité d'un score exact (ex: 2-1)
    """
    proba_A = proba_poisson(score_A, lam_A)
    proba_B = proba_poisson(score_B, lam_B)
    return proba_A * proba_B
