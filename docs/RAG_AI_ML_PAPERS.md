# RAG, AI, and ML Papers Collection

This document describes the curated collection of papers focused on **Retrieval-Augmented Generation (RAG)**, **Artificial Intelligence (AI)**, and **Machine Learning (ML)** that populate the vector database.

## Purpose

The vector database is strictly limited to papers in these three domains:
- **RAG (Retrieval-Augmented Generation)**: Papers on retrieval-augmented language models, RAG systems, and related techniques
- **AI (Artificial Intelligence)**: Foundational and modern AI papers
- **ML (Machine Learning)**: Core machine learning papers, including deep learning, transformers, and neural architectures

## Domain Restrictions

The system is configured to:
- **Answer questions** only when they relate to RAG, AI, or ML
- **Respond with "I don't know"** for questions outside these domains
- **Filter retrieval results** to ensure only relevant content is returned

## Paper Categories

### RAG Papers (Retrieval-Augmented Generation)

1. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (Lewis et al., 2020)
   - ArXiv ID: 2005.11401
   - Foundational RAG paper introducing the concept

2. **In-Context Retrieval-Augmented Language Models** (2023)
   - ArXiv ID: 2305.15217
   - Recent advances in RAG

3. **RAG vs Fine-tuning: Pipelines, Tradeoffs, and a Case Study on Agriculture** (2024)
   - ArXiv ID: 2402.03300
   - Comparative analysis of RAG approaches

4. **RAG-Fusion: A New Take on Retrieval-Augmented Generation** (2024)
   - ArXiv ID: 2403.10131
   - Advanced RAG techniques

5. **Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection** (2024)
   - ArXiv ID: 2404.10904
   - Self-reflective RAG systems

6. **Corrective Retrieval Augmented Generation** (2024)
   - ArXiv ID: 2405.18446
   - Error correction in RAG

7. **RAG 2.0: A Unified Framework for Retrieval-Augmented Generation** (2024)
   - ArXiv ID: 2407.07445
   - Next-generation RAG framework

8. **Developing Retrieval Augmented Generation (RAG) based LLM Systems from PDFs** (2024)
   - ArXiv ID: 2410.15944
   - Practical RAG implementation guide

### Foundational AI/ML Papers

1. **Attention Is All You Need (Transformer)** (Vaswani et al., 2017)
   - ArXiv ID: 1706.03762
   - Introduced the Transformer architecture

2. **BERT: Pre-training of Deep Bidirectional Transformers** (Devlin et al., 2018)
   - ArXiv ID: 1810.04805
   - Bidirectional encoder representations

3. **Language Models are Few-Shot Learners (GPT-3)** (Brown et al., 2020)
   - ArXiv ID: 2005.14165
   - Large-scale language model scaling

4. **GPT-4 Technical Report** (OpenAI, 2023)
   - ArXiv ID: 2303.08774
   - GPT-4 architecture and capabilities

5. **Deep Residual Learning for Image Recognition (ResNet)** (He et al., 2015)
   - ArXiv ID: 1512.03385
   - Residual networks for deep learning

6. **Sequence to Sequence Learning with Neural Networks** (Sutskever et al., 2014)
   - ArXiv ID: 1409.3215
   - Seq2seq architecture

### Modern ML/AI Papers

1. **An Image is Worth 16x16 Words: Transformers for Image Recognition (ViT)** (Dosovitskiy et al., 2020)
   - ArXiv ID: 2010.11929
   - Vision transformers

2. **Learning Transferable Visual Models From Natural Language Supervision (CLIP)** (Radford et al., 2021)
   - ArXiv ID: 2103.00020
   - Vision-language models

3. **PaLM: Scaling Language Modeling with Pathways** (Chowdhery et al., 2022)
   - ArXiv ID: 2203.02155
   - Large-scale language models

4. **LLaMA: Open and Efficient Foundation Language Models** (Touvron et al., 2023)
   - ArXiv ID: 2302.05442
   - Open-source LLMs

5. **Llama 2: Open Foundation and Fine-Tuned Chat Models** (Touvron et al., 2023)
   - ArXiv ID: 2307.09288
   - Llama 2 models

### Vector Databases and Embeddings

1. **Universal Sentence Encoder** (Cer et al., 2018)
   - ArXiv ID: 1803.11175
   - Sentence embeddings

2. **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks** (Reimers & Gurevych, 2019)
   - ArXiv ID: 1908.10084
   - Efficient sentence embeddings

3. **Text Embeddings by Weakly-Supervised Contrastive Pre-training** (2022)
   - ArXiv ID: 2208.03299
   - Contrastive learning for embeddings

## Downloading Papers

To download all papers, run:

```bash
python scripts/download_rag_ai_ml_papers.py
```

This script will:
1. Download papers from arXiv
2. Organize them by category (RAG, AI/ML)
3. Save them to `course_materials/papers/`

## Loading Papers into Vector Database

After downloading papers, load them into the vector database:

```bash
python scripts/load_course_materials.py
```

This will:
1. Process all PDFs in `course_materials/papers/`
2. Chunk the documents
3. Add them to ChromaDB vector store

## Testing Domain Restrictions

To verify that the system correctly handles out-of-domain questions:

1. **In-domain question** (should work):
   - "What is Retrieval-Augmented Generation?"
   - "How do transformers work?"
   - "Explain attention mechanisms"

2. **Out-of-domain question** (should return "I don't know"):
   - "How do I build a REST API?"
   - "What is database normalization?"
   - "Explain TCP/IP networking"

## Maintenance

### Adding New Papers

1. Add the paper to `PAPERS_TO_DOWNLOAD` in `scripts/download_rag_ai_ml_papers.py`
2. Format: `("arxiv_id", "Title", "Category")`
3. Run the download script
4. Reload into vector database

### Updating Domain Restrictions

Domain restrictions are enforced in:
- `backend_python/utils/prompts.py` - System prompts
- `backend_python/services/query_handler.py` - Query processing logic

## Notes

- Papers are organized by category in subdirectories
- The system uses similarity thresholds to filter low-relevance results
- Out-of-domain questions trigger "I don't know" responses even if some context is retrieved
- All prompts explicitly restrict responses to RAG, AI, and ML domains

