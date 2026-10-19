import math_engine as me

def appliquer_correction(lam_A, lam_B, rho=-0.05):
    """
    Calcule la matrice des scores en appliquant la correction Dixon-Coles.
    rho (ρ) est par défaut à -0.05 (valeur standard pour le football).
    """
    matrice_corrigee = {}
    
    for i in range(11):
        for j in range(11):
            # On calcule la probabilité de base (Poisson)
            p_base = me.calculer_score_exact(lam_A, lam_B, i, j)
            
            # On applique le facteur de correction tau (τ) uniquement pour 0-0, 1-0, 0-1, 1-1
            tau = 1.0
            if i == 0 and j == 0:
                tau = 1 - (lam_A * lam_B * rho)
            elif i == 1 and j == 0:
                tau = 1 + (lam_B * rho)
            elif i == 0 and j == 1:
                tau = 1 + (lam_A * rho)
            elif i == 1 and j == 1:
                tau = 1 - rho
                
            matrice_corrigee[(i, j)] = p_base * tau
            
    # On normalise la matrice pour que la somme de toutes les probabilités fasse exactement 1.0
    total = sum(matrice_corrigee.values())
    for k in matrice_corrigee:
        matrice_corrigee[k] /= total
        
    return matrice_corrigee
