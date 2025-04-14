import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
import uuid
from PIL import Image
import data_manager as dm
import io

def criar_rdo():
    st.title("Criar Relatório Diário de Obra")
    
    # Variáveis para controle de sessão
    if 'relatorio_submetido' not in st.session_state:
        st.session_state.relatorio_submetido = False
    
    if st.session_state.relatorio_submetido:
        st.success("Relatório enviado com sucesso!")
        if st.button("Criar novo relatório"):
            st.session_state.relatorio_submetido = False
            st.experimental_rerun()
        return
    
    # Cabeçalho do relatório
    st.subheader("Informações Gerais")
    col1, col2 = st.columns(2)
    
    with col1:
        data_relatorio = st.date_input("Data do Relatório", value=date.today())
        
        # Carregar obras e equipes
        obras = dm.carregar_obras()
        lista_obras = list(obras.keys())
        obra_selecionada = st.selectbox("Obra", lista_obras, index=0 if lista_obras else None)
        
        equipes = dm.carregar_equipes()
        lista_equipes = list(equipes.keys())
        equipe_selecionada = st.selectbox("Equipe", lista_equipes, index=0 if lista_equipes else None)
    
    with col2:
        # Clima
        clima_opcoes = ["Ensolarado", "Nublado", "Chuvoso", "Tempestade", "Outros"]
        clima = st.selectbox("Condição Climática", clima_opcoes)
        
        # Se for "Outros", pedir para especificar
        if clima == "Outros":
            clima_especificado = st.text_input("Especifique a condição climática")
            clima = clima_especificado if clima_especificado else clima
        
        # Impacto do clima
        impacto_clima = st.radio("O clima impactou as atividades?", ["Sim", "Não"], index=1)
        
        # Se o clima impactou, pedir detalhes
        if impacto_clima == "Sim":
            detalhes_clima = st.text_area("Detalhe como o clima impactou as atividades")
        else:
            detalhes_clima = ""
    
    # Seção de Funcionários
    st.subheader("Funcionários")
    
    # Carregar funcionários
    funcionarios = dm.carregar_funcionarios()
    lista_funcionarios = list(funcionarios.keys())
    
    # Multiselect para selecionar funcionários presentes
    funcionarios_presentes = st.multiselect("Funcionários presentes", lista_funcionarios)
    
    # Número de funcionários presentes
    num_funcionarios = st.number_input("Total de funcionários presentes (incluindo terceirizados)", 
                                       min_value=0, 
                                       max_value=1000, 
                                       value=len(funcionarios_presentes),
                                       step=1)
    
    # Atividades Realizadas com anexos individuais
    st.subheader("Atividades Realizadas")
    
    # Inicializar lista de atividades na session state
    if 'lista_atividades' not in st.session_state:
        st.session_state.lista_atividades = [{"descricao": "", "anexo": None}]
    
    # Exibir campos para cada atividade
    atividades_para_remover = []
    
    for i, atividade in enumerate(st.session_state.lista_atividades):
        with st.container():
            st.markdown(f"##### Atividade {i+1}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.session_state.lista_atividades[i]["descricao"] = st.text_area(
                    f"Descrição da atividade {i+1}", 
                    value=atividade["descricao"],
                    height=100,
                    key=f"desc_ativ_{i}"
                )
            
            with col2:
                st.session_state.lista_atividades[i]["anexo"] = st.file_uploader(
                    f"Anexo da atividade {i+1}", 
                    type=["jpg", "jpeg", "png", "pdf"],
                    key=f"anexo_ativ_{i}"
                )
            
            # Botão para remover atividade (exceto a primeira)
            if i > 0:
                if st.button(f"Remover atividade {i+1}", key=f"rm_ativ_{i}"):
                    atividades_para_remover.append(i)
    
    # Remover atividades marcadas para remoção
    for idx in sorted(atividades_para_remover, reverse=True):
        st.session_state.lista_atividades.pop(idx)
    
    # Botão para adicionar nova atividade
    if st.button("Adicionar outra atividade"):
        st.session_state.lista_atividades.append({"descricao": "", "anexo": None})
        st.experimental_rerun()
    
    # Ocorrências com anexos individuais
    st.subheader("Ocorrências")
    
    # Perguntar se houve ocorrências
    teve_ocorrencias = st.radio("Houve ocorrências a relatar?", ["Sim", "Não"], index=1, key="teve_ocorrencias")
    
    if teve_ocorrencias == "Sim":
        # Inicializar lista de ocorrências na session state
        if 'lista_ocorrencias' not in st.session_state or st.session_state.teve_ocorrencias == "Não":
            st.session_state.lista_ocorrencias = [{"descricao": "", "anexo": None}]
        
        # Exibir campos para cada ocorrência
        ocorrencias_para_remover = []
        
        for i, ocorrencia in enumerate(st.session_state.lista_ocorrencias):
            with st.container():
                st.markdown(f"##### Ocorrência {i+1}")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.session_state.lista_ocorrencias[i]["descricao"] = st.text_area(
                        f"Descrição da ocorrência {i+1}", 
                        value=ocorrencia["descricao"],
                        height=100,
                        key=f"desc_ocor_{i}"
                    )
                
                with col2:
                    st.session_state.lista_ocorrencias[i]["anexo"] = st.file_uploader(
                        f"Anexo da ocorrência {i+1}", 
                        type=["jpg", "jpeg", "png", "pdf"],
                        key=f"anexo_ocor_{i}"
                    )
                
                # Botão para remover ocorrência (exceto a primeira)
                if i > 0:
                    if st.button(f"Remover ocorrência {i+1}", key=f"rm_ocor_{i}"):
                        ocorrencias_para_remover.append(i)
        
        # Remover ocorrências marcadas para remoção
        for idx in sorted(ocorrencias_para_remover, reverse=True):
            st.session_state.lista_ocorrencias.pop(idx)
        
        # Botão para adicionar nova ocorrência
        if st.button("Adicionar outra ocorrência"):
            st.session_state.lista_ocorrencias.append({"descricao": "", "anexo": None})
            st.experimental_rerun()
    else:
        # Resetar a lista de ocorrências se selecionou "Não"
        st.session_state.lista_ocorrencias = []
    
    # Seção de Materiais Recebidos
    st.subheader("Recebimento de Material")
    
    recebeu_material = st.radio("Houve recebimento de materiais hoje?", ["Sim", "Não"], index=1, key="recebeu_material")
    
    recebimento_material = {"recebeu_material": recebeu_material, "materiais": []}
    
    if recebeu_material == "Sim":
        # Inicializar lista de materiais recebidos na session state
        if 'lista_materiais_recebidos' not in st.session_state or st.session_state.recebeu_material == "Não":
            st.session_state.lista_materiais_recebidos = [{"nome": "", "quantidade": ""}]
        
        # Exibir campos para cada material recebido
        materiais_para_remover = []
        
        for i, material in enumerate(st.session_state.lista_materiais_recebidos):
            with st.container():
                st.markdown(f"##### Material Recebido {i+1}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_material = st.text_input(
                        f"Nome do material {i+1}", 
                        value=material["nome"],
                        key=f"nome_mat_rec_{i}"
                    )
                
                with col2:
                    qtd_material = st.text_input(
                        f"Quantidade {i+1}", 
                        value=material["quantidade"],
                        key=f"qtd_mat_rec_{i}"
                    )
                
                recebimento_material["materiais"].append({"nome": nome_material, "quantidade": qtd_material})
                
                # Botão para remover material (exceto o primeiro)
                if i > 0:
                    if st.button(f"Remover material {i+1}", key=f"rm_mat_rec_{i}"):
                        materiais_para_remover.append(i)
        
        # Remover materiais marcados para remoção
        for idx in sorted(materiais_para_remover, reverse=True):
            st.session_state.lista_materiais_recebidos.pop(idx)
        
        # Botão para adicionar novo material
        if st.button("Adicionar outro material recebido"):
            st.session_state.lista_materiais_recebidos.append({"nome": "", "quantidade": ""})
            st.experimental_rerun()
    else:
        # Resetar a lista de materiais recebidos se selecionou "Não"
        st.session_state.lista_materiais_recebidos = []
    
    # Seção de Necessidade de Material
    st.subheader("Necessidade de Material")
    
    necessita_material = st.radio("Há necessidade de materiais para os próximos dias?", ["Sim", "Não"], index=1, key="necessita_material")
    
    necessidade_material = {"necessita_material": necessita_material, "materiais": []}
    
    if necessita_material == "Sim":
        # Inicializar lista de materiais necessários na session state
        if 'lista_materiais_necessarios' not in st.session_state or st.session_state.necessita_material == "Não":
            st.session_state.lista_materiais_necessarios = [{"nome": "", "quantidade": ""}]
        
        # Exibir campos para cada material necessário
        materiais_para_remover = []
        
        for i, material in enumerate(st.session_state.lista_materiais_necessarios):
            with st.container():
                st.markdown(f"##### Material Necessário {i+1}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_material = st.text_input(
                        f"Nome do material {i+1}", 
                        value=material["nome"],
                        key=f"nome_mat_nec_{i}"
                    )
                
                with col2:
                    qtd_material = st.text_input(
                        f"Quantidade {i+1}", 
                        value=material["quantidade"],
                        key=f"qtd_mat_nec_{i}"
                    )
                
                necessidade_material["materiais"].append({"nome": nome_material, "quantidade": qtd_material})
                
                # Botão para remover material (exceto o primeiro)
                if i > 0:
                    if st.button(f"Remover material {i+1}", key=f"rm_mat_nec_{i}"):
                        materiais_para_remover.append(i)
        
        # Remover materiais marcados para remoção
        for idx in sorted(materiais_para_remover, reverse=True):
            st.session_state.lista_materiais_necessarios.pop(idx)
        
        # Botão para adicionar novo material
        if st.button("Adicionar outro material necessário"):
            st.session_state.lista_materiais_necessarios.append({"nome": "", "quantidade": ""})
            st.experimental_rerun()
    else:
        # Resetar a lista de materiais necessários se selecionou "Não"
        st.session_state.lista_materiais_necessarios = []
    
    # Equipamentos utilizados
    st.subheader("Equipamentos Utilizados")
    equipamentos = st.text_area("Liste os equipamentos utilizados hoje", height=100)
    
    # Fotografias gerais
    st.subheader("Fotografias da Obra")
    fotografias = st.file_uploader("Adicione fotografias gerais da obra", 
                                   type=["jpg", "jpeg", "png"], 
                                   accept_multiple_files=True)
    
    # Observações gerais
    st.subheader("Observações Gerais")
    observacoes = st.text_area("Observações adicionais", height=150)
    
    # Botão de enviar
    if st.button("Enviar Relatório"):
        # Validações básicas
        if not obra_selecionada:
            st.error("Por favor, selecione uma obra.")
            return
        
        if not equipe_selecionada:
            st.error("Por favor, selecione uma equipe.")
            return
        
        # Processar atividades e verificar se há pelo menos uma com descrição
        atividades_validas = [a for a in st.session_state.lista_atividades if a["descricao"].strip()]
        if not atividades_validas:
            st.error("Por favor, descreva pelo menos uma atividade realizada.")
            return
        
        # Gerar ID único para o relatório
        relatorio_id = str(uuid.uuid4())
        
        # Processar anexos de atividades
        atividades = dm.processar_anexos_atividades(relatorio_id, atividades_validas)
        
        # Processar anexos de ocorrências, se houver
        ocorrencias = []
        if teve_ocorrencias == "Sim":
            ocorrencias_validas = [o for o in st.session_state.lista_ocorrencias if o["descricao"].strip()]
            ocorrencias = dm.processar_anexos_ocorrencias(relatorio_id, ocorrencias_validas)
        
        # Processar fotografias gerais
        fotos_salvas = []
        if fotografias:
            fotos_salvas = dm.processar_fotos_gerais(relatorio_id, fotografias)
        
        # Criar objeto de relatório completo
        relatorio = {
            "id": relatorio_id,
            "data": data_relatorio.strftime("%Y-%m-%d"),
            "obra": obra_selecionada,
            "equipe": equipe_selecionada,
            "clima": clima,
            "impacto_clima": impacto_clima,
            "detalhes_clima": detalhes_clima,
            "funcionarios_presentes": funcionarios_presentes,
            "num_funcionarios": num_funcionarios,
            "atividades": atividades,
            "ocorrencias": ocorrencias,
            "recebimento_material": recebimento_material,
            "necessidade_material": necessidade_material,
            "equipamentos": equipamentos,
            "fotos": fotos_salvas,
            "observacoes": observacoes,
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "criado_por": st.session_state.get("usuario_atual", "desconhecido")
        }
        
        # Salvar relatório
        relatorios = dm.carregar_relatorios()
        relatorios[relatorio_id] = relatorio
        dm.salvar_relatorios(relatorios)
        
        st.session_state.relatorio_submetido = True
        st.experimental_rerun()

