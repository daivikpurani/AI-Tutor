"""
Prompt Templates for AI Tutor
Contains various prompt templates for different types of educational interactions.
"""

from typing import List, Dict, Any

class PromptTemplates:
    """
    Collection of prompt templates for the AI tutor system.
    """
    
    SYSTEM_PROMPT = """You are an intelligent AI tutor designed to help students learn effectively. Your role is to:

1. Provide clear, accurate explanations of educational concepts
2. Use the provided context from uploaded course materials when available
3. Adapt your teaching style to the student's level
4. Encourage learning and provide helpful guidance
5. Be patient, supportive, and encouraging
6. Ask clarifying questions when needed
7. Provide examples and analogies to aid understanding

Guidelines:
- Always base your responses on the provided context when available
- If context is insufficient, clearly state this and provide general guidance
- Use a conversational, friendly tone
- Break down complex concepts into simpler parts
- Provide practical examples when possible
- Encourage further questions and exploration
- Maintain academic accuracy while being accessible

Remember: Your goal is to help the student learn and understand, not just provide answers."""
    
    def create_tutor_prompt(
        self, 
        query: str, 
        context: str = "", 
        conversation_history: str = ""
    ) -> str:
        """
        Create a comprehensive prompt for the AI tutor.
        
        Args:
            query: The student's question
            context: Relevant context from course materials
            conversation_history: Previous conversation context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add conversation history if available
        if conversation_history and conversation_history != "No previous conversation.":
            prompt_parts.append(f"Previous conversation:\n{conversation_history}\n")
        
        # Add context if available
        if context and context != "No relevant context found in the uploaded documents.":
            prompt_parts.append(f"Relevant course material:\n{context}\n")
        
        # Add the current question
        prompt_parts.append(f"Student's question: {query}")
        
        # Add instruction
        prompt_parts.append("\nPlease provide a helpful, educational response that addresses the student's question. Use the provided context when relevant, and explain concepts clearly.")
        
        return "\n".join(prompt_parts)
    
    def create_explanation_prompt(self, topic: str, context: str = "") -> str:
        """
        Create a prompt for explaining a specific topic.
        
        Args:
            topic: The topic to explain
            context: Relevant context from materials
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Please explain the concept of '{topic}' in a clear, educational way."
        
        if context:
            prompt += f"\n\nUse this context from the course materials:\n{context}"
        
        prompt += "\n\nStructure your explanation to be:\n- Clear and easy to understand\n- Include practical examples if possible\n- Break down complex ideas into simpler parts\n- Encourage further questions"
        
        return prompt
    
    def create_summary_prompt(self, content: str, topic: str = "") -> str:
        """
        Create a prompt for summarizing content.
        
        Args:
            content: Content to summarize
            topic: Optional topic focus
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Please provide a clear summary of the following content"
        
        if topic:
            prompt += f" focusing on '{topic}'"
        
        prompt += f":\n\n{content}\n\nMake the summary:\n- Concise but comprehensive\n- Easy to understand\n- Highlight key points\n- Include important details"
        
        return prompt
    
    def create_question_prompt(self, topic: str, difficulty: str = "intermediate") -> str:
        """
        Create a prompt for generating practice questions.
        
        Args:
            topic: The topic for questions
            difficulty: Difficulty level (beginner, intermediate, advanced)
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate 3-5 practice questions about '{topic}' at a {difficulty} level.

For each question:
- Make it clear and specific
- Include the answer with explanation
- Vary the question types (multiple choice, short answer, problem-solving)
- Ensure questions test understanding, not just memorization

Format each question as:
Q: [Question]
A: [Answer with explanation]"""
    
    def create_analogy_prompt(self, concept: str, context: str = "") -> str:
        """
        Create a prompt for generating analogies.
        
        Args:
            concept: The concept to explain with analogies
            context: Relevant context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Please explain '{concept}' using analogies and comparisons to everyday concepts."
        
        if context:
            prompt += f"\n\nUse this context:\n{context}"
        
        prompt += "\n\nProvide:\n- 2-3 different analogies\n- Explain how each analogy relates to the concept\n- Highlight similarities and differences\n- Make it relatable and memorable"
        
        return prompt
    
    def create_study_guide_prompt(self, topics: List[str], context: str = "") -> str:
        """
        Create a prompt for generating study guides.
        
        Args:
            topics: List of topics to include
            context: Relevant context from materials
            
        Returns:
            Formatted prompt string
        """
        topics_str = ", ".join(topics)
        prompt = f"Create a comprehensive study guide covering these topics: {topics_str}"
        
        if context:
            prompt += f"\n\nUse this context from course materials:\n{context}"
        
        prompt += "\n\nStructure the study guide with:\n- Key concepts for each topic\n- Important definitions\n- Key relationships between concepts\n- Practice questions\n- Common misconceptions to avoid\n- Study tips and strategies"
        
        return prompt
    
    def create_clarification_prompt(self, unclear_response: str, original_question: str) -> str:
        """
        Create a prompt for clarifying unclear responses.
        
        Args:
            unclear_response: The response that needs clarification
            original_question: The original question
            
        Returns:
            Formatted prompt string
        """
        return f"""The student asked: "{original_question}"

I provided this response: "{unclear_response}"

Please provide a clearer, more helpful response that:
- Directly addresses the student's question
- Uses simpler language if needed
- Provides step-by-step explanations
- Includes examples or analogies
- Encourages further questions if needed"""
    
    def create_encouragement_prompt(self, student_progress: str) -> str:
        """
        Create a prompt for encouraging the student.
        
        Args:
            student_progress: Description of student's progress
            
        Returns:
            Formatted prompt string
        """
        return f"""The student has shown this progress: {student_progress}

Please provide encouraging feedback that:
- Acknowledges their effort and improvement
- Highlights specific strengths
- Suggests next steps for continued learning
- Maintains a positive, supportive tone
- Motivates them to keep learning"""
    
    def create_difficulty_adjustment_prompt(self, question: str, current_level: str, target_level: str) -> str:
        """
        Create a prompt for adjusting question difficulty.
        
        Args:
            question: The original question
            current_level: Current difficulty level
            target_level: Target difficulty level
            
        Returns:
            Formatted prompt string
        """
        return f"""The student asked: "{question}"

Current difficulty level: {current_level}
Target difficulty level: {target_level}

Please adjust your response to be appropriate for the {target_level} level by:
- Using appropriate vocabulary and complexity
- Providing the right amount of detail
- Including suitable examples
- Asking appropriate follow-up questions
- Maintaining educational value while matching the student's level"""
