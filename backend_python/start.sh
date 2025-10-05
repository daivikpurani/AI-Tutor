#!/bin/bash

# AI Tutor FastAPI Backend Startup Script
# This script sets up and starts the FastAPI backend with all dependencies

echo "🚀 Starting AI Tutor FastAPI Backend Setup..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Kill any existing processes on port 8000 to prevent "address in use" errors
echo "🧹 Cleaning up existing processes on port 8000..."
if [ -f "../scripts/kill-processes.sh" ]; then
    bash ../scripts/kill-processes.sh
else
    echo "⚠️ Process cleanup script not found, checking port manually..."
    # Simple port cleanup for backend only
    existing_pids=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$existing_pids" ]; then
        echo "Found existing processes on port 8000: $existing_pids"
        for pid in $existing_pids; do
            kill -TERM $pid 2>/dev/null && echo "Killed process $pid"
        done
        sleep 2
        # Force kill if still running
        remaining_pids=$(lsof -ti:8000 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            for pid in $remaining_pids; do
                kill -KILL $pid 2>/dev/null && echo "Force killed process $pid"
            done
        fi
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p chroma_db
mkdir -p temp_uploads
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp env.example .env
    echo "⚠️ Please update .env file with your OpenAI API key and other settings"
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️ Warning: Please set your OpenAI API key in the .env file"
    echo "   The system will work with mock responses until you add a real API key"
fi

echo "🎯 Starting FastAPI server..."
echo "📡 API will be available at: http://localhost:8000"
echo "📖 API documentation at: http://localhost:8000/docs"
echo "🔄 WebSocket endpoint at: ws://localhost:8000/ws/chat"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python main.py
