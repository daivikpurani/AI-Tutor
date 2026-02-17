# Ai-Tutor Developer Documentation

This document contains comprehensive technical details for developers working on the Ai-Tutor project. It covers setup, architecture, development workflows, and troubleshooting.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Architecture](#project-architecture)
4. [API Documentation](#api-documentation)
5. [Database Schema](#database-schema)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Contributing Guidelines](#contributing-guidelines)

## Quick Start

```bash
# Clone and setup
git clone https://github.com/daivikpurani/Ai-Tutor.git
cd Ai-Tutor
npm run setup
cp backend_python/.env.example backend_python/.env

# Configure environment variables
# Edit backend_python/.env with your API keys

# Start development servers
npm run dev

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## Development Environment Setup

### Prerequisites

- **Node.js**: >= 18.0.0
- **Python**: 3.11 or 3.12 (required for ChromaDB; 3.14 is not supported)
- **npm**: Latest stable version
- **pip**: Latest stable version
- **Git**: Latest version

### Required API Keys

Before starting development, obtain the following API keys:

1. **OpenAI API Key** (Primary LLM)
   - Sign up at: https://platform.openai.com/
   - Create API key in dashboard
   - Add to `backend_python/.env` as `OPENAI_API_KEY`

2. **Ollama** (Optional - Local LLM)
   - Install Ollama: https://ollama.ai/
   - Download a model: `ollama pull llama2`
   - Configure in `.env` as `OLLAMA_BASE_URL=http://localhost:11434`

### Installation Steps

#### Option 1: Automated Setup (Recommended)
```bash
npm run setup
```

#### Option 2: Manual Setup
```bash
# Install root dependencies
npm install

# Install backend dependencies (use Python 3.11 or 3.12)
cd backend_python && pip install -r requirements.txt && cd ..

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install Python script dependencies (if needed)
pip install -r scripts/requirements.txt
```

**Python version:** ChromaDB and some deps require Python 3.11 or 3.12. If you see Pydantic or ChromaDB errors, create a venv with `python3.11 -m venv venv` and install there. See [CHROMADB_UPGRADE_ISSUES.md](CHROMADB_UPGRADE_ISSUES.md) for details.

### Environment Configuration

Copy the example environment file and configure:

```bash
cp backend_python/.env.example backend_python/.env
```

Edit `backend_python/.env` with your actual API keys and configuration:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here

# Ollama Configuration (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2

# Server Configuration
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
VECTOR_DB_COLLECTION_NAME=ai_tutor_documents

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE=10485760

# Vector Search Configuration
SIMILARITY_THRESHOLD=0.8
MAX_CONTEXT_CHUNKS=5

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Security (optional)
REJECT_ON_INJECTION=false
RATE_LIMIT_CHAT=60/minute
RATE_LIMIT_UPLOAD=10/minute
```

### Security

- **Rate limiting:** Chat and upload endpoints use SlowAPI; limits are configurable via `RATE_LIMIT_CHAT` and `RATE_LIMIT_UPLOAD` in `.env`.
- **Prompt security:** User input is wrapped in delimiters and checked for injection patterns. Set `REJECT_ON_INJECTION=true` to return a safe message instead of calling the LLM when patterns (e.g. "ignore previous instructions") are detected. See `backend_python/utils/prompt_guard.py`.
- **Production:** Set `ENVIRONMENT=production`; the API returns generic error messages and avoids logging prompt/response content.

## Project Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Vector DB     │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│   (ChromaDB)    │
│   Port: 5173    │    │   Port: 8000    │    │   (Local)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chatbot UI    │    │   REST API      │    │   Document       │
│   - Messages    │    │   - /api/chat   │    │   Processing     │
│   - Input       │    │   - /api/upload │    │   - Chunking     │
│   - History     │    │   - /ws/chat    │    │   - Embeddings   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

#### Frontend (React + Vite)
- **Location**: `frontend/`
- **Port**: 5173 (Vite dev)
- **Main Component**: `src/App.jsx`
- **Styling**: `src/App.css`
- **Build Tool**: Vite
- **Proxy**: Configured to proxy API calls to backend

#### Backend (FastAPI)
- **Location**: `backend_python/`
- **Port**: 8000
- **Main File**: `main.py`
- **Framework**: FastAPI with WebSocket support
- **Documentation**: Auto-generated at `/docs`

#### Vector Database (ChromaDB)
- **Location**: `backend_python/chroma_db/`
- **Type**: Local persistent vector database
- **Purpose**: Document embeddings and similarity search

#### Python Scripts
- **Location**: `scripts/`
- **chunker.py**: Document processing and chunking
- **query_handler.py**: LLM query processing
- **requirements.txt**: Python dependencies

## API Documentation

### FastAPI Backend Endpoints

#### Health Check
```http
GET /
```
**Response:**
```json
{
  "message": "Ai-Tutor Backend API",
  "status": "running",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "What is machine learning?",
  "user_id": "user123",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Based on the course material, here's what I found...",
  "query": "What is machine learning?",
  "user_id": "user123",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "context_chunks_used": 3,
  "status": "success"
}
```

#### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

file: [binary data]
```

**Response:**
```json
{
  "message": "Successfully processed document.pdf",
  "filename": "document.pdf",
  "chunks_created": 15,
  "status": "success"
}
```

#### WebSocket Chat
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.send(JSON.stringify({
  "message": "Hello",
  "user_id": "user123"
}));
```

#### Document Management
```http
GET /api/documents          # List all documents
DELETE /api/documents/{id}  # Delete specific document
```

#### Testing Endpoints
```http
GET /api/test-db           # Test database connection
POST /api/test-query       # Test query processing
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

### ChromaDB Vector Database

The system uses ChromaDB as a local persistent vector database for storing document embeddings.

#### Document Storage
```python
# Document chunks are stored with metadata
{
  "id": "document_chunk_1",
  "text": "Document content chunk...",
  "metadata": {
    "filename": "course_material.pdf",
    "chunk_index": 0,
    "page_number": 1,
    "upload_date": "2024-01-01T12:00:00Z"
  },
  "embedding": [0.1, 0.2, 0.3, ...]  # Vector embedding
}
```

#### Collection Structure
- **Collection Name**: `ai_tutor_documents`
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Persistence**: Local SQLite database in `chroma_db/`

## Development Workflow

### Starting Development

#### Option 1: Unified Development
```bash
npm run dev
```
This starts both frontend and backend concurrently.

#### Option 2: Individual Services
```bash
# Terminal 1 - Backend
cd backend_python
python main.py

# Terminal 2 - Frontend
cd frontend
npm start

# Terminal 3 - Python Scripts (as needed)
cd scripts
python3 chunker.py
python3 query_handler.py
```

### Available Scripts

#### Root Level Scripts
```bash
npm run dev              # Start both frontend and backend
npm run dev:all          # Same as npm run dev
npm run dev:backend      # Start backend only
npm run dev:frontend     # Start frontend only
npm run build            # Build frontend for production
npm run test             # Run all tests
npm run test:backend     # Run backend tests
npm run test:frontend    # Run frontend tests
npm run setup            # Install all dependencies
npm run python:test      # Run Python tests
npm run clean            # Remove all node_modules
npm run fresh-install   # Clean and reinstall everything
```

#### Backend Scripts
```bash
cd backend_python
python main.py              # Start development server
uvicorn main:app --reload   # Alternative with auto-reload
python -m pytest           # Run tests
```

#### Frontend Scripts
```bash
cd frontend
npm start                # Start development server
npm run build            # Build for production
npm run preview          # Preview production build
npm test                 # Run tests
```

### Code Structure

#### Frontend Structure
```
frontend/
├── src/
│   ├── App.jsx          # Main chatbot component
│   ├── App.css          # Chatbot styles
│   ├── index.jsx        # React entry point
│   └── index.css        # Global styles
├── public/
│   └── index.html       # HTML template
├── vite.config.js      # Vite configuration
└── package.json         # Dependencies
```

#### Backend Structure
```
backend_python/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── start.sh            # Startup script
├── .env.example        # Environment configuration template
├── services/
│   ├── query_handler.py   # Enhanced query processing with LLM
│   ├── vector_db.py       # ChromaDB integration
│   ├── document_chunker.py # Enhanced document processing
│   └── llm_service.py     # LLM service integration
├── models/
│   └── schemas.py         # Pydantic data models
├── utils/
│   ├── config.py          # Configuration settings
│   └── prompts.py         # LLM prompt templates
└── chroma_db/             # ChromaDB data directory (auto-created)
```

#### Python Scripts Structure
```
scripts/
├── chunker.py           # Document chunking
├── query_handler.py     # LLM query processing
└── requirements.txt     # Python dependencies
```

## Testing

### Backend Testing
```bash
cd backend_python
python -m pytest
```

**Test Structure:**
- Unit tests for API endpoints
- Integration tests for ChromaDB operations
- Mock tests for external API calls
- WebSocket connection tests

### Frontend Testing
```bash
cd frontend
npm test
```

**Test Structure:**
- Component tests for React components
- Integration tests for API calls
- UI tests for user interactions

### Python Testing
```bash
cd scripts
python3 -m pytest
```

**Test Structure:**
- Unit tests for document processing
- Integration tests for LLM APIs
- Mock tests for external services

### Running All Tests
```bash
npm test
```

## Deployment

### Current Status
- **Environment**: Local development
- **Database**: Local ChromaDB
- **CI/CD**: Not implemented
- **Cloud**: Not configured

### Future Deployment Plan

#### Docker Setup
```dockerfile
# Dockerfile (planned)
FROM python:3.9-slim
WORKDIR /app
COPY backend_python/requirements.txt .
RUN pip install -r requirements.txt
COPY backend_python/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Variables for Production
```env
ENVIRONMENT=production
DEBUG=false
PORT=8000
OPENAI_API_KEY=prod-key
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
```

#### Deployment Commands
```bash
# Build frontend
npm run build

# Start production server
cd backend_python
uvicorn main:app --host 0.0.0.0 --port 8000

# Run with PM2 (process manager)
pm2 start backend_python/main.py --name "ai-tutor"
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Error: Port 3000 or 8000 already in use
# Solution: Kill processes using the ports
sslsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

#### 2. Python Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Install Python dependencies
cd backend_python
pip install -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. API Connection Issues
```bash
# Error: Cannot connect to backend
# Solution: Check if backend is running
curl http://localhost:8000/api/health

# Check environment variables
cat backend_python/.env | grep OPENAI_API_KEY
```

#### 4. ChromaDB Issues
```bash
# Error: ChromaDB connection failed
# Solution: Check database directory permissions
ls -la backend_python/chroma_db/

# Reset database if corrupted
rm -rf backend_python/chroma_db/
mkdir backend_python/chroma_db/
```

#### 5. Missing Dependencies
```bash
# Error: Cannot find module
# Solution: Reinstall dependencies
rm -rf node_modules frontend/node_modules package-lock.json frontend/package-lock.json
npm run fresh-install
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
cd backend_python
DEBUG=true python main.py

# Or with uvicorn
uvicorn main:app --reload --log-level debug
```

#### Frontend Debug
```bash
# Enable React DevTools
# Install browser extension
# Or use console.log statements
```

#### Python Debug
```bash
# Enable Python debug mode
cd backend_python
python -m pdb main.py

# Or add debug prints
import pdb; pdb.set_trace()
```

### Log Files

#### Backend Logs
- **Location**: Console output
- **Level**: Set by `LOG_LEVEL` environment variable
- **Format**: Structured JSON logs

#### Frontend Logs
- **Browser Console**: F12 → Console tab
- **Network Tab**: F12 → Network tab for API calls

## Contributing Guidelines

### Code Standards

#### Python (FastAPI)
- Follow PEP 8 style guide
- Use type hints for all functions
- Add docstrings for functions and classes
- Use meaningful variable names
- Handle exceptions properly
- Use async/await for I/O operations

#### JavaScript/React
- Use ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable names
- Add JSDoc comments for functions
- Use functional components with hooks
- Keep components small and focused

### Git Workflow

#### Branch Naming
```bash
feature/add-user-authentication
bugfix/fix-chat-message-display
hotfix/critical-security-patch
```

#### Commit Messages
```bash
# Format: type(scope): description
feat(api): add user authentication endpoint
fix(ui): resolve chat message alignment issue
docs(readme): update installation instructions
```

#### Pull Request Process
1. Create feature branch
2. Make changes with tests
3. Update documentation
4. Create pull request
5. Code review
6. Merge to main

### Development Checklist

#### Before Committing
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No console.log statements
- [ ] No commented code
- [ ] Environment variables documented

#### Before Pull Request
- [ ] Feature complete
- [ ] Tests written and passing
- [ ] README updated
- [ ] API documentation updated
- [ ] No breaking changes
- [ ] Performance tested

### Code Review Guidelines

#### What to Look For
- Code quality and style
- Security vulnerabilities
- Performance issues
- Test coverage
- Documentation completeness
- Error handling

#### Review Process
1. Check code functionality
2. Verify test coverage
3. Review security implications
4. Check performance impact
5. Ensure documentation is updated
6. Approve or request changes

---

## Additional Resources

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Vite Documentation](https://vitejs.dev/)

### Development Tools
- **IDE**: VS Code with Python and React extensions
- **API Testing**: Postman or Insomnia
- **Database**: ChromaDB Studio (if available)
- **Version Control**: Git with GitHub

### Support
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Update this file for new features

---

*Last updated: January 2024*
*Version: 2.0.0 - FastAPI Migration*