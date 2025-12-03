# 🚀 AI Tutor Startup Scripts

This document explains how to start both the frontend and backend of the AI Tutor system together.

## 📋 Available Startup Methods

### 1. **Quick Start (Recommended)**
```bash
./start.sh
```
- **What it does**: Starts both frontend and backend with minimal setup
- **Best for**: Quick development when everything is already configured
- **Requirements**: Dependencies already installed

### 2. **Full Development Setup**
```bash
./start-dev.sh
```
- **What it does**: Comprehensive setup with dependency checks, environment validation, and colored output
- **Best for**: First-time setup or when you want full validation
- **Features**:
  - ✅ Python version check (3.9+)
  - ✅ Node.js version check (18+)
  - ✅ Dependency installation
  - ✅ Environment file setup
  - ✅ Directory creation
  - ✅ Colored output with status indicators

### 3. **NPM Scripts**
```bash
# Start both frontend and backend
npm run dev

# Start only backend
npm run dev:backend

# Start only frontend  
npm run dev:frontend
```

## 🌐 Server URLs

When both servers are running, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket Chat**: ws://localhost:8000/ws/chat
- **Frontend**: http://localhost:5173

## 🔧 Prerequisites

### Required Software
- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git** (for cloning the repository)

### Required Dependencies
- **Backend**: FastAPI, ChromaDB, OpenAI, etc. (see `backend_python/requirements.txt`)
- **Frontend**: React, Vite, Axios (see `frontend/package.json`)
- **Root**: concurrently (for running both servers)

## ⚙️ Environment Setup

### 1. **Backend Environment**
The backend requires a `.env` file in `backend_python/` directory:

```bash
# Copy the example file
cp backend_python/env.example backend_python/.env

# Edit with your settings
nano backend_python/.env
```

**Required Environment Variables:**
```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
VECTOR_DB_COLLECTION_NAME=ai_tutor_documents
```

### 2. **Install Dependencies**
```bash
# Install all dependencies
npm run install:all

# Or install manually
npm install                    # Root dependencies
cd frontend && npm install    # Frontend dependencies
pip install -r backend_python/requirements.txt  # Backend dependencies
```

## 🎯 Usage Examples

### First Time Setup
```bash
# Clone the repository
git clone <repository-url>
cd FinalProject

# Run full development setup
./start-dev.sh
```

### Daily Development
```bash
# Quick start (if everything is already set up)
./start.sh
```

### Individual Services
```bash
# Backend only
cd backend_python && python3 main.py

# Frontend only  
cd frontend && npm run dev
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill processes on ports 8000 and 5173
   lsof -ti:8000,5173 | xargs kill -9
   ```

2. **Python Dependencies Missing**
   ```bash
   pip install -r backend_python/requirements.txt
   ```

3. **Node Dependencies Missing**
   ```bash
   npm install && cd frontend && npm install
   ```

4. **Environment File Missing**
   ```bash
   cp backend_python/env.example backend_python/.env
   # Edit the .env file with your API keys
   ```

5. **Permission Denied**
   ```bash
   chmod +x start.sh start-dev.sh
   ```

### Logs and Debugging

- **Backend logs**: Check terminal output for FastAPI logs
- **Frontend logs**: Check browser console and terminal output
- **API testing**: Use http://localhost:8000/docs for interactive API testing

## 📁 Project Structure

```
FinalProject/
├── start.sh              # Quick start script
├── start-dev.sh          # Full development setup script
├── package.json          # Root package.json with npm scripts
├── backend_python/       # FastAPI backend
│   ├── main.py          # Backend entry point
│   ├── start.sh         # Backend-only startup script
│   ├── .env             # Backend environment variables
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── package.json     # Frontend dependencies
│   └── src/            # React source code
└── scripts/            # Utility scripts
```

## 🎉 Success Indicators

When everything is working correctly, you should see:

1. **Backend**: `{"message":"Ai-Tutor Backend API","status":"running","version":"1.0.0"}`
2. **Frontend**: React development server running on port 5173
3. **API Docs**: Interactive documentation at http://localhost:8000/docs
4. **Chat**: WebSocket connection working for real-time chat

## 🔄 Development Workflow

1. **Start both servers**: `./start.sh`
2. **Make changes** to frontend or backend code
3. **Hot reload** will automatically restart services
4. **Test changes** in browser or API docs
5. **Stop servers**: `Ctrl+C`

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check that ports 8000 and 5173 are available
4. Ensure environment variables are properly set
5. Review the logs for specific error messages
