import numpy as np
from sklearn.metrics import brier_score_loss

def simuler_monte_carlo(lam_A, lam_B, n_simulations=10000):
    """
    Simule le match n_simulations fois et retourne les probabilités.
    """
    # On simule les buts avec une distribution de Poisson
    buts_A = np.random.poisson(lam_A, n_simulations)
    buts_B = np.random.poisson(lam_B, n_simulations)
    
    # Calcul des résultats
    over_25 = np.mean((buts_A + buts_B) > 2.5)
    under_25 = np.mean((buts_A + buts_B) < 2.5)
    btts = np.mean((buts_A > 0) & (buts_B > 0))
    victoire_A = np.mean(buts_A > buts_B)
    match_nul = np.mean(buts_A == buts_B)
    victoire_B = np.mean(buts_A < buts_B)
    
    return {
        "over_25": over_25,
        "under_25": under_25,
        "btts": btts,
        "victoire_A": victoire_A,
        "match_nul": match_nul,
        "victoire_B": victoire_B
    }

def calculer_brier(probas, resultats_reels):
    """
    Calcule le Brier Score (qualité de la calibration).
    Plus c'est proche de 0, mieux c'est.
    """
    if len(probas) == 0:
        return 0.0
    return brier_score_loss(resultats_reels, probas)

def platt_scaling(probabilite, A=1.0, B=0.0):
    """
    Ajuste la probabilité si le modèle est trop confiant ou pas assez.
    (Paramètres A et B à calibrer sur l'historique plus tard).
    """
    # Formule : 1 / (1 + exp(A * p + B))
    p_ajuste = 1 / (1 + np.exp(A * probabilite + B))
    return max(0.01, min(0.99, p_ajuste))

def temperature_scaling(probabilite, T=1.0):
    """
    Température Scaling : Rend le modèle plus ou moins confiant.
    T > 1 = moins confiant. T < 1 = plus confiant.
    """
    # Approximation pour les probabilités
    logit = np.log(probabilite / (1 - probabilite + 1e-9))
    logit_ajuste = logit / T
    return 1 / (1 + np.exp(-logit_ajuste))
