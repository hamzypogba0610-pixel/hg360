import math

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
    if ligne == 2.5:
        proba_under = sum(proba_poisson(k, lam_totale) for k in range(0, 3))
        proba_over = 1 - proba_under
        return proba_over, proba_under
    limite = int(ligne)
    proba_under = sum(proba_poisson(k, lam_totale) for k in range(0, limite + 1))
    proba_over = 1 - proba_under
    return proba_over, proba_under

def calculer_score_exact(lam_A, lam_B, score_A, score_B):
    proba_A = proba_poisson(score_A, lam_A)
    proba_B = proba_poisson(score_B, lam_B)
    return proba_A * proba_B

# --- NOUVELLES FONCTIONS POUR LES AUTRES MARCHÉS ---

def proba_1x2(lam_A, lam_B):
    """Calcule les probabilités de Victoire A, Nul, Victoire B"""
    p_A, p_Nul, p_B = 0.0, 0.0, 0.0
    for i in range(11):
        for j in range(11):
            p = calculer_score_exact(lam_A, lam_B, i, j)
            if i > j:
                p_A += p
            elif i == j:
                p_Nul += p
            else:
                p_B += p
    return p_A, p_Nul, p_B

def proba_btts(lam_A, lam_B):
    """Calcule la probabilité que les deux équipes marquent (BTTS Oui/Non)"""
    # BTTS Non = A marque 0 OU B marque 0
    p_A_zero = sum(calculer_score_exact(lam_A, lam_B, 0, j) for j in range(11))
    p_B_zero = sum(calculer_score_exact(lam_A, lam_B, i, 0) for i in range(11))
    p_0_0 = calculer_score_exact(lam_A, lam_B, 0, 0)
    
    # On utilise la formule des probabilités : P(A U B) = P(A) + P(B) - P(A inter B)
    proba_non = p_A_zero + p_B_zero - p_0_0
    proba_oui = 1.0 - proba_non
    return proba_oui, proba_non
