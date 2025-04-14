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
    
    # Criar o formulário principal
    with st.form(key='rdo_form'):
        st.subheader("1. Informações Básicas")
        
        # Seleção de obra
        obra_selecionada = st.selectbox(
            "Obra:",
            options=list(obras.keys())
        )
        
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
        col1, col2, col3, col4 = st.columns(4)
        
        controle_chuva = {}
        horas = [f"{h:02d}:00" for h in range(24)]
        
        for i, hora in enumerate(horas):
            col = [col1, col2, col3, col4][i % 4]
            with col:
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
        # Não podemos usar st.button dentro de um form, precisamos lidar com isso de outra forma
        # Vamos adicionar um campo para permitir adicionar várias atividades
        adicionar_atividade = st.checkbox("Adicionar outra atividade", key="add_atividade")
        
        st.subheader("4. Ocorrências")
        
        # Checkbox para adicionar ocorrência
        adicionar_ocorrencia = st.checkbox("Registrar ocorrência", key="add_ocorrencia")
        
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
                    adicionar_outra = st.checkbox(f"Adicionar outra ocorrência", key=f"add_ocor_{i}")
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
        
    # Lógica após o submit do formulário
    if submit_button:
        # Verificar se há atividades preenchidas
        atividades_validas = [a for a in st.session_state.atividades if a['descricao'].strip()]
        if not atividades_validas:
            st.error("É necessário adicionar pelo menos uma atividade.")
            return
        
        # Criar o relatório
        id_relatorio = gerar_id_relatorio()
        
        # Criar objeto de relatório
        relatorio = {
            'id': id_relatorio,
            'numero_rdo': str(numero_rdo),
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'nome_usuario_criacao': nome_usuario,
            'obra': obra_selecionada,
            'data_relatorio': data_relatorio,
            'clima_manha': clima_manha,
            'clima_tarde': clima_manha,  # Usando o mesmo valor da manhã por simplicidade
            'temperatura': temperatura,
            'controle_chuva': controle_chuva,
            'funcionarios': funcionarios_selecionados,
            'equipes': equipes_selecionadas,
            'observacoes_pessoal': observacoes_pessoal,
            'atividades': [],
            'ocorrencias': [],
            'recebimento_materiais_sim': recebimento_materiais,
            'materiais_recebidos': materiais_recebidos if recebimento_materiais else "",
            'necessidade_materiais_sim': necessidade_materiais,
            'materiais_necessarios': materiais_necessarios if necessidade_materiais else "",
            'materiais_urgentes': materiais_urgentes,
            'observacoes_gerais': observacoes_gerais,
            'fotos': []
        }
        
        # Processar anexos das atividades
        for atividade in st.session_state.atividades:
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
        for ocorrencia in st.session_state.ocorrencias:
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
        
        # Limpar o estado da sessão
        limpar_estado_sessao()
        
        st.success(f"Relatório RDO Nº {numero_rdo} salvo com sucesso!")
        st.balloons()
    
    # Lógica para adicionar nova atividade (fora do formulário)
    if 'add_atividade' in st.session_state and st.session_state.add_atividade:
        # Se o checkbox de adicionar atividade foi marcado, adiciona uma nova atividade e refaz a página
        st.session_state.atividades.append({
            'descricao': '',
            'status': 'Em Andamento',
            'responsavel': '',
            'anexos': []
        })
        st.session_state.add_atividade = False  # Reset o estado para não adicionar infinitamente
        st.rerun()  # Recarrega a página com a nova atividade

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
