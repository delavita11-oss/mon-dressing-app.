import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import plotly.express as px
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Collection Manager", layout="wide", page_icon="☁️")

# --- CONNEXION SECURISEE (CLOUD COMPATIBLE) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # On essaie d'abord la méthode "Cloud" (Secrets Streamlit)
    if "gcp_service_account" in st.secrets:
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    # Sinon, on essaie la méthode "PC Local" (Fichier)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("secrets.json", scope)
        
    client = gspread.authorize(creds)
    sheet = client.open("Achats_Boutique_DB").sheet1

except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.info("Sur le Cloud, vérifie que les 'Secrets' sont bien configurés.")
    st.stop()

# --- FONCTIONS ---
def load_data():
    data = sheet.get_all_records()
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["Saison", "Année", "Marque", "Montant_Commande", "Date_Saisie", "Commentaire"])

def add_entry(row_data):
    sheet.append_row(row_data)

# Chargement
df = load_data()

# --- INTERFACE ---
st.title("☁️ Collection Manager • Online")

tab1, tab2, tab3 = st.tabs(["📊 Stats", "➕ Saisir", "🗂️ Liste"])

with tab1:
    if not df.empty:
        df["Montant_Commande"] = pd.to_numeric(df["Montant_Commande"], errors='coerce')
        total = df["Montant_Commande"].sum()
        st.metric("Budget Total", f"{total:,.0f} €")
        fig = px.bar(df, x="Marque", y="Montant_Commande", color="Marque")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Nouvelle Commande")
    with st.form("cloud_form"):
        c1, c2 = st.columns(2)
        with c1:
            saison = st.selectbox("Saison", ["AH", "PE"])
            annee = st.selectbox("Année", [2025, 2026, 2027])
            marque = st.text_input("Marque (ex: DIESEL)").upper()
        with c2:
            montant = st.number_input("Montant €", step=50.0)
            note = st.text_area("Note")
            
        if st.form_submit_button("Envoyer au Cloud 🚀"):
            if marque and montant > 0:
                add_entry([saison, annee, marque, montant, datetime.now().strftime("%Y-%m-%d"), note])
                st.success("Sauvegardé !")
                st.balloons()

with tab3:
    if st.button("Actualiser"): st.rerun()
    st.dataframe(df, use_container_width=True)