#!/bin/bash

# Multi-Service Automation Platform Setup Script

set -e

echo "🚀 Setting up Multi-Service Automation Platform..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -e .

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials before running the application"
fi

# Create credentials directory
mkdir -p credentials

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "2. Place your Google credentials.json in the credentials/ directory"
echo "3. Run: docker-compose up -d"
echo "4. Or run locally: uvicorn app.main:app --reload"
echo ""
echo "📚 Documentation: http://localhost:8000/docs"
echo "🔗 WebSocket: ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN"
