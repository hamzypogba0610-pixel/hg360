# ⚽ HYPER-GOALS 360

**HYPER-GOALS 360** est un bot de prédiction et d'analyse probabiliste pour le football, conçu pour les parieurs professionnels et les analystes de données. 

Développé avec **Python**, **Streamlit** et déployé sur **Render**, ce bot utilise un modèle statistique avancé pour estimer les buts attendus, les scores exacts et détecter les "Value Bets".

## 🚀 Fonctionnalités Principales (V3.0)

- **Mode Automatique (API)** : Récupération automatique des statistiques des 15 derniers matchs via l'API Football-Data.org.
- **Modèle de Poisson & xG** : Calcul des buts attendus (λ) basés sur les Expected Goals (xG) et la moyenne du championnat.
- **Shrinkage (Régularisation)** : Ajustement automatique des statistiques des équipes en fonction du nombre de matchs joués (fiabilité).
- **Mode Expert** : Intégration des statistiques avancées (Tirs, Tirs cadrés, Grosses occasions) pour affiner les indices offensifs et défensifs.
- **Correction Dixon-Coles** : Ajustement mathématique des probabilités des scores serrés (0-0, 1-0, 1-1) avec un curseur interactif (ρ).
- **Marchés Supportés** : 
  - Over/Under (lignes entières, demi et quarts avec gestion du "Push")
  - 1X2 (Victoire, Nul, Défaite)
  - BTTS (Les deux équipes marquent)
  - Handicap Asiatique complet (lignes entières, demi et quarts)
- **Gestion de Bankroll** : Calcul de la Cote Équitable, de l'Expected Value (EV) et de la mise optimale via la formule de Kelly fractionnaire.
- **Intervalle de Confiance** : Affichage de l'incertitude du modèle à 90% (IC90).
- **Export CSV** : Sauvegarde et téléchargement de l'historique des Value Bets détectés.

## 🛠️ Architecture Technique

Le projet est modulaire pour garantir la propreté et l'évolutivité du code :
- `app.py` : Interface utilisateur (Streamlit) et orchestration.
- `api_connector.py` : Connexion à l'API Football-Data.org.
- `math_engine.py` : Formules de base (Poisson, λ, Shrinkage, Intervalles).
- `dixon_coles.py` : Correction des scores exacts.
- `asian_handicap.py` : Moteur du marché du Handicap.
- `staking.py` : Formules de Kelly et d'Expected Value.
- `leagues.py` : Base de données des championnats supportés.

## ⚠️ Avertissement (Model Card)

**Statut :** Modèle expérimental (V3.0).
Ce bot est un outil d'aide à la décision statistique. Il ne garantit aucun résultat. Le pari sportif comporte des risques. Ne misez jamais ce que vous ne pouvez pas vous permettre de perdre. Jouez de manière responsable.
