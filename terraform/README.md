# Configuração do Terraform para FastAPI

Este diretório contém a configuração do Terraform para automatizar a configuração do GitHub Actions no repositório FastAPI-like-a-Pro.

## Pré-requisitos

1. **Terraform instalado**: [Download Terraform](https://www.terraform.io/downloads.html)
2. **GitHub Personal Access Token**: Token com permissões `repo`, `workflow`, e `admin:repo_hook`

## Configuração Inicial

### 1. Configurar Variáveis

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edite o arquivo `terraform.tfvars` e adicione seu GitHub token:

```hcl
github_token = "ghp_seu_token_aqui"
```

### 2. Como Obter o GitHub Token

1. Acesse [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Clique em "Generate new token (classic)"
3. Selecione os seguintes escopos:
   - `repo` (acesso completo aos repositórios)
   - `workflow` (atualizar workflows do GitHub Actions)
   - `admin:repo_hook` (gerenciar hooks do repositório)
4. Copie o token gerado

## Uso

### Inicializar Terraform

```bash
terraform init
```

### Planejar as Mudanças

```bash
terraform plan
```

### Aplicar a Configuração

```bash
terraform apply
```

### Destruir Recursos (se necessário)

```bash
terraform destroy
```

## O que o Terraform Faz

Esta configuração:

1. **Conecta ao GitHub**: Usa o provider do GitHub para gerenciar recursos
2. **Referencia o Repositório**: Acessa o repositório `FastAPI-like-a-Pro`
3. **Cria Workflow de CI/CD**: Adiciona um arquivo de workflow do GitHub Actions para:
   - Executar testes automatizados
   - Verificar qualidade do código com linting
   - Suportar múltiplas versões do Python (3.11, 3.12)
   - Usar Poetry para gerenciamento de dependências
   - Gerar relatórios de cobertura

## Estrutura dos Arquivos

```
terraform/
├── main.tf                    # Configuração principal do Terraform
├── variables.tf               # Definição das variáveis
├── terraform.tfvars.example   # Exemplo de configuração de variáveis
├── terraform.tfvars          # Suas variáveis (não commitado)
├── workflows/
│   └── tests.yml             # Workflow do GitHub Actions
└── README.md                 # Esta documentação
```

## Workflow de CI/CD

O workflow criado inclui:

### Jobs de Teste
- Execução em Ubuntu latest
- Matriz de testes com Python 3.11 e 3.12
- Cache de dependências para melhor performance
- Testes com pytest e relatório de cobertura
- Upload de cobertura para Codecov

### Jobs de Linting
- Verificação de qualidade de código com Ruff
- Verificação de formatação

### Triggers
- Push para branches `main` e `develop`
- Pull requests para branch `main`

## Segurança

- O arquivo `terraform.tfvars` está no `.gitignore` para não expor tokens
- Use sempre tokens com permissões mínimas necessárias
- Considere usar GitHub Secrets para tokens em produção

## Troubleshooting

### Erro de Permissão
Se receber erro de permissão, verifique se:
- O token tem os escopos corretos
- Você tem acesso de escrita ao repositório
- O token não expirou

### Erro de Repositório Não Encontrado
Verifique se:
- O nome do repositório está correto no `main.tf`
- O owner (digomes87) está correto
- O repositório existe e é acessível

## Próximos Passos

Após configurar o Terraform, você pode:

1. **Expandir para AWS**: Adicionar recursos AWS para deploy
2. **Configurar Docker**: Adicionar build e push de imagens
3. **Adicionar Ambientes**: Configurar staging e produção
4. **Monitoramento**: Adicionar alertas e métricas

## Referências

- [Terraform GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)