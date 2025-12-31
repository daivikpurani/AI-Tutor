# Quick Start Guide

## Prerequisites

- Python 3.11 or 3.12 (for ChromaDB compatibility)
- pip

## Setup (One Command)

```bash
./scripts/setup_python311.sh
```

This will:
- Check for Python 3.11/3.12
- Create a compatible virtual environment
- Install all dependencies
- Verify ChromaDB works

## If Python 3.11/3.12 Not Installed

**macOS:**
```bash
brew install python@3.11
```

**Or download from:** https://www.python.org/downloads/

Then run the setup script again.

## Load Papers into Vector Database

```bash
# Activate the environment
source venv_py311/bin/activate  # or venv_py312

# Load papers
python scripts/load_course_materials.py
```

## Start the Application

```bash
# Backend
cd backend_python
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Test Questions

See `docs/TEST_QUESTIONS.md` for:
- In-domain questions (RAG, AI, ML) - should get answers
- Out-of-domain questions - should return "I don't know"

## Troubleshooting

See `docs/PYTHON_SETUP_GUIDE.md` for detailed troubleshooting.

