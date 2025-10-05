#!/bin/bash

# Script to kill existing processes on AI Tutor ports
# This prevents "address already in use" errors

echo "🔍 Checking for existing processes on AI Tutor ports..."

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

# Function to kill processes on a specific port
kill_port_processes() {
    local port=$1
    local service_name=$2
    
    print_status "Checking port $port for $service_name..."
    
    # Find processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        print_warning "Found existing processes on port $port: $pids"
        
        # Try graceful shutdown first
        print_status "Attempting graceful shutdown..."
        for pid in $pids; do
            if kill -TERM $pid 2>/dev/null; then
                print_status "Sent TERM signal to process $pid"
            fi
        done
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Check if processes are still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            print_warning "Processes still running, forcing shutdown..."
            for pid in $remaining_pids; do
                if kill -KILL $pid 2>/dev/null; then
                    print_status "Force killed process $pid"
                fi
            done
        fi
        
        # Final check
        sleep 1
        local final_pids=$(lsof -ti:$port 2>/dev/null)
        if [ -z "$final_pids" ]; then
            print_success "Successfully freed port $port"
        else
            print_error "Failed to free port $port. Remaining processes: $final_pids"
            return 1
        fi
    else
        print_success "Port $port is free"
    fi
    
    return 0
}

# Kill processes on backend port (8000)
kill_port_processes 8000 "Backend API"

# Kill processes on frontend port (5173 - Vite default)
kill_port_processes 5173 "Frontend Dev Server"

# Also check for common alternative frontend ports
kill_port_processes 3000 "Frontend Dev Server (alt)"
kill_port_processes 3001 "Frontend Dev Server (alt)"

# Kill any Python processes that might be running our backend
print_status "Checking for existing Python backend processes..."
backend_pids=$(pgrep -f "uvicorn.*main:app" 2>/dev/null)
if [ -n "$backend_pids" ]; then
    print_warning "Found existing uvicorn processes: $backend_pids"
    for pid in $backend_pids; do
        if kill -TERM $pid 2>/dev/null; then
            print_status "Killed uvicorn process $pid"
        fi
    done
fi

# Kill any Node processes that might be running our frontend
print_status "Checking for existing Node frontend processes..."
frontend_pids=$(pgrep -f "vite.*dev" 2>/dev/null)
if [ -n "$frontend_pids" ]; then
    print_warning "Found existing Vite processes: $frontend_pids"
    for pid in $frontend_pids; do
        if kill -TERM $pid 2>/dev/null; then
            print_status "Killed Vite process $pid"
        fi
    done
fi

print_success "Process cleanup completed! ✅"
echo ""
