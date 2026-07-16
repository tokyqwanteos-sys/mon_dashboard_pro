import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import hashlib
import json

# --- Configuration de la page ---
st.set_page_config(
    page_title="MGA Finance Tracker", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CSS : Fond animé, style pro et cinématique ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%); background-attachment: fixed; }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image: radial-gradient(2px 2px at 20px 30px, #ffffff, rgba(0,0,0,0)),
                          radial-gradient(2px 2px at 40px 70px, #ffffff, rgba(0,0,0,0));
        background-size: 200px 200px; animation: stars 10s linear infinite; pointer-events: none;
    }
    @keyframes stars { from { transform: translateY(0); } to { transform: translateY(-200px); } }
    .welcome-screen { text-align: center; padding-top: 10vh; animation: fadeIn 2s; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .sticker { font-size: 40px; animation: bounce 2s infinite; display: inline-block; }
    @keyframes bounce { 0%, 20%, 50%, 80%, 100% {transform: translateY(0);} 40% {transform: translateY(-15px);} }
    .stMetric, .stTabs, .stExpander, .stDataFrame {
        background-color: rgba(255, 255, 255, 0.08); border-radius: 15px; padding: 15px;
        backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 { color: #ffffff !important; }
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 30px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .auth-container input {
        width: 100%;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.05);
        color: white;
    }
    .auth-container button {
        width: 100%;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    .auth-container button:hover {
        transform: scale(1.02);
        opacity: 0.9;
    }
    .switch-auth {
        color: #667eea;
        cursor: pointer;
        text-decoration: underline;
        margin-top: 10px;
        display: inline-block;
    }
    .filter-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .filter-label {
        color: #ffffff;
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
    }
    .stats-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    .note-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin: 5px 0;
    }
    .summary-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Gestion des utilisateurs ---
USER_FILE = "users.json"
DATA_DIR = "user_data"

# Créer le dossier pour les données utilisateurs s'il n'existe pas
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username] == hash_password(password):
        return True
    return False

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    
    # Créer le dossier utilisateur
    user_dir = os.path.join(DATA_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    return True

def get_user_file(username, filename):
    """Retourne le chemin complet du fichier pour un utilisateur spécifique"""
    user_dir = os.path.join(DATA_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return os.path.join(user_dir, filename)

# --- Initialisation session state ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.auth_mode = "login"

# --- Écran d'authentification ---
if not st.session_state.authenticated:
    st.markdown("""
        <div class="welcome-screen">
            <h1>🚀 MGA Finance Tracker</h1>
            <p style="font-size: 18px; color: #aaa;">Gérez vos finances avec précision et style.</p>
            <br>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "login":
            st.markdown("<h2 style='text-align: center; color: white;'>🔐 Connexion</h2>", unsafe_allow_html=True)
            username = st.text_input("👤 Nom d'utilisateur", key="login_username")
            password = st.text_input("🔑 Mot de passe", type="password", key="login_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Se connecter", use_container_width=True):
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
            with col2:
                if st.button("📝 S'inscrire", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()
                    
        else:
            st.markdown("<h2 style='text-align: center; color: white;'>📝 Inscription</h2>", unsafe_allow_html=True)
            username = st.text_input("👤 Choisir un nom d'utilisateur", key="register_username")
            password = st.text_input("🔑 Choisir un mot de passe", type="password", key="register_password")
            confirm_password = st.text_input("✅ Confirmer le mot de passe", type="password", key="register_confirm")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ S'inscrire", use_container_width=True):
                    if password != confirm_password:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif len(password) < 4:
                        st.error("❌ Le mot de passe doit contenir au moins 4 caractères")
                    elif register_user(username, password):
                        st.success("🎉 Inscription réussie ! Vous pouvez maintenant vous connecter")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error("❌ Ce nom d'utilisateur existe déjà")
            with col2:
                if st.button("🔙 Retour à la connexion", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# --- Code existant avec données par utilisateur ---
def get_user_data_file(filename):
    """Retourne le chemin du fichier pour l'utilisateur connecté"""
    return get_user_file(st.session_state.username, filename)

def get_sticker(gain, perte):
    diff = gain - perte
    if diff > 0: return "🤩"
    if diff < 0: return "😫"
    return "😐"

def format_num(n):
    return f"{int(n):,}".replace(",", " ")

def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if "Date" in df.columns:
            # S'assurer que la colonne Date est bien datetime
            df["Date"] = pd.to_datetime(df["Date"], format='mixed', errors='coerce')
            # Supprimer les lignes avec des dates invalides
            df = df.dropna(subset=["Date"])
        # S'assurer que les colonnes sont du bon type
        for col in ["Type", "Catégorie", "Description"]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
        if "Montant" in df.columns:
            df["Montant"] = pd.to_numeric(df["Montant"], errors='coerce').fillna(0)
        return df
    # Créer un DataFrame vide avec les bonnes colonnes
    return pd.DataFrame(columns=["Date", "Type", "Catégorie", "Montant", "Description"])

def save_data(df, file_path):
    # S'assurer que les colonnes sont dans le bon ordre
    columns = ["Date", "Type", "Catégorie", "Montant", "Description"]
    for col in columns:
        if col not in df.columns:
            df[col] = "" if col != "Montant" else 0
    df = df[columns]
    df.to_csv(file_path, index=False)

def load_notes(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], format='mixed', errors='coerce')
            df = df.dropna(subset=["Date"])
        # S'assurer que les colonnes existent et sont du bon type
        for col in ["Produit", "Besoins"]:
            if col not in df.columns:
                df[col] = ""
            else:
                df[col] = df[col].fillna("").astype(str)
        for col in ["Estimation", "Prix_Reel"]:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    return pd.DataFrame(columns=["Date", "Produit", "Besoins", "Estimation", "Prix_Reel"])

def save_notes(df, file_path):
    # S'assurer que les colonnes sont dans le bon ordre
    columns = ["Date", "Produit", "Besoins", "Estimation", "Prix_Reel"]
    for col in columns:
        if col not in df.columns:
            df[col] = 0 if col in ["Estimation", "Prix_Reel"] else ""
    df = df[columns]
    df.to_csv(file_path, index=False)

# En-tête avec bouton veille à droite
col_title, col_user, col_sleep = st.columns([0.60, 0.25, 0.15])
col_title.title("💰 MGA Finance Tracker")
if st.session_state.username:
    col_user.write(f"👤 {st.session_state.username}")
else:
    col_user.write("👤 Utilisateur")
if col_sleep.button("💤 Déconnexion"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["➕ Transactions", "🚀 Projets", "📊 Dashboard Global", "📓 Cahier de Notes"])

with tab1:
    st.subheader("Ajouter une opération")
    with st.form("ajout_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date", datetime.now())
        type_trans = col2.selectbox("Type", ["Revenu", "Dépense", "Prêt +", "Prêt -"])
        cat = st.text_input("Catégorie")
        montant = st.number_input("Montant (Ar)", min_value=0, step=500)
        desc = st.text_input("Description")
        if st.form_submit_button("🚀 Enregistrer"):
            data_file = get_user_data_file("finances.csv")
            df = load_data(data_file)
            new_row = {"Date": date, "Type": type_trans, "Catégorie": cat, "Montant": montant, "Description": desc}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df, data_file)
            st.success("Transaction ajoutée !")

with tab2:
    st.subheader("Gestion de Projets")
    with st.form("projet_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date Projet", datetime.now())
        nom_projet = col2.text_input("Nom du Projet")
        montant = st.number_input("Montant (Ar)", min_value=0, step=500)
        type_p = st.selectbox("Type de Projet", ["Vente", "Dépense Projet", "Prêt +", "Prêt -"])
        remarques = st.text_input("Remarques")
        if st.form_submit_button("Ajouter Projet"):
            proj_file = get_user_data_file("projets.csv")
            df = load_data(proj_file)
            new_row = {"Date": date, "Type": type_p, "Catégorie": nom_projet, "Montant": montant, "Description": remarques}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df, proj_file)
            st.success("Projet mis à jour !")

with tab3:
    data_file = get_user_data_file("finances.csv")
    proj_file = get_user_data_file("projets.csv")
    
    df_base_f = load_data(data_file)
    df_base_p = load_data(proj_file)
    
    # --- FILTRES PRÉCIS ET PROFESSIONNELS ---
    with st.expander("🔍 Filtres précis", expanded=True):
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<span class="filter-label">📅 Période</span>', unsafe_allow_html=True)
            start_date = st.date_input("Début", datetime(datetime.now().year, 1, 1), key="start_date_f")
            end_date = st.date_input("Fin", datetime.now(), key="end_date_f")
        
        with col2:
            st.markdown('<span class="filter-label">🏷️ Type</span>', unsafe_allow_html=True)
            all_types_f = ["Tous"] + sorted(df_base_f["Type"].astype(str).unique().tolist()) if not df_base_f.empty else ["Tous"]
            type_filter_f = st.selectbox("Type de transaction", all_types_f, key="type_filter_f")
            
            st.markdown('<span class="filter-label">📊 Catégorie</span>', unsafe_allow_html=True)
            all_cats_f = ["Toutes"] + sorted(df_base_f["Catégorie"].astype(str).unique().tolist()) if not df_base_f.empty else ["Toutes"]
            cat_filter_f = st.selectbox("Catégorie", all_cats_f, key="cat_filter_f")
        
        with col3:
            st.markdown('<span class="filter-label">💰 Montant</span>', unsafe_allow_html=True)
            if not df_base_f.empty:
                min_val_f = int(df_base_f["Montant"].min())
                max_val_f = int(df_base_f["Montant"].max())
            else:
                min_val_f = 0
                max_val_f = 100000
            
            # S'assurer que min < max pour le slider
            if min_val_f >= max_val_f:
                max_val_f = min_val_f + 1
            
            montant_range_f = st.slider(
                "Plage de montant (Ar)",
                min_value=min_val_f,
                max_value=max_val_f,
                value=(min_val_f, max_val_f),
                step=1000,
                key="montant_range_f"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Application des filtres avec vérification
        if not df_base_f.empty:
            mask_f = (df_base_f["Date"].dt.date >= start_date) & (df_base_f["Date"].dt.date <= end_date)
            
            if type_filter_f != "Tous":
                mask_f &= (df_base_f["Type"].astype(str) == type_filter_f)
            
            if cat_filter_f != "Toutes":
                mask_f &= (df_base_f["Catégorie"].astype(str) == cat_filter_f)
            
            mask_f &= (df_base_f["Montant"] >= montant_range_f[0]) & (df_base_f["Montant"] <= montant_range_f[1])
            
            df_f = df_base_f.loc[mask_f]
        else:
            df_f = df_base_f
        
        # Filtres pour les projets
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown('<span class="filter-label">📅 Période Projets</span>', unsafe_allow_html=True)
            start_date_p = st.date_input("Début Projets", datetime(datetime.now().year, 1, 1), key="start_date_p")
            end_date_p = st.date_input("Fin Projets", datetime.now(), key="end_date_p")
        
        with col5:
            st.markdown('<span class="filter-label">🏷️ Type Projet</span>', unsafe_allow_html=True)
            all_types_p = ["Tous"] + sorted(df_base_p["Type"].astype(str).unique().tolist()) if not df_base_p.empty else ["Tous"]
            type_filter_p = st.selectbox("Type de projet", all_types_p, key="type_filter_p")
            
            st.markdown('<span class="filter-label">📊 Nom Projet</span>', unsafe_allow_html=True)
            all_projects = ["Tous"] + sorted(df_base_p["Catégorie"].astype(str).unique().tolist()) if not df_base_p.empty else ["Tous"]
            project_filter = st.selectbox("Projet", all_projects, key="project_filter")
        
        with col6:
            st.markdown('<span class="filter-label">💰 Montant Projet</span>', unsafe_allow_html=True)
            if not df_base_p.empty:
                min_val_p = int(df_base_p["Montant"].min())
                max_val_p = int(df_base_p["Montant"].max())
            else:
                min_val_p = 0
                max_val_p = 100000
            
            # S'assurer que min < max pour le slider
            if min_val_p >= max_val_p:
                max_val_p = min_val_p + 1
            
            montant_range_p = st.slider(
                "Plage de montant (Ar)",
                min_value=min_val_p,
                max_value=max_val_p,
                value=(min_val_p, max_val_p),
                step=1000,
                key="montant_range_p"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Application des filtres projets avec vérification
        if not df_base_p.empty:
            mask_p = (df_base_p["Date"].dt.date >= start_date_p) & (df_base_p["Date"].dt.date <= end_date_p)
            
            if type_filter_p != "Tous":
                mask_p &= (df_base_p["Type"].astype(str) == type_filter_p)
            
            if project_filter != "Tous":
                mask_p &= (df_base_p["Catégorie"].astype(str) == project_filter)
            
            mask_p &= (df_base_p["Montant"] >= montant_range_p[0]) & (df_base_p["Montant"] <= montant_range_p[1])
            
            df_p = df_base_p.loc[mask_p]
        else:
            df_p = df_base_p
        
        # Statistiques des filtres
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("📊 Transactions filtrées", f"{len(df_f)}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_stats2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            total_f = df_f["Montant"].sum() if not df_f.empty else 0
            st.metric("💰 Total transactions", f"{format_num(total_f)} Ar")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_stats3:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("📊 Projets filtrés", f"{len(df_p)}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_stats4:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            total_p = df_p["Montant"].sum() if not df_p.empty else 0
            st.metric("💰 Total projets", f"{format_num(total_p)} Ar")
            st.markdown('</div>', unsafe_allow_html=True)

    g_f = df_f[df_f["Type"].isin(["Revenu", "Prêt +"])]["Montant"].sum() if not df_f.empty else 0
    p_f = df_f[df_f["Type"].isin(["Dépense", "Prêt -"])]["Montant"].sum() if not df_f.empty else 0
    g_p = df_p[df_p["Type"].isin(["Vente", "Prêt +"])]["Montant"].sum() if not df_p.empty else 0
    p_p = df_p[df_p["Type"].isin(["Dépense Projet", "Prêt -"])]["Montant"].sum() if not df_p.empty else 0

    st.markdown(f"### 📝 Édition : Transactions <span class='sticker'>{get_sticker(g_f, p_f)}</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Entrées", f"{format_num(g_f)} Ar", delta="↑ Hausse" if g_f > 0 else None)
    c2.metric("Sorties", f"{format_num(p_f)} Ar", delta="↓ Baisse" if p_f > 0 else None, delta_color="inverse")
    edited_f = st.data_editor(df_f, use_container_width=True, num_rows="dynamic", key="editeur_trans")
    
    st.markdown(f"### 📝 Édition : Projets <span class='sticker'>{get_sticker(g_p, p_p)}</span>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    c3.metric("Entrées", f"{format_num(g_p)} Ar", delta="↑ Hausse" if g_p > 0 else None)
    c4.metric("Sorties", f"{format_num(p_p)} Ar", delta="↓ Baisse" if p_p > 0 else None, delta_color="inverse")
    edited_p = st.data_editor(df_p, use_container_width=True, num_rows="dynamic", key="editeur_projets")
    
    if st.button("💾 Sauvegarder tout"):
        save_data(edited_f, data_file)
        save_data(edited_p, proj_file)
        st.rerun()

    st.divider()
    df_total = pd.concat([edited_f, edited_p], ignore_index=True)
    if not df_total.empty:
        gain, perte = g_f + g_p, p_f + p_p
        solde = gain - perte
        st.markdown(f"### 📊 Dashboard Global <span class='sticker'>{get_sticker(gain, perte)}</span>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Global Entrées", f"{format_num(gain)} Ar")
        c2.metric("Global Sorties", f"{format_num(perte)} Ar")
        c3.metric("Solde Global Net", f"{format_num(solde)} Ar", delta="CRITIQUE" if solde < 0 else "Positif", delta_color="inverse")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_pie = px.pie(df_total, values="Montant", names="Catégorie", title="Répartition")
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_g2:
            fig_bar = px.bar(df_total, x="Date", y="Montant", color="Type", title="Flux financier")
            fig_bar.update_yaxes(tickformat=".2s") 
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 4 : CAHIER DE NOTES ---
with tab4:
    st.subheader("📓 Cahier de Notes - Suivi des Besoins")
    
    # Charger les notes existantes pour l'utilisateur
    note_file = get_user_data_file("notes.csv")
    df_notes = load_notes(note_file)
    
    # Filtres pour le cahier de notes
    with st.expander("🔍 Filtrer les notes", expanded=True):
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<span class="filter-label">📅 Période</span>', unsafe_allow_html=True)
            filter_type = st.radio("Filtre temporel", ["Toutes", "Cette semaine", "Ce mois"], horizontal=True)
            
            if filter_type == "Cette semaine":
                today = datetime.now()
                start_of_week = today - timedelta(days=today.weekday())
                start_date_note = start_of_week.date()
                end_date_note = today.date()
            elif filter_type == "Ce mois":
                today = datetime.now()
                start_date_note = datetime(today.year, today.month, 1).date()
                end_date_note = today.date()
            else:
                start_date_note = st.date_input("Début", datetime(datetime.now().year, 1, 1), key="start_date_note")
                end_date_note = st.date_input("Fin", datetime.now(), key="end_date_note")
        
        with col2:
            st.markdown('<span class="filter-label">🔍 Recherche</span>', unsafe_allow_html=True)
            search_term = st.text_input("Rechercher un produit", placeholder="Ex: Ordinateur...", key="search_note")
        
        with col3:
            st.markdown('<span class="filter-label">📊 Produit</span>', unsafe_allow_html=True)
            all_products = ["Tous"] + sorted(df_notes["Produit"].astype(str).unique().tolist()) if not df_notes.empty else ["Tous"]
            product_filter = st.selectbox("Filtrer par produit", all_products, key="product_filter_note")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Application des filtres
    if not df_notes.empty:
        mask_note = pd.Series([True] * len(df_notes))
        
        if filter_type in ["Cette semaine", "Ce mois"]:
            mask_note &= (df_notes["Date"].dt.date >= start_date_note) & (df_notes["Date"].dt.date <= end_date_note)
        else:
            mask_note &= (df_notes["Date"].dt.date >= start_date_note) & (df_notes["Date"].dt.date <= end_date_note)
        
        if search_term:
            mask_note &= df_notes["Produit"].astype(str).str.contains(search_term, case=False, na=False)
        
        if product_filter != "Tous":
            mask_note &= (df_notes["Produit"].astype(str) == product_filter)
        
        df_notes_filtered = df_notes.loc[mask_note]
    else:
        df_notes_filtered = df_notes
    
    # Résumé des statistiques
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.markdown('<div class="summary-card">', unsafe_allow_html=True)
        st.metric("📝 Total notes", len(df_notes_filtered))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown('<div class="summary-card">', unsafe_allow_html=True)
        total_estimation = df_notes_filtered["Estimation"].sum() if not df_notes_filtered.empty else 0
        st.metric("💰 Total Estimations", f"{format_num(total_estimation)} Ar")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_stat3:
        st.markdown('<div class="summary-card">', unsafe_allow_html=True)
        total_reel = df_notes_filtered["Prix_Reel"].sum() if not df_notes_filtered.empty else 0
        st.metric("💵 Total Prix Réel", f"{format_num(total_reel)} Ar")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_stat4:
        st.markdown('<div class="summary-card">', unsafe_allow_html=True)
        ecart = total_estimation - total_reel
        delta_color = "normal" if ecart >= 0 else "inverse"
        st.metric("📊 Écart (Est - Réel)", f"{format_num(ecart)} Ar", 
                 delta="✅ Économie" if ecart > 0 else "❌ Dépassement" if ecart < 0 else "✅ Égal",
                 delta_color=delta_color)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Formulaire d'ajout de note
    with st.expander("➕ Ajouter une note", expanded=False):
        with st.form("note_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                date_note = st.date_input("Date", datetime.now())
            
            with col2:
                produit = st.text_input("Produit / Service", placeholder="Nom du produit...")
            
            with col3:
                besoins = st.text_area("Besoins", placeholder="Décrivez vos besoins...", height=68)
            
            with col4:
                estimation = st.number_input("Estimation (Ar)", min_value=0, step=500, value=0)
                prix_reel = st.number_input("Prix Réel (Ar)", min_value=0, step=500, value=0)
            
            if st.form_submit_button("📝 Ajouter la note"):
                if produit:
                    df_notes = load_notes(note_file)
                    new_row = {
                        "Date": date_note,
                        "Produit": produit,
                        "Besoins": besoins,
                        "Estimation": estimation,
                        "Prix_Reel": prix_reel
                    }
                    df_notes = pd.concat([df_notes, pd.DataFrame([new_row])], ignore_index=True)
                    save_notes(df_notes, note_file)
                    st.success("✅ Note ajoutée avec succès !")
                    st.rerun()
                else:
                    st.error("❌ Veuillez entrer un nom de produit")
    
    # Affichage du tableau des notes avec édition directe
    st.markdown("### 📋 Tableau des notes (Édition directe)")
    st.info("💡 Vous pouvez modifier directement les valeurs dans le tableau ci-dessous")
    
    if not df_notes_filtered.empty:
        # Créer une copie pour l'affichage avec les colonnes appropriées
        df_display = df_notes_filtered.copy()
        
        # Ajouter la colonne d'écart pour l'affichage
        df_display["Écart"] = df_display["Estimation"] - df_display["Prix_Reel"]
        
        # Convertir les dates en string pour l'affichage
        df_display["Date"] = df_display["Date"].dt.strftime("%d/%m/%Y")
        
        # S'assurer que les colonnes sont du bon type
        df_display["Estimation"] = pd.to_numeric(df_display["Estimation"], errors='coerce').fillna(0).astype(int)
        df_display["Prix_Reel"] = pd.to_numeric(df_display["Prix_Reel"], errors='coerce').fillna(0).astype(int)
        df_display["Écart"] = pd.to_numeric(df_display["Écart"], errors='coerce').fillna(0).astype(int)
        df_display["Besoins"] = df_display["Besoins"].fillna("").astype(str)
        df_display["Produit"] = df_display["Produit"].fillna("").astype(str)
        
        # Définir les colonnes pour l'édition directe
        edited_notes = st.data_editor(
            df_display,
            use_container_width=True,
            num_rows="dynamic",
            key="editeur_notes",
            column_config={
                "Date": st.column_config.TextColumn("📅 Date", required=True),
                "Produit": st.column_config.TextColumn("📦 Produit", required=True),
                "Besoins": st.column_config.TextColumn("📝 Besoins"),
                "Estimation": st.column_config.NumberColumn(
                    "💰 Estimation",
                    min_value=0,
                    step=500,
                    format="%d Ar"
                ),
                "Prix_Reel": st.column_config.NumberColumn(
                    "💵 Prix Réel",
                    min_value=0,
                    step=500,
                    format="%d Ar"
                ),
                "Écart": st.column_config.NumberColumn(
                    "📊 Écart",
                    format="%d Ar",
                    disabled=True
                )
            },
            hide_index=True
        )
        
        # Bouton de sauvegarde
        col_save1, col_save2, col_save3 = st.columns([1, 2, 1])
        with col_save2:
            if st.button("💾 Sauvegarder les modifications", use_container_width=True, type="primary"):
                try:
                    # Préparer les données pour la sauvegarde
                    df_to_save = edited_notes.copy()
                    
                    # Convertir la date
                    df_to_save["Date"] = pd.to_datetime(df_to_save["Date"], format="%d/%m/%Y", errors='coerce')
                    df_to_save = df_to_save.dropna(subset=["Date"])
                    
                    # Supprimer la colonne Écart
                    if "Écart" in df_to_save.columns:
                        df_to_save = df_to_save.drop(columns=["Écart"])
                    
                    # S'assurer que les colonnes sont au bon format
                    for col in ["Estimation", "Prix_Reel"]:
                        if col in df_to_save.columns:
                            df_to_save[col] = pd.to_numeric(df_to_save[col], errors='coerce').fillna(0)
                    
                    # S'assurer que les colonnes texte sont du bon type
                    for col in ["Produit", "Besoins"]:
                        if col in df_to_save.columns:
                            df_to_save[col] = df_to_save[col].fillna("").astype(str)
                    
                    # Sauvegarder
                    save_notes(df_to_save, note_file)
                    st.success("✅ Notes sauvegardées avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la sauvegarde : {str(e)}")
        
        # Résumé par produit
        st.divider()
        st.markdown("### 📊 Résumé par Produit")
        
        # Recalculer les résumés à partir des données éditées
        edited_data = edited_notes.copy()
        edited_data["Estimation"] = pd.to_numeric(edited_data["Estimation"], errors='coerce').fillna(0)
        edited_data["Prix_Reel"] = pd.to_numeric(edited_data["Prix_Reel"], errors='coerce').fillna(0)
        
        summary_by_product = edited_data.groupby("Produit").agg({
            "Estimation": "sum",
            "Prix_Reel": "sum"
        }).reset_index()
        
        summary_by_product["Écart"] = summary_by_product["Estimation"] - summary_by_product["Prix_Reel"]
        summary_by_product["Estimation"] = summary_by_product["Estimation"].apply(lambda x: f"{format_num(x)} Ar")
        summary_by_product["Prix_Reel"] = summary_by_product["Prix_Reel"].apply(lambda x: f"{format_num(x)} Ar")
        summary_by_product["Écart"] = summary_by_product["Écart"].apply(lambda x: f"{format_num(x)} Ar")
        
        st.dataframe(
            summary_by_product,
            use_container_width=True,
            column_config={
                "Produit": "📦 Produit",
                "Estimation": "💰 Total Estimation",
                "Prix_Reel": "💵 Total Prix Réel",
                "Écart": "📊 Écart Total"
            },
            hide_index=True
        )
        
        # Graphique comparatif
        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Préparer les données pour le graphique
            chart_data = edited_data.groupby("Produit").agg({
                "Estimation": "sum",
                "Prix_Reel": "sum"
            }).reset_index()
            
            fig_compare = px.bar(
                chart_data, 
                x="Produit", 
                y=["Estimation", "Prix_Reel"],
                title="Comparaison Estimation vs Prix Réel",
                barmode="group",
                color_discrete_sequence=["#667eea", "#764ba2"]
            )
            fig_compare.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                font_color="white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_compare, use_container_width=True)
        
        with col_chart2:
            chart_data["Écart"] = chart_data["Estimation"] - chart_data["Prix_Reel"]
            fig_ecart = px.bar(
                chart_data,
                x="Produit",
                y="Écart",
                title="Écart par Produit (Estimation - Prix Réel)",
                color="Écart",
                color_continuous_scale=["red", "yellow", "green"],
                text="Écart"
            )
            fig_ecart.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                font_color="white",
                showlegend=False
            )
            fig_ecart.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            st.plotly_chart(fig_ecart, use_container_width=True)
        
    else:
        st.info("📝 Aucune note trouvée. Commencez par ajouter une note !")