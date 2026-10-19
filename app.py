import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me
import asian_handicap as ah
import staking as sk  # <--- C'EST ICI QU'ON A CORRIGÉ (sk au lieu de st)
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="HYPER-GOALS 360 | Pro", page_icon="⚽", layout="wide")

# 2. Habillage CSS Premium
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #090a0f 0%, #161b26 100%); background-attachment: fixed; }
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF; font-family: 'Helvetica Neue', sans-serif; }
    .main-title { color: #FFFFFF; font-weight: 900; font-size: 3.5rem; text-align: center; margin-bottom: 0px; text-shadow: 0px 0px 20px rgba(76, 175, 80, 0.4); }
    .sub-title { color: #4CAF50; font-weight: 500; font-size: 1.2rem; text-align: center; margin-bottom: 40px; letter-spacing: 2px; text-transform: uppercase; }
    div[data-testid="stForm"] { background: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); }
    div.stButton > button { background: linear-gradient(90deg, #00c853, #00e676); color: #000000; border-radius: 12px; border: none; padding: 15px 30px; font-weight: 800; font-size: 1.2rem; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4); }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 200, 83, 0.6); }
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    </style>
""", unsafe_allow_html=True)

# 3. En-tête
st.markdown('<p class="main-title">⚽ HYPER-GOALS 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse probabiliste</p>', unsafe_allow_html=True)

# 4. Barre latérale
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=70)
    st.header("Panneau de contrôle")
    st.info("💡 Remplis les statistiques et compare avec les cotes du bookmaker.")
    st.caption("HYPER-GOALS 360 V2.2")

# 5. Le Formulaire de saisie
with st.form("prediction_form"):
    st.subheader("📊 Statistiques du Match")
    
    ligue_choisie = st.selectbox("🏆 Compétition", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Équipe A (Domicile)")
        equipe_A = st.text_input("Nom de l'équipe A", placeholder="Ex: Arsenal")
        M_A = st.number_input("Buts marqués par A (moyenne)", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.5")
        E_A = st.number_input("Buts encaissés par A (moyenne)", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.0")
        
    with col2:
        st.markdown("### ✈️ Équipe B (Extérieur)")
        equipe_B = st.text_input("Nom de l'équipe B", placeholder="Ex: Chelsea")
        M_B = st.number_input("Buts marqués par B (moyenne)", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.2")
        E_B = st.number_input("Buts encaissés par B (moyenne)", min_value=0.0, value=None, step=0.1, placeholder="Ex: 1.1")
    
    st.markdown("---")
    
    col_param, col_ah, col_cote = st.columns(3)
    with col_param:
        mu = st.number_input("Moyenne de buts (μ)", min_value=0.1, value=None, step=0.1, placeholder="Ex: 1.3")
    
    with col_ah:
        lignes_ah = [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        ligne_choisie = st.selectbox("Handicap pour l'Équipe A", options=lignes_ah, index=8)
        
    with col_cote:
        cote_over = st.number_input("Cote Bookmaker (Over 2.5)", min_value=1.01, value=None, step=0.05, placeholder="Ex: 1.85")

    submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

# 6. Affichage des résultats
if submit:
    if equipe_A and equipe_B and M_A is not None and E_A is not None and M_B is not None and E_B is not None and mu is not None:
        
        lam_A = me.calculer_lambda(M_A, E_B, mu)
        lam_B = me.calculer_lambda(M_B, E_A, mu)
        
        st.success(f"✅ Analyse terminée : **{equipe_A}** vs **{equipe_B}**")
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric(label=f"Buts attendus (λ) - {equipe_A}", value=f"{lam_A:.2f}")
        col_res2.metric(label=f"Buts attendus (λ) - {equipe_B}", value=f"{lam_B:.2f}")
        
        over_25, under_25 = me.proba_over_under(lam_A, lam_B, 2.5)
        
        st.markdown("### 📈 Marché des Buts (Over/Under 2.5)")
        col_ou1, col_ou2 = st.columns(2)
        col_ou1.metric(label="🔴 Over 2.5", value=f"{over_25*100:.1f} %")
        col_ou2.metric(label="🟢 Under 2.5", value=f"{under_25*100:.1f} %")
        
        # --- NOUVEAU : Cote équitable, EV et Kelly ---
        if cote_over is not None:
            cote_fair = sk.calculer_cote_equitable(over_25)  # <--- CORRIGÉ ICI (sk)
            ev = sk.calculer_ev(over_25, cote_over)          # <--- CORRIGÉ ICI (sk)
            mise_kelly = sk.calculer_kelly(over_25, cote_over) # <--- CORRIGÉ ICI (sk)
            
            st.markdown("### 💰 Analyse de Valeur (Over 2.5)")
            col_v1, col_v2, col_v3 = st.columns(3)
            col_v1.metric("Cote Équitable", f"{cote_fair:.2f}")
            
            if ev > 0:
                col_v2.metric("Valeur (EV)", f"+{ev*100:.1f} %", delta="Value Bet !", delta_color="normal")
            else:
                col_v2.metric("Valeur (EV)", f"{ev*100:.1f} %", delta="Pas de value", delta_color="inverse")
                
            col_v3.metric("Mise Kelly (Bankroll)", f"{mise_kelly*100:.1f} %")
        # ---------------------------------------------

        st.markdown(f"### ⚔️ Handicap Asiatique ({ligne_choisie} pour {equipe_A})")
        resultat_ah = ah.calculer_handicap_asiatique(lam_A, lam_B, ligne_choisie)
        
        if resultat_ah["type"] == "normal":
            col_ah1, col_ah2, col_ah3 = st.columns(3)
            col_ah1.metric("Victoire", f"{resultat_ah['win']*100:.1f} %")
            col_ah2.metric("Remboursé", f"{resultat_ah['push']*100:.1f} %")
            col_ah3.metric("Défaite", f"{resultat_ah['lose']*100:.1f} %")
        else:
            col_ah1, col_ah2, col_ah3, col_ah4 = st.columns(4)
            col_ah1.metric("Gain Total", f"{resultat_ah['full_win']*100:.1f} %")
            col_ah2.metric("Gain Partiel", f"{resultat_ah['half_win']*100:.1f} %")
            col_ah3.metric("Perte Partielle", f"{resultat_ah['half_lose']*100:.1f} %")
            col_ah4.metric("Perte Totale", f"{resultat_ah['full_lose']*100:.1f} %")

        st.markdown("### 🎯 Matrice des Scores Exacts (Probabilités en %)")
        matrice_scores = []
        for buts_A in range(5):
            ligne = []
            for buts_B in range(5):
                proba = me.calculer_score_exact(lam_A, lam_B, buts_A, buts_B)
                ligne.append(proba * 100)
            matrice_scores.append(ligne)
            
        df_scores = pd.DataFrame(
            matrice_scores,
            index=[f"{i} but(s) {equipe_A}" for i in range(5)],
            columns=[f"{j} but(s) {equipe_B}" for j in range(5)]
        )
        
        st.dataframe(
            df_scores.style.format("{:.1f} %").background_gradient(cmap="Greens", axis=None),
            use_container_width=True
        )

    else:
        st.warning("⚠️ Veuillez remplir les noms et les statistiques des équipes.")
