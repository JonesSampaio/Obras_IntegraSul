import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import uuid

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

# Função para adicionar atividades com anexos individuais
def adicionar_atividades():
    st.subheader("Atividades Realizadas")
    
    # Inicializar lista de atividades na session state
    if 'atividades_lista' not in st.session_state:
        st.session_state.atividades_lista = [{"descricao": "", "anexo": None}]
    
    atividades = []
    
    # Criar campos para cada atividade
    for i, atividade in enumerate(st.session_state.atividades_lista):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            descricao = st.text_area(f"Atividade {i+1}", 
                                    value=atividade["descricao"],
                                    key=f"atividade_desc_{i}")
        
        with col2:
            anexo = st.file_uploader(f"Anexo da atividade {i+1}", 
                                    type=["png", "jpg", "jpeg", "pdf", "doc", "docx"], 
                                    key=f"atividade_anexo_{i}")
        
        # Atualizar os dados da atividade
        st.session_state.atividades_lista[i]["descricao"] = descricao
        
        # Processar o anexo (em uma implementação completa, salvaríamos o arquivo)
        if anexo:
            # Apenas salvamos o nome por enquanto, mas poderia salvar o arquivo
            st.session_state.atividades_lista[i]["anexo"] = anexo.name
        
        if descricao:  # Só incluir atividades com descrição
            atividades.append({
                "descricao": descricao,
                "anexo": st.session_state.atividades_lista[i]["anexo"]
            })
    
    # Botão para adicionar mais uma atividade
    if st.button("+ Adicionar outra atividade"):
        st.session_state.atividades_lista.append({"descricao": "", "anexo": None})
        st.experimental_rerun()
    
    return atividades

# Função para adicionar ocorrências com anexos individuais
def adicionar_ocorrencias():
    st.subheader("Ocorrências e Observações")
    
    # Inicializar lista de ocorrências na session state
    if 'ocorrencias_lista' not in st.session_state:
        st.session_state.ocorrencias_lista = [{"descricao": "", "anexo": None}]
    
    ocorrencias = []
    
    # Criar campos para cada ocorrência
    for i, ocorrencia in enumerate(st.session_state.ocorrencias_lista):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            descricao = st.text_area(f"Ocorrência {i+1}", 
                                    value=ocorrencia["descricao"],
                                    key=f"ocorrencia_desc_{i}")
        
        with col2:
            anexo = st.file_uploader(f"Anexo da ocorrência {i+1}", 
                                    type=["png", "jpg", "jpeg", "pdf", "doc", "docx"], 
                                    key=f"ocorrencia_anexo_{i}")
        
        # Atualizar os dados da ocorrência
        st.session_state.ocorrencias_lista[i]["descricao"] = descricao
        
        # Processar o anexo
        if anexo:
            st.session_state.ocorrencias_lista[i]["anexo"] = anexo.name
        
        if descricao:  # Só incluir ocorrências com descrição
            ocorrencias.append({
                "descricao": descricao,
                "anexo": st.session_state.ocorrencias_lista[i]["anexo"]
            })
    
    # Botão para adicionar mais uma ocorrência
    if st.button("+ Adicionar outra ocorrência"):
        st.session_state.ocorrencias_lista.append({"descricao": "", "anexo": None})
        st.experimental_rerun()
    
    return ocorrencias

