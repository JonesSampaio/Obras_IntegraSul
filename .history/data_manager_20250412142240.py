import json
import os

# Garantir que o diretório de dados existe
def garantir_diretorio_dados():
    if not os.path.exists("dados"):
        os.makedirs("dados")

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
                "senha": "gestao2024",  # Esta deve ser hash na implementação real
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
    if username in usuarios and username != "gestao":  # Proteger usuário gestão
        del usuarios[username]
        salvar_usuarios(usuarios)
        return True
    return False

def resetar_senha(username):
    usuarios = carregar_usuarios()
    if username in usuarios:
        usuarios[username]["senha"] = "senha123"  # Esta deve ser hash na implementação real
        usuarios[username]["primeiro_acesso"] = True
        salvar_usuarios(usuarios)
        return True
    return False
