import streamlit as st
import json
import pandas as pd
from datetime import datetime
import auth
import utils
import os

def carregar_dados(arquivo):
    caminho = f'dados/{arquivo}.json'
    if os.path.exists(caminho):
        with open(caminho, 'r') as f:
            return json.load(f)
    return {}

def salvar_dados(arquivo, dados):
    with open(f'dados/{arquivo}.json', 'w') as f:
        json.dump(dados, f, indent=4)

def painel_de_gestao():
    st.title("Painel de Gestão")
    
    tabs = ["Obras", "Funcionários", "Equipes", "Relatórios"]
    
    # Adicionar aba de usuários apenas para administrador
    if st.session_state.nivel_acesso == "admin":
        tabs.append("Usuários")
    
    selected_tab = st.tabs(tabs)
    
    with selected_tab[0]:
        gerenciar_obras()
        
    with selected_tab[1]:
        gerenciar_funcionarios()
        
    with selected_tab[2]:
        gerenciar_equipes()
        
    with selected_tab[3]:
        visualizar_todos_relatorios()
    
    # Aba de usuários apenas para administrador
    if st.session_state.nivel_acesso == "admin" and len(selected_tab) > 4:
        with selected_tab[4]:
            gerenciar_usuarios()

def gerenciar_obras():
    st.header("Gerenciar Obras")
    
    obras = carregar_dados("obras")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Adicionar Nova Obra")
        nome_obra = st.text_input("Nome da Obra")
        endereco = st.text_input("Endereço")
        prazo_inicio = st.date_input("Data de Início")
        prazo_fim = st.date_input("Prazo de Conclusão")
        numero_rrt = st.text_input("Número RRT")
        responsavel_tecnico = st.text_input("Responsável Técnico Principal")
        
        if st.button("Adicionar Obra"):
            if nome_obra and endereco:
                obras[nome_obra] = {
                    "endereco": endereco,
                    "prazo_inicio": prazo_inicio.strftime("%Y-%m-%d"),
                    "prazo_fim": prazo_fim.strftime("%Y-%m-%d"),
                    "numero_rrt": numero_rrt,
                    "responsavel_tecnico": responsavel_tecnico,
                    "equipes": []
                }
                salvar_dados("obras", obras)
                st.success(f"Obra '{nome_obra}' adicionada com sucesso!")
            else:
                st.error("Por favor, preencha pelo menos o nome e endereço da obra.")
    
    with col2:
        st.subheader("Obras Cadastradas")
        if obras:
            obra_selecionada = st.selectbox("Selecione uma obra", list(obras.keys()))
            
            if obra_selecionada:
                obra = obras[obra_selecionada]
                st.write(f"**Endereço:** {obra['endereco']}")
                st.write(f"**Período:** {obra['prazo_inicio']} a {obra['prazo_fim']}")
                st.write(f"**RRT:** {obra['numero_rrt']}")
                st.write(f"**Responsável Técnico:** {obra['responsavel_tecnico']}")
                
                if st.button("Editar esta Obra"):
                    st.session_state.obra_para_editar = obra_selecionada
                    st.session_state.aba_atual = "editar_obra"
                
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir esta Obra", key="excluir_obra"):
                        del obras[obra_selecionada]
                        salvar_dados("obras", obras)
                        st.success(f"Obra '{obra_selecionada}' excluída com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhuma obra cadastrada.")

