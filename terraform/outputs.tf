output "repository_url" {
  description = "URL do repositório GitHub"
  value       = data.github_repository.fastapi_pro.html_url
}

output "repository_clone_url" {
  description = "URL para clonar o repositório"
  value       = data.github_repository.fastapi_pro.ssh_clone_url
}

output "workflow_file_path" {
  description = "Caminho do arquivo de workflow de testes"
  value       = ".github/workflows/tests.yml"
}

output "auto_pr_workflow_path" {
  description = "Caminho do arquivo de workflow de auto-PR"
  value       = github_repository_file.auto_pr_workflow.file
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
  description = "Instruções de configuração pós-aplicação"
  value = <<EOT
✅ Terraform aplicado com sucesso!
    
Próximos passos:
1. Acesse: https://github.com/${data.github_repository.fastapi_pro.name}/actions
2. Crie uma branch 'feature/code' para desenvolvimento
3. Faça commits na branch feature/code
4. O workflow de testes será executado automaticamente
5. Quando os testes passarem, um PR será criado automaticamente para main
6. Configure o Codecov se necessário: https://codecov.io/
    
Recursos criados:
- Workflow de CI/CD em .github/workflows/tests.yml
- Workflow de Auto-PR em ${github_repository_file.auto_pr_workflow.file}
- Proteção de branch para 'main'
- Verificações obrigatórias de status
- Automação de Pull Requests

EOT
}