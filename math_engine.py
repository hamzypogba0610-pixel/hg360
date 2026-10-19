import math

def appliquer_shrinkage(valeur_equipe, n_matchs, moyenne_ligue, k=5):
    if n_matchs <= 0:
        return moyenne_ligue
    w = n_matchs / (n_matchs + k)
    return (w * valeur_equipe) + ((1 - w) * moyenne_ligue)

def calculer_lambda(moyenne_buts_equipe, moyenne_buts_encaisses_adversaire, moyenne_ligue, beta=0.5):
    if moyenne_buts_equipe <= 0 or moyenne_buts_encaisses_adversaire <= 0 or moyenne_ligue <= 0:
        return 1.0  
    ratio_attaque = moyenne_buts_equipe / moyenne_ligue
    ratio_defense = moyenne_buts_encaisses_adversaire / moyenne_ligue
    return moyenne_ligue * (ratio_attaque ** beta) * (ratio_defense ** beta)

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

def proba_1x2(lam_A, lam_B):
    p_A, p_Nul, p_B = 0.0, 0.0, 0.0
    for i in range(11):
        for j in range(11):
            p = calculer_score_exact(lam_A, lam_B, i, j)
            if i > j: p_A += p
            elif i == j: p_Nul += p
            else: p_B += p
    return p_A, p_Nul, p_B

def proba_btts(lam_A, lam_B):
    p_A_zero = sum(calculer_score_exact(lam_A, lam_B, 0, j) for j in range(11))
    p_B_zero = sum(calculer_score_exact(lam_A, lam_B, i, 0) for i in range(11))
    p_0_0 = calculer_score_exact(lam_A, lam_B, 0, 0)
    proba_non = p_A_zero + p_B_zero - p_0_0
    return 1.0 - proba_non, proba_non

def calculer_indice_force(xG, tirs, tirs_cadres, occasions, moyenne_ligue):
    ref_tirs = 12.0
    ref_tirs_cadres = 4.0
    ref_occasions = 2.0
    
    score_xg = xG / moyenne_ligue if moyenne_ligue > 0 else 1.0
    score_tirs = tirs / ref_tirs if ref_tirs > 0 else 1.0
    score_cadres = tirs_cadres / ref_tirs_cadres if ref_tirs_cadres > 0 else 1.0
    score_occasions = occasions / ref_occasions if ref_occasions > 0 else 1.0
    
    indice = (0.5 * score_xg) + (0.2 * score_tirs) + (0.2 * score_cadres) + (0.1 * score_occasions)
    return indice

# --- FONCTION RÉINTÉGRÉE (C'était le bug) ---
def calculer_intervalle_confiance(lam, n_matchs):
    erreur_standard = 1.0 / math.sqrt(n_matchs)
    marge_erreur = 1.645 * erreur_standard
    borne_basse = max(0.1, lam - marge_erreur)
    borne_haute = lam + marge_erreur
    return borne_basse, borne_haute

# --- FONCTION V5 (Domination) ---
def calculer_indice_v5(possession, entrees_surface, ppda, qualite_adversaire):
    s_pos = possession / 50.0 if possession is not None else 1.0
    s_box = entrees_surface / 15.0 if entrees_surface is not None else 1.0
    s_ppda = 10.0 / ppda if (ppda is not None and ppda > 0) else 1.0
    s_qual = qualite_adversaire / 3.0 if qualite_adversaire is not None else 1.0
    
    indice = (s_pos * 0.2) + (s_box * 0.4) + (s_ppda * 0.2) + (s_qual * 0.2)
    return indice
