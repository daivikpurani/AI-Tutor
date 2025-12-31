"""
Benchmark Configuration Module
Defines models to benchmark and test parameters.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from enum import Enum
import httpx

logger = logging.getLogger(__name__)

class BenchmarkModel:
    """Represents a model to benchmark."""
    
    def __init__(self, provider: str, model_name: str, display_name: str = None, 
                 metadata: Dict[str, Any] = None):
        self.provider = provider  # "ollama" or "openai"
        self.model_name = model_name
        self.display_name = display_name or model_name
        self.metadata = metadata or {}
        self.is_available = False
    
    def __repr__(self):
        return f"BenchmarkModel(provider={self.provider}, model={self.model_name}, available={self.is_available})"


class BenchmarkConfig:
    """Configuration for benchmarking multiple LLM models."""
    
    # Default models to benchmark
    DEFAULT_OLLAMA_MODELS = [
        "llama3.3:latest",
        "mistral:7b-instruct",
        "phi3:mini"
    ]
    
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
    
    def __init__(self):
        self.models: List[BenchmarkModel] = []
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.test_temperature = 0.7
        self.test_max_tokens = 1000
        self.test_mode = "exploration"  # or "assessment"
        
    async def detect_available_models(self) -> List[BenchmarkModel]:
        """Detect and return available models for benchmarking."""
        available_models = []
        
        # Detect Ollama models
        ollama_models = await self._detect_ollama_models()
        for model_name in ollama_models:
            if model_name in self.DEFAULT_OLLAMA_MODELS:
                model = BenchmarkModel(
                    provider="ollama",
                    model_name=model_name,
                    display_name=model_name,
                    metadata={"base_url": self.ollama_base_url}
                )
                model.is_available = True
                available_models.append(model)
        
        # Add OpenAI model (check availability separately)
        openai_model = BenchmarkModel(
            provider="openai",
            model_name=self.DEFAULT_OPENAI_MODEL,
            display_name=self.DEFAULT_OPENAI_MODEL,
            metadata={}
        )
        # OpenAI availability will be checked during initialization
        available_models.append(openai_model)
        
        self.models = available_models
        return available_models
    
    async def _detect_ollama_models(self) -> List[str]:
        """Detect available Ollama models via API."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for model_info in data.get("models", []):
                        model_name = model_info.get("name", "")
                        # Extract base model name (handle tags like "llama3.2:latest")
                        if ":" in model_name:
                            models.append(model_name)
                        else:
                            models.append(model_name)
                    logger.info(f"Detected Ollama models: {models}")
                    return models
                else:
                    logger.warning(f"Ollama API returned status {response.status_code}")
                    return []
        except Exception as e:
            logger.warning(f"Failed to detect Ollama models: {e}")
            return []
    
    def get_models_by_provider(self, provider: str) -> List[BenchmarkModel]:
        """Get all models for a specific provider."""
        return [m for m in self.models if m.provider == provider]
    
    def get_model(self, provider: str, model_name: str) -> Optional[BenchmarkModel]:
        """Get a specific model by provider and name."""
        for model in self.models:
            if model.provider == provider and model.model_name == model_name:
                return model
        return None
    
    def add_model(self, provider: str, model_name: str, display_name: str = None,
                  metadata: Dict[str, Any] = None) -> BenchmarkModel:
        """Manually add a model to the benchmark config."""
        model = BenchmarkModel(provider, model_name, display_name, metadata)
        self.models.append(model)
        return model
    
    def set_test_parameters(self, temperature: float = None, max_tokens: int = None,
                           mode: str = None):
        """Set test parameters for benchmarking."""
        if temperature is not None:
            self.test_temperature = temperature
        if max_tokens is not None:
            self.test_max_tokens = max_tokens
        if mode is not None:
            self.test_mode = mode
    
    def get_test_parameters(self) -> Dict[str, Any]:
        """Get current test parameters."""
        return {
            "temperature": self.test_temperature,
            "max_tokens": self.test_max_tokens,
            "mode": self.test_mode
        }


# Global benchmark config instance
benchmark_config = BenchmarkConfig()

