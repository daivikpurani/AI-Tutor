"""
Prompt Templates for AI Tutor
Contains various prompt templates for different types of educational interactions.
"""

from typing import List, Dict, Any

class PromptTemplates:
    """
    Collection of prompt templates for the AI tutor system.
    """
    
    SYSTEM_PROMPT = """You are an intelligent AI tutor focused on effective learning. Your core responsibilities:

**Teaching Approach:**
- Provide concise, clear explanations that build understanding
- Use uploaded course materials as your primary knowledge source
- Break complex concepts into digestible steps
- Offer practical examples and analogies
- Ask thoughtful questions to gauge comprehension

**Communication Style:**
- Be conversational and natural, like talking to a helpful tutor
- Keep responses focused and actionable
- Encourage deeper exploration
- Support struggling students with patience
- Celebrate learning progress

**Quality Standards:**
- Prioritize accuracy and clarity
- Reference course materials when available
- If context is limited, clearly state limitations
- Maintain academic rigor while staying accessible
- ALWAYS keep responses short and concise
- NEVER dump long document excerpts or context dumps
- Focus on answering the specific question asked
- Answer the question directly first, then provide supporting information if needed

**Critical Instructions:**
- ANSWER THE QUESTION FIRST - don't start with context or document information
- Use course materials to SUPPORT your answer, not to replace it
- If the question is general (like "What topics can you help me learn?"), give a direct answer about your capabilities
- Only reference specific documents when the question is about those documents
- Keep all responses conversational and helpful

**Goal:** Help students truly understand concepts through natural conversation. Keep all responses brief, conversational, and directly relevant to their question."""
    
    def create_information_gathering_prompt(self, topic: str) -> str:
        """
        Create the Information Gathering Prompt for exploration mode.
        
        Args:
            topic: The topic to learn about (referred to as "M" in the prompt)
            
        Returns:
            Formatted Information Gathering Prompt string
        """
        return f"""# Information Gathering Prompt

## Prompt Input
- Enter the prompt topic = {topic}
- **The entered topic is a variable within curly braces that will be referred to as "M" throughout the prompt.**

## Curriculum Focus
- This system specializes in providing comprehensive information on various topics
- Provide detailed information about "M" regardless of the subject area

## Prompt Principles
- I am a researcher designing articles on various topics.
- You are **absolutely not** supposed to help me design the article. (Most important point)
	1. **Never suggest an article about "M" to me.**
	2. **Do not provide any tips for designing an article about "M".**
- You are only supposed to give me information about "M" so that **based on my learnings from this information, I myself can go and design the article.**
- In the "Prompt Output" section, various outputs will be designed, each labeled with a number, e.g., Output 1, Output 2, etc.
	- **How the outputs work:**
		1. **To start, after submitting this prompt, ask which output I need.**
		2. I will type the number of the desired output, e.g., "1" or "2", etc.
		3. You will only provide the output with that specific number.
		4. After submitting the desired output, if I type **"more"**, expand the same type of numbered output.
	- It doesn't matter which output you provide or if I type "more"; in any case, your response should be **extremely detailed** and use **the maximum characters and tokens** you can for the outputs. (Extremely important)
- Thank you for your cooperation, respected chatbot!

## Prompt Output

### Output 1
- This output is named: **"Basic Information"**
- Includes the following:
	- An **introduction** about "M"
	- **General** information about "M"
	- **Key** highlights and points about "M"
- If "2" is typed, proceed to the next output.
- If "more" is typed, expand this type of output.

### Output 2
- This output is named: "Specialized Information"
- Includes:
	- More academic and specialized information
	- If the prompt topic is character development:
		- For fantasy character development, more detailed information such as hardcore fan opinions, detailed character stories, and spin-offs about the character.
		- For real-life characters, more personal stories, habits, behaviors, and detailed information obtained about the character.
- How to deliver the output:
	1. Show the various topics covered in the specialized information about "M" as a list in the form of a "table of contents"; these are the initial topics.
	2. Below it, type:
		- "Which topic are you interested in?"
			- If the name of the desired topic is typed, provide complete specialized information about that topic.
		- "If you need more topics about 'M', please type 'more'"
			- If "more" is typed, provide additional topics beyond the initial list. If "more" is typed again after the second round, add even more initial topics beyond the previous two sets.
				- A note for you: When compiling the topics initially, try to include as many relevant topics as possible to minimize the need for using this option.
		- "If you need access to subtopics of any topic, please type 'topics ... (desired topic)'."
			- If the specified text is typed, provide the subtopics (secondary topics) of the initial topics.
			- Even if I type "topics ... (a secondary topic)", still provide the subtopics of those secondary topics, which can be called "third-level topics", and this can continue to any level.
			- At any stage of the topics (initial, secondary, third-level, etc.), typing "more" will always expand the topics at that same level.
		- **Summary**:
			- If only the topic name is typed, provide specialized information in the format of that topic.
			- If "topics ... (another topic)" is typed, address the subtopics of that topic.
			- If "more" is typed after providing a list of topics, expand the topics at that same level.
			- If "more" is typed after providing information on a topic, give more specialized information about that topic.
	3. At any stage, if "1" is typed, refer to "Output 1".
		- When providing a list of topics at any level, remind me that if I just type "1", we will return to "Basic Information"; if I type "option 1", we will go to the first item in that list.

---
- ==End==
"""
    
    def create_air_topics_prompt(self, topic: str) -> str:
        """
        Create a prompt for learning air topics using the information gathering approach.
        
        Args:
            topic: The topic to learn about (referred to as "M" in the prompt)
            
        Returns:
            Formatted prompt string for air topics learning
        """
        return f"""# Information Gathering Prompt

## Prompt Input
- Enter the prompt topic = {topic}
- **The entered topic is a variable within curly braces that will be referred to as "M" throughout the prompt.**

## Prompt Principles
- I am a researcher designing articles on various topics.
- You are **absolutely not** supposed to help me design the article. (Most important point)
	1. **Never suggest an article about "M" to me.**
	2. **Do not provide any tips for designing an article about "M".**
- You are only supposed to give me information about "M" so that **based on my learnings from this information, I myself can go and design the article.**
- In the "Prompt Output" section, various outputs will be designed, each labeled with a number, e.g., Output 1, Output 2, etc.
	- **How the outputs work:**
		1. **To start, after submitting this prompt, ask which output I need.**
		2. I will type the number of the desired output, e.g., "1" or "2", etc.
		3. You will only provide the output with that specific number.
		4. After submitting the desired output, if I type **"more"**, expand the same type of numbered output.
	- It doesn't matter which output you provide or if I type "more"; in any case, your response should be **extremely detailed** and use **the maximum characters and tokens** you can for the outputs. (Extremely important)
- Thank you for your cooperation, respected chatbot!

## Prompt Output

### Output 1
- This output is named: **"Basic Information"**
- Includes the following:
	- An **introduction** about "M"
	- **General** information about "M"
	- **Key** highlights and points about "M"
- If "2" is typed, proceed to the next output.
- If "more" is typed, expand this type of output.

### Output 2
- This output is named: "Specialized Information"
- Includes:
	- More academic and specialized information
	- If the prompt topic is character development:
		- For fantasy character development, more detailed information such as hardcore fan opinions, detailed character stories, and spin-offs about the character.
		- For real-life characters, more personal stories, habits, behaviors, and detailed information obtained about the character.
- How to deliver the output:
	1. Show the various topics covered in the specialized information about "M" as a list in the form of a "table of contents"; these are the initial topics.
	2. Below it, type:
		- "Which topic are you interested in?"
			- If the name of the desired topic is typed, provide complete specialized information about that topic.
		- "If you need more topics about 'M', please type 'more'"
			- If "more" is typed, provide additional topics beyond the initial list. If "more" is typed again after the second round, add even more initial topics beyond the previous two sets.
				- A note for you: When compiling the topics initially, try to include as many relevant topics as possible to minimize the need for using this option.
		- "If you need access to subtopics of any topic, please type 'topics ... (desired topic)'."
			- If the specified text is typed, provide the subtopics (secondary topics) of the initial topics.
			- Even if I type "topics ... (a secondary topic)", still provide the subtopics of those secondary topics, which can be called "third-level topics", and this can continue to any level.
			- At any stage of the topics (initial, secondary, third-level, etc.), typing "more" will always expand the topics at that same level.
		- **Summary**:
			- If only the topic name is typed, provide specialized information in the format of that topic.
			- If "topics ... (another topic)" is typed, address the subtopics of that topic.
			- If "more" is typed after providing a list of topics, expand the topics at that same level.
			- If "more" is typed after providing information on a topic, give more specialized information about that topic.
	3. At any stage, if "1" is typed, refer to "Output 1".
		- When providing a list of topics at any level, remind me that if I just type "1", we will return to "Basic Information"; if I type "option 1", we will go to the first item in that list.

---
- ==End==
"""
    
    def create_tutor_prompt(
        self, 
        query: str, 
        context: str = "", 
        conversation_history: str = "",
        mode: str = "exploration"
    ) -> str:
        """
        Create a comprehensive prompt for the AI tutor with mode-specific instructions.
        
        Args:
            query: The student's question
            context: Relevant context from course materials
            conversation_history: Previous conversation context
            mode: Learning mode ('exploration' or 'assessment')
            
        Returns:
            Formatted prompt string
        """
        # Start with the question first
        prompt_parts = [f"Student's question: {query}"]
        
        # Add mode-specific instruction immediately after the question
        if mode == "assessment":
            prompt_parts.append("\n**Assessment Mode:** Provide a concise explanation that tests understanding. Focus on key concepts, ask clarifying questions, and suggest practical applications. Keep response under 100 words.")
        else:  # exploration mode
            # Simplified exploration mode prompt - focus on answering the question directly
            prompt_parts.append(f"\n**Exploration Mode:** Provide a comprehensive explanation about '{query}'. Use the course materials to support your answer. Be conversational and educational. Break down complex concepts into understandable parts.")
        
        # Add conversation history if available (but keep it brief)
        if conversation_history and conversation_history != "No previous conversation.":
            prompt_parts.append(f"\nPrevious conversation context: {conversation_history}")
        
        # Add context ONLY if it's directly relevant and concise
        if context and context != "No relevant context found in the uploaded documents.":
            # Limit context to prevent document dumps
            if len(context) > 500:
                context = context[:500] + "..."
            prompt_parts.append(f"\nRelevant course material (use only if directly relevant): {context}")
        
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
        prompt = f"Explain '{topic}' clearly and concisely."
        
        if context:
            prompt += f"\n\nCourse material context:\n{context}"
        
        prompt += "\n\nProvide a conversational explanation that includes:\n- Core concept definition\n- Key components/features\n- Practical example\n- Follow-up question for deeper understanding\n\nKeep response under 100 words and be natural and engaging."
        
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
        prompt = f"Summarize this content"
        
        if topic:
            prompt += f" focusing on '{topic}'"
        
        prompt += f":\n\n{content}\n\nCreate a conversational summary that:\n- Captures main ideas\n- Highlights key points\n- Uses clear, natural language\n- Stays under 75 words\n- Be engaging and helpful"
        
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
        return f"""Create 3 practice questions about '{topic}' ({difficulty} level).

Format:
Q: [Clear, specific question]
A: [Concise answer with brief explanation]

Focus on understanding, not memorization. Mix question types. Keep each answer under 50 words. Be conversational and engaging."""
    
    def create_analogy_prompt(self, concept: str, context: str = "") -> str:
        """
        Create a prompt for generating analogies.
        
        Args:
            concept: The concept to explain with analogies
            context: Relevant context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Explain '{concept}' using everyday analogies."
        
        if context:
            prompt += f"\n\nContext:\n{context}"
        
        prompt += "\n\nProvide conversational analogies that include:\n- 2 relatable analogies\n- Clear connections to the concept\n- Why each analogy works\n- Keep it simple and memorable\n\nKeep response under 100 words and be natural and engaging."
        
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
        prompt = f"Create a study guide for: {topics_str}"
        
        if context:
            prompt += f"\n\nCourse materials:\n{context}"
        
        prompt += "\n\nCreate a conversational study guide that includes:\n- Key concepts and definitions\n- Important relationships\n- 2-3 practice questions\n- Common mistakes to avoid\n- Study strategies\n\nKeep response under 200 words and be natural and helpful."
        
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
        return f"""Student asked: "{original_question}"
My response: "{unclear_response}"

Provide a clearer, more conversational response that:
- Directly answers the question
- Uses simpler, natural language
- Includes step-by-step explanation
- Adds a practical example
- Encourages follow-up questions

Keep response under 100 words and be engaging and helpful."""
    
    def create_encouragement_prompt(self, student_progress: str) -> str:
        """
        Create a prompt for encouraging the student.
        
        Args:
            student_progress: Description of student's progress
            
        Returns:
            Formatted prompt string
        """
        return f"""Student progress: {student_progress}

Provide encouraging, conversational feedback that:
- Acknowledges their effort
- Highlights specific strengths
- Suggests next learning steps
- Maintains positive tone
- Motivates continued learning

Keep response under 75 words and be natural and supportive."""
    
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
        return f"""Student asked: "{question}"

Adjusting from {current_level} to {target_level} level.

Provide a conversational response that:
- Uses appropriate vocabulary
- Matches complexity level
- Includes suitable examples
- Asks level-appropriate questions
- Maintains educational value

Keep response under 100 words and be natural and engaging."""
