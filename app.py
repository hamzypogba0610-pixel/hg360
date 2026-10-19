import streamlit as st
from leagues import CHAMPIONNATS

# 1. Configuration de la page (Titre de l'onglet, icône, disposition large)
st.set_page_config(page_title="HYPER-GOALS 360 | Pro", page_icon="⚽", layout="wide")

# 2. Habillage CSS personnalisé (Le "maquillage" du bot)
st.markdown("""
    <style>
    /* Fond principal sombre et propre */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Style du titre principal */
    .main-title {
        color: #FFFFFF;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* Style du sous-titre */
    .sub-title {
        color: #4CAF50;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 500;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 40px;
    }
    
    /* Style des cartes / formulaires */
    div[data-testid="stForm"] {
        background-color: #1E2129;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        border: 1px solid #2E323D;
    }
    
    /* Le bouton d'action (Vert Gazon) */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# 3. En-tête de l'application
st.markdown('<p class="main-title">⚽ HYPER-GOALS 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse probabiliste et de calibration</p>', unsafe_allow_html=True)

# 4. La barre latérale (Menu de gauche)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=80) # Petite icône
    st.header("Panneau de contrôle")
    st.info("Bienvenue sur le bot. Sélectionne tes équipes et lance l'analyse.")
    st.markdown("---")
    st.caption("Version 2.2 | Mode Expert")

# 5. Le Formulaire principal
with st.form("prediction_form"):
    st.subheader("📊 Paramètres du Match")
    
    # Menu déroulant pour choisir le championnat
    ligue_choisie = st.selectbox(
        "🏆 Sélectionne la compétition",
        options=list(CHAMPIONNATS.keys()),
        format_func=lambda x: CHAMPIONNATS[x] # Affiche le joli nom
    )
    
    # Deux colonnes pour les équipes (Domicile vs Extérieur)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Équipe à Domicile")
        equipe_domicile = st.text_input("Nom de l'équipe A", placeholder="Ex: Arsenal")
        
    with col2:
        st.markdown("### ✈️ Équipe à l'Extérieur")
        equipe_exterieur = st.text_input("Nom de l'équipe B", placeholder="Ex: Chelsea")
    
    st.markdown("<br>", unsafe_allow_html=True) # Petit espace
    
    # Bouton de validation
    submit = st.form_submit_button("🚀 Lancer l'analyse", use_container_width=True)

# 6. Ce qui se passe quand on clique sur le bouton
if submit:
    if equipe_domicile and equipe_exterieur:
        st.success(f"✅ Analyse lancée pour : **{equipe_domicile}** vs **{equipe_exterieur}** ({CHAMPIONNATS[ligue_choisie]})")
        
        # Ici, on mettra les vrais calculs mathématiques plus tard !
        st.info("Le moteur mathématique (HBP-360) est en cours de connexion... Les résultats s'afficheront ici.")
    else:
        st.warning("⚠️ N'oublie pas de remplir le nom des deux équipes !")
