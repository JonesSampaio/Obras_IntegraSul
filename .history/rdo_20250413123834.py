import streamlit as st
import pandas as pd
import datetime
from datetime import datetime
import os
import uuid
from PIL import Image
import io
import base64
from data_manager import (
    carregar_obras, carregar_funcionarios, carregar_equipes, carregar_relatorios,
    salvar_relatorios, obter_caminho_anexo, salvar_anexo, processar_anexos_atividades,
    processar_anexos_ocorrencias, processar_fotos_gerais, excluir_anexos_relatorio,
    listar_anexos_relatorio
)
from fpdf import FPDF

def gerar_id_relatorio():
    """Gera um ID único para o relatório"""
    return str(uuid.uuid4())

def gerar_numero_sequencial_rdo():
    """Gera um número sequencial para o RDO"""
    relatorios = carregar_relatorios()
    if not relatorios:
        return 1
    
    numeros_existentes = [int(r.get('numero_rdo', 0)) for r in relatorios.values() if r.get('numero_rdo', '').isdigit()]
    if not numeros_existentes:
        return 1
    
    return max(numeros_existentes) + 1

def criar_rdo():
    """Interface para criar um novo Relatório Diário de Obra (RDO)"""
    # Cabeçalho fixo com informações do usuário
    st.title("RDO - RELATÓRIO DIÁRIO DE OBRA")
    
    # Informações do cabeçalho não editáveis
    numero_rdo = gerar_numero_sequencial_rdo()
    data_atual = datetime.now().strftime("%d/%m/%Y - %H:%M")
    nome_usuario = st.session_state.get('nome_usuario', "Usuário")
    st.write(f"Usuário: {nome_usuario}")
    st.write(f"Nº RDO: {numero_rdo}")
    st.write(f"Data: {data_atual}")
    
    # Carregar dados necessários
    obras = carregar_obras()
    funcionarios = carregar_funcionarios()
    equipes = carregar_equipes()
    
    if not obras:
        st.warning("Não há obras cadastradas. Por favor, cadastre uma obra primeiro.")
        return

    # Inicializar o estado da sessão para atividades e ocorrências
    if 'atividades' not in st.session_state:
        st.session_state.atividades = [{
            'descricao': '',
            'status': 'Em Andamento',
            'responsavel': '',
            'anexos': []
        }]
    
    if 'ocorrencias' not in st.session_state:
        st.session_state.ocorrencias = []
    
    # Inicializar estado para materiais
    if 'recebimento_materiais' not in st.session_state:
        st.session_state.recebimento_materiais = False
    
    if 'necessidade_materiais' not in st.session_state:
        st.session_state.necessidade_materiais = False
        
    if 'materiais_urgentes' not in st.session_state:
        st.session_state.materiais_urgentes = False

    # Seção 1: Informações da Obra
    st.subheader("Informações da Obra")
    obra_selecionada = st.selectbox("Nome da Obra:", options=list(obras.keys()))
    
    # Exibir informações da obra selecionada (preenchidas automaticamente)
    if obra_selecionada:
        obra_info = obras[obra_selecionada]
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Data de Início da Obra:** {obra_info.get('data_inicio', 'N/A')}")
            st.write(f"**Prazo da Obra:** {obra_info.get('prazo', 'N/A')}")
            st.write(f"**Etapa Atual:** {obra_info.get('etapa_atual', 'N/A')}")
        with col2:
            st.write(f"**Endereço:** {obra_info.get('endereco', 'N/A')}")
            st.write(f"**Nº RRT de SI:** {obra_info.get('rrt', 'N/A')}")
            st.write(f"**Responsável Técnico Principal:** {obra_info.get('responsavel_principal', 'N/A')}")
            st.write(f"**Responsável Técnico de Acompanhamento:** {obra_info.get('responsavel_acompanhamento', 'N/A')}")

    # Seção 2: Condições Climáticas
    st.subheader("Condições Climáticas")
    col1, col2 = st.columns(2)
    with col1:
        data_relatorio = st.date_input("Data do Relatório:", datetime.today())
        clima_manha = st.selectbox("Clima da Manhã:", options=[
            "Ensolarado", "Parcialmente Nublado", "Nublado",
            "Chuvoso", "Tempestade", "Neblina"
        ])
    with col2:
        clima_tarde = st.selectbox("Clima da Tarde:", options=[
            "Ensolarado", "Parcialmente Nublado", "Nublado",
            "Chuvoso", "Tempestade", "Neblina"
        ])
        temperatura = st.slider("Temperatura média (°C):", min_value=-10, max_value=50, value=25)
    
    # Controle de Chuva por hora
    st.write("Controle de Chuva:")
    cols = st.columns(10)
    controle_chuva = {}
    horas = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    for i, hora in enumerate(horas):
        with cols[i % 10]:
            st.write(hora)
            controle_chuva[hora] = st.checkbox("Chuva", key=f"chuva_{hora}")
    
    # Seção 3: Equipe e Pessoal
    st.subheader("Equipes na Obra")
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
    
    # Seção 4: Atividades do Dia
    st.subheader("Atividades do Dia")
    
    # Botão fora do formulário para adicionar atividades
    if st.button("+ Adicionar Atividade"):
        st.session_state.atividades.append({
            'descricao': '',
            'status': 'Em Andamento',
            'responsavel': '',
            'anexos': []
        })
        st.rerun()
    
    # Exibir todas as atividades
    for i, atividade in enumerate(st.session_state.atividades):
        st.write(f"**Atividade {i+1}**")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.session_state.atividades[i]['descricao'] = st.text_area(
                f"Descrição da Atividade {i+1}:",
                value=atividade['descricao'],
                key=f"desc_ativ_{i}",
                height=100
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
                index=0 if atividade.get('responsavel', '') == '' else lista_funcionarios.index(atividade['responsavel']) + 1,
                key=f"resp_ativ_{i}"
            )
        
        # Upload de arquivos para a atividade
        st.session_state.atividades[i]['anexos'] = st.file_uploader(
            f"Carregar arquivos (Atividade {i+1}):",
            type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'],
            accept_multiple_files=True,
            key=f"anexo_ativ_{i}"
        )
        
        # Botão para remover esta atividade (exceto a primeira)
        if i > 0:
            if st.button(f"Remover Atividade {i+1}", key=f"rem_ativ_{i}"):
                st.session_state.atividades.pop(i)
                st.rerun()
        
        st.divider()
    
    # Seção 5: Ocorrências
    st.subheader("Ocorrências")
    
    # Botão para adicionar ocorrência
    if st.button("+ Adicionar Ocorrência"):
        if not st.session_state.ocorrencias:
            st.session_state.ocorrencias = []
        
        st.session_state.ocorrencias.append({
            'descricao': '',
            'gravidade': 'Baixa',
            'resolucao': '',
            'anexos': []
        })
        st.rerun()
    
    # Exibir todas as ocorrências
    for i, ocorrencia in enumerate(st.session_state.ocorrencias):
        st.write(f"**Ocorrência {i+1}**")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.session_state.ocorrencias[i]['descricao'] = st.text_area(
                f"Descrição da Ocorrência {i+1}:",
                value=ocorrencia['descricao'],
                key=f"desc_ocor_{i}",
                height=100
            )
        with col2:
            st.session_state.ocorrencias[i]['gravidade'] = st.selectbox(
                f"Gravidade da Ocorrência {i+1}:",
                options=["Baixa", "Média", "Alta", "Crítica"],
                index=["Baixa", "Média", "Alta", "Crítica"].index(ocorrencia['gravidade']),
                key=f"grav_ocor_{i}"
            )
            st.session_state.ocorrencias[i]['resolucao'] = st.text_area(
                f"Resolução/Encaminhamento da Ocorrência {i+1}:",
                value=ocorrencia.get('resolucao', ''),
                key=f"resol_ocor_{i}",
                height=80
            )
        
        # Upload de arquivos para a ocorrência
        st.session_state.ocorrencias[i]['anexos'] = st.file_uploader(
            f"Carregar arquivos (Ocorrência {i+1}):",
            type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'],
            accept_multiple_files=True,
            key=f"anexo_ocor_{i}"
        )
        
        # Botão para remover esta ocorrência
        if st.button(f"Remover Ocorrência {i+1}", key=f"rem_ocor_{i}"):
            st.session_state.ocorrencias.pop(i)
            st.rerun()
        
        st.divider()
    
    # Seção 6: Materiais
    st.subheader("Materiais")
    
    # Recebimento de materiais
    receb_materiais = st.radio(
        "Houve recebimento de materiais na obra hoje?",
        options=["Sim", "Não"],
        horizontal=True,
        index=1
    )
    
    st.session_state.recebimento_materiais = (receb_materiais == "Sim")
    
    # Se houve recebimento, mostrar campo para detalhamento
    if st.session_state.recebimento_materiais:
        materiais_recebidos = st.text_area(
            "Descreva os materiais recebidos:",
            height=100,
            key="materiais_recebidos_texto"
        )
    else:
        materiais_recebidos = ""
    
    # Necessidade de materiais
    neces_materiais = st.radio(
        "Há necessidade de materiais para os próximos dias?",
        options=["Sim", "Não"],
        horizontal=True,
        index=1
    )
    
    st.session_state.necessidade_materiais = (neces_materiais == "Sim")
    
    # Se há necessidade, mostrar campo para detalhamento e opção de urgência
    if st.session_state.necessidade_materiais:
        materiais_necessarios = st.text_area(
            "Descreva os materiais necessários:",
            height=100,
            key="materiais_necessarios_texto"
        )
        
        st.session_state.materiais_urgentes = st.checkbox(
            "URGENTE (necessário nas próximas 48 horas)",
            key="materiais_urgentes_check"
        )
    else:
        materiais_necessarios = ""
        st.session_state.materiais_urgentes = False
    
    # Seção 7: Fotos Gerais
    st.subheader("Relatório Fotográfico / Documentos")
    fotos_gerais = st.file_uploader(
        "Carregar arquivos:",
        type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'],
        accept_multiple_files=True,
        key="fotos_gerais"
    )
    
    # Observações gerais
    observacoes_gerais = st.text_area("Observações Gerais:", height=150)
    
    # Botões de ação
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Relatório", use_container_width=True):
            # Processar o salvamento do relatório
            salvar_dados_rdo(
                numero_rdo=numero_rdo,
                obra=obra_selecionada,
                data_relatorio=data_relatorio.strftime("%Y/%m/%d"),
                clima_manha=clima_manha,
                clima_tarde=clima_tarde,
                temperatura=temperatura,
                controle_chuva=controle_chuva,
                funcionarios=funcionarios_selecionados,
                equipes=equipes_selecionadas,
                observacoes_pessoal=observacoes_pessoal,
                atividades=st.session_state.atividades,
                ocorrencias=st.session_state.ocorrencias,
                recebimento_materiais_sim=st.session_state.recebimento_materiais,
                materiais_recebidos=materiais_recebidos,
                necessidade_materiais_sim=st.session_state.necessidade_materiais,
                materiais_necessarios=materiais_necessarios,
                materiais_urgentes=st.session_state.materiais_urgentes,
                fotos_gerais=fotos_gerais,
                observacoes_gerais=observacoes_gerais
            )
            st.success("Relatório salvo com sucesso!")
            # Limpar o estado da sessão
            limpar_estado_sessao()
    
    with col2:
        if st.button("Salvar Relatório e Gerar PDF", use_container_width=True):
            # Salvar relatório
            id_relatorio = salvar_dados_rdo(
                numero_rdo=numero_rdo,
                obra=obra_selecionada,
                data_relatorio=data_relatorio.strftime("%Y/%m/%d"),
                clima_manha=clima_manha,
                clima_tarde=clima_tarde,
                temperatura=temperatura,
                controle_chuva=controle_chuva,
                funcionarios=funcionarios_selecionados,
                equipes=equipes_selecionadas,
                observacoes_pessoal=observacoes_pessoal,
                atividades=st.session_state.atividades,
                ocorrencias=st.session_state.ocorrencias,
                recebimento_materiais_sim=st.session_state.recebimento_materiais,
                materiais_recebidos=materiais_recebidos,
                necessidade_materiais_sim=st.session_state.necessidade_materiais,
                materiais_necessarios=materiais_necessarios,
                materiais_urgentes=st.session_state.materiais_urgentes,
                fotos_gerais=fotos_gerais,
                observacoes_gerais=observacoes_gerais
            )
            
            # Gerar PDF
            pdf_path = gerar_pdf_rdo(id_relatorio)
            
            # Disponibilizar PDF para download
            if pdf_path:
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="Baixar PDF",
                        data=file,
                        file_name=f"RDO_{numero_rdo}_{obra_selecionada}.pdf",
                        mime="application/pdf"
                    )
                st.success("Relatório salvo e PDF gerado com sucesso!")
                # Limpar o estado da sessão
                limpar_estado_sessao()

