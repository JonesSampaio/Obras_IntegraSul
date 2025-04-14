O usuário está refinando detalhes sobre a estrutura de permissões. Vamos catalogar o que ele quer:

Níveis de acesso:
Gestão (admin): pode tudo
Gerente (sócios/arquiteto): podem quase tudo com algumas restrições
Encarregados (usuários operacionais): podem ver e criar relatórios
Permissões específicas para gerentes:
PODEM adicionar novos encarregados/usuários operacionais
NÃO PODEM excluir permanentemente usuários (precisam solicitar à gestão)
Podem gerenciar obras, funcionários e outras funcionalidades operacionais
Sistema de senhas:
Ao criar um novo usuário, uma senha padrão é definida
No primeiro login, o usuário é forçado a alterar a senha
Se alguém esquecer a senha, precisa solicitar ao gerente ou gestão para reset
Após reset, o processo se repete (senha padrão e obrigação de alterar no primeiro login)

O usuário pede que eu reformule tudo e prepare os arquivos prontos para implementação. Vou criar um plano estruturado para os arquivos necessários e a lógica de cada um.

Entendi perfeitamente todos os requisitos. Vou reformular a estrutura completa e preparar os arquivos prontos para implementação imediata. Aqui está como ficará o sistema:

Estrutura de Permissões Refinada
Gestão (Admin)
Acesso total ao sistema
Única que pode excluir usuários permanentemente
Pode fazer reset de senhas
Todas as outras permissões
Gerente (Sócios e Arquiteto)
Pode adicionar novos encarregados
Pode gerenciar obras/equipes/funcionários
Pode visualizar todos os relatórios
NÃO pode excluir permanentemente usuários
NÃO pode modificar permissões de outros gerentes

Encarregados (Operacional)
Apenas acesso a criar/visualizar relatórios das suas obras
Visualização limitada ao seu escopo

Sistema de Senhas
Senha padrão no cadastro inicial (ex: "mudar123")
Obrigatoriedade de troca no primeiro acesso
Sistema de recuperação via solicitação ao gerente/gestão
Arquivos Necessários

Vou preparar os seguintes arquivos prontos para implementação:

1. app.py - Arquivo Principal
Python
Copiar
import streamlit as st
import pandas as pd
import json
import hashlib
import os
from datetime import datetime
import base64
from io import BytesIO

# Funções de autenticação e gerenciamento de sessão
def carregar_usuarios():
    """Carrega os usuários do arquivo JSON"""
    if os.path.exists("dados/usuarios.json"):
        with open("dados/usuarios.json", "r") as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    """Salva os usuários no arquivo JSON"""
    os.makedirs("dados", exist_ok=True)
    with open("dados/usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=4)

def hash_senha(senha):
    """Cria um hash da senha para armazenamento seguro"""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha, hash_armazenado):
    """Verifica se a senha fornecida corresponde ao hash armazenado"""
    return hash_senha(senha) == hash_armazenado

def verificar_primeiro_acesso(usuario):
    """Verifica se é o primeiro acesso do usuário"""
    usuarios = carregar_usuarios()
    return usuarios[usuario].get("primeiro_acesso", False)

def atualizar_senha(usuario, nova_senha):
    """Atualiza a senha do usuário e marca que não é mais primeiro acesso"""
    usuarios = carregar_usuarios()
    usuarios[usuario]["senha"] = hash_senha(nova_senha)
    usuarios[usuario]["primeiro_acesso"] = False
    salvar_usuarios(usuarios)

# Inicialização de dados
if not os.path.exists("dados/usuarios.json"):
    # Cria usuário Gestão padrão
    usuarios_iniciais = {
        "gestao": {
            "senha": hash_senha("gestao123"),
            "nivel": "admin",
            "nome_completo": "Administrador do Sistema",
            "primeiro_acesso": True
        }
    }
    salvar_usuarios(usuarios_iniciais)

# Inicializar diretórios de dados
for diretorio in ["dados/obras", "dados/funcionarios", "dados/equipes", "dados/relatorios"]:
    os.makedirs(diretorio, exist_ok=True)

