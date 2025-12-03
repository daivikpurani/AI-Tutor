#!/bin/bash

# Quick Start Script for AI Tutor
# Simple script to start both frontend and backend

echo "🚀 Starting AI Tutor (Quick Start)..."
echo "====================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend_python" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"

# Check if Ollama is running, start if not
echo "🔍 Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️ Ollama is not running. Starting Ollama service..."
    if command -v ollama > /dev/null 2>&1; then
        # Start Ollama in the background
        ollama serve > /dev/null 2>&1 &
        OLLAMA_PID=$!
        # Wait a moment for Ollama to start
        sleep 2
        # Verify it started successfully
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama service started successfully (PID: $OLLAMA_PID)"
        else
            echo "⚠️ Ollama may still be starting up. Continuing..."
        fi
    else
        echo "⚠️ Ollama command not found. Please install Ollama from https://ollama.ai/"
        echo "⚠️ Continuing without Ollama..."
    fi
else
    echo "✅ Ollama service is already running"
fi

# Kill any existing processes on our ports to prevent "address in use" errors
echo "🧹 Cleaning up existing processes..."
if [ -f "scripts/kill-processes.sh" ]; then
    bash scripts/kill-processes.sh
else
    echo "⚠️ Process cleanup script not found, continuing anyway..."
fi

# Start both servers using npm script
echo "🎯 Starting both servers..."
echo ""
echo "📡 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🧹 Shutting down servers..."
    # Kill Ollama if we started it
    if [ -n "$OLLAMA_PID" ]; then
        echo "🛑 Stopping Ollama service (PID: $OLLAMA_PID)..."
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

npm run dev
