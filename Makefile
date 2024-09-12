# Makefile

# Variables
DOCKER_COMPOSE = docker-compose
FLAKE8 = flake8
BLACK = black

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build          Build the Docker images"
	@echo "  make up             Start the Docker containers"
	@echo "  make down           Stop the Docker containers"
	@echo "  make logs           Show logs from the Docker containers"
	@echo "  make lint           Run flake8 for linting"
	@echo "  make format         Run black for code formatting"
	@echo "  make test           Run tests"
	@echo "  make clean          Clean up Docker containers and images"

.PHONY: up down build logs

# Bring up all services
up:
	docker-compose -f ../devops_admin/docker-compose.yml up --build

# Bring down all services
down:
	docker-compose -f ../devops_admin/docker-compose.yml down

# Build all services or a specific service
build:
	@if [ -z "$(service)" ]; then \
		docker-compose -f ../devops_admin/docker-compose.yml build; \
	else \
		docker-compose -f ../devops_admin/docker-compose.yml build $(service); \
	fi

# View logs for all services or a specific service
logs:
	@if [ -z "$(service)" ]; then \
		docker-compose -f ../devops_admin/docker-compose.yml logs -f; \
	else \
		docker-compose -f ../devops_admin/docker-compose.yml logs -f $(service); \
	fi

# Run flake8 for linting
.PHONY: lint
lint:
	$(FLAKE8) .

# Run black for code formatting
.PHONY: format
format:
	$(BLACK) .

# Run tests
.PHONY: test
test:
	$(DOCKER_COMPOSE) run --rm api pytest

# Clean up Docker containers and images
.PHONY: clean
clean:
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans
