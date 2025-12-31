# Benchmark Questions Summary

## Overview

Total Questions: **78 questions** (97 lines including comments)

## Question Breakdown

### 1. Original RAG/AI/ML Questions (17 questions)

#### Simple Factual Queries (6)
- What is RAG?
- Explain vector databases in 2 sentences.
- How do embeddings work for document search?
- What is a transformer model?
- Define attention mechanism in one sentence.

#### Complex Analytical Queries (5)
- Compare OpenAI and local LLM usage tradeoffs.
- Analyze the benefits and drawbacks of RAG architecture.
- Explain how vector databases improve search relevance compared to traditional keyword search.
- What are the key differences between fine-tuning and RAG for adapting LLMs?
- Compare the computational requirements of different embedding models.

#### Domain-Specific Academic Queries (5)
- Explain transformer architecture and its key components.
- What is the attention mechanism and why is it important?
- How does backpropagation work in neural networks?
- Describe the difference between supervised and unsupervised learning.
- What are the main challenges in training large language models?

#### Edge Cases (3)
- ? (very short/ambiguous)
- Explain RAG and vector databases and embeddings and transformers. (multi-part)
- What is the meaning of life? (philosophical/out of scope)

---

### 2. Algorithms/Analysis of Algorithms (30 questions)

#### Answerable Questions (24)
These should be answerable from uploaded course materials:

1. What is the formal definition of an α-approximation algorithm for a minimization problem?
2. In the vertex cover approximation algorithm, what structure is computed before selecting vertices?
3. What inequality relates the size of a maximal matching to the size of an optimal vertex cover?
4. What probability does a random partition place an edge in the cut for the Maximum Cut problem?
5. What approximation ratio does the randomized Maximum Cut algorithm achieve?
6. What probability does a random assignment satisfy a clause in MAXSAT?
7. What three properties must be shown to prove a loop invariant?
8. In insertion sort, which subarray is guaranteed to be sorted at the start of each iteration?
9. What condition on pre(v) and post(v) defines a vertex as "active" in DFS?
10. What four types of edges are identified in depth-first search?
11. According to the Parentheses Theorem, what interval relationship characterizes a back edge?
12. What is the time complexity of checking whether an edge exists using an adjacency matrix?
13. What is the time complexity of listing all outgoing edges of a vertex in an adjacency list?
14. Under what condition are adjacency matrices preferred over adjacency lists?
15. What constraint must flows satisfy at every non-source and non-sink vertex?
16. How is the value of a flow defined in a flow network?
17. What is an augmenting path in the context of the Ford–Fulkerson algorithm?
18. What determines the bottleneck value when augmenting a flow?
19. What are the three defining properties of a metric used in Metric TSP?
20. Why do "shortcuts" not increase the cost of a tour in Metric TSP?
21. What data structure replaces recursive calls in dynamic programming for Fibonacci numbers?
22. What is the time complexity of the dynamic programming Fibonacci algorithm shown?
23. What are the three components listed for designing a backtracking algorithm?
24. What algorithm design technique fills a table iteratively instead of using recursion?

#### Intentionally Unanswerable Questions (6)
These should receive "I don't know." responses:

1. What is the approximation ratio of Christofides' algorithm for Metric TSP?
2. What is the amortized time complexity of the Edmonds–Karp algorithm?
3. What is the worst-case time complexity of DFS using adjacency maps?
4. What specific textbook theorem proves NP-completeness of Vertex Cover?
5. What optimization heuristic is recommended for choosing augmenting paths?
6. What is the expected runtime of Ford–Fulkerson with irrational capacities?

---

### 3. Data Visualization (CSC 805) (31 questions)

#### Answerable Questions (25)
These should be answerable from uploaded course materials:

1. How is perception defined in the context of perception and cognition?
2. How is cognition defined in the course materials?
3. What are the three main aims of visual representations listed in the slides?
4. Which of the aims of visual representation is stated to be specific to visualization and not other representations?
5. What are two advantages of visual representations mentioned related to understanding data features?
6. What are the four main stages listed in the visualization process?
7. What is meant by preattentive processing in visualization?
8. According to the slides, what are visual variables used for in visualization design?
9. What are the seven key challenges with visualizing data listed in Chapter 3?
10. In the context of empowerment, what is the primary reason cited for why people buy visual analytics software?
11. What is confirmatory visualization used for?
12. What is exploratory visualization used for?
13. According to the slides, why is "the question at hand" considered critical in visualization design?
14. What are the seven representation methods for data types proposed by Shneiderman?
15. What distinguishes one-dimensional data from two-dimensional data in visualization?
16. What type of data is characterized by start and finish times?
17. What is an example use case mentioned for temporal data?
18. What is the primary goal when dealing with large amounts of data, according to the slides?
19. What are the five main stages shown in the information extraction pipeline diagram?
20. What additional stages are added in the interactive information visualization pipeline compared to information extraction?
21. What is the defining characteristic of tree (hierarchical) data?
22. In graph visualization, what do nodes represent?
23. In graph visualization, what do edges represent?
24. What is one key difference between graph drawing and graph visualization mentioned in the slides?

#### Intentionally Unanswerable Questions (6)
These should receive "I don't know." responses:

1. What is the recommended color map for visualizing high-dimensional biomedical data?
2. What quantitative metric is used to evaluate visualization effectiveness in this course?
3. What algorithm is proposed for automatically optimizing node placement in large graphs?
4. What is the maximum number of nodes recommended for interactive graph visualization?
5. What specific user study results are cited to validate the visualization pipeline?
6. What programming library is mandated for implementing visualizations in this course?

---

## Expected Results

### Answerable Questions (49 total)
- Should receive detailed answers with citations from course materials
- Should demonstrate proper RAG retrieval and response generation
- Should include source citations: `[source: filename | section]`

### Unanswerable Questions (12 total)
- Should return: **"I don't know."**
- Should NOT include background information
- Should NOT speculate or fabricate answers

### Edge Cases (3)
- Test system's handling of ambiguous, multi-part, or out-of-scope questions

## Metrics to Evaluate

For each question-model combination:

1. **Answer Quality**
   - Correctness: Does answerable question get proper answer?
   - Honesty: Does unanswerable question return "I don't know."?
   - Citations: Are sources properly cited?

2. **Performance**
   - Latency: Response time
   - Token usage: Efficiency
   - Cost: API costs (if applicable)

3. **Retrieval Quality**
   - Context relevance: Are correct chunks retrieved?
   - Similarity scores: How well do chunks match query?

4. **System Behavior**
   - Consistency: Same question → similar answer
   - Error handling: Graceful failures
   - Mode differences: Exploration vs Assessment

## Running the Benchmark

See [BENCHMARK_RUN_INSTRUCTIONS.md](./BENCHMARK_RUN_INSTRUCTIONS.md) for detailed instructions.

Quick start:
```bash
cd /Users/daivikpurani/Desktop/ACAD/Thesis/code/FinalProject
source venv/bin/activate
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --models all \
  --mode exploration
```

## Output Location

Results saved to: `backend_python/logs/benchmarks/`
- JSON: Detailed results with all metrics
- CSV: Spreadsheet-friendly format for analysis
