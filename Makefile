# Makefile

# Variables
DOCKER_COMPOSE = docker-compose
PIPENV = pipenv run
FLAKE8 = $(PIPENV) flake8
BLACK = $(PIPENV) black
AUTOPEP8 = $(PIPENV) autopep8

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build          Build the Docker images"
	@echo "  make up             Start the Docker containers"
	@echo "  make down           Stop the Docker containers"
	@echo "  make logs           Show logs from the Docker containers"
	@echo "  make lint           Run flake8 for linting"
	@echo "  make lint-fix       Fix linting issues using autopep8"
	@echo "  make format         Run black for code formatting"
	@echo "  make format-fix     Fix code formatting using black"
	@echo "  make test           Run tests"
	@echo "  make clean          Clean up Docker containers and images"

.PHONY: up down build logs lint lint-fix format format-fix test clean

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
