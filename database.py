import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "hg360_database.db"

def initialiser_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table historique des paris
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, match TEXT, ligue TEXT, lambda_a REAL, lambda_b REAL,
            marche TEXT, probabilite REAL, cote_book REAL, ev REAL, mise_kelly REAL,
            resultat INTEGER DEFAULT NULL
        )
    """)
    # Table bankroll
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bankroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, type TEXT, montant REAL, description TEXT
        )
    """)
    # NOUVEAU : Table mémoire GAMMA-X (R3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoire_equipes (
            equipe TEXT PRIMARY KEY,
            erreur_moyenne REAL DEFAULT 0.0,
            nb_observations INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def ajouter_analyse(match, ligue, lam_a, lam_b, marche, proba, cote, ev, kelly):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
        INSERT INTO historique (date, match, ligue, lambda_a, lambda_b, marche, probabilite, cote_book, ev, mise_kelly)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date_str, match, ligue, lam_a, lam_b, marche, proba, cote, ev, kelly))
    conn.commit()
    conn.close()

def recuperer_historique():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM historique ORDER BY id DESC", conn)
    conn.close()
    return df

def recuperer_memoire_equipe(equipe):
    """Récupère l'erreur moyenne mémorisée pour une équipe (R3)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT erreur_moyenne FROM memoire_equipes WHERE equipe = ?", (equipe,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def mettre_a_jour_memoire(equipe, erreur_actuelle, alpha=0.3):
    """Met à jour la mémoire (Moyenne Mobile Exponentielle)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT erreur_moyenne, nb_observations FROM memoire_equipes WHERE equipe = ?", (equipe,))
    result = cursor.fetchone()
    
    if result:
        ancienne_erreur, nb_obs = result
        nouvelle_erreur = (alpha * erreur_actuelle) + ((1 - alpha) * ancienne_erreur)
        cursor.execute("UPDATE memoire_equipes SET erreur_moyenne = ?, nb_observations = ? WHERE equipe = ?", (nouvelle_erreur, nb_obs + 1, equipe))
    else:
        cursor.execute("INSERT INTO memoire_equipes (equipe, erreur_moyenne, nb_observations) VALUES (?, ?, 1)", (equipe, erreur_actuelle))
        
    conn.commit()
    conn.close()

def maj_resultat(id_pari, resultat):
    """Met à jour le résultat et APPREND de l'erreur pour GAMMA-X"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Récupérer les infos du pari
    cursor.execute("SELECT match, probabilite FROM historique WHERE id = ?", (id_pari,))
    row = cursor.fetchone()
    
    if row:
        match_str, proba_pct = row
        proba = proba_pct / 100.0
        # L'erreur est la différence entre le résultat (1 ou 0) et la proba
        erreur = resultat - proba 
        
        # 2. Extraire les noms d'équipes (ex: "Arsenal - Chelsea")
        if " - " in match_str:
            equipe_A, equipe_B = match_str.split(" - ")
            mettre_a_jour_memoire(equipe_A.strip(), erreur)
            mettre_a_jour_memoire(equipe_B.strip(), erreur)

    cursor.execute("UPDATE historique SET resultat = ? WHERE id = ?", (resultat, id_pari))
    conn.commit()
    conn.close()

def vider_historique():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM historique")
    conn.commit()
    conn.close()

def ajouter_transaction(type_trans, montant, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO bankroll (date, type, montant, description) VALUES (?, ?, ?, ?)", (date_str, type_trans, montant, description))
    conn.commit()
    conn.close()

def recuperer_solde():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT type, montant FROM bankroll", conn)
    conn.close()
    if df.empty: return 0.0
    solde = 0.0
    for index, row in df.iterrows():
        if row['type'] in ['depot', 'gain']: solde += row['montant']
        else: solde -= row['montant']
    return solde

initialiser_db()
