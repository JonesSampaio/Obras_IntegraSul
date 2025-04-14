import streamlit as st
import os
from auth import login_page, verificar_autenticacao, logout, mudar_senha
from admin import painel_administrativo
from rdo import criar_rdo, visualizar_relatorios


# Configurações da página
st.set_page_config(
    page_title="Sistema de Gestão de Obras",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Criar estrutura de pastas se não existir
if not os.path.exists("dados"):
    os.makedirs("dados")


# Criar diretório para anexos se não existir
if not os.path.exists("dados/anexos"):
    os.makedirs("dados/anexos")


# Verificar arquivos essenciais
for arquivo in ["usuarios.json", "obras.json", "funcionarios.json", "equipes.json", "relatorios.json"]:
    caminho = os.path.join("dados", arquivo)
    if not os.path.exists(caminho):
        with open(caminho, 'w') as f:
            f.write("{}")


# A configuração de tamanho máximo agora é definida no arquivo .streamlit/config.toml
# e não mais via st.set_option()


# Inicializar estado da sessão se necessário
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.primeiro_acesso = False
    st.session_state.usuario_atual = None
    st.session_state.nivel_acesso = None
    st.session_state.nome_completo = None


# Renderizar a página apropriada
if not st.session_state.autenticado:
    login_page()
elif st.session_state.primeiro_acesso:
    mudar_senha()
else:
    # Sidebar com informações do usuário e logout
    st.sidebar.title("Sistema de Gestão de Obras")
    st.sidebar.write(f"Usuário: {st.session_state.nome_completo}")
    st.sidebar.write(f"Nível: {st.session_state.nivel_acesso}")

    # Menu diferente para cada nível de acesso
    if st.session_state.nivel_acesso == "admin":
        opcao = st.sidebar.radio(
            "Menu",
            ["Painel Administrativo", "Criar RDO", "Visualizar Relatórios"]
        )
    elif st.session_state.nivel_acesso == "gerente":
        opcao = st.sidebar.radio(
            "Menu",
            ["Painel Administrativo", "Criar RDO", "Visualizar Relatórios"]
        )
    else: # Nível "usuario" (encarregados)
        opcao = st.sidebar.radio(
            "Menu",
            ["Criar RDO", "Meus Relatórios"]
        )

    if st.sidebar.button("Sair"):
        logout()
        st.rerun()

    # Renderizar a página selecionada
    if opcao == "Painel Administrativo":
        painel_administrativo()
    elif opcao == "Criar RDO" or opcao == None:
        criar_rdo()
    elif opcao == "Visualizar Relatórios" or opcao == "Meus Relatórios":
        visualizar_relatorios()
