#!/bin/bash

# AI Tutor Development Startup Script
# Starts both frontend and backend together for development

echo "🚀 Starting AI Tutor Development Environment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend_python" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Project structure verified ✅"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

print_success "Python version check passed: $python_version"

# Check Node.js version
node_version=$(node --version 2>&1 | cut -d'v' -f2 | cut -d. -f1)
required_node_version="18"

if [ "$node_version" -lt "$required_node_version" ]; then
    print_error "Node.js 18+ is required. Current version: $(node --version)"
    exit 1
fi

print_success "Node.js version check passed: $(node --version)"

# Check if .env file exists in backend
if [ ! -f "backend_python/.env" ]; then
    print_warning ".env file not found in backend_python/"
    if [ -f "backend_python/env.example" ]; then
        print_status "Copying env.example to .env..."
        cp backend_python/env.example backend_python/.env
        print_warning "Please update backend_python/.env with your OpenAI API key"
    else
        print_error "env.example file not found. Please create .env file manually"
        exit 1
    fi
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" backend_python/.env 2>/dev/null; then
    print_warning "OpenAI API key not set in backend_python/.env"
    print_warning "The system will work with mock responses until you add a real API key"
fi

# Install dependencies if needed
print_status "Checking dependencies..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing root dependencies..."
    npm install
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    print_status "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# Check if Python dependencies are installed
if ! python3 -c "import fastapi, chromadb, openai" 2>/dev/null; then
    print_status "Installing Python dependencies..."
    pip3 install -r backend_python/requirements.txt
fi

print_success "Dependencies check completed ✅"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backend_python/chroma_db
mkdir -p backend_python/temp_uploads
mkdir -p backend_python/logs

print_success "Directory setup completed ✅"

echo ""
echo "🎯 Starting Development Servers..."
echo "================================="
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔄 WebSocket: ws://localhost:8000/ws/chat"
echo ""
echo "🌐 Frontend: http://localhost:3001 (or check terminal for actual port)"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start both servers using concurrently
npx concurrently \
    --kill-others \
    --prefix "[{name}]" \
    --prefix-colors "cyan,magenta" \
    --names "backend,frontend" \
    "cd backend_python && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" \
    "cd frontend && npm run dev"

print_success "Development environment started! 🎉"
