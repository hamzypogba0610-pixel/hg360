import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "hg360_database.db"

def initialiser_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table pour l'historique des Value Bets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, match TEXT, ligue TEXT, lambda_a REAL, lambda_b REAL,
            marche TEXT, probabilite REAL, cote_book REAL, ev REAL, mise_kelly REAL
        )
    """)
    # Table pour la Bankroll (Portefeuille)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bankroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, type TEXT, montant REAL, description TEXT
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

def vider_historique():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM historique")
    conn.commit()
    conn.close()

# --- NOUVELLES FONCTIONS BANKROLL ---

def ajouter_transaction(type_trans, montant, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
        INSERT INTO bankroll (date, type, montant, description) VALUES (?, ?, ?, ?)
    """, (date_str, type_trans, montant, description))
    conn.commit()
    conn.close()

def recuperer_solde():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT type, montant FROM bankroll", conn)
    conn.close()
    if df.empty:
        return 0.0
    # Dépôt = +, Retrait/Pari = -
    solde = 0.0
    for index, row in df.iterrows():
        if row['type'] == 'depot' or row['type'] == 'gain':
            solde += row['montant']
        else:
            solde -= row['montant']
    return solde

def recuperer_transactions():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM bankroll ORDER BY id DESC", conn)
    conn.close()
    return df

initialiser_db()
