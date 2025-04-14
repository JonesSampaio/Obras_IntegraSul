import streamlit as st
import pandas as pd
import datetime
import os

# Configuração da página
st.set_page_config(page_title="RDO - Relatório Diário de Obra", layout="wide")

# Título da aplicação
st.title("RDO - RELATÓRIO DIÁRIO DE OBRA")

# Função para formatar a data no formato dd/mm/yyyy - hh:mm
def formatar_data(data):
    return data.strftime("%d/%m/%Y - %H:%M")

# Dados do usuário
st.subheader("Usuário")
usuario = st.text_input("", value="Engenheiro")

# Número do RDO
col1, col2 = st.columns(2)
with col1:
    numero_rdo = st.number_input("Nº RDO:", min_value=1, value=1, step=1)

# Data e Hora
with col2:
    data_hora = st.text_input("Data:", value=formatar_data(datetime.datetime.now()), disabled=True)

# Informações da Obra
st.header("Informações da Obra")

nome_obra = st.text_input("Nome da Obra", value="")
col1, col2 = st.columns(2)

with col1:
    data_inicio = st.text_input("Data de Início da Obra", value="YYYY/MM/DD")
with col2:
    prazo_obra = st.text_input("Prazo da Obra (ex: 9 MESES)", value="")

etapa_obra = st.text_input("Etapa da Obra (ex: TERRAPLANAGEM/ MURO GABIÃO/ BLOCOS E PILARES)", value="")
endereco_obra = st.text_area("Endereço da Obra")
responsavel_tecnico = st.text_input("Responsável Técnico pelo Acompanhamento", value="")
resp_tecnico = st.text_input("Resp. Técnico", value="")
numero_rrt = st.text_input("Nº RRT", value="")

# Clima da obra
st.header("Clima da Obra")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Manhã")
    chuva_manha = st.radio("Chuva pela manhã:", ("SIM", "NÃO"), index=1, horizontal=True, key="manha")

with col2:
    st.subheader("Tarde")
    chuva_tarde = st.radio("Chuva pela tarde:", ("SIM", "NÃO"), index=1, horizontal=True, key="tarde")

# Registrar horários de chuva
st.subheader("Horários de Chuva (selecione os horários)")
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

with col1:
    h8 = st.checkbox("08:00")
with col2:
    h9 = st.checkbox("09:00")
with col3:
    h10 = st.checkbox("10:00")
with col4:
    h11 = st.checkbox("11:00")
with col5:
    h12 = st.checkbox("12:00")
with col6:
    h13 = st.checkbox("13:00")
with col7:
    h14 = st.checkbox("14:00")
with col8:
    h15 = st.checkbox("15:00")
with col9:
    h16 = st.checkbox("16:00")
with col10:
    h17 = st.checkbox("17:00")

# Contagem de trabalhadores por empresa
st.header("Equipe na Obra")
st.subheader("Quantidade de trabalhadores por empresa")

empresas = []
quantidades = []

col1, col2 = st.columns(2)

with col1:
    num_empresas = st.number_input("Número de empresas", min_value=0, value=1, step=1)

for i in range(int(num_empresas)):
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input(f"Nome da Empresa {i+1}")
        empresas.append(empresa)
    with col2:
        qtd = st.number_input(f"Quantidade de trabalhadores {i+1}", min_value=0, value=1, step=1)
        quantidades.append(qtd)

# Ocorrências
st.header("Ocorrências")
ocorrencias = st.text_area("Descreva as ocorrências do dia:")

# Relatório Fotográfico
st.header("Relatório Fotográfico")
fotos = st.file_uploader("Anexar fotos", accept_multiple_files=True)

# Botão para gerar relatório
if st.button("Gerar Relatório"):
    # Criar dataframe com os dados
    data = {
        'Campo': ['Número RDO', 'Data e Hora', 'Nome da Obra', 'Data de Início', 'Prazo da Obra', 'Etapa da Obra', 
                 'Endereço da Obra', 'Responsável Técnico', 'Resp. Técnico', 'Nº RRT', 'Chuva Manhã', 'Chuva Tarde', 
                 'Horários de Chuva', 'Ocorrências'],
        'Valor': [numero_rdo, data_hora, nome_obra, data_inicio, prazo_obra, etapa_obra, endereco_obra, 
                 responsavel_tecnico, resp_tecnico, numero_rrt, chuva_manha, chuva_tarde, 
                 f"08:00: {h8}, 09:00: {h9}, 10:00: {h10}, 11:00: {h11}, 12:00: {h12}, 13:00: {h13}, 14:00: {h14}, 15:00: {h15}, 16:00: {h16}, 17:00: {h17}",
                 ocorrencias]
    }
    
    df = pd.DataFrame(data)
    
    # Dataframe para empresas
    empresas_data = {
        'Empresa': empresas,
        'Quantidade': quantidades
    }
    df_empresas = pd.DataFrame(empresas_data)
    
    # Criar pasta para guardar os relatórios se não existir
    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')
    
    # Salvar o relatório em CSV
    nome_arquivo = f"relatorios/RDO_{numero_rdo}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(nome_arquivo, index=False)
    
    # Salvar dados das empresas
    nome_arquivo_empresas = f"relatorios/RDO_{numero_rdo}_empresas_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df_empresas.to_csv(nome_arquivo_empresas, index=False)
    
    # Salvar as fotos
    if fotos:
        if not os.path.exists(f"relatorios/fotos_RDO_{numero_rdo}"):
            os.makedirs(f"relatorios/fotos_RDO_{numero_rdo}")
        
        for foto in fotos:
            with open(f"relatorios/fotos_RDO_{numero_rdo}/{foto.name}", "wb") as f:
                f.write(foto.getbuffer())
    
    st.success(f"Relatório RDO_{numero_rdo} gerado com sucesso!")
    
    # Exibir resumo do relatório
    st.subheader("Resumo do Relatório")
    st.write(df)
    st.write("Empresas:")
    st.write(df_empresas)
