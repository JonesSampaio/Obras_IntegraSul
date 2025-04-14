import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Função para carregar dados de obras
def carregar_obras():
    try:
        with open("dados/obras.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para carregar equipes
def carregar_equipes():
    try:
        with open("dados/equipes.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para carregar funcionários
def carregar_funcionarios():
    try:
        with open("dados/funcionarios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para carregar relatórios
def carregar_relatorios():
    try:
        with open("dados/relatorios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para salvar relatórios
def salvar_relatorios(relatorios):
    with open("dados/relatorios.json", "w") as f:
        json.dump(relatorios, f, indent=4)

# Função para criar um novo RDO
def criar_rdo():
    st.title("Relatório Diário de Obra (RDO)")
    
    obras = carregar_obras()
    equipes = carregar_equipes()
    funcionarios = carregar_funcionarios()
    
    # Se o usuário for encarregado, mostrar apenas as obras atribuídas
    if st.session_state.nivel_acesso == "usuario" and 'obras_atribuidas' in st.session_state:
        obras_disponiveis = {k: v for k, v in obras.items() if k in st.session_state.obras_atribuidas}
    else:
        obras_disponiveis = obras
    
    if not obras_disponiveis:
        st.warning("Não há obras disponíveis para este usuário.")
        return
    
    # Selecionar obra
    obra_selecionada = st.selectbox("Selecione a Obra", list(obras_disponiveis.keys()))
    
    if obra_selecionada:
        data_relatorio = st.date_input("Data do Relatório", datetime.now())
        
        # Preencher automaticamente dados da obra
        dados_obra = obras[obra_selecionada]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Endereço:** {dados_obra['endereco']}")
            st.write(f"**Responsável Técnico:** {dados_obra['responsavel_tecnico']}")
        with col2:
            st.write(f"**Prazo:** {dados_obra['prazo_inicio']} a {dados_obra['prazo_fim']}")
            st.write(f"**RRT:** {dados_obra['rrt']}")
        
        # Equipes da obra
        equipes_obra = [nome for nome, e in equipes.items() if e["obra"] == obra_selecionada]
        
        if equipes_obra:
            equipe_selecionada = st.selectbox("Equipe", equipes_obra)
            
            if equipe_selecionada:
                # Mostrar membros da equipe
                membros = equipes[equipe_selecionada]["membros"]
                st.write("**Membros da Equipe:**")
                for membro in membros:
                    st.write(f"- {membro}")
        else:
            st.warning("Não há equipes cadastradas para esta obra.")
            equipe_selecionada = None
        
        # Formulário para preenchimento do relatório
        with st.form("formulario_rdo"):
            st.subheader("Dados do Relatório")
            
            # Condições climáticas
            clima = st.selectbox("Condições Climáticas", 
                               ["Ensolarado", "Nublado", "Chuvoso", "Tempestade", "Outro"])
            
            # Atividades realizadas
            atividades = st
