"""
Monkey patch for ChromaDB compatibility.
This fixes the pydantic config issue by patching before ChromaDB imports.
"""
import os
import warnings

# Suppress pydantic warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")

# Set default config values to avoid pydantic inference issues
os.environ.setdefault('CHROMA_SERVER_HOST', 'localhost')
os.environ.setdefault('CHROMA_SERVER_HTTP_PORT', '8000')

# Disable ChromaDB telemetry to avoid capture() error
# This prevents the "capture() takes 1 positional argument but 3 were given" error
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'False')

# Import and patch chromadb.config before it's used
try:
    import chromadb.config
    # For ChromaDB 0.4.18, Settings doesn't accept extra fields
    # So we filter out any clickhouse-related kwargs that aren't in the model
    original_init = chromadb.config.Settings.__init__
    
    def patched_init(self, **kwargs):
        # Remove clickhouse fields if they're not part of the Settings model
        # These fields cause validation errors in ChromaDB 0.4.18
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                          if not k.startswith('clickhouse_')}
        return original_init(self, **filtered_kwargs)
    
    chromadb.config.Settings.__init__ = patched_init
except Exception as e:
    # If patching fails, continue anyway
    pass

# Note: ChromaDB telemetry errors are suppressed via ANONYMIZED_TELEMETRY=False
# If telemetry errors still occur, they will be caught and logged but won't crash the app

