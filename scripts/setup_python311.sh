#!/bin/bash
# Script to set up Python 3.11/3.12 virtual environment for ChromaDB compatibility
# This resolves Python 3.14 + Pydantic v1 compatibility issues

set -e  # Exit on error

echo "=========================================="
echo "Python 3.11/3.12 Setup for ChromaDB"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for Python 3.11 or 3.12
PYTHON_VERSION=""
PYTHON_CMD=""

if command -v python3.12 &> /dev/null; then
    PYTHON_VERSION="3.12"
    PYTHON_CMD="python3.12"
    echo -e "${GREEN}✓ Found Python 3.12${NC}"
elif command -v python3.11 &> /dev/null; then
    PYTHON_VERSION="3.11"
    PYTHON_CMD="python3.11"
    echo -e "${GREEN}✓ Found Python 3.11${NC}"
else
    echo -e "${RED}✗ Python 3.11 or 3.12 not found${NC}"
    echo ""
    echo "Please install Python 3.11 or 3.12:"
    echo "  macOS: brew install python@3.11"
    echo "  Or download from: https://www.python.org/downloads/"
    exit 1
fi

# Get the actual version
ACTUAL_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Using: $PYTHON_CMD ($ACTUAL_VERSION)"
echo ""

# Determine venv name
VENV_NAME="venv_py${PYTHON_VERSION}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Project root: $PROJECT_ROOT"
echo "Virtual environment: $VENV_NAME"
echo ""

# Remove old venv if it exists
if [ -d "$PROJECT_ROOT/$VENV_NAME" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf "$PROJECT_ROOT/$VENV_NAME"
fi

# Create new virtual environment
echo -e "${GREEN}Creating virtual environment with Python $PYTHON_VERSION...${NC}"
cd "$PROJECT_ROOT"
$PYTHON_CMD -m venv "$VENV_NAME"

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$VENV_NAME/bin/activate"

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install backend dependencies
echo -e "${GREEN}Installing backend dependencies...${NC}"
cd "$PROJECT_ROOT/backend_python"
pip install -r requirements.txt

# Install script dependencies
echo -e "${GREEN}Installing script dependencies...${NC}"
cd "$PROJECT_ROOT/scripts"
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Verify ChromaDB installation
echo ""
echo -e "${GREEN}Verifying ChromaDB installation...${NC}"
python -c "import chromadb; print(f'✓ ChromaDB {chromadb.__version__} installed successfully')" || {
    echo -e "${RED}✗ ChromaDB verification failed${NC}"
    exit 1
}

# Test VectorDatabase initialization
echo -e "${GREEN}Testing VectorDatabase...${NC}"
python -c "
import sys
sys.path.insert(0, '../backend_python')
from services.vector_db import VectorDatabase
db = VectorDatabase()
print('✓ VectorDatabase initialized successfully')
" || {
    echo -e "${RED}✗ VectorDatabase test failed${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}=========================================="
echo "✓ Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "To use this environment:"
echo "  source $VENV_NAME/bin/activate"
echo ""
echo "To load papers into vector database:"
echo "  python scripts/load_course_materials.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""

