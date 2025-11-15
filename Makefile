.PHONY: help build up down restart logs clean status dev

# Default target
help:
	@echo "DBRefactor AI Agent - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build       Build all Docker images"
	@echo "  up          Start all services in production mode"
	@echo "  down        Stop all services"
	@echo "  restart     Restart all services"
	@echo "  logs        View logs from all services"
	@echo "  logs-backend View logs from backend only"
	@echo "  logs-frontend View logs from frontend only"
	@echo "  clean       Stop and remove all containers, networks, and volumes"
	@echo "  status      Show status of all services"
	@echo "  dev         Start all services in development mode"
	@echo "  dev-down    Stop development services"
	@echo "  shell-backend Open shell in backend container"
	@echo "  shell-frontend Open shell in frontend container"
	@echo "  test        Run tests"
	@echo ""

# Build all images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start services in production mode
up:
	@echo "Starting services in production mode..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop services
down:
	@echo "Stopping services..."
	docker-compose down

# Restart services
restart:
	@echo "Restarting services..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# View backend logs
logs-backend:
	docker-compose logs -f backend

# View frontend logs
logs-frontend:
	docker-compose logs -f frontend

# Clean up everything
clean:
	@echo "Cleaning up containers, networks, and volumes..."
	docker-compose down -v
	@echo "Cleanup complete!"

# Check status
status:
	@echo "Service Status:"
	docker-compose ps

# Development mode
dev:
	@echo "Starting services in development mode..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"

# Stop development services
dev-down:
	@echo "Stopping development services..."
	docker-compose -f docker-compose.dev.yml down

# Open shell in backend container
shell-backend:
	docker-compose exec backend /bin/bash

# Open shell in frontend container
shell-frontend:
	docker-compose exec frontend /bin/sh

# Run tests
test:
	docker-compose exec backend pytest

# Build and start (convenience)
rebuild: down build up

# View environment
env-check:
	@echo "Checking environment configuration..."
	@if [ -f .env ]; then \
		echo "✓ .env file exists"; \
	else \
		echo "✗ .env file not found"; \
		echo "  Run: cp .env.docker .env"; \
	fi

# Database migrations (placeholder for when alembic is set up)
migrate:
	docker-compose exec backend alembic upgrade head

# Create new migration
migration:
	@read -p "Enter migration message: " msg; \
	docker-compose exec backend alembic revision --autogenerate -m "$$msg"
