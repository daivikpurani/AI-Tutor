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

# Try to import tiktoken for token counting (optional)
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)

if not TIKTOKEN_AVAILABLE:
    logger.warning("tiktoken not available, token counting for Ollama will be approximate")

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
            from utils.config import settings
            api_key = settings.openai_api_key
            if not api_key:
                logger.warning("OPENAI_API_KEY not found")
                return False
            
            self.client = AsyncOpenAI(api_key=api_key)
            # Align default model with configuration
            if getattr(settings, 'openai_model', None):
                self.default_model = settings.openai_model
            
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
            # Debug: Log what we're sending to OpenAI
            user_message = messages[-1]['content'] if messages else ""
            logger.info(f"OpenAI streaming request - Model: {model}, User message length: {len(user_message)}")
            logger.debug(f"OpenAI user message: {user_message[:200]}...")
            
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            
            chunk_count = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    if content and content.strip():  # Only yield non-empty content
                        chunk_count += 1
                        logger.debug(f"OpenAI chunk {chunk_count}: {content[:50]}...")
                        yield content
            
            logger.info(f"OpenAI streaming complete - {chunk_count} chunks yielded")
                    
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
            # Sync defaults from settings if available
            try:
                from utils.config import settings
                if getattr(settings, 'ollama_base_url', None):
                    self.base_url = settings.ollama_base_url
                if getattr(settings, 'ollama_default_model', None):
                    self.default_model = settings.ollama_default_model
            except Exception:
                pass
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
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using tiktoken or approximation."""
        if TIKTOKEN_AVAILABLE:
            try:
                # Use cl100k_base encoding (used by GPT-3.5/GPT-4)
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))
            except Exception as e:
                logger.warning(f"Token counting failed: {e}, using approximation")
        
        # Fallback: approximate tokens (1 token ≈ 4 characters)
        return len(text) // 4
    
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
            
            response_content = response['message']['content']
            
            # Estimate token usage
            prompt_tokens = self._estimate_tokens(prompt)
            completion_tokens = self._estimate_tokens(response_content)
            total_tokens = prompt_tokens + completion_tokens
            
            return LLMResponse(
                content=response_content,
                provider=self.provider,
                model=model,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
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
            
            # Debug: Log what we're sending to Ollama
            logger.info(f"Ollama streaming request - Model: {model}, Prompt length: {len(prompt)}")
            logger.debug(f"Ollama prompt: {prompt[:200]}...")
            
            stream = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                stream=True
            )
            
            chunk_count = 0
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    if content and content.strip():  # Only yield non-empty content
                        chunk_count += 1
                        logger.debug(f"Ollama chunk {chunk_count}: {content[:50]}...")
                        yield content
            
            logger.info(f"Ollama streaming complete - {chunk_count} chunks yielded")
                    
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
        
        # Return the prompt without the "Assistant:" suffix to avoid confusion
        return "\n\n".join(prompt_parts)

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
        
        # Extract the actual question from the user message
        # The user message contains the full prompt, we need to extract just the question
        question = user_message
        if "Student's question:" in user_message:
            # Extract just the question part (stop before prompt instructions)
            question_section = user_message.split("Student's question:", 1)[1]
            question_section = question_section.strip()
            # Stop at the first known delimiter that indicates extra metadata/instructions
            delimiters = [
                "\nPrevious conversation",
                "\n[RETRIEVAL",
                "\nRelevant context",
                "\n[EXAMPLES",
                "\n[CHAIN-OF-THOUGHT",
                "\n[EXPLORATION MODE",
                "\n[ASSESSMENT MODE",
                "\n[FINAL REMINDERS]",
                "\n⚠️",
                "\n\n"
            ]
            for delimiter in delimiters:
                idx = question_section.find(delimiter)
                if idx != -1:
                    question_section = question_section[:idx]
                    break
            # Use first line if multiple remain
            question_lines = [line.strip() for line in question_section.splitlines() if line.strip()]
            if question_lines:
                question = question_lines[0]
            else:
                question = question_section.strip()
        
        # Generate a proper mock response about the question
        mock_responses = [
            f"I'd be happy to help explain {question}. This is a mock response from our local AI system. In a real implementation, this would provide detailed information about the topic.",
            f"Great question about {question}! This is a simulated response. The actual AI would provide comprehensive information about this topic.",
            f"Let me help you understand {question}. This is a mock response, but in production, you'd get detailed explanations and examples."
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
            # Default preference is local first for cost/token balance, escalate as needed
            QueryComplexity.SIMPLE: [LLMProvider.OLLAMA, LLMProvider.OPENAI, LLMProvider.MOCK],
            QueryComplexity.COMPLEX: [LLMProvider.OLLAMA, LLMProvider.OPENAI, LLMProvider.MOCK],
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
        
        # Log provider availability
        for provider_type, provider in self.providers.items():
            logger.info(f"Provider {provider_type.value}: available={provider.is_available}")
        
        # Find first available provider in preference order
        for provider_type in preferred_providers:
            provider = self.providers.get(provider_type)
            if provider and provider.is_available:
                logger.info(f"Selected provider: {provider_type.value}")
                return provider
        
        # Fallback to mock provider
        logger.warning("No preferred providers available, using mock provider")
        return self.providers[LLMProvider.MOCK]

    async def _self_check(self, draft_answer: str, mode: str) -> Dict[str, Any]:
        """Run a lightweight self-check to estimate confidence and detect issues."""
        from utils.prompts import PromptTemplates
        from utils.config import settings
        messages: List[Dict[str, str]] = []
        if mode == "assessment":
            system_text = PromptTemplates.SELF_CHECK_ASSESSMENT
        else:
            system_text = PromptTemplates.SELF_CHECK_EXPLORATION
        messages.append({"role": "system", "content": system_text})
        messages.append({
            "role": "user",
            "content": f"Answer to validate:\n{draft_answer}\nReturn ONLY the JSON."
        })

        # Prefer OpenAI mini for reliable JSON; fallback to Ollama
        provider: Optional[BaseLLMProvider] = None
        if self.providers.get(LLMProvider.OPENAI) and self.providers[LLMProvider.OPENAI].is_available:
            provider = self.providers[LLMProvider.OPENAI]
            model = getattr(settings, 'openai_model', None) or None
        else:
            provider = self.providers.get(LLMProvider.OLLAMA)
            model = getattr(settings, 'ollama_default_model', None) or None

        if not provider:
            return {"confidence": 0.0, "issues": ["no_provider"], "missing_citations": True}

        try:
            resp = await provider.generate_response(messages=messages, model=model, max_tokens=200, temperature=0)
            raw = resp.content or "{}"
            # Attempt to locate JSON in text
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1 and end > start:
                raw = raw[start:end+1]
            data = json.loads(raw)
            return data
        except Exception as e:
            logger.warning(f"Self-check parsing failed: {e}")
            # Conservative low confidence on parse failure
            if mode == "assessment":
                return {"confidence": 0.0, "issues": ["parse_error"], "missing_citations": True}
            return {"confidence": 0.3, "notes": ["parse_error"]}
    
    async def generate_response_with_provider(
        self,
        messages: List[Dict[str, str]],
        provider: LLMProvider,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using a specific provider and model (for benchmarking).
        Bypasses hybrid routing logic.
        
        Args:
            messages: List of message dictionaries
            provider: Specific provider to use
            model: Specific model name (optional, uses default if not provided)
            max_tokens: Maximum tokens to generate
            temperature: Temperature setting
            **kwargs: Additional arguments
            
        Returns:
            LLMResponse from the specified provider
        """
        provider_instance = self.providers.get(provider)
        if not provider_instance:
            raise ValueError(f"Provider {provider.value} not initialized")
        
        if not provider_instance.is_available:
            raise RuntimeError(f"Provider {provider.value} is not available")
        
        # Use default model if not specified
        if not model:
            if provider == LLMProvider.OPENAI:
                from utils.config import settings
                model = getattr(settings, 'openai_model', 'gpt-4o-mini')
            elif provider == LLMProvider.OLLAMA:
                model = provider_instance.default_model
        
        return await provider_instance.generate_response(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        query: str = None,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response using hybrid routing with self-check and escalation."""
        if not query and messages:
            query = messages[-1].get('content', '')
        mode = kwargs.get('mode', 'exploration')
        from utils.config import settings

        # Always attempt a local draft first for token/latency balance
        draft_provider = self.providers.get(LLMProvider.OLLAMA) if self.providers.get(LLMProvider.OLLAMA) and self.providers[LLMProvider.OLLAMA].is_available else None
        hosted_provider = self.providers.get(LLMProvider.OPENAI) if self.providers.get(LLMProvider.OPENAI) and self.providers[LLMProvider.OPENAI].is_available else None

        # If no local, try hosted directly
        primary_provider = draft_provider or hosted_provider or self.providers[LLMProvider.MOCK]

        # Adjust generation params by mode
        if mode == 'assessment':
            max_tokens = min(max_tokens, getattr(settings, 'assessment_max_gen_tokens', 600))
            temperature = getattr(settings, 'assessment_temperature', 0.2)
        else:
            max_tokens = min(max_tokens, getattr(settings, 'exploration_max_gen_tokens', 400))
            temperature = getattr(settings, 'exploration_temperature', 0.7)

        # Generate draft
        draft = await primary_provider.generate_response(
            messages=messages,
            model=(getattr(settings, 'ollama_default_model', None) if primary_provider.provider == LLMProvider.OLLAMA else getattr(settings, 'openai_model', None)),
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Self-check and potential escalation
        check = await self._self_check(draft.content, mode)
        assessment_min = getattr(settings, 'assessment_min_conf', 0.72)
        exploration_min = getattr(settings, 'exploration_min_conf', 0.55)
        threshold = assessment_min if mode == 'assessment' else exploration_min
        missing_citations = bool(check.get('missing_citations', False)) if mode == 'assessment' else False
        confidence = float(check.get('confidence', 0.0)) if isinstance(check.get('confidence', None), (int, float)) else 0.0

        escalated = False
        final_response = draft
        if (confidence < threshold) or missing_citations:
            if hosted_provider:
                escalated = True
                try:
                    final_response = await hosted_provider.generate_response(
                        messages=messages,
                        model=getattr(settings, 'openai_model', None),
                        max_tokens=max_tokens,
                        temperature=temperature if mode == 'exploration' else 0.3,
                    )
                except Exception as e:
                    logger.warning(f"Escalation to hosted provider failed: {e}")
                    final_response = draft

        # Attach metadata
        final_response.metadata['routing_provider'] = final_response.provider.value
        final_response.metadata['query_complexity'] = self.complexity_analyzer.analyze_complexity(query).value
        final_response.metadata['confidence'] = confidence
        final_response.metadata['escalated'] = escalated
        # Structured log for observability
        logger.info(json.dumps({
            "event": "hybrid_decision",
            "provider": final_response.provider.value,
            "model": final_response.model,
            "escalated": escalated,
            "confidence": confidence,
            "complexity": final_response.metadata['query_complexity']
        }))

        return final_response
    
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
