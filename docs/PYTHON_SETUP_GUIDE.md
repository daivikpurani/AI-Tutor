# Python 3.11/3.12 Setup Guide

## Why Python 3.11/3.12?

Python 3.14 is very new and has compatibility issues with ChromaDB 0.3.23 (which uses Pydantic v1). Most production applications use Python 3.11 or 3.12 for stability and compatibility.

## Quick Setup

Run the setup script:

```bash
./scripts/setup_python311.sh
```

This script will:
1. Check for Python 3.11 or 3.12
2. Create a new virtual environment (`venv_py311` or `venv_py312`)
3. Install all dependencies
4. Verify ChromaDB works correctly

## Manual Setup

If you prefer to set up manually:

### 1. Install Python 3.11 or 3.12

**macOS (using Homebrew):**
```bash
brew install python@3.11
# or
brew install python@3.12
```

**Or download from:**
https://www.python.org/downloads/

### 2. Create Virtual Environment

```bash
# For Python 3.11
python3.11 -m venv venv_py311

# For Python 3.12
python3.12 -m venv venv_py312
```

### 3. Activate Virtual Environment

```bash
# For Python 3.11
source venv_py311/bin/activate

# For Python 3.12
source venv_py312/bin/activate
```

### 4. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install backend dependencies
cd backend_python
pip install -r requirements.txt
cd ..

# Install script dependencies (if needed)
cd scripts
pip install -r requirements.txt
cd ..
```

### 5. Verify Installation

```bash
# Test ChromaDB
python -c "import chromadb; print(f'ChromaDB {chromadb.__version__}')"

# Test VectorDatabase
python -c "
import sys
sys.path.insert(0, 'backend_python')
from services.vector_db import VectorDatabase
db = VectorDatabase()
print('VectorDatabase works!')
"
```

## Using the New Environment

### Activate the Environment

```bash
source venv_py311/bin/activate
# or
source venv_py312/bin/activate
```

### Load Papers into Vector Database

```bash
python scripts/load_course_materials.py
```

### Run the Backend

```bash
cd backend_python
python main.py
```

### Deactivate

```bash
deactivate
```

## Switching Between Environments

You can keep both environments:
- `venv/` - Original Python 3.14 environment (may have ChromaDB issues)
- `venv_py311/` or `venv_py312/` - Compatible environment for ChromaDB

Just activate the one you need:
```bash
source venv_py311/bin/activate  # For ChromaDB work
# or
source venv/bin/activate  # For other work
```

## Troubleshooting

### "Python 3.11/3.12 not found"

Install Python 3.11 or 3.12:
- macOS: `brew install python@3.11`
- Or download from python.org

### "ChromaDB still has issues"

1. Make sure you're using the correct virtual environment
2. Verify Python version: `python --version`
3. Reinstall ChromaDB: `pip install --force-reinstall chromadb==0.3.23`

### "Import errors"

Make sure you've activated the virtual environment:
```bash
source venv_py311/bin/activate
```

## Benefits of Python 3.11/3.12

- ✅ Full ChromaDB compatibility
- ✅ Stable and widely used in production
- ✅ Better package compatibility
- ✅ No Pydantic v1 warnings
- ✅ Faster startup times

## Next Steps

After setup:
1. Load papers: `python scripts/load_course_materials.py`
2. Test queries using the questions in `docs/TEST_QUESTIONS.md`
3. Start the backend: `cd backend_python && python main.py`

