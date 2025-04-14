import streamlit as st
import pandas as pd
import os
import json
import uuid
import io
import base64
from datetime import datetime, date, timedelta
from PIL import Image
from fpdf import FPDF
from auth import verificar_autenticacao, logout
from data_manager import (
    carregar_obras, carregar_funcionarios, carregar_equipes, carregar_relatorios,
    salvar_relatorios, obter_caminho_anexo, salvar_anexo, processar_anexos_atividades,
    processar_anexos_ocorrencias, processar_fotos_gerais, excluir_anexos_relatorio,
    listar_anexos_relatorio
)

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
    
    numeros_existentes = []
    for r in relatorios.values():
        numero_rdo = r.get('numero_rdo')
        if numero_rdo is not None:
            # Se for string, converte para int se possível
            if isinstance(numero_rdo, str) and numero_rdo.isdigit():
                numeros_existentes.append(int(numero_rdo))
            # Se já for int, adiciona diretamente
            elif isinstance(numero_rdo, int):
                numeros_existentes.append(numero_rdo)
    
    if not numeros_existentes:
        return 1
    
    return max(numeros_existentes) + 1


def salvar_rdo(obra, data_relatorio, clima_manha, clima_tarde, temperatura,
               horarios_chuva_manha, horarios_chuva_tarde, equipe, equipamentos,
               obs_equipe, atividades, ocorrencias, recebimento_materiais_sim,
               materiais_recebidos, necessidade_materiais_sim, materiais_necessarios,
               materiais_urgentes, observacoes_gerais, usuario):
    """Salva o relatório no armazenamento"""
    try:
        # Carregar os relatórios existentes
        relatorios = carregar_relatorios()
        
        # Gerar ID único para o relatório
        id_relatorio = str(uuid.uuid4())
        
        # Definir número do RDO
        numero_rdo = gerar_numero_sequencial_rdo()
        
        # Garantir formato consistente da data (YYYY-MM-DD)
        if isinstance(data_relatorio, (datetime, date)):
            # Se for objeto datetime ou date, converter para string
            data_formatada = data_relatorio.strftime("%Y-%m-%d")
        else:
            # Se já for string, tentar converter para formato padronizado
            try:
                # Tentar interpretar como DD/MM/YYYY
                data_objeto = datetime.strptime(str(data_relatorio), "%d/%m/%Y")
                data_formatada = data_objeto.strftime("%Y-%m-%d")
            except ValueError:
                try:
                    # Tentar interpretar como YYYY-MM-DD
                    data_objeto = datetime.strptime(str(data_relatorio), "%Y-%m-%d")
                    data_formatada = data_relatorio  # Já está no formato correto
                except ValueError:
                    # Se falhar, usa como está (não ideal, mas evita erro)
                    data_formatada = str(data_relatorio)
                    
        # Criar o relatório
        relatorio = {
            'id': id_relatorio,
            'numero_rdo': numero_rdo,
            'obra': obra,
            'data_relatorio': data_formatada,  # Usa a data no formato padronizado
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'clima_manha': clima_manha,
            'clima_tarde': clima_tarde,
            'temperatura': temperatura,
            'horarios_chuva_manha': horarios_chuva_manha,
            'horarios_chuva_tarde': horarios_chuva_tarde,
            'equipe': equipe,
            'equipamentos': equipamentos,
            'obs_equipe': obs_equipe,
            'atividades': atividades,
            'ocorrencias': ocorrencias,
            'recebimento_materiais_sim': recebimento_materiais_sim,
            'materiais_recebidos': materiais_recebidos,
            'necessidade_materiais_sim': necessidade_materiais_sim,
            'materiais_necessarios': materiais_necessarios,
            'materiais_urgentes': materiais_urgentes,
            'observacoes_gerais': observacoes_gerais,
            'id_usuario_criacao': usuario['login'],
            'nome_usuario_criacao': usuario['nome']
        }
        
        # Adicionar o relatório
        relatorios[id_relatorio] = relatorio
        
        # Salvar os relatórios
        salvar_relatorios(relatorios)
        st.success(f"Relatório Nº {numero_rdo} salvo com sucesso!")
        return id_relatorio
    except Exception as e:
        st.error(f"Erro ao salvar o relatório: {str(e)}")
        return None


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
    """Interface para criar um novo relatório diário de obra"""
    st.title("RDO - RELATÓRIO DIÁRIO DE OBRA")
    
    # Verificar usuário
    usuario_logado = verificar_usuario_logado()
    if not usuario_logado:
        st.warning("Você precisa estar logado para criar um RDO.")
        return
    
    # Cabeçalho automático - corrigido para mostrar o nome do usuário
    st.write(f"Usuário: {usuario_logado['nome']}")
    
    # Número sequencial do RDO
    proximo_num_rdo = gerar_numero_sequencial_rdo()
    col1, col2 = st.columns(2)

    
    with col1:
        st.write(f"Número do RDO: {proximo_num_rdo}")
    
    # Data do relatório (hoje por padrão)
    with col2:
        data_relatorio = st.date_input(
            "Data do relatório:",
            value=datetime.now().date(),
            format="DD/MM/YYYY"
        )
    
    # Informações da obra
    st.subheader("1. Informações da Obra")
    obras = carregar_obras()
    if not obras:
        st.error("Nenhuma obra cadastrada. Cadastre uma obra antes de criar um RDO.")
        return
    
    obra_selecionada = st.selectbox(
        "Selecione a obra:",
        options=obras.keys()
    )
    
    if obra_selecionada:
        obra = obras[obra_selecionada]
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Data de Início: {obra.get('data_inicio', 'N/A')}")
            st.write(f"Prazo da Obra: {obra.get('prazo', 'N/A')}")
            st.write(f"Etapa Atual: {obra.get('etapa_atual', 'N/A')}")
        with col2:
            st.write(f"Endereço: {obra.get('endereco', 'N/A')}")
            st.write(f"Nº RRT de SI: {obra.get('rrt', 'N/A')}")
            st.write(f"RT Principal: {obra.get('responsavel_principal', 'N/A')}")
            st.write(f"RT Acompanhamento: {obra.get('responsavel_acompanhamento', 'N/A')}")
    
    # Condições climáticas - reorganizadas em manhã e tarde
    st.subheader("2. Condições Climáticas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Manhã:**")
        clima_manha = st.selectbox(
            "Clima - Manhã:",
            options=["Ensolarado", "Parcialmente nublado", "Nublado", "Chuvoso", "Tempestade"]
        )
    
    with col2:
        st.write("**Tarde:**")
        clima_tarde = st.selectbox(
            "Clima - Tarde:",
            options=["Ensolarado", "Parcialmente nublado", "Nublado", "Chuvoso", "Tempestade"]
        )
    
    temperatura = st.slider("Temperatura (°C):", min_value=0, max_value=40, value=25)
    
    # Controle de chuva dividido em manhã e tarde
    st.write("**Controle de Chuva por Hora:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Manhã:")
        horarios_manha = {
            "7h-9h": st.checkbox("Chuva 7h-9h"),
            "9h-11h": st.checkbox("Chuva 9h-11h"),
            "11h-13h": st.checkbox("Chuva 11h-13h")
        }
    
    with col2:
        st.write("Tarde:")
        horarios_tarde = {
            "13h-15h": st.checkbox("Chuva 13h-15h"),
            "15h-17h": st.checkbox("Chuva 15h-17h"),
            "17h-19h": st.checkbox("Chuva 17h-19h")
        }
    
    # Equipes na obra
    st.subheader("3. Equipes na Obra")
    
    # Carrega funcionários do arquivo JSON
    try:
        with open('data/funcionarios.json', 'r', encoding='utf-8') as file:
            funcionarios_dict = json.load(file)
            nomes_funcionarios = [f['nome'] for f in funcionarios_dict.values()]
    except (FileNotFoundError, json.JSONDecodeError):
        nomes_funcionarios = []
        st.warning("Arquivo de funcionários não encontrado ou inválido.")
    
    # Inicializar equipe se não existir no estado da sessão
    if 'equipe' not in st.session_state:
        st.session_state.equipe = []
    
    # Adicionar funcionário à equipe
    col1, col2 = st.columns([3, 1])
    with col1:
        novo_funcionario = st.selectbox("Selecionar funcionário:", options=[""] + nomes_funcionarios)
    with col2:
        if st.button("Adicionar Funcionário") and novo_funcionario:
            st.session_state.equipe.append(novo_funcionario)
            st.rerun()
    
    # Exibir funcionários adicionados
    if st.session_state.equipe:
        st.write("**Funcionários na obra:**")
        for i, func in enumerate(st.session_state.equipe):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i+1}. {func}")
            with col2:
                if st.button(f"Remover", key=f"rem_func_{i}"):
                    st.session_state.equipe.pop(i)
                    st.rerun()
        
        st.write(f"**Total de funcionários:** {len(st.session_state.equipe)}")
    
    # Equipamentos
    equipamentos = st.text_area("Equipamentos Utilizados:", height=100)
    
    # Observações sobre a equipe
    obs_equipe = st.text_area("Observações sobre a equipe:", height=100)
    
    # Atividades do dia - usando um sistema de botão para adicionar mais
    st.subheader("4. Atividades Realizadas")
    
    # Inicializar atividades se não existir
    if 'atividades' not in st.session_state:
        st.session_state.atividades = [{'descricao': '', 'status': 'Em Andamento', 'anexos': []}]
    
    for i, atividade in enumerate(st.session_state.atividades):
        st.write(f"**Atividade {i+1}**")
        
        # Campos da atividade
        st.session_state.atividades[i]['descricao'] = st.text_area(
            f"Descrição da Atividade {i+1}:",
            value=atividade['descricao'],
            height=100,
            key=f"desc_ativ_{i}"
        )
        
        st.session_state.atividades[i]['status'] = st.selectbox(
            f"Status da Atividade {i+1}:",
            options=["Em Andamento", "Concluída", "Atrasada", "Impedida"],
            index=["Em Andamento", "Concluída", "Atrasada", "Impedida"].index(atividade['status']),
            key=f"status_ativ_{i}"
        )
        
        # Upload de arquivos (tanto imagens quanto PDFs)
        uploaded_files = st.file_uploader(
            f"Anexo da Atividade {i+1}:", 
            accept_multiple_files=True,
            type=["jpg", "jpeg", "png", "pdf"],
            key=f"upload_ativ_{i}"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Salvar arquivo se já não estiver salvo
                if uploaded_file.name not in [os.path.basename(a) for a in atividade['anexos']]:
                    file_path = os.path.join("uploads", f"{uuid.uuid4()}_{uploaded_file.name}")
                    os.makedirs("uploads", exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.session_state.atividades[i]['anexos'].append(file_path)
        
        # Mostrar anexos já salvos
        if atividade['anexos']:
            st.write("Anexos salvos:")
            for j, anexo_path in enumerate(atividade['anexos']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(os.path.basename(anexo_path))
                with col2:
                    if st.button(f"Remover anexo", key=f"rem_anexo_{i}_{j}"):
                        if os.path.exists(anexo_path):
                            try:
                                os.remove(anexo_path)
                            except:
                                pass
                        st.session_state.atividades[i]['anexos'].pop(j)
                        st.rerun()
    
    # Botão para adicionar nova atividade
    if st.button("Adicionar outra atividade"):
        st.session_state.atividades.append({
            'descricao': '',
            'status': 'Em Andamento',
            'anexos': []
        })
        st.rerun()
    
    # Ocorrências - usando botão para adicionar mais
    st.subheader("5. Ocorrências")
    
    # Inicializar ocorrências se não existir
    if 'ocorrencias' not in st.session_state:
        st.session_state.ocorrencias = []
    
    # Mostrar ocorrências existentes
    for i, ocorrencia in enumerate(st.session_state.ocorrencias):
        st.write(f"**Ocorrência {i+1}**")
        
        # Campos da ocorrência
        st.session_state.ocorrencias[i]['descricao'] = st.text_area(
            f"Descrição da Ocorrência {i+1}:",
            value=ocorrencia['descricao'],
            height=100,
            key=f"desc_ocor_{i}"
        )
        
        st.session_state.ocorrencias[i]['gravidade'] = st.selectbox(
            f"Gravidade da Ocorrência {i+1}:",
            options=["Baixa", "Média", "Alta", "Crítica"],
            index=["Baixa", "Média", "Alta", "Crítica"].index(ocorrencia.get('gravidade', 'Baixa')),
            key=f"grav_ocor_{i}"
        )
        
        st.session_state.ocorrencias[i]['resolucao'] = st.text_area(
            f"Resolução/Encaminhamento para Ocorrência {i+1}:",
            value=ocorrencia.get('resolucao', ''),
            height=100,
            key=f"res_ocor_{i}"
        )
        
        # Upload de arquivos
        uploaded_files = st.file_uploader(
            f"Anexo da Ocorrência {i+1}:", 
            accept_multiple_files=True,
            type=["jpg", "jpeg", "png", "pdf"],
            key=f"upload_ocor_{i}"
        )
        
        if uploaded_files:
            if 'anexos' not in st.session_state.ocorrencias[i]:
                st.session_state.ocorrencias[i]['anexos'] = []
                
            for uploaded_file in uploaded_files:
                # Salvar arquivo se já não estiver salvo
                if uploaded_file.name not in [os.path.basename(a) for a in st.session_state.ocorrencias[i]['anexos']]:
                    file_path = os.path.join("uploads", f"{uuid.uuid4()}_{uploaded_file.name}")
                    os.makedirs("uploads", exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.session_state.ocorrencias[i]['anexos'].append(file_path)
        
        # Mostrar anexos já salvos
        if ocorrencia.get('anexos'):
            st.write("Anexos salvos:")
            for j, anexo_path in enumerate(ocorrencia['anexos']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(os.path.basename(anexo_path))
                with col2:
                    if st.button(f"Remover anexo", key=f"rem_anexo_ocor_{i}_{j}"):
                        if os.path.exists(anexo_path):
                            try:
                                os.remove(anexo_path)
                            except:
                                pass
                        st.session_state.ocorrencias[i]['anexos'].pop(j)
                        st.rerun()
    
    # Botão para adicionar nova ocorrência
    if st.button("Registrar Ocorrência"):
        st.session_state.ocorrencias.append({
            'descricao': '',
            'gravidade': 'Baixa',
            'resolucao': '',
            'anexos': []
        })
        st.rerun()
    
    # Materiais
    st.subheader("6. Materiais")
    
    # Recebimento de materiais (com botões)
    st.write("**Houve recebimento de materiais?**")
    col1, col2 = st.columns(2)
    
    with col1:
        recebimento_sim = st.button("Sim", key="rec_sim")
    with col2:
        recebimento_nao = st.button("Não", key="rec_nao")
    
    # Controle do estado de recebimento
    if 'recebimento_materiais' not in st.session_state:
        st.session_state.recebimento_materiais = None
    
    if recebimento_sim:
        st.session_state.recebimento_materiais = True
    elif recebimento_nao:
        st.session_state.recebimento_materiais = False
    
    # Mostrar seleção atual
    if st.session_state.recebimento_materiais is not None:
        st.write(f"Selecionado: **{'Sim' if st.session_state.recebimento_materiais else 'Não'}**")
    
    # Campo de descrição se for "Sim"
    materiais_recebidos = ""
    if st.session_state.recebimento_materiais:
        materiais_recebidos = st.text_area(
            "Descreva os materiais recebidos:",
            height=100
        )
    
    # Necessidade de materiais (com botões)
    st.write("**Há necessidade de materiais?**")
    col1, col2 = st.columns(2)
    
    with col1:
        necessidade_sim = st.button("Sim", key="nec_sim")
    with col2:
        necessidade_nao = st.button("Não", key="nec_nao")
    
    # Controle do estado de necessidade
    if 'necessidade_materiais' not in st.session_state:
        st.session_state.necessidade_materiais = None
    
    if necessidade_sim:
        st.session_state.necessidade_materiais = True
    elif necessidade_nao:
        st.session_state.necessidade_materiais = False
    
    # Mostrar seleção atual
    if st.session_state.necessidade_materiais is not None:
        st.write(f"Selecionado: **{'Sim' if st.session_state.necessidade_materiais else 'Não'}**")
    
    # Campos adicionais se for "Sim"
    materiais_necessarios = ""
    materiais_urgentes = False
    
    if st.session_state.necessidade_materiais:
        materiais_urgentes = st.checkbox("URGENTE (necessário nas próximas 48 horas)")
        materiais_necessarios = st.text_area(
            "Descreva os materiais necessários:",
            height=100
        )
    
    # Observações gerais
    st.subheader("7. Observações Gerais")
    observacoes_gerais = st.text_area("Observações gerais:", height=150)
    
    # Botões para salvar relatório
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Relatório"):
            salvar_rdo(
                obra=obra_selecionada,
                data_relatorio=data_relatorio.strftime("%Y/%m/%d"),
                clima_manha=clima_manha,
                clima_tarde=clima_tarde,
                temperatura=temperatura,
                horarios_chuva_manha=horarios_manha,
                horarios_chuva_tarde=horarios_tarde,
                equipe=st.session_state.equipe,
                equipamentos=equipamentos,
                obs_equipe=obs_equipe,
                atividades=st.session_state.atividades,
                ocorrencias=st.session_state.ocorrencias,
                recebimento_materiais_sim=st.session_state.recebimento_materiais,
                materiais_recebidos=materiais_recebidos if st.session_state.recebimento_materiais else "",
                necessidade_materiais_sim=st.session_state.necessidade_materiais,
                materiais_necessarios=materiais_necessarios if st.session_state.necessidade_materiais else "",
                materiais_urgentes=materiais_urgentes,
                observacoes_gerais=observacoes_gerais,
                usuario=usuario_logado
            )
    with col2:
        if st.button("Salvar Relatório e Gerar PDF"):
            id_relatorio = salvar_rdo(
                obra=obra_selecionada,
                data_relatorio=data_relatorio.strftime("%Y/%m/%d"),
                clima_manha=clima_manha,
                clima_tarde=clima_tarde,
                temperatura=temperatura,
                horarios_chuva_manha=horarios_manha,
                horarios_chuva_tarde=horarios_tarde,
                equipe=st.session_state.equipe,
                equipamentos=equipamentos,
                obs_equipe=obs_equipe,
                atividades=st.session_state.atividades,
                ocorrencias=st.session_state.ocorrencias,
                recebimento_materiais_sim=st.session_state.recebimento_materiais,
                materiais_recebidos=materiais_recebidos if st.session_state.recebimento_materiais else "",
                necessidade_materiais_sim=st.session_state.necessidade_materiais,
                materiais_necessarios=materiais_necessarios if st.session_state.necessidade_materiais else "",
                materiais_urgentes=materiais_urgentes,
                observacoes_gerais=observacoes_gerais,
                usuario=usuario_logado
            )
            
            # Gerar PDF
            if id_relatorio:
                with st.spinner("Gerando PDF..."):
                    pdf_path = gerar_pdf_rdo(id_relatorio)
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )

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
                                     value=datetime.now() - timedelta(days=30),
                                     format="DD/MM/YYYY")
        data_final = st.date_input("Data final:", 
                                  value=datetime.now(),
                                  format="DD/MM/YYYY")
    
    # Aplicar filtros
    relatorios_filtrados = []
    for id_rel, relatorio in relatorios_ordenados:
        # Debug - Mostrar a data para inspeção (opcional)
        # st.write(f"Debug - Data em {id_rel}: {relatorio['data_relatorio']}")
        
        # Identificar e converter a data
        data_rel = None
        data_str = relatorio.get('data_relatorio')
        
        # Se não houver data, pula este relatório
        if not data_str:
            st.warning(f"Relatório {id_rel} não possui data.")
            continue
            
        # Tenta vários formatos possíveis
        formatos = [
            "%Y-%m-%d",        # YYYY-MM-DD
            "%d/%m/%Y",        # DD/MM/YYYY
            "%Y/%m/%d",        # YYYY/MM/DD
            "%m/%d/%Y",        # MM/DD/YYYY
            "%d-%m-%Y",        # DD-MM-YYYY
            "%d.%m.%Y",        # DD.MM.YYYY
            "%Y-%m-%d %H:%M:%S"  # YYYY-MM-DD HH:MM:SS
        ]
        
        for formato in formatos:
            try:
                data_rel = datetime.strptime(data_str, formato).date()
                break  # Se conseguir converter, sai do loop
            except ValueError:
                continue
        
        # Se nenhum formato funcionou
        if data_rel is None:
            # Tenta tratar formato de datetime já convertido para string
            # Para casos como "2023-04-15 00:00:00" - extrair só a data
            try:
                # Tenta extrair apenas a parte da data
                data_parts = data_str.split()[0]  # Pega a parte antes do espaço
                for formato in ["%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        data_rel = datetime.strptime(data_parts, formato).date()
                        break
                    except ValueError:
                        continue
            except:
                pass
            
            # Se ainda não conseguiu, tenta tratar como objeto datetime serializado
            if data_rel is None:
                try:
                    # Tenta extrair datetime de string mais complexa
                    import re
                    match = re.search(r'(\d{2,4}[-/\.]\d{1,2}[-/\.]\d{1,4})', data_str)
                    if match:
                        data_str_extracted = match.group(1)
                        for formato in formatos:
                            try:
                                data_rel = datetime.strptime(data_str_extracted, formato).date()
                                break
                            except ValueError:
                                continue
                except:
                    pass
        
        # Se ainda não conseguiu processar a data
        if data_rel is None:
            st.warning(f"Formato de data inválido no relatório {id_rel}: '{data_str}'")
            continue
        
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
                
                # Formatar data para exibição no formato brasileiro
                data_str = relatorio.get('data_relatorio', '')
                data_formatada = data_str  # Padrão caso não consiga formatar
                
                # Tentar converter para formato de exibição brasileiro
                for formato in formatos:
                    try:
                        data_objeto = datetime.strptime(data_str, formato)
                        data_formatada = data_objeto.strftime("%d/%m/%Y")
                        break
                    except ValueError:
                        continue
                    except:
                        pass
                
                st.write(f"Data: {data_formatada}")
                st.write(f"Criado por: {relatorio['nome_usuario_criacao']}")
                
                # Exibir um resumo das atividades
                atividades_count = len(relatorio.get('atividades', []))
                ocorrencias_count = len(relatorio.get('ocorrencias', []))
                st.write(f"Atividades: {atividades_count} | Ocorrências: {ocorrencias_count}")
            
            # (resto do código permanece igual)

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
    if "visualizar_detalhes" in st.session_state and st.session_state["visualizar_detalhes"]:
        opcao = "Visualizar Relatórios"
    
    if "editar_relatorio" in st.session_state and st.session_state["editar_relatorio"]:
      opcao = "Editar Relatório"
        
    # Executar a opção selecionada
    if opcao == "Criar novo RDO":
        criar_rdo()
    elif opcao == "Visualizar Relatórios":
        visualizar_relatorios()
    elif opcao == "Editar Relatório":
        if hasattr(st.session_state, 'editar_relatorio') and st.session_state["editar_relatorio"]:
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
