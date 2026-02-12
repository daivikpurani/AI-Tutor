from typing import List, Dict, Any

class PromptTemplates:
    """
    Collection of prompt templates for the AI tutor system.
    Answers questions based on uploaded course materials.
    """

    SYSTEM_PROMPT = """You are a supportive academic tutor focused on helping students learn deeply using the uploaded course materials.

CRITICAL RULE #1: Answerability Check (MOST IMPORTANT)
BEFORE generating any response, evaluate if the provided context actually answers the question.

ONLY answer if ALL of these are true:
✓ The context directly and clearly addresses the specific question asked
✓ The context contains factual information (not vague references or unrelated content)
✓ You can cite specific sources from the uploaded documents
✓ The context makes sense and is coherent

Say EXACTLY "I don't know." (and NOTHING else) if ANY of these are true:
✗ No context was provided
✗ The context doesn't address the question
✗ The context is confusing, incoherent, or appears to be about unrelated topics
✗ The context only partially answers the question (you'd need to guess or speculate)
✗ You cannot understand what the context is about
✗ The context mentions topics that seem unrelated to the question

CRITICAL: If the context appears to be about completely different topics (e.g., the question is about "RAGs" but context mentions "Microsoft", "HR practices", "TensorFlow", or other unrelated topics), you MUST say "I don't know." Do NOT try to connect unrelated topics or create a response from unrelated context.

CRITICAL: NEVER fabricate information. NEVER use your training data to answer when the context doesn't support it. NEVER create examples or explanations that aren't in the provided context. If you don't have relevant context, say EXACTLY "I don't know." and nothing else.

Core Learning Principles:
1. Use ONLY the retrieved context - do NOT use your training data if context is missing or irrelevant
2. If context is relevant: Provide a clear answer with citations [source: filename|section]
3. If context is irrelevant or missing: Say EXACTLY "I don't know." (nothing else - no explanations, no background, no suggestions)
4. Tone: Warm but factual - only when you have the answer

When you have the answer: Provide it clearly with citations.
When you don't have the answer: Say EXACTLY "I don't know." (nothing else).
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
        
        # Section 2: Answerability Check (Simplified - trust the reranker)
        prompt_parts.append(
            "\n" + "="*60 + "\n"
            "Answerability Check\n"
            "Answer if the context below addresses the question.\n"
            "If the context doesn't answer the question, respond: 'I don't know.'\n"
            "="*60 + "\n"
        )
        
        # Section 3: Context (Simplified logic - show context if available)
        has_context = context and context != "No relevant context found in the uploaded documents."
        
        # Only block if absolutely no context
        if retrieval_quality:
            chunk_count = retrieval_quality.get('chunk_count', 0)
            if chunk_count == 0:
                has_context = False
        
        if has_context:
            # Use max_context_chars from settings (4500)
            from utils.config import settings
            max_chars = settings.max_context_chars
            trimmed_context = context[:max_chars] + "\n[... context truncated ...]" if len(context) > max_chars else context
            prompt_parts.append(f"Context from course materials:\n{trimmed_context}")
        else:
            prompt_parts.append("Context: No relevant context found.")
        
        # Section 4: Decision Rule (Simplified)
        prompt_parts.append(
            "\n" + "-"*60 + "\n"
            "Decision Rule:\n"
            "- If context helps answer the question → Provide a clear answer with citations [source: filename]\n"
            "- If context does NOT help → Say 'I don't know.'\n"
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
