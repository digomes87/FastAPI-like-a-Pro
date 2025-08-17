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
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM para banco de dados
- **[Alembic](https://alembic.sqlalchemy.org/)** - Migrações de banco de dados

### **Desenvolvimento**
- **[Poetry](https://python-poetry.org/)** - Gerenciamento de dependências
- **[Pytest](https://pytest.org/)** - Framework de testes
- **[Ruff](https://github.com/astral-sh/ruff)** - Linter e formatter ultra-rápido
- **[Taskipy](https://github.com/taskipy/taskipy)** - Task runner

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
| `POST` | `/users/` | Criar novo usuário | ✅ |
| `GET` | `/users/` | Listar todos os usuários | ✅ |
| `PUT` | `/users/{user_id}` | Atualizar usuário | ✅ |
| `DELETE` | `/users/{user_id}` | Deletar usuário | ✅ |

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

### **Instalação**

```bash
# Clone o repositório
git clone https://github.com/digomes87/FastAPI-like-a-Pro.git
cd FastAPI-like-a-Pro

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### **Executando a Aplicação**

```bash
# Desenvolvimento
poetry run task run
# ou
fastapi dev fast_zero/app.py

# A API estará disponível em: http://localhost:8000
# Documentação automática: http://localhost:8000/docs
```

### **Executando Testes**

```bash
# Executar todos os testes
poetry run task test

# Executar testes com cobertura
poetry run pytest --cov=fast_zero --cov-report=html

# Verificar qualidade do código
poetry run task lint
poetry run task format
```

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
