"""
Test script for hybrid LLM service
Tests the query complexity detection and provider routing.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend_python directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.llm_service import HybridLLMService, QueryComplexityAnalyzer

async def test_complexity_analyzer():
    """Test query complexity detection."""
    print("=" * 60)
    print("Testing Query Complexity Analyzer")
    print("=" * 60)
    
    analyzer = QueryComplexityAnalyzer()
    
    test_queries = [
        # Simple queries
        "What is machine learning?",
        "Define neural network",
        "What does AI mean?",
        "Yes or no: Is Python a programming language?",
        
        # Complex queries
        "Analyze the relationship between machine learning and artificial intelligence",
        "Compare and contrast supervised and unsupervised learning algorithms",
        "Explain the comprehensive process of training a deep neural network",
        "What are the various implications of using different activation functions?",
        
        # Medium complexity
        "How does a neural network work?",
        "What is the difference between machine learning and deep learning?",
        "Explain the process of gradient descent",
        
        # Edge cases
        "",
        "Hi",
        "Can you help me understand the complex relationships between multiple variables in statistical analysis and their implications for machine learning models?"
    ]
    
    for query in test_queries:
        complexity = analyzer.analyze_complexity(query)
        print(f"Query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        print(f"Complexity: {complexity.value}")
        print("-" * 40)

async def test_hybrid_service():
    """Test hybrid LLM service initialization and routing."""
    print("\n" + "=" * 60)
    print("Testing Hybrid LLM Service")
    print("=" * 60)
    
    # Initialize service
    service = HybridLLMService()
    
    print("Initializing hybrid LLM service...")
    success = await service.initialize()
    
    if success:
        print("✅ Hybrid LLM service initialized successfully")
        
        # Show available providers
        available = service.get_available_providers()
        status = service.get_provider_status()
        
        print(f"\nAvailable providers: {available}")
        print("Provider status:")
        for provider, is_available in status.items():
            status_icon = "✅" if is_available else "❌"
            print(f"  {status_icon} {provider}")
        
        # Test routing with different query types
        test_queries = [
            ("Simple query", "What is Python?"),
            ("Complex query", "Analyze the comprehensive relationship between machine learning algorithms and their performance metrics"),
            ("Medium query", "How does gradient descent work in neural networks?")
        ]
        
        print(f"\nTesting provider routing:")
        print("-" * 40)
        
        for query_type, query in test_queries:
            print(f"\n{query_type}: '{query}'")
            
            try:
                # Get the provider that would be selected
                provider = service.get_provider_for_query(query)
                print(f"Selected provider: {provider.provider.value}")
                
                # Test actual response generation (if providers are available)
                if available:
                    messages = [
                        {"role": "system", "content": "You are a helpful AI tutor."},
                        {"role": "user", "content": query}
                    ]
                    
                    print("Generating response...")
                    response = await service.generate_response(
                        messages=messages,
                        query=query,
                        max_tokens=100
                    )
                    
                    print(f"Response provider: {response.provider.value}")
                    print(f"Query complexity: {response.metadata.get('query_complexity', 'unknown')}")
                    print(f"Response: {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
    
    else:
        print("❌ Failed to initialize hybrid LLM service")
        print("This is expected if no LLM providers are configured")

async def test_streaming():
    """Test streaming response generation."""
    print("\n" + "=" * 60)
    print("Testing Streaming Response")
    print("=" * 60)
    
    service = HybridLLMService()
    await service.initialize()
    
    available = service.get_available_providers()
    if not available:
        print("No providers available for streaming test")
        return
    
    query = "Explain machine learning in simple terms"
    messages = [
        {"role": "system", "content": "You are a helpful AI tutor."},
        {"role": "user", "content": query}
    ]
    
    print(f"Testing streaming with query: '{query}'")
    print("Streaming response:")
    print("-" * 40)
    
    try:
        full_response = ""
        async for chunk in service.generate_streaming_response(
            messages=messages,
            query=query,
            max_tokens=50
        ):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print(f"\n\nFull response length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"❌ Streaming error: {e}")

async def main():
    """Run all tests."""
    print("Hybrid LLM Service Test Suite")
    print("=" * 60)
    
    # Test complexity analyzer
    await test_complexity_analyzer()
    
    # Test hybrid service
    await test_hybrid_service()
    
    # Test streaming
    await test_streaming()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)
    
    print("\nSetup Instructions:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. For OpenAI: Set OPENAI_API_KEY in .env")
    print("3. For Ollama: Install Ollama and run 'ollama serve'")
    print("4. Pull a model: 'ollama pull llama2' (or another model)")
    print("5. Run this test: python test_hybrid_llm.py")

if __name__ == "__main__":
    asyncio.run(main())
