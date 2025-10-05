#!/bin/bash

# Quick script to kill AI Tutor processes
# Run this if you're having "address already in use" issues

echo "🧹 Killing AI Tutor processes..."

# Kill processes on common ports
for port in 8000 5173 3000 3001; do
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "Killing processes on port $port: $pids"
        kill -TERM $pids 2>/dev/null
        sleep 1
        # Force kill if still running
        remaining=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$remaining" ]; then
            kill -KILL $remaining 2>/dev/null
        fi
    fi
done

# Kill specific process patterns
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "Killed uvicorn processes"
pkill -f "vite.*dev" 2>/dev/null && echo "Killed Vite processes"

echo "✅ Process cleanup completed!"