def visualizar_rdos():
    st.title("Relatórios Diários de Obra")
    
    # Carregar relatórios
    relatorios = dm.carregar_relatorios()
    
    if not relatorios:
        st.info("Não há relatórios registrados ainda.")
        return
    
    # Converter relatórios em DataFrame para facilitar a filtragem
    relatorios_df = []
    for rel_id, rel in relatorios.items():
        relatorios_df.append({
            "id": rel_id,
            "data": rel.get("data", ""),
            "obra": rel.get("obra", ""),
            "equipe": rel.get("equipe", ""),
            "criado_em": rel.get("data_criacao", "")
        })
    
    df = pd.DataFrame(relatorios_df)
    
    # Adicionar filtros
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtrar por obra
        obras = ["Todas"] + list(set(df["obra"].tolist()))
        obra_filtro = st.selectbox("Filtrar por Obra", obras)
    
    with col2:
        # Filtrar por data
        datas = ["Todas"] + sorted(list(set(df["data"].tolist())))
        data_filtro = st.selectbox("Filtrar por Data", datas)
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if obra_filtro != "Todas":
        filtered_df = filtered_df[filtered_df["obra"] == obra_filtro]
    
    if data_filtro != "Todas":
        filtered_df = filtered_df[filtered_df["data"] == data_filtro]
    
    # Ordenar por data (mais recente primeiro)
    filtered_df = filtered_df.sort_values(by="data", ascending=False)
    
    # Mostrar relatórios filtrados
    st.subheader("Relatórios Disponíveis")
    
    if filtered_df.empty:
        st.info("Não há relatórios que correspondam aos filtros selecionados.")
        return
    
    # Exibir os relatórios como cards
    for index, row in filtered_df.iterrows():
        rel_id = row["id"]
        relatorio = relatorios[rel_id]
        
        with st.expander(f"RDO: {row['data']} - {row['obra']} - Equipe: {row['equipe']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Data do Relatório:** {relatorio.get('data', '')}")
                st.write(f"**Obra:** {relatorio.get('obra', '')}")
                st.write(f"**Equipe:** {relatorio.get('equipe', '')}")
            
            with col2:
                st.write(f"**Clima:** {relatorio.get('clima', '')}")
                st.write(f"**Impacto do Clima:** {relatorio.get('impacto_clima', '')}")
                if relatorio.get('impacto_clima') == "Sim" and relatorio.get('detalhes_clima'):
                    st.write(f"**Detalhes do impacto:** {relatorio.get('detalhes_clima', '')}")
            
            # Funcionários presentes
            st.subheader("Funcionários")
            st.write(f"**Total de Funcionários:** {relatorio.get('num_funcionarios', '0')}")
            if relatorio.get('funcionarios_presentes'):
                st.write("**Funcionários Presentes:**")
                for funcionario in relatorio.get('funcionarios_presentes', []):
                    st.write(f"- {funcionario}")
            
            # Atividades
            st.subheader("Atividades Realizadas")
            if isinstance(relatorio.get('atividades'), list) and relatorio['atividades']:
                for i, atividade in enumerate(relatorio['atividades']):
                    st.markdown(f"##### Atividade {i+1}")
                    st.write(atividade.get('descricao', ''))
                    
                    # Mostrar anexo da atividade se existir
                    if atividade.get('anexo'):
                        try:
                            # Se for um caminho válido no sistema
                            anexo_path = dm.obter_caminho_anexo(atividade['anexo'])
                            if os.path.exists(anexo_path):
                                # Verificar se é uma imagem ou PDF
                                if anexo_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                    img = Image.open(anexo_path)
                                    st.image(img, caption=f"Anexo da Atividade {i+1}", width=300)
                                else:
                                    # Para outros tipos de arquivos, mostramos apenas o link
                                    st.write(f"[Anexo da Atividade {i+1}]({anexo_path})")
                        except Exception as e:
                            st.error(f"Erro ao exibir anexo: {str(e)}")
            else:
                # Compatibilidade com formato antigo
                st.write(relatorio.get('atividades', 'Nenhuma atividade registrada'))
            
            # Ocorrências
            st.subheader("Ocorrências")
            if relatorio.get('ocorrencias'):
                if isinstance(relatorio['ocorrencias'], list) and len(relatorio['ocorrencias']) > 0:
                    for i, ocorrencia in enumerate(relatorio['ocorrencias']):
                        st.markdown(f"##### Ocorrência {i+1}")
                        st.write(ocorrencia.get('descricao', ''))
                        
                        # Mostrar anexo da ocorrência se existir
                        if ocorrencia.get('anexo'):
                            try:
                                anexo_path = dm.obter_caminho_anexo(ocorrencia['anexo'])
                                if os.path.exists(anexo_path):
                                    if anexo_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                        img = Image.open(anexo_path)
                                        st.image(img, caption=f"Anexo da Ocorrência {i+1}", width=300)
                                    else:
                                        st.write(f"[Anexo da Ocorrência {i+1}]({anexo_path})")
                            except Exception as e:
                                st.error(f"Erro ao exibir anexo: {str(e)}")
                else:
                    # Compatibilidade com formato antigo
                    st.write(relatorio.get('ocorrencias', 'Nenhuma ocorrência registrada'))
            else:
                st.write("Não houve ocorrências.")
            
            # Materiais Recebidos
            st.subheader("Recebimento de Materiais")
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
            
            # Necessidade de Material
            st.subheader("Necessidade de Material")
            if isinstance(relatorio.get('necessidade_material'), dict):
                necessidade = relatorio['necessidade_material']
                if necessidade.get('necessita_material') == "Sim" and necessidade.get('materiais'):
                    for i, material in enumerate(necessidade['materiais']):
                        st.write(f"**Material {i+1}:** {material['nome']} - Quantidade: {material['quantidade']}")
                else:
                    st.write("Não há necessidade de materiais.")
            else:
                st.write("Não há registro de necessidade de materiais.")
            
            # Equipamentos
            st.subheader("Equipamentos Utilizados")
            st.write(relatorio.get('equipamentos', 'Nenhum equipamento registrado'))
            
            # Fotos gerais
            if relatorio.get('fotos') and len(relatorio['fotos']) > 0:
                st.subheader("Fotos da Obra")
                foto_cols = st.columns(3)
                for i, foto_caminho in enumerate(relatorio['fotos']):
                    try:
                        foto_path = dm.obter_caminho_anexo(foto_caminho)
                        if os.path.exists(foto_path):
                            img = Image.open(foto_path)
                            foto_cols[i % 3].image(img, caption=f"Foto {i+1}", use_column_width=True)
                    except Exception as e:
                        st.error(f"Erro ao exibir foto {i+1}: {str(e)}")
            
            # Observações
            if relatorio.get('observacoes'):
                st.subheader("Observações Gerais")
                st.write(relatorio.get('observacoes', ''))
            
            # Metadados do relatório
            st.divider()
            st.write(f"**Criado em:** {relatorio.get('data_criacao', '')}")
            st.write(f"**Por:** {relatorio.get('criado_por', 'Desconhecido')}")
            
            # Botão para baixar relatório em JSON (facilidade para depuração/backup)
            relatorio_str = json.dumps(relatorio, indent=4)
            buffer = io.StringIO()
            buffer.write(relatorio_str)
            buffer.seek(0)
            
            st.download_button(
                label="Baixar Relatório (JSON)",
                data=buffer,
                file_name=f"rdo_{relatorio.get('data', 'sem_data')}_{relatorio.get('obra', 'sem_obra')}.json",
                mime="application/json"
            )

