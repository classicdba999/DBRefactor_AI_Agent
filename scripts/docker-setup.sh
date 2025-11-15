#!/bin/bash

# Docker Setup Script for DBRefactor AI Agent
# This script helps set up and run the application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "DBRefactor AI Agent - Docker Setup"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ No .env file found${NC}"
    echo "Creating .env file from .env.docker template..."
    cp .env.docker .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
    echo ""
fi

# Function to show menu
show_menu() {
    echo "What would you like to do?"
    echo ""
    echo "1) Build and start all services (Production)"
    echo "2) Build and start all services (Development)"
    echo "3) Start services (without rebuilding)"
    echo "4) Stop all services"
    echo "5) View logs"
    echo "6) Restart services"
    echo "7) Clean up (stop and remove containers, networks, volumes)"
    echo "8) Check service status"
    echo "9) Exit"
    echo ""
    read -p "Enter your choice [1-9]: " choice
}

# Function to build and start production
build_and_start_prod() {
    echo -e "${GREEN}Building and starting production services...${NC}"
    docker-compose up --build -d
    echo ""
    echo -e "${GREEN}✓ Services started successfully!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
}

# Function to build and start development
build_and_start_dev() {
    echo -e "${GREEN}Building and starting development services...${NC}"
    docker-compose -f docker-compose.dev.yml up --build -d
    echo ""
    echo -e "${GREEN}✓ Development services started successfully!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
}

# Function to start services
start_services() {
    echo -e "${GREEN}Starting services...${NC}"
    docker-compose up -d
    echo ""
    echo -e "${GREEN}✓ Services started${NC}"
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    docker-compose down
    echo ""
    echo -e "${GREEN}✓ Services stopped${NC}"
}

# Function to view logs
view_logs() {
    echo "Which service logs would you like to view?"
    echo "1) All services"
    echo "2) Backend"
    echo "3) Frontend"
    echo "4) PostgreSQL"
    echo "5) MySQL"
    echo "6) Redis"
    echo ""
    read -p "Enter your choice [1-6]: " log_choice

    case $log_choice in
        1) docker-compose logs -f ;;
        2) docker-compose logs -f backend ;;
        3) docker-compose logs -f frontend ;;
        4) docker-compose logs -f postgres ;;
        5) docker-compose logs -f mysql ;;
        6) docker-compose logs -f redis ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
}

# Function to restart services
restart_services() {
    echo -e "${YELLOW}Restarting services...${NC}"
    docker-compose restart
    echo ""
    echo -e "${GREEN}✓ Services restarted${NC}"
}

# Function to clean up
cleanup() {
    echo -e "${RED}WARNING: This will remove all containers, networks, and volumes${NC}"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}Cleaning up...${NC}"
        docker-compose down -v
        echo ""
        echo -e "${GREEN}✓ Cleanup complete${NC}"
    else
        echo "Cleanup cancelled"
    fi
}

# Function to check status
check_status() {
    echo -e "${GREEN}Service Status:${NC}"
    echo ""
    docker-compose ps
}

# Main loop
while true; do
    show_menu

    case $choice in
        1) build_and_start_prod ;;
        2) build_and_start_dev ;;
        3) start_services ;;
        4) stop_services ;;
        5) view_logs ;;
        6) restart_services ;;
        7) cleanup ;;
        8) check_status ;;
        9) echo "Goodbye!"; exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
    clear
done
