"""
Dashboard ALTERN - Suivi des Mandats
Prototype v1
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="ALTERN Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1A5276;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1A5276 0%, #1F618D 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .alert-red {
        background-color: #FADBD8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #E74C3C;
    }
    .alert-orange {
        background-color: #FDEBD0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #F39C12;
    }
</style>
""", unsafe_allow_html=True)

# Fonction de chargement des données
@st.cache_data
def load_data(filepath):
    """Charge les données depuis le fichier Excel"""
    try:
        # Lire en spécifiant la ligne d'en-tête (ligne 3 = index 2)
        mandats = pd.read_excel(filepath, sheet_name='📋 DB_MANDATS', header=2)
        factures = pd.read_excel(filepath, sheet_name='💸 DB_FACTURATION', header=2)
        
        # Nettoyer les noms de colonnes (enlever espaces)
        mandats.columns = mandats.columns.str.strip()
        factures.columns = factures.columns.str.strip()
        
        # Filtrer les lignes vides
        mandats = mandats[mandats['ID Mandat'].notna()].copy()
        factures = factures[factures['ID Mandat'].notna()].copy()
        
        return mandats, factures
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.exception(e)  # Afficher le détail de l'erreur
        return None, None

# Sidebar - Sélection du fichier
st.sidebar.markdown("## 📁 Source de données")
uploaded_file = st.sidebar.file_uploader(
    "Charger le fichier Excel ALTERN",
    type=['xlsx'],
    help="Sélectionnez le fichier ALTERN_Suivi_Mandats.xlsx"
)

