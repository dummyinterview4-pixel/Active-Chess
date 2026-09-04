# Active Chess - Docker Setup Guide

## 🐳 Docker Overview

This guide provides comprehensive instructions for running Active Chess using Docker and Docker Compose.

---

## Prerequisites

- **Docker**: 20.10 or higher
  - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: 2.0 or higher
  - Usually included with Docker Desktop
- **Git**: Latest version
- **Available Ports**: 3000, 8000, 5432, 80, 443

---

## Quick Start (Development)

### 1. Clone and Setup

```bash
git clone https://github.com/balasuresh/active-chess.git
cd active-chess
```

### 2. Configure Environment

```bash
cp .env.docker .env
```

Edit `.env` if needed:
```env
DB_USER=chess_user
DB_PASSWORD=chess_password_dev
DB_NAME=active_chess
SECRET_KEY=your-secret-key-here
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Verify Services

```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS          PORTS
active-chess-db         Up (healthy)    5432/tcp
active-chess-backend    Up              0.0.0.0:8000->8000/tcp
active-chess-frontend   Up              0.0.0.0:3000->3000/tcp
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (chess_user / chess_password_dev)

---

## Development Workflow

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Access Containers

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend bash

# PostgreSQL shell
docker-compose exec postgres psql -U chess_user -d active_chess
```

### Run Commands

```bash
# Backend tests
docker-compose exec backend pytest

# Backend linting
docker-compose exec backend flake8 .

# Frontend tests
docker-compose exec frontend npm test

# Frontend build
docker-compose exec frontend npm run build
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop without removing
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove, and clear volumes
docker-compose down -v
```

---

## Production Deployment

### 1. Prepare Production Environment

```bash
cp .env.docker .env.prod
```

Edit `.env.prod` with production values:
```env
DB_USER=prod_chess_user
DB_PASSWORD=<STRONG_PASSWORD_HERE>
DB_NAME=active_chess_prod
SECRET_KEY=<GENERATE_NEW_SECRET>
API_URL=https://api.yourdomain.com
```

Generate a strong secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Configure Nginx (Optional SSL)

Edit `docker/nginx/nginx.conf`:

Uncomment the HTTPS section and update:
```nginx
server_name your-domain.com;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

Place SSL certificates in `docker/nginx/ssl/` directory.

### 3. Build and Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
```

### 4. Access Application

- **Application**: http://localhost (or your domain)
- **Nginx handles routing** to frontend and backend

---

## Docker Images

### Backend Image

**Development** (`backend/Dockerfile`):
- Based on `python:3.11-slim`
- Installs dependencies from `requirements.txt`
- Runs with `--reload` flag
- Volume mounts for live code changes

**Production** (`backend/Dockerfile.prod`):
- Multi-stage build for smaller image size
- Optimized for production
- No `--reload` flag

### Frontend Image

**Development** (`frontend/Dockerfile`):
- Based on `node:18-alpine`
- Installs dependencies
- Runs dev server
- Volume mounts for live code changes

**Production** (`frontend/Dockerfile.prod`):
- Multi-stage build
- Builds React app
- Uses `serve` to run production build
- Minimal final image size

### Database Image

- **Image**: `postgres:15-alpine`
- **Initialization**: Runs `docker/postgres/init.sql` on first start
- **Volume**: `postgres_data` persists database between runs

---

## Environment Configuration

### Development (`.env.docker`)

```env
# Database
DB_USER=chess_user
DB_PASSWORD=chess_password_dev
DB_NAME=active_chess

# API Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Production API URL (for production compose)
API_URL=https://api.activechess.com
```

### Production (`.env.prod`)

Same variables as development but with:
- Strong database password
- Unique SECRET_KEY
- Production domain in API_URL
- Increased token expiration if needed

---

## Docker Compose Files

### docker-compose.yml (Development)

Services:
1. **postgres** - Database with health checks
2. **backend** - FastAPI app with hot reload
3. **frontend** - React app with hot reload

Features:
- Volume mounts for code changes
- Service health checks
- Environment variable support
- Network isolation

### docker-compose.prod.yml (Production)

Services:
1. **postgres** - Database (no exposed ports)
2. **backend** - FastAPI app (no exposed ports)
3. **frontend** - React app (no exposed ports)
4. **nginx** - Reverse proxy (exposed on 80/443)

Features:
- All services on internal network only
- Nginx handles all external traffic
- Automatic restart policies
- SSL/TLS support ready

---

## Networking

### Development
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │     │   Backend   │     │  Database   │
│ :3000       │────▶│   :8000     │────▶│   :5432     │
└─────────────┘     └─────────────┘     └─────────────┘
        ▲                   ▲                   ▲
        └─────────────────────────────────────┘
           Shared network: chess-network
```

### Production
```
        ┌──────────────┐
        │   Internet   │
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │   Nginx      │
        │   :80/:443   │
        └──────┬───────┘
               │
      ┌────────┴─────────┐
      │                  │
 ┌────▼──────┐    ┌─────▼─────┐
 │ Frontend   │    │  Backend   │
 │ :3000      │    │  :8000     │
 └────┬──────┘    └─────┬──────┘
      │                 │
      └────────┬────────┘
               │
        ┌──────▼──────┐
        │  Database   │
        │  :5432      │
        └─────────────┘
   All on internal network
```

