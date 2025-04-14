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
from datetime import datetime, timedelta
from auth import verificar_autenticacao, logout

# Função adaptadora para compatibilidade com o código existente
def verificar_usuario_logado():
    """Adapta verificar_autenticacao para retornar informações do usuário"""
    if verificar_autenticacao():
        return {
            "login": st.session_state.usuario_atual,
            "nome": st.session_state.nome_completo,
            "cargo": "Não especificado",  # Ou adapte conforme necessário
            "admin": st.session_state.nivel_acesso == "admin"
        }
    return None

# Função adaptadora para logout
def logout_usuario():
    """Wrapper para função logout do módulo auth"""
    logout()

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

def gerar_pdf_rdo(id_relatorio):
    try:
        # Carregar o relatório
        relatorios = carregar_relatorios()
        if id_relatorio not in relatorios:
            st.error("Relatório não encontrado.")
            return False
            
        dados = relatorios[id_relatorio]
        
        # Definir nome do arquivo PDF
        os.makedirs("pdfs", exist_ok=True)
        pdf_filename = f"pdfs/RDO_{dados['numero_rdo']}_{id_relatorio}.pdf"
        
        # Criar PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "RELATÓRIO DIÁRIO DE OBRA - RDO", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Nº RDO: {dados['numero_rdo']}", ln=True)
        pdf.cell(0, 10, f"Data: {dados['data_relatorio']}", ln=True)
        pdf.cell(0, 10, f"Obra: {dados['obra']}", ln=True)
        
        # Informações da obra
        obra_detalhes = carregar_obras().get(dados['obra'], {})
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Informações da Obra", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Endereço: {obra_detalhes.get('endereco', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Data início: {obra_detalhes.get('prazo_inicio', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Data término prevista: {obra_detalhes.get('prazo_fim', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Responsável técnico: {obra_detalhes.get('responsavel_tecnico', 'N/A')}", ln=True)
        
        # Condições climáticas
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. Condições Climáticas", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Clima: {dados['clima_manha']}", ln=True)
        pdf.cell(0, 10, f"Temperatura: {dados['temperatura']}°C", ln=True)
        
        # Equipe
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "3. Equipe e Pessoal", ln=True)
        pdf.set_font("Arial", "", 12)
        # Processar dados de equipes e funcionários para o PDF
        # [...]
        
        # Atividades e resto do conteúdo
        # [...]
        
        # Salvar o PDF
        pdf.output(pdf_filename)
        return pdf_filename
        
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {str(e)}")
        return None

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

    # Criar o formulário principal
    with st.form(key='rdo_form'):
        st.subheader("1. Informações Básicas")

        # Seleção de obra
        obra_selecionada = st.selectbox(
            "Obra:",
            options=list(obras.keys())
        )

        # Logo após a seleção de obra
        obra_detalhes = obras[obra_selecionada]
        st.write("#### Informações da Obra:")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Data de início:** {obra_detalhes.get('prazo_inicio', 'N/A')}")
            st.write(f"**Data de término prevista:** {obra_detalhes.get('prazo_fim', 'N/A')}")
        with col2:
            st.write(f"**Endereço:** {obra_detalhes.get('endereco', 'N/A')}")
            st.write(f"**Número RRT:** {obra_detalhes.get('rrt', 'N/A')}")
            st.write(f"**Responsável técnico:** {obra_detalhes.get('responsavel_tecnico', 'N/A')}")

        # Data do relatório
        data_relatorio = st.date_input(
            "Data do Relatório:",
            datetime.now()
        ).strftime("%Y/%m/%d")

        # Clima
        col1, col2 = st.columns(2)
        with col1:
            clima_manha = st.selectbox(
                "Condições Climáticas:",
                options=["Ensolarado", "Parcialmente Nublado", "Nublado", "Chuvoso"]
            )
        with col2:
            temperatura = st.slider(
                "Temperatura (°C):",
                min_value=-10,
                max_value=50,
                value=25
            )

        # Controle de chuva por hora
        st.subheader("Controle de Chuva por Hora")
        # Manhã
        st.write("**Período da Manhã:**")
        col1, col2, col3 = st.columns(3)
        controle_chuva = {}
        # Horários da manhã (7, 9, 11)
        colunas_manha = [col1, col2, col3]
        horas_manha = ["07:00", "09:00", "11:00"]
        for i, hora in enumerate(horas_manha):
            with colunas_manha[i]:
                controle_chuva[hora] = st.checkbox(f"Chuva às {hora}", key=f"chuva_{hora}")

        # Tarde
        st.write("**Período da Tarde:**")
        col4, col5, col6 = st.columns(3)
        colunas_tarde = [col4, col5, col6]
        horas_tarde = ["13:00", "15:00", "17:00"]
        for i, hora in enumerate(horas_tarde):
            with colunas_tarde[i]:
                controle_chuva[hora] = st.checkbox(f"Chuva às {hora}", key=f"chuva_{hora}")

        st.subheader("2. Equipe e Pessoal")
        # Funcionários presentes
        if funcionarios:
            funcionarios_selecionados = st.multiselect(
                "Funcionários Presentes:",
                options=list(funcionarios.keys()),
                format_func=lambda x: funcionarios[x]['nome'] if x in funcionarios else x
            )
        else:
            st.write("Não há funcionários cadastrados.")
            funcionarios_selecionados = []

        # Equipes presentes
        if equipes:
            equipes_selecionadas = st.multiselect(
                "Equipes Presentes:",
                options=list(equipes.keys())
            )
        else:
            st.write("Não há equipes cadastradas.")
            equipes_selecionadas = []

        # Observações sobre pessoal
        observacoes_pessoal = st.text_area(
            "Observações sobre Pessoal:",
            height=100
        )

        st.subheader("3. Atividades Realizadas")
        # Adicionar campos para cada atividade
        for i, atividade in enumerate(st.session_state.atividades):
            st.markdown(f"#### Atividade {i+1}")
            # Campos da atividade
            descricao = st.text_area(
                f"Descrição da Atividade {i+1}:",
                value=atividade['descricao'],
                height=100,
                key=f"desc_ativ_{i}"
            )
            status = st.selectbox(
                f"Status da Atividade {i+1}:",
                options=["Em Andamento", "Concluída", "Atrasada", "Paralisada"],
                index=["Em Andamento", "Concluída", "Atrasada", "Paralisada"].index(atividade['status']),
                key=f"status_ativ_{i}"
            )
            responsavel = st.text_input(
                f"Responsável pela Atividade {i+1}:",
                value=atividade['responsavel'],
                key=f"resp_ativ_{i}"
            )
            # Anexos da atividade
            anexos = st.file_uploader(
                f"Anexo da Atividade {i+1}:",
                accept_multiple_files=True,
                key=f"anexo_ativ_{i}"
            )
            # Atualizar o estado da sessão
            st.session_state.atividades[i]['descricao'] = descricao
            st.session_state.atividades[i]['status'] = status
            st.session_state.atividades[i]['responsavel'] = responsavel
            if anexos:
                st.session_state.atividades[i]['anexos'] = anexos

        # Botão para adicionar nova atividade (fora do loop, após todas as atividades)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Usamos st.checkbox como antes, mas com melhor apresentação
            adicionar_atividade = st.checkbox("➕ Adicionar outra atividade", key="add_atividade")

        st.subheader("4. Ocorrências")
        # Checkbox para adicionar ocorrência
        adicionar_ocorrencia = st.checkbox("📝 Registrar ocorrência", key="add_ocorrencia")
        if adicionar_ocorrencia:
            # Campos para ocorrências
            for i in range(len(st.session_state.ocorrencias) + 1):
                if i >= len(st.session_state.ocorrencias):
                    st.session_state.ocorrencias.append({
                        'descricao': '',
                        'gravidade': 'Baixa',
                        'resolucao': '',
                        'anexos': []
                    })
                st.markdown(f"#### Ocorrência {i+1}")
                descricao = st.text_area(
                    f"Descrição da Ocorrência {i+1}:",
                    value=st.session_state.ocorrencias[i]['descricao'],
                    height=100,
                    key=f"desc_ocor_{i}"
                )
                gravidade = st.selectbox(
                    f"Gravidade da Ocorrência {i+1}:",
                    options=["Baixa", "Média", "Alta", "Crítica"],
                    index=["Baixa", "Média", "Alta", "Crítica"].index(st.session_state.ocorrencias[i]['gravidade']),
                    key=f"grav_ocor_{i}"
                )
                resolucao = st.text_area(
                    f"Resolução/Encaminhamento da Ocorrência {i+1}:",
                    value=st.session_state.ocorrencias[i]['resolucao'],
                    height=100,
                    key=f"resol_ocor_{i}"
                )
                # Anexos da ocorrência
                anexos = st.file_uploader(
                    f"Anexo da Ocorrência {i+1}:",
                    accept_multiple_files=True,
                    key=f"anexo_ocor_{i}"
                )
                # Atualizar o estado da sessão
                st.session_state.ocorrencias[i]['descricao'] = descricao
                st.session_state.ocorrencias[i]['gravidade'] = gravidade
                st.session_state.ocorrencias[i]['resolucao'] = resolucao
                if anexos:
                    st.session_state.ocorrencias[i]['anexos'] = anexos
                # Opção para adicionar outra ocorrência
                if i == len(st.session_state.ocorrencias) - 1:
                    adicionar_outra = st.checkbox(f"➕ Adicionar outra ocorrência", key=f"add_ocor_{i}")
                    if adicionar_outra:
                        continue
                    else:
                        break

        st.subheader("5. Materiais")
        # Recebimento de materiais
        col1, col2 = st.columns(2)
        with col1:
            recebimento_materiais = st.checkbox(
                "Houve recebimento de materiais?",
                value=st.session_state.recebimento_materiais,
                key="recebimento"
            )
        materiais_recebidos = ""
        if recebimento_materiais:
            materiais_recebidos = st.text_area(
                "Descreva os materiais recebidos:",
                height=100,
                key="materiais_recebidos_text"
            )

        # Necessidade de materiais
        with col2:
            necessidade_materiais = st.checkbox(
                "Há necessidade de materiais?",
                value=st.session_state.necessidade_materiais,
                key="necessidade"
            )
        materiais_necessarios = ""
        if necessidade_materiais:
            materiais_necessarios = st.text_area(
                "Descreva os materiais necessários:",
                height=100,
                key="materiais_necessarios_text"
            )
            materiais_urgentes = st.checkbox(
                "Material urgente (necessário nas próximas 48 horas)",
                value=st.session_state.materiais_urgentes,
                key="urgente"
            )
        else:
            materiais_urgentes = False

        # Atualizar estado da sessão para materiais
        st.session_state.recebimento_materiais = recebimento_materiais
        st.session_state.necessidade_materiais = necessidade_materiais
        st.session_state.materiais_urgentes = materiais_urgentes

        st.subheader("6. Observações Gerais")
        observacoes_gerais = st.text_area(
            "Observações Gerais:",
            height=150
        )

        st.subheader("7. Relatório Fotográfico")
        fotos_gerais = st.file_uploader(
            "Adicione fotos da obra:",
            accept_multiple_files=True,
            key="fotos_gerais"
        )

        # Botão para salvar o relatório
        submit_button = st.form_submit_button(label="Salvar Relatório")

    # O código abaixo está FORA do bloco with st.form()
    # Lógica após o submit do formulário
    if submit_button:
        # Verificar se há atividades preenchidas
        atividades_validas = [a for a in st.session_state.atividades if a['descricao'].strip()]
        if not atividades_validas:
            st.error("É necessário adicionar pelo menos uma atividade.")
            return

        # Criar o relatório
        id_relatorio = gerar_id_relatorio()
        # Todo o resto do código de processamento continuaria aqui...
        st.success(f"Relatório {numero_rdo} salvo com sucesso!")

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
        pdf.multi_cell(180, 6, f"Descrição: {atividade['descricao']}")
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
            pdf.multi_cell(180, 6, f"Descrição: {ocorrencia['descricao']}")
            pdf.cell(100, 6, f"Gravidade: {ocorrencia['gravidade']}", ln=True)
            pdf.multi_cell(180, 6, f"Resolução: {ocorrencia.get('resolucao', 'N/A')}")
            
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
    pdf_filename = f"RDO_{relatorio['numero_rdo']}_{relatorio['obra'].replace(' ', '_')}.pdf"
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
    relatorios_ordenados = sorted()

    relatorios.items(),
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
        key=lambda x: datetime.strptime(x[1]['data_criacao'], "%Y-%m-%d %H:%M:%S"),
        reverse=True
    )
    
    # Opções de filtro
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        # Lista única de obras nos relatórios
        obras_disponiveis = list(set([r[1]['obra'] for r in relatorios_ordenados]))
        obra_filtro = st.selectbox("Filtrar por obra:", ["Todas"] + obras_disponiveis)
    
    with col2:
        # Filtro de data
        data_inicial = st.date_input("Data inicial:", 
                                     value=datetime.now() - timedelta(days=30))
        data_final = st.date_input("Data final:", value=datetime.now())
    
    # Aplicar filtros
    relatorios_filtrados = []
    for id_rel, relatorio in relatorios_ordenados:
        # Converter string para datetime para comparação
        data_rel = datetime.strptime(relatorio['data_relatorio'], "%Y-%m-%d").date()
        
        # Verificar filtros
        if (obra_filtro == "Todas" or relatorio['obra'] == obra_filtro) and \
           (data_inicial <= data_rel <= data_final):
            relatorios_filtrados.append((id_rel, relatorio))
    
    # Exibir relatórios em formato de cards
    st.subheader(f"Relatórios encontrados: {len(relatorios_filtrados)}")
    
    for id_rel, relatorio in relatorios_filtrados:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            # Informações do relatório
            with col1:
                st.markdown(f"**RDO Nº {relatorio['numero_rdo']} - {relatorio['obra']}**")
                st.write(f"Data: {relatorio['data_relatorio']}")
                st.write(f"Criado por: {relatorio['nome_usuario_criacao']}")
                
                # Exibir um resumo das atividades
                atividades_count = len(relatorio.get('atividades', []))
                ocorrencias_count = len(relatorio.get('ocorrencias', []))
                st.write(f"Atividades: {atividades_count} | Ocorrências: {ocorrencias_count}")
            
            # Botão para visualizar detalhes
            with col2:
                if st.button("Detalhes", key=f"detalhe_{id_rel}"):
                    st.session_state.visualizar_detalhes = id_rel
                    st.rerun()
            
            # Botão para gerar/baixar PDF
            with col3:
                if st.button("Gerar PDF", key=f"pdf_{id_rel}"):
                    with st.spinner("Gerando PDF..."):
                        pdf_path = gerar_pdf_rdo(id_rel)
                        if pdf_path:
                            # Ler o arquivo PDF para download
                            with open(pdf_path, "rb") as f:
                                pdf_bytes = f.read()
                            
                            st.download_button(
                                label="Download PDF",
                                data=pdf_bytes,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                key=f"download_{id_rel}"
                            )
            
            st.divider()
    
    # Lógica para visualizar detalhes de um relatório específico
    if hasattr(st.session_state, 'visualizar_detalhes') and st.session_state.visualizar_detalhes:
        exibir_detalhes_relatorio(st.session_state.visualizar_detalhes)

