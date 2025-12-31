from typing import List, Dict, Any

class PromptTemplates:
    """
    Collection of prompt templates for the AI tutor system.
    Answers questions based on uploaded course materials.
    """

    SYSTEM_PROMPT = """You are a supportive academic tutor focused on helping students learn deeply using the uploaded course materials.

CRITICAL: Answerability Evaluation
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

Say "I don't know." (and nothing else) IF ANY of the following are true:
✗ No relevant context retrieved  
✗ Context is too vague or only partially answers the question  
✗ You'd need to speculate beyond the documents  
✗ Retrieval quality is poor (similarity < 0.6 or distance > 1.8)
✗ You cannot understand or make sense of the retrieved chunks

NEVER fabricate, speculate, or add background information when you don't know. Simply say "I don't know."

Core Learning Principles:
1. Use ONLY retrieved documents - answer based on what's in the uploaded course materials
2. If you have relevant context, provide a clear, direct answer with citations
3. If you don't have relevant context or can't understand it, say "I don't know." (no background, no elaboration)
4. Tone: Warm, conversational, and concise
5. Citations: Always use [source: filename | section/page] after key claims

When you have the answer: Provide it clearly with citations and end with an engaging follow-up question.
When you don't have the answer: Simply say "I don't know."
"""

    SYSTEM_EXPLORATION = """You are an academic tutor helping students learn using uploaded course materials.

CRITICAL RULE #1: Answerability Check
ONLY answer if the provided context directly and clearly addresses the question. If the context doesn't answer the question, respond with exactly: "I don't know." (nothing else - no background, no speculation, no suggestions).

CRITICAL RULE #2: Response Format
When you have an answer:
- Start with a direct answer to the question (lead with the answer, not background)
- Use simple, clear language - avoid jargon unless necessary
- Break complex concepts into digestible parts
- Include examples when helpful
- Cite sources inline: [source: filename|section]
- Keep concise: 2-3 short paragraphs maximum
- End with a brief key takeaway or follow-up question
- Use a warm, conversational but educational tone

When you don't have an answer:
- Say exactly: "I don't know." (nothing else)

Never speculate, fabricate, or add background information when context doesn't support the answer.
"""

    SYSTEM_ASSESSMENT = """You are an academic tutor helping students with assessments using uploaded course materials.

CRITICAL RULE #1: Answerability Check
ONLY answer if the provided context directly and clearly addresses the question. If the context doesn't answer the question, respond with exactly: "I don't know." (nothing else - no background, no speculation, no suggestions).

CRITICAL RULE #2: Response Format
When you have an answer:
- Start with a direct answer to the question (lead with the answer, not background)
- Use simple, clear language - be precise and factual
- Break complex concepts into digestible parts
- Include examples when helpful
- Cite sources inline: [source: filename|section]
- Keep concise: 1-2 short paragraphs maximum
- End with a brief key takeaway
- Use a clear, educational tone

When you don't have an answer:
- Say exactly: "I don't know." (nothing else)

Never speculate, fabricate, or add background information when context doesn't support the answer. Accuracy and grounding in course materials is critical.
"""

    SELF_CHECK_EXPLORATION = (
        "You are validating a draft for basic sanity and usefulness. Return ONLY JSON with keys: "
        '{"confidence": <0..1>, "notes": ["string"]}\n'
        "Lower confidence if the answer is off-topic, contradictory, or ignores the question."
    )

    SELF_CHECK_ASSESSMENT = (
        "You are validating an answer for accuracy and grounding. Return ONLY JSON with keys: "
        '{"confidence": <0..1>, "issues": ["string"], "missing_citations": <true|false>}\n'
        "Lower confidence if unsupported claims, missing citations, or content not grounded in the provided context."
    )

    QUERY_COMPRESSOR = (
        "Given a user query and conversation history, produce a compact brief capturing intent, constraints, and key entities. "
        "Do not include salutations. Keep under 120 words."
    )

    def create_tutor_prompt(
        self,
        query: str,
        context: str = "",
        conversation_history: str = "",
        mode: str = "exploration",
        retrieval_quality: Dict[str, Any] = None
    ) -> str:
        """
        Create a simplified tutor prompt with clear answerability check.
        
        Structure:
        1. Question
        2. Answerability Check (prominent)
        3. Context (if available)
        4. Decision Rule (simple binary)
        """
        prompt_parts: List[str] = []
        
        # Section 1: Question
        prompt_parts.append(f"Question: {query.strip()}")
        
        # Section 2: Answerability Check (MOST PROMINENT)
        prompt_parts.append(
            "\n" + "="*60 + "\n"
            "CRITICAL: Answerability Check\n"
            "ONLY answer if the context below directly addresses the question above.\n"
            "If the context doesn't answer the question, respond with exactly: 'I don't know.'\n"
            "Do NOT speculate, connect to unrelated topics, or add background information.\n"
            "="*60 + "\n"
        )
        
        # Section 3: Context
        has_context = context and context != "No relevant context found in the uploaded documents."
        
        if has_context:
            # Trim context if too long
            trimmed_context = context[:2000] + "\n[... additional context truncated ...]" if len(context) > 2000 else context
            prompt_parts.append(f"Context from course materials:\n{trimmed_context}")
        else:
            prompt_parts.append("Context: No relevant context found.")
            prompt_parts.append("Decision: Respond with exactly 'I don't know.' (nothing else).")
        
        # Section 4: Decision Rule (Simple Binary)
        prompt_parts.append(
            "\n" + "-"*60 + "\n"
            "Decision Rule:\n"
            "- If context directly answers the question → Provide a clear answer with citations [source: filename|section]\n"
            "- If context does NOT answer the question → Say exactly 'I don't know.' (nothing else)\n"
            "-"*60
        )
        
        return "\n".join(prompt_parts).strip()

    def create_explanation_prompt(self, topic: str, context: str = "") -> str:
        prompt = f"Explain '{topic}' clearly and concisely based on the course materials."
        if context:
            prompt += f"\n\nCourse material context:\n{context}"
        else:
            prompt += "\n\nIf no relevant context is available, say 'I don't know.' (nothing else)."
        prompt += "\n\nIf context is available, provide a conversational explanation that includes:\n- Core concept definition\n- Key components/features\n- Practical example\n- Follow-up question\n\nKeep response under 100 words and be natural and engaging."
        return prompt

    def create_summary_prompt(self, content: str, topic: str = "") -> str:
        prompt = f"Summarize this content"
        if topic:
            prompt += f" focusing on '{topic}'"
        prompt += f":\n\n{content}\n\nCreate a conversational summary that:\n- Captures main ideas\n- Highlights key points\n- Uses clear, natural language\n- Stays under 75 words\n- Be engaging and helpful"
        return prompt

    def create_question_prompt(self, topic: str, difficulty: str = "intermediate") -> str:
        return f"""Create 3 practice questions about '{topic}' ({difficulty} level) based on the course materials.

Format:
Q: [Clear, specific question]
A: [Concise answer with brief explanation]

Focus on understanding, not memorization. Mix question types. Keep each answer under 50 words. Be conversational and engaging."""

    def create_analogy_prompt(self, concept: str, context: str = "") -> str:
        prompt = f"Explain '{concept}' using everyday analogies based on the course materials."
        if context:
            prompt += f"\n\nContext:\n{context}"
        else:
            prompt += "\n\nIf no relevant context is available, say 'I don't know.' (nothing else)."
        prompt += "\n\nIf context is available, provide conversational analogies that include:\n- 2 relatable analogies\n- Clear connections to the concept\n- Why each analogy works\n\nKeep response under 100 words and be natural and engaging."
        return prompt

    def create_study_guide_prompt(self, topics: List[str], context: str = "") -> str:
        topics_str = ", ".join(topics)
        prompt = f"Create a study guide for: {topics_str} based on the course materials"
        if context:
            prompt += f"\n\nCourse materials:\n{context}"
        else:
            prompt += "\n\nIf no relevant context is available, say 'I don't know.' (nothing else)."
        prompt += "\n\nIf context is available, include:\n- Key concepts and definitions\n- Important relationships\n- 2-3 practice questions\n- Common mistakes\n- Study strategies\n\nKeep response under 200 words and be helpful and natural."
        return prompt

    def create_clarification_prompt(self, unclear_response: str, original_question: str) -> str:
        return f"""Student asked: "{original_question}"
My response: "{unclear_response}"

Provide a clearer, more conversational response that:
- Directly answers the question based on course materials
- Uses simpler, natural language
- Includes step-by-step explanation
- Adds a practical example
- Encourages follow-up questions

If you don't have relevant context, say 'I don't know.' (nothing else).

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

Adjusting from {current_level} to {target_level} level based on course materials.

Provide a response that:
- Matches appropriate difficulty
- Uses suitable vocabulary
- Gives an example
- Ends with a follow-up

If you don't have relevant context, say 'I don't know.' (nothing else).

Keep under 100 words and be engaging and helpful."""
