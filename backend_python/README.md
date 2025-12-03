# AI Tutor - FastAPI Backend

## 🚀 **High-Performance AI Tutoring System**

A modern, scalable AI tutoring system built with FastAPI, ChromaDB, and OpenAI integration. This backend provides intelligent document processing, semantic search, and real-time chat capabilities.

## ✨ **Key Features**

- 🤖 **AI-Powered Tutoring**: OpenAI GPT-3.5-turbo integration with custom educational prompts
- 🔍 **Semantic Search**: ChromaDB vector database for intelligent document retrieval
- 📄 **Document Processing**: Support for TXT, MD, PDF, DOCX files with intelligent chunking
- 💬 **Real-time Chat**: WebSocket support for live conversations
- 🔒 **Type Safety**: Pydantic models for request/response validation
- 📚 **Auto Documentation**: Swagger UI and ReDoc integration
- ⚡ **High Performance**: Async/await support with FastAPI
- 🛠️ **Easy Setup**: One-command startup with comprehensive configuration

## 🏗️ **Architecture**

```
Frontend (React) 
    ↓ HTTP/WebSocket
FastAPI Backend (Python)
    ├── API Routes (/api/chat, /api/upload, etc.)
    ├── WebSocket (/ws/chat)
    ├── ChromaDB Vector Database
    ├── OpenAI LLM Integration
    └── Document Processing Pipeline
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+
- OpenAI API key (optional - works with mock responses)

### **Installation**

1. **Clone and navigate to backend:**
   ```bash
   cd backend_python
   ```

2. **Run the startup script:**
   ```bash
   ./start.sh
   ```

3. **Or manual setup:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp env.example .env
   # Edit .env with your OpenAI API key
   
   # Start server
   python main.py
   ```

### **Configuration**

Update `.env` file:
```bash
# Required: OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 💡 Session Memory (Per-Session Conversation Chaining)

- The backend maintains short-term conversation memory per session using the `user_id` you send on each request.
- To enable multi-step, context-aware answers, send the same `user_id` across consecutive messages in a session.
- Memory is kept in-process only and limited to the most recent turns for that `user_id`. It is not persisted across server restarts.
- For HTTP chat, include `user_id` in the `ChatRequest` body. For WebSocket chat, include `user_id` when establishing the session and in subsequent messages.

Example HTTP body:
```json
{
  "message": "Explain backpropagation",
  "user_id": "session-1234"
}
```

## 📚 Document-Grounded Responses

- The assistant answers strictly using the retrieved documents from the vector database.
- If the answer is not present in the retrieved context, the assistant will say so.
- When documents conflict, the assistant acknowledges and summarizes the differences.
- Responses begin with a direct answer, followed by brief supporting details, in a professional conversational tone.

## 📡 **API Endpoints**

### **REST API**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Chat with AI tutor |
| `POST` | `/api/upload` | Upload documents |
| `GET` | `/api/documents` | List documents |
| `DELETE` | `/api/documents/{id}` | Delete document |

### **WebSocket**
| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws/chat` | Real-time chat |

### **Documentation**
| URL | Description |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |

## 💡 **Usage Examples**

### **Chat with AI Tutor**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain machine learning?",
    "user_id": "student_123"
  }'
```

### **Upload Document**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@course_materials.pdf"
```

### **WebSocket Chat**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Hello! I need help with calculus.",
    user_id: "student_123"
  }));
};
```

## 🧪 **Testing**

Run the comprehensive test suite:
```bash
python test_backend.py
```

This will test:
- ✅ Health check endpoint
- ✅ Chat functionality
- ✅ Document upload
- ✅ Vector search
- ✅ Context-aware responses

## 📊 **Performance**

### **Benchmarks**
- **API Response Time**: ~200-500ms (with OpenAI)
- **Document Processing**: ~1-2 seconds per MB
- **Vector Search**: ~50-100ms per query
- **Concurrent Users**: 100+ (depending on hardware)

### **Memory Usage**
- **Base Application**: ~100MB
- **Per Document**: ~10-50MB (depending on size)
- **Per Active User**: ~5-10MB

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE=10485760

# Vector Search
SIMILARITY_THRESHOLD=0.8
MAX_CONTEXT_CHUNKS=5

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

## 🛠️ **Development**

### **Project Structure**
```
backend_python/
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── start.sh               # Startup script
├── test_backend.py        # Test suite
├── services/
│   ├── query_handler.py   # LLM integration
│   ├── vector_db.py       # ChromaDB service
│   └── document_chunker.py # Document processing
├── models/
│   └── schemas.py         # Pydantic models
├── utils/
│   ├── config.py          # Configuration
│   └── prompts.py         # LLM prompts
└── chroma_db/             # Vector database storage
```

### **Adding New Features**

1. **New API Endpoint:**
   ```python
   @app.post("/api/new-endpoint")
   async def new_endpoint(request: NewRequestModel):
       # Implementation
       return NewResponseModel(...)
   ```

2. **New Service:**
   ```python
   # Create in services/
   class NewService:
       async def new_method(self):
           # Implementation
   ```

3. **New Data Model:**
   ```python
   # Add to models/schemas.py
   class NewModel(BaseModel):
       field: str = Field(..., description="Field description")
   ```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Port 8000 already in use:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **OpenAI API errors:**
   - Check API key in `.env`
   - Verify API credits
   - System uses mock responses if API unavailable

3. **ChromaDB errors:**
   - Ensure `chroma_db` directory is writable
   - Check disk space
   - Reset: Delete `chroma_db` directory

4. **Document upload errors:**
   - Check file format (TXT, MD, PDF, DOCX)
   - Verify file size limits
   - Ensure `temp_uploads` directory exists

### **Logs**
Check application logs for detailed error information:
```bash
# Logs are printed to console
# For production, configure logging in utils/config.py
```

## 🔮 **Roadmap**

### **Planned Features**
- [ ] User authentication and sessions
- [ ] Advanced analytics and learning insights
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Mobile app integration
- [ ] Advanced document formats
- [ ] Custom embedding models
- [ ] Distributed vector search

### **Scalability Options**
- [ ] Redis for session management
- [ ] PostgreSQL for user data
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Load balancing
- [ ] CDN integration

## 📚 **Dependencies**

### **Core Dependencies**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `chromadb` - Vector database
- `openai` - LLM integration
- `sentence-transformers` - Embeddings
- `pydantic` - Data validation

### **Document Processing**
- `PyPDF2` - PDF processing
- `python-docx` - Word documents
- `python-magic` - File type detection

### **Development**
- `pytest` - Testing
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is part of a research thesis. See the main project README for license information.

## 🆘 **Support**

- 📖 **Documentation**: Check `/docs` endpoint
- 🐛 **Issues**: Create GitHub issues
- 💬 **Discussions**: Use GitHub discussions
- 📧 **Contact**: See main project README

---

**Built with ❤️ for AI-powered education**
