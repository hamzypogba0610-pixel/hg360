import math

def calculer_memoire_adaptative(erreur_precedente, erreur_actuelle, alpha=0.3):
    """
    Module R3 : Mémoire adaptative des erreurs.
    M_t = alpha * e_t + (1 - alpha) * M_{t-1}
    """
    if erreur_precedente is None:
        return erreur_actuelle
    return (alpha * erreur_actuelle) + ((1 - alpha) * erreur_precedente)

def appliquer_correction_multiplicative(lambda_base, erreur_memoire, eta=0.2):
    """
    Module R5 : Correction contrôlée des intensités.
    Corrige lambda de manière exponentielle pour éviter les valeurs négatives.
    eta (η) est le taux de correction (0 à 1).
    """
    # On limite l'impact de l'erreur pour éviter une explosion du lambda
    delta = max(-1.5, min(1.5, erreur_memoire)) 
    return lambda_base * math.exp(eta * delta)

def detecter_changement_regime(erreur_actuelle, ecart_type_historique, seuil=2.0):
    """
    Module R8 : Détection de dérive.
    """
    if ecart_type_historique == 0:
        return False
    z_score = abs(erreur_actuelle) / ecart_type_historique
    return z_score > seuil
