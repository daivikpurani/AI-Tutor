# ChromaDB Pydantic Compatibility Patch

## Issue
ChromaDB 0.3.23 uses Pydantic v1 API (`BaseSettings`), but the environment has Pydantic v2 installed, which moved `BaseSettings` to `pydantic-settings`.

## Solution Applied
Patched `/venv/lib/python3.14/site-packages/chromadb/config.py`:

1. **Import fix**: Changed from `from pydantic import BaseSettings` to:
   ```python
   try:
       from pydantic_settings import BaseSettings
   except ImportError:
       try:
           from pydantic import BaseSettings
       except ImportError:
           from pydantic import BaseModel as BaseSettings
   ```

2. **Type annotations fix**: Changed `str = None` to `Optional[str] = None` for:
   - `clickhouse_host`
   - `clickhouse_port`
   - `chroma_server_host`
   - `chroma_server_http_port`
   - `chroma_server_grpc_port`

3. **Import Optional**: Added `Optional` to imports from `typing`.

## Verification
```bash
source venv/bin/activate
python3 -c "import chromadb; print('✅ ChromaDB imported successfully')"
python3 scripts/benchmarks/etb_benchmark.py --help
```

## Note
This patch is applied to the virtual environment. If you recreate the venv, you'll need to reapply this patch or use a ChromaDB version that supports Pydantic v2 natively.

