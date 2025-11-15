# Docker Deployment Guide

Complete guide for running DBRefactor AI Agent using Docker containers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development Mode](#development-mode)
- [Docker Commands](#docker-commands)
- [Services](#services)
- [Networking](#networking)
- [Volumes](#volumes)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Prerequisites

- **Docker** 20.10+ installed ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- **Minimum System Requirements**:
  - 4 GB RAM
  - 10 GB disk space
  - 2 CPU cores

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd DBRefactor_AI_Agent

# Create environment file
cp .env.docker .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 2. Start the Application

**Option A: Using Make (Recommended)**

```bash
# Start all services
make up

# View logs
make logs

# Stop services
make down
```

**Option B: Using Docker Compose**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Option C: Using Helper Script**

```bash
# Run interactive setup script
./scripts/docker-setup.sh
```

### 3. Access the Application

- **Web UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.docker .env
```

**Key Configuration Options**:

```env
# Source Database (Your Oracle database)
SOURCE_DB_HOST=your-oracle-server.com
SOURCE_DB_PORT=1521
SOURCE_DB_USER=your_user
SOURCE_DB_PASSWORD=your_password

# Target Database (PostgreSQL - uses Docker)
TARGET_DB_HOST=postgres
TARGET_DB_PORT=5432

# AI API Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

## Running the Application

### Production Mode

Full production deployment with optimized builds:

```bash
# Build and start
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Development Mode

Development mode with hot-reloading:

```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Watch logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.dev.yml down
```

Or using Make:

```bash
make dev        # Start dev mode
make logs       # Watch logs
make dev-down   # Stop dev mode
```

## Docker Commands

### Using Make

```bash
make help           # Show all available commands
make build          # Build all images
make up             # Start services
make down           # Stop services
make restart        # Restart services
make logs           # View all logs
make logs-backend   # View backend logs only
make logs-frontend  # View frontend logs only
make status         # Check service status
make clean          # Remove everything (containers, volumes, networks)
make dev            # Start in development mode
make shell-backend  # Open backend container shell
make shell-frontend # Open frontend container shell
```

### Using Docker Compose Directly

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Restart a specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python -m pytest

# Scale a service
docker-compose up -d --scale backend=3

# Remove everything including volumes
docker-compose down -v
```

## Services

### Backend (FastAPI)

- **Container**: `dbrefactor-backend`
- **Port**: 8000
- **Image**: Built from `./Dockerfile`
- **Health Check**: `/api/v1/health`

**Access backend shell**:
```bash
docker-compose exec backend /bin/bash
```

**Run Python commands**:
```bash
docker-compose exec backend python -c "print('Hello')"
```

### Frontend (Next.js)

- **Container**: `dbrefactor-frontend`
- **Port**: 3000
- **Image**: Built from `./ui/Dockerfile`
- **Health Check**: HTTP GET on port 3000

**Access frontend shell**:
```bash
docker-compose exec frontend /bin/sh
```

### PostgreSQL

- **Container**: `dbrefactor-postgres`
- **Port**: 5432
- **Database**: postgres
- **User**: postgres
- **Password**: postgres (change in .env)

**Connect to database**:
```bash
docker-compose exec postgres psql -U postgres
```

### MySQL

- **Container**: `dbrefactor-mysql`
- **Port**: 3306
- **Database**: migration_tracker
- **User**: root
- **Password**: mysql (change in .env)

**Connect to database**:
```bash
docker-compose exec mysql mysql -u root -pmysql migration_tracker
```

### Redis

- **Container**: `dbrefactor-redis`
- **Port**: 6379

**Connect to Redis**:
```bash
docker-compose exec redis redis-cli
```

## Networking

All services are connected via the `dbrefactor-network` bridge network.

**Internal service communication**:
- Frontend → Backend: `http://backend:8000`
- Backend → PostgreSQL: `postgres:5432`
- Backend → MySQL: `mysql:3306`
- Backend → Redis: `redis:6379`

## Volumes

### Persistent Data

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep dbrefactor

# Inspect a volume
docker volume inspect dbrefactor_postgres-data

# Backup a volume
docker run --rm -v dbrefactor_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .

# Restore a volume
docker run --rm -v dbrefactor_postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /data
```

### Volume Locations

- `backend-data`: Application data
- `postgres-data`: PostgreSQL database
- `mysql-data`: MySQL database
- `redis-data`: Redis cache

## Troubleshooting

### Services Won't Start

**Check logs**:
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common issues**:

1. **Port already in use**:
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000

   # Kill the process or change ports in docker-compose.yml
   ```

2. **Build failures**:
   ```bash
   # Clean build
   docker-compose build --no-cache
   ```

3. **Database connection issues**:
   ```bash
   # Check if databases are healthy
   docker-compose ps

   # Restart databases
   docker-compose restart postgres mysql
   ```

### Container Keeps Restarting

```bash
# View container logs
docker logs dbrefactor-backend

# Check health status
docker inspect dbrefactor-backend | grep -A 10 Health
```

### Out of Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Database Migrations

```bash
# Run migrations
make migrate

# Create new migration
make migration
```

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
make clean

# Or
docker-compose down -v

# Remove all Docker resources
docker system prune -a --volumes
```

## Production Deployment

### Security Best Practices

1. **Change default passwords** in `.env`:
   ```env
   TARGET_DB_PASSWORD=strong-password-here
   APP_DB_PASSWORD=strong-password-here
   ```

2. **Use secrets management**:
   - Use Docker secrets for sensitive data
   - Or use external secrets manager (HashiCorp Vault, AWS Secrets Manager)

3. **Enable HTTPS**:
   - Use the Nginx profile with SSL certificates
   - Update `nginx/nginx.conf` with your SSL config

4. **Limit container resources**:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

### Using Nginx Reverse Proxy

```bash
# Create SSL certificates directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp your-cert.crt nginx/ssl/
cp your-key.key nginx/ssl/

# Start with Nginx
docker-compose --profile with-nginx up -d
```

### Scaling Services

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Use load balancer (add to docker-compose.yml)
```

### Monitoring

```bash
# View resource usage
docker stats

# View specific service stats
docker stats dbrefactor-backend
```

### Backup Strategy

**Automated backup script**:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U postgres postgres > $BACKUP_DIR/postgres.sql

# Backup MySQL
docker-compose exec -T mysql mysqldump -u root -pmysql migration_tracker > $BACKUP_DIR/mysql.sql

# Backup volumes
docker run --rm -v dbrefactor_backend-data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/backend-data.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
```

### Environment-Specific Configs

```bash
# Production
docker-compose -f docker-compose.yml up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d

# Development
docker-compose -f docker-compose.dev.yml up -d
```

## Advanced Usage

### Custom Docker Network

```bash
# Create custom network
docker network create dbrefactor-custom

# Use in docker-compose.yml
networks:
  default:
    external:
      name: dbrefactor-custom
```

### Health Checks

All services have health checks configured. View health status:

```bash
docker inspect dbrefactor-backend | grep -A 20 Health
```

### Logs Management

```bash
# Limit log size in docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Open an issue on GitHub
- Consult the main README.md

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js Docker](https://nextjs.org/docs/deployment#docker-image)
