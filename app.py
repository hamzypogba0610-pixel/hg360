import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me
import dixon_coles as dc
import asian_handicap as ah
import staking as sk
import api_connector as api
import calibration_engine as ce
import pandas as pd
import datetime
import os

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
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚽ HYPER-GOALS 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Ultimate V4 (Calibration Hybride)</p>', unsafe_allow_html=True)

if "historique" not in st.session_state:
    st.session_state.historique = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=70)
    st.header("Configuration API")
    
    # RECHERCHE DE LA CLÉ DANS LE SERVEUR RENDER
    api_key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
    
    if api_key:
        st.success("✅ Clé API connectée au serveur de manière sécurisée.")
    else:
        st.warning("⚠️ Clé API non trouvée dans le serveur. Entre-la manuellement ci-dessous.")
        api_key = st.text_input("Clé API Football-Data.org", type="password")
    
    st.markdown("---")
    if len(st.session_state.historique) > 0:
        df_export = pd.DataFrame(st.session_state.historique)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Télécharger l'historique", data=csv, file_name=f"hg360_{datetime.date.today()}.csv", mime="text/csv")
    st.caption("HYPER-GOALS 360 V4.0")

# --- FORMULAIRE ---
with st.form("prediction_form"):
    st.subheader("📊 1. Sélection du Match")
    ligue_choisie = st.selectbox("🏆 Compétition", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x])
    
    col1, col2 = st.columns(2)
    with col1:
        equipe_A = st.text_input("Nom de l'équipe A (Domicile)", placeholder="Ex: Arsenal")
    with col2:
        equipe_B = st.text_input("Nom de l'équipe B (Extérieur)", placeholder="Ex: Chelsea")
        
    st.markdown("---")
    st.subheader("⚙️ 2. Récupération des Données")
    
    # Bouton de récupération API
    bouton_recup = st.form_submit_button("🔄 Récupérer les stats via API")
    
    if bouton_recup:
        if not api_key:
            st.error("⚠️ Clé API manquante.")
        elif not equipe_A or not equipe_B:
            st.error("⚠️ Écris le nom des deux équipes.")
        else:
            with st.spinner("Recherche des données sur internet..."):
                stats_A = api.recuperer_stats_equipe(equipe_A, ligue_choisie, api_key)
                stats_B = api.recuperer_stats_equipe(equipe_B, ligue_choisie, api_key)
                
                if "erreur" in stats_A or "erreur" in stats_B:
                    st.error(stats_A.get("erreur", stats_B.get("erreur", "Erreur inconnue")))
                else:
                    st.session_state.stats_auto_A = stats_A
                    st.session_state.stats_auto_B = stats_B
                    st.success("✅ Données récupérées ! Vérifie les chiffres ci-dessous.")
    
    # Valeurs par défaut (remplies par l'API si le bouton a été cliqué)
    defaut_A_marques = st.session_state.stats_auto_A["moy_marques"] if "stats_auto_A" in st.session_state else None
    defaut_A_encaisses = st.session_state.stats_auto_A["moy_encaisses"] if "stats_auto_A" in st.session_state else None
    defaut_A_matchs = st.session_state.stats_auto_A["matchs"] if "stats_auto_A" in st.session_state else 15
    
    defaut_B_marques = st.session_state.stats_auto_B["moy_marques"] if "stats_auto_B" in st.session_state else None
    defaut_B_encaisses = st.session_state.stats_auto_B["moy_encaisses"] if "stats_auto_B" in st.session_state else None
    defaut_B_matchs = st.session_state.stats_auto_B["matchs"] if "stats_auto_B" in st.session_state else 15

    st.markdown("**Statistiques (Modifiables manuellement si besoin) :**")
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

    # Mode Expert
    with st.expander("⚙️ Mode Expert : Statistiques Avancées (Optionnel)"):
        col_exp_A, col_exp_B = st.columns(2)
        with col_exp_A:
            st.markdown(f"**{equipe_A.strip() if equipe_A else 'Équipe A'}**")
            tirs_A = st.number_input("Tirs par match (A)", min_value=0.0, value=None, step=0.1)
            cadres_A = st.number_input("Tirs cadrés par match (A)", min_value=0.0, value=None, step=0.1)
            occasions_A = st.number_input("Grosses occasions (A)", min_value=0.0, value=None, step=0.1)
        with col_exp_B:
            st.markdown(f"**{equipe_B.strip() if equipe_B else 'Équipe B'}**")
            tirs_B = st.number_input("Tirs par match (B)", min_value=0.0, value=None, step=0.1)
            cadres_B = st.number_input("Tirs cadrés par match (B)", min_value=0.0, value=None, step=0.1)
            occasions_B = st.number_input("Grosses occasions (B)", min_value=0.0, value=None, step=0.1)

    st.markdown("---")
    st.subheader("💰 3. Cotes & Paramètres")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        mu = st.number_input("Moyenne de buts (μ)", min_value=0.1, value=2.8, step=0.1)
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

    # Le bouton d'analyse final
    submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

