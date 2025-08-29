#!/bin/bash

echo "🚀 Starting CronPilot Task Management System"
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists (optional)
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f "requirements_installed" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    touch requirements_installed
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs tasks templates static

# Check if config file exists
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found. Please create it first."
    exit 1
fi

# Start the application
echo "🌐 Starting CronPilot server..."
echo "   Admin Panel: http://localhost:7000/admin"
echo "   API Docs: http://localhost:7000/docs"
echo "   Health Check: http://localhost:7000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="

python3 -m app.main 