---

## Volumes

### Development

```yaml
postgres_data:        # Database files persist between restarts
./backend:/app        # Backend code mounted for live reload
./frontend:/app       # Frontend code mounted for live reload
/app/node_modules    # Node modules volume (prevents conflicts)
```

### Production

```yaml
postgres_data_prod:   # Database files persist between restarts
```

---

## Health Checks

The docker-compose files include health checks:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U chess_user"]
  interval: 10s
  timeout: 5s
  retries: 5
```

Check container health:
```bash
docker-compose ps  # Shows health status

docker inspect active-chess-db --format='{{.State.Health.Status}}'
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Complete reset
docker-compose down -v
docker-compose up -d
```

### Database Connection Failed

```bash
# Verify database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U chess_user -d active_chess -c "SELECT 1"
```

### Port Already in Use

```bash
# Find process using port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Frontend Can't Connect to Backend

1. Check backend is running:
   ```bash
   docker-compose logs backend
   ```

2. Check REACT_APP_API_URL in `.env`:
   ```bash
   cat .env | grep REACT_APP_API_URL
   ```

3. Verify network connectivity:
   ```bash
   docker-compose exec frontend curl http://backend:8000/docs
   ```

### Database Initialization Failed

```bash
# Check init logs
docker-compose logs postgres

# Reinitialize (WARNING: Deletes data)
docker-compose down -v
docker-compose up -d postgres
```

---

## Performance Optimization

### Memory Limits

Edit `docker-compose.yml` to add memory limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### CPU Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
```

### Database Optimization

Add to `docker-compose.yml`:

```yaml
postgres:
  command:
    - "postgres"
    - "-c"
    - "max_connections=200"
    - "-c"
    - "shared_buffers=256MB"
```

---

## Backup & Recovery

### Backup Database

```bash
docker-compose exec postgres pg_dump -U chess_user active_chess > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U chess_user active_chess < backup.sql
```

### Backup Volumes

```bash
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz /data
```

---

## Monitoring

### Container Metrics

```bash
# CPU, memory, network usage
docker stats

# Memory usage
docker stats --no-stream

# Specific container
docker stats active-chess-backend
```

### Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Timestamps
docker-compose logs -f --timestamps
```

---

## Security

### Change Default Credentials

1. Edit `.env.prod`:
   ```env
   DB_USER=strong_username
   DB_PASSWORD=<VERY_STRONG_PASSWORD>
   SECRET_KEY=<RANDOM_SECRET>
   ```

2. Regenerate and restart:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Enable SSL/TLS

1. Obtain certificates (Let's Encrypt recommended)

2. Place in `docker/nginx/ssl/`

3. Uncomment SSL section in `docker/nginx/nginx.conf`

4. Restart Nginx:
   ```bash
   docker-compose restart nginx
   ```

### Network Security

The production setup uses:
- Internal-only database network
- Nginx reverse proxy for all external traffic
- No direct service exposure
- Automatic health checks

---

## Scaling

### Horizontal Scaling (Multiple Backend Instances)

Edit `docker-compose.prod.yml`:

```yaml
services:
  backend:
    deploy:
      replicas: 3
```

Then restart:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Database Connection Pooling

Add to backend `app/config.py`:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build backend
        run: docker build -f backend/Dockerfile.prod -t backend:latest ./backend
      
      - name: Build frontend
        run: docker build -f frontend/Dockerfile.prod -t frontend:latest ./frontend
      
      - name: Test
        run: docker-compose -f docker-compose.prod.yml up -d
```

---

## Debugging

### Enable Debug Mode

Backend:
```yaml
backend:
  environment:
    DEBUG: "true"
```

Frontend:
```yaml
frontend:
  environment:
    DEBUG: "true"
```

### Access Database Directly

```bash
docker-compose exec postgres psql -U chess_user -d active_chess

# Common queries
\dt                           # List tables
SELECT * FROM users;          # View users
SELECT * FROM courses;        # View courses
\q                            # Quit
```

### View Container Filesystem

```bash
docker-compose exec backend ls -la /app
docker-compose exec frontend ls -la /app
```

---

## Cleanup

### Remove Unused Resources

```bash
# Unused images
docker image prune

# Unused volumes
docker volume prune

# Unused networks
docker network prune

# All unused
docker system prune -a
```

### Complete Cleanup

```bash
# Stop and remove all
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## Advanced Topics

### Custom Networks

```yaml
networks:
  chess-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Docker Registry

Push to private registry:
```bash
docker tag backend:latest registry.example.com/backend:latest
docker push registry.example.com/backend:latest
```

### Secrets Management

Use Docker Compose secrets:
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  backend:
    secrets:
      - db_password
```

---

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Node.js Docker Image](https://hub.docker.com/_/node)
- [Python Docker Image](https://hub.docker.com/_/python)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review this guide
3. Check [GitHub Issues](https://github.com/balasuresh/active-chess/issues)
4. Create a new issue with logs and details

---

**Happy Dockerizing! 🐳**