# Função para registrar recebimento de material
def registrar_recebimento_material():
    st.subheader("Recebimento de Material")
    
    # Perguntar se houve recebimento de material
    recebeu_material = st.radio("Existiu algum recebimento de material na obra?", 
                              ["Não", "Sim"], key="recebeu_material_radio")
    
    materiais_recebidos = []
    
    if recebeu_material == "Sim":
        # Inicializar lista de materiais recebidos na session state
        if 'materiais_recebidos_lista' not in st.session_state:
            st.session_state.materiais_recebidos_lista = [{"nome": "", "quantidade": ""}]
        
        # Criar campos para cada material recebido
        for i, material in enumerate(st.session_state.materiais_recebidos_lista):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input(f"Material recebido {i+1}", 
                                    value=material["nome"],
                                    key=f"material_recebido_nome_{i}")
            
            with col2:
                quantidade = st.text_input(f"Quantidade {i+1}", 
                                         value=material["quantidade"],
                                         key=f"material_recebido_qtd_{i}")
            
            # Atualizar os dados do material
            st.session_state.materiais_recebidos_lista[i]["nome"] = nome
            st.session_state.materiais_recebidos_lista[i]["quantidade"] = quantidade
            
            if nome:  # Só incluir materiais com nome
                materiais_recebidos.append({
                    "nome": nome,
                    "quantidade": quantidade
                })
        
        # Botão para adicionar mais um material
        if st.button("+ Adicionar outro material recebido"):
            st.session_state.materiais_recebidos_lista.append({"nome": "", "quantidade": ""})
            st.experimental_rerun()
    
    return {
        "recebeu_material": recebeu_material,
        "materiais": materiais_recebidos
    }

