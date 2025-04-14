import streamlit as st
import pandas as pd
from datetime import datetime, time
import os

# Configuração básica
st.set_page_config(page_title="Relatórios Diários de Obra (RDO)", layout="wide")

# Inicializar variáveis de estado
if 'funcionarios_adicionados' not in st.session_state:
    st.session_state.funcionarios_adicionados = []

if 'numero_rdo' not in st.session_state:
    # Inicializar com 1 ou buscar o último número usado
    if os.path.exists("relatorios"):
        arquivos = [f for f in os.listdir("relatorios") if f.endswith('.csv')]
        if arquivos:
            # Tenta extrair o último número de RDO usado
            try:
                numeros = []
                for arquivo in arquivos:
                    df = pd.read_csv(f"relatorios/{arquivo}", sep=';', encoding='utf-8-sig')
                    if 'Número RDO' in df.columns:
                        numeros.extend(df['Número RDO'].tolist())
                if numeros:
                    st.session_state.numero_rdo = max([int(n) for n in numeros if str(n).isdigit()]) + 1
                else:
                    st.session_state.numero_rdo = 1
            except:
                st.session_state.numero_rdo = 1
        else:
            st.session_state.numero_rdo = 1
    else:
        st.session_state.numero_rdo = 1

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
    st.title("RDO - RELATÓRIO DIÁRIO DE OBRA")
    
    # Cabeçalho com mais detalhes
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f"**Usuário: {st.session_state.tipo_usuario}**")
    with col2:
        st.markdown(f"**Nº RDO: {st.session_state.numero_rdo}**")
    with col3:
        data_atual = datetime.today()
        hora_atual = datetime.now().strftime("%H:%M")
        data_formatada = data_atual.strftime("%d/%m/%Y")
        st.markdown(f"**Data: {data_formatada} - {hora_atual}**")
    
    # Informações básicas da obra
    st.subheader("Informações da Obra")
    
    col1, col2 = st.columns(2)
    with col1:
        # Lista atualizada com as obras fornecidas
        lista_obras = [
            "EEEM ADELINA ISABELA KONZEN - OBRA_INTEGRA SUL",
            "EEEF DR CARLOS BARBOSA GONÇALVES - OBRA_INTEGRA SUL",
            "EEEF DÉCIO MARTINS COSTA - OBRA_INTEGRA SUL",
            "EEEM GUARARAPES - OBRA_INTEGRA SUL",
            "DIMED – EXPANSÃO LOGÍSTICA EDS"
        ]
        nome_obra = st.selectbox("Nome da Obra", lista_obras)
        
        data_inicio = st.date_input("Data de Início da Obra", value=None)
        
        prazo_obra = st.text_input("Prazo da Obra (ex: 9 MESES)")
        
        etapa_obra = st.text_input("Etapa da Obra (ex: TERRAPLANAGEM/ MURO GABIÃO/ BLOCOS E PILARES)")
    
    with col2:
        endereco_obra = st.text_area("Endereço da Obra", height=60)
        
        num_rrt = st.text_input("Nº RRT de SI")
        
        # Adicionar campos para responsáveis técnicos
        resp_acompanhamento = st.text_input("Responsável Técnico pelo Acompanhamento")
        resp_tecnico = st.text_input("Responsável Técnico Principal")
    
    # Condições climáticas melhoradas
    st.subheader("Condições Climáticas")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        data = st.date_input("Data do Relatório", datetime.today())
    with col2:
        clima_manha = st.selectbox("Clima da Manhã", 
                                ["Ensolarado", "Nublado", "Chuvoso", "Parcialmente nublado"])
    with col3:
        clima_tarde = st.selectbox("Clima da Tarde", 
                                ["Ensolarado", "Nublado", "Chuvoso", "Parcialmente nublado"])
    
    # Tabela de controle de chuva por hora
    st.subheader("Controle de Chuva")
    horarios = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    # Criar layout de checkboxes para cada hora
    chuva_por_hora = {}
    cols = st.columns(len(horarios))
    
    for i, hora in enumerate(horarios):
        with cols[i]:
            st.write(f"{hora}")
            chove = not st.checkbox("Não chove", key=f"chuva_{hora}", value=True)
            chuva_por_hora[hora] = "Chove" if chove else "Não chove"
    
    # Temperatura
    temperatura = st.number_input("Temperatura (°C)", min_value=-10, max_value=50)
    
    # Equipes em um formato mais estruturado
    st.subheader("Equipes de Trabalho")
    
    # Sistema para adicionar múltiplas empresas/equipes
    if 'equipes' not in st.session_state:
        st.session_state.equipes = []
    
    with st.expander("Adicionar Empresa/Equipe", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            empresa = st.text_input("Nome da Empresa", key="empresa_input")
        with col2:
            responsavel = st.text_input("Responsável", key="resp_input")
        with col3:
            num_funcionarios = st.number_input("Quantidade de Funcionários", min_value=0, value=1, key="num_func_input")
        
        equipamentos = st.text_area("Equipamentos/Função dos Funcionários", key="equip_input")
        
        if st.button("Adicionar Equipe"):
            if empresa:
                nova_equipe = {
                    "empresa": empresa,
                    "responsavel": responsavel,
                    "num_funcionarios": int(num_funcionarios),
                    "equipamentos": equipamentos
                }
                st.session_state.equipes.append(nova_equipe)
                st.success(f"Equipe da empresa {empresa} adicionada!")
                st.rerun()
    
    # Exibir equipes adicionadas
    total_funcionarios = 0
    if st.session_state.equipes:
        for i, equipe in enumerate(st.session_state.equipes):
            total_funcionarios += equipe["num_funcionarios"]
            st.markdown(f"""
            **Empresa {i+1}: {equipe['empresa']}**  
            Responsável: {equipe['responsavel']}  
            Funcionários: {equipe['num_funcionarios']}  
            Equipamentos/Função: {equipe['equipamentos']}
            """)
        
        # Mostrar totais
        num_equipes = len(st.session_state.equipes)
        st.info(f"Total de Equipes: {num_equipes} | Total de Funcionários: {total_funcionarios}")
        
        if st.button("Limpar Equipes"):
            st.session_state.equipes = []
            st.rerun()
    else:
        st.warning("Nenhuma equipe adicionada ainda.")
    
    # Atividades realizadas em formato numerado
    st.subheader("Relatórios de Atividades")
    
    if 'atividades' not in st.session_state:
        st.session_state.atividades = ["", "", "", "", "", "", ""]  # Inicializar com 7 campos vazios
    
    for i in range(7):
        st.session_state.atividades[i] = st.text_area(f"Atividade {i+1}", value=st.session_state.atividades[i], height=50, key=f"atividade_{i}")
    
    # Ocorrências
    st.subheader("Ocorrências")
    if 'ocorrencias' not in st.session_state:
        st.session_state.ocorrencias = ["", "", ""]  # Inicializar com 3 campos vazios
    
    for i in range(3):
        st.session_state.ocorrencias[i] = st.text_area(f"Ocorrência {i+1}", value=st.session_state.ocorrencias[i], height=50, key=f"ocorrencia_{i}")
    
    # Upload de arquivos (fotos e PDFs) com descrições
    st.subheader("Relatório Fotográfico")
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
        st.session_state.file_descriptions = []
    
    uploaded_files = st.file_uploader(
        "Carregar fotos e documentos",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "pdf"],
        key="file_upload"
    )
    
    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            file_type = file.name.split('.')[-1].lower()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if file_type in ['jpg', 'jpeg', 'png']:
                    st.image(file, caption=file.name, width=250)
                elif file_type == 'pdf':
                    st.write(f"📄 PDF: {file.name}")
            with col2:
                desc_key = f"desc_{file.name}"
                file_desc = st.text_area(f"Descrição da imagem {i+1}", key=desc_key, height=100)
                
                # Armazenar descrição na sessão
                if desc_key not in st.session_state:
                    st.session_state[desc_key] = ""
                st.session_state[desc_key] = file_desc
        
        st.session_state.uploaded_files = uploaded_files
    
    # Botão salvar e sair em lados opostos
    col_botoes1, col_botoes2 = st.columns(2)
    
    with col_botoes1:
        if st.button("💾 Salvar Relatório", use_container_width=True):
            # Usar a data do seletor mas a hora atual no momento do salvamento
            data_selecionada = data.strftime("%d/%m/%Y")
            hora_salvamento = datetime.now().strftime("%H:%M")
            
            # Preparar dados das equipes
            equipes_info = ""
            equipamentos_info = ""
            
            for equipe in st.session_state.equipes:
                equipes_info += f"{equipe['empresa']} ({equipe['responsavel']}): {equipe['num_funcionarios']} | "
                equipamentos_info += f"{equipe['empresa']}: {equipe['equipamentos']} | "
            
            # Preparar dados das atividades
            atividades_texto = ""
            for i, atividade in enumerate(st.session_state.atividades):
                if atividade:
                    atividades_texto += f"{i+1}. {atividade} | "
            
            # Preparar dados das ocorrências
            ocorrencias_texto = ""
            for i, ocorrencia in enumerate(st.session_state.ocorrencias):
                if ocorrencia:
                    ocorrencias_texto += f"{i+1}. {ocorrencia} | "
            
            # Preparar dados do controle de chuva
            chuva_texto = ""
            for hora, status in chuva_por_hora.items():
                chuva_texto += f"{hora}: {status} | "
            
            # Criando o dicionário de dados para salvar
            relatorio = {
                "Número RDO": st.session_state.numero_rdo,
                "Data": data_selecionada,
                "Hora": hora_salvamento,
                "Data e Hora": f"{data_selecionada} {hora_salvamento}",
                "Obra": nome_obra,
                "Endereço da Obra": endereco_obra,
                "Data de Início": data_inicio.strftime("%d/%m/%Y") if data_inicio else "",
                "Prazo da Obra": prazo_obra,
                "Número RRT": num_rrt,
                "Etapa da Obra": etapa_obra,
                "Responsável Acompanhamento": resp_acompanhamento,
                "Responsável Técnico Principal": resp_tecnico,
                "Clima Manhã": clima_manha,
                "Clima Tarde": clima_tarde,
                "Controle de Chuva": chuva_texto,
                "Temperatura (°C)": temperatura,
                "Número de Equipes": len(st.session_state.equipes),
                "Número de Funcionários": total_funcionarios,
                "Equipes": equipes_info,
                "Equipamentos": equipamentos_info,
                "Atividades": atividades_texto,
                "Ocorrências": ocorrencias_texto,
                "Usuário": st.session_state.tipo_usuario
            }
            
            # Salvar em CSV formatado para Excel
            df_relatorio = pd.DataFrame([relatorio])
            
            # Criar pasta para relatórios se não existir
            os.makedirs("relatorios", exist_ok=True)
            
            # Nome do arquivo com data
            arquivo_csv = f"relatorios/RDO_{st.session_state.numero_rdo}_{data.strftime('%d%m%Y')}_{nome_obra.replace(' ', '_').replace('-','_')[:30]}.csv"
            
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
                
                # Salvar arquivos com suas descrições
                for i, file in enumerate(uploaded_files):
                    # Salvar o arquivo
                    with open(f"{pasta_destino}/{file.name}", "wb") as f:
                        f.write(file.getbuffer())
                    
                    # Salvar a descrição
                    desc_key = f"desc_{file.name}"
                    if desc_key in st.session_state:
                        with open(f"{pasta_destino}/{file.name}.desc.txt", "w") as f:
                            f.write(st.session_state[desc_key])
                
                st.success(f"RDO Nº {st.session_state.numero_rdo} e {len(uploaded_files)} arquivos salvos com sucesso!")
            else:
                st.success(f"RDO Nº {st.session_state.numero_rdo} salvo com sucesso!")
            
            # Incrementar o número do RDO para o próximo relatório
            st.session_state.numero_rdo += 1
    
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
            arquivos_relatorios.sort(reverse=True)  # Ordenar do mais recente para o mais antigo
            for arquivo in arquivos_relatorios[:5]:  # Mostrar apenas os 5 últimos
                st.write(f"📊 {arquivo}")
                # Opção para visualizar o relatório
                if st.button(f"Visualizar {arquivo}", key=f"view_{arquivo}"):
                    try:
                        df = pd.read_csv(f"relatorios/{arquivo}", sep=';', encoding='utf-8-sig')
                        st.dataframe(df)
                    except Exception as e:
                        st.error(f"Erro ao abrir o arquivo: {e}")
        else:
            st.write("Nenhum relatório salvo ainda.")
