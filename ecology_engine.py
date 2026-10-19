def calculer_pression_offensive(c, t, m, d, v):
    """
    Calcule le score de pression offensive sur 100.
    c = Contexte, t = Tactique, m = Moteur, d = Défense, v = Variance
    (Chaque note est sur 10, on multiplie par 10 pour avoir une base sur 100)
    """
    pression = (0.25 * (c * 10)) + (0.25 * (t * 10)) + (0.20 * (m * 10)) + (0.15 * (d * 10)) + (0.15 * (v * 10))
    return round(pression, 1)

def calculer_indice_buts(pression_A, pression_B, bonus_dynamique):
    """
    Calcule l'indice global de buts du match.
    Le bonus de dynamique va de -10 à +10.
    """
    indice = ((pression_A + pression_B) / 2) + bonus_dynamique
    # On plafonne entre 0 et 100
    return max(0, min(100, round(indice, 1)))

def interpreter_indice(indice):
    """
    Retourne la lecture du match et les marchés conseillés selon la grille.
    """
    if indice >= 75:
        return "🔥 MATCH TRÈS OUVERT", "Over (toutes lignes), BTTS, But dans les 30 premières minutes."
    elif 60 <= indice < 75:
        return "🟢 OUVERTURE MODÉRÉE", "Over 1.5, BTTS conditionnel."
    elif 45 <= indice < 60:
        return "🟡 MATCH ÉQUILIBRÉ OU FERMÉ", "Under, peu de buts, marché asiatique."
    else:
        return "🔴 FORT RISQUE DE MATCH VERROUILLÉ", "Under 2.5, 0-0 / 1-0, équipe solide défensivement."
