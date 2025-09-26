#!/usr/bin/env python3
"""
AI Tutor Backend Test Script
Tests all major functionality of the FastAPI backend.
"""

import asyncio
import httpx
import json
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_FILE_PATH = "test_document.txt"

async def test_api_endpoints():
    """Test all API endpoints."""
    print("🧪 Testing AI Tutor FastAPI Backend...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health Check
        print("1️⃣ Testing health check...")
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed: {data['status']}")
                print(f"   📊 Services: {data['services']}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        print()
        
        # Test 2: Root endpoint
        print("2️⃣ Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Root endpoint: {data['message']}")
            else:
                print(f"   ❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Root endpoint error: {e}")
        
        print()
        
        # Test 3: Chat endpoint
        print("3️⃣ Testing chat endpoint...")
        try:
            chat_data = {
                "message": "Hello! Can you help me understand machine learning?",
                "user_id": "test_user"
            }
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=chat_data
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Chat response received")
                print(f"   💬 Response: {data['response'][:100]}...")
                print(f"   📊 Context chunks used: {data['context_chunks_used']}")
            else:
                print(f"   ❌ Chat endpoint failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Chat endpoint error: {e}")
        
        print()
        
        # Test 4: Document upload (if test file exists)
        print("4️⃣ Testing document upload...")
        test_file_path = Path(TEST_FILE_PATH)
        if test_file_path.exists():
            try:
                with open(test_file_path, 'rb') as f:
                    files = {"file": (test_file_path.name, f, "text/plain")}
                    response = await client.post(
                        f"{BASE_URL}/api/upload",
                        files=files
                    )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Document uploaded: {data['filename']}")
                    print(f"   📄 Chunks created: {data['chunks_created']}")
                else:
                    print(f"   ❌ Upload failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
            except Exception as e:
                print(f"   ❌ Upload error: {e}")
        else:
            print(f"   ⚠️ Test file {TEST_FILE_PATH} not found, skipping upload test")
            print(f"   💡 Create a test file to test document upload functionality")
        
        print()
        
        # Test 5: List documents
        print("5️⃣ Testing document listing...")
        try:
            response = await client.get(f"{BASE_URL}/api/documents")
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                print(f"   ✅ Documents listed: {len(documents)} documents")
                for doc in documents:
                    print(f"      📄 {doc['filename']} ({doc['chunk_count']} chunks)")
            else:
                print(f"   ❌ Document listing failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Document listing error: {e}")
        
        print()
        
        # Test 6: Chat with context (if documents exist)
        print("6️⃣ Testing chat with context...")
        try:
            chat_data = {
                "message": "What did I upload? Can you summarize it?",
                "user_id": "test_user"
            }
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json=chat_data
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Context-aware response received")
                print(f"   💬 Response: {data['response'][:150]}...")
                print(f"   📊 Context chunks used: {data['context_chunks_used']}")
            else:
                print(f"   ❌ Context chat failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Context chat error: {e}")

def create_test_document():
    """Create a test document for upload testing."""
    test_content = """
    Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience.
    
    Types of Machine Learning:
    
    1. Supervised Learning: Learning with labeled training data
    - Classification: Predicting categories
    - Regression: Predicting continuous values
    
    2. Unsupervised Learning: Learning without labeled data
    - Clustering: Grouping similar data points
    - Dimensionality Reduction: Reducing data complexity
    
    3. Reinforcement Learning: Learning through interaction with environment
    - Agent learns through trial and error
    - Rewards and penalties guide learning
    
    Key Concepts:
    - Training Data: Data used to train the model
    - Features: Input variables used for prediction
    - Labels: Target variables in supervised learning
    - Model: The algorithm that makes predictions
    - Overfitting: When model performs well on training data but poorly on new data
    - Cross-validation: Technique to evaluate model performance
    
    Applications:
    - Image recognition
    - Natural language processing
    - Recommendation systems
    - Fraud detection
    - Medical diagnosis
    - Autonomous vehicles
    
    This is a comprehensive overview of machine learning fundamentals.
    """
    
    with open(TEST_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📄 Created test document: {TEST_FILE_PATH}")

async def main():
    """Main test function."""
    print("🚀 AI Tutor Backend Test Suite")
    print("=" * 50)
    
    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/health", timeout=5.0)
            if response.status_code != 200:
                print("❌ Backend is not running or not responding")
                print("💡 Start the backend with: ./start.sh")
                return
    except Exception as e:
        print("❌ Cannot connect to backend")
        print("💡 Make sure the backend is running on http://localhost:8000")
        print(f"   Error: {e}")
        return
    
    # Create test document if it doesn't exist
    if not Path(TEST_FILE_PATH).exists():
        create_test_document()
        print()
    
    # Run tests
    await test_api_endpoints()
    
    print("=" * 50)
    print("🎉 Test suite completed!")
    print("💡 Check the results above to verify all functionality")
    
    # Cleanup
    if Path(TEST_FILE_PATH).exists():
        os.remove(TEST_FILE_PATH)
        print(f"🧹 Cleaned up test file: {TEST_FILE_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
