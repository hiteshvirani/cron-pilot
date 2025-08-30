# CronPilot Docker Quickstart

## 🚀 Quick Start

### 1. Simple Deployment
```bash
# Start the application
docker-compose -f docker-compose.simple.yml up -d

# Access: http://localhost:7000/admin
# Username: admin
# Password: admin123
```

### 2. Development Mode
```bash
# Start with hot reloading
docker-compose up -d

# View logs
docker-compose logs -f cronpilot
```

### 3. Production Setup
```bash
# Production with PostgreSQL
docker-compose -f docker-compose.prod.yml up -d

# With SSL
docker-compose -f docker-compose.prod.yml -f docker-compose.ssl.yml up -d
```

## 📁 File Structure

```
CronPilot/
├── Dockerfile                    # Main application container
├── docker-compose.yml            # Full stack (dev/prod)
├── docker-compose.simple.yml     # Simple setup
├── docker-compose.prod.yml       # Production setup
├── docker-compose.ssl.yml        # SSL/TLS setup
├── docker-compose.monitoring.yml # Monitoring stack
├── nginx.conf                    # Nginx configuration
├── .dockerignore                 # Docker ignore file
└── DOCKER_QUICKSTART.md          # This file
```

## 🔧 Management Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Update
docker-compose pull && docker-compose up -d

# Access container
docker-compose exec cronpilot bash
```

## 📊 Monitoring

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana: http://localhost:3000
# Username: admin, Password: admin
```

## 🔒 Security

1. **Change default passwords** in `config.yaml`
2. **Use environment variables** for secrets
3. **Enable SSL/TLS** for production
4. **Use reverse proxy** for external access

## 🆘 Troubleshooting

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Health check
curl http://localhost:7000/health

# Restart services
docker-compose restart
```

## 📈 Scaling

```bash
# Scale application
docker-compose up -d --scale cronpilot=3

# Use external database
# Update config.yaml with external DB URL
```

## 🗄️ Backup

```bash
# Backup database
docker-compose exec cronpilot cp cronpilot.db cronpilot.db.backup

# Backup tasks
tar -czf tasks_backup.tar.gz tasks/

# Backup logs
tar -czf logs_backup.tar.gz logs/
```

## 🎯 Deployment Options

| Setup | File | Use Case |
|-------|------|----------|
| Simple | `docker-compose.simple.yml` | Testing, development |
| Development | `docker-compose.yml` | Development with hot reload |
| Production | `docker-compose.prod.yml` | Production servers |
| SSL | `docker-compose.ssl.yml` | HTTPS deployment |
| Monitoring | `docker-compose.monitoring.yml` | Metrics and dashboards |

## ⚡ Quick Commands

```bash
# Start simple
docker-compose -f docker-compose.simple.yml up -d

# Start production
docker-compose -f docker-compose.prod.yml up -d

# Start with monitoring
docker-compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml up -d

# Stop all
docker-compose down

# View all logs
docker-compose logs -f
```
