import streamlit as st
import json
import os
from auth import carregar_usuarios, salvar_usuarios, hash_senha
from datetime import datetime
from rdo import verificar_usuario_logado

# Carregar dados de obras
def carregar_obras():
    try:
        with open("dados/obras.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Salvar dados de obras
def salvar_obras(obras):
    with open("dados/obras.json", "w") as f:
        json.dump(obras, f, indent=4)

# Carregar dados de funcionários
def carregar_funcionarios():
    try:
        with open("dados/funcionarios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Salvar dados de funcionários
def salvar_funcionarios(funcionarios):
    with open("dados/funcionarios.json", "w") as f:
        json.dump(funcionarios, f, indent=4)

# Carregar dados de equipes
def carregar_equipes():
    try:
        with open("dados/equipes.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Salvar dados de equipes
def salvar_equipes(equipes):
    with open("dados/equipes.json", "w") as f:
        json.dump(equipes, f, indent=4)

# Painel administrativo principal
def painel_administrativo():
    st.title("Painel Administrativo")
    
    # Verificar se usuário é admin ou gerente
    if st.session_state.nivel_acesso not in ["admin", "gerente"]:
        st.error("Você não tem permissão para acessar esta área")
        return
    
    # Abas do painel administrativo
    tabs = ["Obras", "Funcionários", "Equipes", "Relatórios"]
    
    # Adicionar aba de usuários apenas para admins
    if st.session_state.nivel_acesso == "admin":
        tabs.append("Usuários")
    
    tab1, tab2, tab3, tab4, *extra_tabs = st.tabs(tabs)
    
    with tab1:
        gerenciar_obras()
    
    with tab2:
        gerenciar_funcionarios()
    
    with tab3:
        gerenciar_equipes()
    
    with tab4:
        visualizar_dashboard()
    
    # Gerenciamento de usuários apenas para admin
    if st.session_state.nivel_acesso == "admin" and len(extra_tabs) > 0:
        with extra_tabs[0]:
            gerenciar_usuarios()

# Função para gerenciar obras
def gerenciar_obras():
    st.header("Gerenciamento de Obras")
    
    obras = carregar_obras()
    
    # Formulário para adicionar nova obra
    with st.expander("Adicionar Nova Obra", expanded=False):
        with st.form("nova_obra"):
            nome_obra = st.text_input("Nome da Obra")
            endereco = st.text_input("Endereço")
            prazo_inicio = st.date_input("Data de Início")
            prazo_fim = st.date_input("Prazo de Conclusão")
            rrt = st.text_input("Número do RRT")
            responsavel_tecnico = st.text_input("Responsável Técnico")
            
            submitted = st.form_submit_button("Adicionar Obra")
            if submitted and nome_obra:
                obras[nome_obra] = {
                    "endereco": endereco,
                    "prazo_inicio": prazo_inicio.strftime("%Y-%m-%d"),
                    "prazo_fim": prazo_fim.strftime("%Y-%m-%d"),
                    "rrt": rrt,
                    "responsavel_tecnico": responsavel_tecnico,
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                salvar_obras(obras)
                st.success(f"Obra '{nome_obra}' adicionada com sucesso!")
                st.rerun()
    
    # Listar e editar obras existentes
    st.subheader("Obras Cadastradas")
    for nome_obra, dados in obras.items():
        with st.expander(nome_obra):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Endereço:** {dados['endereco']}")
                st.write(f"**Período:** {dados['prazo_inicio']} a {dados['prazo_fim']}")
                st.write(f"**RRT:** {dados['rrt']}")
                st.write(f"**Responsável:** {dados['responsavel_tecnico']}")
            
            with col2:
                # Botão para editar obra
                if st.button("Editar", key=f"edit_{nome_obra}"):
                    st.session_state.obra_para_editar = nome_obra
                
                # Botão para excluir obra - apenas admin pode excluir
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir", key=f"del_{nome_obra}"):
                        if nome_obra in obras:
                            del obras[nome_obra]
                            salvar_obras(obras)
                            st.success(f"Obra '{nome_obra}' excluída com sucesso!")
                            st.rerun()

# Função para gerenciar funcionários
def gerenciar_funcionarios():
    st.header("Gerenciamento de Funcionários")
    
    funcionarios = carregar_funcionarios()
    
    # Formulário para adicionar novo funcionário
    with st.expander("Adicionar Novo Funcionário", expanded=False):
        with st.form("novo_funcionario"):
            nome = st.text_input("Nome Completo")
            funcao = st.text_input("Função")
            obras = carregar_obras()
            obra_selecionada = st.multiselect("Obras Atribuídas", list(obras.keys()))
            
            submitted = st.form_submit_button("Adicionar Funcionário")
            if submitted and nome:
                funcionarios[nome] = {
                    "nome": nome,
                    "funcao": funcao,
                    "obras": obra_selecionada,
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                salvar_funcionarios(funcionarios)
                st.success(f"Funcionário '{nome}' adicionado com sucesso!")
                st.rerun()
    
    # Listar e editar funcionários existentes
    st.subheader("Funcionários Cadastrados")
    for nome, dados in funcionarios.items():
        with st.expander(nome):
            st.write(f"**Função:** {dados['funcao']}")
            st.write(f"**Obras Atribuídas:** {', '.join(dados['obras'])}")
            
            # Botão para editar funcionário
            if st.button("Editar", key=f"edit_{nome}"):
                st.session_state.funcionario_para_editar = nome
            
            # Botão para excluir funcionário - apenas admin pode excluir
            if st.session_state.nivel_acesso == "admin":
                if st.button("Excluir", key=f"del_{nome}"):
                    if nome in funcionarios:
                        del funcionarios[nome]
                        salvar_funcionarios(funcionarios)
                        st.success(f"Funcionário '{nome}' excluído com sucesso!")
                        st.rerun()

# Função para gerenciar equipes
def gerenciar_equipes():
    st.header("Gerenciamento de Equipes")
    
    equipes = carregar_equipes()
    funcionarios = carregar_funcionarios()
    obras = carregar_obras()
    
    # Formulário para criar nova equipe
    with st.expander("Criar Nova Equipe", expanded=False):
        with st.form("nova_equipe"):
            nome_equipe = st.text_input("Nome da Equipe")
            obra_equipe = st.selectbox("Obra", list(obras.keys()))
            membros = st.multiselect("Membros da Equipe", list(funcionarios.keys()))
            
            submitted = st.form_submit_button("Criar Equipe")
            if submitted and nome_equipe and obra_equipe:
                equipes[nome_equipe] = {
                    "nome": nome_equipe,
                    "obra": obra_equipe,
                    "membros": membros,
                    "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                salvar_equipes(equipes)
                st.success(f"Equipe '{nome_equipe}' criada com sucesso!")
                st.rerun()
    
    # Listar e editar equipes existentes
    st.subheader("Equipes Cadastradas")
    for nome_equipe, dados in equipes.items():
        with st.expander(nome_equipe):
            st.write(f"**Obra:** {dados['obra']}")
            st.write(f"**Membros:** {', '.join(dados['membros'])}")
            
            # Botão para editar equipe
            if st.button("Editar", key=f"edit_{nome_equipe}"):
                st.session_state.equipe_para_editar = nome_equipe
            
            # Botão para excluir equipe - apenas admin pode excluir
            if st.session_state.nivel_acesso == "admin":
                if st.button("Excluir", key=f"del_{nome_equipe}"):
                    if nome_equipe in equipes:
                        del equipes[nome_equipe]
                        salvar_equipes(equipes)
                        st.success(f"Equipe '{nome_equipe}' excluída com sucesso!")
                        st.rerun()

# Função para visualizar dashboard
def visualizar_dashboard():
    st.header("Dashboard de Obras")
    
    obras = carregar_obras()
    equipes = carregar_equipes()
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Obras", len(obras))
    with col2:
        st.metric("Total de Equipes", len(equipes))
    with col3:
        # Calcular obras em andamento
        hoje = datetime.now().strftime("%Y-%m-%d")
        obras_andamento = sum(1 for obra in obras.values() 
                            if obra["prazo_inicio"] <= hoje <= obra["prazo_fim"])
        st.metric("Obras em Andamento", obras_andamento)
    
    # Listar obras com status
    st.subheader("Status das Obras")
    for nome_obra, dados in obras.items():
        with st.expander(nome_obra):
            # Calcular progresso
            data_inicio = datetime.strptime(dados["prazo_inicio"], "%Y-%m-%d")
            data_fim = datetime.strptime(dados["prazo_fim"], "%Y-%m-%d")
            hoje = datetime.now()
            
            if hoje < data_inicio:
                status = "Não iniciada"
                progresso = 0
            elif hoje > data_fim:
                status = "Concluída"
                progresso = 100
            else:
                status = "Em andamento"
                total_dias = (data_fim - data_inicio).days
                dias_passados = (hoje - data_inicio).days
                progresso = min(100, int((dias_passados / total_dias) * 100))
            
            st.write(f"**Status:** {status}")
            st.progress(progresso)
            
            # Mostrar equipes associadas a esta obra
            equipes_obra = [nome for nome, e in equipes.items() if e["obra"] == nome_obra]
            if equipes_obra:
                st.write(f"**Equipes:** {', '.join(equipes_obra)}")

# Função para gerenciar usuários (apenas admin)
def gerenciar_usuarios():
    """Interface para gerenciar usuários do sistema"""
    st.title("Gerenciamento de Usuários")
    
    # Verificar se o usuário atual é admin
    if not verificar_usuario_logado() or not verificar_usuario_logado()["admin"]:
        st.error("Acesso negado. Apenas administradores podem gerenciar usuários.")
        return
    
    # Carregar usuários existentes
    usuarios = carregar_usuarios()
    
    # Formulário para adicionar novo usuário
    st.subheader("Adicionar Novo Usuário")
    with st.form("novo_usuario_form"):
        nome_usuario = st.text_input("Nome de Usuário")
        nome_completo = st.text_input("Nome Completo")
        nivel_acesso = st.selectbox(
            "Nível de Acesso",
            ["admin", "gerente", "engenheiro", "arquiteto", "usuario"]
        )
        
        if st.form_submit_button("Adicionar Usuário"):
            if not nome_usuario or not nome_completo:
                st.error("Por favor, preencha todos os campos.")
            elif nome_usuario in usuarios:
                st.error("Nome de usuário já existe.")
            else:
                # Criar novo usuário com senha padrão
                novo_usuario = {
                    "nome_completo": nome_completo,
                    "nivel_acesso": nivel_acesso,
                    "senha": hash_senha("mudar123"),  # Senha padrão
                    "ultima_troca_senha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ativo": True
                }
                usuarios[nome_usuario] = novo_usuario
                salvar_usuarios(usuarios)
                st.success(f"Usuário {nome_usuario} adicionado com sucesso!")
                st.info("A senha padrão é 'mudar123'. O usuário deve alterá-la no primeiro acesso.")
    
    # Lista de usuários existentes
    st.subheader("Usuários Cadastrados")
    
    # Campo de busca
    busca = st.text_input("Buscar usuário")
    
    # Filtrar usuários pela busca
    usuarios_filtrados = {
        user: data for user, data in usuarios.items()
        if busca.lower() in user.lower() or busca.lower() in data["nome_completo"].lower()
    }
    
    # Exibir usuários em formato de tabela
    if usuarios_filtrados:
        for usuario, dados in usuarios_filtrados.items():
            with st.expander(f"{usuario} - {dados['nome_completo']} ({dados['nivel_acesso']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nome Completo:** {dados['nome_completo']}")
                    st.write(f"**Nível de Acesso:** {dados['nivel_acesso']}")
                    st.write(f"**Status:** {'Ativo' if dados['ativo'] else 'Inativo'}")
                with col2:
                    if st.button("Resetar Senha", key=f"reset_{usuario}"):
                        if resetar_senha(usuario):
                            st.success(f"Senha do usuário {usuario} resetada para 'mudar123'")
                        else:
                            st.error("Erro ao resetar senha")
                    
                    if st.button("Desativar/Ativar", key=f"toggle_{usuario}"):
                        dados['ativo'] = not dados['ativo']
                        salvar_usuarios(usuarios)
                        st.success(f"Status do usuário {usuario} alterado para {'Ativo' if dados['ativo'] else 'Inativo'}")
    else:
        st.info("Nenhum usuário encontrado.")
