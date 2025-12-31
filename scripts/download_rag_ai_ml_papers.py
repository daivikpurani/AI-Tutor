#!/usr/bin/env python3
"""
Script to download RAG (Retrieval-Augmented Generation), AI, and ML papers
from arXiv and other sources to populate the vector database.

This script downloads foundational and recent papers in:
- Retrieval-Augmented Generation (RAG)
- Artificial Intelligence (AI)
- Machine Learning (ML)

Papers are saved to course_materials/papers/ directory.
"""

import os
import sys
import requests
import time
from pathlib import Path
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend_python to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend_python'))

# Curated list of RAG, AI, and ML papers
# Format: (arxiv_id, title, category)
PAPERS_TO_DOWNLOAD = [
    # RAG (Retrieval-Augmented Generation) Papers
    ("2005.11401", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "RAG"),
    ("2305.15217", "In-Context Retrieval-Augmented Language Models", "RAG"),
    ("2402.03300", "RAG vs Fine-tuning: Pipelines, Tradeoffs, and a Case Study on Agriculture", "RAG"),
    ("2403.10131", "RAG-Fusion: A New Take on Retrieval-Augmented Generation", "RAG"),
    ("2404.10904", "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", "RAG"),
    ("2405.18446", "Corrective Retrieval Augmented Generation", "RAG"),
    ("2407.07445", "RAG 2.0: A Unified Framework for Retrieval-Augmented Generation", "RAG"),
    ("2410.15944", "Developing Retrieval Augmented Generation (RAG) based LLM Systems from PDFs", "RAG"),
    
    # Foundational AI/ML Papers
    ("1706.03762", "Attention Is All You Need (Transformer)", "AI/ML"),
    ("1810.04805", "BERT: Pre-training of Deep Bidirectional Transformers", "AI/ML"),
    ("2005.14165", "Language Models are Few-Shot Learners (GPT-3)", "AI/ML"),
    ("2303.08774", "GPT-4 Technical Report", "AI/ML"),
    ("1703.03130", "Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks", "AI/ML"),
    ("1409.3215", "Sequence to Sequence Learning with Neural Networks", "AI/ML"),
    ("1506.01497", "Faster R-CNN: Towards Real-Time Object Detection", "AI/ML"),
    ("1512.03385", "Deep Residual Learning for Image Recognition (ResNet)", "AI/ML"),
    ("1609.02907", "Semi-Supervised Classification with Graph Convolutional Networks", "AI/ML"),
    ("1711.01558", "Neural Architecture Search with Reinforcement Learning", "AI/ML"),
    
    # Modern ML/AI Papers
    ("2010.11929", "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (ViT)", "AI/ML"),
    ("2103.00020", "Learning Transferable Visual Models From Natural Language Supervision (CLIP)", "AI/ML"),
    ("2203.02155", "PaLM: Scaling Language Modeling with Pathways", "AI/ML"),
    ("2204.02311", "PaLM: Scaling Language Modeling with Pathways (Extended)", "AI/ML"),
    ("2302.05442", "LLaMA: Open and Efficient Foundation Language Models", "AI/ML"),
    ("2307.09288", "Llama 2: Open Foundation and Fine-Tuned Chat Models", "AI/ML"),
    ("2305.18290", "Voyager: An Open-Ended Embodied Agent with Large Language Models", "AI/ML"),
    
    # Vector Databases and Embeddings
    ("1803.11175", "Universal Sentence Encoder", "AI/ML"),
    ("1908.10084", "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", "AI/ML"),
    ("2208.03299", "Text Embeddings by Weakly-Supervised Contrastive Pre-training", "AI/ML"),
    
    # Evaluation and Benchmarking
    ("2005.14165", "Language Models are Few-Shot Learners", "AI/ML"),
    ("2306.05685", "A Survey on Evaluation of Large Language Models", "AI/ML"),
    ("2402.03300", "RAG vs Fine-tuning: Pipelines, Tradeoffs, and a Case Study", "RAG"),
]

def download_arxiv_paper(arxiv_id: str, output_dir: Path) -> bool:
    """
    Download a paper from arXiv.
    
    Args:
        arxiv_id: arXiv ID (e.g., "2005.11401")
        output_dir: Directory to save the paper
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Construct arXiv PDF URL
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        # Download the PDF
        logger.info(f"Downloading {arxiv_id}...")
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        # Save to file
        output_file = output_dir / f"{arxiv_id}.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✓ Downloaded {arxiv_id} -> {output_file.name}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Failed to download {arxiv_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error downloading {arxiv_id}: {e}")
        return False

def download_from_url(url: str, output_dir: Path, filename: str = None) -> bool:
    """
    Download a paper from a direct URL.
    
    Args:
        url: Direct URL to the PDF
        output_dir: Directory to save the paper
        filename: Optional filename (defaults to URL basename)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading from {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if filename is None:
            filename = os.path.basename(urlparse(url).path)
            if not filename.endswith('.pdf'):
                filename = f"paper_{hash(url)}.pdf"
        
        output_file = output_dir / filename
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✓ Downloaded -> {output_file.name}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to download from {url}: {e}")
        return False

def main():
    """Main function to download all papers."""
    # Get project root
    project_root = Path(__file__).parent.parent
    papers_dir = project_root / "course_materials" / "papers"
    
    # Create papers directory if it doesn't exist
    papers_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading papers to: {papers_dir}")
    logger.info(f"Total papers to download: {len(PAPERS_TO_DOWNLOAD)}")
    logger.info("-" * 60)
    
    # Organize by category
    papers_by_category = {}
    for arxiv_id, title, category in PAPERS_TO_DOWNLOAD:
        if category not in papers_by_category:
            papers_by_category[category] = []
        papers_by_category[category].append((arxiv_id, title))
    
    # Create category subdirectories
    for category in papers_by_category.keys():
        (papers_dir / category.lower().replace('/', '_')).mkdir(exist_ok=True)
    
    # Download papers
    success_count = 0
    fail_count = 0
    
    for arxiv_id, title, category in PAPERS_TO_DOWNLOAD:
        category_dir = papers_dir / category.lower().replace('/', '_')
        
        # Check if file already exists
        existing_file = category_dir / f"{arxiv_id}.pdf"
        if existing_file.exists():
            logger.info(f"⊘ Skipping {arxiv_id} (already exists)")
            success_count += 1
            continue
        
        # Download paper
        if download_arxiv_paper(arxiv_id, category_dir):
            success_count += 1
        else:
            fail_count += 1
        
        # Be polite to arXiv servers
        time.sleep(1)
    
    logger.info("-" * 60)
    logger.info(f"Summary:")
    logger.info(f"  Successfully downloaded: {success_count}/{len(PAPERS_TO_DOWNLOAD)}")
    logger.info(f"  Failed: {fail_count}")
    logger.info(f"\nPapers saved to: {papers_dir}")
    logger.info("\nNext steps:")
    logger.info("1. Review downloaded papers")
    logger.info("2. Run: python scripts/load_course_materials.py")
    logger.info("3. Test queries to ensure proper domain filtering")

if __name__ == "__main__":
    main()

