# Test Questions for RAG, AI, and ML Vector Store

This document contains test questions to verify the vector store is working correctly and that domain restrictions are properly enforced.

## In-Domain Questions (Should Get Answers)

These questions are within RAG, AI, and ML domains and should receive detailed answers from the uploaded papers.

### RAG (Retrieval-Augmented Generation) Questions

1. **What is Retrieval-Augmented Generation?**
   - Expected: Should explain RAG concept from the foundational paper (2005.11401)

2. **How does RAG combine retrieval and generation?**
   - Expected: Should explain the architecture and mechanism

3. **What are the advantages of RAG over fine-tuning?**
   - Expected: Should reference comparison papers (2402.03300)

4. **Explain Self-RAG and how it works**
   - Expected: Should explain self-reflection mechanism (2404.10904)

5. **What is RAG-Fusion and how does it differ from standard RAG?**
   - Expected: Should explain fusion techniques (2403.10131)

6. **How do you build a RAG system from PDFs?**
   - Expected: Should reference implementation guide (2410.15944)

7. **What is Corrective RAG?**
   - Expected: Should explain error correction in RAG (2405.18446)

8. **What are the key components of a RAG 2.0 system?**
   - Expected: Should explain unified framework (2407.07445)

### AI/ML Foundational Questions

9. **What is the Transformer architecture?**
   - Expected: Should explain attention mechanism from "Attention Is All You Need" (1706.03762)

10. **How does BERT work?**
    - Expected: Should explain bidirectional encoding (1810.04805)

11. **What is GPT-3 and how does it differ from previous models?**
    - Expected: Should explain few-shot learning (2005.14165)

12. **Explain the attention mechanism in transformers**
    - Expected: Should detail self-attention from transformer paper

13. **What are residual networks (ResNet)?**
    - Expected: Should explain skip connections (1512.03385)

14. **How do Vision Transformers (ViT) work?**
    - Expected: Should explain image transformers (2010.11929)

15. **What is CLIP and how does it work?**
    - Expected: Should explain vision-language model (2103.00020)

16. **Explain how LLaMA models are trained**
    - Expected: Should reference LLaMA papers (2302.05442, 2307.09288)

17. **What is sentence-BERT?**
    - Expected: Should explain sentence embeddings (1908.10084)

18. **How do universal sentence encoders work?**
    - Expected: Should explain embedding models (1803.11175)

### Advanced AI/ML Questions

19. **What is the difference between GPT-3 and GPT-4?**
    - Expected: Should compare capabilities (2005.14165 vs 2303.08774)

20. **How do graph convolutional networks work?**
    - Expected: Should explain GCN architecture (1609.02907)

21. **What is neural architecture search?**
    - Expected: Should explain NAS with RL (1711.01558)

22. **Explain sequence-to-sequence learning**
    - Expected: Should explain seq2seq architecture (1409.3215)

23. **What are the key innovations in PaLM?**
    - Expected: Should explain Pathways scaling (2203.02155)

24. **How do contrastive learning methods work for embeddings?**
    - Expected: Should explain contrastive pre-training (2208.03299)

## Out-of-Domain Questions (Should Return "I don't know")

These questions are outside RAG, AI, and ML domains and should trigger the domain guardrail.

### Computer Science (General) - Should be Rejected

1. **How do I build a REST API?**
   - Expected: "I don't know. This tutor only supports topics related to Retrieval-Augmented Generation (RAG), Artificial Intelligence (AI), and Machine Learning (ML)."

2. **What is database normalization?**
   - Expected: "I don't know..." (out of domain)

3. **Explain TCP/IP networking protocols**
   - Expected: "I don't know..." (out of domain)

4. **How do operating systems handle memory management?**
   - Expected: "I don't know..." (out of domain)

5. **What is the difference between SQL and NoSQL databases?**
   - Expected: "I don't know..." (out of domain)

6. **How do I implement a binary search tree?**
   - Expected: "I don't know..." (out of domain)

7. **Explain the CAP theorem**
   - Expected: "I don't know..." (out of domain)

8. **What are design patterns in software engineering?**
   - Expected: "I don't know..." (out of domain)

### Web Development - Should be Rejected

9. **How do I create a React component?**
   - Expected: "I don't know..." (out of domain)

10. **What is CSS Grid layout?**
    - Expected: "I don't know..." (out of domain)

11. **How do I deploy a website to AWS?**
    - Expected: "I don't know..." (out of domain)

12. **Explain how HTTP/2 works**
    - Expected: "I don't know..." (out of domain)

### Other Domains - Should be Rejected

13. **What is quantum computing?**
    - Expected: "I don't know..." (out of domain - quantum computing is not ML/AI)

14. **How does blockchain work?**
    - Expected: "I don't know..." (out of domain)

15. **Explain the theory of relativity**
    - Expected: "I don't know..." (out of domain - physics)

16. **What is photosynthesis?**
    - Expected: "I don't know..." (out of domain - biology)

17. **How do I cook pasta?**
    - Expected: "I don't know..." (out of domain)

18. **What is the capital of France?**
    - Expected: "I don't know..." (out of domain - geography)

## Edge Cases - Should Handle Gracefully

### In-Domain but No Context Available

1. **What is reinforcement learning?**
   - Expected: If no RL papers are uploaded, should say "I don't have sufficient information in the uploaded documents about reinforcement learning" and optionally provide brief background

2. **Explain convolutional neural networks**
   - Expected: If no CNN-specific papers, should acknowledge lack of context

### Ambiguous Questions

3. **What is attention?**
   - Expected: Should clarify if asking about transformer attention (in-domain) vs psychological attention (out-of-domain)

4. **How do neural networks work?**
   - Expected: Should work if neural network papers are available, otherwise acknowledge gap

## Testing Checklist

- [ ] Test in-domain RAG questions get answers
- [ ] Test in-domain AI/ML questions get answers  
- [ ] Test out-of-domain CS questions return "I don't know"
- [ ] Test out-of-domain web dev questions return "I don't know"
- [ ] Test out-of-domain other topics return "I don't know"
- [ ] Test edge cases handle gracefully
- [ ] Verify citations are included in responses
- [ ] Verify responses cite specific papers when available

## Notes

- All in-domain questions should include citations to source papers
- Out-of-domain questions should clearly state domain restrictions
- The system should not speculate or provide generic answers for out-of-domain topics
- Responses should be grounded in the uploaded documents

