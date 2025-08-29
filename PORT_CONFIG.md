# CronPilot Port Configuration

## 🌐 Current Configuration

**Port**: 7000 (within your requested range 6666-7777)

## 🔧 How to Change Port

### Method 1: Edit config.yaml (Recommended)
```yaml
server:
  host: "0.0.0.0"
  port: 7000  # Change this to any port between 6666-7777
```

### Method 2: Environment Variable
```bash
export CRONPILOT_PORT=7000
```

### Method 3: Command Line
```bash
python3 -m app.main --port 7000
```

## 📋 Available Ports in Range

You can use any port between **6666** and **7777**:

- 6666 - 6999: Available
- **7000** - Current port (recommended)
- 7001 - 7777: Available

## 🚀 Quick Port Changes

### Change to Port 6666:
```bash
sed -i 's/port: 7000/port: 6666/' config.yaml
```

### Change to Port 7777:
```bash
sed -i 's/port: 7000/port: 7777/' config.yaml
```

### Change to Random Port in Range:
```bash
# Generate random port between 6666-7777
RANDOM_PORT=$((6666 + RANDOM % 1112))
sed -i "s/port: 7000/port: $RANDOM_PORT/" config.yaml
echo "Port changed to: $RANDOM_PORT"
```

## 🔍 Verify Port Configuration

After changing the port, restart the application and verify:

```bash
# Restart application
pkill -f "python3 -m app.main"
python3 -m app.main

# Test health endpoint
curl http://localhost:NEW_PORT/health

# Test admin panel
curl -u admin:admin123 http://localhost:NEW_PORT/admin
```

## 📊 Current System Status

- ✅ **Port**: 7000
- ✅ **Host**: 0.0.0.0 (accessible from any IP)
- ✅ **Status**: Running and tested
- ✅ **Admin Panel**: http://localhost:7000/admin
- ✅ **API Docs**: http://localhost:7000/docs
- ✅ **Health Check**: http://localhost:7000/health

## 🎯 Recommended Ports

- **7000**: Current (recommended)
- **6666**: Alternative option
- **7777**: Alternative option
- **7500**: Middle of range

## 🔒 Security Note

The system is configured to bind to `0.0.0.0` which makes it accessible from any IP address. For production use, consider:

1. Using a reverse proxy (nginx, Apache)
2. Configuring firewall rules
3. Using `127.0.0.1` for local-only access
4. Implementing additional security measures 