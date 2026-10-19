import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me
import dixon_coles as dc
import asian_handicap as ah
import staking as sk
import pandas as pd
import datetime

# 1. Configuration & CSS
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
st.markdown('<p class="sub-title">Modèle ULTIMATE (xG + Stats Avancées)</p>', unsafe_allow_html=True)

if "historique" not in st.session_state:
    st.session_state.historique = []

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=70)
    st.header("Panneau de contrôle")
    st.success("🟢 Moteurs chargés :\n- Poisson / xG\n- Indices Avancés\n- Dixon-Coles\n- Handicap\n- Kelly")
    st.caption("HYPER-GOALS 360 V2.2")
    
    if len(st.session_state.historique) > 0:
        st.markdown("---")
        df_export = pd.DataFrame(st.session_state.historique)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Télécharger l'historique", data=csv, file_name=f"hg360_{datetime.date.today()}.csv", mime="text/csv")

with st.form("prediction_form"):
    st.subheader("📊 1. Statistiques de Base")
    ligue_choisie = st.selectbox("🏆 Compétition", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏠 Équipe A (Domicile)")
        equipe_A = st.text_input("Nom de l'équipe A", placeholder="Ex: Arsenal")
        n_A = st.number_input("Matchs pris en compte (A)", min_value=1, value=15, step=1, help="Idéalement 10 dom + 5 récents")
        M_A_brut = st.number_input("xG (ou Buts) marqués par A", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.5")
        E_A_brut = st.number_input("xGA (ou Buts) encaissés par A", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.0")
    with col2:
        st.markdown("### ✈️ Équipe B (Extérieur)")
        equipe_B = st.text_input("Nom de l'équipe B", placeholder="Ex: Chelsea")
        n_B = st.number_input("Matchs pris en compte (B)", min_value=1, value=15, step=1, help="Idéalement 10 ext + 5 récents")
        M_B_brut = st.number_input("xG (ou Buts) marqués par B", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.2")
        E_B_brut = st.number_input("xGA (ou Buts) encaissés par B", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.1")

    # --- NOUVEAU : MODE EXPERT (Stats avancées) ---
    with st.expander("⚙️ Mode Expert : Statistiques Avancées (Optionnel)"):
        st.write("Ajoute ces données pour affiner l'indice de force offensive et défensive (O et V).")
        
        col_exp_A, col_exp_B = st.columns(2)
        with col_exp_A:
            st.markdown(f"**{equipe_A if equipe_A else 'Équipe A'}**")
            tirs_A = st.number_input("Tirs par match (A)", min_value=0.0, value=None, step=0.1)
            cadres_A = st.number_input("Tirs cadrés par match (A)", min_value=0.0, value=None, step=0.1)
            occasions_A = st.number_input("Grosses occasions (A)", min_value=0.0, value=None, step=0.1)
            
        with col_exp_B:
            st.markdown(f"**{equipe_B if equipe_B else 'Équipe B'}**")
            tirs_B = st.number_input("Tirs par match (B)", min_value=0.0, value=None, step=0.1)
            cadres_B = st.number_input("Tirs cadrés par match (B)", min_value=0.0, value=None, step=0.1)
            occasions_B = st.number_input("Grosses occasions (B)", min_value=0.0, value=None, step=0.1)
    # -----------------------------------------------
    
    st.markdown("---")
    st.subheader("💰 2. Cotes & Paramètres")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        mu = st.number_input("Moyenne de buts (μ)", min_value=0.1, value=None, step=0.1, placeholder="Ex: 1.3")
        ligne_ou = st.number_input("Ligne Over/Under", min_value=0.5, max_value=10.0, value=2.5, step=0.25)
        cote_ou = st.number_input(f"Cote Over {ligne_ou}", min_value=1.01, value=None, step=0.05, placeholder="Ex: 1.85")
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
        cote_1 = st.number_input(f"Victoire {equipe_A if equipe_A else 'A'}", min_value=1.01, value=None, step=0.05)
    with col_1x2_2:
        cote_X = st.number_input("Match Nul", min_value=1.01, value=None, step=0.05)
    with col_1x2_3:
        cote_2 = st.number_input(f"Victoire {equipe_B if equipe_B else 'B'}", min_value=1.01, value=None, step=0.05)

    submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

if submit:
    if equipe_A and equipe_B and M_A_brut is not None and E_A_brut is not None and M_B_brut is not None and E_B_brut is not None and mu is not None:
        
        # 1. Shrinkage
        M_A = me.appliquer_shrinkage(M_A_brut, n_A, mu)
        E_A = me.appliquer_shrinkage(E_A_brut, n_A, mu)
        M_B = me.appliquer_shrinkage(M_B_brut, n_B, mu)
        E_B = me.appliquer_shrinkage(E_B_brut, n_B, mu)
        
        # 2. Calcul des indices de force (O et V) si Mode Expert rempli
        multiplicateur_A = 1.0
        multiplicateur_B = 1.0
        
        if all(v is not None for v in [tirs_A, cadres_A, occasions_A, tirs_B, cadres_B, occasions_B]):
            # Indice Offensif A vs Indice Défensif B
            indice_off_A = me.calculer_indice_force(M_A, tirs_A, cadres_A, occasions_A, mu)
            indice_def_B = me.calculer_indice_force(E_B, tirs_B, cadres_B, occasions_B, mu) # E_B représente les tirs concédés
            multiplicateur_A = (indice_off_A + indice_def_B) / 2.0
            
            # Indice Offensif B vs Indice Défensif A
            indice_off_B = me.calculer_indice_force(M_B, tirs_B, cadres_B, occasions_B, mu)
            indice_def_A = me.calculer_indice_force(E_A, tirs_A, cadres_A, occasions_A, mu)
            multiplicateur_B = (indice_off_B + indice_def_A) / 2.0
            st.info("⚙️ Mode Expert activé : Les indices de Tirs/Cadrés/Occasions ont été intégrés au calcul.")
        
        # 3. Calcul des Lambdas
        lam_A = me.calculer_lambda(M_A, E_B, mu) * multiplicateur_A
        lam_B = me.calculer_lambda(M_B, E_A, mu) * multiplicateur_B
        matrice_dc = dc.appliquer_correction(lam_A, lam_B, rho)
        
        st.success(f"✅ Analyse terminée : **{equipe_A}** vs **{equipe_B}**")
        
        poids_A = n_A / (n_A + 5) * 100
        poids_B = n_B / (n_B + 5) * 100
        st.caption(f"📊 **Shrinkage** : Confiance de {poids_A:.0f}% dans les stats de {equipe_A} et {poids_B:.0f}% dans celles de {equipe_B}.")
        
        over_line_dc = sum(p for (i, j), p in matrice_dc.items() if i + j > ligne_ou)
        push_line = sum(p for (i, j), p in matrice_dc.items() if i + j == ligne_ou)
        under_line_dc = sum(p for (i, j), p in matrice_dc.items() if i + j < ligne_ou)
        p_btts = sum(p for (i, j), p in matrice_dc.items() if i > 0 and j > 0)
        p_A = sum(p for (i, j), p in matrice_dc.items() if i > j)
        p_Nul = sum(p for (i, j), p in matrice_dc.items() if i == j)
        p_B = sum(p for (i, j), p in matrice_dc.items() if i < j)
        
        res_ah = ah.calculer_handicap_asiatique(lam_A, lam_B, ligne_choisie)
        p_win_ah = res_ah["win"] if res_ah["type"] == "normal" else res_ah["full_win"] + 0.5 * res_ah["half_win"]

        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric(label=f"xG Ajusté (λ) - {equipe_A}", value=f"{lam_A:.2f}")
        col_res2.metric(label=f"xG Ajusté (λ) - {equipe_B}", value=f"{lam_B:.2f}")
        col_res3.metric(label="Total Buts Attendus", value=f"{lam_A + lam_B:.2f}")
        
        st.markdown("### 📋 Récapitulatif des Marchés")
        data = []
        
        data.append([f"Over {ligne_ou}", f"{over_line_dc*100:.1f}%", f"{sk.calculer_cote_equitable(over_line_dc):.2f}", f"{cote_ou:.2f}" if cote_ou else "-", f"{sk.calculer_ev(over_line_dc, cote_ou)*100:+.1f}%" if cote_ou else "-", f"{sk.calculer_kelly(over_line_dc, cote_ou)*100:.1f}%" if cote_ou else "-"])
        if push_line > 0:
            data.append([f"Push {ligne_ou} (Remboursé)", f"{push_line*100:.1f}%", "-", "-", "-", "-"])
        data.append([f"Under {ligne_ou}", f"{under_line_dc*100:.1f}%", f"{sk.calculer_cote_equitable(under_line_dc):.2f}", "-", "-", "-"])
        
        data.append(["BTTS (Oui)", f"{p_btts*100:.1f}%", f"{sk.calculer_cote_equitable(p_btts):.2f}", f"{cote_btts:.2f}" if cote_btts else "-", f"{sk.calculer_ev(p_btts, cote_btts)*100:+.1f}%" if cote_btts else "-", f"{sk.calculer_kelly(p_btts, cote_btts)*100:.1f}%" if cote_btts else "-"])
        data.append([f"Victoire {equipe_A}", f"{p_A*100:.1f}%", f"{sk.calculer_cote_equitable(p_A):.2f}", f"{cote_1:.2f}" if cote_1 else "-", f"{sk.calculer_ev(p_A, cote_1)*100:+.1f}%" if cote_1 else "-", f"{sk.calculer_kelly(p_A, cote_1)*100:.1f}%" if cote_1 else "-"])
        data.append(["Match Nul", f"{p_Nul*100:.1f}%", f"{sk.calculer_cote_equitable(p_Nul):.2f}", f"{cote_X:.2f}" if cote_X else "-", f"{sk.calculer_ev(p_Nul, cote_X)*100:+.1f}%" if cote_X else "-", f"{sk.calculer_kelly(p_Nul, cote_X)*100:.1f}%" if cote_X else "-"])
        data.append([f"Victoire {equipe_B}", f"{p_B*100:.1f}%", f"{sk.calculer_cote_equitable(p_B):.2f}", f"{cote_2:.2f}" if cote_2 else "-", f"{sk.calculer_ev(p_B, cote_2)*100:+.1f}%" if cote_2 else "-", f"{sk.calculer_kelly(p_B, cote_2)*100:.1f}%" if cote_2 else "-"])
        data.append([f"Handicap A ({ligne_choisie})", f"{p_win_ah*100:.1f}%", f"{sk.calculer_cote_equitable(p_win_ah):.2f}", f"{cote_ah:.2f}" if cote_ah else "-", f"{sk.calculer_ev(p_win_ah, cote_ah)*100:+.1f}%" if cote_ah else "-", f"{sk.calculer_kelly(p_win_ah, cote_ah)*100:.1f}%" if cote_ah else "-"])
        
        df_markets = pd.DataFrame(data, columns=["Marché", "Probabilité", "Cote Équitable", "Cote Book", "EV", "Mise Kelly"])
        st.dataframe(
            df_markets.style.format({"Probabilité": "{}", "Cote Équitable": "{}", "Cote Book": "{}", "EV": "{}", "Mise Kelly": "{}"}).map(lambda x: 'color: #00e676' if isinstance(x, str) and x.startswith('+') else ('color: #ff5252' if isinstance(x, str) and x.startswith('-') and x != '-' else 'color: white'), subset=["EV"]),
            use_container_width=True, hide_index=True
        )

        st.markdown(f"### 🎯 Matrice des Scores (ρ={rho})")
        matrice_scores = [[matrice_dc.get((i, j), 0) * 100 for j in range(5)] for i in range(5)]
        df_scores = pd.DataFrame(matrice_scores, index=[f"{i} but(s) {equipe_A}" for i in range(5)], columns=[f"{j} but(s) {equipe_B}" for j in range(5)])
        st.dataframe(df_scores.style.format("{:.1f} %").background_gradient(cmap="Greens", axis=None), use_container_width=True)

    else:
        st.warning("⚠️ Veuillez remplir tous les champs de base.")
