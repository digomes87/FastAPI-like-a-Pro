# 🚀 FastAPI Like a Pro

> **Uma API REST moderna construída com FastAPI, demonstrando práticas profissionais de desenvolvimento com CI/CD completo.**

[![Tests](https://github.com/digomes87/FastAPI-like-a-Pro/actions/workflows/tests.yml/badge.svg)](https://github.com/digomes87/FastAPI-like-a-Pro/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green)](https://fastapi.tiangolo.com/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## 📋 Sobre o Projeto

Este projeto demonstra a implementação de uma API REST profissional usando **FastAPI**, com foco em:

- ✅ **Arquitetura limpa** e organizada
- ✅ **Testes automatizados** com alta cobertura
- ✅ **CI/CD pipeline** completo
- ✅ **Infraestrutura como código** com Terraform
- ✅ **Qualidade de código** com linting e formatação
- ✅ **Documentação automática** com OpenAPI/Swagger

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[Pydantic](https://pydantic.dev/)** - Validação de dados com type hints
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM assíncrono para banco de dados
- **[Alembic](https://alembic.sqlalchemy.org/)** - Migrações de banco de dados
- **[PostgreSQL](https://www.postgresql.org/)** - Banco de dados relacional robusto
- **[AsyncPG](https://github.com/MagicStack/asyncpg)** - Driver assíncrono para PostgreSQL
- **[JWT](https://jwt.io/)** - Autenticação com JSON Web Tokens

### **Desenvolvimento**
- **[Poetry](https://python-poetry.org/)** - Gerenciamento de dependências
- **[Pytest](https://pytest.org/)** - Framework de testes
- **[Ruff](https://github.com/astral-sh/ruff)** - Linter e formatter ultra-rápido
- **[Taskipy](https://github.com/taskipy/taskipy)** - Task runner
- **[Docker](https://www.docker.com/)** - Containerização da aplicação
- **[Docker Compose](https://docs.docker.com/compose/)** - Orquestração de contêineres

### **DevOps & CI/CD**
- **[GitHub Actions](https://github.com/features/actions)** - Pipeline de CI/CD
- **[Terraform](https://www.terraform.io/)** - Infraestrutura como código
- **[Codecov](https://codecov.io/)** - Cobertura de código
- **[GitGuardian](https://www.gitguardian.com/)** - Segurança e detecção de secrets

## 🏗️ Arquitetura da API

### **Endpoints Disponíveis**

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/` | Mensagem de boas-vindas | ✅ |
| `GET` | `/health` | Health check para monitoramento | ✅ |
| `POST` | `/users/` | Criar novo usuário | ✅ |
| `GET` | `/users/` | Listar todos os usuários | ✅ |
| `PUT` | `/users/{user_id}` | Atualizar usuário | ✅ |
| `DELETE` | `/users/{user_id}` | Deletar usuário | ✅ |
| `POST` | `/auth/token` | Login e obtenção de token JWT | ✅ |
| `GET` | `/auth/refresh` | Renovar token de acesso | ✅ |
| `GET` | `/auth/google/login` | Iniciar login com Google OAuth2 | ✅ |
| `GET` | `/auth/google/callback` | Callback do Google OAuth2 | ✅ |

### **Modelos de Dados**

```python
# Esquema de entrada
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

# Esquema de saída (público)
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
```

## 🚀 Como Executar

### **Pré-requisitos**
- Python 3.11 ou 3.12
- Poetry instalado
- Docker e Docker Compose (para execução com PostgreSQL)

### **Opção 1: Execução com Docker (Recomendado)**

```bash
# Clone o repositório
git clone https://github.com/digomes87/FastAPI-like-a-Pro.git
cd FastAPI-like-a-Pro

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env conforme necessário

# Execute com Docker Compose
docker-compose up -d

# A API estará disponível em: http://localhost:8000
# PgAdmin estará disponível em: http://localhost:5050
# Documentação automática: http://localhost:8000/docs
```

### **Opção 2: Execução Local**

```bash
# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell

# Execute as migrações (se usando PostgreSQL local)
poetry run alembic upgrade head

# Execute a aplicação
poetry run task run
# ou
fastapi dev fast_zero/async_app.py
```

### **Configuração do Banco de Dados**

#### **PostgreSQL (Produção)**
```bash
# Variáveis de ambiente no .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=fast_zero
DATABASE_USER=fast_zero_user
DATABASE_PASSWORD=fast_zero_password
```



### **Executando Testes**

```bash
# Executar todos os testes
poetry run task test

# Executar testes com cobertura
poetry run pytest --cov=fast_zero --cov-report=html

# Executar testes assíncronos
poetry run pytest tests/ -v

# Verificar qualidade do código
poetry run task lint
poetry run task format
```

## 🐳 Docker

### **Serviços Disponíveis**

| Serviço | Porta | Descrição |
|---------|-------|----------|
| **FastAPI App** | 8000 | Aplicação principal |
| **PostgreSQL** | 5432 | Banco de dados |
| **PgAdmin** | 5050 | Interface web para PostgreSQL |

### **Comandos Docker Úteis**

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs da aplicação
docker-compose logs app

# Executar migrações no container
docker-compose exec app poetry run alembic upgrade head

# Acessar shell do container
docker-compose exec app bash

# Parar todos os serviços
docker-compose down

# Rebuild da aplicação
docker-compose up -d --build app
```

### **Configuração do PgAdmin**

1. Acesse http://localhost:5050
2. Login: `admin@admin.com` / Senha: `admin`
3. Adicione servidor:
   - Host: `postgres`
   - Port: `5432`
   - Database: `fast_zero`
   - Username: `fast_zero_user`
   - Password: `fast_zero_password`

## 🔄 Pipeline CI/CD

### **GitHub Actions Workflows**

#### **1. Tests Workflow** (`.github/workflows/tests.yml`)
- ✅ **Matrix Testing**: Python 3.11 e 3.12
- ✅ **Dependency Caching**: Cache do Poetry para otimização
- ✅ **Code Quality**: Linting com Ruff
- ✅ **Test Coverage**: Cobertura de código com Codecov
- ✅ **Security**: Verificação com GitGuardian

#### **2. Auto-PR Workflow** (`.github/workflows/auto-pr.yml`)
- ✅ **Automação**: Criação automática de Pull Requests
- ✅ **Labels**: Adição automática de labels
- ✅ **Integration**: Integração com GitHub API

### **Proteção de Branch**
- ✅ **Required Checks**: `test` e `lint` obrigatórios
- ✅ **Review Required**: Pelo menos 1 aprovação necessária
- ✅ **Up-to-date**: Branch deve estar atualizada
- ✅ **Admin Enforcement**: Regras aplicadas para admins

## 🏗️ Infraestrutura como Código

### **Terraform Configuration**

O projeto inclui configuração completa do Terraform para:

- 🔒 **Branch Protection**: Configuração automática de proteção
- ✅ **Required Checks**: Definição de verificações obrigatórias
- 🔄 **Workflow Management**: Gerenciamento de workflows
- 📊 **Repository Settings**: Configurações do repositório

```bash
# Navegar para o diretório do Terraform
cd terraform/

# Inicializar Terraform
terraform init

# Planejar mudanças
terraform plan

# Aplicar configurações
terraform apply
```

## 📊 Qualidade e Métricas

### **Cobertura de Código**
- 🎯 **Meta**: > 90% de cobertura
- 📈 **Relatórios**: Gerados automaticamente no CI
- 🔍 **Codecov**: Integração para tracking de cobertura

### **Code Quality**
- 🔧 **Ruff**: Linting e formatação ultra-rápida
- 📏 **Line Length**: 79 caracteres
- 🎨 **Style**: Single quotes, formatação consistente
- 🚫 **Warnings**: Zero warnings policy

## 🔐 Segurança

### **Autenticação e Autorização**
- 🔑 **JWT Tokens**: Autenticação stateless com JSON Web Tokens
- 🔒 **Password Hashing**: Senhas criptografadas com bcrypt
- ⏰ **Token Expiration**: Tokens com tempo de vida configurável
- 🛡️ **Protected Routes**: Endpoints protegidos por autenticação

### **Validação de Senhas**
- 📏 **Comprimento mínimo**: 8 caracteres
- 🔤 **Maiúsculas e minúsculas**: Obrigatório
- 🔢 **Números**: Pelo menos um dígito
- 🔣 **Caracteres especiais**: Pelo menos um símbolo

### **Rate Limiting e Proteção**
- 🚦 **Rate Limiting**: Limite de requisições por IP
- 🔒 **Account Lockout**: Bloqueio após tentativas de login falhadas
- 🛡️ **CORS**: Configuração de origens permitidas

### **DevOps Security**
- 🛡️ **GitGuardian**: Detecção automática de secrets
- 🔒 **Environment Variables**: Configuração segura
- 🚫 **No Hardcoded Secrets**: Política de zero secrets no código
- ✅ **Dependency Scanning**: Verificação de vulnerabilidades

## 📚 Documentação

### **API Documentation**
- 📖 **Swagger UI**: `/docs` - Interface interativa
- 📋 **ReDoc**: `/redoc` - Documentação alternativa
- 🔄 **OpenAPI**: Schema automático gerado pelo FastAPI

### **Desenvolvimento**
- 📝 **README**: Este arquivo
- 🔧 **TROUBLESHOOTING**: `terraform/TROUBLESHOOTING.md`
- 📋 **Tasks**: Definidas no `pyproject.toml`

## 🤝 Contribuindo

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### **Padrões de Commit**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Diego Gomes**
- 📧 Email: diego.gomes87@gmail.com
- 🐙 GitHub: [@digomes87](https://github.com/digomes87)

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!** ⭐
