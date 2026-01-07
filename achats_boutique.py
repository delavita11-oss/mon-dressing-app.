import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestion Dépenses", page_icon="💰", layout="centered")

# Nom du fichier Excel
FICHIER_EXCEL = 'depenses.xlsx'

# --- FONCTIONS ---
def charger_donnees():
    if not os.path.exists(FICHIER_EXCEL):
        # Création d'un fichier vide avec les bonnes colonnes si inexistant
        df = pd.DataFrame(columns=["Date", "Description", "Montant", "Categorie"])
        df.to_excel(FICHIER_EXCEL, index=False)
        return df
    return pd.read_excel(FICHIER_EXCEL)

def sauvegarder_donnees(df):
    df.to_excel(FICHIER_EXCEL, index=False)

# --- INTERFACE PRINCIPALE ---
st.title("💸 Suivi des Dépenses")
st.markdown("---")

# 1. Chargement des données
df = charger_donnees()

# 2. Formulaire d'ajout (Dans la barre latérale pour faire propre)
with st.sidebar:
    st.header("Nouvelle Dépense")
    with st.form("ajout_form", clear_on_submit=True):
        desc = st.text_input("Description (ex: Levi's)")
        montant = st.number_input("Montant (€)", min_value=0.0, format="%.2f")
        categorie = st.selectbox("Catégorie", ["Vêtements", "Alimentation", "Loisirs", "Autre"])
        date = st.date_input("Date", datetime.now())
        
        submit = st.form_submit_button("Ajouter")
        
        if submit and desc:
            nouvelle_ligne = pd.DataFrame([{
                "Date": date,
                "Description": desc,
                "Montant": montant,
                "Categorie": categorie
            }])
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            sauvegarder_donnees(df)
            st.success("Ajouté !")
            st.rerun() # Rafraichit la page immédiatement

# 3. Affichage et Suppression
st.subheader("Historique")

if not df.empty:
    # On affiche les données avec un design propre
    # Pour la suppression, on utilise une astuce : une case à cocher ou un selecteur
    
    # Affiche un tableau interactif
    st.dataframe(df, use_container_width=True)

    st.markdown("### 🗑️ Zone de suppression")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Liste déroulante pour choisir quoi supprimer (plus sûr qu'un bouton partout)
        options = df.index.astype(str) + " : " + df["Description"] + " (" + df["Montant"].astype(str) + "€)"
        to_delete = st.selectbox("Sélectionne la ligne à supprimer", options, index=None, placeholder="Choisis une dépense...")
    
    with col2:
        st.write("") # Espacement
        st.write("") 
        if st.button("Supprimer ❌", type="primary"):
            if to_delete:
                index_to_drop = int(to_delete.split(" : ")[0])
                df = df.drop(index_to_drop).reset_index(drop=True)
                sauvegarder_donnees(df)
                st.success("Dépense supprimée !")
                st.rerun()
            else:
                st.warning("Sélectionne une ligne d'abord.")

    # 4. Petit bonus : Total
    st.markdown("---")
    total = df["Montant"].sum()
    st.metric(label="Total des dépenses", value=f"{total} €")

else:
    st.info("Aucune dépense pour le moment.")
