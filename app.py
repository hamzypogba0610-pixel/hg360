import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me
import asian_handicap as ah
import staking as sk
import pandas as pd

# 1. Configuration
st.set_page_config(page_title="HYPER-GOALS 360 | Pro", page_icon="⚽", layout="wide")

# 2. CSS Premium
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
st.markdown('<p class="sub-title">Tableau de Bord du Parieur</p>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=70)
    st.header("Panneau de contrôle")
    st.info("💡 Remplis les stats, entre les cotes du bookmaker, et le bot trouvera les Value Bets !")
    st.caption("HYPER-GOALS 360 V2.2")

# 5. Formulaire de saisie
with st.form("prediction_form"):
    st.subheader("📊 1. Statistiques de Base")
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
    st.subheader("💰 2. Cotes du Bookmaker (Optionnel)")
    st.write("Laisse vide si tu ne veux pas calculer la value sur ce marché.")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        mu = st.number_input("Moyenne de buts (μ)", min_value=0.1, value=None, step=0.1, placeholder="Ex: 1.3")
        cote_over = st.number_input("Cote Over 2.5", min_value=1.01, value=None, step=0.05, placeholder="Ex: 1.85")
    with col_c2:
        lignes_ah = [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        ligne_choisie = st.selectbox("Ligne Handicap A", options=lignes_ah, index=8)
        cote_ah = st.number_input(f"Cote Handicap ({ligne_choisie})", min_value=1.01, value=None, step=0.05, placeholder="Ex: 1.90")
    with col_c3:
        cote_btts = st.number_input("Cote BTTS (Oui)", min_value=1.01, value=None, step=0.05, placeholder="Ex: 1.75")
    
    st.markdown("**Cotes 1X2 (Victoire / Nul / Défaite)**")
    col_1x2_1, col_1x2_2, col_1x2_3 = st.columns(3)
    with col_1x2_1:
        cote_1 = st.number_input(f"Cote Victoire {equipe_A if equipe_A else 'A'}", min_value=1.01, value=None, step=0.05)
    with col_1x2_2:
        cote_X = st.number_input("Cote Match Nul", min_value=1.01, value=None, step=0.05)
    with col_1x2_3:
        cote_2 = st.number_input(f"Cote Victoire {equipe_B if equipe_B else 'B'}", min_value=1.01, value=None, step=0.05)

    submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

# 6. Affichage des résultats
if submit:
    if equipe_A and equipe_B and M_A is not None and E_A is not None and M_B is not None and E_B is not None and mu is not None:
        
        lam_A = me.calculer_lambda(M_A, E_B, mu)
        lam_B = me.calculer_lambda(M_B, E_A, mu)
        
        st.success(f"✅ Analyse terminée : **{equipe_A}** vs **{equipe_B}** ({CHAMPIONNATS[ligue_choisie]})")
        
        # --- TABLEAU RÉCAPITULATIF DES VALUE BETS ---
        st.markdown("### 📋 Récapitulatif des Marchés et Value Bets")
        
        # Dictionnaire pour stocker les données du tableau
        data = []
        
        # 1. Over 2.5
        over_25, _ = me.proba_over_under(lam_A, lam_B, 2.5)
        c_fair = sk.calculer_cote_equitable(over_25)
        ev = sk.calculer_ev(over_25, cote_over) if cote_over else 0
        kelly = sk.calculer_kelly(over_25, cote_over) if cote_over else 0
        data.append(["Over 2.5", f"{over_25*100:.1f}%", f"{c_fair:.2f}", f"{cote_over:.2f}" if cote_over else "-", f"{ev*100:+.1f}%" if cote_over else "-", f"{kelly*100:.1f}%" if cote_over else "-"])
        
        # 2. BTTS
        p_btts, _ = me.proba_btts(lam_A, lam_B)
        c_fair_btts = sk.calculer_cote_equitable(p_btts)
        ev_btts = sk.calculer_ev(p_btts, cote_btts) if cote_btts else 0
        kelly_btts = sk.calculer_kelly(p_btts, cote_btts) if cote_btts else 0
        data.append(["BTTS (Oui)", f"{p_btts*100:.1f}%", f"{c_fair_btts:.2f}", f"{cote_btts:.2f}" if cote_btts else "-", f"{ev_btts*100:+.1f}%" if cote_btts else "-", f"{kelly_btts*100:.1f}%" if cote_btts else "-"])
        
        # 3. 1X2
        p_A, p_Nul, p_B = me.proba_1x2(lam_A, lam_B)
        c_fair_1 = sk.calculer_cote_equitable(p_A)
        ev_1 = sk.calculer_ev(p_A, cote_1) if cote_1 else 0
        kelly_1 = sk.calculer_kelly(p_A, cote_1) if cote_1 else 0
        data.append([f"Victoire {equipe_A}", f"{p_A*100:.1f}%", f"{c_fair_1:.2f}", f"{cote_1:.2f}" if cote_1 else "-", f"{ev_1*100:+.1f}%" if cote_1 else "-", f"{kelly_1*100:.1f}%" if cote_1 else "-"])
        
        c_fair_X = sk.calculer_cote_equitable(p_Nul)
        ev_X = sk.calculer_ev(p_Nul, cote_X) if cote_X else 0
        kelly_X = sk.calculer_kelly(p_Nul, cote_X) if cote_X else 0
        data.append(["Match Nul", f"{p_Nul*100:.1f}%", f"{c_fair_X:.2f}", f"{cote_X:.2f}" if cote_X else "-", f"{ev_X*100:+.1f}%" if cote_X else "-", f"{kelly_X*100:.1f}%" if cote_X else "-"])
        
        c_fair_2 = sk.calculer_cote_equitable(p_B)
        ev_2 = sk.calculer_ev(p_B, cote_2) if cote_2 else 0
        kelly_2 = sk.calculer_kelly(p_B, cote_2) if cote_2 else 0
        data.append([f"Victoire {equipe_B}", f"{p_B*100:.1f}%", f"{c_fair_2:.2f}", f"{cote_2:.2f}" if cote_2 else "-", f"{ev_2*100:+.1f}%" if cote_2 else "-", f"{kelly_2*100:.1f}%" if cote_2 else "-"])
        
        # 4. Handicap Asiatique
        res_ah = ah.calculer_handicap_asiatique(lam_A, lam_B, ligne_choisie)
        if res_ah["type"] == "normal":
            p_ah_win = res_ah["win"]
        else:
            p_ah_win = res_ah["full_win"] + 0.5 * res_ah["half_win"] # Probabilité effective
        c_fair_ah = sk.calculer_cote_equitable(p_ah_win)
        ev_ah = sk.calculer_ev(p_ah_win, cote_ah) if cote_ah else 0
        kelly_ah = sk.calculer_kelly(p_ah_win, cote_ah) if cote_ah else 0
        data.append([f"Handicap A ({ligne_choisie})", f"{p_ah_win*100:.1f}%", f"{c_fair_ah:.2f}", f"{cote_ah:.2f}" if cote_ah else "-", f"{ev_ah*100:+.1f}%" if cote_ah else "-", f"{kelly_ah*100:.1f}%" if cote_ah else "-"])
        
        # Création du DataFrame
        df_markets = pd.DataFrame(data, columns=["Marché", "Probabilité", "Cote Équitable", "Cote Book", "EV", "Mise Kelly"])
        
        # Affichage avec un beau style
        st.dataframe(
            df_markets.style.format({
                "Probabilité": "{}",
                "Cote Équitable": "{}",
                "Cote Book": "{}",
                "EV": "{}",
                "Mise Kelly": "{}"
            }).map(lambda x: 'color: #00e676' if isinstance(x, str) and x.startswith('+') else ('color: #ff5252' if isinstance(x, str) and x.startswith('-') and x != '-' else 'color: white'), subset=["EV"]),
            use_container_width=True,
            hide_index=True
        )
        st.caption("🟢 EV positif = Value Bet | 🔴 EV négatif = Pas de value")

        # --- DÉTAILS (Handicap & Scores) ---
        st.markdown("---")
        col_det1, col_det2 = st.columns([1, 2])
        
        with col_det1:
            st.markdown(f"### ⚔️ Détail Handicap ({ligne_choisie})")
            if res_ah["type"] == "normal":
                st.metric("Victoire", f"{res_ah['win']*100:.1f} %")
                st.metric("Remboursé", f"{res_ah['push']*100:.1f} %")
                st.metric("Défaite", f"{res_ah['lose']*100:.1f} %")
            else:
                st.metric("Gain Total", f"{res_ah['full_win']*100:.1f} %")
                st.metric("Gain Partiel", f"{res_ah['half_win']*100:.1f} %")
                st.metric("Perte Partielle", f"{res_ah['half_lose']*100:.1f} %")
                st.metric("Perte Totale", f"{res_ah['full_lose']*100:.1f} %")
                
        with col_det2:
            st.markdown("### 🎯 Matrice des Scores Exacts")
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
