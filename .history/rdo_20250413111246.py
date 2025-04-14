import streamlit as st
import pandas as pd
import datetime
from data_manager import (
    carregar_obras, carregar_funcionarios, carregar_equipes, carregar_relatorios, 
    salvar_relatorios, obter_caminho_anexo, salvar_anexo, processar_anexos_atividades, 
    processar_anexos_ocorrencias, processar_fotos_gerais, excluir_anexos_relatorio,
    listar_anexos_relatorio
)
import os
import uuid
from PIL import Image
import io
from datetime import datetime

def gerar_id_relatorio():
    """Gera um ID único para o relatório"""
    return str(uuid.uuid4())

def criar_rdo():
    """Interface para criar um novo Relatório Diário de Obra (RDO)"""
    st.title("Criar Relatório Diário de Obra (RDO)")
    
    # Carregar dados necessários
    obras = carregar_obras()
    funcionarios = carregar_funcionarios()
    equipes = carregar_equipes()
    
    if not obras:
        st.warning("Não há obras cadastradas. Por favor, cadastre uma obra primeiro.")
        return
    
    # Formulário principal
    with st.form("formulario_rdo"):
        # Seção 1: Informações Básicas
        st.subheader("1. Informações Básicas")
        col1, col2 = st.columns(2)
        
        with col1:
            obra = st.selectbox("Obra:", options=list(obras.keys()))
            data_relatorio = st.date_input("Data do Relatório:", datetime.today())
            
        with col2:
            clima = st.selectbox("Condições Climáticas:", options=[
                "Ensolarado", "Parcialmente Nublado", "Nublado", 
                "Chuvoso", "Tempestade", "Neblina"
            ])
            temperatura = st.slider("Temperatura (°C):", min_value=-10, max_value=50, value=25)
        
        # Seção 2: Equipe e Pessoal
        st.subheader("2. Equipe e Pessoal")
        
        # Criar lista de funcionários disponíveis para seleção
        lista_funcionarios = list(funcionarios.keys())
        if lista_funcionarios:
            funcionarios_selecionados = st.multiselect(
                "Funcionários Presentes:", 
                options=lista_funcionarios,
                format_func=lambda x: f"{x} - {funcionarios[x].get('nome', 'Nome não informado')}"
            )
        else:
            st.warning("Não há funcionários cadastrados.")
            funcionarios_selecionados = []
        
        equipes_disponiveis = list(equipes.keys())
        if equipes_disponiveis:
            equipes_selecionadas = st.multiselect(
                "Equipes Presentes:", 
                options=equipes_disponiveis
            )
        else:
            st.warning("Não há equipes cadastradas.")
            equipes_selecionadas = []
            
        # Campo para observações de pessoal
        observacoes_pessoal = st.text_area("Observações sobre Pessoal:", height=100)
        
        # Seção 3: Atividades Realizadas (com suporte a anexos)
        st.subheader("3. Atividades Realizadas")
        
        # Usar estado da sessão para controlar as atividades dinâmicas
        if 'atividades' not in st.session_state:
            st.session_state.atividades = [{
                'descricao': '',
                'status': 'Em Andamento',
                'responsavel': '',
                'anexo': None
            }]
        
        # Display all activities
        for i, atividade in enumerate(st.session_state.atividades):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.session_state.atividades[i]['descricao'] = st.text_area(
                    f"Descrição da Atividade {i+1}:", 
                    value=atividade['descricao'],
                    key=f"desc_ativ_{i}"
                )
            
            with col2:
                st.session_state.atividades[i]['status'] = st.selectbox(
                    f"Status da Atividade {i+1}:", 
                    options=["Não Iniciada", "Em Andamento", "Concluída", "Atrasada"], 
                    index=["Não Iniciada", "Em Andamento", "Concluída", "Atrasada"].index(atividade['status']),
                    key=f"status_ativ_{i}"
                )
                st.session_state.atividades[i]['responsavel'] = st.selectbox(
                    f"Responsável pela Atividade {i+1}:", 
                    options=[''] + lista_funcionarios,
                    format_func=lambda x: '' if x == '' else f"{x} - {funcionarios[x].get('nome', 'Nome não informado')}",
                    index=0 if atividade['responsavel'] == '' else lista_funcionarios.index(atividade['responsavel']) + 1,
                    key=f"resp_ativ_{i}"
                )
            
            with col3:
                st.session_state.atividades[i]['anexo'] = st.file_uploader(
                    f"Anexo da Atividade {i+1}:", 
                    type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'],
                    key=f"anexo_ativ_{i}"
                )
                
                if i > 0:  # Não permitir remover a primeira atividade
                    if st.button(f"Remover Atividade {i+1}", key=f"rem_ativ_{i}"):
                        st.session_state.atividades.pop(i)
                        st.rerun()
        
        # Botão para adicionar nova atividade
        if st.button("+ Adicionar Atividade"):
            st.session_state.atividades.append({
                'descricao': '',
                'status': 'Em Andamento',
                'responsavel': '',
                'anexo': None
            })
            st.rerun()
        
        # Seção 4: Ocorrências e Problemas (com suporte a anexos)
        st.subheader("4. Ocorrências e Problemas")
        
        # Usar estado da sessão para controlar as ocorrências
        if 'ocorrencias' not in st.session_state:
            st.session_state.ocorrencias = []
        
        # Opção para adicionar uma ocorrência
        adicionar_ocorrencia = st.checkbox("Registrar Ocorrência/Problema")
        
        if adicionar_ocorrencia:
            if len(st.session_state.ocorrencias) == 0:
                st.session_state.ocorrencias.append({
                    'descricao': '',
                    'gravidade': 'Baixa',
                    'resolucao': '',
                    'anexo': None
                })
            
            # Display all occurrences
            for i, ocorrencia in enumerate(st.session_state.ocorrencias):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.session_state.ocorrencias[i]['descricao'] = st.text_area(
                        f"Descrição da Ocorrência {i+1}:", 
                        value=ocorrencia['descricao'],
                        key=f"desc_ocor_{i}"
                    )
                
                with col2:
                    st.session_state.ocorrencias[i]['gravidade'] = st.selectbox(
                        f"Gravidade da Ocorrência {i+1}:", 
                        options=["Baixa", "Média", "Alta", "Crítica"],
                        index=["Baixa", "Média", "Alta", "Crítica"].index(ocorrencia['gravidade']),
                        key=f"grav_ocor_{i}"
                    )
                    st.session_state.ocorrencias[i]['resolucao'] = st.text_area(
                        f"Resolução/Encaminhamento {i+1}:", 
                        value=ocorrencia['resolucao'],
                        key=f"resol_ocor_{i}"
                    )
                
                with col3:
                    st.session_state.ocorrencias[i]['anexo'] = st.file_uploader(
                        f"Anexo da Ocorrência {i+1}:", 
                        type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'],
                        key=f"anexo_ocor_{i}"
                    )
                    
                    if i > 0:  # Permitir remover ocorrências adicionais
                        if st.button(f"Remover Ocorrência {i+1}", key=f"rem_ocor_{i}"):
                            st.session_state.ocorrencias.pop(i)
                            st.rerun()
            
            # Botão para adicionar nova ocorrência
            if st.button("+ Adicionar Ocorrência"):
                st.session_state.ocorrencias.append({
                    'descricao': '',
                    'gravidade': 'Baixa',
                    'resolucao': '',
                    'anexo': None
                })
                st.rerun()
        
        # Seção 5: Fotos da Obra
        st.subheader("5. Fotos da Obra")
        fotos = st.file_uploader("Carregar Fotos do Dia:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        # Mostrar imagens carregadas em formato de galeria
        if fotos:
            cols = st.columns(3)
            for i, foto in enumerate(fotos):
                with cols[i % 3]:
                    st.image(foto, caption=f"Foto {i+1}", use_column_width=True)
        
        # Seção 6: Observações Gerais
        st.subheader("6. Observações Gerais")
        observacoes_gerais = st.text_area("Observações:", height=150)
        
        # Botão de submissão
        submissao = st.form_submit_button("Salvar Relatório")
        
    # Processamento do formulário quando submetido
    if submissao:
        if not st.session_state.atividades[0]['descricao']:
            st.error("Por favor, adicione pelo menos uma atividade ao relatório.")
            return
        
        # Preparar dados do relatório
        id_relatorio = gerar_id_relatorio()
        relatorio = {
            "id": id_relatorio,
            "obra": obra,
            "data_relatorio": data_relatorio.strftime("%Y-%m-%d"),
            "clima": clima,
            "temperatura": temperatura,
            "funcionarios": funcionarios_selecionados,
            "equipes": equipes_selecionadas,
            "observacoes_pessoal": observacoes_pessoal,
            "usuario_criacao": st.session_state.usuario_atual,
            "nome_usuario_criacao": st.session_state.nome_completo,
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "observacoes_gerais": observacoes_gerais
        }
        
        # Processar e salvar anexos das atividades
        relatorio["atividades"] = processar_anexos_atividades(id_relatorio, st.session_state.atividades)
        
        # Processar e salvar anexos das ocorrências
        if adicionar_ocorrencia and st.session_state.ocorrencias:
            relatorio["ocorrencias"] = processar_anexos_ocorrencias(id_relatorio, st.session_state.ocorrencias)
        else:
            relatorio["ocorrencias"] = []
        
        # Processar e salvar fotos gerais
        if fotos:
            relatorio["fotos"] = processar_fotos_gerais(id_relatorio, fotos)
        else:
            relatorio["fotos"] = []
        
        # Salvar o relatório
        relatorios = carregar_relatorios()
        relatorios[id_relatorio] = relatorio
        salvar_relatorios(relatorios)
        
        # Limpar o formulário
        st.session_state.atividades = [{
            'descricao': '',
            'status': 'Em Andamento',
            'responsavel': '',
            'anexo': None
        }]
        st.session_state.ocorrencias = []
        
        # Mostrar mensagem de sucesso
        st.success(f"Relatório salvo com sucesso! ID: {id_relatorio}")
        st.balloons()

def visualizar_relatorios():
    """Interface para visualizar os relatórios de obra"""
    st.title("Relatórios Diários de Obra")
    
    # Carregar dados
    relatorios = carregar_relatorios()
    obras = carregar_obras()
    funcionarios = carregar_funcionarios()
    
    if not relatorios:
        st.info("Nenhum relatório encontrado.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro por obra
        todas_obras = ["Todas"] + list(obras.keys())
        obra_filtro = st.selectbox("Filtrar por Obra:", todas_obras)
    
    with col2:
        # Filtro por data
        data_inicio = st.date_input(
            "Data Inicial:", 
            datetime.today() - datetime.timedelta(days=30)
        )
    
    with col3:
        data_fim = st.date_input("Data Final:", datetime.today())
    
    # Aplicar filtros
    relatorios_filtrados = {}
    for id_relatorio, relatorio in relatorios.items():
        # Filtrar por obra
        if obra_filtro != "Todas" and relatorio["obra"] != obra_filtro:
            continue
        
        # Filtrar por data
        data_rel = datetime.strptime(relatorio["data_relatorio"], "%Y-%m-%d").date()
        if data_rel < data_inicio or data_rel > data_fim:
            continue
        
        # Filtrar por usuário (se não for admin)
        if st.session_state.nivel_acesso != "admin" and st.session_state.nivel_acesso != "gerente":
            if relatorio["usuario_criacao"] != st.session_state.usuario_atual:
                continue
        
        relatorios_filtrados[id_relatorio] = relatorio
    
    # Exibir relatórios em formato de tabela
    if not relatorios_filtrados:
        st.info("Nenhum relatório encontrado com os filtros aplicados.")
        return
    
    # Preparar dados para tabela
    tabela_dados = []
    for id_relatorio, relatorio in relatorios_filtrados.items():
        tabela_dados.append({
            "ID": id_relatorio[:8] + "...",  # Mostrar apenas parte do UUID
            "Obra": relatorio["obra"],
            "Data": relatorio["data_relatorio"],
            "Clima": relatorio["clima"],
            "Criado por": relatorio["nome_usuario_criacao"],
            "Atividades": len(relatorio["atividades"]),
            "Ocorrências": len(relatorio["ocorrencias"]),
            "ID_Completo": id_relatorio  # Para uso interno
        })
    
    # Converter para DataFrame
    df = pd.DataFrame(tabela_dados)
    
    # Exibir tabela com opção de ordenação
    st.dataframe(df.drop(columns=["ID_Completo"]), use_container_width=True)
    
    # Seleção de relatório para visualização detalhada
    relatorio_selecionado = st.selectbox(
        "Selecione um relatório para visualizar detalhes:",
        options=[f"{r['ID']} - {r['Obra']} ({r['Data']})" for r in tabela_dados],
        format_func=lambda x: x
    )
    
    if relatorio_selecionado:
        # Encontrar o ID completo do relatório selecionado
        id_parcial = relatorio_selecionado.split(" - ")[0]
        id_completo = next((r["ID_Completo"] for r in tabela_dados if r["ID"] == id_parcial), None)
        
        if id_completo and id_completo in relatorios:
            exibir_detalhes_relatorio(id_completo, relatorios[id_completo], funcionarios)

def exibir_detalhes_relatorio(id_relatorio, relatorio, funcionarios):
    """Exibe os detalhes de um relatório específico"""
    st.divider()
    st.subheader(f"Relatório da Obra: {relatorio['obra']}")
    st.caption(f"Data: {relatorio['data_relatorio']} | Criado por: {relatorio['nome_usuario_criacao']}")
    
    # Informações Básicas
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Clima:** {relatorio['clima']}")
        st.write(f"**Temperatura:** {relatorio['temperatura']}°C")
    
    with col2:
        # Exibir funcionários presentes
        if relatorio['funcionarios']:
            funcionarios_nomes = [
                f"{id_func} - {funcionarios.get(id_func, {}).get('nome', 'Nome não disponível')}" 
                for id_func in relatorio['funcionarios']
            ]
            st.write("**Funcionários Presentes:**")
            st.write(", ".join(funcionarios_nomes))
        
        # Exibir equipes presentes
        if relatorio['equipes']:
            st.write("**Equipes Presentes:**")
            st.write(", ".join(relatorio['equipes']))
    
    # Observações sobre Pessoal
    if relatorio.get('observacoes_pessoal'):
        st.write("**Observações sobre Pessoal:**")
        st.write(relatorio['observacoes_pessoal'])
    
    # Atividades Realizadas
    st.write("### Atividades Realizadas")
    for i, atividade in enumerate(relatorio['atividades']):
        expandir = st.expander(f"Atividade {i+1}: {atividade['descricao'][:50]}...")
        with expandir:
            st.write(f"**Descrição:** {atividade['descricao']}")
            st.write(f"**Status:** {atividade['status']}")
            
            if atividade.get('responsavel'):
                responsavel = funcionarios.get(atividade['responsavel'], {}).get('nome', atividade['responsavel'])
                st.write(f"**Responsável:** {responsavel}")
            
            # Mostrar anexo se houver
            if atividade.get('anexo'):
                try:
                    caminho_anexo = obter_caminho_anexo(atividade['anexo'])
                    if os.path.exists(caminho_anexo):
                        nome_arquivo = os.path.basename(caminho_anexo)
                        extensao = nome_arquivo.split('.')[-1].lower()
                        
                        if extensao in ['png', 'jpg', 'jpeg']:
                            img = Image.open(caminho_anexo)
                            st.image(img, caption=f"Anexo da Atividade {i+1}", use_column_width=True)
                        else:
                            st.write(f"**Anexo:** {nome_arquivo} (Clique para baixar)")
                            with open(caminho_anexo, "rb") as file:
                                st.download_button(
                                    label="Baixar Anexo",
                                    data=file,
                                    file_name=nome_arquivo,
                                    mime=f"application/{extensao}"
                                )
                except Exception as e:
                    st.error(f"Erro ao carregar anexo: {str(e)}")
    
    # Ocorrências e Problemas
    if relatorio.get('ocorrencias') and len(relatorio['ocorrencias']) > 0:
        st.write("### Ocorrências e Problemas")
        for i, ocorrencia in enumerate(relatorio['ocorrencias']):
            expandir = st.expander(f"Ocorrência {i+1}: {ocorrencia['descricao'][:50]}...")
            with expandir:
                st.write(f"**Descrição:** {ocorrencia['descricao']}")
                st.write(f"**Gravidade:** {ocorrencia['gravidade']}")
                
                if ocorrencia.get('resolucao'):
                    st.write(f"**Resolução/Encaminhamento:** {ocorrencia['resolucao']}")
                
                # Mostrar anexo se houver
                if ocorrencia.get('anexo'):
                    try:
                        caminho_anexo = obter_caminho_anexo(ocorrencia['anexo'])
                        if os.path.exists(caminho_anexo):
                            nome_arquivo = os.path.basename(caminho_anexo)
                            extensao = nome_arquivo.split('.')[-1].lower()
                            
                            if extensao in ['png', 'jpg', 'jpeg']:
                                img = Image.open(caminho_anexo)
                                st.image(img, caption=f"Anexo da Ocorrência {i+1}", use_column_width=True)
                            else:
                                st.write(f"**Anexo:** {nome_arquivo}")
                                with open(caminho_anexo, "rb") as file:
                                    st.download_button(
                                        label="Baixar Anexo",
                                        data=file,
                                        file_name=nome_arquivo,
                                        mime=f"application/{extensao}"
                                    )
                    except Exception as e:
                        st.error(f"Erro ao carregar anexo: {str(e)}")
    
    # Fotos da Obra
    if relatorio.get('fotos') and len(relatorio['fotos']) > 0:
        st.write("### Fotos da Obra")
        
        # Criar galeria de fotos
        colunas = st.columns(3)
        for i, foto_path in enumerate(relatorio['fotos']):
            try:
                caminho_foto = obter_caminho_anexo(foto_path)
                if os.path.exists(caminho_foto):
                    with colunas[i % 3]:
                        img = Image.open(caminho_foto)
                        st.image(img, caption=f"Foto {i+1}", use_column_width=True)
            except Exception as e:
                st.error(f"Erro ao carregar foto {i+1}: {str(e)}")
    
    # Observações Gerais
    if relatorio.get('observacoes_gerais'):
        st.write("### Observações Gerais")
        st.write(relatorio['observacoes_gerais'])
    
    # Opções de administração (para admin e gerente)
    if st.session_state.nivel_acesso in ["admin", "gerente"]:
        st.divider()
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Excluir Relatório", type="primary", use_container_width=True):
                if confirmar_exclusao(id_relatorio):
                    st.success("Relatório excluído com sucesso!")
                    st.rerun()

def confirmar_exclusao(id_relatorio):
    """Confirma e exclui um relatório"""
    relatorios = carregar_relatorios()
    
    # Verificar se o relatório existe
    if id_relatorio not in relatorios:
        st.error("Relatório não encontrado!")
        return False
    
    # Remover o relatório
    excluir_anexos_relatorio(id_relatorio)
    del relatorios[id_relatorio]
    salvar_relatorios(relatorios)
    return True
