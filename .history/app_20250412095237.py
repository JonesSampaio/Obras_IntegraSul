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
            st.rerun()
        else:
            st.error("Credenciais inválidas")
else:
    # Interface principal
    st.title("Relatório Diário de Obra")
    
    # Cabeçalho do relatório
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.today())
        # Lista predefinida de obras
        lista_obras = ["Edifício Aurora", "Residencial Bela Vista", "Centro Comercial Plaza", "Condomínio Parque das Flores"]
        nome_obra = st.selectbox("Selecione a Obra", lista_obras)
    with col2:
        clima = st.selectbox("Condições Climáticas", 
                            ["Ensolarado", "Nublado", "Chuvoso", "Parcialmente nublado"])
        temperatura = st.number_input("Temperatura (°C)", min_value=-10, max_value=50)
    
    # Detalhes da equipe
    st.subheader("Equipe presente")
    num_funcionarios = st.number_input("Número total de funcionários", min_value=0, max_value=1000, step=1)
    
    # Lista de funcionários específicos
    st.write("Funcionários presentes:")
    
    # Lista predefinida de possíveis funcionários
    todos_funcionarios = [
        "João Silva - Pedreiro", 
        "Carlos Oliveira - Mestre de obras",
        "Maria Santos - Engenheira civil",
        "Pedro Souza - Eletricista",
        "Ana Costa - Arquiteta",
        "Lucas Ferreira - Ajudante",
        "Roberto Almeida - Encanador",
        "Fernanda Lima - Pintora"
    ]
    
    # Criar checkboxes para cada funcionário
    funcionarios_presentes = []
    cols = st.columns(2)  # Dividir em duas colunas para economizar espaço
    
    for i, funcionario in enumerate(todos_funcionarios):
        with cols[i % 2]:  # Alterna entre as colunas
            if st.checkbox(funcionario, key=f"func_{i}"):
                funcionarios_presentes.append(funcionario)
                
    # Opção para adicionar funcionários não listados
    with st.expander("Adicionar outro funcionário"):
        novo_funcionario = st.text_input("Nome do funcionário")
        cargo = st.text_input("Cargo")
        if st.button("Adicionar à lista"):
            if novo_funcionario and cargo:
                funcionario_completo = f"{novo_funcionario} - {cargo}"
                funcionarios_presentes.append(funcionario_completo)
                st.success(f"Adicionado: {funcionario_completo}")
    
    # Atividades
    st.subheader("Atividades Realizadas")
    atividades = st.text_area("Descreva as atividades realizadas hoje")
    
    # Upload de arquivos (fotos E PDFs)
    st.subheader("Arquivos e Fotos")
    uploaded_files = st.file_uploader(
        "Carregar fotos e documentos", 
        accept_multiple_files=True, 
        type=["jpg", "jpeg", "png", "pdf"]
    )
    
    if uploaded_files:
        st.write(f"Arquivos carregados: {len(uploaded_files)}")
        for file in uploaded_files:
            file_type = file.name.split('.')[-1].lower()
            if file_type in ['jpg', 'jpeg', 'png']:
                st.image(file, caption=file.name, width=300)
            elif file_type == 'pdf':
                st.write(f"📄 PDF: {file.name}")
    
    # Observações
    st.subheader("Problemas e Observações")
    problemas = st.text_area("Problemas encontrados")
    observacoes = st.text_area("Observações gerais")
    
    # Simplificando a parte de avanço físico
    st.subheader("Situação da Obra")
    status_obra = st.radio(
        "Status atual da obra:",
        ["Conforme cronograma", "Adiantada", "Atrasada"]
    )
    
    # Botão salvar
    if st.button("Salvar Relatório"):
        # Criando o dicionário de dados para salvar
        relatorio = {
            "data": data.strftime("%Y-%m-%d"),
            "obra": nome_obra,
            "clima": clima,
            "temperatura": temperatura,
            "num_funcionarios": num_funcionarios,
            "funcionarios_presentes": ", ".join(funcionarios_presentes),
            "atividades": atividades,
            "problemas": problemas,
            "observacoes": observacoes,
            "status_obra": status_obra,
        }
        
        # Salvar em CSV
        df_relatorio = pd.DataFrame([relatorio])
        
        # Verificar se o arquivo existe para adicionar cabeçalho apenas na primeira vez
        arquivo_existe = os.path.isfile("relatorios.csv")
        df_relatorio.to_csv("relatorios.csv", mode='a', header=not arquivo_existe, index=False)
        
        # Lidando com os arquivos
        if uploaded_files:
            # Criar pasta para arquivos se não existir
            pasta_data = data.strftime("%Y-%m-%d")
            pasta_obra = nome_obra.replace(" ", "_")
            pasta_destino = f"arquivos/{pasta_obra}/{pasta_data}"
            
            os.makedirs(pasta_destino, exist_ok=True)
            
            # Salvar arquivos
            for file in uploaded_files:
                with open(f"{pasta_destino}/{file.name}", "wb") as f:
                    f.write(file.getbuffer())
            
            st.success(f"Relatório e {len(uploaded_files)} arquivos salvos com sucesso!")
        else:
            st.success("Relatório salvo com sucesso!")
        
    # Botão para logout
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()
