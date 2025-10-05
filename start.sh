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

npm run dev