def exportar_rdos():
    st.title("Exportar Relatórios")
    
    # Carregar relatórios
    relatorios = dm.carregar_relatorios()
    
    if not relatorios:
        st.info("Não há relatórios para exportar.")
        return
    
    # Opções de exportação
    st.subheader("Opções de Exportação")
    
    formato_export = st.radio("Escolha o formato de exportação", ["Excel", "CSV", "JSON"])
    
    # Filtros
    st.subheader("Filtros")
    
    # Obter lista de obras únicas
    obras = list(set([rel.get("obra", "") for rel in relatorios.values()]))
    
    # Filtrar por obra
    obras_filtro = st.multiselect("Filtrar por Obras", obras, default=obras)
    
    # Filtrar por período
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data de Início", value=date.today().replace(month=1, day=1))
    with col2:
        data_fim = st.date_input("Data de Fim", value=date.today())
    
    if data_inicio > data_fim:
        st.error("A data de início deve ser anterior à data de fim.")
        return
    
    # Botão para exportar
    if st.button("Gerar Exportação"):
        # Filtrar relatórios
        filtrados = {}
        for rel_id, rel in relatorios.items():
            # Verificar se a obra está nos filtros
            if rel.get("obra", "") not in obras_filtro:
                continue
            
            # Verificar se a data está no período
            try:
                rel_data = datetime.strptime(rel.get("data", ""), "%Y-%m-%d").date()
                if not (data_inicio <= rel_data <= data_fim):
                    continue
            except ValueError:
                continue
            
            # Adicionar relatório filtrado
            filtrados[rel_id] = rel
        
        if not filtrados:
            st.warning("Nenhum relatório encontrado com os filtros selecionados.")
            return
        
        # Preparar dados para exportação
        if formato_export == "Excel" or formato_export == "CSV":
            # Para Excel e CSV, precisamos transformar em linhas de planilha
            dados_export = []
            
            for rel_id, rel in filtrados.items():
                # Dados básicos
                linha_base = {
                    "ID": rel_id,
                    "Data": rel.get("data", ""),
                    "Obra": rel.get("obra", ""),
                    "Equipe": rel.get("equipe", ""),
                    "Clima": rel.get("clima", ""),
                    "Impacto do Clima": rel.get("impacto_clima", ""),
                    "Detalhes do Clima": rel.get("detalhes_clima", ""),
                    "Número de Funcionários": rel.get("num_funcionarios", ""),
                    "Equipamentos": rel.get("equipamentos", ""),
                    "Observações": rel.get("observacoes", ""),
                    "Data de Criação": rel.get("data_criacao",
