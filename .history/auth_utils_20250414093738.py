import streamlit as st
from auth import verificar_autenticacao

def verificar_usuario_logado():
    """Adapta verificar_autenticacao para retornar informações do usuário"""
    if verificar_autenticacao():
        return {
            "login": st.session_state["usuario_atual"],
            "nome": st.session_state["nome_completo"],
            "cargo": "Não especificado", # Ou adapte conforme necessário
            "admin": st.session_state["nivel_acesso"] == "admin"
        }
    return None 