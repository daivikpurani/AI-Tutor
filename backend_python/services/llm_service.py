"""
LLM Service Abstraction
Provides a unified interface for multiple LLM providers with hybrid routing.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod
from enum import Enum

import openai
from openai import AsyncOpenAI
import ollama
import httpx

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    MOCK = "mock"

class QueryComplexity(Enum):
    """Query complexity levels for routing decisions."""
    SIMPLE = "simple"      # Can be handled by local/fast models
    COMPLEX = "complex"    # Requires more capable models
    UNKNOWN = "unknown"    # Default fallback

class LLMResponse:
    """Standardized response from any LLM provider."""
    
    def __init__(self, content: str, provider: LLMProvider, model: str, 
                 usage: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        self.content = content
        self.provider = provider
        self.model = model
        self.usage = usage or {}
        self.metadata = metadata or {}

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.is_available = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider and check availability."""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM."""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self):
        super().__init__(LLMProvider.OPENAI)
        self.client = None
        self.default_model = "gpt-3.5-turbo"
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client."""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY not found")
                return False
            
            self.client = AsyncOpenAI(api_key=api_key)
            
            # Test the connection
            try:
                await self.client.models.list()
                self.is_available = True
                logger.info("OpenAI provider initialized successfully")
                return True
            except Exception as e:
                logger.error(f"OpenAI connection test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            return False
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        if not self.is_available:
            raise RuntimeError("OpenAI provider not available")
        
        model = model or self.default_model
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider,
                model=model,
                usage={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API."""
        if not self.is_available:
            raise RuntimeError("OpenAI provider not available")
        
        model = model or self.default_model
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            raise

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self):
        super().__init__(LLMProvider.OLLAMA)
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.default_model = os.getenv('OLLAMA_DEFAULT_MODEL', 'llama2')
    
    async def initialize(self) -> bool:
        """Initialize Ollama client."""
        try:
            # Test connection to Ollama server
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    self.is_available = True
                    logger.info("Ollama provider initialized successfully")
                    return True
                else:
                    logger.warning(f"Ollama server not responding: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.warning(f"Ollama provider not available: {e}")
            return False
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Ollama API."""
        if not self.is_available:
            raise RuntimeError("Ollama provider not available")
        
        model = model or self.default_model
        
        try:
            # Convert messages to Ollama format
            prompt = self._convert_messages_to_prompt(messages)
            
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )
            
            return LLMResponse(
                content=response['message']['content'],
                provider=self.provider,
                model=model,
                usage={}  # Ollama doesn't provide usage stats
            )
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Ollama API."""
        if not self.is_available:
            raise RuntimeError("Ollama provider not available")
        
        model = model or self.default_model
        
        try:
            # Convert messages to Ollama format
            prompt = self._convert_messages_to_prompt(messages)
            
            stream = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                stream=True
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            logger.error(f"Ollama streaming API error: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt."""
        prompt_parts = []
        
        for message in messages:
            role = message['role']
            content = message['content']
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"

class MockProvider(BaseLLMProvider):
    """Mock provider for testing and fallback."""
    
    def __init__(self):
        super().__init__(LLMProvider.MOCK)
        self.is_available = True
    
    async def initialize(self) -> bool:
        """Mock provider is always available."""
        logger.info("Mock provider initialized")
        return True
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock response."""
        user_message = messages[-1]['content'] if messages else "Hello"
        
        mock_responses = [
            f"I understand you're asking about: {user_message}. This is a mock response from the local system.",
            f"Based on your question '{user_message}', here's a helpful response generated locally.",
            f"Thank you for your question about {user_message}. I'm processing this with our local AI system."
        ]
        
        import random
        content = random.choice(mock_responses)
        
        return LLMResponse(
            content=content,
            provider=self.provider,
            model="mock-model",
            usage={'total_tokens': len(content.split())}
        )
    
    async def generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate mock streaming response."""
        response = await self.generate_response(messages, model, max_tokens, temperature, **kwargs)
        
        # Simulate streaming by yielding words
        words = response.content.split()
        for word in words:
            yield word + " "
            import asyncio
            await asyncio.sleep(0.05)  # Small delay to simulate streaming

class QueryComplexityAnalyzer:
    """Analyzes query complexity to determine routing strategy."""
    
    def __init__(self):
        # Keywords that indicate complex queries
        self.complex_keywords = [
            'analyze', 'compare', 'explain', 'describe', 'evaluate', 'assess',
            'synthesis', 'comprehensive', 'detailed', 'thorough', 'in-depth',
            'multiple', 'various', 'different', 'relationship', 'connection',
            'implications', 'consequences', 'significance', 'importance'
        ]
        
        # Keywords that indicate simple queries
        self.simple_keywords = [
            'what is', 'define', 'meaning', 'simple', 'basic', 'quick',
            'brief', 'short', 'yes', 'no', 'true', 'false'
        ]
        
        # Question patterns that indicate complexity
        self.complex_patterns = [
            r'how.*work', r'why.*happen', r'what.*difference',
            r'compare.*and', r'analyze.*relationship', r'explain.*process'
        ]
        
        self.simple_patterns = [
            r'^what is', r'^define', r'^meaning of', r'^yes or no'
        ]
    
    def analyze_complexity(self, query: str) -> QueryComplexity:
        """Analyze query complexity and return routing recommendation."""
        if not query or len(query.strip()) < 3:
            return QueryComplexity.SIMPLE
        
        query_lower = query.lower().strip()
        
        # Check for simple patterns first
        import re
        for pattern in self.simple_patterns:
            if re.search(pattern, query_lower):
                return QueryComplexity.SIMPLE
        
        # Check for complex patterns
        for pattern in self.complex_patterns:
            if re.search(pattern, query_lower):
                return QueryComplexity.COMPLEX
        
        # Check keyword presence
        complex_count = sum(1 for keyword in self.complex_keywords if keyword in query_lower)
        simple_count = sum(1 for keyword in self.simple_keywords if keyword in query_lower)
        
        # Check query length and structure
        word_count = len(query.split())
        has_question_mark = '?' in query
        has_multiple_sentences = query.count('.') > 0
        
        # Scoring system
        complexity_score = 0
        
        # Length factors
        if word_count > 20:
            complexity_score += 2
        elif word_count > 10:
            complexity_score += 1
        
        # Structure factors
        if has_multiple_sentences:
            complexity_score += 1
        if has_question_mark and word_count > 15:
            complexity_score += 1
        
        # Keyword factors
        complexity_score += complex_count * 2
        complexity_score -= simple_count
        
        # Decision logic
        if complexity_score >= 3:
            return QueryComplexity.COMPLEX
        elif complexity_score <= 0:
            return QueryComplexity.SIMPLE
        else:
            return QueryComplexity.UNKNOWN

class HybridLLMService:
    """Hybrid LLM service that routes queries to appropriate providers."""
    
    def __init__(self):
        self.providers = {}
        self.complexity_analyzer = QueryComplexityAnalyzer()
        self.routing_strategy = {
            QueryComplexity.SIMPLE: [LLMProvider.OLLAMA, LLMProvider.MOCK],
            QueryComplexity.COMPLEX: [LLMProvider.OPENAI, LLMProvider.OLLAMA],
            QueryComplexity.UNKNOWN: [LLMProvider.OLLAMA, LLMProvider.OPENAI, LLMProvider.MOCK]
        }
    
    async def initialize(self) -> bool:
        """Initialize all available providers."""
        # Initialize providers in order of preference
        self.providers[LLMProvider.OPENAI] = OpenAIProvider()
        self.providers[LLMProvider.OLLAMA] = OllamaProvider()
        self.providers[LLMProvider.MOCK] = MockProvider()
        
        # Initialize each provider
        for provider in self.providers.values():
            try:
                await provider.initialize()
            except Exception as e:
                logger.warning(f"Provider {provider.provider.value} initialization failed: {e}")
        
        available_providers = [p.provider.value for p in self.providers.values() if p.is_available]
        logger.info(f"Available LLM providers: {available_providers}")
        
        return len(available_providers) > 0
    
    def get_provider_for_query(self, query: str) -> BaseLLMProvider:
        """Get the best provider for a given query."""
        complexity = self.complexity_analyzer.analyze_complexity(query)
        preferred_providers = self.routing_strategy.get(complexity, [LLMProvider.MOCK])
        
        logger.info(f"Query complexity: {complexity.value}, routing to: {[p.value for p in preferred_providers]}")
        
        # Find first available provider in preference order
        for provider_type in preferred_providers:
            provider = self.providers.get(provider_type)
            if provider and provider.is_available:
                logger.info(f"Selected provider: {provider_type.value}")
                return provider
        
        # Fallback to mock provider
        logger.warning("No preferred providers available, using mock provider")
        return self.providers[LLMProvider.MOCK]
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        query: str = None,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using hybrid routing."""
        if not query and messages:
            query = messages[-1].get('content', '')
        
        provider = self.get_provider_for_query(query)
        
        try:
            response = await provider.generate_response(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Add routing metadata
            response.metadata['routing_provider'] = provider.provider.value
            response.metadata['query_complexity'] = self.complexity_analyzer.analyze_complexity(query).value
            
            return response
            
        except Exception as e:
            logger.error(f"Error with provider {provider.provider.value}: {e}")
            
            # Try fallback providers
            for fallback_provider in self.providers.values():
                if fallback_provider.is_available and fallback_provider != provider:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider.provider.value}")
                        response = await fallback_provider.generate_response(
                            messages=messages,
                            model=model,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            **kwargs
                        )
                        response.metadata['routing_provider'] = fallback_provider.provider.value
                        response.metadata['fallback_used'] = True
                        return response
                    except Exception as fallback_error:
                        logger.warning(f"Fallback provider {fallback_provider.provider.value} also failed: {fallback_error}")
                        continue
            
            # All providers failed, raise the original error
            raise
    
    async def generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        query: str = None,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using hybrid routing."""
        if not query and messages:
            query = messages[-1].get('content', '')
        
        provider = self.get_provider_for_query(query)
        
        try:
            async for chunk in provider.generate_streaming_response(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error with provider {provider.provider.value}: {e}")
            
            # Try fallback providers
            for fallback_provider in self.providers.values():
                if fallback_provider.is_available and fallback_provider != provider:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider.provider.value}")
                        async for chunk in fallback_provider.generate_streaming_response(
                            messages=messages,
                            model=model,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            **kwargs
                        ):
                            yield chunk
                        return
                    except Exception as fallback_error:
                        logger.warning(f"Fallback provider {fallback_provider.provider.value} also failed: {fallback_error}")
                        continue
            
            # All providers failed, yield error message
            yield f"Error: Unable to generate response. All providers failed. Original error: {str(e)}"
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.provider.value for p in self.providers.values() if p.is_available]
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {p.provider.value: p.is_available for p in self.providers.values()}
