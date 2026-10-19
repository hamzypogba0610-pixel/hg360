import streamlit as st
from leagues import CHAMPIONNATS

# 1. Configuration de la page
st.set_page_config(page_title="HYPER-GOALS 360 | Pro", page_icon="⚽", layout="wide")

# 2. Habillage CSS personnalisé (Le grand relooking)
st.markdown("""
    <style>
    /* --- FOND D'ÉCRAN PREMIUM --- */
    .stApp {
        /* Un dégradé sombre avec une touche de bleu nuit */
        background: linear-gradient(135deg, #090a0f 0%, #161b26 100%);
        background-attachment: fixed;
    }
    
    /* --- TYPOGRAPHIE --- */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    .main-title {
        color: #FFFFFF;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(76, 175, 80, 0.4); /* Lueur verte */
    }
    
    .sub-title {
        color: #4CAF50;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 500;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 40px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* --- EFFET VERRE (GLASSMORPHISM) SUR LE FORMULAIRE --- */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* --- STYLE DES CHAMPS DE TEXTE ET MENUS --- */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* --- BOUTON VERT NÉON --- */
    div.stButton > button {
        background: linear-gradient(90deg, #00c853, #00e676);
        color: #000000;
        border-radius: 12px;
        border: none;
        padding: 15px 30px;
        font-weight: 800;
        font-size: 1.2rem;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 200, 83, 0.6);
    }
    
    /* --- BARRE LATÉRALE --- */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 3. En-tête de l'application
st.markdown('<p class="main-title">⚽ HYPER-GOALS 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse probabiliste</p>', unsafe_allow_html=True)

# 4. La barre latérale
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=70)
    st.header("Panneau de contrôle")
    st.info("💡 Sélectionne la compétition et les équipes pour lancer le calcul des probabilités.")
    st.markdown("---")
    st.markdown("**Statut du système :** 🟢 En ligne")
    st.caption("HYPER-GOALS 360 V2.2")

# 5. Le Formulaire principal
with st.form("prediction_form"):
    st.subheader("📊 Configuration du Match")
    
    # Menu déroulant pour choisir le championnat
    ligue_choisie = st.selectbox(
        "🏆 Compétition",
        options=list(CHAMPIONNATS.keys()),
        format_func=lambda x: CHAMPIONNATS[x]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Deux colonnes pour les équipes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Domicile")
        equipe_domicile = st.text_input("Équipe A", placeholder="Ex: Arsenal", label_visibility="collapsed")
        
    with col2:
        st.markdown("### ✈️ Extérieur")
        equipe_exterieur = st.text_input("Équipe B", placeholder="Ex: Chelsea", label_visibility="collapsed")
    
    st.markdown("<br><br>", unsafe_allow_html=True) 
    
    # Bouton de validation
    submit = st.form_submit_button("🚀 ANALYSER LE MATCH", use_container_width=True)

# 6. Ce qui se passe quand on clique
if submit:
    if equipe_domicile and equipe_exterieur:
        st.success(f"✅ Analyse initialisée : **{equipe_domicile}** vs **{equipe_exterieur}** ({CHAMPIONNATS[ligue_choisie]})")
        st.info("Le moteur mathématique (HBP-360) est prêt à recevoir les données historiques...")
    else:
        st.warning("⚠️ Veuillez entrer le nom des deux équipes.")
