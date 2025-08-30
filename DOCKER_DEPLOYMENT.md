# CronPilot Docker Deployment Guide

## Quick Start

### 1. Simple Deployment (Recommended for testing)
```bash
# Build and run with simple setup
docker-compose -f docker-compose.simple.yml up -d

# Access the application
# URL: http://localhost:7000/admin
# Username: admin
# Password: admin123
```

### 2. Development Setup
```bash
# Development with hot reloading
docker-compose up -d

# View logs
docker-compose logs -f cronpilot
```

### 3. Production Deployment
```bash
# Production setup with PostgreSQL
docker-compose -f docker-compose.prod.yml up -d

# With SSL/TLS
docker-compose -f docker-compose.prod.yml -f docker-compose.ssl.yml up -d
```

## Deployment Options

### 🚀 Simple Deployment
**File**: `docker-compose.simple.yml`
**Use case**: Testing, development, single-server deployment

```bash
# Start
docker-compose -f docker-compose.simple.yml up -d

# Stop
docker-compose -f docker-compose.simple.yml down

# View logs
docker-compose -f docker-compose.simple.yml logs -f
```

**Features**:
- Single container setup
- SQLite database (persistent)
- Mounted tasks and logs directories
- Health checks enabled

### 🏭 Production Deployment
**File**: `docker-compose.prod.yml`
**Use case**: Production servers, high availability

```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# With custom environment variables
POSTGRES_PASSWORD=your_secure_password docker-compose -f docker-compose.prod.yml up -d
```

**Features**:
- PostgreSQL database
- Nginx reverse proxy
- Resource limits
- Security headers
- Rate limiting

### 🔒 SSL/TLS Setup
**File**: `docker-compose.ssl.yml`
**Use case**: Secure HTTPS deployment

```bash
# 1. Update domain in docker-compose.ssl.yml
# 2. Create SSL certificates
docker-compose -f docker-compose.ssl.yml --profile ssl-setup up certbot

# 3. Start with SSL
docker-compose -f docker-compose.ssl.yml up -d
```

**Features**:
- Let's Encrypt certificates
- Automatic SSL renewal
- HTTPS redirect
- Security headers

### 📊 Monitoring Setup
**File**: `docker-compose.monitoring.yml`
**Use case**: Production monitoring and alerting

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
# URL: http://localhost:3000
# Username: admin
# Password: admin
```

**Features**:
- Prometheus metrics collection
- Grafana dashboards
- Node exporter for system metrics
- Pre-configured dashboards

## Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=cronpilot
POSTGRES_DB=cronpilot

# Application
TZ=UTC
DEBUG=0
PYTHONOPTIMIZE=1

# SSL
DOMAIN=your-domain.com
EMAIL=your-email@example.com
```

### Volume Mounts

The Docker setup mounts several directories:

- `./tasks` → `/app/tasks` - Task files and environments
- `./logs` → `/app/logs` - Application logs
- `./config.yaml` → `/app/config.yaml` - Configuration file
- `cronpilot_data` → `/app` - Database and persistent data

### Network Configuration

- **Simple**: Single container, port 7000
- **Production**: Internal network, Nginx proxy
- **SSL**: HTTPS on port 443, HTTP redirect on port 80

## Management Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Execute commands in container
docker-compose exec cronpilot python -c "print('Hello from container')"
```

### Database Operations
```bash
# Backup database
docker-compose exec cronpilot cp cronpilot.db cronpilot.db.backup

# Restore database
docker-compose exec cronpilot cp cronpilot.db.backup cronpilot.db

# Access PostgreSQL (if using)
docker-compose exec postgres psql -U cronpilot -d cronpilot
```

### Task Management
```bash
# Add new task files
cp my_task.py ./tasks/

# Create virtual environment for task
docker-compose exec cronpilot bash -c "cd /app/tasks && python -m venv my_task_env"

# Install requirements
docker-compose exec cronpilot bash -c "cd /app/tasks/my_task_env && pip install -r ../requirements.txt"
```

## Security Considerations

### Production Security
1. **Change default passwords**:
   ```bash
   # Update config.yaml
   admin:
     username: "your_admin_username"
     password: "your_secure_password"
   ```

2. **Use environment variables**:
   ```bash
   export POSTGRES_PASSWORD="your_secure_password"
   ```

3. **Enable SSL/TLS**:
   ```bash
   docker-compose -f docker-compose.prod.yml -f docker-compose.ssl.yml up -d
   ```

4. **Network isolation**:
   - Use internal networks
   - Expose only necessary ports
   - Use reverse proxy for external access

### Backup Strategy
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec cronpilot cp cronpilot.db cronpilot.db.backup
docker cp cronpilot-app:/app/cronpilot.db.backup $BACKUP_DIR/cronpilot_$DATE.db

# Backup tasks
tar -czf $BACKUP_DIR/tasks_$DATE.tar.gz tasks/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

echo "Backup completed: $BACKUP_DIR/"
EOF

chmod +x backup.sh
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :7000

# Kill the process or change port in docker-compose.yml
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER ./tasks ./logs

# Or run with proper user
docker-compose exec cronpilot chown -R cronpilot:cronpilot /app
```

#### 3. Database Connection Issues
```bash
# Check database status
docker-compose exec cronpilot python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# Recreate database
docker-compose down -v
docker-compose up -d
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
docker-compose exec nginx nginx -t

# Renew certificates
docker-compose -f docker-compose.ssl.yml run --rm certbot renew
```

### Log Analysis
```bash
# View application logs
docker-compose logs -f cronpilot

# View nginx logs
docker-compose logs -f nginx

# View database logs
docker-compose logs -f postgres

# Search for errors
docker-compose logs | grep -i error
```

## Performance Tuning

### Resource Limits
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### Database Optimization
```bash
# PostgreSQL tuning (if using)
docker-compose exec postgres psql -U cronpilot -d cronpilot -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
"
```

### Monitoring Setup
```bash
# Start monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana dashboards
# URL: http://localhost:3000
# Username: admin
# Password: admin
```

## Scaling

### Horizontal Scaling
```bash
# Scale application containers
docker-compose up -d --scale cronpilot=3

# Use load balancer
docker-compose -f docker-compose.prod.yml up -d
```

### Database Scaling
```bash
# Use external database
# Update config.yaml
database:
  url: "postgresql://user:pass@external-db:5432/cronpilot"
```

## Maintenance

### Regular Maintenance Tasks
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f

# Clean up old volumes
docker volume prune -f

# Update application
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Manual health check
curl -f http://localhost:7000/health

# Check all services
docker-compose exec cronpilot python -c "
import requests
print('Health:', requests.get('http://localhost:7000/health').json())
"
```

## Support

For issues and support:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `docker-compose exec cronpilot curl localhost:7000/health`
4. Check resource usage: `docker stats`

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start services |
| `docker-compose down` | Stop services |
| `docker-compose logs -f` | View logs |
| `docker-compose restart` | Restart services |
| `docker-compose exec cronpilot bash` | Access container |
| `docker-compose ps` | Check status |
| `docker-compose pull` | Update images |
| `docker-compose build` | Rebuild images |
