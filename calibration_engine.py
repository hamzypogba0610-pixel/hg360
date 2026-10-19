import math

def calibrer_lambda_hybride(lam_base, lam_avance, mu, n_matchs, k=5):
    """
    Fusionne le modèle de base (Poisson) et le modèle avancé (Stats) 
    en utilisant un poids de confiance dynamique.
    Si les modèles divergent, on applique un "Shrinkage d'urgence" vers la moyenne.
    """
    # Si le mode expert n'est pas activé, on retourne simplement le modèle de base
    if lam_avance is None or lam_avance == lam_base:
        return lam_base, 1.0 # (Lambda, Poids de confiance)

    # 1. Calcul de la divergence (l'écart entre les deux experts)
    # Si l'écart est grand, la divergence est forte.
    ecart = abs(lam_base - lam_avance)
    moyenne_lam = (lam_base + lam_avance) / 2.0
    divergence = ecart / moyenne_lam if moyenne_lam > 0 else 0

    # 2. Calcul du poids de confiance (W)
    # Si les experts sont proches, W est proche de 1. S'ils sont éloignés, W baisse.
    w_confiance = 1.0 / (1.0 + divergence)

    # 3. Moyenne pondérée des deux experts
    lam_fusionne = (lam_base * 0.5) + (lam_avance * 0.5)

    # 4. Le "Juge" intervient : on applique le shrinkage pondéré par la confiance
    # Si W est bas (grosse dispute), on tire fortement vers mu.
    poids_echantillon = n_matchs / (n_matchs + k)
    poids_final = w_confiance * poids_echantillon
    
    lam_final = (lam_fusionne * poids_final) + (mu * (1 - poids_final))

    return lam_final, poids_final
