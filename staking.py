def calculer_cote_equitable(probabilite):
    """
    Transforme une probabilité (ex: 0.55) en cote équitable (ex: 1.81).
    """
    if probabilite <= 0:
        return 0.0
    return 1.0 / probabilite

def calculer_ev(probabilite, cote_bookmaker):
    """
    Calcule l'Espérance de Valeur (Expected Value).
    EV > 0 = Bon pari. EV < 0 = Mauvais pari.
    """
    if cote_bookmaker <= 1.0:
        return 0.0
    return (probabilite * cote_bookmaker) - 1.0

def calculer_kelly(probabilite, cote_bookmaker, fraction_kelly=0.25):
    """
    Calcule la mise optimale selon le Critère de Kelly.
    On utilise 1/4 de Kelly (fraction=0.25) pour être prudent et éviter la faillite.
    Retourne un pourcentage de la banque à miser (ex: 0.05 = 5%).
    """
    if cote_bookmaker <= 1.0:
        return 0.0
        
    b = cote_bookmaker - 1.0
    p = probabilite
    q = 1.0 - p
    
    # Formule de Kelly classique : (bp - q) / b
    kelly_brut = (b * p - q) / b
    
    if kelly_brut <= 0:
        return 0.0 # Pas de value, on ne mise pas
        
    # On applique la fraction (1/4) pour réduire le risque
    mise = kelly_brut * fraction_kelly
    
    # Sécurité : on ne mise jamais plus de 5% de sa banque sur un seul pari
    return min(mise, 0.05)
