import streamlit as st
import json
import os
import hashlib
import secrets
from datetime import datetime
import time

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Carregar usuários do arquivo
def carregar_usuarios():
    try:
        with open("data/usuarios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver vazio, criar com usuário admin padrão
        usuarios = {
            "admin": {
                "senha": hash_senha("admin123"),
                "nivel": "admin",
                "nome_completo": "Administrador do Sistema",
                "primeiro_acesso": True,
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        salvar_usuarios(usuarios)
        return usuarios

# Salvar usuários no arquivo
def salvar_usuarios(usuarios):
    os.makedirs("data", exist_ok=True)
    with open("data/usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=4)

# Função para autenticar usuário
def autenticar_usuario(login, senha):
    usuarios = carregar_usuarios()
    if login in usuarios and hash_senha(senha) == usuarios[login]["senha"]:
        return True
    return False

# Função para obter nível de acesso
def obter_nivel_acesso(login):
    usuarios = carregar_usuarios()
    return usuarios.get(login, {}).get("nivel", "usuario")

# Função para obter nome completo
def obter_nome_completo(login):
    usuarios = carregar_usuarios()
    return usuarios.get(login, {}).get("nome_completo", login)

# Função para verificar primeiro acesso
def verificar_primeiro_acesso(login):
    usuarios = carregar_usuarios()
    return usuarios.get(login, {}).get("primeiro_acesso", False)

# Função de login
def login_page():
    """Página de login"""
    st.title("Login")
    
    # Campos de login
    login = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    # Botão de login
    if st.button("Entrar"):
        if autenticar_usuario(login, senha):
            st.session_state.autenticado = True
            st.session_state.usuario_atual = login
            st.session_state.nivel_acesso = obter_nivel_acesso(login)
            st.session_state.nome_completo = obter_nome_completo(login)
            st.session_state.primeiro_acesso = verificar_primeiro_acesso(login)
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")
    
    # Botão para mudar senha
    if st.button("Mudar Senha"):
        st.session_state.mudar_senha = True
        st.rerun()

# Função para mudar senha no primeiro acesso
def mudar_senha():
    st.title("Primeiro acesso - Alterar senha")
    st.info("Você precisa alterar sua senha para continuar.")
    
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password")
    
    if st.button("Salvar nova senha"):
        if nova_senha == confirmar_senha and len(nova_senha) >= 6:
            usuarios = carregar_usuarios()
            usuario = st.session_state.usuario_atual
            
            usuarios[usuario]["senha"] = hash_senha(nova_senha)
            usuarios[usuario]["primeiro_acesso"] = False
            usuarios[usuario]["ultima_alteracao_senha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            salvar_usuarios(usuarios)
            
            st.session_state.primeiro_acesso = False
            st.success("Senha alterada com sucesso!")
            # Redireciona para a página principal
            st.rerun()
        elif len(nova_senha) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
        else:
            st.error("As senhas não coincidem.")

# Verificar autenticação
def verificar_autenticacao():
    return st.session_state.get('autenticado', False)

# Logout
def logout():
    for key in ['autenticado', 'usuario_atual', 'nivel_acesso', 'nome_completo', 'obras_atribuidas']:
        if key in st.session_state:
            del st.session_state[key]

