# Docker Setup com Colima

Este projeto está configurado para rodar com Docker usando Colima no macOS.

## Pré-requisitos

- [Colima](https://github.com/abiosoft/colima) instalado
- Docker CLI instalado
- Docker Compose instalado

## Configuração Inicial

### 1. Iniciar Colima

```bash
# Iniciar Colima com configurações adequadas
colima start --cpu 4 --memory 8 --disk 60

# Verificar se está rodando
colima status
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar as variáveis conforme necessário
vim .env
```

### 3. Construir e Executar os Containers

```bash
# Construir as imagens
docker-compose build

# Executar os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f app
```

## Serviços Disponíveis

- **FastAPI App**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050
  - Email: admin@fastzero.com
  - Senha: admin123

## Comandos Úteis

### Gerenciamento dos Containers

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados do banco)
docker-compose down -v

# Reconstruir apenas a aplicação
docker-compose build app
docker-compose up -d app

# Ver logs em tempo real
docker-compose logs -f
```

### Banco de Dados

```bash
# Executar migrações
docker-compose exec app poetry run alembic upgrade head

# Criar nova migração
docker-compose exec app poetry run alembic revision --autogenerate -m "Descrição da migração"

# Acessar o banco diretamente
docker-compose exec postgres psql -U fast_zero_user -d fast_zero
```

### Desenvolvimento

```bash
# Executar testes
docker-compose exec app poetry run pytest

# Acessar shell do container
docker-compose exec app bash

# Instalar nova dependência
docker-compose exec app poetry add nome-da-dependencia
docker-compose restart app
```

## Troubleshooting

### Problema: Container não consegue conectar ao banco

```bash
# Verificar se o PostgreSQL está saudável
docker-compose ps

# Ver logs do PostgreSQL
docker-compose logs postgres

# Reiniciar serviços
docker-compose restart
```

### Problema: Porta já está em uso

```bash
# Verificar processos usando a porta
lsof -i :8000
lsof -i :5432

# Parar processo ou alterar porta no docker-compose.yml
```

### Problema: Colima não está rodando

```bash
# Verificar status
colima status

# Reiniciar Colima
colima stop
colima start
```

## Configuração de Produção

Para produção, considere:

1. Usar variáveis de ambiente seguras
2. Configurar volumes persistentes
3. Usar secrets do Docker
4. Configurar health checks
5. Usar multi-stage builds para otimizar imagens

```bash
# Exemplo para produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```