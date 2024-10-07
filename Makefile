# Makefile

# Variables
REPO_NAME = auth_service
DOCKER_COMPOSE = docker-compose
PIPENV = pipenv run
FLAKE8 = $(PIPENV) flake8
BLACK = $(PIPENV) black
AUTOPEP8 = $(PIPENV) autopep8

# Terraform Variables
TF_DIR = tf
ENV = staging

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

# Clean up Docker containers and images
clean:
	$(DOCKER_COMPOSE) -f ../devops_admin/docker-compose.yml down --rmi all --volumes --remove-orphans

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

# Variables
ENV ?= staging
BACKEND_DIR ?= ./tf
AWS_REGION ?= us-east-1
IMAGE_TAG ?= $(shell git rev-parse --short HEAD)
AWS_ACCOUNT_ID ?= $(AWS_ACCOUNT_ID)
ECR_REPO := $(REPO_NAME)_$(ENV)

.PHONY: init plan build push ecr-login

# Initialize Terraform
init:
	@echo "Initializing Terraform for $(ENV) environment..."
	cd $(BACKEND_DIR) && terraform init -var env=$(ENV) -backend-config=backend-$(ENV).tfbackend

# Generate Terraform Plan
plan:
	@echo "Generating Terraform plan for $(ENV) environment..."
	cd $(BACKEND_DIR) && terraform plan -out=tfplan -var env=$(ENV) -var image_tag=$(IMAGE_TAG)

# Generate Terraform Apply
apply:
	@echo "Generating Terraform apply for $(ENV) environment..."
	cd $(BACKEND_DIR) && terraform apply tfplan

# Build Docker Image
build:
	@echo "Building Docker image $(ECR_REPO):$(IMAGE_TAG)..."
	docker build -t $(ECR_REPO):$(IMAGE_TAG) -f Dockerfile.$(ENV) .

# Authenticate Docker to Amazon ECR
ecr-login:
	@echo "Logging into Amazon ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

# Push Docker Image to ECR
push: ecr-login build
	@echo "Tagging Docker image..."
	docker tag $(ECR_REPO):$(IMAGE_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO):$(IMAGE_TAG)
	@echo "Pushing Docker image to ECR..."
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO):$(IMAGE_TAG)
