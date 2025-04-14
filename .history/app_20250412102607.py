import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração básica
st.set_page_config(page_title="Relatórios de Obra", layout="wide")

# Inicializar lista de funcionários adicionados na sessão
if 'funcionarios_adicionados' not in st.session_state:
    st.session_state.funcionarios_adicionados = []

# Autenticação simples
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.tipo_usuario = None

if not st.session_state.autenticado:
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # Lógica de autenticação com múltiplos usuários
        usuarios_validos = {
            "engenheiro": {"senha": "obra123", "tipo": "Engenheiro"},
            "arquiteto": {"senha": "felipe123", "tipo": "Arq Fillipe Ely"},
            "encarregado": {"senha": "obra456", "tipo": "Encarregado da Obra"}
        }
        
        if usuario in usuarios_validos and senha == usuarios_validos[usuario]["senha"]:
            st.session_state.autenticado = True
            st.session_state.tipo_usuario = usuarios_validos[usuario]["tipo"]
            st.rerun()
        else:
            st.error("Credenciais inválidas")
else:
    # Interface principal
    st.title("Relatório Diário de Obra")
    
    # Obter data e hora atual automaticamente
    data_atual = datetime.today()
    hora_atual = datetime.now().strftime("%H:%M")
    data_formatada = data_atual.strftime("%d/%m/%Y")
    
    # Cabeçalho com usuário, data e hora
    st.markdown(f"**Usuário: {st.session_state.tipo_usuario}** &nbsp;&nbsp;&nbsp;&nbsp; **Data formatada: {data_formatada} - {hora_atual}**")
    
    # Segunda linha - seletor de data, condições climáticas e temperatura
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        data = st.date_input("Data", datetime.today())
    
    with col2:
        clima = st.selectbox("Condições Climáticas", 
                            ["Ensolarado", "Nublado", "Chuvoso", "Parcialmente nublado"])
    with col3:
        temperatura = st.number_input("Temperatura (°C)", min_value=-10, max_value=50)
    
    # Terceira linha - apenas o seletor de obra ocupando toda a largura
    # Lista atualizada com as obras fornecidas
    lista_obras = [
        "EEEM ADELINA ISABELA KONZEN - OBRA_INTEGRA SUL",
        "EEEF DR CARLOS BARBOSA GONÇALVES - OBRA_INTEGRA SUL",
        "EEEF DÉCIO MARTINS COSTA - OBRA_INTEGRA SUL",
        "EEEM GUARARAPES - OBRA_INTEGRA SUL"
    ]
    nome_obra = st.selectbox("Selecione a Obra", lista_obras)
    
    # Detalhes da equipe
    st.subheader("Equipe presente")
    
    # Lista predefinida de possíveis funcionários
    todos_funcionarios = [
        "João Silva - Pedreiro", 
        "Carlos Oliveira - Mestre de obras",
        "Maria Santos - Engenheira civil",
        "Pedro Souza - Eletricista",
        "Ana Costa - Arquiteta",
        "Lucas Ferreira - Ajudante",
        "Roberto Almeida - Encanador",
        "Fernanda Lima - Pintora"
    ]
    
    # Criar checkboxes para cada funcionário
    funcionarios_presentes = []
    cols = st.columns(2)  # Dividir em duas colunas para economizar espaço
    
    for i, funcionario in enumerate(todos_funcionarios):
        with cols[i % 2]:  # Alterna entre as colunas
            if st.checkbox(funcionario, key=f"func_{i}"):
                funcionarios_presentes.append(funcionario)
    
    # Adicionar funcionários previamente adicionados na sessão
    for i, funcionario in enumerate(st.session_state.funcionarios_adicionados):
        with cols[i % 2]:  # Alterna entre as colunas
            if st.checkbox(funcionario, key=f"func_add_{i}"):
                funcionarios_presentes.append(funcionario)
                
    # Opção para adicionar funcionários não listados
    with st.expander("Adicionar outro funcionário"):
        novo_funcionario = st.text_input("Nome do funcionário")
        cargo = st.text_input("Cargo")
        if st.button("Adicionar à lista"):
            if novo_funcionario and cargo:
                funcionario_completo = f"{novo_funcionario} - {cargo}"
                st.session_state.funcionarios_adicionados.append(funcionario_completo)
                funcionarios_presentes.append(funcionario_completo)
                st.success(f"Adicionado: {funcionario_completo}")
                st.rerun()  # Rerun para atualizar a interface com o novo funcionário
    
    # Mostrar número total automaticamente
    num_funcionarios = len(funcionarios_presentes)
    st.info(f"Número total de funcionários presentes: {num_funcionarios}")
    
    # Atividades
    st.subheader("Atividades Realizadas")
    atividades = st.text_area("Descreva as atividades realizadas hoje")
    
    # Upload de arquivos (fotos E PDFs)
    st.subheader("Arquivos e Fotos")
    uploaded_files = st.file_uploader(
        "Carregar fotos e documentos", 
        accept_multiple_files=True, 
        type=["jpg", "jpeg", "png", "pdf"]
    )
    
    if uploaded_files:
        st.write(f"Arquivos carregados: {len(uploaded_files)}")
        for file in uploaded_files:
            file_type = file.name.split('.')[-1].lower()
            if file_type in ['jpg', 'jpeg', 'png']:
                st.image(file, caption=file.name, width=300)
            elif file_type == 'pdf':
                st.write(f"📄 PDF: {file.name}")
    
    # Observações
    st.subheader("Problemas e Observações")
    problemas = st.text_area("Problemas encontrados")
    observacoes = st.text_area("Observações gerais")
    
    # Simplificando a parte de avanço físico
    st.subheader("Situação da Obra")
    status_obra = st.radio(
        "Status atual da obra:",
        ["Conforme cronograma", "Adiantada", "Atrasada"]
    )
    
    # Botão salvar e sair em lados opostos
    col_botoes1, col_botoes2 = st.columns(2)
    
    with col_botoes1:
        if st.button("💾 Salvar Relatório", use_container_width=True):
            # Usar a data do seletor mas a hora atual no momento do salvamento
            data_selecionada = data.strftime("%d/%m/%Y")
            hora_salvamento = datetime.now().strftime("%H:%M")
            
            # Criando o dicionário de dados para salvar
            relatorio = {
                "Data": data_selecionada,
                "Hora": hora_salvamento,
                "Data e Hora": f"{data_selecionada} {hora_salvamento}",
                "Obra": nome_obra,
                "Condições Climáticas": clima,
                "Temperatura (°C)": temperatura,
                "Número de Funcionários": num_funcionarios,
                "Funcionários Presentes": ", ".join(funcionarios_presentes),
                "Atividades Realizadas": atividades,
                "Problemas Encontrados": problemas,
                "Observações Gerais": observacoes,
                "Status da Obra": status_obra,
                "Usuário": st.session_state.tipo_usuario
            }
            
            # Salvar em CSV formatado para Excel
            df_relatorio = pd.DataFrame([relatorio])
            
            # Criar pasta para relatórios se não existir
            os.makedirs("relatorios", exist_ok=True)
            
            # Nome do arquivo com data
            arquivo_csv = f"relatorios/relatorio_{data.strftime('%d%m%Y')}_{nome_obra.replace(' ', '_').replace('-','_')[:30]}.csv"
            
            # Verificar se o arquivo existe para adicionar cabeçalho apenas na primeira vez
            arquivo_existe = os.path.isfile(arquivo_csv)
            
            # Salvar com encoding e separador que o Excel reconhece bem
            df_relatorio.to_csv(
                arquivo_csv, 
                mode='a', 
                header=not arquivo_existe, 
                index=False, 
                encoding='utf-8-sig',  # Encoding que o Excel reconhece acentos
                sep=';'  # Usar ponto-e-vírgula como separador (padrão em Excel BR)
            )
            
            # Lidando com os arquivos
            if uploaded_files:
                # Criar pasta para arquivos se não existir
                pasta_data = data.strftime("%d-%m-%Y")
                pasta_obra = nome_obra.replace(" ", "_").replace("-","_")[:30]
                pasta_destino = f"arquivos/{pasta_obra}/{pasta_data}"
                
                os.makedirs(pasta_destino, exist_ok=True)
                
                # Salvar arquivos
                for file in uploaded_files:
                    with open(f"{pasta_destino}/{file.name}", "wb") as f:
                        f.write(file.getbuffer())
                
                st.success(f"Relatório e {len(uploaded_files)} arquivos salvos com sucesso!")
            else:
                st.success("Relatório salvo com sucesso!")
    
    with col_botoes2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.tipo_usuario = None
            st.rerun()

    # Adicionar um histórico simples dos relatórios
    st.subheader("Relatórios Anteriores")
    if os.path.exists("relatorios"):
        arquivos_relatorios = [f for f in os.listdir("relatorios") if f.endswith('.csv')]
        if arquivos_relatorios:
            for arquivo in arquivos_relatorios[-5:]:  # Mostrar apenas os 5 últimos
                st.write(f"📊 {arquivo}")
        else:
            st.write("Nenhum relatório salvo ainda.")
