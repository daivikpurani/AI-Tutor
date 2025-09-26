# Ai-Tutor

A research-oriented chatbot-based learning assistant system designed to enhance educational experiences through contextual AI tutoring, automated assessment, and comprehensive learning analytics.

## 1. Project Overview

Ai-Tutor is an intelligent tutoring system that leverages conversational AI to provide personalized learning experiences grounded in course-specific content. The system enables instructors to upload educational materials (modules, documents, resources) which are then processed and made available to students through an interactive chatbot interface.

### Core Features

- **Context-Aware Tutoring**: AI-powered chatbot that understands and references uploaded course materials to provide relevant, contextual assistance
- **Automated Grading**: Integrated assessment capabilities through the chat interface, enabling real-time evaluation and feedback
- **Exploratory Learning**: Interactive learning environment that encourages student exploration and discovery
- **Learning Analytics Dashboard**: Comprehensive visualization of learning bottlenecks, performance metrics, and progress tracking (future implementation)
- **Multi-Role Support**: Distinct interfaces and capabilities for students, instructors, and developers

## 2. Tech Stack

### Frontend
- **React**: Modern UI framework for chatbot interface and dashboard components
- **State Management**: Context API / Redux for application state
- **Styling**: CSS-in-JS or styled-components for component styling

### Backend
- **Node.js**: JavaScript runtime for API server and business logic
- **Express.js**: Web framework for RESTful API endpoints
- **Database**: MongoDB/PostgreSQL for user data and conversation history

### AI & Machine Learning
- **Python**: Core language for LLM interactions and data processing
- **LLM Integration**: Support for OpenAI GPT models and ChaiJibri API
- **Vector Storage**: Pinecone for embedding storage and similarity search
- **Document Processing**: Text chunking and embedding generation

## 3. Repository Structure

```
Ai-Tutor/
├── frontend/                 # React application
│   ├── src/
│   │   ├── App.jsx          # Main chatbot component
│   │   ├── App.css          # Chatbot styling
│   │   ├── index.js         # React entry point
│   │   └── index.css        # Global styles
│   ├── public/
│   │   └── index.html       # HTML template
│   └── package.json         # Frontend dependencies
├── backend/                  # Node.js API server
│   ├── index.js             # Express server with API routes
│   └── package.json         # Backend dependencies
├── scripts/                  # Python AI processing scripts
│   ├── chunker.py           # Document chunking functionality
│   ├── query_handler.py     # LLM query processing
│   └── requirements.txt     # Python dependencies
├── package.json             # Root package.json with unified scripts
├── env.example              # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 4. Setup Instructions

### Prerequisites

- **Node.js**: >= 18.x
- **Python**: >= 3.9
- **npm**: Latest stable version
- **pip**: Latest stable version

### Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
CHAIBRI_API_KEY=your_chaibri_api_key_here

# Database Configuration
DATABASE_URL=your_database_connection_string
MONGODB_URI=your_mongodb_connection_string

# Server Configuration
PORT=3001
NODE_ENV=development

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/daivikpurani/Ai-Tutor.git
   cd Ai-Tutor
   ```

2. **Install all dependencies (recommended)**
   ```bash
   npm run setup
   ```

   Or install individually:
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

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

### Development Entry Points

#### Option 1: Individual Services
```bash
# Terminal 1 - Backend Server
cd backend_python
python main.py

# Terminal 2 - Frontend Development Server
cd frontend
npm start

# Terminal 3 - Python Scripts (as needed)
cd scripts
python chunker.py
python query_handler.py
```

#### Option 2: Unified Development Command
```bash
# Run both frontend and backend concurrently
npm run dev

# Alternative command (same as above)
npm run dev:all
```

## 5. Testing

### Backend Testing
- **Framework**: Jest
- **Coverage**: Unit tests for controllers, services, and utilities
- **Command**: `npm test` (from backend directory)

### Python Scripts Testing
- **Framework**: Pytest
- **Coverage**: Unit tests for document processing and LLM interactions
- **Command**: `pytest` (from scripts directory)

### Test Commands
```bash
# Run all tests
npm test

# Run backend tests only
npm run test:backend

# Run frontend tests only
npm run test:frontend

# Run Python tests
npm run python:test
```

## 6. User Roles & Interfaces

### Students
- **Primary Interface**: Chatbot UI for interactive learning
- **Capabilities**:
  - Ask questions about course material
  - Receive contextual explanations and examples
  - Take automated assessments through chat
  - Access learning progress and feedback

### Instructors
- **Primary Interface**: Material upload interface (future: comprehensive dashboard)
- **Capabilities**:
  - Upload course modules, documents, and resources
  - Monitor student progress and engagement
  - Access learning analytics and performance metrics
  - Configure assessment parameters

### Developers
- **Primary Interface**: Backend API endpoints
- **Capabilities**:
  - Direct API access for integration
  - Custom script execution for data processing
  - System monitoring and debugging

## 7. Deployment

### Current Status
- **Environment**: Local development only
- **CI/CD**: Not implemented
- **Cloud Deployment**: Not configured

### Future Deployment Considerations
- Containerization with Docker
- Cloud platform integration (AWS, GCP, Azure)
- Automated testing and deployment pipelines
- Environment-specific configuration management

## 8. Documentation

### Current Documentation
- **README.md**: This comprehensive project overview
- **DEVELOPER.md**: Detailed developer documentation with technical specifications
- **Inline Comments**: Code documentation within source files

### Planned Documentation
- **System Architecture Diagram**: Visual representation of component interactions
- **Data Flow Diagram**: Illustration of data movement through the system
- **Module Interaction Chart**: Detailed component relationship mapping
- **API Documentation**: Comprehensive endpoint reference
- **User Guides**: Role-specific usage instructions

### Available Scripts
```bash
# Development
npm run dev              # Run both frontend and backend
npm run dev:all          # Same as npm run dev
npm run dev:backend      # Run backend only
npm run dev:frontend     # Run frontend only

# Python scripts
npm run python:chunker   # Test document chunker
npm run python:query     # Test query handler

# Building and deployment
npm run build            # Build frontend for production
npm start                # Start production server

# Maintenance
npm run clean            # Remove all node_modules
npm run fresh-install    # Clean and reinstall everything
```

## 9. Licensing & Contribution

### Licensing
- **Status**: Proprietary research project
- **License**: No open-source license
- **Usage**: Restricted to authorized research participants

### Contribution Guidelines
- **Public Contributions**: Not accepted
- **Internal Development**: Follow established coding standards
- **Code Review**: Required for all changes
- **Documentation**: Maintain inline comments and update README as needed

---

## Getting Started

1. **Clone and setup the project**
   ```bash
   git clone https://github.com/daivikpurani/Ai-Tutor.git
   cd Ai-Tutor
   npm run setup
   cp env.example .env
   ```

2. **Configure your environment variables**
   - Edit `.env` with your actual API keys
   - Set up OpenAI, Pinecone, or ChaiJibri credentials

3. **Start the development servers**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

5. **Test the Python scripts**
   ```bash
   npm run python:chunker
   npm run python:query
   ```

6. **Begin exploring the chatbot interface**
   - Open the frontend in your browser
   - Start chatting with the AI tutor
   - Upload course materials through the backend API

For detailed technical information, API documentation, and troubleshooting, see [DEVELOPER.md](./DEVELOPER.md).

For additional support or questions, please contact the development team or refer to the internal documentation repository.
