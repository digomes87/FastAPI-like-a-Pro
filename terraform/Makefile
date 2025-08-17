.PHONY: help init plan apply destroy validate fmt check clean

# Variáveis
TF_VAR_FILE := terraform.tfvars

# Cores para output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

help: ## Mostra esta ajuda
	@echo "$(BLUE)Comandos disponíveis:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'

check-vars: ## Verifica se o arquivo de variáveis existe
	@if [ ! -f $(TF_VAR_FILE) ]; then \
		echo "$(RED)❌ Arquivo $(TF_VAR_FILE) não encontrado!$(RESET)"; \
		echo "$(YELLOW)💡 Copie o arquivo de exemplo:$(RESET)"; \
		echo "   cp terraform.tfvars.example $(TF_VAR_FILE)"; \
		echo "   Depois edite o arquivo com suas configurações."; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Arquivo de variáveis encontrado$(RESET)"

init: ## Inicializa o Terraform
	@echo "$(BLUE)🚀 Inicializando Terraform...$(RESET)"
	terraform init
	@echo "$(GREEN)✅ Terraform inicializado$(RESET)"

validate: init ## Valida a configuração do Terraform
	@echo "$(BLUE)🔍 Validando configuração...$(RESET)"
	terraform validate
	@echo "$(GREEN)✅ Configuração válida$(RESET)"

fmt: ## Formata os arquivos Terraform
	@echo "$(BLUE)🎨 Formatando arquivos...$(RESET)"
	terraform fmt -recursive
	@echo "$(GREEN)✅ Arquivos formatados$(RESET)"

plan: check-vars validate ## Mostra o plano de execução
	@echo "$(BLUE)📋 Gerando plano de execução...$(RESET)"
	terraform plan -var-file=$(TF_VAR_FILE)

apply: check-vars validate ## Aplica as mudanças
	@echo "$(YELLOW)⚠️  Aplicando mudanças...$(RESET)"
	terraform apply -var-file=$(TF_VAR_FILE)
	@echo "$(GREEN)✅ Mudanças aplicadas com sucesso!$(RESET)"

apply-auto: check-vars validate ## Aplica as mudanças automaticamente (sem confirmação)
	@echo "$(YELLOW)⚠️  Aplicando mudanças automaticamente...$(RESET)"
	terraform apply -var-file=$(TF_VAR_FILE) -auto-approve
	@echo "$(GREEN)✅ Mudanças aplicadas com sucesso!$(RESET)"

destroy: check-vars ## Destrói os recursos
	@echo "$(RED)💥 ATENÇÃO: Isso irá destruir todos os recursos!$(RESET)"
	@echo "$(YELLOW)Pressione Ctrl+C para cancelar ou Enter para continuar...$(RESET)"
	@read
	terraform destroy -var-file=$(TF_VAR_FILE)

show: ## Mostra o estado atual
	@echo "$(BLUE)📊 Estado atual dos recursos:$(RESET)"
	terraform show

output: ## Mostra os outputs
	@echo "$(BLUE)📤 Outputs:$(RESET)"
	terraform output

clean: ## Remove arquivos temporários
	@echo "$(BLUE)🧹 Limpando arquivos temporários...$(RESET)"
	rm -rf .terraform/
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate.backup
	rm -f *tfplan*
	@echo "$(GREEN)✅ Limpeza concluída$(RESET)"

setup: ## Configuração inicial completa
	@echo "$(BLUE)🔧 Configuração inicial...$(RESET)"
	@if [ ! -f $(TF_VAR_FILE) ]; then \
		echo "$(YELLOW)📝 Criando arquivo de variáveis...$(RESET)"; \
		cp terraform.tfvars.example $(TF_VAR_FILE); \
		echo "$(GREEN)✅ Arquivo $(TF_VAR_FILE) criado$(RESET)"; \
		echo "$(YELLOW)⚠️  IMPORTANTE: Edite o arquivo $(TF_VAR_FILE) com suas configurações!$(RESET)"; \
	else \
		echo "$(GREEN)✅ Arquivo de variáveis já existe$(RESET)"; \
	fi
	make init
	make validate
	@echo "$(GREEN)🎉 Configuração inicial concluída!$(RESET)"
	@echo "$(BLUE)Próximos passos:$(RESET)"
	@echo "  1. Edite o arquivo $(TF_VAR_FILE) com suas configurações"
	@echo "  2. Execute: make plan"
	@echo "  3. Execute: make apply"

status: ## Mostra o status dos recursos
	@echo "$(BLUE)📊 Status dos recursos:$(RESET)"
	@terraform state list 2>/dev/null || echo "$(YELLOW)Nenhum recurso encontrado$(RESET)"

refresh: ## Atualiza o estado
	@echo "$(BLUE)🔄 Atualizando estado...$(RESET)"
	terraform refresh -var-file=$(TF_VAR_FILE)
	@echo "$(GREEN)✅ Estado atualizado$(RESET)"