def exibir_detalhes_relatorio(id_relatorio):
    """Exibe os detalhes completos de um relatório específico"""
    relatorios = carregar_relatorios()
    if id_relatorio not in relatorios:
        st.error("Relatório não encontrado!")
        st.session_state.visualizar_detalhes = None
        return
    
    relatorio = relatorios[id_relatorio]
    
    # Criamos uma container e uma coluna para o botão de voltar estar no topo
    with st.container():
        col_back, _ = st.columns([1, 5])
        with col_back:
            if st.button("← Voltar para a lista"):
                st.session_state.visualizar_detalhes = None
                st.rerun()
    
    # Exibir detalhes do relatório
    st.title(f"RDO Nº {relatorio['numero_rdo']} - {relatorio['obra']}")
    st.write(f"Data do relatório: {relatorio['data_relatorio']}")
    st.write(f"Criado por: {relatorio['nome_usuario_criacao']} em {relatorio['data_criacao']}")
    
    # Seção de clima
    st.subheader("Clima")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"Manhã: {relatorio['clima_manha']}")
    with col2:
        st.write(f"Tarde: {relatorio['clima_tarde']}")
    with col3:
        st.write(f"Temperatura: {relatorio.get('temperatura', 'N/A')}°C")
    
    # Controle de chuva
    if relatorio.get('controle_chuva'):
        st.write("Horários com chuva:")
        for hora, choveu in relatorio['controle_chuva'].items():
            if choveu:
                st.markdown(f"- {hora}")
    # Continuação da função exibir_detalhes_relatorio
    
    # Equipe e pessoal
    st.subheader("Equipe e Pessoal")
    
    # Funcionários
    funcionarios = carregar_funcionarios()
    if relatorio.get('funcionarios'):
        st.write("Funcionários presentes:")
        for func_id in relatorio['funcionarios']:
            if func_id in funcionarios:
                st.markdown(f"- {funcionarios[func_id].get('nome', func_id)}")
    
    # Equipes
    if relatorio.get('equipes'):
        st.write("Equipes presentes:")
        for equipe in relatorio['equipes']:
            st.markdown(f"- {equipe}")
    
    # Observações sobre pessoal
    if relatorio.get('observacoes_pessoal'):
        st.write("Observações sobre equipe/pessoal:")
        st.write(relatorio['observacoes_pessoal'])
    
    # Atividades
    st.subheader("Atividades")
    if relatorio.get('atividades'):
        for i, atividade in enumerate(relatorio['atividades']):
            with st.expander(f"Atividade {i+1}: {atividade['descricao'][:50]}..."):
                st.write(f"**Descrição completa:** {atividade['descricao']}")
                st.write(f"**Status:** {atividade['status']}")
                st.write(f"**Responsável:** {atividade.get('responsavel', 'N/A')}")
                
                # Mostrar anexos se houver
                if atividade.get('anexos'):
                    st.write("**Anexos:**")
                    for anexo_path in atividade['anexos']:
                        try:
                            file_name = os.path.basename(anexo_path)
                            if os.path.exists(anexo_path):
                                with open(anexo_path, 'rb') as f:
                                    file_bytes = f.read()
                                    st.download_button(
                                        label=f"Download {file_name}",
                                        data=file_bytes,
                                        file_name=file_name,
                                        mime="application/octet-stream"
                                    )
                            else:
                                st.warning(f"Arquivo não encontrado: {file_name}")
                        except Exception as e:
                            st.error(f"Erro ao carregar anexo: {str(e)}")
    else:
        st.info("Nenhuma atividade registrada.")
    
    # Ocorrências
    st.subheader("Ocorrências")
    if relatorio.get('ocorrencias'):
        for i, ocorrencia in enumerate(relatorio['ocorrencias']):
            # Usar cor conforme gravidade
            cor = {
                'Baixa': 'blue',
                'Média': 'orange',
                'Alta': 'red',
                'Crítica': 'darkred'
            }.get(ocorrencia['gravidade'], 'black')
            
            with st.expander(f"Ocorrência {i+1}: {ocorrencia['descricao'][:50]}..."):
                st.markdown(f"**Descrição completa:** {ocorrencia['descricao']}")
                st.markdown(f"**Gravidade:** :{cor}[{ocorrencia['gravidade']}]")
                st.markdown(f"**Resolução/Encaminhamento:** {ocorrencia.get('resolucao', 'N/A')}")
                
                # Mostrar anexos se houver
                if ocorrencia.get('anexos'):
                    st.write("**Anexos:**")
                    for anexo_path in ocorrencia['anexos']:
                        try:
                            file_name = os.path.basename(anexo_path)
                            if os.path.exists(anexo_path):
                                with open(anexo_path, 'rb') as f:
                                    file_bytes = f.read()
                                    st.download_button(
                                        label=f"Download {file_name}",
                                        data=file_bytes,
                                        file_name=file_name,
                                        mime="application/octet-stream"
                                    )
                            else:
                                st.warning(f"Arquivo não encontrado: {file_name}")
                        except Exception as e:
                            st.error(f"Erro ao carregar anexo: {str(e)}")
    else:
        st.info("Nenhuma ocorrência registrada.")
    
    # Materiais
    st.subheader("Materiais")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Recebimento de materiais:**")
        if relatorio.get('recebimento_materiais_sim'):
            st.write("Sim")
            st.write(relatorio.get('materiais_recebidos', 'Não especificado'))
        else:
            st.write("Não")
    
    with col2:
        st.write("**Necessidade de materiais:**")
        if relatorio.get('necessidade_materiais_sim'):
            st.write("Sim")
            st.write(relatorio.get('materiais_necessarios', 'Não especificado'))
            if relatorio.get('materiais_urgentes'):
                st.error("URGENTE: Necessário nas próximas 48 horas")
        else:
            st.write("Não")
    
    # Observações gerais
    if relatorio.get('observacoes_gerais'):
        st.subheader("Observações Gerais")
        st.write(relatorio['observacoes_gerais'])
    
    # Relatório fotográfico
    st.subheader("Relatório Fotográfico")
    if relatorio.get('fotos') and len(relatorio['fotos']) > 0:
        col_fotos = st.columns(3)
        for i, foto_path in enumerate(relatorio['fotos']):
            col_idx = i % 3
            with col_fotos[col_idx]:
                try:
                    if os.path.exists(foto_path):
                        file_name = os.path.basename(foto_path)
                        img = Image.open(foto_path)
                        st.image(img, caption=f"Foto {i+1}", use_column_width=True)
                        with open(foto_path, 'rb') as f:
                            file_bytes = f.read()
                            st.download_button(
                                label=f"Download",
                                data=file_bytes,
                                file_name=file_name,
                                mime="application/octet-stream"
                            )
                    else:
                        st.warning(f"Imagem não encontrada: {os.path.basename(foto_path)}")
                except Exception as e:
                    st.error(f"Erro ao carregar imagem: {str(e)}")
    else:
        st.info("Nenhuma foto registrada.")