# --- RÉSULTATS ---
if submit:
    if equipe_A and equipe_B and M_A_brut is not None and E_A_brut is not None and M_B_brut is not None and E_B_brut is not None and mu is not None:
        
        nom_A = equipe_A.strip()
        nom_B = equipe_B.strip()

        # 1. Shrinkage initial (Modèle de base)
        M_A = me.appliquer_shrinkage(M_A_brut, n_A, mu)
        E_A = me.appliquer_shrinkage(E_A_brut, n_A, mu)
        M_B = me.appliquer_shrinkage(M_B_brut, n_B, mu)
        E_B = me.appliquer_shrinkage(E_B_brut, n_B, mu)
        
        # 2. Lambdas de base (Poisson pur)
        lam_A_base = me.calculer_lambda(M_A, E_B, mu)
        lam_B_base = me.calculer_lambda(M_B, E_A, mu)
        
        # 3. Lambdas Avancés (Si Mode Expert rempli)
        lam_A_avance = None
        lam_B_avance = None
        
        if all(v is not None for v in [tirs_A, cadres_A, occasions_A, tirs_B, cadres_B, occasions_B]):
            indice_off_A = me.calculer_indice_force(M_A, tirs_A, cadres_A, occasions_A, mu)
            indice_def_B = me.calculer_indice_force(E_B, tirs_B, cadres_B, occasions_B, mu)
            lam_A_avance = (lam_A_base * (indice_off_A + indice_def_B) / 2.0)
            
            indice_off_B = me.calculer_indice_force(M_B, tirs_B, cadres_B, occasions_B, mu)
            indice_def_A = me.calculer_indice_force(E_A, tirs_A, cadres_A, occasions_A, mu)
            lam_B_avance = (lam_B_base * (indice_off_B + indice_def_A) / 2.0)

        # 4. CALIBRATION HYBRIDE (Le Juge Oméga)
        lam_A, confiance_A = ce.calibrer_lambda_hybride(lam_A_base, lam_A_avance, mu, n_A)
        lam_B, confiance_B = ce.calibrer_lambda_hybride(lam_B_base, lam_B_avance, mu, n_B)
        
        # 5. Dixon-Coles (Matrice corrigée)
        matrice_dc = dc.appliquer_correction(lam_A, lam_B, rho)
        
        st.success(f"✅ Analyse Hybride terminée : **{nom_A}** vs **{nom_B}**")
        
        # Affichage du statut du Juge (Calibration)
        if confiance_A > 0.8 and confiance_B > 0.8:
            st.info("🟢 Calibration Optimale : Les modèles xG et Stats Avancées sont en parfait accord.")
        elif confiance_A > 0.5 and confiance_B > 0.5:
            st.warning("🟡 Calibration Modérée : Légère divergence entre les modèles, résultat sécurisé.")
        else:
            st.error("🔴 Calibration Prudente : Les modèles sont en conflit. Le bot a ramené les estimations vers la moyenne pour éviter une erreur.")

        # Intervalles de confiance
        ci_A_bas, ci_A_haut = me.calculer_intervalle_confiance(lam_A, n_A)
        ci_B_bas, ci_B_haut = me.calculer_intervalle_confiance(lam_B, n_B)
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric(f"Buts Calibrés (λ) - {nom_A}", f"{lam_A:.2f}", f"IC90: [{ci_A_bas:.2f} - {ci_A_haut:.2f}]", delta_color="off")
        col_res2.metric(f"Buts Calibrés (λ) - {nom_B}", f"{lam_B:.2f}", f"IC90: [{ci_B_bas:.2f} - {ci_B_haut:.2f}]", delta_color="off")
        col_res3.metric("Total Buts", f"{lam_A + lam_B:.2f}")
        
        # Calcul des marchés à partir de la matrice Dixon-Coles
        over_line = sum(p for (i, j), p in matrice_dc.items() if i + j > ligne_ou)
        push_line = sum(p for (i, j), p in matrice_dc.items() if i + j == ligne_ou)
        under_line = sum(p for (i, j), p in matrice_dc.items() if i + j < ligne_ou)
        p_btts = sum(p for (i, j), p in matrice_dc.items() if i > 0 and j > 0)
        p_A = sum(p for (i, j), p in matrice_dc.items() if i > j)
        p_Nul = sum(p for (i, j), p in matrice_dc.items() if i == j)
        p_B = sum(p for (i, j), p in matrice_dc.items() if i < j)
        
        res_ah = ah.calculer_handicap_asiatique(lam_A, lam_B, ligne_choisie)
        p_win_ah = res_ah["win"] if res_ah["type"] == "normal" else res_ah["full_win"] + 0.5 * res_ah["half_win"]

        st.markdown("### 📋 Récapitulatif des Marchés")
        data = []
        
        data.append([f"Over {ligne_ou}", f"{over_line*100:.1f}%", f"{sk.calculer_cote_equitable(over_line):.2f}", f"{cote_ou:.2f}" if cote_ou else "-", f"{sk.calculer_ev(over_line, cote_ou)*100:+.1f}%" if cote_ou else "-", f"{sk.calculer_kelly(over_line, cote_ou)*100:.1f}%" if cote_ou else "-"])
        if push_line > 0:
            data.append([f"Push {ligne_ou} (Remboursé)", f"{push_line*100:.1f}%", "-", "-", "-", "-"])
        data.append([f"Under {ligne_ou}", f"{under_line*100:.1f}%", f"{sk.calculer_cote_equitable(under_line):.2f}", "-", "-", "-"])
        
        data.append(["BTTS (Oui)", f"{p_btts*100:.1f}%", f"{sk.calculer_cote_equitable(p_btts):.2f}", f"{cote_btts:.2f}" if cote_btts else "-", f"{sk.calculer_ev(p_btts, cote_btts)*100:+.1f}%" if cote_btts else "-", f"{sk.calculer_kelly(p_btts, cote_btts)*100:.1f}%" if cote_btts else "-"])
        data.append([f"Victoire {nom_A}", f"{p_A*100:.1f}%", f"{sk.calculer_cote_equitable(p_A):.2f}", f"{cote_1:.2f}" if cote_1 else "-", f"{sk.calculer_ev(p_A, cote_1)*100:+.1f}%" if cote_1 else "-", f"{sk.calculer_kelly(p_A, cote_1)*100:.1f}%" if cote_1 else "-"])
        data.append(["Match Nul", f"{p_Nul*100:.1f}%", f"{sk.calculer_cote_equitable(p_Nul):.2f}", f"{cote_X:.2f}" if cote_X else "-", f"{sk.calculer_ev(p_Nul, cote_X)*100:+.1f}%" if cote_X else "-", f"{sk.calculer_kelly(p_Nul, cote_X)*100:.1f}%" if cote_X else "-"])
        data.append([f"Victoire {nom_B}", f"{p_B*100:.1f}%", f"{sk.calculer_cote_equitable(p_B):.2f}", f"{cote_2:.2f}" if cote_2 else "-", f"{sk.calculer_ev(p_B, cote_2)*100:+.1f}%" if cote_2 else "-", f"{sk.calculer_kelly(p_B, cote_2)*100:.1f}%" if cote_2 else "-"])
        data.append([f"Handicap A ({ligne_choisie})", f"{p_win_ah*100:.1f}%", f"{sk.calculer_cote_equitable(p_win_ah):.2f}", f"{cote_ah:.2f}" if cote_ah else "-", f"{sk.calculer_ev(p_win_ah, cote_ah)*100:+.1f}%" if cote_ah else "-", f"{sk.calculer_kelly(p_win_ah, cote_ah)*100:.1f}%" if cote_ah else "-"])
        
        df_markets = pd.DataFrame(data, columns=["Marché", "Probabilité", "Cote Équitable", "Cote Book", "EV", "Mise Kelly"])
        st.dataframe(
            df_markets.style.format({"Probabilité": "{}", "Cote Équitable": "{}", "Cote Book": "{}", "EV": "{}", "Mise Kelly": "{}"}).map(lambda x: 'color: #00e676' if isinstance(x, str) and x.startswith('+') else ('color: #ff5252' if isinstance(x, str) and x.startswith('-') and x != '-' else 'color: white'), subset=["EV"]),
            use_container_width=True, hide_index=True
        )

        st.markdown(f"### 🎯 Matrice des Scores (ρ={rho})")
        matrice_scores = [[matrice_dc.get((i, j), 0) * 100 for j in range(5)] for i in range(5)]
        df_scores = pd.DataFrame(matrice_scores, index=[f"{i} but(s) {nom_A}" for i in range(5)], columns=[f"{j} but(s) {nom_B}" for j in range(5)])
        st.dataframe(df_scores.style.format("{:.1f} %").background_gradient(cmap="Greens", axis=None), use_container_width=True)

    else:
        st.warning("⚠️ Veuillez remplir les noms et les statistiques.")
