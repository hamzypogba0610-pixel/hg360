import streamlit as st
from leagues import CHAMPIONNATS
import math_engine as me

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
    st.info("💡 Entre les statistiques des équipes pour lancer le calcul de Poisson.")
    st.caption("HYPER-GOALS 360 V2.2")

# 5. Le Formulaire de saisie
with st.form("prediction_form"):
    st.subheader("📊 Statistiques du Match")
    
    ligue_choisie = st.selectbox("🏆 Compétition", options=list(CHAMPIONNATS.keys()), format_func=lambda x: CHAMPIONNATS[x])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Équipe A (Domicile)")
        equipe_A = st.text_input("Nom de l'équipe A", placeholder="Ex: Arsenal")
        M_A = st.number_input("Buts marqués par A (moyenne)", min_value=0.0, value=1.5, step=0.1)
        E_A = st.number_input("Buts encaissés par A (moyenne)", min_value=0.0, value=1.0, step=0.1)
        
    with col2:
        st.markdown("### ✈️ Équipe B (Extérieur)")
        equipe_B = st.text_input("Nom de l'équipe B", placeholder="Ex: Chelsea")
        M_B = st.number_input("Buts marqués par B (moyenne)", min_value=0.0, value=1.2, step=0.1)
        E_B = st.number_input("Buts encaissés par B (moyenne)", min_value=0.0, value=1.1, step=0.1)
    
    st.markdown("---")
    mu = st.number_input("Moyenne de buts du championnat (μ)", min_value=0.1, value=1.3, step=0.1)
    
    submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

# 6. Affichage des résultats
if submit:
    if equipe_A and equipe_B:
        # Calcul des lambdas via notre moteur
        lam_A = me.calculer_lambda(M_A, E_B, mu)
        lam_B = me.calculer_lambda(M_B, E_A, mu)
        
        # Affichage des résultats
        st.success(f"✅ Analyse terminée : **{equipe_A}** vs **{equipe_B}** ({CHAMPIONNATS[ligue_choisie]})")
        
        # Cartes de buts attendus
        col_res1, col_res2 = st.columns(2)
        col_res1.metric(label=f"Buts attendus (λ) - {equipe_A}", value=f"{lam_A:.2f}")
        col_res2.metric(label=f"Buts attendus (λ) - {equipe_B}", value=f"{lam_B:.2f}")
        
        # Calcul des probabilités Over/Under
        over_25, under_25 = me.proba_over_under(lam_A, lam_B, 2.5)
        
        st.markdown("### 📈 Marché des Buts (Over/Under 2.5)")
        col_ou1, col_ou2 = st.columns(2)
        col_ou1.metric(label="🔴 Over 2.5 (Plus de 2 buts)", value=f"{over_25*100:.1f} %")
        col_ou2.metric(label="🟢 Under 2.5 (Moins de 3 buts)", value=f"{under_25*100:.1f} %")
        
        # Calcul des scores exacts les plus probables
        st.markdown("### 🎯 Scores exacts probables")
        scores = [(0,0), (1,0), (0,1), (1,1), (2,0), (0,2), (2,1), (1,2), (2,2)]
        scores_probables = []
        
        for sA, sB in scores:
            p = me.calculer_score_exact(lam_A, lam_B, sA, sB)
            scores_probables.append((f"{sA} - {sB}", p))
            
        # Trier du plus probable au moins probable
        scores_probables.sort(key=lambda x: x[1], reverse=True)
        
        # Afficher les 4 meilleurs
        cols_scores = st.columns(4)
        for i in range(4):
            score_str, prob = scores_probables[i]
            cols_scores[i].metric(label=f"Score {score_str}", value=f"{prob*100:.1f} %")
            
    else:
        st.warning("⚠️ Veuillez entrer le nom des deux équipes.")