def salvar_dados_rdo(numero_rdo, obra, data_relatorio, clima_manha, clima_tarde, temperatura, 
                   controle_chuva, funcionarios, equipes, observacoes_pessoal, atividades, 
                   ocorrencias, recebimento_materiais_sim, materiais_recebidos, 
                   necessidade_materiais_sim, materiais_necessarios, materiais_urgentes,
                   fotos_gerais, observacoes_gerais):
    """Salva os dados do RDO"""
    id_relatorio = gerar_id_relatorio()
    
    # Preparar dados do relatório
    relatorio = {
        'id': id_relatorio,
        'numero_rdo': str(numero_rdo),
        'obra': obra,
        'data_relatorio': data_relatorio,
        'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'usuario_criacao': st.session_state.get('nome_usuario', "Usuário"),
        'nome_usuario_criacao': st.session_state.get('nome_usuario', "Usuário"),
        'clima_manha': clima_manha,
        'clima_tarde': clima_tarde,
        'temperatura': temperatura,
        'controle_chuva': controle_chuva,
        'funcionarios': funcionarios,
        'equipes': equipes,
        'observacoes_pessoal': observacoes_pessoal,
        'atividades': [],  # Será preenchido após processamento dos anexos
        'ocorrencias': [],  # Será preenchido após processamento dos anexos
        'recebimento_materiais_sim': recebimento_materiais_sim,
        'materiais_recebidos': materiais_recebidos if recebimento_materiais_sim else "",
        'necessidade_materiais_sim': necessidade_materiais_sim,
        'materiais_necessarios': materiais_necessarios if necessidade_materiais_sim else "",
        'materiais_urgentes': materiais_urgentes,
        'observacoes_gerais': observacoes_gerais,
        'fotos': []  # Será preenchido após processamento dos anexos
    }
    
    # Processar anexos das atividades
    for atividade in atividades:
        anexos_processados = []
        if 'anexos' in atividade and atividade['anexos']:
            for anexo in atividade['anexos']:
                if anexo is not None:
                    nome_arquivo = f"{id_relatorio}_atividade_{atividade['descricao'][:10]}_{anexo.name}"
                    caminho_anexo = salvar_anexo(anexo, nome_arquivo)
                    anexos_processados.append(caminho_anexo)
        
        atividade_processada = {
            'descricao': atividade['descricao'],
            'status': atividade['status'],
            'responsavel': atividade.get('responsavel', ""),
            'anexos': anexos_processados
        }
        
        relatorio['atividades'].append(atividade_processada)
    
    # Processar anexos das ocorrências
    for ocorrencia in ocorrencias:
        anexos_processados = []
        if 'anexos' in ocorrencia and ocorrencia['anexos']:
            for anexo in ocorrencia['anexos']:
                if anexo is not None:
                    nome_arquivo = f"{id_relatorio}_ocorrencia_{ocorrencia['descricao'][:10]}_{anexo.name}"
                    caminho_anexo = salvar_anexo(anexo, nome_arquivo)
                    anexos_processados.append(caminho_anexo)
        
        ocorrencia_processada = {
            'descricao': ocorrencia['descricao'],
            'gravidade': ocorrencia['gravidade'],
            'resolucao': ocorrencia.get('resolucao', ""),
            'anexos': anexos_processados
        }
        
        relatorio['ocorrencias'].append(ocorrencia_processada)
    
    # Processar fotos gerais
    if fotos_gerais:
        for foto in fotos_gerais:
            nome_arquivo = f"{id_relatorio}_foto_geral_{foto.name}"
            caminho_foto = salvar_anexo(foto, nome_arquivo)
            relatorio['fotos'].append(caminho_foto)
    
    # Salvar o relatório
    relatorios = carregar_relatorios()
    relatorios[id_relatorio] = relatorio
    salvar_relatorios(relatorios)
    
    return id_relatorio

