import streamlit as st
from auth import verificar_autenticacao

def verificar_usuario_logado():
    """Adapta verificar_autenticacao para retornar informações do usuário"""
    if verificar_autenticacao():
        usuario = {
            "login": st.session_state["usuario_atual"],
            "nome": st.session_state["nome_completo"],
            "cargo": "Não especificado",
            "admin": st.session_state["nivel_acesso"] == "admin",
            "gerente": st.session_state["nivel_acesso"] in ["gerente", "arquiteto"]
        }
        return usuario
    return None 