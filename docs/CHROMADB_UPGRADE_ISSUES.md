# ChromaDB Upgrade Issues and Workarounds

## Current Situation

We encountered compatibility issues when trying to upgrade ChromaDB:

1. **ChromaDB 0.3.23** (currently installed):
   - Has a bug where `collection.add()` loses client reference
   - Works with pydantic 1.x but Python 3.14 warns about incompatibility
   - Collection object loses `_client` attribute when using embedding functions

2. **ChromaDB 0.4.18** (target version):
   - Requires pydantic 2.x
   - Has compatibility issues with Python 3.14
   - Deprecated `chroma_db_impl` configuration
   - Requires additional dependencies (pypika, tenacity, typer)

3. **Python 3.14 Compatibility**:
   - Pydantic v1 warns about incompatibility with Python 3.14+
   - ChromaDB 0.4.x has internal config issues with Python 3.14

## Recommended Solutions

### Option 1: Use Python 3.11 or 3.12 (Recommended)
```bash
# Create a new virtual environment with Python 3.11 or 3.12
python3.11 -m venv venv_py311
source venv_py311/bin/activate
pip install -r backend_python/requirements.txt
```

### Option 2: Patch ChromaDB Collection (Current Workaround)
The current code includes a workaround that reinitializes the collection if it loses the client reference. This should work but may be slower.

### Option 3: Use Explicit Embeddings
Instead of relying on ChromaDB's embedding function, generate embeddings manually and pass them explicitly:

```python
# Generate embeddings manually
embeddings = embedding_model.encode(documents, convert_to_tensor=False).tolist()

# Add with explicit embeddings
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)
```

### Option 4: Switch to Alternative Vector Database
Consider alternatives like:
- **FAISS** (Facebook AI Similarity Search) - More stable, no Python version issues
- **Qdrant** - Modern, well-maintained
- **Weaviate** - Production-ready

## Current Status

- ✅ Papers downloaded successfully (29 papers)
- ✅ Prompts updated for RAG/AI/ML domain restrictions
- ✅ Test questions document created
- ⚠️ ChromaDB upload has compatibility issues
- ⚠️ Need to resolve Python 3.14 / ChromaDB compatibility

## Next Steps

1. **Short-term**: Use the workaround in `vector_db.py` that reinitializes collection
2. **Medium-term**: Consider switching to Python 3.11/3.12 for better compatibility
3. **Long-term**: Evaluate alternative vector databases or wait for ChromaDB Python 3.14 support

## Testing the Workaround

Try running the load script with the current workaround:

```bash
python scripts/load_course_materials.py
```

If it still fails, the collection reinitialization workaround should handle it, but it may be slower as it recreates the collection for each batch.

