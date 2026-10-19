import math_engine as me

def calculer_handicap_asiatique(lam_A, lam_B, handicap):
    """
    Calcule les probabilités du Handicap Asiatique pour une équipe A.
    Le handicap s'applique à A (ex: -1, -0.5, -0.25, +0.75...).
    """
    # On calcule la probabilité de chaque score de 0-0 à 10-10 pour avoir une matrice précise
    matrice_probas = {}
    total_proba = 0.0
    for i in range(11):
        for j in range(11):
            p = me.calculer_score_exact(lam_A, lam_B, i, j)
            matrice_probas[(i, j)] = p
            total_proba += p
            
    # On normalise pour être sûr que le total fait 100%
    for k in matrice_probas:
        matrice_probas[k] /= total_proba

    # On détermine si c'est une ligne quart (ex: -0.25, +0.75) ou une ligne normale (-0.5, -1)
    est_quart = (handicap % 0.5 != 0)

    if not est_quart:
        # LIGNE ENTIÈRE OU DEMI-LIGNE
        p_win, p_push, p_lose = 0.0, 0.0, 0.0
        for (i, j), p in matrice_probas.items():
            marge_A = i - j
            resultat = marge_A + handicap
            if resultat > 0:
                p_win += p
            elif resultat == 0:
                p_push += p
            else:
                p_lose += p
        return {"win": p_win, "push": p_push, "lose": p_lose, "type": "normal"}
        
    else:
        # LIGNE QUART (On coupe la mise en deux)
        # Ex: -0.25 devient -0.5 et 0
        h_inf = handicap - 0.25
        h_sup = handicap + 0.25
        
        full_win, half_win, push, half_lose, full_lose = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for (i, j), p in matrice_probas.items():
            marge_A = i - j
            
            r_inf = marge_A + h_inf
            r_sup = marge_A + h_sup
            
            # Logique du quart de ligne
            if r_inf > 0 and r_sup > 0:
                full_win += p
            elif r_inf == 0 and r_sup > 0:
                half_win += p
            elif r_inf < 0 and r_sup == 0:
                half_lose += p
            elif r_inf < 0 and r_sup < 0:
                full_lose += p
            elif r_inf == 0 and r_sup == 0: # Ne devrait pas arriver, mais sécurité
                push += p
                
        return {
            "full_win": full_win, 
            "half_win": half_win, 
            "push": push,
            "half_lose": half_lose,
            "full_lose": full_lose, 
            "type": "quart"
                                        }
