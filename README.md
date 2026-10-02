# Holística Real

Projeto web desenvolvido com Python e Flask. 

## 🚀 Como iniciar o projeto localmente

Siga as instruções abaixo para configurar o ambiente de desenvolvimento:

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/holistica-real.git
cd holistica-real
```

### 2. Criar e ativar o ambiente virtual (Recomendado)
Para isolar as dependências do projeto:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Copie o arquivo `.env.example` e crie um arquivo `.env` na raiz do projeto:
```bash
cp .env.example .env
```
Abra o `.env` e ajuste as variáveis de acordo com a sua necessidade (ex: `SECRET_KEY`).

### 5. Configurar o Banco de Dados (Usuários Iniciais)
Por segurança, os usuários padrão não vêm no banco. Para criá-los, rode o script auxiliar:
```bash
python seed.py
```

### 6. Rodar o servidor
```bash
python main.py
```
Acesse `http://localhost:5000` ou o endereço indicado no terminal.

## 🛠️ Tecnologias
- Python 3
- Flask
- SQLite (via Flask-SQLAlchemy)
