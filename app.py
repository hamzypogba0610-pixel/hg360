import streamlit as st

st.set_page_config(page_title="HYPER-GOALS 360", page_icon="⚽")

st.title("⚽ HYPER-GOALS 360")
st.subheader("Bienvenue sur ton bot de prédiction !")

st.write("Le bot est en cours de construction. Bientôt, tu pourras entrer les équipes et voir les probabilités.")

with st.form("match_form"):
    st.write("Formulaire de prédiction (Bientôt disponible)")
    equipe_domicile = st.text_input("Équipe à domicile")
    equipe_exterieur = st.text_input("Équipe à l'extérieur")
    submit = st.form_submit_button("Calculer")
    if submit:
        st.write(f"Prédiction pour {equipe_domicile} vs {equipe_exterieur} (en construction...)")