# Interface de login
def tela_login():
    st.title("Sistema de Gestão de Obras")
    st.subheader("Login")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        usuario = st.text_input("Usuário")
    with col2:
        senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar", type="primary", use_container_width=True):
        usuarios = carregar_usuarios()
        
        if usuario in usuarios and verificar_senha(senha, usuarios[usuario]["senha"]):
            # Autenticação bem-sucedida
            st.session_state.autenticado = True
            st.session_state.usuario_atual = usuario
            st.session_state.nivel_acesso = usuarios[usuario]["nivel"]
            st.session_state.nome_completo = usuarios[usuario]["nome_completo"]
            
            # Verificar se é primeiro acesso
            if verificar_primeiro_acesso(usuario):
                st.session_state.forcar_troca_senha = True
            
            # Carregar obras atribuídas para encarregados
            if usuarios[usuario]["nivel"] == "usuario":
                st.session_state.obras_atribuidas = usuarios[usuario].get("obras", [])
            
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")

# Tela para troca obrigatória de senha no primeiro acesso
def tela_troca_senha():
    st.title("Troca de Senha Obrigatória")
    st.warning("Por segurança, você precisa alterar sua senha no primeiro acesso.")
    
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")
    
    if st.button("Alterar Senha", type="primary"):
        if nova_senha == confirmar_senha and len(nova_senha) >= 6:
            atualizar_senha(st.session_state.usuario_atual, nova_senha)
            st.session_state.forcar_troca_senha = False
            st.success("Senha alterada com sucesso!")
            st.rerun()
        else:
            if nova_senha != confirmar_senha:
                st.error("As senhas não conferem!")
            else:
                st.error("A senha deve ter pelo menos 6 caracteres!")

