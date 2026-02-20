# AI-Tutor System Architecture Diagrams

This document contains comprehensive Mermaid diagrams illustrating the architecture of the AI-Tutor system, a hybrid LLM-powered educational platform with vector database integration.

**Quick reference (single-page):** [AI-Tutor Architecture draw.io](ai_tutor_architecture.drawio) — open in [diagrams.net](https://app.diagrams.net) or VS Code Draw.io extension. [HTML view](ai_tutor_architecture.html) for browser/print.

## Table of Contents
1. [System Context Diagram](#1-system-context-diagram)
2. [Container Diagram](#2-container-diagram)
3. [Component Diagram](#3-component-diagram)
4. [Query Processing Sequence Diagram](#4-query-processing-sequence-diagram)
5. [Document Upload Flow](#5-document-upload-flow)
6. [WebSocket Communication Flow](#6-websocket-communication-flow)
7. [LLM Provider Routing](#7-llm-provider-routing)

---

## 1. System Context Diagram

This diagram shows the AI-Tutor system in its environment, including users and external systems.

```mermaid
C4Context
title AI-Tutor System Context Diagram

Person(student, "Student", "A learner using the AI-Tutor for educational assistance")
Person(instructor, "Instructor", "An educator uploading course materials and monitoring student progress")

System(ai_tutor, "AI-Tutor System", "AI-powered tutoring platform with vector database and real-time chat")

System_Ext(openai_api, "OpenAI API", "External LLM service for complex queries")
System_Ext(ollama_local, "Ollama Local (Llama 3)", "Local LLM service running Llama 3 model for simple queries")
System_Ext(file_storage, "File Storage", "Local file system for document storage")

Rel(student, ai_tutor, "Uses", "Web Interface")
Rel(instructor, ai_tutor, "Uploads materials via", "Web Interface")
Rel(ai_tutor, openai_api, "Routes complex queries to", "HTTPS/REST API")
Rel(ai_tutor, ollama_local, "Routes simple queries to", "HTTP/REST API")
Rel(ai_tutor, file_storage, "Stores documents in", "File System")

Boundary(ai_tutor_boundary, "AI-Tutor System") {
    System(ai_tutor, "AI-Tutor System", "AI-powered tutoring platform with vector database and real-time chat")
}
```

---

## 2. Container Diagram

This diagram shows the high-level shape of the AI-Tutor system and how responsibilities are distributed across containers.

```mermaid
C4Container
title AI-Tutor Container Diagram

Person(student, "Student", "Learner using the tutoring system")
Person(instructor, "Instructor", "Educator uploading materials")

System_Boundary(ai_tutor_system, "AI-Tutor System") {
    Container(web_app, "React Frontend", "React", "Modern web interface with real-time chat, document upload, and demo mode")
    
    Container(api_gateway, "FastAPI Backend", "Python/FastAPI", "REST API and WebSocket server handling requests, file uploads, and real-time communication")
    
    Container(query_handler, "Query Handler Service", "Python", "Processes user queries, manages conversation history, and coordinates LLM responses")
    
    Container(vector_db, "Vector Database", "ChromaDB", "Stores document embeddings and enables semantic search")
    
    Container(llm_service, "Hybrid LLM Service", "Python", "Routes queries to appropriate LLM providers based on complexity analysis")
    
    Container(document_processor, "Document Processor", "Python", "Chunks and processes uploaded documents for vector storage")
    
    ContainerDb(chroma_storage, "ChromaDB Storage", "SQLite", "Persistent storage for vector embeddings and metadata")
    
    ContainerDb(file_storage, "File Storage", "File System", "Temporary storage for uploaded documents")
}

System_Ext(openai, "OpenAI API", "External LLM service")
System_Ext(ollama, "Ollama Local (Llama 3)", "Local LLM service running Llama 3 model")

Rel(student, web_app, "Interacts with", "HTTPS/WebSocket")
Rel(instructor, web_app, "Uploads materials via", "HTTPS")

Rel(web_app, api_gateway, "Makes API calls to", "HTTPS/WebSocket")
Rel(api_gateway, query_handler, "Delegates queries to", "Python calls")
Rel(api_gateway, document_processor, "Processes uploads via", "Python calls")

Rel(query_handler, vector_db, "Searches for context", "Python API")
Rel(query_handler, llm_service, "Generates responses via", "Python calls")

Rel(vector_db, chroma_storage, "Persists data to", "SQLite")
Rel(document_processor, file_storage, "Stores files in", "File System")
Rel(document_processor, vector_db, "Adds chunks to", "Python API")

Rel(llm_service, openai, "Routes complex queries to", "HTTPS/REST")
Rel(llm_service, ollama, "Routes simple queries to", "HTTP/REST")
```

---

## 3. Component Diagram

This diagram shows how the backend services are organized internally.

```mermaid
C4Component
title AI-Tutor Backend Component Diagram

Container_Boundary(backend, "FastAPI Backend") {
    Component(api_routes, "API Routes", "FastAPI", "REST endpoints for chat, upload, health checks")
    Component(websocket_handler, "WebSocket Handler", "FastAPI", "Real-time communication for streaming responses")
    Component(cors_middleware, "CORS Middleware", "FastAPI", "Cross-origin resource sharing configuration")
    
    Component(query_handler_service, "Query Handler", "Python Class", "Processes user queries and manages conversation flow")
    Component(vector_db_service, "Vector Database Service", "Python Class", "ChromaDB operations and semantic search")
    Component(llm_service_component, "LLM Service", "Python Class", "Hybrid LLM routing and response generation")
    Component(document_chunker, "Document Chunker", "Python Class", "File processing and text chunking")
    
    ComponentDb(chroma_client, "ChromaDB Client", "ChromaDB", "Vector database client and operations")
    ComponentDb(embedding_model, "Embedding Model", "SentenceTransformers", "Text-to-vector conversion")
}

System_Ext(openai_provider, "OpenAI Provider", "External LLM")
System_Ext(ollama_provider, "Ollama Provider (Llama 3)", "Local LLM running Llama 3 model")
System_Ext(mock_provider, "Mock Provider", "Fallback LLM")

Rel(api_routes, query_handler_service, "Delegates to", "Python calls")
Rel(websocket_handler, query_handler_service, "Streams via", "Python calls")

Rel(query_handler_service, vector_db_service, "Searches context", "Python calls")
Rel(query_handler_service, llm_service_component, "Generates responses", "Python calls")

Rel(vector_db_service, chroma_client, "Queries", "ChromaDB API")
Rel(vector_db_service, embedding_model, "Creates embeddings", "SentenceTransformers")

Rel(llm_service_component, openai_provider, "Routes to", "HTTP/REST")
Rel(llm_service_component, ollama_provider, "Routes to", "HTTP/REST")
Rel(llm_service_component, mock_provider, "Fallback to", "Local")

Rel(document_chunker, vector_db_service, "Adds chunks", "Python calls")
```

---

## 4. Query Processing Sequence Diagram

This diagram shows the flow of a user query through the system.

```mermaid
sequenceDiagram
    participant U as User
    participant F as React Frontend
    participant A as FastAPI Backend
    participant Q as Query Handler
    participant V as Vector Database
    participant L as LLM Service
    participant O as OpenAI/Ollama

    U->>F: Asks question
    F->>A: POST /api/chat or WebSocket message
    
    alt WebSocket Mode
        A->>F: Processing status
        A->>Q: process_query_streaming()
    else REST Mode
        A->>Q: process_query()
    end
    
    Q->>Q: Store query in history
    Q->>V: search_similar(query, n_results=5)
    V->>V: Semantic similarity search
    V-->>Q: Returns relevant context chunks
    
    Q->>Q: Build context text from chunks
    Q->>L: generate_response(messages, context)
    
    L->>L: Analyze query complexity
    alt Complex Query
        L->>O: Route to OpenAI
        O-->>L: GPT response
    else Simple Query
        L->>O: Route to Ollama (Llama 3)
        O-->>L: Llama 3 response
    end
    
    L-->>Q: LLM response with metadata
    Q->>Q: Store response in history
    
    alt WebSocket Mode
        Q->>F: Stream response chunks
        F->>U: Display streaming response
    else REST Mode
        Q-->>A: Complete response
        A-->>F: JSON response
        F->>U: Display complete response
    end
```

---

## 5. Document Upload Flow

This diagram shows how documents are processed and stored in the vector database.

```mermaid
flowchart TD
    A[User Uploads Document] --> B{File Type Check}
    B -->|Supported| C[Save to temp_uploads/]
    B -->|Unsupported| D[Return Error]
    
    C --> E[Document Chunker]
    E --> F{File Format}
    
    F -->|.txt, .md| G[Extract Text Directly]
    F -->|.pdf| H[PyPDF2 Extraction]
    F -->|.docx, .doc| I[python-docx Extraction]
    
    G --> J[Text Chunking]
    H --> J
    I --> J
    
    J --> K[Create Chunks with Metadata]
    K --> L[Vector Database Service]
    
    L --> M[Generate Embeddings]
    M --> N[Store in ChromaDB]
    N --> O[Update Collection Metadata]
    
    O --> P[Cleanup Temp Files]
    P --> Q[Return Success Response]
    
    style A fill:#e1f5fe
    style Q fill:#c8e6c9
    style D fill:#ffcdd2
```

---

## 6. WebSocket Communication Flow

This diagram shows the real-time communication between frontend and backend.

```mermaid
sequenceDiagram
    participant F as Frontend
    participant W as WebSocket Handler
    participant Q as Query Handler
    participant L as LLM Service
    participant P as LLM Provider

    F->>W: WebSocket Connection
    W->>F: Connection Established
    
    F->>W: Send Query Message
    W->>Q: process_query_streaming()
    
    Q->>F: "Processing your question..."
    Q->>Q: Retrieve Context
    Q->>F: "Found X relevant sections"
    
    Q->>L: generate_streaming_response()
    L->>P: Stream from LLM Provider
    
    loop For each response chunk
        P-->>L: Response chunk
        L-->>Q: Chunk data
        Q->>F: Stream chunk to client
        F->>F: Update UI with chunk
    end
    
    Q->>F: "Response complete"
    W->>F: Close streaming
    
    Note over F,P: Real-time streaming provides<br/>better user experience
```

---

## 7. LLM Provider Routing

This diagram shows how the hybrid LLM service routes queries to appropriate providers.

```mermaid
flowchart TD
    A[User Query] --> B[Query Complexity Analyzer]
    
    B --> C{Complexity Analysis}
    
    C -->|Simple| D[Simple Keywords Detected]
    C -->|Complex| E[Complex Keywords Detected]
    C -->|Unknown| F[Default Routing]
    
    D --> G[Route to Ollama (Llama 3)]
    E --> H[Route to OpenAI]
    F --> I[Try Ollama (Llama 3) First]
    
    G --> J{Llama 3 Available?}
    H --> K{OpenAI Available?}
    I --> L{Llama 3 Available?}
    
    J -->|Yes| M[Generate Response with Llama 3]
    J -->|No| N[Fallback to Mock]
    
    K -->|Yes| O[Generate Response with GPT]
    K -->|No| P[Fallback to Llama 3]
    
    L -->|Yes| M
    L -->|No| Q{OpenAI Available?}
    
    P --> R{Llama 3 Available?}
    Q -->|Yes| O
    Q -->|No| N
    
    R -->|Yes| M
    R -->|No| N
    
    M --> S[Return Response]
    O --> S
    N --> S
    
    S --> T[Add Routing Metadata]
    T --> U[Return to Query Handler]
    
    style A fill:#e3f2fd
    style S fill:#c8e6c9
    style N fill:#fff3e0
```

---

## Architecture Key Features

### 1. **Hybrid LLM Architecture**
- **Intelligent Routing**: Queries are analyzed for complexity and routed to appropriate LLM providers
- **Llama 3 Integration**: Local Llama 3 model via Ollama for simple queries and fallback scenarios
- **Fallback Strategy**: Multiple fallback options ensure system reliability (Llama 3 → Mock)
- **Provider Abstraction**: Unified interface for different LLM services

### 2. **Vector Database Integration**
- **Semantic Search**: ChromaDB enables context-aware responses
- **Document Chunking**: Intelligent text splitting with overlap
- **Persistent Storage**: SQLite-based persistence for embeddings

### 3. **Real-time Communication**
- **WebSocket Support**: Streaming responses for better UX
- **Dual Mode**: Both REST API and WebSocket endpoints
- **Connection Management**: Robust WebSocket connection handling

### 4. **Document Processing Pipeline**
- **Multi-format Support**: PDF, DOCX, TXT, MD files
- **Intelligent Chunking**: Sentence-boundary aware splitting
- **Metadata Preservation**: Rich metadata for each document chunk

### 5. **Frontend Architecture**
- **React-based UI**: Modern, responsive interface
- **Demo Mode**: Offline demonstration capability
- **Real-time Updates**: Live streaming of AI responses
- **Markdown Rendering**: Rich text display with syntax highlighting

---

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for embeddings
- **SentenceTransformers**: Text embedding generation
- **OpenAI API**: External LLM service (GPT-3.5-turbo)
- **Ollama**: Local LLM service running **Llama 3** model
- **WebSocket**: Real-time communication

### Frontend
- **React**: Component-based UI framework
- **ReactMarkdown**: Markdown rendering
- **WebSocket API**: Real-time communication
- **CSS3**: Modern styling and animations

### Infrastructure
- **SQLite**: ChromaDB persistence
- **File System**: Document storage
- **CORS**: Cross-origin resource sharing
- **Environment Variables**: Configuration management

---

## Llama 3 Configuration Details

### Ollama Setup with Llama 3
The AI-Tutor system is configured to use **Llama 3** as the primary local LLM provider through Ollama:

```bash
# Install Llama 3 via Ollama
ollama pull llama3

# Verify installation
ollama list
```

### Configuration Parameters
- **Model**: `llama3` (default Ollama model)
- **Base URL**: `http://localhost:11434` (default Ollama server)
- **Temperature**: 0.7 (configurable per query)
- **Max Tokens**: 1000 (configurable per query)

### Query Routing Strategy
- **Simple Queries**: Routed to Llama 3 for fast, local processing
- **Complex Queries**: Routed to OpenAI GPT-3.5-turbo for advanced reasoning
- **Fallback**: Llama 3 serves as primary fallback when OpenAI is unavailable
- **Mock Provider**: Final fallback for testing and development

### Performance Benefits
- **Low Latency**: Local processing eliminates network round-trips
- **Cost Effective**: No API costs for simple queries
- **Privacy**: Sensitive queries processed locally
- **Reliability**: Works offline when OpenAI API is unavailable

---

## Deployment Considerations

### Development Environment
- Local ChromaDB instance
- Ollama local LLM server
- File-based document storage
- Hot-reload enabled FastAPI server

### Production Considerations
- **Scalability**: ChromaDB clustering for large document collections
- **Security**: API key management and CORS configuration
- **Monitoring**: Health checks and logging
- **Backup**: Database backup and restore capabilities

---

*This architecture documentation provides a comprehensive overview of the AI-Tutor system's design, components, and data flows. The diagrams illustrate both the high-level system context and detailed internal component interactions.*
