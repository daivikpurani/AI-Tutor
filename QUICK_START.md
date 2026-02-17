# Quick Start

## Prerequisites

- Python 3.11 or 3.12 (ChromaDB compatibility)
- Node.js 18+
- pip, npm

## One-command setup (if script available)

```bash
./scripts/setup_python311.sh
```

Then activate the venv and load materials:

```bash
source venv_py311/bin/activate   # or venv_py312
python scripts/load_course_materials.py
```

## Manual setup

### Backend

```bash
cd backend_python
cp .env.example .env
# Edit .env: set OPENAI_API_KEY (and optionally OLLAMA_BASE_URL)
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Start both (from repo root)

```bash
npm run dev
```

Or use scripts: `./start.sh` (quick) or `./start-dev.sh` (full checks and setup).

- **Frontend:** http://localhost:5173  
- **Backend:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs  

## Test questions

See `docs/TEST_QUESTIONS.md` for in-domain and out-of-domain sample questions.

## Troubleshooting

- **Python/ChromaDB issues:** Use Python 3.11 or 3.12; see [docs/DEVELOPER.md](docs/DEVELOPER.md#troubleshooting) and [docs/CHROMADB_UPGRADE_ISSUES.md](docs/CHROMADB_UPGRADE_ISSUES.md).
- **Env file:** Copy `backend_python/.env.example` to `backend_python/.env`.
