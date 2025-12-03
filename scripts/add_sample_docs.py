#!/usr/bin/env python3
"""
Script to add sample educational documents about RAG, AI, ML, and CS to the vector database.
"""

import sys
import os
import asyncio

# Add backend_python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend_python'))

from services.vector_db import VectorDatabase

# Sample documents covering RAG, AI, ML, and CS topics
DOCUMENTS = [
    {
        "filename": "rag_overview.md",
        "text": """
# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is a technique that enhances large language models by combining them with external knowledge retrieval systems. RAG addresses the limitations of LLMs, such as their inability to access real-time information or domain-specific knowledge that wasn't in their training data.

## How RAG Works

RAG operates in two main phases:

1. **Retrieval Phase**: When a query is received, the system searches a knowledge base (typically a vector database) to find relevant information chunks that are semantically similar to the query.

2. **Augmentation Phase**: The retrieved context is combined with the original query and passed to the LLM, which generates a response informed by both its pre-trained knowledge and the retrieved context.

## Benefits of RAG

- **Up-to-date Information**: Can incorporate recent information not in training data
- **Domain-Specific Knowledge**: Can access specialized knowledge bases
- **Transparency**: Provides citations and sources for generated content
- **Reduced Hallucination**: Grounds responses in retrieved documents
- **Cost Efficiency**: Avoids expensive fine-tuning for domain adaptation

## Architecture Components

A typical RAG system consists of:
- Document ingestion pipeline (chunking, embedding)
- Vector database for semantic search
- Embedding model for converting text to vectors
- LLM for generating responses
- Retrieval mechanism (similarity search, reranking)
"""
    },
    {
        "filename": "vector_databases.md",
        "text": """
# Vector Databases

Vector databases are specialized databases designed to store, index, and query high-dimensional vectors efficiently. They are essential for semantic search, recommendation systems, and RAG applications.

## Key Concepts

**Embeddings**: Text, images, or other data converted into numerical vectors that capture semantic meaning. Similar items have similar vectors.

**Similarity Search**: Finding vectors that are most similar to a query vector, typically using cosine similarity, Euclidean distance, or dot product.

**Indexing**: Efficient data structures (like HNSW, IVF, or LSH) that enable fast approximate nearest neighbor search in high-dimensional spaces.

## Popular Vector Databases

- **ChromaDB**: Lightweight, open-source, easy to use
- **Pinecone**: Managed service with high performance
- **Weaviate**: Open-source with GraphQL API
- **Milvus**: Scalable, production-ready
- **Qdrant**: Fast, written in Rust

## Use Cases

- Semantic search and retrieval
- Recommendation systems
- Anomaly detection
- Image and video search
- RAG applications for LLMs
"""
    },
    {
        "filename": "embeddings.md",
        "text": """
# Embeddings for Document Search

Embeddings are dense vector representations of text that capture semantic meaning. They enable computers to understand and compare text based on meaning rather than exact word matching.

## How Embeddings Work

Embeddings are generated using neural network models (like BERT, GPT, or specialized embedding models) that learn to represent text as vectors in a high-dimensional space. Words or sentences with similar meanings are positioned close together in this space.

## Embedding Models

**Sentence Transformers**: Models specifically designed for creating sentence embeddings:
- all-MiniLM-L6-v2: Fast, lightweight, good for general use
- all-mpnet-base-v2: Higher quality, slower
- multilingual models for non-English text

**OpenAI Embeddings**: 
- text-embedding-ada-002: High-quality embeddings via API

## Embedding Process

1. **Text Preprocessing**: Clean and normalize text
2. **Tokenization**: Break text into tokens
3. **Model Encoding**: Pass tokens through embedding model
4. **Vector Output**: Receive dense vector representation (typically 384-1536 dimensions)

## Similarity Metrics

- **Cosine Similarity**: Measures angle between vectors (most common for embeddings)
- **Euclidean Distance**: Measures straight-line distance
- **Dot Product**: Measures vector alignment

## Applications

- Semantic search
- Document clustering
- Duplicate detection
- Content recommendation
- RAG systems
"""
    },
    {
        "filename": "transformer_architecture.md",
        "text": """
# Transformer Architecture

The Transformer architecture, introduced in "Attention Is All You Need" (2017), revolutionized natural language processing and became the foundation for modern LLMs like GPT, BERT, and T5.

## Key Components

**Self-Attention Mechanism**: Allows the model to weigh the importance of different words in a sequence when processing each word. This enables understanding of long-range dependencies.

**Multi-Head Attention**: Runs multiple attention mechanisms in parallel, allowing the model to focus on different types of relationships simultaneously.

**Positional Encoding**: Adds information about word positions since transformers don't inherently understand sequence order.

**Feed-Forward Networks**: Applied to each position independently, typically consisting of two linear transformations with a ReLU activation.

**Layer Normalization**: Stabilizes training by normalizing inputs across features.

**Residual Connections**: Skip connections that help with gradient flow during training.

## Architecture Variants

**Encoder-Only** (BERT): Bidirectional understanding, good for classification and understanding tasks.

**Decoder-Only** (GPT): Autoregressive generation, good for text generation and completion.

**Encoder-Decoder** (T5, BART): Full sequence-to-sequence models, good for translation and summarization.

## Why Transformers Work Well

- Parallel processing (unlike RNNs)
- Long-range dependency modeling
- Transfer learning capabilities
- Scalability to very large models
"""
    },
    {
        "filename": "attention_mechanism.md",
        "text": """
# Attention Mechanism

The attention mechanism is a fundamental component of transformer architectures that allows models to focus on relevant parts of the input when making predictions.

## Core Concept

Attention computes a weighted sum of values, where the weights are determined by the compatibility between a query and a set of keys. This allows the model to dynamically focus on different parts of the input.

## Attention Formula

Attention(Q, K, V) = softmax(QK^T / √d_k) V

Where:
- Q (Query): What we're looking for
- K (Key): What each position offers
- V (Value): The actual content at each position
- d_k: Dimension of keys (for scaling)

## Types of Attention

**Self-Attention**: Queries, keys, and values all come from the same sequence. Allows each position to attend to all positions in the sequence.

**Cross-Attention**: Queries come from one sequence, keys and values from another. Used in encoder-decoder architectures.

**Multi-Head Attention**: Multiple attention mechanisms run in parallel, each learning different types of relationships.

## Why Attention Matters

- Captures long-range dependencies
- Provides interpretability (attention weights show what the model focuses on)
- Enables parallel computation
- Handles variable-length sequences naturally
- Allows the model to learn which parts of input are relevant

## Applications Beyond NLP

- Computer vision (Vision Transformers)
- Speech recognition
- Graph neural networks
- Multi-modal learning
"""
    },
    {
        "filename": "neural_networks_backpropagation.md",
        "text": """
# Backpropagation in Neural Networks

Backpropagation is the algorithm used to train neural networks by efficiently computing gradients of the loss function with respect to network parameters.

## How It Works

1. **Forward Pass**: Input data flows through the network, producing predictions and computing loss.

2. **Backward Pass**: Gradients are computed starting from the output layer and propagated backward through the network using the chain rule of calculus.

3. **Parameter Update**: Weights and biases are updated using the computed gradients (typically via gradient descent or variants like Adam).

## Chain Rule

Backpropagation relies on the chain rule: if y = f(g(x)), then dy/dx = (dy/dg) * (dg/dx). This allows gradients to be computed layer by layer.

## Key Concepts

**Loss Function**: Measures how far predictions are from true values (e.g., cross-entropy, MSE).

**Gradient**: Partial derivative showing how loss changes with respect to each parameter.

**Learning Rate**: Step size for parameter updates (too large = unstable, too small = slow convergence).

**Vanishing Gradients**: Problem in deep networks where gradients become very small, making early layers hard to train.

**Exploding Gradients**: Problem where gradients become very large, causing unstable training.

## Modern Improvements

- Batch normalization
- Residual connections
- Gradient clipping
- Adaptive optimizers (Adam, RMSprop)
- Better initialization strategies
"""
    },
    {
        "filename": "supervised_unsupervised_learning.md",
        "text": """
# Supervised vs Unsupervised Learning

Machine learning can be broadly categorized into supervised and unsupervised learning based on the availability of labeled training data.

## Supervised Learning

Supervised learning uses labeled training data where each example has an input and a corresponding correct output.

**Examples**:
- Classification: Predicting categories (spam/not spam, image recognition)
- Regression: Predicting continuous values (house prices, temperature)

**Common Algorithms**:
- Linear regression
- Logistic regression
- Decision trees
- Random forests
- Support vector machines
- Neural networks

**Advantages**: Clear evaluation metrics, well-understood, widely applicable.

**Disadvantages**: Requires labeled data (expensive/time-consuming to create).

## Unsupervised Learning

Unsupervised learning finds patterns in data without labeled examples.

**Examples**:
- Clustering: Grouping similar data points (customer segmentation)
- Dimensionality reduction: Reducing feature space (PCA, t-SNE)
- Anomaly detection: Finding unusual patterns
- Association rules: Finding relationships (market basket analysis)

**Common Algorithms**:
- K-means clustering
- Hierarchical clustering
- Principal Component Analysis (PCA)
- Autoencoders
- Generative models (GANs, VAEs)

**Advantages**: No labels needed, can discover hidden patterns.

**Disadvantages**: Harder to evaluate, less predictable outcomes.

## Semi-Supervised Learning

Uses both labeled and unlabeled data, common in real-world scenarios where labeling is expensive but unlabeled data is abundant.
"""
    },
    {
        "filename": "llm_training_challenges.md",
        "text": """
# Challenges in Training Large Language Models

Training large language models presents numerous technical, computational, and practical challenges.

## Computational Challenges

**Scale**: Modern LLMs have billions or trillions of parameters, requiring massive computational resources.

**Memory**: Storing model weights, activations, and gradients requires significant GPU memory.

**Training Time**: Training can take weeks or months even with powerful hardware clusters.

**Cost**: Training costs can reach millions of dollars in compute resources.

## Technical Challenges

**Vanishing/Exploding Gradients**: Deep networks struggle with gradient flow, addressed through normalization and residual connections.

**Overfitting**: Large models can memorize training data rather than generalize, requiring regularization techniques.

**Catastrophic Forgetting**: When fine-tuning, models may forget previously learned knowledge.

**Hallucination**: Models generate plausible but incorrect information, especially for facts not in training data.

**Bias and Fairness**: Models can perpetuate or amplify biases present in training data.

## Data Challenges

**Data Quality**: Requires massive, high-quality, diverse datasets.

**Data Curation**: Filtering harmful, biased, or low-quality content is difficult at scale.

**Copyright and Licensing**: Ensuring legal use of training data.

**Multilingual Support**: Creating balanced multilingual datasets.

## Optimization Challenges

**Hyperparameter Tuning**: Finding optimal learning rates, batch sizes, and architectures.

**Distributed Training**: Coordinating training across multiple GPUs/nodes efficiently.

**Mixed Precision**: Using lower precision (FP16/BF16) to speed up training while maintaining stability.

## Mitigation Strategies

- Transfer learning and fine-tuning
- Retrieval-Augmented Generation (RAG)
- Parameter-efficient fine-tuning (LoRA, QLoRA)
- Model distillation
- Better evaluation metrics
- Human feedback (RLHF)
"""
    },
    {
        "filename": "openai_vs_local_llm.md",
        "text": """
# OpenAI vs Local LLM Tradeoffs

Choosing between cloud-based APIs (like OpenAI) and local LLMs involves balancing multiple factors.

## OpenAI/Cloud APIs Advantages

**Performance**: State-of-the-art models (GPT-4, Claude) with superior capabilities.

**No Infrastructure**: No need to manage hardware, GPUs, or model deployment.

**Scalability**: Automatically handles load and scaling.

**Up-to-Date**: Access to latest model versions and improvements.

**Cost Efficiency (for low volume)**: Pay-per-use can be cheaper than maintaining infrastructure.

## OpenAI/Cloud APIs Disadvantages

**Cost at Scale**: Can become expensive with high usage volumes.

**Latency**: Network round-trips add latency compared to local inference.

**Data Privacy**: Queries sent to external servers raise privacy concerns.

**Vendor Lock-in**: Dependency on external service availability and pricing.

**Limited Control**: Cannot fine-tune or modify models easily.

**Rate Limits**: API usage restrictions may limit throughput.

## Local LLMs Advantages

**Privacy**: All data stays on-premises, no external transmission.

**Cost at Scale**: Lower marginal cost for high-volume usage.

**Latency**: Faster response times without network overhead.

**Control**: Full control over models, fine-tuning, and deployment.

**Offline Capability**: Works without internet connection.

**No Rate Limits**: Process as many requests as hardware allows.

## Local LLMs Disadvantages

**Hardware Requirements**: Need powerful GPUs and significant memory.

**Model Quality**: Generally lower performance than top cloud models.

**Maintenance**: Must manage infrastructure, updates, and scaling.

**Initial Setup Cost**: Significant upfront investment in hardware.

**Expertise Required**: Need ML/DevOps knowledge for deployment and optimization.

## Hybrid Approach

Many systems use local models for simple queries and cloud APIs for complex tasks, balancing cost, privacy, and performance.
"""
    },
    {
        "filename": "rag_benefits_drawbacks.md",
        "text": """
# RAG Architecture: Benefits and Drawbacks

RAG (Retrieval-Augmented Generation) combines information retrieval with language generation, offering both advantages and limitations.

## Benefits

**Access to Current Information**: Can incorporate information not in training data, including recent events and domain-specific knowledge.

**Reduced Hallucination**: Grounding responses in retrieved documents reduces fabrication of facts.

**Transparency**: Provides citations and sources, improving trustworthiness and verifiability.

**Cost Efficiency**: Avoids expensive fine-tuning; can update knowledge by adding documents.

**Domain Adaptation**: Easy to adapt to new domains by adding relevant documents.

**Interpretability**: Users can see which documents informed the response.

**Scalability**: Can handle growing knowledge bases without retraining models.

## Drawbacks

**Retrieval Quality**: System performance heavily depends on retrieval quality; poor retrieval leads to poor responses.

**Context Window Limits**: Limited by model's context window; may not include all relevant information.

**Latency**: Two-stage process (retrieval + generation) adds latency compared to direct generation.

**Complexity**: More complex architecture requiring multiple components (vector DB, embeddings, retrieval logic).

**Chunking Challenges**: Breaking documents into chunks can lose context or split related information.

**Redundancy**: May retrieve duplicate or overlapping information.

**Dependency on Embeddings**: Quality of embeddings significantly affects retrieval performance.

**Cold Start**: Requires initial document ingestion and indexing before use.

## Best Practices

- Use high-quality embedding models
- Optimize chunking strategies
- Implement reranking for better retrieval
- Monitor retrieval quality metrics
- Balance chunk size and overlap
- Use metadata filtering when possible
"""
    },
    {
        "filename": "fine_tuning_vs_rag.md",
        "text": """
# Fine-Tuning vs RAG for Adapting LLMs

Both fine-tuning and RAG adapt LLMs to specific domains, but they serve different use cases and have distinct tradeoffs.

## Fine-Tuning

**Process**: Retrain model parameters on domain-specific data to learn new patterns and knowledge.

**Advantages**:
- Learns domain-specific language and patterns
- Can improve performance on specific tasks
- Model internalizes knowledge
- No retrieval overhead at inference time

**Disadvantages**:
- Expensive and time-consuming
- Requires large labeled datasets
- Risk of catastrophic forgetting
- Hard to update with new information
- Requires significant compute resources

**Best For**: Tasks requiring domain-specific language patterns, consistent style, or specialized reasoning.

## RAG (Retrieval-Augmented Generation)

**Process**: Retrieves relevant context from external knowledge base and augments prompts.

**Advantages**:
- Easy to update knowledge (just add documents)
- No model retraining required
- Provides citations and sources
- Can handle diverse knowledge domains
- Lower cost and faster to implement

**Disadvantages**:
- Depends on retrieval quality
- Adds latency (retrieval + generation)
- Limited by context window size
- May not learn domain-specific patterns
- Requires maintaining knowledge base

**Best For**: Applications needing up-to-date information, multiple knowledge domains, or where citations are important.

## When to Use Each

**Use Fine-Tuning When**:
- Need domain-specific language patterns
- Have large labeled datasets
- Want consistent style/format
- Task requires specialized reasoning
- Can afford training costs

**Use RAG When**:
- Need frequently updated information
- Want citations and transparency
- Have diverse knowledge domains
- Limited labeled data available
- Need faster implementation

## Hybrid Approach

Many systems combine both: fine-tune for domain adaptation and use RAG for dynamic knowledge retrieval.
"""
    },
    {
        "filename": "embedding_models_computation.md",
        "text": """
# Computational Requirements of Embedding Models

Different embedding models have varying computational requirements, affecting choice based on available resources and use case.

## Model Size Categories

**Small Models** (e.g., all-MiniLM-L6-v2):
- Parameters: ~22M
- Embedding Dimension: 384
- Memory: ~90MB
- Speed: Very fast (thousands of sentences/second on GPU)
- Use Case: General-purpose, high-throughput applications

**Medium Models** (e.g., all-mpnet-base-v2):
- Parameters: ~110M
- Embedding Dimension: 768
- Memory: ~440MB
- Speed: Moderate (hundreds of sentences/second)
- Use Case: Higher quality when speed allows

**Large Models** (e.g., OpenAI text-embedding-ada-002):
- Parameters: Unknown (API-based)
- Embedding Dimension: 1536
- Memory: N/A (cloud-based)
- Speed: API-dependent
- Use Case: Highest quality, when API costs acceptable

## Computational Factors

**Inference Speed**: Affected by model size, hardware (CPU vs GPU), batch size, and sequence length.

**Memory Requirements**: 
- Model weights: ~4 bytes per parameter (FP32) or ~2 bytes (FP16)
- Activations: Depends on batch size and sequence length
- GPU memory: Critical for large models

**Training Requirements**: 
- Much higher than inference
- Requires GPUs, often multiple
- Can take days/weeks for large models

## Hardware Considerations

**CPU**: Sufficient for small models, slower for larger ones.

**GPU**: Dramatically faster (10-100x), essential for large models and high throughput.

**TPU**: Specialized for ML workloads, fastest but less common.

## Optimization Strategies

- Use quantization (FP16/BF16) to reduce memory
- Batch processing for efficiency
- Model distillation for smaller models
- Caching embeddings for repeated queries
- Use appropriate model size for task requirements
"""
    }
]


async def add_documents():
    """Add all sample documents to the vector database."""
    vector_db = VectorDatabase()
    
    print("Adding sample documents to vector database...")
    print(f"Collection: {vector_db.collection_name}")
    print("-" * 60)
    
    success_count = 0
    for doc in DOCUMENTS:
        try:
            success = await vector_db.add_document_direct(
                text=doc["text"].strip(),
                filename=doc["filename"],
                metadata={
                    "file_type": "markdown",
                    "source": "sample_educational_content",
                    "category": "educational",
                    "upload_method": "script"
                }
            )
            if success:
                success_count += 1
                print(f"✓ Added: {doc['filename']}")
            else:
                print(f"✗ Failed: {doc['filename']}")
        except Exception as e:
            print(f"✗ Error adding {doc['filename']}: {e}")
    
    print("-" * 60)
    print(f"Successfully added {success_count}/{len(DOCUMENTS)} documents")
    
    # Check final count
    count = vector_db.collection.count()
    print(f"Total documents in database: {count}")


if __name__ == "__main__":
    asyncio.run(add_documents())

