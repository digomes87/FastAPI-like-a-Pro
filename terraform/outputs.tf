output "repository_url" {
  description = "URL do repositório GitHub"
  value       = data.github_repository.fastapi_pro.html_url
}

output "repository_clone_url" {
  description = "URL para clonar o repositório"
  value       = data.github_repository.fastapi_pro.ssh_clone_url
}

output "workflow_file_path" {
  description = "Caminho do arquivo de workflow criado"
  value       = github_repository_file.ci_workflow.file
}

output "branch_protection_enabled" {
  description = "Proteção de branch habilitada para main"
  value       = github_branch_protection.main.pattern
}

output "actions_url" {
  description = "URL para visualizar GitHub Actions"
  value       = "${data.github_repository.fastapi_pro.html_url}/actions"
}

output "setup_instructions" {
  description = "Próximos passos após aplicar o Terraform"
  value       = <<-EOT
    ✅ Terraform aplicado com sucesso!
    
    Próximos passos:
    1. Acesse: ${data.github_repository.fastapi_pro.html_url}/actions
    2. Verifique se o workflow está funcionando
    3. Faça um commit para testar o CI/CD
    4. Configure o Codecov se necessário: https://codecov.io/
    
    Recursos criados:
    - Workflow de CI/CD em .github/workflows/tests.yml
    - Proteção de branch para 'main'
    - Verificações obrigatórias de status
  EOT
}