import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me
import dixon_coles as dc
import asian_handicap as ah
import staking as sk
import api_connector as api
import calibration_engine as ce
import calibration_v5 as cal5
import database as db
import pandas as pd
import datetime
import os
import math

# 1. Configuration & CSS Premium
st.set_page_config(page_title="HYPER-GOALS 360 | Pro", page_icon="⚽", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #090a0f 0%, #161b26 100%); background-attachment: fixed; }
    h1, h2, h3 { color: #FFFFFF; font-family: 'Helvetica Neue', sans-serif; }
    .main-title { color: #FFFFFF; font-weight: 900; font-size: 3.5rem; text-align: center; margin-bottom: 0px; text-shadow: 0px 0px 20px rgba(76, 175, 80, 0.4); }
    .sub-title { color: #4CAF50; font-weight: 500; font-size: 1.2rem; text-align: center; margin-bottom: 40px; letter-spacing: 2px; text-transform: uppercase; }
    div[data-testid="stForm"] { background: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); }
    div.stButton > button { background: linear-gradient(90deg, #00c853, #00e676); color: #000000; border-radius: 12px; border: none; padding: 15px 30px; font-weight: 800; font-size: 1.2rem; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4); }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 200, 83, 0.6); }
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: #1E2129; border-radius: 10px; padding: 10px 20px; color: #FFF; }
    .stTabs [aria-selected="true"] { background-color: #4CAF50; color: #000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚽ HYPER-GOALS 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Ultimate V5 (Modèle Prédictif)</p>', unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=50)
    st.header("💼 Mon Portefeuille")
    solde = db.recuperer_solde()
    st.metric(label="Bankroll Actuelle", value=f"{solde:.2f} €")
    
    with st.expander("Gérer mon argent"):
        with st.form("form_bankroll"):
            type_trans = st.selectbox("Type", ["Dépôt", "Retrait", "Gain (Pari gagné)"])
            montant = st.number_input("Montant (€)", min_value=1.0, step=10.0)
            desc = st.text_input("Description")
            if st.form_submit_button("Valider"):
                t = "depot" if type_trans == "Dépôt" else ("retrait" if type_trans == "Retrait" else "gain")
                db.ajouter_transaction(t, montant, desc)
                st.rerun()
                
    st.markdown("---")
    st.header("Configuration API")
    api_key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
    if api_key:
        st.success("✅ Clé API connectée.")
    else:
        api_key = st.text_input("Clé API Football-Data.org", type="password")
    
    st.markdown("---")
    st.subheader("📁 Historique des Value Bets")
    df_hist = db.recuperer_historique()
    if not df_hist.empty:
        csv = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Télécharger l'historique", data=csv, file_name=f"hg360_{datetime.date.today()}.csv", mime="text/csv")
        if st.button("🗑️ Effacer l'historique"):
            db.vider_historique()
            st.rerun()
    else:
        st.caption("Aucun pari enregistré.")
    st.caption("HYPER-GOALS 360 V5.0")

# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🔍 Analyse Simple", "📡 Radar Multi-Matchs", "📊 Calibration & Brier"])

# ==========================================
# ONGLET 1 : ANALYSE SIMPLE (Partie Formulaire)
# ==========================================
with tab1:
    st.subheader("📊 1. Sélection du Match")
    liste_affichage = list(CHAMPIONNATS.keys()) + ["COUPE_NATIONALE"]
    ligue_choisie = st.selectbox("🏆 Compétition", options=liste_affichage, format_func=lambda x: CHAMPIONNATS.get(x, "Coupe Nationale (Hybride)"))
    
    if ligue_choisie == "COUPE_NATIONALE":
        st.info("🛡️ Mode Coupe : Sélectionne le championnat d'origine des deux équipes.")
        col_cup1, col_cup2 = st.columns(2)
        with col_cup1:
            ligue_A = st.selectbox("Ligue d'origine de l'équipe A", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x], key="ligue_cup_A")
        with col_cup2:
            ligue_B = st.selectbox("Ligue d'origine de l'équipe B", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x], key="ligue_cup_B")
    else:
        ligue_A = ligue_choisie
        ligue_B = ligue_choisie

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            equipe_A = st.text_input("Nom de l'équipe A (Domicile)", placeholder="Ex: PSG")
        with col2:
            equipe_B = st.text_input("Nom de l'équipe B (Extérieur)", placeholder="Ex: Marseille")
            
        st.markdown("---")
        st.subheader("⚙️ 2. Récupération des Données")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            bouton_recup = st.form_submit_button("🔄 Récupérer Stats Équipes")
        with col_btn2:
            bouton_mu = st.form_submit_button("🔄 Récupérer Moyenne (μ)")
        
        if bouton_mu:
            if not api_key: st.error("Clé API requise.")
            else:
                with st.spinner("Calcul de la moyenne..."):
                    mu_auto = api.recuperer_moyenne_ligue(ligue_A, api_key)
                    st.session_state.mu_auto = mu_auto
                    st.success(f"Moyenne (μ) trouvée : {mu_auto}")

        if bouton_recup:
            if not api_key: st.error("Clé API requise.")
            elif not equipe_A or not equipe_B: st.error("Écris les noms des deux équipes.")
            else:
                with st.spinner("Recherche des données..."):
                    stats_A = api.recuperer_stats_equipe(equipe_A, ligue_A, api_key)
                    stats_B = api.recuperer_stats_equipe(equipe_B, ligue_B, api_key)
                    
                    if "erreur" in stats_A or "erreur" in stats_B:
                        st.error(stats_A.get("erreur", stats_B.get("erreur", "Erreur")))
                    else:
                        st.session_state.stats_auto_A = stats_A
                        st.session_state.stats_auto_B = stats_B
                        st.success("✅ Données récupérées !")
        
        defaut_A_marques = st.session_state.stats_auto_A["moy_marques"] if "stats_auto_A" in st.session_state else None
        defaut_A_encaisses = st.session_state.stats_auto_A["moy_encaisses"] if "stats_auto_A" in st.session_state else None
        defaut_A_matchs = st.session_state.stats_auto_A["matchs"] if "stats_auto_A" in st.session_state else 15
        defaut_B_marques = st.session_state.stats_auto_B["moy_marques"] if "stats_auto_B" in st.session_state else None
        defaut_B_encaisses = st.session_state.stats_auto_B["moy_encaisses"] if "stats_auto_B" in st.session_state else None
        defaut_B_matchs = st.session_state.stats_auto_B["matchs"] if "stats_auto_B" in st.session_state else 15
        defaut_mu = st.session_state.mu_auto if "mu_auto" in st.session_state else 2.8

        st.markdown("**Statistiques de Base (Modifiables) :**")
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**{equipe_A.strip() if equipe_A else 'Équipe A'}**")
            n_A = st.number_input("Matchs (A)", min_value=1, value=defaut_A_matchs, step=1)
            M_A_brut = st.number_input("Buts/xG marqués (A)", min_value=0.0, value=defaut_A_marques, step=0.1)
            E_A_brut = st.number_input("Buts/xG encaissés (A)", min_value=0.0, value=defaut_A_encaisses, step=0.1)
        with colB:
            st.markdown(f"**{equipe_B.strip() if equipe_B else 'Équipe B'}**")
            n_B = st.number_input("Matchs (B)", min_value=1, value=defaut_B_matchs, step=1)
            M_B_brut = st.number_input("Buts/xG marqués (B)", min_value=0.0, value=defaut_B_marques, step=0.1)
            E_B_brut = st.number_input("Buts/xG encaissés (B)", min_value=0.0, value=defaut_B_encaisses, step=0.1)

        with st.expander("⚙️ Mode Expert : Statistiques Avancées"):
            col_exp_A, col_exp_B = st.columns(2)
            with col_exp_A:
                tirs_A = st.number_input("Tirs/m (A)", min_value=0.0, value=None, step=0.1)
                cadres_A = st.number_input("Tirs cadrés/m (A)", min_value=0.0, value=None, step=0.1)
                occasions_A = st.number_input("Grosses occ. (A)", min_value=0.0, value=None, step=0.1)
            with col_exp_B:
                tirs_B = st.number_input("Tirs/m (B)", min_value=0.0, value=None, step=0.1)
                cadres_B = st.number_input("Tirs cadrés/m (B)", min_value=0.0, value=None, step=0.1)
                occasions_B = st.number_input("Grosses occ. (B)", min_value=0.0, value=None, step=0.1)

        # --- NOUVEAU : MODE V5 (Domination) ---
        with st.expander("🔥 Mode V5 : Domination & Contexte (Optionnel)"):
            st.write("Si tu renseignes ces données, le bot boostera ou pénalisera les buts attendus (λ).")
            col_v5_A, col_v5_B = st.columns(2)
            with col_v5_A:
                st.markdown(f"**{equipe_A.strip() if equipe_A else 'Équipe A'}**")
                pos_A = st.number_input("Possession moyenne (%) (A)", min_value=0.0, value=None, step=1.0, placeholder="Ex: 55")
                box_A = st.number_input("Entrées dans la surface (A)", min_value=0.0, value=None, step=1.0, placeholder="Ex: 18")
                ppda_A = st.number_input("PPDA (Pressing) (A)", min_value=1.0, value=None, step=0.1, placeholder="Ex: 8.5")
                qual_A = st.selectbox("Qualité des adversaires affrontés (A)", options=[1, 2, 3, 4, 5], index=2, help="1=Faible, 3=Moyen, 5=Très fort")
            with col_v5_B:
                st.markdown(f"**{equipe_B.strip() if equipe_B else 'Équipe B'}**")
                pos_B = st.number_input("Possession moyenne (%) (B)", min_value=0.0, value=None, step=1.0, placeholder="Ex: 45")
                box_B = st.number_input("Entrées dans la surface (B)", min_value=0.0, value=None, step=1.0, placeholder="Ex: 12")
                ppda_B = st.number_input("PPDA (Pressing) (B)", min_value=1.0, value=None, step=0.1, placeholder="Ex: 11.2")
                qual_B = st.selectbox("Qualité des adversaires affrontés (B)", options=[1, 2, 3, 4, 5], index=2, help="1=Faible, 3=Moyen, 5=Très fort")

        st.markdown("---")
        st.subheader("💰 3. Cotes & Paramètres")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            mu = st.number_input("Moyenne de buts (μ)", min_value=0.1, value=defaut_mu, step=0.1)
            ligne_ou = st.number_input("Ligne Over/Under", min_value=0.5, max_value=10.0, value=2.5, step=0.25)
            cote_ou = st.number_input(f"Cote Over {ligne_ou}", min_value=1.01, value=None, step=0.05)
        with col_c2:
            lignes_ah = [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
            ligne_choisie = st.selectbox("Ligne Handicap A", options=lignes_ah, index=8)
            cote_ah = st.number_input(f"Cote Handicap ({ligne_choisie})", min_value=1.01, value=None, step=0.05)
        with col_c3:
            cote_btts = st.number_input("Cote BTTS (Oui)", min_value=1.01, value=None, step=0.05)
            rho = st.slider("Paramètre Rho (ρ)", min_value=-0.15, max_value=0.15, value=-0.05, step=0.01)

        st.markdown("**Cotes 1X2**")
        col_1x2_1, col_1x2_2, col_1x2_3 = st.columns(3)
        with col_1x2_1:
            cote_1 = st.number_input(f"Victoire {equipe_A.strip() if equipe_A else 'A'}", min_value=1.01, value=None, step=0.05)
        with col_1x2_2:
            cote_X = st.number_input("Match Nul", min_value=1.01, value=None, step=0.05)
        with col_1x2_3:
            cote_2 = st.number_input(f"Victoire {equipe_B.strip() if equipe_B else 'B'}", min_value=1.01, value=None, step=0.05)

        submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

    # --- RÉSULTATS ANALYSE SIMPLE ---
    if submit:
        if equipe_A and equipe_B and M_A_brut is not None and E_A_brut is not None and M_B_brut is not None and E_B_brut is not None and mu is not None:
            
            nom_A = equipe_A.strip()
            nom_B = equipe_B.strip()
            
            # 1. Shrinkage & Lambdas de base
            M_A = me.appliquer_shrinkage(M_A_brut, n_A, mu)
            E_A = me.appliquer_shrinkage(E_A_brut, n_A, mu)
            M_B = me.appliquer_shrinkage(M_B_brut, n_B, mu)
            E_B = me.appliquer_shrinkage(E_B_brut, n_B, mu)
            
            lam_A_base = me.calculer_lambda(M_A, E_B, mu)
            lam_B_base = me.calculer_lambda(M_B, E_A, mu)
            
            # 2. Modèle Oméga (Hybride xG + Stats)
            lam_A_avance = None
            lam_B_avance = None
            if all(v is not None for v in [tirs_A, cadres_A, occasions_A, tirs_B, cadres_B, occasions_B]):
                indice_off_A = me.calculer_indice_force(M_A, tirs_A, cadres_A, occasions_A, mu)
                indice_def_B = me.calculer_indice_force(E_B, tirs_B, cadres_B, occasions_B, mu)
                lam_A_avance = (lam_A_base * (indice_off_A + indice_def_B) / 2.0)
                indice_off_B = me.calculer_indice_force(M_B, tirs_B, cadres_B, occasions_B, mu)
                indice_def_A = me.calculer_indice_force(E_A, tirs_A, cadres_A, occasions_A, mu)
                lam_B_avance = (lam_B_base * (indice_off_B + indice_def_A) / 2.0)

            lam_A, confiance_A = ce.calibrer_lambda_hybride(lam_A_base, lam_A_avance, mu, n_A)
            lam_B, confiance_B = ce.calibrer_lambda_hybride(lam_B_base, lam_B_avance, mu, n_B)
            
            # 3. Application de l'Indice de Domination V5
            if all(v is not None for v in [pos_A, box_A, ppda_A, pos_B, box_B, ppda_B]):
                indice_A = me.calculer_indice_v5(pos_A, box_A, ppda_A, qual_A)
                indice_B = me.calculer_indice_v5(pos_B, box_B, ppda_B, qual_B)
                
                impact_A = math.exp(0.5 * (indice_A - 1))
                impact_B = math.exp(0.5 * (indice_B - 1))
                
                lam_A = lam_A * impact_A
                lam_B = lam_B * impact_B
                st.info(f"🔥 Indice de Domination V5 appliqué : Impact A = x{impact_A:.2f} | Impact B = x{impact_B:.2f}")

            matrice_dc = dc.appliquer_correction(lam_A, lam_B, rho)
            
            st.success(f"✅ Analyse V5 terminée : **{nom_A}** vs **{nom_B}**")
            if confiance_A > 0.8 and confiance_B > 0.8: st.info("🟢 Calibration Oméga Optimale.")
            elif confiance_A > 0.5 and confiance_B > 0.5: st.warning("🟡 Calibration Modérée.")
            else: st.error("🔴 Calibration Prudente (Conflit).")

            # 4. Intervalles et Affichage
            ci_A_bas, ci_A_haut = me.calculer_intervalle_confiance(lam_A, n_A)
            ci_B_bas, ci_B_haut = me.calculer_intervalle_confiance(lam_B, n_B)
            
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric(f"λ V5 - {nom_A}", f"{lam_A:.2f}", f"IC90: [{ci_A_bas:.2f} - {ci_A_haut:.2f}]", delta_color="off")
            col_res2.metric(f"λ V5 - {nom_B}", f"{lam_B:.2f}", f"IC90: [{ci_B_bas:.2f} - {ci_B_haut:.2f}]", delta_color="off")
            col_res3.metric("Total Buts", f"{lam_A + lam_B:.2f}")
            
            # 5. Monte Carlo
            with st.expander("🎲 Simulation Monte Carlo (10 000 matchs)", expanded=True):
                mc_resultats = cal5.simuler_monte_carlo(lam_A, lam_B, n_simulations=10000)
                col_mc1, col_mc2, col_mc3 = st.columns(3)
                col_mc1.metric("Over 2.5 (MC)", f"{mc_resultats['over_25']*100:.1f}%")
                col_mc2.metric("BTTS (MC)", f"{mc_resultats['btts']*100:.1f}%")
                col_mc3.metric("Victoire A (MC)", f"{mc_resultats['victoire_A']*100:.1f}%")

            # 6. Marchés
            over_line = sum(p for (i, j), p in matrice_dc.items() if i + j > ligne_ou)
            push_line = sum(p for (i, j), p in matrice_dc.items() if i + j == ligne_ou)
            under_line = sum(p for (i, j), p in matrice_dc.items() if i + j < ligne_ou)
            p_btts = sum(p for (i, j), p in matrice_dc.items() if i > 0 and j > 0)
            p_A = sum(p for (i, j), p in matrice_dc.items() if i > j)
            p_Nul = sum(p for (i, j), p in matrice_dc.items() if i == j)
            p_B = sum(p for (i, j), p in matrice_dc.items() if i < j)
            
            res_ah = ah.calculer_handicap_asiatique(lam_A, lam_B, ligne_choisie)
            p_win_ah = res_ah["win"] if res_ah["type"] == "normal" else res_ah["full_win"] + 0.5 * res_ah["half_win"]

            nom_match = f"{nom_A} - {nom_B}"
            nom_ligue = CHAMPIONNATS.get(ligue_choisie, "Coupe Nationale")
            
            # Enregistrement
            if cote_ou and sk.calculer_ev(over_line, cote_ou) > 0:
                db.ajouter_analyse(nom_match, nom_ligue, lam_A, lam_B, f"Over {ligne_ou}", over_line*100, cote_ou, sk.calculer_ev(over_line, cote_ou)*100, sk.calculer_kelly(over_line, cote_ou)*100)
            if cote_btts and sk.calculer_ev(p_btts, cote_btts) > 0:
                db.ajouter_analyse(nom_match, nom_ligue, lam_A, lam_B, "BTTS (Oui)", p_btts*100, cote_btts, sk.calculer_ev(p_btts, cote_btts)*100, sk.calculer_kelly(p_btts, cote_btts)*100)
            if cote_1 and sk.calculer_ev(p_A, cote_1) > 0:
                db.ajouter_analyse(nom_match, nom_ligue, lam_A, lam_B, f"Victoire {nom_A}", p_A*100, cote_1, sk.calculer_ev(p_A, cote_1)*100, sk.calculer_kelly(p_A, cote_1)*100)
            if cote_X and sk.calculer_ev(p_Nul, cote_X) > 0:
                db.ajouter_analyse(nom_match, nom_ligue, lam_A, lam_B, "Match Nul", p_Nul*100, cote_X, sk.calculer_ev(p_Nul, cote_X)*100, sk.calculer_kelly(p_Nul, cote_X)*100)
            if cote_2 and sk.calculer_ev(p_B, cote_2) > 0:
                db.ajouter_analyse(nom_match, nom_ligue, lam_A, lam_B, f"Victoire {nom_B}", p_B*100, cote_2, sk.calculer_ev(p_B, cote_2)*100, sk.calculer_kelly(p_B, cote_2)*100)
            if cote_ah and sk.calculer_ev(p_win_ah, cote_ah) > 0:
                db.ajouter_analyse(nom_match, nom_ligue, lam_A, lam_B, f"Handicap {ligne_choisie}", p_win_ah*100, cote_ah, sk.calculer_ev(p_win_ah, cote_ah)*100, sk.calculer_kelly(p_win_ah, cote_ah)*100)

            st.markdown("### 📋 Récapitulatif des Marchés")
            data = []
            data.append([f"Over {ligne_ou}", f"{over_line*100:.1f}%", f"{sk.calculer_cote_equitable(over_line):.2f}", f"{cote_ou:.2f}" if cote_ou else "-", f"{sk.calculer_ev(over_line, cote_ou)*100:+.1f}%" if cote_ou else "-", f"{sk.calculer_kelly(over_line, cote_ou)*100:.1f}%" if cote_ou else "-"])
            if push_line > 0: data.append([f"Push {ligne_ou}", f"{push_line*100:.1f}%", "-", "-", "-", "-"])
            data.append([f"Under {ligne_ou}", f"{under_line*100:.1f}%", f"{sk.calculer_cote_equitable(under_line):.2f}", "-", "-", "-"])
            data.append(["BTTS (Oui)", f"{p_btts*100:.1f}%", f"{sk.calculer_cote_equitable(p_btts):.2f}", f"{cote_btts:.2f}" if cote_btts else "-", f"{sk.calculer_ev(p_btts, cote_btts)*100:+.1f}%" if cote_btts else "-", f"{sk.calculer_kelly(p_btts, cote_btts)*100:.1f}%" if cote_btts else "-"])
            data.append([f"Victoire {nom_A}", f"{p_A*100:.1f}%", f"{sk.calculer_cote_equitable(p_A):.2f}", f"{cote_1:.2f}" if cote_1 else "-", f"{sk.calculer_ev(p_A, cote_1)*100:+.1f}%" if cote_1 else "-", f"{sk.calculer_kelly(p_A, cote_1)*100:.1f}%" if cote_1 else "-"])
            data.append(["Match Nul", f"{p_Nul*100:.1f}%", f"{sk.calculer_cote_equitable(p_Nul):.2f}", f"{cote_X:.2f}" if cote_X else "-", f"{sk.calculer_ev(p_Nul, cote_X)*100:+.1f}%" if cote_X else "-", f"{sk.calculer_kelly(p_Nul, cote_X)*100:.1f}%" if cote_X else "-"])
            data.append([f"Victoire {nom_B}", f"{p_B*100:.1f}%", f"{sk.calculer_cote_equitable(p_B):.2f}", f"{cote_2:.2f}" if cote_2 else "-", f"{sk.calculer_ev(p_B, cote_2)*100:+.1f}%" if cote_2 else "-", f"{sk.calculer_kelly(p_B, cote_2)*100:.1f}%" if cote_2 else "-"])
            data.append([f"Handicap A ({ligne_choisie})", f"{p_win_ah*100:.1f}%", f"{sk.calculer_cote_equitable(p_win_ah):.2f}", f"{cote_ah:.2f}" if cote_ah else "-", f"{sk.calculer_ev(p_win_ah, cote_ah)*100:+.1f}%" if cote_ah else "-", f"{sk.calculer_kelly(p_win_ah, cote_ah)*100:.1f}%" if cote_ah else "-"])
            
            df_markets = pd.DataFrame(data, columns=["Marché", "Probabilité", "Cote Équitable", "Cote Book", "EV", "Mise Kelly"])
            st.dataframe(df_markets.style.format({"Probabilité": "{}", "Cote Équitable": "{}", "Cote Book": "{}", "EV": "{}", "Mise Kelly": "{}"}).map(lambda x: 'color: #00e676' if isinstance(x, str) and x.startswith('+') else ('color: #ff5252' if isinstance(x, str) and x.startswith('-') and x != '-' else 'color: white'), subset=["EV"]), use_container_width=True, hide_index=True)

            st.markdown(f"### 🎯 Matrice des Scores")
            matrice_scores = [[matrice_dc.get((i, j), 0) * 100 for j in range(5)] for i in range(5)]
            df_scores = pd.DataFrame(matrice_scores, index=[f"{i} but(s) {nom_A}" for i in range(5)], columns=[f"{j} but(s) {nom_B}" for j in range(5)])
            st.dataframe(df_scores.style.format("{:.1f} %").background_gradient(cmap="Greens", axis=None), use_container_width=True)
        else:
            st.warning("⚠️ Remplis les noms et les stats.")

# ==========================================
# ONGLET 2 : RADAR MULTI-MATCHS
# ==========================================
with tab2:
    st.subheader("📡 Radar des Matchs à Venir")
    st.write("Le radar va chercher les prochains matchs de la ligue sélectionnée et calcule les probabilités de base (Over 2.5 / BTTS).")
    
    ligue_radar = st.selectbox("Choisir la ligue à scanner", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x], key="ligue_radar")
    
    if st.button("🚀 Lancer le Scanner (Max 5 matchs)"):
        if not api_key:
            st.error("Clé API requise dans le menu de gauche.")
        else:
            with st.spinner("Scan des matchs en cours..."):
                mu_radar = api.recuperer_moyenne_ligue(ligue_radar, api_key)
                matchs = api.recuperer_prochains_matchs(ligue_radar, api_key, limite=5)
                
                if not matchs:
                    st.warning("Aucun match à venir trouvé ou limite d'API atteinte.")
                else:
                    resultats_radar = []
                    
                    for m in matchs:
                        eq_A = m["equipe_A"]
                        eq_B = m["equipe_B"]
                        
                        sA = api.recuperer_stats_equipe(eq_A, ligue_radar, api_key)
                        sB = api.recuperer_stats_equipe(eq_B, ligue_radar, api_key)
                        
                        if "erreur" not in sA and "erreur" not in sB:
                            M_A = me.appliquer_shrinkage(sA["moy_marques"], sA["matchs"], mu_radar)
                            E_A = me.appliquer_shrinkage(sA["moy_encaisses"], sA["matchs"], mu_radar)
                            M_B = me.appliquer_shrinkage(sB["moy_marques"], sB["matchs"], mu_radar)
                            E_B = me.appliquer_shrinkage(sB["moy_encaisses"], sB["matchs"], mu_radar)
                            
                            lam_A = me.calculer_lambda(M_A, E_B, mu_radar)
                            lam_B = me.calculer_lambda(M_B, E_A, mu_radar)
                            
                            matrice_dc = dc.appliquer_correction(lam_A, lam_B, -0.05)
                            
                            over_25 = sum(p for (i, j), p in matrice_dc.items() if i + j > 2.5)
                            p_btts = sum(p for (i, j), p in matrice_dc.items() if i > 0 and j > 0)
                            p_A = sum(p for (i, j), p in matrice_dc.items() if i > j)
                            
                            resultats_radar.append({
                                "Date": m["date"],
                                "Match": f"{eq_A} vs {eq_B}",
                                "λ A": f"{lam_A:.2f}",
                                "λ B": f"{lam_B:.2f}",
                                "Over 2.5": f"{over_25*100:.1f}%",
                                "BTTS": f"{p_btts*100:.1f}%",
                                "Victoire A": f"{p_A*100:.1f}%"
                            })
                    
                    if resultats_radar:
                        df_radar = pd.DataFrame(resultats_radar)
                        st.dataframe(df_radar, use_container_width=True, hide_index=True)
                        st.info("💡 Pour trouver des Value Bets, compare ces probabilités avec les cotes de ton bookmaker dans l'onglet 'Analyse Simple'.")
                    else:
                        st.error("Impossible de récupérer les stats des équipes (limite API atteinte ?).")

# ==========================================
# ONGLET 3 : CALIBRATION & BRIER SCORE
# ==========================================
with tab3:
    st.subheader("📊 Dashboard de Calibration")
    st.write("Ici, tu peux vérifier si les probabilités de ton bot sont fiables (Brier Score) et lui apprendre de ses erreurs.")
    
    st.markdown("### 1. Enregistrer les résultats des paris")
    st.write("Sélectionne un pari dans l'historique pour dire s'il a été gagné ou perdu.")
    
    df_hist_cal = db.recuperer_historique()
    if df_hist_cal.empty:
        st.info("Aucun pari enregistré pour le moment. Fais des analyses pour remplir l'historique !")
    else:
        df_attente = df_hist_cal[df_hist_cal['resultat'].isna()]
        
        if not df_attente.empty:
            for index, row in df_attente.head(5).iterrows():
                col_info, col_btn_win, col_btn_lose = st.columns([3, 1, 1])
                with col_info:
                    st.write(f"**{row['match']}** - {row['marche']} (Proba: {row['probabilite']:.1f}%)")
                with col_btn_win:
                    if st.button(f"✅ Gagné", key=f"win_{row['id']}"):
                        db.maj_resultat(row['id'], 1)
                        st.rerun()
                with col_btn_lose:
                    if st.button(f"❌ Perdu", key=f"lose_{row['id']}"):
                        db.maj_resultat(row['id'], 0)
                        st.rerun()
        else:
            st.success("Tous les paris ont un résultat enregistré !")

        st.markdown("---")
        st.markdown("### 2. Évaluation de la Fiabilité (Brier Score)")
        
        df_avec_resultat = df_hist_cal[df_hist_cal['resultat'].notna()]
        
        if len(df_avec_resultat) > 0:
            import numpy as np
            probas = df_avec_resultat['probabilite'].values / 100.0
            resultats = df_avec_resultat['resultat'].astype(int).values
            
            brier = cal5.calculer_brier(probas, resultats)
            
            col_bs1, col_bs2 = st.columns(2)
            col_bs1.metric("Brier Score Actuel", f"{brier:.4f}", help="Plus c'est proche de 0, meilleur est le modèle.")
            
            if brier < 0.15:
                st.success("🟢 Excellent ! Ton modèle est très bien calibré.")
            elif brier < 0.25:
                st.warning("🟡 Moyen. Le modèle est acceptable mais peut être amélioré.")
            else:
                st.error("🔴 Faible. Le modèle est trop confiant ou pas assez. Il faut le recalibrer.")
                
            st.markdown("### 3. Couche de Recalibrage")
            st.write("Voici ce que donneraient tes probabilités après ajustement mathématique :")
            
            probas_platt = [cal5.platt_scaling(p, A=1.0, B=0.0) for p in probas]
            brier_platt = cal5.calculer_brier(probas_platt, resultats)
            
            probas_temp = [cal5.temperature_scaling(p, T=1.5) for p in probas]
            brier_temp = cal5.calculer_brier(probas_temp, resultats)
            
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("Brier Original", f"{brier:.4f}")
            col_r2.metric("Brier Platt Scaling", f"{brier_platt:.4f}")
            col_r3.metric("Brier Temp Scaling", f"{brier_temp:.4f}")
            
            st.info("💡 Si une méthode de recalibrage donne un Brier Score plus bas, c'est qu'elle corrige mieux les erreurs du bot.")
            
        else:
            st.warning("⚠️ Il faut enregistrer au moins un résultat (Gagné/Perdu) pour calculer le Brier Score.")