def gerenciar_funcionarios():
    st.header("Gerenciar Funcionários")
    
    funcionarios = carregar_dados("funcionarios")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Adicionar Novo Funcionário")
        nome = st.text_input("Nome Completo")
        cargo = st.text_input("Cargo")
        contato = st.text_input("Telefone de Contato")
        
        if st.button("Adicionar Funcionário"):
            if nome and cargo:
                # Gerar ID único para o funcionário
                funcionario_id = utils.gerar_id()
                funcionarios[funcionario_id] = {
                    "nome": nome,
                    "cargo": cargo,
                    "contato": contato,
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d")
                }
                salvar_dados("funcionarios", funcionarios)
                st.success(f"Funcionário '{nome}' adicionado com sucesso!")
            else:
                st.error("Por favor, preencha pelo menos o nome e cargo do funcionário.")
    
    with col2:
        st.subheader("Funcionários Cadastrados")
        if funcionarios:
            # Criar DataFrame para melhor visualização
            df = pd.DataFrame([
                {
                    "ID": id,
                    "Nome": dados["nome"],
                    "Cargo": dados["cargo"],
                    "Contato": dados.get("contato", "")
                }
                for id, dados in funcionarios.items()
            ])
            
            st.dataframe(df)
            
            # Opção para editar ou excluir
            funcionario_id = st.selectbox("Selecione um funcionário para ações", list(funcionarios.keys()), 
                                        format_func=lambda x: funcionarios[x]["nome"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Editar Funcionário"):
                    st.session_state.funcionario_para_editar = funcionario_id
                    st.session_state.aba_atual = "editar_funcionario"
            
            with col2:
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir Funcionário"):
                        del funcionarios[funcionario_id]
                        salvar_dados("funcionarios", funcionarios)
                        st.success(f"Funcionário '{funcionarios[funcionario_id]['nome']}' excluído com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum funcionário cadastrado.")

def gerenciar_equipes():
    st.header("Gerenciar Equipes")
    
    equipes = carregar_dados("equipes")
    obras = carregar_dados("obras")
    funcionarios = carregar_dados("funcionarios")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Criar Nova Equipe")
        nome_equipe = st.text_input("Nome da Equipe")
        obra_selecionada = st.selectbox("Obra", list(obras.keys()) if obras else ["Nenhuma obra cadastrada"])
        
        # Multiselect para funcionários
        funcionarios_disponiveis = [f"{id} - {dados['nome']}" for id, dados in funcionarios.items()]
        funcionarios_selecionados = st.multiselect("Selecione os Funcionários", funcionarios_disponiveis)
        
        if st.button("Criar Equipe"):
            if nome_equipe and obra_selecionada != "Nenhuma obra cadastrada" and funcionarios_selecionados:
                # Extrair IDs dos funcionários selecionados
                ids_funcionarios = [f.split(" - ")[0] for f in funcionarios_selecionados]
                
                # Gerar ID único para a equipe
                equipe_id = utils.gerar_id()
                equipes[equipe_id] = {
                    "nome": nome_equipe,
                    "obra": obra_selecionada,
                    "funcionarios": ids_funcionarios,
                    "data_criacao": datetime.now().strftime("%Y-%m-%d")
                }
                
                # Associar equipe à obra
                if obra_selecionada in obras:
                    if "equipes" not in obras[obra_selecionada]:
                        obras[obra_selecionada]["equipes"] = []
                    obras[obra_selecionada]["equipes"].append(equipe_id)
                
                salvar_dados("equipes", equipes)
                salvar_dados("obras", obras)
                st.success(f"Equipe '{nome_equipe}' criada com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos e selecione pelo menos um funcionário.")
    
    with col2:
        st.subheader("Equipes Existentes")
        if equipes:
            equipe_selecionada = st.selectbox("Selecione uma equipe", 
                                            list(equipes.keys()),
                                            format_func=lambda x: equipes[x]["nome"])
            
            if equipe_selecionada:
                equipe = equipes[equipe_selecionada]
                st.write(f"**Nome da Equipe:** {equipe['nome']}")
                st.write(f"**Obra:** {equipe['obra']}")
                
                # Listar funcionários da equipe
                st.write("**Funcionários:**")
                for funcionario_id in equipe['funcionarios']:
                    if funcionario_id in funcionarios:
                        st.write(f"- {funcionarios[funcionario_id]['nome']} ({funcionarios[funcionario_id]['cargo']})")
                
                if st.button("Editar esta Equipe"):
                    st.session_state.equipe_para_editar = equipe_selecionada
                    st.session_state.aba_atual = "editar_equipe"
                
                if st.session_state.nivel_acesso == "admin":
                    if st.button("Excluir esta Equipe"):
                        # Remover associação da obra
                        if equipe['obra'] in obras and "equipes" in obras[equipe['obra']]:
                            if equipe_selecionada in obras[equipe['obra']]["equipes"]:
                                obras[equipe['obra']]["equipes"].remove(equipe_selecionada)
                        
                        # Excluir equipe
                        del equipes[equipe_selecionada]
                        
                        salvar_dados("equipes", equipes)
                        salvar_dados("obras", obras)
                        st.success(f"Equipe '{equipe['nome']}' excluída com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhuma equipe cadastrada.")

def visualizar_todos_relatorios():
    st.header("Visualização de Relatórios")
    
    # Listar todos os relatórios disponíveis
    relatorios_dir = "relatorios"
    if not os.path.exists(relatorios_dir):
        st.info("Nenhum relatório encontrado.")
        return
    
    relatorios = [f for f in os.listdir(relatorios_dir) if f.endswith(".json")]
    
    if not relatorios:
        st.info("Nenhum relatório encontrado.")
        return
    
    # Opções de filtro
    col1, col2 = st.columns(2)
    
    with col1:
        # Extrair nomes de obras dos relatórios
        obras = set()
        for relatorio in relatorios:
            try:
                with open(os.path.join(relatorios_dir, relatorio), 'r') as f:
                    dados = json.load(f)
                    if "obra" in dados:
                        obras.add(dados["obra"])
            except:
                pass
        
        obra_filtro = st.selectbox("Filtrar por Obra", ["Todas"] + list(obras))
    
    with col2:
        data_inicio = st.date_input("Data Inicial")
        data_fim = st.date_input("Data Final")
    
    # Filtrar relatórios
    relatorios_filtrados = []
    for relatorio in relatorios:
        try:
            with open(os.path.join(relatorios_dir, relatorio), 'r') as f:
                dados = json.load(f)
                
                # Verificar filtro de obra
                if obra_filtro != "Todas" and dados.get("obra") != obra_filtro:
                    continue
                
                # Verificar filtro de data
                data_relatorio = datetime.strptime(dados.get("data", "2000-01-01"), "%Y-%m-%d").date()
                if data_relatorio < data_inicio or data_relatorio > data_fim:
                    continue
                
                # Adicionar à lista filtrada
                relatorios_filtrados.append({
                    "arquivo": relatorio,
                    "obra": dados.get("obra", "N/A"),
                    "data": dados.get("data", "N/A"),
                    "responsavel": dados.get("responsavel", "N/A")
                })
        except:
            pass
    
    # Exibir relatórios filtrados
    if relatorios_filtrados:
        df = pd.DataFrame(relatorios_filtrados)
        st.dataframe(df)
        
        # Visualizar relatório selecionado
        relatorio_selecionado = st.selectbox("Selecione um relatório para visualizar", 
                                          [r["arquivo"] for r in relatorios_filtrados])
        
        if relatorio_selecionado:
            with open(os.path.join(relatorios_dir, relatorio_selecionado), 'r') as f:
                dados_relatorio = json.load(f)
                
                st.subheader(f"Relatório: {relatorio_selecionado}")
                
                # Exibir dados do relatório de forma organizada
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Obra:** {dados_relatorio.get('obra', 'N/A')}")
                    st.write(f"**Data:** {dados_relatorio.get('data', 'N/A')}")
                with col2:
                    st.write(f"**Responsável:** {dados_relatorio.get('responsavel', 'N/A')}")
                    st.write(f"**Equipe:** {dados_relatorio.get('equipe', 'N/A')}")
                
                # Exibir outros dados do relatório
                for chave, valor in dados_relatorio.items():
                    if chave not in ["obra", "data", "responsavel", "equipe"]:
                        if isinstance(valor, list):
                            st.subheader(f"{chave.capitalize()}")
                            for item in valor:
                                st.write(f"- {item}")
                        else:
                            st.subheader(f"{chave.capitalize()}")
                            st.write(valor)
    else:
        st.info("Nenhum relatório encontrado para os filtros selecionados.")

def gerenciar_usuarios():
    st.header("Gerenciar Usuários")
    
    # Verificar se o usuário atual tem permissão para esta função
    if st.session_state.nivel_acesso != "admin" and st.session_state.nivel_acesso != "gerente":
        st.error("Você não tem permissão para acessar esta área.")
        return
    
    usuarios = auth.carregar_usuarios()
    obras = carregar_dados("obras")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Adicionar Novo Usuário")
        
        # Campos para novo usuário
        novo_usuario = st.text_input("Nome de Usuário")
        nome_completo = st.text_input("Nome Completo")
        
        # Determinar níveis que podem ser criados
        niveis_disponiveis = []
        if st.session_state.nivel_acesso == "admin":
            niveis_disponiveis = ["admin", "gerente", "encarregado"]
        elif st.session_state.nivel_acesso == "gerente":
            niveis_disponiveis = ["encarregado"]
            
        nivel = st.selectbox("Nível de Acesso", niveis_disponiveis)
        
        # Para encarregados, selecionar obras associadas
        obras_selecionadas = []
        if nivel == "encarregado":
            obras_disponiveis = list(obras.keys())
            obras_selecionadas = st.multiselect("Associar a Obras", obras_disponiveis)
        
        if st.button("Adicionar Usuário"):
            if novo_usuario and nome_completo and nivel:
                # Verificar se usuário já existe
                if novo_usuario in usuarios:
                    st.error(f"Usuário '{novo_usuario}' já existe.")
                else:
                    # Criar novo usuário com senha padrão
                    senha_padrao = "senha123"
                    
                    usuarios[novo_usuario] = {
                        "senha": utils.hash_senha(senha_padrao),
                        "nivel": nivel,
                        "nome_completo": nome_completo,
                        "primeiro_acesso": True,
                        "data_criacao": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    # Adicionar obras associadas para encarregados
                    if nivel == "encarregado" and obras_selecionadas:
                        usuarios[novo_usuario]["obras"] = obras_selecionadas
                    
                    auth.salvar_usuarios(usuarios)
                    st.success(f"Usuário '{novo_usuario}' adicionado com sucesso! Senha padrão: {senha_padrao}")
            else:
                st.error("Por favor, preencha todos os campos.")
    
    with col2:
        st.subheader("Usuários do Sistema")
        
        # Filtrar usuários baseado no nível de acesso do usuário atual
        usuarios_filtrados = {}
        for usuario, dados in usuarios.items():
            # Admin vê todos
            if st.session_state.nivel_acesso == "admin":
                usuarios_filtrados[usuario] = dados
            # Gerente vê apenas encarregados
            elif st.session_state.nivel_acesso == "gerente" and dados["nivel"] == "encarregado":
                usuarios_filtrados[usuario] = dados
        
        # Criar DataFrame para melhor visualização
        if usuarios_filtrados:
            df = pd.DataFrame([
                {
                    "Usuário": usuario,
                    "Nome Completo": dados["nome_completo"],
                    "Nível": dados["nivel"].capitalize(),
                    "Primeiro Acesso": "Sim" if dados.get("primeiro_acesso", True) else "Não"
                }
                for usuario, dados in usuarios_filtrados.items()
            ])
            
            st.dataframe(df)
            
            # Ações para usuários
            usuario_selecionado = st.selectbox("Selecione um usuário", list(usuarios_filtrados.keys()))
