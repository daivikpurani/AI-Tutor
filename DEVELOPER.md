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
cp env.example .env

# Configure environment variables
# Edit .env with your API keys

# Start development servers
npm run dev

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Development Environment Setup

### Prerequisites

- **Node.js**: >= 18.0.0
- **Python**: >= 3.9.0
- **npm**: Latest stable version
- **pip**: Latest stable version
- **Git**: Latest version

### Required API Keys

Before starting development, obtain the following API keys:

1. **OpenAI API Key** (Primary LLM)
   - Sign up at: https://platform.openai.com/
   - Create API key in dashboard
   - Add to `.env` as `OPENAI_API_KEY`

2. **Pinecone API Key** (Vector Database)
   - Sign up at: https://www.pinecone.io/
   - Create project and get API key
   - Add to `.env` as `PINECONE_API_KEY`

3. **ChaiJibri API Key** (Alternative LLM)
   - Sign up at: https://chaibri.com/
   - Get API key from dashboard
   - Add to `.env` as `CHAIBRI_API_KEY`

### Installation Steps

#### Option 1: Automated Setup (Recommended)
```bash
npm run setup
```

#### Option 2: Manual Setup
```bash
# Install root dependencies
npm install

# Install backend dependencies
   cd backend_python && pip install -r requirements.txt && cd ..

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install Python dependencies
pip install -r scripts/requirements.txt
```

### Environment Configuration

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` with your actual API keys and configuration:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
PINECONE_API_KEY=your-pinecone-key-here
CHAIBRI_API_KEY=your-chaibri-key-here

# Database (optional for development)
MONGODB_URI=mongodb://localhost:27017/ai-tutor
DATABASE_URL=postgresql://username:password@localhost:5432/ai_tutor

# Server Configuration
PORT=3001
NODE_ENV=development
REACT_APP_API_URL=http://localhost:8000
```

## Project Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Python        │
│   (React)       │◄──►│   (Node.js)     │◄──►│   Scripts       │
│   Port: 3000    │    │   Port: 3001    │    │   (AI/ML)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chatbot UI    │    │   REST API      │    │   Document       │
│   - Messages    │    │   - /api/chat   │    │   Processing     │
│   - Input       │    │   - /api/upload │    │   - Chunking     │
│   - History     │    │   - /api/health │    │   - Embeddings   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

#### Frontend (React)
- **Location**: `frontend/`
- **Port**: 3000
- **Main Component**: `src/App.jsx`
- **Styling**: `src/App.css`
- **Proxy**: Configured to proxy API calls to backend

#### Backend (Node.js/Express)
- **Location**: `backend/`
- **Port**: 3001
- **Main File**: `index.js`
- **Routes**:
  - `GET /` - Health check
  - `POST /api/chat` - Chat endpoint
  - `POST /api/upload` - File upload
  - `GET /api/health` - System health

#### Python Scripts
- **Location**: `scripts/`
- **chunker.py**: Document processing and chunking
- **query_handler.py**: LLM query processing
- **requirements.txt**: Python dependencies

## API Documentation

### Backend API Endpoints

#### Health Check
```http
GET /
```
**Response:**
```json
{
  "message": "Ai-Tutor Backend API",
  "status": "running",
  "version": "1.0.0"
}
```

#### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "What is machine learning?",
  "userId": "user123"
}
```

**Response:**
```json
{
  "message": "Based on the course material, here's what I found...",
  "userId": "user123",
  "timestamp": "2024-01-01T12:00:00.000Z",
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
  "message": "File upload endpoint - placeholder",
  "status": "success"
}
```

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Python Scripts API

#### Document Chunker
```python
from chunker import DocumentChunker

chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_text("Your document text here...")
```

#### Query Handler
```python
from query_handler import QueryHandler

