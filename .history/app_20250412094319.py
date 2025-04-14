import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração básica
st.set_page_config(page_title="Relatórios de Obra", layout="wide")

# Autenticação simples
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # Lógica simples de autenticação (substitua por algo mais seguro depois)
        if usuario == "engenheiro" and senha == "obra123":
            st.session_state.autenticado = True
            st.experimental_rerun()
        else:
            st.error("Credenciais inválidas")
else:
    # Interface principal
    st.title("Relatório Diário de Obra")
    
    # Cabeçalho do relatório
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.today())
        nome_obra = st.text_input("Nome da Obra")
    with col2:
        clima = st.selectbox("Condições Climáticas", 
                            ["Ensolarado", "Nublado", "Chuvoso", "Parcialmente nublado"])
        temperatura = st.number_input("Temperatura (°C)", min_value=-10, max_value=50)
    
    # Detalhes da equipe
    st.subheader("Equipe presente")
    num_funcionarios = st.number_input("Número de funcionários", min_value=0, max_value=1000, step=1)
    
    # Atividades
    st.subheader("Atividades Realizadas")
    atividades = st.text_area("Descreva as atividades realizadas hoje")
    
    # Upload de fotos
    st.subheader("Fotos da Obra")
    fotos = st.file_uploader("Carregar fotos", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
    
    # Observações
    st.subheader("Problemas e Observações")
    problemas = st.text_area("Problemas encontrados")
    observacoes = st.text_area("Observações gerais")
    
    # Avanço físico
    st.subheader("Avanço Físico")
    avanco = st.slider("Percentual de avanço da obra", 0, 100, 0)
    
    # Botão salvar (exemplo básico - em produção usaria banco de dados)
    if st.button("Salvar Relatório"):
        # Aqui você implementaria a lógica de salvar em CSV ou banco de dados
        # Exemplo simples salvando em CSV:
        relatorio = {
            "data": data.strftime("%Y-%m-%d"),
            "obra": nome_obra,
            "clima": clima,
            "temperatura": temperatura,
            "num_funcionarios": num_funcionarios,
            "atividades": atividades,
            "problemas": problemas,
            "observacoes": observacoes,
            "avanco": avanco,
        }
        
        # Salvar em CSV (exemplo)
        df_relatorio = pd.DataFrame([relatorio])
        
        # Verificar se o arquivo existe para adicionar cabeçalho apenas na primeira vez
        arquivo_existe = os.path.isfile("relatorios.csv")
        df_relatorio.to_csv("relatorios.csv", mode='a', header=not arquivo_existe, index=False)
        
        st.success("Relatório salvo com sucesso!")
        
    # Botão para logout
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.experimental_rerun()
