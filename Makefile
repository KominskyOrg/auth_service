# Makefile

# Directory where Terraform configurations are located
TF_DIR = tf

# Default goal
.DEFAULT_GOAL := help

# Terraform commands
init: ## Initialize Terraform, install providers
	terraform -chdir=$(TF_DIR) init

validate: ## Validate Terraform files
	terraform -chdir=$(TF_DIR) validate

fmt: ## Format Terraform files
	terraform -chdir=$(TF_DIR) fmt -recursive

plan: ## Plan Terraform changes
	terraform -chdir=$(TF_DIR) plan

apply: ## Apply Terraform changes
	terraform -chdir=$(TF_DIR) apply

destroy: ## Destroy Terraform-managed infrastructure
	terraform -chdir=$(TF_DIR) destroy

clean: ## Remove all generated files
	rm -f $(TF_PLAN_FILE)

output: ## Show Terraform outputs
	terraform -chdir=$(TF_DIR) output

.PHONY: test

test:
	@echo "Running tests..."
	@echo "No tests implemented yet."
	@exit 0