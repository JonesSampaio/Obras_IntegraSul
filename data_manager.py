import json
import os
import shutil
from datetime import datetime
import hashlib

# Garantir que o diretório de dados existe
def garantir_diretorio_dados():
    if not os.path.exists("dados"):
        os.makedirs("dados")

# Garantir que o diretório de anexos existe
def garantir_diretorio_anexos():
    if not os.path.exists("dados/anexos"):
        os.makedirs("dados/anexos")

# Funções para gerenciar obras
def carregar_obras():
    garantir_diretorio_dados()
    try:
        with open("dados/obras.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_obras(obras):
    garantir_diretorio_dados()
    with open("dados/obras.json", "w") as f:
        json.dump(obras, f, indent=4)

def adicionar_obra(nome, dados):
    obras = carregar_obras()
    obras[nome] = dados
    salvar_obras(obras)
    return True

def atualizar_obra(nome, dados):
    obras = carregar_obras()
    if nome in obras:
        obras[nome] = dados
        salvar_obras(obras)
        return True
    return False

def excluir_obra(nome):
    obras = carregar_obras()
    if nome in obras:
        del obras[nome]
        salvar_obras(obras)
        return True
    return False

# Funções para gerenciar funcionários
def carregar_funcionarios():
    garantir_diretorio_dados()
    try:
        with open("dados/funcionarios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_funcionarios(funcionarios):
    garantir_diretorio_dados()
    with open("dados/funcionarios.json", "w") as f:
        json.dump(funcionarios, f, indent=4)

def adicionar_funcionario(id, dados):
    funcionarios = carregar_funcionarios()
    funcionarios[id] = dados
    salvar_funcionarios(funcionarios)
    return True

def atualizar_funcionario(id, dados):
    funcionarios = carregar_funcionarios()
    if id in funcionarios:
        funcionarios[id] = dados
        salvar_funcionarios(funcionarios)
        return True
    return False

def excluir_funcionario(id):
    funcionarios = carregar_funcionarios()
    if id in funcionarios:
        del funcionarios[id]
        salvar_funcionarios(funcionarios)
        return True
    return False

# Funções para gerenciar equipes
def carregar_equipes():
    garantir_diretorio_dados()
    try:
        with open("dados/equipes.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_equipes(equipes):
    garantir_diretorio_dados()
    with open("dados/equipes.json", "w") as f:
        json.dump(equipes, f, indent=4)

def adicionar_equipe(nome, dados):
    equipes = carregar_equipes()
    equipes[nome] = dados
    salvar_equipes(equipes)
    return True

def atualizar_equipe(nome, dados):
    equipes = carregar_equipes()
    if nome in equipes:
        equipes[nome] = dados
        salvar_equipes(equipes)
        return True
    return False

def excluir_equipe(nome):
    equipes = carregar_equipes()
    if nome in equipes:
        del equipes[nome]
        salvar_equipes(equipes)
        return True
    return False

# Funções para gerenciar usuários
def carregar_usuarios():
    garantir_diretorio_dados()
    try:
        with open("dados/usuarios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Criar usuário padrão se não existir
        usuarios = {
            "gestao": {
                "senha": "gestao2024", # Esta deve ser hash na implementação real
                "nivel": "admin",
                "nome_completo": "Administrador do Sistema",
                "primeiro_acesso": True
            }
        }
        salvar_usuarios(usuarios)
        return usuarios

def salvar_usuarios(usuarios):
    garantir_diretorio_dados()
    with open("dados/usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=4)

def adicionar_usuario(username, dados):
    usuarios = carregar_usuarios()
    usuarios[username] = dados
    salvar_usuarios(usuarios)
    return True

def atualizar_usuario(username, dados):
    usuarios = carregar_usuarios()
    if username in usuarios:
        usuarios[username] = dados
        salvar_usuarios(usuarios)
        return True
    return False

def excluir_usuario(username):
    usuarios = carregar_usuarios()
    if username in usuarios and username != "gestao": # Proteger usuário gestão
        del usuarios[username]
        salvar_usuarios(usuarios)
        return True
    return False

def hash_senha(senha):
    """Função para gerar hash da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

def resetar_senha(username):
    usuarios = carregar_usuarios()
    if username in usuarios:
        senha_padrao = "mudar123"
        usuarios[username]["senha"] = hash_senha(senha_padrao)
        usuarios[username]["primeiro_acesso"] = True
        usuarios[username]["ultima_alteracao_senha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        salvar_usuarios(usuarios)
        return True
    return False

# Funções para gerenciar relatórios
def carregar_relatorios():
    garantir_diretorio_dados()
    try:
        with open("dados/relatorios.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_relatorios(relatorios):
    garantir_diretorio_dados()
    with open("dados/relatorios.json", "w") as f:
        json.dump(relatorios, f, indent=4)

# Funções para gerenciar anexos
def salvar_anexo(arquivo, relatorio_id, tipo, indice):
    """Salva um arquivo anexo e retorna o caminho relativo
    
    Args:
        arquivo: Objeto do arquivo enviado pelo Streamlit
        relatorio_id: ID do relatório
        tipo: Tipo de anexo ('atividade', 'ocorrencia', etc)
        indice: Índice do item no relatório
    
    Returns:
        str: Caminho relativo do arquivo salvo
    """
    garantir_diretorio_anexos()
    
    # Criar diretório específico para este relatório se não existir
    dir_relatorio = f"dados/anexos/{relatorio_id}"
    if not os.path.exists(dir_relatorio):
        os.makedirs(dir_relatorio)
    
    # Define um nome de arquivo seguro com timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nome_arquivo = f"{tipo}_{indice}_{timestamp}_{arquivo.name}"
    caminho_completo = os.path.join(dir_relatorio, nome_arquivo)
    
    # Salvar o arquivo
    with open(caminho_completo, "wb") as f:
        f.write(arquivo.getbuffer())
    
    # Retorna o caminho relativo para armazenar no JSON
    return os.path.join(relatorio_id, nome_arquivo)

def obter_caminho_anexo(caminho_relativo):
    """Retorna o caminho completo de um anexo
    
    Args:
        caminho_relativo: Caminho relativo do anexo
    
    Returns:
        str: Caminho completo do anexo
    """
    return os.path.join("dados/anexos", caminho_relativo)

def excluir_anexos_relatorio(relatorio_id):
    """Exclui todos os anexos de um relatório
    
    Args:
        relatorio_id: ID do relatório
    """
    dir_relatorio = f"dados/anexos/{relatorio_id}"
    if os.path.exists(dir_relatorio):
        shutil.rmtree(dir_relatorio)

def listar_anexos_relatorio(relatorio_id):
    """Lista todos os anexos de um relatório
    
    Args:
        relatorio_id: ID do relatório
    
    Returns:
        list: Lista de caminhos relativos dos anexos
    """
    dir_relatorio = f"dados/anexos/{relatorio_id}"
    if os.path.exists(dir_relatorio):
        arquivos = os.listdir(dir_relatorio)
        return [os.path.join(relatorio_id, arquivo) for arquivo in arquivos]
    return []

def processar_anexos_atividades(relatorio_id, atividades):
    """Processa os anexos das atividades e atualiza o campo 'anexo' com o caminho salvo
    
    Args:
        relatorio_id: ID do relatório
        atividades: Lista de dicionários de atividades
    
    Returns:
        list: Lista atualizada de atividades com caminhos de anexos
    """
    for i, atividade in enumerate(atividades):
        if atividade.get("anexo") and hasattr(atividade["anexo"], "name"):
            # Se for um objeto de arquivo do Streamlit, salva-o
            caminho = salvar_anexo(atividade["anexo"], relatorio_id, "atividade", i)
            atividade["anexo"] = caminho
    return atividades

def processar_anexos_ocorrencias(relatorio_id, ocorrencias):
    """Processa os anexos das ocorrências e atualiza o campo 'anexo' com o caminho salvo
    
    Args:
        relatorio_id: ID do relatório
        ocorrencias: Lista de dicionários de ocorrências
    
    Returns:
        list: Lista atualizada de ocorrências com caminhos de anexos
    """
    for i, ocorrencia in enumerate(ocorrencias):
        if ocorrencia.get("anexo") and hasattr(ocorrencia["anexo"], "name"):
            # Se for um objeto de arquivo do Streamlit, salva-o
            caminho = salvar_anexo(ocorrencia["anexo"], relatorio_id, "ocorrencia", i)
            ocorrencia["anexo"] = caminho
    return ocorrencias

def processar_fotos_gerais(relatorio_id, fotos):
    """Processa as fotos gerais do relatório
    
    Args:
        relatorio_id: ID do relatório
        fotos: Lista de objetos de arquivo do Streamlit
    
    Returns:
        list: Lista de caminhos relativos das fotos salvas
    """
    caminhos = []
    for i, foto in enumerate(fotos):
        caminho = salvar_anexo(foto, relatorio_id, "foto_geral", i)
        caminhos.append(caminho)
    return caminhos
