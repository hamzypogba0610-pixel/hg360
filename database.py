import sqlite3
import pandas as pd
from datetime import datetime

# Nom du fichier de base de données (il sera créé automatiquement)
DB_NAME = "hg360_database.db"

def initialiser_db():
    """Crée la table si elle n'existe pas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            match TEXT,
            ligue TEXT,
            lambda_a REAL,
            lambda_b REAL,
            marche TEXT,
            probabilite REAL,
            cote_book REAL,
            ev REAL,
            mise_kelly REAL
        )
    """)
    conn.commit()
    conn.close()

def ajouter_analyse(match, ligue, lam_a, lam_b, marche, proba, cote, ev, kelly):
    """Insère une nouvelle analyse (Value Bet) dans la base."""
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
    """Récupère tout l'historique sous forme de tableau Pandas."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM historique ORDER BY id DESC", conn)
    conn.close()
    return df

def vider_historique():
    """Efface tout l'historique."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historique")
    conn.commit()
    conn.close()

# On initialise la base au chargement du module
initialiser_db()
