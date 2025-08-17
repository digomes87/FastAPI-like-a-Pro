
terraform {
  required_version = ">= 1.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
}

provider "github" {
  owner = var.github_owner
  token = var.github_token
}

# Referencia o repositório existente
data "github_repository" "fastapi_pro" {
  name = var.repository_name
}

# Cria o arquivo de workflow do GitHub Actions para testes
# Comentado porque o arquivo já existe no repositório
# resource "github_repository_file" "ci_workflow" {
#   repository          = data.github_repository.fastapi_pro.name
#   branch              = "main"
#   file                = ".github/workflows/tests.yml"
#   content             = file("${path.module}/workflows/tests.yml")
#   commit_message      = "Add CI/CD workflow with tests and linting"
#   commit_author       = "Terraform"
#   commit_email        = "terraform@example.com"
#   overwrite_on_create = true
# }

# Cria o arquivo de workflow para auto-PR
# Comentado porque o arquivo já foi criado manualmente
# resource "github_repository_file" "auto_pr_workflow" {
#   repository          = data.github_repository.fastapi_pro.name
#   branch              = "main"
#   file                = ".github/workflows/auto-pr.yml"
#   content             = file("${path.module}/workflows/auto-pr.yml")
#   commit_message      = "Add auto PR creation workflow"
#   commit_author       = "Terraform"
#   commit_email        = "terraform@example.com"
#   overwrite_on_create = true
# }

# Proteção de branch
resource "github_branch_protection" "main" {
  repository_id  = data.github_repository.fastapi_pro.node_id
  pattern        = "main"
  enforce_admins = true

  required_status_checks {
    strict = true
    contexts = [
      "test",
      "lint"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
  }
}

# Configura secrets do repositório (se necessário)
resource "github_actions_secret" "codecov_token" {
  count           = var.codecov_token != "" ? 1 : 0
  repository      = data.github_repository.fastapi_pro.name
  secret_name     = "CODECOV_TOKEN"
  plaintext_value = var.codecov_token
}