# Função para criar o menu lateral baseado no nível de acesso
def menu_lateral():
    with st.sidebar:
        st.write(f"Bem-vindo, {st.session_state.nome_completo}")
        st.write(f"Nível: {st.session_state.nivel_acesso.capitalize()}")
        
        # Menu baseado no nível de acesso
        if st.session_state.nivel_acesso == "admin":
            opcao = st.selectbox("Menu", [
                "Dashboard", 
                "Gestão de Obras", 
                "Gestão de Funcionários", 
                "Gestão de Equipes",
                "Relatórios Diários",
                "Usuários e Permissões"
            ])
        elif st.session_state.nivel_acesso == "gerente":
            opcao = st.selectbox("Menu", [
                "Dashboard", 
                "Gestão de Obras", 
                "Gestão de Funcionários", 
                "Gestão de Equipes",
                "Relatórios Diários",
                "Encarregados" # Gerentes podem adicionar encarregados
            ])
        else:
            opcao = st.selectbox("Menu", [
                "Relatórios Diários",
                "Minhas Obras"
            ])
        
        if st.button("Sair"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        return opcao

# Funções para cada seção do sistema
def dashboard():
    st.title("Dashboard")
    st.subheader("Visão Geral das Obras")
    
    # Carregar dados das obras
    obras = []
    if os.path.exists("dados/obras"):
        for arquivo in os.listdir("dados/obras"):
            if arquivo.endswith(".json"):
                with open(f"dados/obras/{arquivo}", "r") as f:
                    obra = json.load(f)
                    obras.append(obra)
    
    # Exibir estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Obras", len(obras))
    with col2:
        obras_andamento = sum(1 for obra in obras if obra.get("status") == "Em andamento")
        st.metric("Obras em Andamento", obras_andamento)
    with col3:
        obras_concluidas = sum(1 for obra in obras if obra.get("status") == "Concluída")
        st.metric("Obras Concluídas", obras_concluidas)
    
    # Gráfico de progresso das obras
    st.subheader("Progresso das Obras")
    for obra in obras:
        st.write(f"{obra['nome']} - {obra.get('progresso', 0)}%")
        st.progress(float(obra.get('progresso', 0))/100)

def gestao_obras():
    st.title("Gestão de Obras")
    
    tab1, tab2 = st.tabs(["Lista de Obras", "Adicionar/Editar Obra"])
    
    with tab1:
        # Listar obras existentes
        st.subheader("Obras Cadastradas")
        obras = []
        if os.path.exists("dados/obras"):
            for arquivo in os.listdir("dados/obras"):
                if arquivo.endswith(".json"):
                    with open(f"dados/obras/{arquivo}", "r") as f:
                        obra = json.load(f)
                        obras.append(obra)
        
        if obras:
            df = pd.DataFrame(obras)
            st.dataframe(df[["nome", "endereco", "status", "responsavel_tecnico", "data_inicio", "data_prevista_fim"]])
            
            # Opção para editar ou excluir
            obra_selecionada = st.selectbox("Selecione uma obra para ações", 
                                           [obra["nome"] for obra in obras])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Editar Obra Selecionada"):
                    st.session_state.obra_para_editar = obra_selecionada
                    st.rerun()
            
            with col2:
                # Apenas admin pode excluir permanentemente
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir Obra Permanentemente"):
                        arquivo = f"dados/obras/{obra_selecionada.replace(' ', '_')}.json"
                        if os.path.exists(arquivo):
                            os.remove(arquivo)
                            st.success(f"Obra {obra_selecionada} excluída com sucesso!")
                            st.rerun()
        else:
            st.info("Nenhuma obra cadastrada.")
    
    with tab2:
        st.subheader("Cadastro de Obra")
        
        # Se estiver editando, carrega os dados da obra
        obra_para_editar = st.session_state.get("obra_para_editar", None)
        dados_obra = {}
        
        if obra_para_editar:
            arquivo = f"dados/obras/{obra_para_editar.replace(' ', '_')}.json"
            if os.path.exists(arquivo):
                with open(arquivo, "r") as f:
                    dados_obra = json.load(f)
                st.info(f"Editando obra: {obra_para_editar}")
        
        nome_obra = st.text_input("Nome da Obra", value=dados_obra.get("nome", ""))
        endereco = st.text_input("Endereço", value=dados_obra.get("endereco", ""))
        responsavel_tecnico = st.text_input("Responsável Técnico", value=dados_obra.get("responsavel_tecnico", ""))
        rrt = st.text_input("RRT", value=dados_obra.get("rrt", ""))
        data_inicio = st.date_input("Data de Início", value=datetime.strptime(dados_obra.get("data_inicio", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"))
        data_fim = st.date_input("Data Prevista para Conclusão", value=datetime.strptime(dados_obra.get("data_prevista_fim", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"))
        status = st.selectbox("Status", ["Em andamento", "Concluída", "Não iniciada"], index=["Em andamento", "Concluída", "Não iniciada"].index(dados_obra.get("status", "Em andamento")))
        progresso = st.slider("Progresso (%)", 0, 100, value=int(dados_obra.get("progresso", 0)))
        
        if st.button("Salvar Obra"):
            nova_obra = {
                "nome": nome_obra,
                "endereco": endereco,
                "responsavel_tecnico": responsavel_tecnico,
                "rrt": rrt,
                "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                "data_prevista_fim": data_fim.strftime("%Y-%m-%d"),
                "status": status,
                "progresso": progresso
            }
            
            arquivo = f"dados/obras/{nome_obra.replace(' ', '_')}.json"
            with open(arquivo, "w") as f:
                json.dump(nova_obra, f, indent=4)
            
            st.success(f"Obra {nome_obra} salva com sucesso!")
            
            # Limpar o estado de edição
            if "obra_para_editar" in st.session_state:
                del st.session_state.obra_para_editar
                
            st.rerun()

def gestao_funcionarios():
    st.title("Gestão de Funcionários")
    
    tab1, tab2 = st.tabs(["Lista de Funcionários", "Adicionar/Editar Funcionário"])
    
    with tab1:
        # Listar funcionários existentes
        st.subheader("Funcionários Cadastrados")
        funcionarios = []
        if os.path.exists("dados/funcionarios"):
            for arquivo in os.listdir("dados/funcionarios"):
                if arquivo.endswith(".json"):
                    with open(f"dados/funcionarios/{arquivo}", "r") as f:
                        funcionario = json.load(f)
                        funcionarios.append(funcionario)
        
        if funcionarios:
            df = pd.DataFrame(funcionarios)
            st.dataframe(df[["nome", "funcao", "telefone", "obra_atual"]])
            
            # Opção para editar ou excluir
            funcionario_selecionado = st.selectbox("Selecione um funcionário para ações", 
                                           [func["nome"] for func in funcionarios])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Editar Funcionário"):
                    st.session_state.funcionario_para_editar = funcionario_selecionado
                    st.rerun()
            
            with col2:
                # Apenas admin pode excluir permanentemente
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir Funcionário Permanentemente"):
                        arquivo = f"dados/funcionarios/{funcionario_selecionado.replace(' ', '_')}.json"
                        if os.path.exists(arquivo):
                            os.remove(arquivo)
                            st.success(f"Funcionário {funcionario_selecionado} excluído com sucesso!")
                            st.rerun()
        else:
            st.info("Nenhum funcionário cadastrado.")
    
    with tab2:
        st.subheader("Cadastro de Funcionário")
        
        # Se estiver editando, carrega os dados do funcionário
        funcionario_para_editar = st.session_state.get("funcionario_para_editar", None)
        dados_funcionario = {}
        
        if funcionario_para_editar:
            arquivo = f"dados/funcionarios/{funcionario_para_editar.replace(' ', '_')}.json"
            if os.path.exists(arquivo):
                with open(arquivo, "r") as f:
                    dados_funcionario = json.load(f)
                st.info(f"Editando funcionário: {funcionario_para_editar}")
        
        nome = st.text_input("Nome Completo", value=dados_funcionario.get("nome", ""))
        funcao = st.text_input("Função", value=dados_funcionario.get("funcao", ""))
        telefone = st.text_input("Telefone", value=dados_funcionario.get("telefone", ""))
        
        # Lista de obras para selecionar
        obras = []
        if os.path.exists("dados/obras"):
            for arquivo in os.listdir("dados/obras"):
                if arquivo.endswith(".json"):
                    with open(f"dados/obras/{arquivo}", "r") as f:
                        obra = json.load(f)
                        obras.append(obra["nome"])
        
        obra_atual = st.selectbox("Obra Atual", ["Sem obra atribuída"] + obras, 
                                 index=(obras.index(dados_funcionario.get("obra_atual")) + 1 if dados_funcionario.get("obra_atual") in obras else 0))
        
        if obra_atual == "Sem obra atribuída":
            obra_atual = ""
        
        if st.button("Salvar Funcionário"):
            novo_funcionario = {
                "nome": nome,
                "funcao": funcao,
                "telefone": telefone,
                "obra_atual": obra_atual
            }
            
            arquivo = f"dados/funcionarios/{nome.replace(' ', '_')}.json"
            with open(arquivo, "w") as f:
                json.dump(novo_funcionario, f, indent=4)
            
            st.success(f"Funcionário {nome} salvo com sucesso!")
            
            # Limpar o estado de edição
            if "funcionario_para_editar" in st.session_state:
                del st.session_state.funcionario_para_editar
                
            st.rerun()

def gestao_equipes():
    st.title("Gestão de Equipes")
    
    tab1, tab2 = st.tabs(["Lista de Equipes", "Adicionar/Editar Equipe"])
    
    with tab1:
        # Listar equipes existentes
        st.subheader("Equipes Cadastradas")
        equipes = []
        if os.path.exists("dados/equipes"):
            for arquivo in os.listdir("dados/equipes"):
                if arquivo.endswith(".json"):
                    with open(f"dados/equipes/{arquivo}", "r") as f:
                        equipe = json.load(f)
                        equipes.append(equipe)
        
        if equipes:
            for equipe in equipes:
                st.subheader(f"Equipe: {equipe['nome']}")
                st.write(f"Obra: {equipe['obra']}")
                st.write(f"Líder: {equipe['lider']}")
                st.write("Membros:")
                for membro in equipe['membros']:
                    st.write(f"- {membro}")
                st.write("---")
            
            # Opção para editar ou excluir
            equipe_selecionada = st.selectbox("Selecione uma equipe para ações", 
                                           [equipe["nome"] for equipe in equipes])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Editar Equipe"):
                    st.session_state.equipe_para_editar = equipe_selecionada
                    st.rerun()
            
            with col2:
                # Apenas admin pode excluir permanentemente
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir Equipe Permanentemente"):
                        arquivo = f"dados/equipes/{equipe_selecionada.replace(' ', '_')}.json"
                        if os.path.exists(arquivo):
                            os.remove(arquivo)
                            st.success(f"Equipe {equipe_selecionada} excluída com sucesso!")
                            st.rerun()
        else:
            st.info("Nenhuma equipe cadastrada.")
    
    with tab2:
        st.subheader("Cadastro de Equipe")
        
        # Se estiver editando, carrega os dados da equipe
        equipe_para_editar = st.session_state.get("equipe_para_editar", None)
        dados_equipe = {"membros": []}
        
        if equipe_para_editar:
            arquivo = f"dados/equipes/{equipe_para_editar.replace(' ', '_')}.json"
            if os.path.exists(arquivo):
                with open(arquivo, "r") as f:
                    dados_equipe = json.load(f)
                st.info(f"Editando equipe: {equipe_para_editar}")
        
        nome_equipe = st.text_input("Nome da Equipe", value=dados_equipe.get("nome", ""))
        
        # Lista de obras para selecionar
        obras = []
        if os.path.exists("dados/obras"):
            for arquivo in os.listdir("dados/obras"):
                if arquivo.endswith(".json"):
                    with open(f"dados/obras/{arquivo}", "r") as f:
                        obra = json.load(f)
                        obras.append(obra["nome"])
        
        obra = st.selectbox("Obra", obras, 
                          index=obras.index(dados_equipe.get("obra")) if dados_equipe.get("obra") in obras else 0)
        
        # Lista de funcionários para selecionar como líder e membros
        funcionarios = []
        if os.path.exists("dados/funcionarios"):
            for arquivo in os.listdir("dados/funcionarios"):
                if arquivo.endswith(".json"):
                    with open(f"dados/funcionarios/{arquivo}", "r") as f:
                        funcionario = json.load(f)
                        funcionarios.append(funcionario["nome"])
        
        lider = st.selectbox("Líder da Equipe", funcionarios, 
                           index=funcionarios.index(dados_equipe.get("lider")) if dados_equipe.get("lider") in funcionarios else 0)
        
        # Multiselect para membros da equipe
        membros = st.multiselect("Membros da Equipe", funcionarios, default=dados_equipe.get("membros", []))
        
        if st.button("Salvar Equipe"):
            nova_equipe = {
                "nome": nome_equipe,
                "obra": obra,
                "lider": lider,
                "membros": membros
            }
            
            arquivo = f"dados/equipes/{nome_equipe.replace(' ', '_')}.json"
            with open(arquivo, "w") as f:
                json.dump(nova_equipe, f, indent=4)
            
            st.success(f"Equipe {nome_equipe} salva com sucesso!")
            
            # Limpar o estado de edição
            if "equipe_para_editar" in st.session_state:
                del st.session_state.equipe_para_editar
                
            st.rerun()

def relatorios():
    st.title("Relatórios Diários de Obra (RDO)")
    
    tab1, tab2 = st.tabs(["Criar Relatório", "Visualizar Relatórios"])
    
    with tab1:
        st.subheader("Novo Relatório Diário")
        
        # Determinar quais obras o usuário pode ver
        if st.session_state.nivel_acesso in ["admin", "gerente"]:
            # Admins e gerentes veem todas as obras
            obras = []
            if os.path.exists("dados/obras"):
                for arquivo in os.listdir("dados/obras"):
                    if arquivo.endswith(".json"):
                        with open(f"dados/obras/{arquivo}", "r") as f:
                            obra = json.load(f)
                            obras.append(obra["nome"])
        else:
            # Usuários operacionais veem apenas suas obras atribuídas
            obras = st.session_state.obras_atribuidas
        
        if not obras:
            st.warning("Nenhuma obra disponível para criar relatórios.")
            return
        
        obra_selecionada = st.selectbox("Selecione a Obra", obras)
        data_relatorio = st.date_input("Data do Relatório", datetime.now())
        
        # Carregar detalhes da obra selecionada
        arquivo_obra = f"dados/obras/{obra_selecionada.replace(' ', '_')}.json"
        if os.path.exists(arquivo_obra):
            with open(arquivo_obra, "r") as f:
                dados_obra = json.load(f)
                
            st.write(f"**Endereço:** {dados_obra['endereco']}")
            st.write(f"**Responsável Técnico:** {dados_obra['responsavel_tecnico']}")
            st.write(f"**RRT:** {dados_obra['rrt']}")
            
            # Buscar a equipe associada a esta obra
            equipe_obra = None
            if os.path.exists("dados/equipes"):
                for arquivo in os.listdir("dados/equipes"):
                    if arquivo.endswith(".json"):
                        with open(f"dados/equipes/{arquivo}", "r") as f:
                            equipe = json.load(f)
                            if equipe['obra'] == obra_selecionada:
                                equipe_obra = equipe
                                break
            
            if equipe_obra:
                st.write(f"**Equipe:** {equipe_obra['nome']}")
                st.write(f"**Líder:** {equipe_obra['lider']}")
                st.write("**Membros da Equipe:**")
                for membro in equipe_obra['membros']:
                    st.write(f"- {membro}")
        
        # Formulário do relatório
        atividades_realizadas = st.text_area("Atividades Realizadas", height=150)
        problemas_encontrados = st.text_area("Problemas Encontrados", height=100)
        solucoes_adotadas = st.text_area("Soluções Adotadas", height=100)
        
        observacoes = st.text_area("Observações Gerais", height=100)
        
        # Upload de fotos
        st.write("**Fotos do Dia**")
        fotos = st.file_uploader("Adicionar Fotos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        fotos_codificadas = []
        for foto in fotos:
            bytes_data = foto.read()
            b64_str = base64.b64encode(bytes_data).decode()
            fotos_codificadas.append({
                "nome": foto.name,
                "dados": b64_str,
                "tipo": foto.type
            })
        
        # Atualizar progresso da obra
        novo_progresso = st.slider("Progresso Atual da Obra (%)", 0, 100, int(dados_obra.get("progresso", 0)))
        
        if st.button("Salvar Relatório"):
            novo_relatorio = {
                "obra": obra_selecionada,
                "data": data_relatorio.strftime("%Y-%m-%d"),
                "atividades": atividades_realizadas,
                "problemas": problemas_encontrados,
                "solucoes": solucoes_adotadas,
                "observacoes": observacoes,
                "fotos": fotos_codificadas,
                "criado_por": st.session_state.nome_completo,
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Salvar relatório
            os.makedirs("dados/relatorios", exist_ok=True)
            nome_arquivo = f"{obra_selecionada.replace(' ', '_')}_{data_relatorio.strftime('%Y-%m-%d')}.json"
            with open(f"dados/relatorios/{nome_arquivo}", "w") as f:
                json.dump(novo_relatorio, f, indent=4)
            
            # Atualizar progresso da obra
            dados_obra["progresso"] = novo_progresso
            with open(arquivo_obra, "w") as f:
                json.dump(dados_obra, f, indent=4)
            
            st.success("Relatório salvo com sucesso!")
            st.rerun()
    
    with tab2:
        st.subheader("Relatórios Existentes")
        
        # Determinar quais obras o usuário pode ver
        if st.session_state.nivel_acesso in ["admin", "gerente"]:
            # Admins e gerentes veem todas as obras
            obras = []
            if os.path.exists("dados/obras"):
                for arquivo in os.listdir("dados/obras"):
                    if arquivo.endswith(".json"):
                        with open(f"dados/obras/{arquivo}", "r") as f:
                            obra = json.load(f)
                            obras.append(obra["nome"])
        else:
            # Usuários operacionais veem apenas suas obras atribuídas
            obras = st.session_state.obras_atribuidas
        
        obra_filtro = st.selectbox("Filtrar por Obra", ["Todas"] + obras)
        
        # Carregar relatórios
        relatorios = []
        if os.path.exists("dados/relatorios"):
            for arquivo in os.listdir("dados/relatorios"):
                if arquivo.endswith(".json"):
                    with open(f"dados/relatorios/{arquivo}", "r") as f:
                        relatorio = json
