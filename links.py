import streamlit as st
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

# Fonction d'authentification
def authenticate(url, username, password):
    ctx_auth = AuthenticationContext(url)
    if ctx_auth.acquire_token_for_user(username, password):
        ctx = ClientContext(url, ctx_auth)
        return ctx
    else:
        return None

# Fonction pour lister les fichiers et dossiers dans un dossier SharePoint
def list_files_and_folders_in_folder(ctx, folder_url, search_term='', depth=0, url_shrpt=''):
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    ctx.load(folder)
    ctx.execute_query()

    files = folder.files
    ctx.load(files)
    ctx.execute_query()

    folders = folder.folders
    ctx.load(folders)
    ctx.execute_query()

    for file in files:
        if search_term.lower() in file.properties['Name'].lower():
            st.markdown(f"<a href='{url_shrpt + file.properties['ServerRelativeUrl']}' target='_blank'>{file.properties['Name']}</a>", unsafe_allow_html=True)

    for folder in folders:
        if search_term.lower() in folder.properties['Name'].lower():
            st.write("  " * depth + f"📁 {folder.properties['Name']}")
        list_files_and_folders_in_folder(ctx, f"{folder_url}/{folder.properties['Name']}", search_term, depth + 1, url_shrpt)

# Page de connexion
def login_page():
    st.title("Page de connexion à SharePoint")
    url_shrpt = 'https://segulagrp.sharepoint.com/sites/SystemEngTeam/'
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    folder_url = 'Documents partages/Training'

    if st.button("Se connecter"):
        ctx = authenticate(url_shrpt, username, password)
        if ctx:
            st.success("Connexion réussie!")
            st.session_state.authenticated = True
            st.session_state.ctx = ctx
            st.session_state.folder_url = folder_url
            st.session_state.url_shrpt = url_shrpt
            st.experimental_rerun()
        else:
            st.error("Échec de l'authentification. Veuillez vérifier vos informations d'identification.")

# Page principale
def main_page():
    st.title("Arborescence de fichiers et dossiers dans SharePoint")
    search_term = st.text_input("Rechercher des fichiers et des dossiers")

    if st.button("Lister les documents et dossiers"):
        try:
            st.success(f"Arborescence de fichiers et dossiers dans le dossier {st.session_state.folder_url}:")
            list_files_and_folders_in_folder(st.session_state.ctx, st.session_state.folder_url, search_term, url_shrpt=st.session_state.url_shrpt)
        except Exception as e:
            st.error(f"Erreur lors de la récupération des fichiers et dossiers : {e}")

# Routage entre les pages
if 'authenticated' not in st.session_state:
    login_page()
else:
    main_page()