if uploaded_file is not None:
    mandats, factures = load_data(uploaded_file)
    
    if mandats is not None and factures is not None:
        
        # Header
        st.markdown('<div class="main-header">📊 Dashboard ALTERN — Suivi des Mandats</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 1 : VUE D'ENSEMBLE
        # ═══════════════════════════════════════════════════════════════════
        
        tab1, tab2, tab3 = st.tabs(["📈 Vue d'ensemble", "🔍 Suivi opérationnel", "💰 Santé financière"])
        
        with tab1:
            st.markdown("### 📋 Indicateurs clés")
            
            # KPIs en haut
            col1, col2, col3, col4 = st.columns(4)
            
            nb_actifs = len(mandats[mandats['Statut mandat'] == 'Signé / En cours'])
            nb_attente = len(mandats[mandats['Statut mandat'] == 'En attente de signature'])
            nb_bloques = len(mandats[mandats['Statut mandat'] == 'Suspendu / Bloqué'])
            nb_total = len(mandats)
            
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Mandats actifs</div>
                    <div class="kpi-value">{nb_actifs}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">En attente signature</div>
                    <div class="kpi-value">{nb_attente}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                color = "#E74C3C" if nb_bloques > 0 else "#27AE60"
                st.markdown(f"""
                <div class="kpi-card" style="background: {color};">
                    <div class="kpi-label">Bloqués / Suspendus</div>
                    <div class="kpi-value">{nb_bloques}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total mandats</div>
                    <div class="kpi-value">{nb_total}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Graphiques
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("#### 📊 Répartition par type de mandat")
                type_counts = mandats['Type de mandat'].value_counts()
                fig_types = px.bar(
                    x=type_counts.index,
                    y=type_counts.values,
                    labels={'x': 'Type', 'y': 'Nombre de mandats'},
                    color=type_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_types.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig_types, use_container_width=True)
            
            with col_right:
                st.markdown("#### 🎯 Statuts des mandats")
                statut_counts = mandats['Statut mandat'].value_counts()
                colors = {
                    'Signé / En cours': '#3498DB',
                    'En attente de signature': '#F39C12',
                    'Suspendu / Bloqué': '#E74C3C',
                    'Livré / Clôturé': '#27AE60',
                    'Prospection': '#95A5A6'
                }
                fig_statuts = px.pie(
                    values=statut_counts.values,
                    names=statut_counts.index,
                    color=statut_counts.index,
                    color_discrete_map=colors
                )
                fig_statuts.update_layout(height=350)
                st.plotly_chart(fig_statuts, use_container_width=True)
            
            # Charge par chargé
            st.markdown("#### 👥 Charge par chargé(e) de mission")
            charges = pd.concat([
                mandats[['Chargé(e) 1']].rename(columns={'Chargé(e) 1': 'Chargé'}),
                mandats[['Chargé(e) 2']].rename(columns={'Chargé(e) 2': 'Chargé'})
            ])
            charges = charges[charges['Chargé'].notna()]
            charge_counts = charges['Chargé'].value_counts().sort_values(ascending=True)
            
            fig_charges = px.bar(
                x=charge_counts.values,
                y=charge_counts.index,
                orientation='h',
                labels={'x': 'Nombre de mandats', 'y': 'Chargé(e)'},
                color=charge_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_charges.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_charges, use_container_width=True)
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 2 : SUIVI OPÉRATIONNEL
        # ═══════════════════════════════════════════════════════════════════
        
        with tab2:
            st.markdown("### 🔍 Liste des mandats")
            
            # Filtres
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                filtre_statut = st.multiselect(
                    "Filtrer par statut",
                    options=mandats['Statut mandat'].unique(),
                    default=None
                )
            
            with col_f2:
                filtre_type = st.multiselect(
                    "Filtrer par type",
                    options=mandats['Type de mandat'].unique(),
                    default=None
                )
            
            with col_f3:
                charges_unique = pd.concat([
                    mandats['Chargé(e) 1'],
                    mandats['Chargé(e) 2']
                ]).dropna().unique()
                filtre_charge = st.multiselect(
                    "Filtrer par chargé(e)",
                    options=sorted(charges_unique),
                    default=None
                )
            
            # Appliquer les filtres
            mandats_filtered = mandats.copy()
            if filtre_statut:
                mandats_filtered = mandats_filtered[mandats_filtered['Statut mandat'].isin(filtre_statut)]
            if filtre_type:
                mandats_filtered = mandats_filtered[mandats_filtered['Type de mandat'].isin(filtre_type)]
            if filtre_charge:
                mandats_filtered = mandats_filtered[
                    mandats_filtered['Chargé(e) 1'].isin(filtre_charge) |
                    mandats_filtered['Chargé(e) 2'].isin(filtre_charge)
                ]
            
            # Affichage tableau
            colonnes_affichage = ['ID Mandat', 'Commune', 'Type de mandat', 'Statut mandat', 
                                 'Chargé(e) 1', 'Date début mandat', 'Date fin mandat']
            st.dataframe(
                mandats_filtered[colonnes_affichage],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown(f"**{len(mandats_filtered)}** mandat(s) affiché(s)")
            
            # Alertes
            st.markdown("### 🚩 Alertes du jour")
            
            # Calcul alertes (exemple simplifié)
            today = datetime.now()
            alertes = []
            
            for _, row in mandats.iterrows():
                if pd.notna(row['Date fin mandat']) and row['Statut mandat'] == 'Signé / En cours':
                    fin = pd.to_datetime(row['Date fin mandat'])
                    if fin < today:
                        alertes.append({
                            'Type': 'Mandat en retard',
                            'Mandat': row['ID Mandat'],
                            'Commune': row['Commune'],
                            'Message': f"Date de fin dépassée ({fin.strftime('%d/%m/%Y')})"
                        })
            
            if alertes:
                for alerte in alertes:
                    st.markdown(f"""
                    <div class="alert-red">
                        <strong>{alerte['Type']}</strong><br>
                        {alerte['Mandat']} — {alerte['Commune']}<br>
                        {alerte['Message']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.success("✅ Aucune alerte aujourd'hui")
        
        # ═══════════════════════════════════════════════════════════════════
        # PAGE 3 : SANTÉ FINANCIÈRE
        # ═══════════════════════════════════════════════════════════════════
        
        with tab3:
            st.markdown("### 💰 Vue financière")
            
            # KPIs financiers
            col1, col2, col3 = st.columns(3)
            
            total_facture = factures['Montant HT (€)'].sum()
            factures_payees = factures[factures['Statut'] == 'Payée']['Montant HT (€)'].sum()
            en_attente = factures[factures['Statut'] == 'Émise / En attente de paiement']['Montant HT (€)'].sum()
            
            with col1:
                st.metric("Total facturé", f"{total_facture:,.0f} €")
            
            with col2:
                st.metric("Encaissé", f"{factures_payees:,.0f} €", delta=None)
            
            with col3:
                st.metric("En attente", f"{en_attente:,.0f} €", delta=None)
            
            # Tableau des factures
            st.markdown("#### 📋 Liste des factures")
            
            factures_display = factures[['ID Mandat', 'Type de ligne', 'Phase', 'Montant HT (€)', 'Statut']].copy()
            
            # Colorier par statut
            def highlight_statut(row):
                if row['Statut'] == 'Payée':
                    return ['background-color: #D5F5E3'] * len(row)
                elif row['Statut'] == 'En retard / Relance':
                    return ['background-color: #FADBD8'] * len(row)
                elif row['Statut'] == 'Émise / En attente de paiement':
                    return ['background-color: #FDEBD0'] * len(row)
                else:
                    return [''] * len(row)
            
            st.dataframe(
                factures_display.style.apply(highlight_statut, axis=1),
                use_container_width=True,
                hide_index=True
            )
            
            # Graphique statuts factures
            st.markdown("#### 📊 Répartition des statuts de facturation")
            statut_factures = factures['Statut'].value_counts()
            fig_fact = px.pie(
                values=statut_factures.values,
                names=statut_factures.index,
                color=statut_factures.index,
                color_discrete_map={
                    'Payée': '#27AE60',
                    'Émise / En attente de paiement': '#F39C12',
                    'À émettre': '#3498DB',
                    'En retard / Relance': '#E74C3C'
                }
            )
            st.plotly_chart(fig_fact, use_container_width=True)

else:
    # Page d'accueil quand aucun fichier n'est chargé
    st.markdown('<div class="main-header">📊 Dashboard ALTERN</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.info("👈 **Commencez par charger le fichier Excel dans la barre latérale**")
    
    st.markdown("""
    ### 🎯 Fonctionnalités
    
    Ce dashboard vous permet de visualiser en temps réel :
    
    - **Vue d'ensemble** : KPIs, répartition par type, charge par chargé(e)
    - **Suivi opérationnel** : Liste filtrable des mandats, alertes automatiques
    - **Santé financière** : Suivi de la facturation, statuts des paiements
    
    ### 📁 Comment l'utiliser ?
    
    1. Ouvrez le fichier Excel et travaillez normalement
    2. Sauvegardez vos modifications
    3. Chargez le fichier dans ce dashboard (barre latérale)
    4. Les graphiques se mettent à jour automatiquement
    
    ---
    *ALTERN — Agence de transition énergétique — Métropole Rouen Normandie*
    """)
