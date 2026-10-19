import math

def calculer_esperance_croisee(force_off_A, vuln_def_B, moyenne_ligue):
    """Moteur A : Espérance offensive croisée"""
    if moyenne_ligue <= 0: return 1.0
    return (force_off_A * vuln_def_B) / moyenne_ligue

def calculer_dynamique_temporelle(buts_recents, buts_historiques):
    """Moteur B : Dynamique temporelle (Delta)"""
    if not buts_recents or not buts_historiques: return 0.0
    moy_rec = sum(buts_recents) / len(buts_recents)
    moy_hist = sum(buts_historiques) / len(buts_historiques)
    return moy_rec - moy_hist

def calculer_conversion(buts, xg, epsilon=0.1):
    """Moteur C : Efficacité de conversion"""
    return (buts + epsilon) / (xg + epsilon)

def evaluer_dispersion(probabilites):
    """
    Moteur F : Mesure le désaccord entre les modèles.
    Prend une liste de probabilités (ex: [0.45, 0.52, 0.48]) et calcule la variance.
    """
    if len(probabilites) < 2: return 0.0
    moyenne = sum(probabilites) / len(probabilites)
    variance = sum((p - moyenne) ** 2 for p in probabilites) / len(probabilites)
    return variance

def interpreter_dispersion(variance):
    """Interprète l'indice de dispersion pour ajuster la confiance"""
    if variance < 0.0005:
        return "🟢 Faible dispersion : Les modèles sont d'accord. Confiance élevée."
    elif variance < 0.002:
        return "🟡 Dispersion modérée : Légères divergences. Confiance standard."
    else:
        return "🔴 Forte dispersion : Les modèles se contredisent. Prudence extrême requise."