handler = QueryHandler()
response = handler.process_query("What is AI?", user_id="user123")
```

## Database Schema

### Current Status
- **Database**: Not yet implemented
- **Storage**: File-based for development
- **Future**: MongoDB/PostgreSQL integration planned

### Planned Schema

#### Users Collection
```javascript
{
  _id: ObjectId,
  userId: String,
  email: String,
  role: String, // 'student', 'instructor', 'admin'
  createdAt: Date,
  lastActive: Date
}
```

#### Conversations Collection
```javascript
{
  _id: ObjectId,
  userId: String,
  messages: [{
    role: String, // 'user', 'assistant'
    content: String,
    timestamp: Date
  }],
  createdAt: Date,
  updatedAt: Date
}
```

#### Documents Collection
```javascript
{
  _id: ObjectId,
  filename: String,
  filePath: String,
  chunks: [{
    chunkId: Number,
    text: String,
    embeddings: [Number],
    metadata: Object
  }],
  uploadedBy: String,
  uploadedAt: Date
}
```

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
npm run setup            # Install all dependencies
npm run python:chunker   # Test document chunker
npm run python:query     # Test query handler
npm run python:test      # Run Python tests
npm run clean            # Remove all node_modules
npm run fresh-install    # Clean and reinstall everything
```

#### Backend Scripts
```bash
cd backend_python
python main.py              # Start development server
uvicorn main:app --reload   # Alternative with auto-reload
npm run test             # Run Jest tests
npm run test:watch       # Run tests in watch mode
```

#### Frontend Scripts
```bash
cd frontend
npm start                # Start development server
npm run build            # Build for production
npm run test             # Run React tests
npm run eject            # Eject from Create React App
```

### Code Structure

#### Frontend Structure
```
frontend/
├── src/
│   ├── App.jsx          # Main chatbot component
│   ├── App.css          # Chatbot styles
│   ├── index.js         # React entry point
│   └── index.css        # Global styles
├── public/
│   └── index.html       # HTML template
└── package.json         # Dependencies
```

#### Backend Structure
```
backend/
├── index.js             # Express server
└── package.json         # Dependencies
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
- Integration tests for database operations
- Mock tests for external API calls

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
- **Environment**: Local development only
- **CI/CD**: Not implemented
- **Cloud**: Not configured

### Future Deployment Plan

#### Docker Setup
```dockerfile
# Dockerfile (planned)
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

#### Environment Variables for Production
```env
NODE_ENV=production
PORT=3001
OPENAI_API_KEY=prod-key
PINECONE_API_KEY=prod-key
DATABASE_URL=prod-database-url
```

#### Deployment Commands
```bash
# Build frontend
npm run build

# Start production server
npm start

# Run with PM2 (process manager)
pm2 start backend_python/main.py --name "ai-tutor"
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Error: Port 3000 or 3001 already in use
# Solution: Kill processes using the ports
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

#### 2. Python Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Install Python dependencies
pip install -r scripts/requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r scripts/requirements.txt
```

#### 3. API Connection Issues
```bash
# Error: Cannot connect to backend
# Solution: Check if backend is running
curl http://localhost:8000/api/health

# Check environment variables
cat .env | grep REACT_APP_API_URL
```

#### 4. Missing Dependencies
```bash
# Error: Cannot find module
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# For Python
pip install --upgrade -r scripts/requirements.txt
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
DEBUG=* npm run dev:backend

# Or with specific debug namespace
DEBUG=ai-tutor:* npm run dev:backend
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
python3 -m pdb chunker.py

# Or add debug prints
import pdb; pdb.set_trace()
```

### Log Files

#### Backend Logs
- **Location**: `./logs/ai-tutor.log`
- **Level**: Set by `LOG_LEVEL` environment variable
- **Rotation**: Configured for daily rotation

#### Frontend Logs
- **Browser Console**: F12 → Console tab
- **Network Tab**: F12 → Network tab for API calls

## Contributing Guidelines

### Code Standards

#### JavaScript/Node.js
- Use ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable names
- Add JSDoc comments for functions
- Use async/await instead of callbacks

#### Python
- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings for functions and classes
- Use meaningful variable names
- Handle exceptions properly

#### React
- Use functional components with hooks
- Use meaningful component names
- Keep components small and focused
- Use PropTypes or TypeScript for type checking
- Follow React best practices

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
- [React Documentation](https://reactjs.org/docs/)
- [Express.js Documentation](https://expressjs.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)

### Development Tools
- **IDE**: VS Code with React and Python extensions
- **API Testing**: Postman or Insomnia
- **Database**: MongoDB Compass or pgAdmin
- **Version Control**: Git with GitHub

### Support
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Update this file for new features

---

*Last updated: January 2024*
*Version: 1.0.0*
