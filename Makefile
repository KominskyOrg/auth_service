# Makefile

# Variables
DOCKER_COMPOSE = docker-compose
PIPENV = pipenv run
FLAKE8 = $(PIPENV) flake8
BLACK = $(PIPENV) black
AUTOPEP8 = $(PIPENV) autopep8

# Terraform Variables
TF_DIR = tf
TFVARS_DEV = dev.tfvars
# TFVARS_DEV_SECRETS = dev.tfvars.secrets
TFVARS_PROD = prod.tfvars
# TFVARS_PROD_SECRETS = prod.tfvars.secrets

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build            Build the Docker images"
	@echo "  make up               Start the Docker containers"
	@echo "  make down             Stop the Docker containers"
	@echo "  make logs             Show logs from the Docker containers"
	@echo "  make lint             Run flake8 for linting"
	@echo "  make lint-fix         Fix linting issues using autopep8"
	@echo "  make format           Run black for code formatting"
	@echo "  make format-fix       Fix code formatting using black"
	@echo "  make test             Run tests"
	@echo "  make clean            Clean up Docker containers and images"
	@echo "  make terraform-init   Initialize Terraform"
	@echo "  make terraform-plan   Run Terraform plan"
	@echo "  make terraform-apply  Apply Terraform changes"
	@echo "  make terraform-destroy Destroy Terraform-managed infrastructure"

.PHONY: up down build logs lint lint-fix format format-fix test clean terraform-init terraform-plan terraform-apply terraform-destroy

# Bring up all services
up:
	$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml up --build

# Bring down all services
down:
	$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml down

# Build all services or a specific service
build:
	@if [ -z "$(service)" ]; then \
		$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml build; \
	else \
		$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml build $(service); \
	fi

# View logs for all services or a specific service
logs:
	@if [ -z "$(service)" ]; then \
		$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml logs -f; \
	else \
		$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml logs -f $(service); \
	fi

# Run flake8 for linting
lint:
	$(FLAKE8) .

# Fix linting issues using autopep8
lint-fix:
	$(AUTOPEP8) --in-place --aggressive --aggressive -r .

# Run black for code formatting
format:
	$(BLACK) .

# Fix code formatting using black
format-fix:
	$(BLACK) .

# Run tests
test:
	$(DOCKER_COMPOSE) run --rm api pytest

# Clean up Docker containers and images
clean:
	$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml down --rmi all --volumes --remove-orphans

# Terraform Targets

# Initialize Terraform
terraform-init:
	@echo "Initializing Terraform..."
	cd $(TF_DIR) && terraform init

# Run Terraform Plan
terraform-plan:
	@echo "Running Terraform plan..."
	@if [ "$(ENV)" = "prod" ]; then \
		cd $(TF_DIR) && terraform plan -var-file=$(TFVARS_PROD); \
	else \
		cd $(TF_DIR) && terraform plan -var-file=$(TFVARS_DEV); \
	fi

# Apply Terraform changes
terraform-apply:
	@echo "Applying Terraform changes..."
	@if [ "$(ENV)" = "prod" ]; then \
		cd $(TF_DIR) && terraform apply -var-file=$(TFVARS_PROD); \
	else \
		cd $(TF_DIR) && terraform apply -var-file=$(TFVARS_DEV); \
	fi

# Destroy Terraform-managed infrastructure
terraform-destroy:
	@echo "Destroying Terraform-managed infrastructure..."
	@if [ "$(ENV)" = "prod" ]; then \
		cd $(TF_DIR) && terraform destroy -var-file=$(TFVARS_PROD); \
	else \
		cd $(TF_DIR) && terraform destroy -var-file=$(TFVARS_DEV); \
	fi
