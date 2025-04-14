import streamlit as st
import os
import json
from datetime import datetime
from auth import login_page, mudar_senha, verificar_autenticacao
from rdo import criar_rdo, visualizar_relatorios, editar_rdo

# Configuração da página
st.set_page_config(
    page_title="Sistema de Relatórios Diários",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Criar diretórios necessários
os.makedirs("data", exist_ok=True)
os.makedirs("arquivos/pdfs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Inicializar variáveis de sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None
if "nivel_acesso" not in st.session_state:
    st.session_state.nivel_acesso = None
if "nome_completo" not in st.session_state:
    st.session_state.nome_completo = None
if "primeiro_acesso" not in st.session_state:
    st.session_state.primeiro_acesso = False
if "obras_atribuidas" not in st.session_state:
    st.session_state.obras_atribuidas = []

# Verificar autenticação
if not verificar_autenticacao():
    login_page()
else:
    if st.session_state.primeiro_acesso:
        mudar_senha()
    else:
        # Menu principal
        st.sidebar.title("Menu")
        opcao = st.sidebar.radio(
            "Selecione uma opção:",
            ["Criar RDO", "Visualizar RDOs", "Editar RDO"]
        )

        if opcao == "Criar RDO":
            criar_rdo()
        elif opcao == "Visualizar RDOs":
            visualizar_relatorios()
        elif opcao == "Editar RDO":
            editar_rdo()