# Função para registrar necessidade de material
def registrar_necessidade_material():
    st.subheader("Necessidade de Material")
    
    # Perguntar se há necessidade de material
    necessita_material = st.radio("Existe a necessidade de algum outro material para a obra?", 
                                ["Não", "Sim"], key="necessita_material_radio")
    
    materiais_necessarios = []
    
    if necessita_material == "Sim":
        # Inicializar lista de materiais necessários na session state
        if 'materiais_necessarios_lista' not in st.session_state:
            st.session_state.materiais_necessarios_lista = [{"nome": "", "quantidade": ""}]
        
        # Criar campos para cada material necessário
        for i, material in enumerate(st.session_state.materiais_necessarios_lista):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input(f"Material necessário {i+1}", 
                                    value=material["nome"],
                                    key=f"material_necessario_nome_{i}")
            
            with col2:
                quantidade = st.text_input(f"Quantidade necessária {i+1}", 
                                         value=material["quantidade"],
                                         key=f"material_necessario_qtd_{i}")
            
            # Atualizar os dados do material
            st.session_state.materiais_necessarios_lista[i]["nome"] = nome
            st.session_state.materiais_necessarios_lista[i]["quantidade"] = quantidade
            
            if nome:  # Só incluir materiais com nome
                materiais_necessarios.append({
                    "nome": nome,
                    "quantidade": quantidade
                })
        
        # Botão para adicionar mais um material
        if st.button("+ Adicionar outra necessidade de material"):
            st.session_state.materiais_necessarios_lista.append({"nome": "", "quantidade": ""})
            st.experimental_rerun()
    
    return {
        "necessita_material": necessita_material,
        "materiais": materiais_necessarios
    }

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
            
            # Atividades realizadas (nova implementação com anexos por atividade)
            st.write("### Atividades Realizadas")
            # Inicializar atividades na session state para o formulário
            if 'form_atividades' not in st.session_state:
                st.session_state.form_atividades = [{"descricao": "", "anexo": None}]
            
            atividades = []
            for i in range(len(st.session_state.form_atividades)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    descricao = st.text_area(f"Atividade {i+1}", key=f"form_atividade_desc_{i}")
                with col2:
                    anexo = st.file_uploader(f"Anexo", 
                                           type=["png", "jpg", "jpeg", "pdf", "doc", "docx"], 
                                           key=f"form_atividade_anexo_{i}")
                
                if descricao:
                    atividade_item = {"descricao": descricao, "anexo": None}
                    if anexo:
                        atividade_item["anexo"] = anexo.name
                    atividades.append(atividade_item)
            
            # Botão para adicionar mais uma atividade (dentro do formulário)
            add_atividade = st.checkbox("Adicionar outra atividade", key="add_atividade")
            if add_atividade and len(st.session_state.form_atividades) == len(atividades):
                st.session_state.form_atividades.append({"descricao": "", "anexo": None})
            
            # Ocorrências e observações (nova implementação com anexos por ocorrência)
            st.write("### Ocorrências e Observações")
            # Inicializar ocorrências na session state para o formulário
            if 'form_ocorrencias' not in st.session_state:
                st.session_state.form_ocorrencias = [{"descricao": "", "anexo": None}]
            
            ocorrencias = []
            for i in range(len(st.session_state.form_ocorrencias)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    descricao = st.text_area(f"Ocorrência {i+1}", key=f"form_ocorrencia_desc_{i}")
                with col2:
                    anexo = st.file_uploader(f"Anexo", 
                                           type=["png", "jpg", "jpeg", "pdf", "doc", "docx"], 
                                           key=f"form_ocorrencia_anexo_{i}")
                
                if descricao:
                    ocorrencia_item = {"descricao": descricao, "anexo": None}
                    if anexo:
                        ocorrencia_item["anexo"] = anexo.name
                    ocorrencias.append(ocorrencia_item)
            
            # Botão para adicionar mais uma ocorrência (dentro do formulário)
            add_ocorrencia = st.checkbox("Adicionar outra ocorrência", key="add_ocorrencia")
            if add_ocorrencia and len(st.session_state.form_ocorrencias) == len(ocorrencias):
                st.session_state.form_ocorrencias.append({"descricao": "", "anexo": None})
            
            # Recebimento de material (novo)
            st.write("### Recebimento de Material")
            recebeu_material = st.radio("Existiu algum recebimento de material na obra?", 
                                      ["Não", "Sim"], key="form_recebeu_material")
            
            materiais_recebidos = []
            if recebeu_material == "Sim":
                # Inicializar materiais recebidos na session state para o formulário
                if 'form_materiais_recebidos' not in st.session_state:
                    st.session_state.form_materiais_recebidos = [{"nome": "", "quantidade": ""}]
                
                for i in range(len(st.session_state.form_materiais_recebidos)):
                    col1, col2 = st.columns(2)
                    with col1:
                        nome = st.text_input(f"Material recebido {i+1}", key=f"form_material_recebido_nome_{i}")
                    with col2:
                        quantidade = st.text_input(f"Quantidade {i+1}", key=f"form_material_recebido_qtd_{i}")
                    
                    if nome:
                        materiais_recebidos.append({"nome": nome, "quantidade": quantidade})
                
                # Botão para adicionar mais um material recebido
                add_material_recebido = st.checkbox("Adicionar outro material recebido", key="add_material_recebido")
                if add_material_recebido and len(st.session_state.form_materiais_recebidos) == len(materiais_recebidos):
                    st.session_state.form_materiais_recebidos.append({"nome": "", "quantidade": ""})
            
            # Necessidade de material (novo)
            st.write("### Necessidade de Material")
            necessita_material = st.radio("Existe a necessidade de algum outro material para a obra?", 
                                        ["Não", "Sim"], key="form_necessita_material")
            
            materiais_necessarios = []
            if necessita_material == "Sim":
                # Inicializar materiais necessários na session state para o formulário
                if 'form_materiais_necessarios' not in st.session_state:
                    st.session_state.form_materiais_necessarios = [{"nome": "", "quantidade": ""}]
                
                for i in range(len(st.session_state.form_materiais_necessarios)):
                    col1, col2 = st.columns(2)
                    with col1:
                        nome = st.text_input(f"Material necessário {i+1}", key=f"form_material_necessario_nome_{i}")
                    with col2:
                        quantidade = st.text_input(f"Quantidade necessária {i+1}", key=f"form_material_necessario_qtd_{i}")
                    
                    if nome:
                        materiais_necessarios.append({"nome": nome, "quantidade": quantidade})
                
                # Botão para adicionar mais um material necessário
                add_material_necessario = st.checkbox("Adicionar outra necessidade de material", key="add_material_necessario")
                if add_material_necessario and len(st.session_state.form_materiais_necessarios) == len(materiais_necessarios):
                    st.session_state.form_materiais_necessarios.append({"nome": "", "quantidade": ""})
            
            # Equipamentos utilizados (mantido como estava)
            equipamentos = st.text_area("Equipamentos Utilizados", height=100)
            
            # Efetivo presente
            efetivo_presente = st.number_input("Efetivo Presente", min_value=1, value=1)
            
            # Upload de fotos gerais (opcional)
            fotos = st.file_uploader("Adicionar Fotos Gerais (opcional)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            
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
                    "recebimento_material": {
                        "recebeu_material": recebeu_material,
                        "materiais": materiais_recebidos
                    },
                    "necessidade_material": {
                        "necessita_material": necessita_material,
                        "materiais": materiais_necessarios
                    },
                    "equipamentos": equipamentos,
                    "efetivo_presente": efetivo_presente,
                    "equipe": equipe_selecionada if equipe_selecionada else "",
                    "hora_criacao": datetime.now().strftime("%H:%M:%S"),
                    "fotos": [] # Aqui seria necessário implementar o salvamento de fotos
                }
                
                # Salvar relatório
                relatorios = carregar_relatorios()
                relatorios[relatorio_id] = novo_relatorio
                salvar_relatorios(relatorios)
                
                # Limpar os formulários
                st.session_state.form_atividades = [{"descricao": "", "anexo": None}]
                st.session_state.form_ocorrencias = [{"descricao": "", "anexo": None}]
                st.session_state.form_materiais_recebidos = [{"nome": "", "quantidade": ""}]
                st.session_state.form_materiais_necessarios = [{"nome": "", "quantidade": ""}]
                
                st.success(f"Relatório {relatorio_id} criado com sucesso!")

# Função para visualizar relatórios
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
            
            # Exibir atividades com seus anexos
            st.subheader("Atividades Realizadas")
            if isinstance(relatorio.get('atividades'), list):
                for i, atividade in enumerate(relatorio['atividades']):
                    st.write(f"**Atividade {i+1}:** {atividade['descricao']}")
                    if atividade.get('anexo'):
                        st.write(f"**Anexo:** {atividade['anexo']}")
            else:
                # Compatibilidade com formato antigo
                st.write(relatorio.get('atividades', 'Nenhuma atividade registrada'))
            
            # Exibir ocorrências com seus anexos
            st.subheader("Ocorrências e Observações")
            if isinstance(relatorio.get('ocorrencias'), list):
                for i, ocorrencia in enumerate(relatorio['ocorrencias']):
                    st.write(f"**Ocorrência {i+1}:** {ocorrencia['descricao']}")
                    if ocorrencia.get('anexo'):
                        st.write(f"**Anexo:** {ocorrencia['anexo']}")
            else:
                # Compatibilidade com formato antigo
                st.write(relatorio.get('ocorrencias', 'Nenhuma ocorrência registrada'))
            
            # Exibir informações de recebimento de material
            st.subheader("Materiais Recebidos")
            if isinstance(relatorio.get('recebimento_material'), dict):
                recebimento = relatorio['recebimento_material']
                if recebimento.get('recebeu_material') == "Sim" and recebimento.get('materiais'):
                    for i, material in enumerate(recebimento['materiais']):
                        st.write(f"**Material {i+1}:** {material['nome']} - Quantidade: {material['quantidade']}")
                else:
                    st.write("Não houve recebimento de materiais.")
            else:
                # Compatibilidade com formato antigo
                st.write(relatorio.get('materiais', 'Nenhum material recebido'))
            
            # Exibir informações de necessidade de material
            st.subheader("Necessidade de Material")
            if isinstance(relatorio.get('necessidade_material'), dict):
                necessidade = relatorio['necessidade_material']
                if necessidade.get('necessita_material') == "Sim" and necessidade.get('materiais'):
                    for i, material in enumerate(necessidade['materiais']):
                        st.write(f"**Material {i+1}:** {material['nome']} - Quantidade: {material['quantidade']}")
                else:
                    st.write("Não há necessidade de materiais.")
            
            # Exibir equipamentos
            st.subheader("Equipamentos Utilizados")
            st.write(relatorio.get('equipamentos', 'Nenhum equipamento registrado'))
            
            # Aqui mostrar fotos se houver
            if relatorio.get('fotos') and len(relatorio['fotos']) > 0:
                st.subheader("Fotos")
                # Implementar visualização das fotos
