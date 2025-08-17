# Guia de Troubleshooting - Terraform GitHub

## ❌ Erro: "401 Bad credentials"

### Problema
O erro `401 Bad credentials` indica que o GitHub token não está configurado corretamente ou é inválido.

### Soluções

#### 1. Verificar se o arquivo terraform.tfvars existe
```bash
ls -la terraform.tfvars
```

Se não existir, crie a partir do exemplo:
```bash
cp terraform.tfvars.example terraform.tfvars
```

#### 2. Gerar um novo GitHub Personal Access Token

1. **Acesse**: [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. **Clique**: "Generate new token (classic)"
3. **Configure**:
   - **Note**: "Terraform FastAPI Project"
   - **Expiration**: 90 days (ou conforme necessário)
   - **Scopes** (OBRIGATÓRIOS):
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `admin:repo_hook` (Full control of repository hooks)
     - ✅ `read:org` (Read org and team membership, read org projects)
     - ✅ `read:discussion` (Read discussions)

4. **Copie o token** (você só verá uma vez!)

#### 3. Configurar o token no terraform.tfvars

Edite o arquivo `terraform.tfvars`:
```hcl
github_token = "ghp_seu_token_aqui"
```

#### 4. Verificar se o repositório existe

O erro também pode indicar que o repositório não existe. Verifique:

1. **Repositório existe?**: https://github.com/digomes87/FastAPI-like-a-Pro
2. **Você tem acesso?**: Verifique se o repositório é público ou se você tem permissões
3. **Nome correto?**: Confirme o nome exato do repositório

#### 5. Testar o token manualmente

Teste se o token funciona:
```bash
curl -H "Authorization: token SEU_TOKEN" https://api.github.com/user
```

Deve retornar suas informações do GitHub.

#### 6. Configurar variáveis alternativas

Se o repositório for diferente, configure no `terraform.tfvars`:
```hcl
github_token = "ghp_seu_token_aqui"
github_owner = "seu_usuario"
repository_name = "seu_repositorio"
```

### Comandos para Resolver

```bash
# 1. Verificar configuração atual
cat terraform.tfvars

# 2. Testar conectividade
make validate

# 3. Executar plano novamente
make plan

# 4. Se tudo estiver ok, aplicar
make apply
```

### Verificações de Segurança

- ✅ Nunca commite o arquivo `terraform.tfvars`
- ✅ Use tokens com permissões mínimas necessárias
- ✅ Configure expiração adequada para os tokens
- ✅ Revogue tokens antigos quando não precisar mais

### Outros Erros Comuns

#### Repositório não encontrado (404)
```
Error: GET https://api.github.com/repos/owner/repo: 404 Not Found
```
**Solução**: Verifique se o nome do repositório e owner estão corretos.

#### Rate limit (403)
```
Error: GET https://api.github.com/repos/owner/repo: 403 rate limit exceeded
```
**Solução**: Aguarde alguns minutos ou use um token autenticado.

#### Permissões insuficientes (403)
```
Error: POST https://api.github.com/repos/owner/repo: 403 Forbidden
```
**Solução**: Verifique se o token tem os scopes necessários.

## ❌ Erro: "refusing to allow a Personal Access Token to create or update workflow without workflow scope"

### Problema
Este erro ocorre quando você tenta fazer push de workflows (.github/workflows/*.yml) mas o token não tem o escopo `workflow`.

### Soluções

#### 1. Verificar os escopos do seu token atual
```bash
curl -H "Authorization: token SEU_TOKEN" https://api.github.com/user
```
Verifique o header `X-OAuth-Scopes` na resposta.

#### 2. Gerar um novo token com escopo `workflow`
1. **Acesse**: [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. **Encontre** seu token atual e clique em "Edit" OU crie um novo token
3. **IMPORTANTE**: Marque o escopo `workflow`
4. **Atualize** o `terraform.tfvars` com o novo token

#### 3. Configurar o Git para usar o novo token
```bash
git remote set-url origin https://SEU_TOKEN@github.com/digomes87/FastAPI-like-a-Pro.git
```
OU configure o credential helper:
```bash
git config --global credential.helper store
echo "https://SEU_TOKEN@github.com" > ~/.git-credentials
```

### Contato

Se o problema persistir:
1. Verifique os logs completos com `terraform plan -var-file=terraform.tfvars`
2. Confirme que o repositório existe e é acessível
3. Teste o token manualmente com curl
4. Verifique se não há caracteres especiais no token