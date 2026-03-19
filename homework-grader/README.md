# AI-Powered Homework Grading System
**SF State Computer Science Department**

## Project Overview
An intelligent system powered by AI models to automatically grade student homework and assignments using knowledge extracted from class materials, textbooks, professor's notes, and PDFs. The system provides grades based on custom natural-language instructions and offers constructive feedback.

## Architecture

### Backend (`/backend`)
- **FastAPI** RESTful API server
- **PostgreSQL** for persistent data storage
- **ChromaDB** for vector embeddings
- **LangChain** for RAG orchestration
- **Gemini API** for LLM capabilities

### Frontend (`/frontend`)
- **React** + **TypeScript** (Webpack) minimal demo UI

### Document Processing (`/backend/services/document_processor`)
- PDF extraction and chunking
- Text preprocessing
- Metadata extraction

### Vector Store (`/backend/services/vector_store`)
- Embedding generation
- Similarity search
- RAG retrieval

## Project Structure

```
homework-grader/
│
├── backend/                          # Backend API application
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── config.py                 # Configuration & environment variables
│   │   ├── api/                      # API routes/endpoints
│   │   │   └── v1/                   # materials, submissions, grading, lists
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/                 # Document processing, vector store, LLM, RAG, grading
│   │   ├── db/                       # DB engine + session
│   │   ├── core/                     # Logging, exceptions, security
│   │   └── utils/                    # File handling and helpers
│   ├── data/                         # Backend uploads + vector store (gitignored)
│   │   ├── uploads/                  # Course materials + submissions
│   │   ├── chroma_db/                # ChromaDB storage
│   │   └── logs/                     # Application logs
│   └── requirements.txt              # Backend Python dependencies
│
├── frontend/                         # React + TypeScript UI
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   ├── index.css
│   │   ├── api.ts
│   │   └── pages/                    # Home, Upload Materials, Upload Submission, Grade, View Materials
│   ├── package.json
│   ├── tsconfig.json
│   └── webpack.config.js
│
├── scripts/                          # Utility scripts
│   ├── init_db.py                    # Initialize database schema
│   ├── seed_realistic_data.py        # Seed realistic SF State CS data
│   └── data/                         # Script-local logs/output
│
├── docs/                             # Documentation
│   ├── database_schema.md            # System database schema
│   └── DEMO_README.md                # End-to-end demo workflow (e.g. CSC 810)
│
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Root-level Python dependencies (if needed)
└── README.md                         # Project overview
```

## Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for serving FastAPI
- **PostgreSQL**: Relational database for structured data
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool (future)

### AI/ML
- **Gemini API**: Large Language Model for grading and feedback
- **LangChain**: Framework for LLM orchestration and RAG
- **ChromaDB**: Vector database for embeddings and similarity search

### Document Processing
- **PyPDF2/pdfplumber**: PDF text extraction
- **python-docx**: Word document processing (future)

### Frontend
- **React** + **TypeScript**: Minimal demo UI (Webpack, no Vite)

### Utilities
- **python-dotenv**: Environment variable management
- **Pydantic**: Data validation and settings management
- **pytest**: Testing framework

## Key Features

### For Faculty
1. **Course Management**: Create and manage CS courses
2. **Assignment Setup**: Define assignments with custom grading instructions
3. **Material Upload**: Upload textbooks, notes, slides, PDFs
4. **Automated Grading**: AI-powered grading based on uploaded materials
5. **Custom Rubrics**: Natural language grading instructions
6. **Feedback Generation**: Automatic constructive feedback for students

### For Students (Future)
1. **Assignment Submission**: Upload homework via web interface
2. **View Grades**: See grades and detailed feedback
3. **Improvement Suggestions**: AI-generated suggestions for improvement

## Database Schema (High-Level)

### Core Entities
- **Faculty**: Professors and instructors
- **Course**: CS courses (e.g., CSC 101, CSC 895)
- **Student**: Student information
- **Assignment**: Homework/assignment definitions
- **Material**: Course materials (PDFs, notes, etc.)
- **Submission**: Student homework submissions
- **Grade**: Grading results
- **Feedback**: Detailed feedback for students

## Core API Endpoints (Implemented)

- **Health**
  - `GET /` – Root info
  - `GET /health` – Basic health check
  - `GET /api/v1/` – API root + links