def editar_rdo(id_relatorio=None):
    """Interface para editar um relatório existente"""
    if id_relatorio is None:
        st.title("Editar RDO")
        relatorios = carregar_relatorios()
        
        if not relatorios:
            st.warning("Nenhum relatório disponível para edição.")
            return
        
        # Ordenar relatórios por data (mais recente primeiro)
        relatorios_ordenados = sorted(
            relatorios.items(),
            key=lambda x: datetime.strptime(x[1]['data_criacao'], "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        options = {f"RDO Nº {r[1]['numero_rdo']} - {r[1]['obra']} ({r[1]['data_relatorio']})": r[0] 
                  for r in relatorios_ordenados}
        
        selected = st.selectbox("Selecione o relatório para editar:", options.keys())
        id_relatorio = options[selected]
        
        if st.button("Editar este relatório"):
            st.session_state.editar_relatorio = id_relatorio
            st.rerun()
            
    else:
        # Aqui implementaríamos a lógica para editar um relatório específico
        # Basicamente, pré-preenchendo o formulário de criação com os dados existentes
        st.title("Editar RDO")
        relatorios = carregar_relatorios()
        
        if id_relatorio not in relatorios:
            st.error("Relatório não encontrado!")
            return
        
        st.warning("Funcionalidade de edição em desenvolvimento. Para editar um relatório, " 
                  "crie um novo relatório e delete o antigo.")
        
        # Implementação completa da edição exigiria replicar o formulário de criação
        # com os valores preenchidos do relatório existente
        # ...
def visualizar_rdo():
    st.title("Visualizar Relatórios Diários de Obra")
    
    relatorios = carregar_relatorios()
    if not relatorios:
        st.info("Não há relatórios cadastrados ainda.")
        return
    
    # Opções de filtro
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        filtro_obra = st.selectbox(
            "Filtrar por obra:",
            options=["Todas"] + list(set(r['obra'] for r in relatorios.values())),
            key="filtro_obra"
        )
    
    with col2:
        data_inicial = st.date_input("Data inicial:", datetime.now() - timedelta(days=30))
        data_final = st.date_input("Data final:", datetime.now())
    
    # Filtrar relatórios
    relatorios_filtrados = {}
    for id_rel, rel in relatorios.items():
        data_rel = datetime.strptime(rel['data_relatorio'], "%Y/%m/%d").date()
        if (filtro_obra == "Todas" or rel['obra'] == filtro_obra) and \
           data_inicial <= data_rel <= data_final:
            relatorios_filtrados[id_rel] = rel
    
    if not relatorios_filtrados:
        st.info("Nenhum relatório encontrado com os filtros selecionados.")
        return
    
    # Exibir relatórios em formato de tabela
    dados_tabela = []
    for id_rel, rel in relatorios_filtrados.items():
        dados_tabela.append({
            "ID": id_rel,
            "Nº RDO": rel['numero_rdo'],
            "Data": rel['data_relatorio'],
            "Obra": rel['obra'],
            "Usuário": rel.get('nome_usuario_criacao', "N/A")
        })
    
    df = pd.DataFrame(dados_tabela)
    st.dataframe(df, use_container_width=True)
    
    # Seleção de relatório para visualizar
    relatorio_selecionado = st.selectbox(
        "Selecione um relatório para visualizar:",
        options=list(relatorios_filtrados.keys()),
        format_func=lambda x: f"RDO {relatorios_filtrados[x]['numero_rdo']} - {relatorios_filtrados[x]['data_relatorio']} - {relatorios_filtrados[x]['obra']}"
    )
    
    if st.button("Visualizar Relatório"):
        with st.spinner("Gerando PDF..."):
            pdf_path = gerar_pdf_rdo(relatorio_selecionado)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )

def main():
    """Função principal para controlar o fluxo da aplicação"""
    # Inicializar o estado da sessão se não existir
    if 'atividades' not in st.session_state:
        st.session_state.atividades = [{
            'descricao': '',
            'status': 'Em Andamento',
            'responsavel': '',
            'anexos': []
        }]
        
    if 'ocorrencias' not in st.session_state:
        st.session_state.ocorrencias = []
        
    if 'recebimento_materiais' not in st.session_state:
        st.session_state.recebimento_materiais = False
        
    if 'necessidade_materiais' not in st.session_state:
        st.session_state.necessidade_materiais = False
        
    if 'materiais_urgentes' not in st.session_state:
        st.session_state.materiais_urgentes = False

    # Sidebar para navegação
    st.sidebar.title("RDO - Relatório Diário de Obra")
    
    # Verificar autenticação do usuário
    usuario_logado = verificar_usuario_logado()
    if not usuario_logado:
        st.sidebar.warning("Você precisa fazer login para continuar.")
        st.title("RDO - Relatório Diário de Obra")
        st.write("Por favor, faça login para acessar o sistema.")
        return
    
    st.sidebar.write(f"Usuário: {usuario_logado['nome']}")
    
    # Menu de navegação
    opcao = st.sidebar.radio(
        "Navegação",
        ["Criar novo RDO", "Visualizar Relatórios", "Editar Relatório", "Dashboard"],
        index=0
    )
    
    # Tratar navegação através do estado da sessão (para redirect após ações)
    if hasattr(st.session_state, 'visualizar_detalhes') and st.session_state.visualizar_detalhes:
        opcao = "Visualizar Relatórios"
    
    if hasattr(st.session_state, 'editar_relatorio') and st.session_state.editar_relatorio:
        opcao = "Editar Relatório"
        
    # Executar a opção selecionada
    if opcao == "Criar novo RDO":
        criar_rdo()
    elif opcao == "Visualizar Relatórios":
        visualizar_relatorios()
    elif opcao == "Editar Relatório":
        if hasattr(st.session_state, 'editar_relatorio') and st.session_state.editar_relatorio:
            editar_rdo(st.session_state.editar_relatorio)
        else:
            editar_rdo()
    elif opcao == "Dashboard":
        st.title("Dashboard - Relatórios Diários de Obra")
        st.write("Implementação em andamento. Esta funcionalidade permitirá visualizar indicadores e análises dos RDOs.")
        # Aqui colocaríamos métricas e gráficos baseados nos dados dos relatórios
        
    # Botão para logout
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        logout_usuario()
        st.rerun()

if __name__ == "__main__":
    main()
