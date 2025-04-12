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
    try:
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
    except Exception as e:
        st.session_state.numero_rdo = 1
        st.warning(f"Erro ao configurar número do RDO: {e}")

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
        # CORREÇÃO: Removido o parâmetro height=60
        endereco_obra = st.text_area("Endereço da Obra")
        
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
    cols_chuva = st.columns(10)
    for i, hora in enumerate(horarios):
        with cols_chuva[i]:
            st.write(hora)
            chuva = st.checkbox("Chuva", key=f"chuva_{hora}")
            chuva_por_hora[hora] = "Sim" if chuva else "Não"
    
    # Adicionar temperatura
    temperatura = st.slider("Temperatura média (°C)", 0, 40, 25)
    
    # Equipes na obra (refatorado)
    st.subheader("Equipes na Obra")
    
    if 'equipes' not in st.session_state:
        st.session_state.equipes = []
    
    # Interface para adicionar equipes
    with st.expander("Adicionar Equipe", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Empresa")
            responsavel = st.text_input("Responsável")
        
        with col2:
            num_funcionarios = st.number_input("Número de Funcionários", min_value=1, value=1)
            equipamentos = st.text_area("Equipamentos Utilizados")
        
        if st.button("Adicionar Equipe"):
            nova_equipe = {
                "empresa": empresa,
                "responsavel": responsavel,
                "num_funcionarios": num_funcionarios,
                "equipamentos": equipamentos
            }
            st.session_state.equipes.append(nova_equipe)
            st.success(f"Equipe de {empresa} adicionada com sucesso!")
            st.rerun()
    
    # Exibir equipes adicionadas
    total_funcionarios = 0
    if st.session_state.equipes:
        st.write("Equipes registradas:")
        
        # Calcular totais
        total_funcionarios = sum(eq["num_funcionarios"] for eq in st.session_state.equipes)
        
        for i, equipe in enumerate(st.session_state.equipes):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{equipe['empresa']}** - {equipe['responsavel']}")
            with col2:
                st.write(f"{equipe['num_funcionarios']} funcionários")
            with col3:
                if st.button("Remover", key=f"remove_{i}"):
                    st.session_state.equipes.pop(i)
                    st.rerun()
            
            st.write(f"Equipamentos: {equipe['equipamentos']}")
            st.divider()
        
        st.info(f"Total: {len(st.session_state.equipes)} equipes com {total_funcionarios} funcionários")
    
    # Atividades do dia
    st.subheader("Atividades do Dia")
    
    # Interface para atividades
    num_atividades = st.number_input("Número de atividades a registrar", min_value=1, max_value=10, value=3)
    
    atividades = []
    for i in range(num_atividades):
        atividade = st.text_area(f"Atividade {i+1}", key=f"atividade_{i}")
        atividades.append(atividade)
    
    # Ocorrências
    st.subheader("Ocorrências")
    
    num_ocorrencias = st.number_input("Número de ocorrências a registrar", min_value=0, max_value=5, value=0)
    
    ocorrencias = []
    for i in range(num_ocorrencias):
        ocorrencia = st.text_area(f"Ocorrência {i+1}", key=f"ocorrencia_{i}")
        ocorrencias.append(ocorrencia)
    
    # Upload de arquivos
    st.subheader("Relatório Fotográfico / Documentos")
    
    uploaded_files = st.file_uploader("Carregar arquivos", accept_multiple_files=True)
    
    # Adicionar descrição para cada arquivo
    if uploaded_files:
        st.write("Descreva cada arquivo:")
        for file in uploaded_files:
            desc_key = f"desc_{file.name}"
            if desc_key not in st.session_state:
                st.session_state[desc_key] = ""
            st.session_state[desc_key] = st.text_area(f"Descrição de {file.name}", st.session_state[desc_key])
    
    # Botões de ação
    col_botoes1, col_botoes2 = st.columns(2)
    
    with col_botoes1:
        if st.button("📥 Salvar RDO", use_container_width=True):
            try:
                # Formatar a data para o relatório
                data_selecionada = data.strftime("%d/%m/%Y")
                hora_salvamento = datetime.now().strftime("%H:%M:%S")
                
                # Formatar as equipes
                equipes_info = "\n".join([
                    f"{eq['empresa']} - {eq['responsavel']} ({eq['num_funcionarios']} funcionários)"
                    for eq in st.session_state.equipes
                ]) if st.session_state.equipes else "Nenhuma equipe registrada"
                
                # Formatar os equipamentos
                equipamentos_info = "\n".join([
                    f"{eq['empresa']}: {eq['equipamentos']}"
                    for eq in st.session_state.equipes if eq['equipamentos']
                ]) if st.session_state.equipes else "Nenhum equipamento registrado"
                
                # Formatar as atividades
                atividades_texto = "\n".join([
                    f"{i+1}. {ativ}" for i, ativ in enumerate(atividades) if ativ.strip()
                ]) if any(ativ.strip() for ativ in atividades) else "Nenhuma atividade registrada"
                
                # Formatar as ocorrências
                ocorrencias_texto = "\n".join([
                    f"- {ocor}" for ocor in ocorrencias if ocor.strip()
                ]) if any(ocor.strip() for ocor in ocorrencias) else "Nenhuma ocorrência registrada"
                
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
                    "Data de Início": data_inicio.strftime("%d/%m/%Y") if data_inicio else "Não definida",
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
                
                # Nome do arquivo com data - garantindo que não haja caracteres especiais
                nome_obra_limpo = nome_obra.replace(' ', '_').replace('-','_').replace('/','_')[:30]
                arquivo_csv = f"relatorios/RDO_{st.session_state.numero_rdo}_{data.strftime('%d%m%Y')}_{nome_obra_limpo}.csv"
                
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
                    pasta_obra = nome_obra.replace(" ", "_").replace("-","_").replace('/','_')[:30]
                    pasta_destino = f"arquivos/{pasta_obra}/{pasta_data}"
                    os.makedirs(pasta_destino, exist_ok=True)
                    
                    # Salvar arquivos com suas descrições
                    for i, file in enumerate(uploaded_files):
                        try:
                            # Salvar o arquivo
                            with open(f"{pasta_destino}/{file.name}", "wb") as f:
                                f.write(file.getbuffer())
                            
                            # Salvar a descrição
                            desc_key = f"desc_{file.name}"
                            if desc_key in st.session_state:
                                with open(f"{pasta_destino}/{file.name}.desc.txt", "w", encoding="utf-8") as f:
                                    f.write(st.session_state[desc_key])
                        except Exception as e:
                            st.warning(f"Erro ao salvar arquivo {file.name}: {e}")
                    
                    st.success(f"RDO Nº {st.session_state.numero_rdo} e {len(uploaded_files)} arquivos salvos com sucesso!")
                else:
                    st.success(f"RDO Nº {st.session_state.numero_rdo} salvo com sucesso!")
                
                # Incrementar o número do RDO para o próximo relatório
                st.session_state.numero_rdo += 1
            
            except Exception as e:
                st.error(f"Erro ao salvar o relatório: {e}")
                import traceback
                st.error(traceback.format_exc())
    
    with col_botoes2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.tipo_usuario = None
            st.rerun()
    
    # Adicionar um histórico simples dos relatórios
    st.subheader("Relatórios Anteriores")
    try:
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
    except Exception as e:
        st.warning(f"Erro ao acessar relatórios anteriores: {e}")