def limpar_estado_sessao():
    """Limpa o estado da sessão após salvar o relatório"""
    st.session_state.atividades = [{
        'descricao': '',
        'status': 'Em Andamento',
        'responsavel': '',
        'anexos': []
    }]
    st.session_state.ocorrencias = []
    st.session_state.recebimento_materiais = False
    st.session_state.necessidade_materiais = False
    st.session_state.materiais_urgentes = False

def gerar_pdf_rdo(id_relatorio):
    """Gera um PDF do relatório"""
    relatorios = carregar_relatorios()
    if id_relatorio not in relatorios:
        st.error("Relatório não encontrado!")
        return None
       
    relatorio = relatorios[id_relatorio]
    
    # Criar o PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Configurar fonte
    pdf.set_font("Arial", size=12)
    
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RDO - RELATÓRIO DIÁRIO DE OBRA", ln=True, align='C')
    pdf.ln(5)
    
    # Informações básicas
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"RDO Nº {relatorio['numero_rdo']} - {relatorio['obra']}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, f"Data: {relatorio['data_relatorio']} | Criado por: {relatorio['nome_usuario_criacao']}", ln=True)
    pdf.ln(5)
    
    # Informações da Obra
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Informações da Obra", ln=True)
    pdf.set_font("Arial", size=10)
    
    obras = carregar_obras()
    if relatorio['obra'] in obras:
        obra_info = obras[relatorio['obra']]
        pdf.cell(100, 8, f"Data de Início: {obra_info.get('data_inicio', 'N/A')}", ln=True)
        pdf.cell(100, 8, f"Prazo da Obra: {obra_info.get('prazo', 'N/A')}", ln=True)
        pdf.cell(100, 8, f"Etapa Atual: {obra_info.get('etapa_atual', 'N/A')}", ln=True)
        pdf.cell(100, 8, f"Endereço: {obra_info.get('endereco', 'N/A')}", ln=True)
        pdf.cell(100, 8, f"Nº RRT de SI: {obra_info.get('rrt', 'N/A')}", ln=True)
        pdf.cell(100, 8, f"RT Principal: {obra_info.get('responsavel_principal', 'N/A')}", ln=True)
        pdf.cell(100, 8, f"RT Acompanhamento: {obra_info.get('responsavel_acompanhamento', 'N/A')}", ln=True)
    
    pdf.ln(5)
    
    # Clima
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Condições Climáticas", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 8, f"Clima Manhã: {relatorio['clima_manha']}", ln=True)
    pdf.cell(100, 8, f"Clima Tarde: {relatorio['clima_tarde']}", ln=True)
    pdf.cell(100, 8, f"Temperatura: {relatorio.get('temperatura', 'N/A')}°C", ln=True)
    
    # Controle de chuva
    pdf.cell(100, 8, "Controle de Chuva:", ln=True)
    controle_text = ""
    for hora, choveu in relatorio.get('controle_chuva', {}).items():
        if choveu:
            controle_text += f"{hora} "
    pdf.cell(100, 8, f"Horários com chuva: {controle_text if controle_text else 'Nenhum'}", ln=True)
    
    pdf.ln(5)
    
    # Equipes
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Equipes na Obra", ln=True)
    pdf.set_font("Arial", size=10)
    
    # Funcionários
    funcionarios = carregar_funcionarios()
    pdf.cell(100, 8, "Funcionários:", ln=True)
    for func_id in relatorio.get('funcionarios', []):
        if func_id in funcionarios:
            pdf.cell(100, 6, f"- {funcionarios[func_id].get('nome', func_id)}", ln=True)
    
    # Equipes
    pdf.cell(100, 8, "Equipes:", ln=True)
    for equipe in relatorio.get('equipes', []):
        pdf.cell(100, 6, f"- {equipe}", ln=True)
    
    if relatorio.get('observacoes_pessoal'):
        pdf.cell(100, 8, "Observações:", ln=True)
        pdf.multi_cell(180, 6, relatorio['observacoes_pessoal'])
    
    pdf.ln(5)
    
    # Atividades
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Atividades do Dia", ln=True)
    pdf.set_font("Arial", size=10)
    
    for i, atividade in enumerate(relatorio.get('atividades', [])):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(100, 8, f"Atividade {i+1}:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(100, 6, f"Descrição: {atividade['descricao']}", ln=True)
        pdf.cell(100, 6, f"Status: {atividade['status']}", ln=True)
        pdf.cell(100, 6, f"Responsável: {atividade.get('responsavel', 'N/A')}", ln=True)
        
        # Anexos (apenas menção, não é possível incluir imagens facilmente com FPDF)
        if atividade.get('anexos'):
            pdf.cell(100, 6, f"Anexos: {len(atividade['anexos'])} arquivos", ln=True)
    
    pdf.ln(5)
    
    # Ocorrências
    if relatorio.get('ocorrencias'):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "Ocorrências", ln=True)
        pdf.set_font("Arial", size=10)
        
        for i, ocorrencia in enumerate(relatorio['ocorrencias']):
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(100, 8, f"Ocorrência {i+1}:", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.cell(100, 6, f"Descrição: {ocorrencia['descricao']}", ln=True)
            pdf.cell(100, 6, f"Gravidade: {ocorrencia['gravidade']}", ln=True)
            pdf.cell(100, 6, f"Resolução: {ocorrencia.get('resolucao', 'N/A')}", ln=True)
            
            # Anexos
            if ocorrencia.get('anexos'):
                pdf.cell(100, 6, f"Anexos: {len(ocorrencia['anexos'])} arquivos", ln=True)
        
        pdf.ln(5)
    
    # Materiais
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Materiais", ln=True)
    pdf.set_font("Arial", size=10)
    
    # Recebimento
    if relatorio.get('recebimento_materiais_sim'):
        pdf.cell(100, 8, "Recebimento de materiais: Sim", ln=True)
        pdf.multi_cell(180, 6, relatorio.get('materiais_recebidos', 'Não especificado'))
    else:
        pdf.cell(100, 8, "Recebimento de materiais: Não", ln=True)
    
    # Necessidade
    if relatorio.get('necessidade_materiais_sim'):
        pdf.cell(100, 8, "Necessidade de materiais: Sim", ln=True)
        pdf.multi_cell(180, 6, relatorio.get('materiais_necessarios', 'Não especificado'))
        if relatorio.get('materiais_urgentes'):
            pdf.set_text_color(255, 0, 0) # Vermelho para urgência
            pdf.cell(100, 8, "URGENTE: Necessário nas próximas 48 horas", ln=True)
            pdf.set_text_color(0, 0, 0) # Voltar para preto
    else:
        pdf.cell(100, 8, "Necessidade de materiais: Não", ln=True)
    
    pdf.ln(5)
    
    # Observações gerais
    if relatorio.get('observacoes_gerais'):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "Observações Gerais", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(180, 6, relatorio['observacoes_gerais'])
    
    # Fotos (menção apenas)
    if relatorio.get('fotos') and len(relatorio['fotos']) > 0:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "Relatório Fotográfico", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(100, 8, f"Total de arquivos: {len(relatorio['fotos'])}", ln=True)
    
    # Salvar PDF
    pdf_filename = f"RDO_{relatorio['numero_rdo']}_{relatorio['obra']}.pdf"
    pdf_path = os.path.join("arquivos", "pdfs", pdf_filename)
    
    # Garantir que o diretório existe
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    pdf.output(pdf_path)
    return pdf_path

def visualizar_relatorios():
    """Interface para visualizar os relatórios existentes"""
    st.title("Visualizar Relatórios")
    
    relatorios = carregar_relatorios()
    if not relatorios:
        st.warning("Nenhum relatório encontrado.")
        return
    
    # Ordenar relatórios por data (mais recente primeiro)
    relatorios_ordenados = sorted(
        relatorios.items(),
        key=lambda x: datetime.strptime(x[1].get('data_criacao', '2000-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S"),
        reverse=True
    )
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_obra = st.selectbox(
            "Filtrar por Obra:",
            options=["Todas"] + list(set(r[1]['obra'] for r in relatorios_ordenados))
        )
    
    with col2:
        # Extrair todas as datas únicas e ordená-las
        todas_datas = sorted(list(set(r[1]['data_relatorio'] for r in relatorios_ordenados)), reverse=True)
        filtro_data = st.selectbox(
            "Filtrar por Data:",
            options=["Todas"] + todas_datas
        )
    
    # Aplicar filtros
    relatorios_filtrados = relatorios_ordenados
    if filtro_obra != "Todas":
        relatorios_filtrados = [r for r in relatorios_filtrados if r[1]['obra'] == filtro_obra]
    
    if filtro_data != "Todas":
        relatorios_filtrados = [r for r in relatorios_filtrados if r[1]['data_relatorio'] == filtro_data]
    
    # Lista de relatórios
    st.subheader("Relatórios Disponíveis")
    for id_relatorio, relatorio in relatorios_filtrados:
        with st.expander(f"RDO Nº {relatorio.get('numero_rdo', 'N/A')} - {relatorio['obra']} - {relatorio['data_relatorio']}"):
            # Exibir detalhes resumidos
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**Obra:** {relatorio['obra']}")
                st.write(f"**Data:** {relatorio['data_relatorio']}")
            with col2:
                st.write(f"**Clima Manhã:** {relatorio['clima_manha']}")
                st.write(f"**Clima Tarde:** {relatorio['clima_tarde']}")
            with col3:
                # Botão para visualizar detalhes completos
                if st.button("Ver Detalhes", key=f"ver_{id_relatorio}"):
                    st.session_state.visualizar_id = id_relatorio
                    st.rerun()
                
                # Botão para baixar PDF
                if st.button("Gerar PDF", key=f"pdf_{id_relatorio}"):
                    pdf_path = gerar_pdf_rdo(id_relatorio)
                    if pdf_path:
                        with open(pdf_path, "rb") as file:
                            st.download_button(
                                label="Baixar PDF",
                                data=file,
                                file_name=f"RDO_{relatorio['numero_rdo']}_{relatorio['obra']}.pdf",
                                mime="application/pdf",
                                key=f"download_{id_relatorio}"
                            )
    
    # Visualizar relatório específico
    if 'visualizar_id' in st.session_state and st.session_state.visualizar_id:
        id_relatorio = st.session_state.visualizar_id
        if id_relatorio in relatorios:
            exibir_detalhes_relatorio(id_relatorio, relatorios[id_relatorio], carregar_funcionarios())
            
            # Botão para voltar
            if st.button("Voltar para Lista"):
                st.session_state.visualizar_id = None
                st.rerun()

def exibir_detalhes_relatorio(id_relatorio, relatorio, funcionarios):
    """Exibe os detalhes de um relatório específico"""
    st.divider()
    st.subheader(f"RDO Nº {relatorio.get('numero_rdo', 'N/A')} - {relatorio['obra']}")
    st.caption(f"Data: {relatorio['data_relatorio']} | Criado por: {relatorio['nome_usuario_criacao']}")
    
    # Informações Básicas
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Clima Manhã:** {relatorio['clima_manha']}")
        st.write(f"**Clima Tarde:** {relatorio['clima_tarde']}")
        st.write(f"**Temperatura:** {relatorio.get('temperatura', 'N/A')}°C")
    
    with col2:
        # Controle de chuva
        st.write("**Controle de Chuva:**")
        if relatorio.get('controle_chuva'):
            horas_com_chuva = [hora for hora, choveu in relatorio['controle_chuva'].items() if choveu]
            if horas_com_chuva:
                st.write(f"Chovia às: {', '.join(horas_com_chuva)}")
            else:
                st.write("Sem chuva registrada")
    
    # Equipes
    st.write("### Equipes na Obra")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Funcionários:**")
        for func_id in relatorio.get('funcionarios', []):
            if func_id in funcionarios:
                st.write(f"- {funcionarios[func_id].get('nome', func_id)}")
            else:
                st.write(f"- {func_id}")
    
    with col2:
        st.write("**Equipes:**")
        for equipe in relatorio.get('equipes', []):
            st.write(f"- {equipe}")
    
    if relatorio.get('observacoes_pessoal'):
        st.write("**Observações sobre Pessoal:**")
        st.write(relatorio['observacoes_pessoal'])
    
    # Atividades
    st.write("### Atividades do Dia")
    for i, atividade in enumerate(relatorio.get('atividades', [])):
        with st.expander(f"Atividade {i+1}: {atividade['descricao'][:50]}..."):
            st.write(f"**Descrição:** {atividade['descricao']}")
            st.write(f"**Status:** {atividade['status']}")
            st.write(f"**Responsável:** {atividade.get('responsavel', 'N/A')}")
            
            # Exibir anexos
            if atividade.get('anexos') and len(atividade['anexos']) > 0:
                st.write("**Anexos:**")
                for anexo in atividade['anexos']:
                    nome_arquivo = os.path.basename(anexo)
                    if anexo.lower().endswith(('.png', '.jpg', '.jpeg')):
                        try:
                            imagem = Image.open(anexo)
                            st.image(imagem, caption=nome_arquivo, width=300)
                        except:
                            st.write(f"Não foi possível exibir a imagem: {nome_arquivo}")
                    else:
                        st.write(f"Anexo: {nome_arquivo}")
    
    # Ocorrências
    if relatorio.get('ocorrencias') and len(relatorio['ocorrencias']) > 0:
        st.write("### Ocorrências")
        for i, ocorrencia in enumerate(relatorio['ocorrencias']):
            gravidade = ocorrencia['gravidade']
            cor = "green"
            if gravidade == "Média":
                cor = "orange"
            elif gravidade in ["Alta", "Crítica"]:
                cor = "red"
            
            with st.expander(f"Ocorrência {i+1}: {ocorrencia['descricao'][:50]}..."):
                st.write(f"**Descrição:** {ocorrencia['descricao']}")
                st.markdown(f"**Gravidade:** <span style='color:{cor}'>{gravidade}</span>", unsafe_allow_html=True)
                st.write(f"**Resolução/Encaminhamento:** {ocorrencia.get('resolucao', 'N/A')}")
                
                # Exibir anexos
                if ocorrencia.get('anexos') and len(ocorrencia['anexos']) > 0:
                    st.write("**Anexos:**")
                    for anexo in ocorrencia['anexos']:
                        nome_arquivo = os.path.basename(anexo)
                        if anexo.lower().endswith(('.png', '.jpg', '.jpeg')):
                            try:
                                imagem = Image.open(anexo)
                                st.image(imagem, caption=nome_arquivo, width=300)
                            except:
                                st.write(f"Não foi possível exibir a imagem: {nome_arquivo}")
                        else:
                            st.write(f"Anexo: {nome_arquivo}")
    
    # Materiais
    st.write("### Materiais")
    
    # Recebimento de materiais
    if relatorio.get('recebimento_materiais_sim'):
        st.write("**Recebimento de Materiais:** Sim")
        st.write(relatorio.get('materiais_recebidos', 'Não especificado'))
    else:
        st.write("**Recebimento de Materiais:** Não")
    
    # Necessidade de materiais
    if relatorio.get('materiais_necessarios_sim'):
        st.write("**Materiais Necessários:**")
        st.write(relatorio.get('materiais_necessarios', 'Não especificado'))
        if relatorio.get('materiais_urgentes'):
            st.error("**URGENTE: Necessário nas próximas 48 horas**")
    else:
        st.write("**Não há necessidade de materiais.**")
    
    # Fotos da Obra
    if relatorio.get('fotos') and len(relatorio['fotos']) > 0:
        st.write("### Fotos da Obra")
        # Criar galeria de fotos
        colunas = st.columns(3)
        for i, foto_path in enumerate(relatorio['fotos']):
            try:
                if foto_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    with colunas[i % 3]:
                        imagem = Image.open(foto_path)
                        st.image(imagem, caption=os.path.basename(foto_path), use_column_width=True)
                else:
                    with colunas[i % 3]:
                        st.write(f"Documento: {os.path.basename(foto_path)}")
            except:
                with colunas[i % 3]:
                    st.write(f"Não foi possível exibir: {os.path.basename(foto_path)}")
    
    # Observações Gerais
    if relatorio.get('observacoes_gerais'):
        st.write("### Observações Gerais")
        st.write(relatorio['observacoes_gerais'])
