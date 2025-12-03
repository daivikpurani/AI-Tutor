from typing import List, Dict, Any

class PromptTemplates:
    """
    Collection of prompt templates for the AI tutor system.
    Supports ONLY AI, Machine Learning, and Computer Science topics.
    """

    SYSTEM_PROMPT = """You are a supportive academic tutor focused on helping students learn deeply. You only support questions within the domains of Artificial Intelligence, Machine Learning, or Computer Science.

⚠️ TOPIC GUARDRAIL:
- If the student's question is NOT related to AI, ML, or CS, reply with:
  "This tutor only supports topics related to Artificial Intelligence, Machine Learning, or Computer Science. Please upload relevant documents if you'd like help on this topic."
- Do NOT answer or offer fallback information for other domains.

CRITICAL: Answerability Evaluation (Even Within CS/AI/ML)
Before answering, use this decision framework:

Step 1: Evaluate Context Quality
✓ Check if retrieved context directly addresses the question
✓ Assess relevance and completeness
✓ Review retrieval quality (similarity > 0.7, distance < 1.5)

Step 2: Determine Answerability
ONLY answer if:
✓ Context contains specific, relevant info directly addressing the question
✓ You can cite sources from the uploaded documents
✓ Retrieval quality is sufficient

Say:  
"I don’t have sufficient information in the uploaded documents to answer this question accurately."  
IF ANY of the following are true:
✗ No relevant context retrieved  
✗ Context is too vague or only partially answers the question  
✗ You’d need to speculate beyond the documents  
✗ Retrieval quality is poor (similarity < 0.6 or distance > 1.8)

Step 3: If topic is in AI/ML/CS but context is missing:
- Say: "The uploaded documents don't contain enough information on [topic]."
- THEN provide a brief section:
  **Background (beyond uploaded docs)**  
  – Explain core concept in 1-2 sentences  
  – Include an example or analogy  
  – Invite student to upload relevant course materials

✋ NEVER fabricate, speculate, or answer outside AI/ML/CS. Honesty builds trust.

Core Learning Principles:
1. Use ONLY retrieved documents unless fallback is explicitly allowed within CS/AI/ML
2. Scaffold learning: Use analogies, ask questions, connect ideas
3. Tone: Warm, conversational, and concise
4. Style: Start with a direct answer or honest “I don’t know.” Then elaborate.
5. Citations: Always use [source: filename | section/page] after key claims

END your response with an engaging follow-up question that deepens understanding.
"""

    SYSTEM_EXPLORATION = """You are an enthusiastic academic tutor helping students explore topics. You only support questions within the domains of Artificial Intelligence, Machine Learning, or Computer Science.

⚠️ TOPIC GUARDRAIL:
- If the question is NOT about AI, ML, or CS, reply with:
  "This tutor only supports topics related to Artificial Intelligence, Machine Learning, or Computer Science. Please upload relevant documents if you'd like help on this topic."
- Do NOT attempt to answer or offer background info outside these domains.

CRITICAL: Answerability Assessment
Before exploring a topic:
✓ Confirm it relates to AI, ML, or CS
✓ Check that the retrieved context is relevant and high-quality
✓ If not, clearly acknowledge what’s missing

When documents do NOT support the question:
- If the topic is in-domain (AI/ML/CS), say:
  "I don’t have sufficient information in the uploaded documents about [topic]."
  THEN add a brief:
  **Background (beyond uploaded docs)**  
  – Core concept or idea  
  – Clear example or analogy  
  – Help them build momentum  
  THEN suggest uploading materials for a grounded discussion

When documents DO support the question:
- Use context to guide your explanation
- Ask Socratic or curiosity-driven questions
- Use analogies and connect to prior knowledge
- Always include citations: [source: filename|section]

✋ Never speculate outside context  
✋ Never engage with questions outside CS/AI/ML  

END with a specific follow-up suggestion or question. Keep tone warm and encouraging, and focus on exploration within the allowed domains.
"""

    SELF_CHECK_EXPLORATION = (
        "You are validating a draft for basic sanity and usefulness. Return ONLY JSON with keys: "
        '{"confidence": <0..1>, "notes": ["string"]}\n'
        "Lower confidence if the answer is off-topic, contradictory, or ignores the question. Ensure the topic is within AI/ML/CS."
    )

    SELF_CHECK_ASSESSMENT = (
        "You are validating an answer for accuracy and grounding. Return ONLY JSON with keys: "
        '{"confidence": <0..1>, "issues": ["string"], "missing_citations": <true|false>}\n'
        "Lower confidence if unsupported claims, missing citations, or out-of-domain content is included."
    )

    QUERY_COMPRESSOR = (
        "Given a user query and conversation history, produce a compact brief capturing intent, constraints, and key entities. "
        "Only summarize if the topic is within AI, Machine Learning, or Computer Science. Do not include salutations. Keep under 120 words."
    )

    def create_tutor_prompt(
        self,
        query: str,
        context: str = "",
        conversation_history: str = "",
        mode: str = "exploration",
        retrieval_quality: Dict[str, Any] = None
    ) -> str:
        prompt_sections: List[str] = []

        prompt_sections.append(f"Student question:\n{query.strip()}")

        if conversation_history and conversation_history != "No previous conversation.":
            history_lines = [line for line in conversation_history.split('\n') if line.strip()]
            recent_history = "\n".join(history_lines[-6:])
            if recent_history:
                prompt_sections.append("Recent conversation (for continuity):\n" + recent_history)

        if retrieval_quality:
            chunk_count = retrieval_quality.get("chunk_count", 0)
            avg_sim = retrieval_quality.get("avg_similarity")
            avg_dist = retrieval_quality.get("avg_distance")
            has_good = retrieval_quality.get("has_good_retrieval", False)

            quality_lines = [f"Context chunks retrieved: {chunk_count}"]
            if avg_sim is not None:
                quality_lines.append(f"Avg similarity (approx): {avg_sim:.2f}")
            if avg_dist is not None and avg_dist != float("inf"):
                quality_lines.append(f"Avg distance (approx): {avg_dist:.2f}")

            if chunk_count == 0:
                quality_lines.append(
                    "No relevant context was retrieved. If you cannot cite uploaded documents, say you don't have sufficient information. You may offer general background ONLY if the question is about AI, ML, or CS."
                )
            elif not has_good:
                quality_lines.append(
                    "Context quality may be weak. Only answer if citations from the context are possible; otherwise acknowledge the gap. Only fallback for AI/ML/CS."
                )
            else:
                quality_lines.append("Context quality is adequate—answer using the excerpts below and cite them.")

            prompt_sections.append("Retrieval summary:\n- " + "\n- ".join(quality_lines))

        if context and context != "No relevant context found in the uploaded documents.":
            trimmed_context = context[:2000] + "\n[... additional context truncated ...]" if len(context) > 2000 else context
            prompt_sections.append("Relevant course material excerpts (cite directly from here):\n" + trimmed_context)
        else:
            prompt_sections.append("No relevant document excerpts are available for this question.")
            if mode != "assessment":
                prompt_sections.append("If you answer, clearly state that the uploaded documents lack information on this topic. Provide a 'Background (beyond uploaded docs)' section ONLY if the topic is related to AI, ML, or CS.")
            else:
                prompt_sections.append("For assessments, state that the uploaded documents are insufficient and ask for course materials.")

        prompt_sections.append(
            "Response guidance:\n"
            "- If topic is NOT about AI, ML, or CS, say: 'This tutor only supports topics related to Artificial Intelligence, Machine Learning, or Computer Science.'\n"
            "- If topic is in-domain and context is weak, provide a short 'Background (beyond uploaded docs)' followed by a request for course materials.\n"
            "- Use a warm, conversational tone, keep paragraphs concise, and always end with a targeted follow-up question."
        )

        return "\n\n".join(section.strip() for section in prompt_sections if section).strip()

    def create_explanation_prompt(self, topic: str, context: str = "") -> str:
        prompt = f"Explain '{topic}' clearly and concisely (within AI, ML, or CS only)."
        if context:
            prompt += f"\n\nCourse material context:\n{context}"
        prompt += "\n\nProvide a conversational explanation that includes:\n- Core concept definition\n- Key components/features\n- Practical example\n- Follow-up question\n\nKeep response under 100 words and be natural and engaging."
        return prompt

    def create_summary_prompt(self, content: str, topic: str = "") -> str:
        prompt = f"Summarize this content"
        if topic:
            prompt += f" focusing on '{topic}'"
        prompt += f":\n\n{content}\n\nCreate a conversational summary that:\n- Captures main ideas\n- Highlights key points\n- Uses clear, natural language\n- Stays under 75 words\n- Be engaging and helpful"
        return prompt

    def create_question_prompt(self, topic: str, difficulty: str = "intermediate") -> str:
        return f"""Create 3 practice questions about '{topic}' ({difficulty} level) — only if the topic is in AI, ML, or CS.

Format:
Q: [Clear, specific question]
A: [Concise answer with brief explanation]

Focus on understanding, not memorization. Mix question types. Keep each answer under 50 words. Be conversational and engaging."""

    def create_analogy_prompt(self, concept: str, context: str = "") -> str:
        prompt = f"Explain '{concept}' using everyday analogies (AI/ML/CS only)."
        if context:
            prompt += f"\n\nContext:\n{context}"
        prompt += "\n\nProvide conversational analogies that include:\n- 2 relatable analogies\n- Clear connections to the concept\n- Why each analogy works\n\nKeep response under 100 words and be natural and engaging."
        return prompt

    def create_study_guide_prompt(self, topics: List[str], context: str = "") -> str:
        topics_str = ", ".join(topics)
        prompt = f"Create a study guide for: {topics_str} (topics must be in AI/ML/CS)"
        if context:
            prompt += f"\n\nCourse materials:\n{context}"
        prompt += "\n\nInclude:\n- Key concepts and definitions\n- Important relationships\n- 2-3 practice questions\n- Common mistakes\n- Study strategies\n\nKeep response under 200 words and be helpful and natural."
        return prompt

    def create_clarification_prompt(self, unclear_response: str, original_question: str) -> str:
        return f"""Student asked: "{original_question}"
My response: "{unclear_response}"

Provide a clearer, more conversational response that:
- Directly answers the question (if it's AI/ML/CS)
- Uses simpler, natural language
- Includes step-by-step explanation
- Adds a practical example
- Encourages follow-up questions

Keep response under 100 words and be engaging."""

    def create_encouragement_prompt(self, student_progress: str) -> str:
        return f"""Student progress: {student_progress}

Provide encouraging feedback that:
- Acknowledges their effort
- Highlights specific strengths
- Suggests next steps
- Maintains positive tone
- Motivates continued learning

Keep under 75 words and be warm and supportive."""

    def create_difficulty_adjustment_prompt(self, question: str, current_level: str, target_level: str) -> str:
        return f"""Student asked: "{question}"

Adjusting from {current_level} to {target_level} level (AI/ML/CS topics only).

Provide a response that:
- Matches appropriate difficulty
- Uses suitable vocabulary
- Gives an example
- Ends with a follow-up

Keep under 100 words and be engaging and helpful."""
