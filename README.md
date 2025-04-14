# Sistema de Relatórios Diários de Obra (RDO)

Sistema para gerenciamento de relatórios diários de obra, com controle de usuários, obras, funcionários e equipes.

## Funcionalidades

- Autenticação de usuários com diferentes níveis de acesso
- Criação e gerenciamento de relatórios diários de obra
- Gerenciamento de obras, funcionários e equipes
- Geração de PDFs dos relatórios
- Dashboard para visualização de dados

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_SEU_REPOSITORIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
streamlit run app.py
```

## Estrutura do Projeto

- `app.py`: Arquivo principal da aplicação
- `auth.py`: Gerenciamento de autenticação
- `auth_utils.py`: Utilitários de autenticação
- `admin.py`: Painel administrativo
- `rdo.py`: Funcionalidades de relatórios diários
- `data_manager.py`: Gerenciamento de dados
- `dados/`: Diretório com arquivos JSON de dados

## Níveis de Acesso

- Admin: Acesso total ao sistema
- Gerente/Arquiteto: Gerenciamento de obras, funcionários e equipes
- Engenheiro: Criação e visualização de relatórios
- Usuário: Apenas visualização de relatórios 