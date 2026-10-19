import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me
import dixon_coles as dc
import staking as sk
import pandas as pd
import datetime

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
st.markdown('<p class="sub-title">Tableau de Bord du Parieur Pro</p>', unsafe_allow_html=True)

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if "historique" not in st.session_state:
    st.session_state.historique = []

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=70)
    st.header("Panneau de contrôle")
    st.info("💡 Ajuste le paramètre Rho (ρ) pour corriger les scores serrés (0-0, 1-1).")
    st.caption("HYPER-GOALS 360 V2.2")
    
    # Bouton d'export dans la barre latérale
    if len(st.session_state.historique) > 0:
        st.markdown("---")
        st.subheader("📁 Exporter mes données")
        df_export = pd.DataFrame(st.session_state.historique)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger l'historique (CSV)",
            data=csv,
            file_name=f"hg360_historique_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.historique = []
            st.rerun()

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
    st.subheader("💰 2. Cotes du Bookmaker & Paramètres")
    
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
        rho = st.slider("Paramètre Rho (ρ) Dixon-Coles", min_value=-0.15, max_value=0.15, value=-0.05, step=0.01)
    
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
        matrice_dc = dc.appliquer_correction(lam_A, lam_B, rho)
        
        st.success(f"✅ Analyse terminée (Dixon-Coles Activé) : **{equipe_A}** vs **{equipe_B}**")
        
        # --- SAUVEGARDE DANS L'HISTORIQUE ---
        match_id = f"{equipe_A} vs {equipe_B} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})"
        
        over_25 = sum(p for (i, j), p in matrice_dc.items() if i + j > 2)
        if over_25 > 0 and cote_over:
            ev = sk.calculer_ev(over_25, cote_over)
            if ev > 0: # On sauvegarde seulement les value bets !
                st.session_state.historique.append({
                    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Match": f"{equipe_A} - {equipe_B}",
                    "Ligue": CHAMPIONNATS[ligue_choisie],
                    "Lambda A": round(lam_A, 2),
                    "Lambda B": round(lam_B, 2),
                    "Marché": "Over 2.5",
                    "Proba (%)": round(over_25*100, 1),
                    "Cote Book": cote_over,
                    "EV (%)": round(ev*100, 1),
                    "Mise Kelly (%)": round(sk.calculer_kelly(over_25, cote_over)*100, 1)
                })
        # -----------------------------------

        col_res1, col_res2 = st.columns(2)
        col_res1.metric(label=f"Buts attendus (λ) - {equipe_A}", value=f"{lam_A:.2f}")
        col_res2.metric(label=f"Buts attendus (λ) - {equipe_B}", value=f"{lam_B:.2f}")
        
        p_btts = sum(p for (i, j), p in matrice_dc.items() if i > 0 and j > 0)
        p_A = sum(p for (i, j), p in matrice_dc.items() if i > j)
        p_Nul = sum(p for (i, j), p in matrice_dc.items() if i == j)
        p_B = sum(p for (i, j), p in matrice_dc.items() if i < j)
        
        st.markdown("### 📋 Récapitulatif des Marchés et Value Bets")
        data = []
        
        # Over 2.5
        c_fair = sk.calculer_cote_equitable(over_25)
        ev = sk.calculer_ev(over_25, cote_over) if cote_over else 0
        kelly = sk.calculer_kelly(over_25, cote_over) if cote_over else 0
        data.append(["Over 2.5", f"{over_25*100:.1f}%", f"{c_fair:.2f}", f"{cote_over:.2f}" if cote_over else "-", f"{ev*100:+.1f}%" if cote_over else "-", f"{kelly*100:.1f}%" if cote_over else "-"])
        
        # BTTS
        c_fair_btts = sk.calculer_cote_equitable(p_btts)
        ev_btts = sk.calculer_ev(p_btts, cote_btts) if cote_btts else 0
        kelly_btts = sk.calculer_kelly(p_btts, cote_btts) if cote_btts else 0
        data.append(["BTTS (Oui)", f"{p_btts*100:.1f}%", f"{c_fair_btts:.2f}", f"{cote_btts:.2f}" if cote_btts else "-", f"{ev_btts*100:+.1f}%" if cote_btts else "-", f"{kelly_btts*100:.1f}%" if cote_btts else "-"])
        
        # 1X2
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
        
        # Handicap Asiatique
        est_quart = (ligne_choisie % 0.5 != 0)
        if not est_quart:
            p_win_ah = sum(p for (i, j), p in matrice_dc.items() if (i - j) + ligne_choisie > 0)
        else:
            h_inf, h_sup = ligne_choisie - 0.25, ligne_choisie + 0.25
            full_w = sum(p for (i, j), p in matrice_dc.items() if (i-j)+h_inf > 0 and (i-j)+h_sup > 0)
            half_w = sum(p for (i, j), p in matrice_dc.items() if (i-j)+h_inf == 0 and (i-j)+h_sup > 0)
            p_win_ah = full_w + 0.5 * half_w
            
        c_fair_ah = sk.calculer_cote_equitable(p_win_ah)
        ev_ah = sk.calculer_ev(p_win_ah, cote_ah) if cote_ah else 0
        kelly_ah = sk.calculer_kelly(p_win_ah, cote_ah) if cote_ah else 0
        data.append([f"Handicap A ({ligne_choisie})", f"{p_win_ah*100:.1f}%", f"{c_fair_ah:.2f}", f"{cote_ah:.2f}" if cote_ah else "-", f"{ev_ah*100:+.1f}%" if cote_ah else "-", f"{kelly_ah*100:.1f}%" if cote_ah else "-"])
        
        df_markets = pd.DataFrame(data, columns=["Marché", "Probabilité", "Cote Équitable", "Cote Book", "EV", "Mise Kelly"])
        
        st.dataframe(
            df_markets.style.format({
                "Probabilité": "{}", "Cote Équitable": "{}", "Cote Book": "{}", "EV": "{}", "Mise Kelly": "{}"
            }).map(lambda x: 'color: #00e676' if isinstance(x, str) and x.startswith('+') else ('color: #ff5252' if isinstance(x, str) and x.startswith('-') and x != '-' else 'color: white'), subset=["EV"]),
            use_container_width=True,
            hide_index=True
        )
        st.caption("🟢 EV positif = Value Bet | 🔴 EV négatif = Pas de value")

        st.markdown("---")
        st.markdown(f"### 🎯 Matrice des Scores Exacts (Corrigée Dixon-Coles ρ={rho})")
        
        matrice_scores = []
        for buts_A in range(5):
            ligne = []
            for buts_B in range(5):
                proba = matrice_dc.get((buts_A, buts_B), 0) * 100
                ligne.append(proba)
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
