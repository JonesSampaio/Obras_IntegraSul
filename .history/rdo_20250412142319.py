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
            atividades = st.text_area("Atividades Realizadas", height=150)
            
            # Ocorrências e observações
            ocorrencias = st.text_area("Ocorrências e Observações", height=100)
            
            # Materiais recebidos
            materiais = st.text_area("Materiais Recebidos", height=100)
            
            # Equipamentos utilizados
            equipamentos = st.text_area("Equipamentos Utilizados", height=100)
            
            # Efetivo presente
            efetivo_presente = st.number_input("Efetivo Presente", min_value=1, value=1)
            
            # Upload de fotos (opcional)
            fotos = st.file_uploader("Adicionar Fotos (opcional)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            
            # Botão de envio
            submitted = st.form_submit_button("Enviar Relatório")
            
            if submitted:
                # Gerar ID único para o relatório
                relatorio_id = f"{obra_selecionada}_{data_relatorio.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}"
                
                # Criar dicionário do relatório
                novo_relatorio = {
                    "id": relatorio_id,
                    "obra": obra_selecionada,
                    "data": data_relatorio.strftime("%Y-%m-%d"),
                    "criado_por": st.session_state.nome_completo,
                    "usuario": st.session_state.usuario_atual,
                    "clima": clima,
                    "atividades": atividades,
                    "ocorrencias": ocorrencias,
                    "materiais": materiais,
                    "equipamentos": equipamentos,
                    "efetivo_presente": efetivo_presente,
                    "equipe": equipe_selecionada if equipe_selecionada else "",
                    "hora_criacao": datetime.now().strftime("%H:%M:%S"),
                    "fotos": []  # Aqui seria necessário implementar o salvamento de fotos
                }
                
                # Salvar relatório
                relatorios = carregar_relatorios()
                relatorios[relatorio_id] = novo_relatorio
                salvar_relatorios(relatorios)
                
                st.success(f"Relatório {relatorio_id} criado com sucesso!")

# Função para visualizar relatórios (que estava faltando)
def visualizar_relatorios():
    st.title("Visualizar Relatórios")
    
    relatorios = carregar_relatorios()
    
    if not relatorios:
        st.warning("Não há relatórios disponíveis.")
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        # Filtrar por obra
        obras = carregar_obras()
        
        # Se o usuário for encarregado, mostrar apenas as obras atribuídas
        if st.session_state.nivel_acesso == "usuario" and 'obras_atribuidas' in st.session_state:
            obras_disponiveis = [obra for obra in list(obras.keys()) if obra in st.session_state.obras_atribuidas]
        else:
            obras_disponiveis = list(obras.keys())
        
        obra_filtro = st.selectbox("Filtrar por Obra", ["Todas"] + obras_disponiveis)
    
    with col2:
        # Filtrar por data
        data_filtro = st.date_input("Filtrar por Data", datetime.now())
    
    # Aplicar filtros
    relatorios_filtrados = relatorios.copy()
    
    if obra_filtro != "Todas":
        relatorios_filtrados = {k: v for k, v in relatorios_filtrados.items() if v["obra"] == obra_filtro}
    
    if data_filtro:
        data_str = data_filtro.strftime("%Y-%m-%d")
        relatorios_filtrados = {k: v for k, v in relatorios_filtrados.items() if v["data"] == data_str}
    
    # Ordenar por data (mais recente primeiro)
    relatorios_ordenados = dict(sorted(relatorios_filtrados.items(), 
                                      key=lambda item: item[1]["data"] + item[1]["hora_criacao"], 
                                      reverse=True))
    
    # Exibir relatórios
    st.subheader(f"Relatórios encontrados: {len(relatorios_ordenados)}")
    
    for rel_id, relatorio in relatorios_ordenados.items():
        with st.expander(f"{relatorio['obra']} - {relatorio['data']} - {rel_id}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Obra:** {relatorio['obra']}")
                st.write(f"**Data:** {relatorio['data']}")
                st.write(f"**Clima:** {relatorio['clima']}")
                st.write(f"**Efetivo Presente:** {relatorio['efetivo_presente']}")
                st.write(f"**Equipe:** {relatorio['equipe']}")
            with col2:
                st.write(f"**Criado por:** {relatorio['criado_por']}")
                st.write(f"**Usuário:** {relatorio['usuario']}")
                st.write(f"**Hora:** {relatorio['hora_criacao']}")
            
            st.subheader("Atividades Realizadas")
            st.write(relatorio['atividades'])
            
            st.subheader("Ocorrências e Observações")
            st.write(relatorio['ocorrencias'])
            
            st.subheader("Materiais Recebidos")
            st.write(relatorio['materiais'])
            
            st.subheader("Equipamentos Utilizados")
            st.write(relatorio['equipamentos'])
            
            # Aqui mostrar fotos se houver
            if relatorio['fotos'] and len(relatorio['fotos']) > 0:
                st.subheader("Fotos")
                # Implementar visualização das fotos