- **Materials**
  - `POST /api/v1/materials/upload` – Upload and index a course material PDF for a section
  - `GET /api/v1/materials/section/{section_id}` – List materials for a section
  - `GET /api/v1/materials/vector-store/stats/{section_id}` – Vector store stats for a section

- **Submissions**
  - `POST /api/v1/submissions/upload` – Upload a homework submission (PDF)
  - `GET /api/v1/submissions/assignment/{assignment_id}` – List submissions for an assignment
  - `GET /api/v1/submissions/{submission_id}` – Get submission details

- **Grading**
  - `POST /api/v1/grading/grade` – Grade a submission with AI (RAG + rubric + Gemini)
  - `GET /api/v1/grading/grade/{submission_id}` – Get stored grade for a submission

- **Lists (for dropdowns in UI)**
  - `GET /api/v1/lists/sections` – List active sections
  - `GET /api/v1/lists/assignments` – List published assignments
  - `GET /api/v1/lists/students` – List active students

## API Endpoints (Planned)

### Courses
- `POST /api/v1/courses/` - Create course
- `GET /api/v1/courses/` - List all courses
- `GET /api/v1/courses/{id}` - Get course details
- `PUT /api/v1/courses/{id}` - Update course
- `DELETE /api/v1/courses/{id}` - Delete course

### Assignments
- `POST /api/v1/assignments/` - Create assignment
- `GET /api/v1/assignments/` - List assignments
- `GET /api/v1/assignments/{id}` - Get assignment details
- `PUT /api/v1/assignments/{id}` - Update assignment

### Materials
- `POST /api/v1/materials/` - Upload course material
- `GET /api/v1/materials/` - List materials
- `DELETE /api/v1/materials/{id}` - Delete material

### Submissions
- `POST /api/v1/submissions/` - Submit homework
- `GET /api/v1/submissions/` - List submissions
- `GET /api/v1/submissions/{id}` - Get submission details

### Grading
- `POST /api/v1/grading/grade` - Grade a submission
- `POST /api/v1/grading/batch` - Grade multiple submissions

## RAG Architecture

1. **Document Ingestion**: Upload course materials (PDFs, notes)
2. **Text Extraction**: Extract text from documents
3. **Chunking**: Split text into semantic chunks
4. **Embedding**: Generate embeddings using Gemini
5. **Vector Storage**: Store in ChromaDB
6. **Retrieval**: Query relevant chunks for grading context
7. **Augmentation**: Build context for LLM prompt
8. **Generation**: Generate grade and feedback using Gemini

## Security Considerations

- API key management via environment variables
- Input validation using Pydantic
- SQL injection prevention via SQLAlchemy ORM
- File upload validation and sanitization
- Rate limiting (future)
- Authentication/Authorization (future)

## Development Workflow

1. **Setup Environment**: Create and activate a virtualenv (e.g. `python -m venv venv && source venv/bin/activate`)
2. **Configure**: Create `.env` in the project root with DB + API keys (see `backend/app/config.py` for defaults)
3. **Initialize DB**: `./venv/bin/python scripts/init_db.py`
4. **Seed Realistic Data (recommended)**: `./venv/bin/python scripts/seed_realistic_data.py` (SF State CS faculty, courses, sections, rubrics, assignments)
5. **Start Backend**: `cd backend && uvicorn app.main:app --reload`
6. **Start Frontend**: `cd frontend && npm install && npm start` (dev server at http://localhost:3000, proxies API to backend)
7. **Run Demo**: Follow `docs/DEMO_README.md` for a complete CSC 810 workflow

## Deployment Considerations (Future)

- **Backend**: Deploy to cloud (AWS, GCP, Azure)
- **Database**: Managed PostgreSQL service
- **Vector Store**: Persistent ChromaDB or managed service
- **Frontend**: Static build (`npm run build`) or containerized deployment
- **File Storage**: Cloud storage (S3, GCS) for uploads
- **Monitoring**: Application monitoring and logging
- **CI/CD**: Automated testing and deployment pipeline

## Maintenance

- Regular dependency updates
- Database backups
- Vector store backups
- Log rotation
- Performance monitoring
- API versioning for backward compatibility

## Contributing

This is a research project for SF State CS Department. For questions or contributions, please contact the project maintainer.

## License

[To be determined]

---

**Project Status**: Demo-ready (end-to-end workflow implemented)  
**Last Updated**: February 20, 2026
