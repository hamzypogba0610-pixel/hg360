# ⚽ HYPER-GOALS 360 - Ultimate V4

**HYPER-GOALS 360** est un bot d'analyse probabiliste et de prédiction football de niveau professionnel. Conçu pour être utilisé sur mobile, il combine des modèles mathématiques avancés (Poisson, Dixon-Coles), une calibration hybride (Modèle Oméga), et une connexion API pour automatiser la récupération des données.

## 🚀 Fonctionnalités (V4)

- **Modèle Mathématique** : Loi de Poisson corrigée par Dixon-Coles.
- **Calibration Oméga** : Fusion intelligente entre les xG et les statistiques avancées (Tirs, Occasions), avec sécurité en cas de conflit.
- **Connexion API** : Récupération automatique des 15 derniers matchs via Football-Data.org.
- **Auto-μ** : Calcul automatique de la moyenne de buts du championnat.
- **Marchés Supportés** : Over/Under (avec gestion du Push), 1X2, BTTS, Handicap Asiatique (lignes entières/demi/quart).
- **Gestion de Bankroll** : Calcul de l'EV, Cote Équitable, et Mise Kelly fractionnaire (plafonnée à 5%).
- **Base de Données Persistante** : Sauvegarde automatique des Value Bets et suivi du portefeuille via SQLite.
- **Radar Multi-Matchs** : Scanner pour analyser les prochaines rencontres en un clic.
- **Mode Hybride** : Analyse des coupes nationales (hors API) en croisant les données des championnats d'origine.
- **Export CSV** : Téléchargement de l'historique des paris détectés.

## 🛠️ Architecture Technique

- `app.py` : Interface utilisateur (Streamlit).
- `api_connector.py` : Connexion à l'API Football-Data.org.
- `math_engine.py` : Poisson, Shrinkage, Intervalles de confiance.
- `calibration_engine.py` : Modèle Oméga (Juge mathématique).
- `dixon_coles.py` : Correction des scores exacts.
- `asian_handicap.py` : Moteur du Handicap.
- `staking.py` : Formules de Kelly et d'EV.
- `database.py` : Gestion de la base de données SQLite.
- `leagues.py` : Base de données des compétitions.

## ⚠️ Avertissement (Model Card)

**Statut :** Version finale de recherche (V4.0).
Ce bot est un outil d'aide à la décision statistique. Il ne garantit aucun résultat. Le pari sportif comporte des risques. Ne misez jamais ce que vous ne pouvez pas vous permettre de perdre. Jouez de manière responsable.
