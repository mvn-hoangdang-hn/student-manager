# app/services/prompt_engineering.py

from typing import Dict, List, Any, Optional


class PromptTemplates:
    """Centralized class for managing all prompt templates with advanced engineering techniques"""

    @staticmethod
    def get_system_message(user_role: Optional[str] = None) -> str:
        """Get the appropriate system message based on user role"""
        base_message = """
        You are an academic assistant for a student management system. Your name is EduBot.

        Follow these guidelines:
        1. Be precise and concise in your answers
        2. When presenting data about students, format it clearly with bullet points or tables
        3. Maintain privacy by not sharing sensitive student information unnecessarily
        4. If you're uncertain about an answer, acknowledge the limitations of your knowledge
        5. Focus on being helpful and informative rather than conversational
        6. Only provide information that is directly supported by the context provided
        7. Do not make up or hallucinate information that isn't in the provided context
        """

        if user_role == "teacher":
            return base_message + """
            Since you're assisting a teacher:
            - You can provide detailed academic analytics
            - Suggest interventions for struggling students
            - Offer comparative analysis across classes and subjects
            - Highlight exceptional performance and concerning patterns
            """
        elif user_role == "student":
            return base_message + """
            Since you're assisting a student:
            - Focus on their personal performance
            - Provide encouraging feedback
            - Suggest resources for improvement in weaker areas
            - Maintain a supportive and motivational tone
            """
        elif user_role == "admin":
            return base_message + """
            Since you're assisting an administrator:
            - Provide high-level analytics across all students
            - Focus on system-wide patterns and trends
            - Highlight areas that may need policy intervention
            - Maintain a factual, data-driven approach
            """
        else:
            return base_message

    @staticmethod
    def format_rag_prompt(query: str, context: str, metadata: Dict[str, Any] = None) -> str:
        """
        Create a RAG prompt with context inserted intelligently
        """
        # Extract query type to customize prompt
        query_type = PromptTemplates._classify_query_type(query)

        # Basic prompt with context
        prompt = f"""
        Based on the following academic database information, please answer this question:

        Question: {query}

        Context Information:
        {context}

        Remember: Only use the information provided in the context. If you can't find the answer in the context, 
        say "I don't have enough information in my current dataset to answer this question accurately."
        """

        # Add specific instructions based on query type
        if query_type == "comparison":
            prompt += """
            When comparing students or subjects:
            1. Present a clear comparison using bullet points or tables
            2. Highlight key differences and similarities
            3. Avoid making judgments about which is "better" - just present facts
            4. Include specific metrics that are relevant for comparison
            """
        elif query_type == "ranking":
            prompt += """
            When providing rankings:
            1. Clearly state the criteria used for ranking
            2. Present a numbered list with scores where available
            3. Explain any ties or special considerations
            4. Note if the ranking is based on limited data
            """
        elif query_type == "analytics":
            prompt += """
            When providing analytics:
            1. Include relevant statistical measures (average, median, range)
            2. Highlight any notable outliers or patterns
            3. Provide context for the numbers (is this good/typical/concerning?)
            4. Mention any limitations in the analysis
            """

        # Add specific context awareness based on metadata
        if metadata and metadata.get("recent_updates"):
            prompt += f"""
            Note: The database was last updated on {metadata.get('recent_updates')}. 
            Consider this when providing time-sensitive information.
            """

        return prompt

    @staticmethod
    def _classify_query_type(query: str) -> str:
        """
        Classify the type of query to customize prompt engineering
        """
        query = query.lower()

        # Classification logic
        if any(word in query for word in ["compare", "difference", "versus", "vs", "against"]):
            return "comparison"
        elif any(word in query for word in ["top", "best", "highest", "lowest", "rank", "worst"]):
            return "ranking"
        elif any(word in query for word in ["average", "mean", "median", "analyze", "trend", "pattern"]):
            return "analytics"
        elif any(word in query for word in ["who", "student", "name", "person"]):
            return "identification"
        elif any(word in query for word in ["when", "date", "time", "schedule"]):
            return "temporal"
        else:
            return "general"

    @staticmethod
    def generate_few_shot_examples(query_type: str) -> str:
        """
        Generate few-shot examples to guide the model's responses
        """
        examples = {
            "comparison": """
            Example Q: Compare the performance of students in Math vs Physics this semester.
            Example A: Based on the data provided:

            Math class:
            - Average score: 82.5
            - Highest score: 98 (by Jane Smith)
            - Number of students: 24

            Physics class:
            - Average score: 79.3
            - Highest score: 95 (by John Doe)
            - Number of students: 22

            The Math class has a slightly higher average score by 3.2 points, and the highest individual score is also 3 points higher than in Physics.
            """,

            "ranking": """
            Example Q: Who are the top 3 students in Computer Science?
            Example A: Based on the data provided, the top 3 students in Computer Science are:

            1. Maria Garcia - 97.5%
            2. James Wilson - 95.2%
            3. Sarah Johnson - 94.8%

            This ranking is based on their latest test scores in the Computer Science course.
            """,

            "analytics": """
            Example Q: What's the average performance in Biology this semester?
            Example A: Based on the data provided:

            The average score in Biology this semester is 78.6%.
            - Highest score: 94% (by Alex Wong)
            - Lowest score: 62% (by Chris Martin)
            - Median score: 79%
            - Standard deviation: 8.3

            25% of students scored above 85%, while 15% scored below 70%.
            """,
        }

        return examples.get(query_type, "")


class RAGPromptOptimizer:
    """Optimizes RAG prompts based on different strategies"""

    @staticmethod
    def optimize_for_relevance(query: str, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and re-rank retrieved documents for maximum relevance"""
        # Simple implementation - in production this would be more sophisticated
        # This could involve re-ranking based on semantic similarity to the query

        # For now, just filter out obviously irrelevant docs
        filtered_docs = []
        query_terms = set(query.lower().split())

        for doc in retrieved_docs:
            content = doc.get("page_content", "").lower()
            # Calculate a simple relevance score based on term overlap
            matching_terms = sum(1 for term in query_terms if term in content)
            if matching_terms > 0:
                doc["relevance_score"] = matching_terms / len(query_terms)
                filtered_docs.append(doc)

        filtered_docs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return filtered_docs[:3]

    @staticmethod
    def prioritize_context(retrieved_docs: List[Dict[str, Any]], query_type: str) -> str:
        """
        Arrange context in order of importance based on query type
        Returns formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found in the database."

        formatted_chunks = []

        if query_type == "ranking":
            for doc in retrieved_docs:
                content = doc.get("page_content", "")
                if any(c.isdigit() for c in content):
                    formatted_chunks.append(f"[HIGH RELEVANCE] {content}")
                else:
                    formatted_chunks.append(content)
        else:
            for i, doc in enumerate(retrieved_docs):
                content = doc.get("page_content", "")
                relevance = doc.get("relevance_score", 0)
                if relevance > 0.7:
                    formatted_chunks.append(f"[HIGH RELEVANCE] {content}")
                else:
                    formatted_chunks.append(content)

        return "\n\n".join(formatted_chunks)