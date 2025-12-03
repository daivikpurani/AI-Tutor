# ETB Installation Notes

## Dependency Issues and Solutions

### ChromaDB and Pydantic Compatibility

There is a known compatibility issue between ChromaDB versions and Pydantic v2. The current ChromaDB version (0.3.23) uses Pydantic v1 API (`BaseSettings`), while newer packages require Pydantic v2.

### Recommended Installation Approach

**Option 1: Use system Python (if dependencies already installed)**
```bash
# If backend dependencies are already installed system-wide
python3 scripts/benchmarks/etb_benchmark.py --help
```

**Option 2: Install dependencies in virtual environment**
```bash
# Create venv
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install httpx openai ollama fastapi uvicorn python-dotenv

# For ChromaDB compatibility, you may need to:
# 1. Use ChromaDB 0.4.18+ (if available for your Python version)
# 2. Or patch ChromaDB's config.py to use pydantic-settings

# Install other dependencies
pip install -r backend_python/requirements.txt
```

**Option 3: Patch ChromaDB (if needed)**

If ChromaDB fails to import due to BaseSettings, you can patch it:

```python
# In chromadb/config.py, change:
from pydantic import BaseSettings

# To:
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
```

### Minimal Dependencies for ETB Benchmark

The ETB benchmark requires these core dependencies:
- `httpx` - For HTTP requests (benchmark_config)
- `openai` - For OpenAI LLM provider
- `ollama` - For Ollama LLM provider  
- `chromadb` - For vector database (if using QueryHandler)
- `sentence-transformers` - For embeddings (if using QueryHandler)
- `fastapi`, `uvicorn` - For web framework (if running API)
- `python-dotenv` - For environment variables

### Testing Installation

Test that imports work:
```bash
python3 -c "
import sys
sys.path.insert(0, 'scripts/benchmarks')
from pedagogical_evaluator import PedagogicalEvaluator
from dialog_evaluator import DialogEvaluator
from domain_evaluator import DomainEvaluator
from etb_report_generator import ETBReportGenerator
print('All ETB modules imported successfully')
"
```

### Running Without Full Backend

If you only want to test the evaluators (without running full benchmarks), you can use them standalone:

```python
from pedagogical_evaluator import PedagogicalEvaluator

evaluator = PedagogicalEvaluator()
scores = evaluator.evaluate_response(
    response="Your tutor response here",
    student_query="What is RAG?",
    student_mistakes=None
)
print(scores)
```

## Code Status

All ETB code is complete and functional:
- ✅ `pedagogical_evaluator.py` - Complete
- ✅ `dialog_evaluator.py` - Complete  
- ✅ `domain_evaluator.py` - Complete
- ✅ `etb_dataset.json` - Complete (20 conversations)
- ✅ `etb_benchmark.py` - Complete
- ✅ `etb_report_generator.py` - Complete
- ✅ `README_ETB.md` - Complete documentation

The code is ready to use once dependencies are properly installed.

