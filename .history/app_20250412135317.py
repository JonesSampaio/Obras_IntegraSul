import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import auth
import admin
import rdo
import utils

# Configurações da página
st.set_page_config(
    page_title="Sistema de Gestão de Obras",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar sistema de arquivos
def inicializar_sistema():
    diretorios = ['dados', 'relatorios']
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
    
    # Criar arquivos de dados iniciais se não existirem
    arquivos = {
        'dados/usuarios.json': {'gestao': {'senha': utils.hash_senha('admin123'), 'nivel': 'admin', 'nome_completo': 'Administrador do Sistema', 'primeiro_acesso': False}},
        'dados/obras.json': {},
        'dados/funcionarios.json': {},
        'dados/equipes.json': {}
    }
    
    for arquivo, dados_iniciais in arquivos.items():
        if not os.path.exists(arquivo):
            with open(arquivo, 'w') as f:
                json.dump(dados_iniciais, f, indent=4)

# Inicializar sistema
inicializar_sistema()

# Verificar se o usuário está autenticado
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.primeiro_acesso = False

# Fluxo principal do aplicativo
if not st.session_state.autenticado:
    auth.tela_login()
elif st.session_state.primeiro_acesso:
    auth.alterar_senha_primeiro_acesso()
else:
    # Sidebar com menu de navegação baseado no nível de acesso
    with st.sidebar:
        st.write(f"Olá, {st.session_state.nome_completo}")
        st.write(f"Nível de acesso: {st.session_state.nivel_acesso.capitalize()}")
        
        # Menu baseado no nível de acesso
        if st.session_state.nivel_acesso == "admin":
            opcoes = ["Painel de Gestão", "Criar RDO", "Visualizar Relatórios", "Gerenciar Sistema"]
        elif st.session_state.nivel_acesso == "gerente":
            opcoes = ["Painel de Gestão", "Criar RDO", "Visualizar Relatórios"]
        else:  # encarregado
            opcoes = ["Criar RDO", "Meus Relatórios"]
            
        opcao = st.sidebar.selectbox("Menu", opcoes)
        
        if st.sidebar.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
    
    # Exibir conteúdo baseado na opção selecionada
    if opcao == "Painel de Gestão":
        admin.painel_de_gestao()
    elif opcao == "Criar RDO":
        rdo.criar_rdo()
    elif opcao == "Visualizar Relatórios" or opcao == "Meus Relatórios":
        rdo.visualizar_relatorios()
    elif opcao == "Gerenciar Sistema":
        admin.gerenciar_sistema()
