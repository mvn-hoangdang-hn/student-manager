# app/services/ai_service.py

import os
from typing import Dict, List, Any, Optional
import httpx
import json
from datetime import datetime

from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.services.data_service import DataService
from app.services.prompt_engineering import PromptTemplates, RAGPromptOptimizer


class AIService:
    """Service for AI-related functionality including the chatbot and RAG system"""

    def __init__(self):
        self.data_service = DataService()
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.last_update_time = None
        self.initialize_vector_store()

    def initialize_vector_store(self):
        """Initialize the vector store with data from the database"""
        # Get data for embedding
        students_data = self.data_service.get_all_students_with_grades()
        courses_data = self.data_service.get_courses_data()

        # Process and split the data
        documents = self._process_data_to_documents(students_data, courses_data)

        # Create vector store
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        self.last_update_time = datetime.now()

        # Save vector store info for analytics
        self._save_vector_store_stats(len(documents))

    def _process_data_to_documents(self, students_data: List[Dict[str, Any]],
                                   courses_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert structured data to documents for the vector store with enhanced metadata"""
        documents = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        # Process student data
        for item in students_data:
            # Create rich text representation of each student with their grades
            text = f"Student: {item['name']} (Email: {item['email']})\n"
            text += f"ID: {item['id']}\n"
            text += f"Enrollment Date: {item['enrollment_date']}\n"

            if 'grades' in item and item['grades']:
                text += "Grades:\n"
                for grade in item['grades']:
                    text += f"- {grade['subject']}: {grade['score']} ({grade['semester']})\n"

                # Add calculated metrics
                if len(item['grades']) > 0:
                    avg_score = sum(g['score'] for g in item['grades']) / len(item['grades'])
                    text += f"Average Score: {avg_score:.2f}\n"

                    # Best and worst subjects
                    best_subject = max(item['grades'], key=lambda g: g['score'])
                    worst_subject = min(item['grades'], key=lambda g: g['score'])
                    text += f"Best Subject: {best_subject['subject']} ({best_subject['score']})\n"
                    text += f"Needs Improvement: {worst_subject['subject']} ({worst_subject['score']})\n"

            # Add any project or contribution info if available
            if item.get('ai_rag_project'):
                text += f"AI RAG Project: {item['ai_rag_project']}\n"
            if item.get('project_contributions'):
                text += f"Project Contributions: {item['project_contributions']}\n"
            if item.get('learning_results'):
                text += f"Learning Results: {item['learning_results']}\n"

            # Split into chunks and add to documents
            chunks = text_splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                documents.append({
                    "page_content": chunk,
                    "metadata": {
                        "student_id": str(item['id']),
                        "type": "student_record",
                        "name": item['name'],
                        "chunk_number": i,
                        "total_chunks": len(chunks)
                    }
                })

        # Process course data
        for course in courses_data:
            text = f"Course: {course['name']} (ID: {course['id']})\n"
            text += f"Department: {course['department']}\n"
            text += f"Description: {course['description']}\n"

            if 'statistics' in course:
                text += "Course Statistics:\n"
                text += f"- Average Score: {course['statistics']['avg_score']:.2f}\n"
                text += f"- Number of Students: {course['statistics']['student_count']}\n"
                text += f"- Pass Rate: {course['statistics']['pass_rate'] * 100:.1f}%\n"

            chunks = text_splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                documents.append({
                    "page_content": chunk,
                    "metadata": {
                        "course_id": str(course['id']),
                        "type": "course_record",
                        "name": course['name'],
                        "chunk_number": i,
                        "total_chunks": len(chunks)
                    }
                })

        return documents

    def _save_vector_store_stats(self, document_count: int):
        """Save statistics about the vector store for monitoring"""
        stats = {
            "document_count": document_count,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "last_updated": self.last_update_time.isoformat(),
            "vector_dimensions": 384  # Dimensions for the selected model
        }

        # In a real system, save to a database or log file
        # For now, just print
        print(f"Vector store stats: {json.dumps(stats, indent=2)}")

    async def query_groq(self, prompt: str, system_message: str = None) -> str:
        """Query the Groq API for a response with enhanced error handling and logging"""
        groq_api_key = settings.GROQ_API_KEY
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        data = {
            "model": "llama3-70b-8192",  # Or another Groq model
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 1000
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=data)
                if response.status_code != 200:
                    error_detail = response.json() if response.headers.get(
                        "content-type") == "application/json" else response.text
                    raise Exception(f"Error from Groq API ({response.status_code}): {error_detail}")

                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            raise Exception("Request to Groq API timed out. The service might be experiencing high demand.")
        except Exception as e:
            # Log the error, then re-raise
            print(f"Error in Groq API call: {str(e)}")
            raise

    async def chat(self, query: str, user_id: Optional[str] = None, user_role: Optional[str] = None) -> Dict[str, Any]:
        """Process a natural language query using RAG and return a response with enhanced context processing"""
        # 1. Classify query type for prompt optimization
        query_type = PromptTemplates._classify_query_type(query)

        # 2. Retrieve relevant documents based on the query
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 8})  # Get more docs for filtering
        raw_docs = retriever.get_relevant_documents(query)

        # 3. Convert to dict format for optimization
        docs_dict = [
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata
            } for doc in raw_docs
        ]

        # 4. Optimize retrieved documents using RAG techniques
        optimized_docs = RAGPromptOptimizer.optimize_for_relevance(query, docs_dict)

        # 5. Prioritize and format context based on query type
        context = RAGPromptOptimizer.prioritize_context(optimized_docs, query_type)

        # 6. Build advanced prompts
        system_message = PromptTemplates.get_system_message(user_role)

        # Add few-shot examples if available
        few_shot_examples = PromptTemplates.generate_few_shot_examples(query_type)
        if few_shot_examples:
            system_message += "\n\nHere's an example of how to answer this type of question:\n" + few_shot_examples

        # Create metadata for prompt
        metadata = {
            "recent_updates": self.last_update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "query_type": query_type
        }

        # Generate the main prompt with context
        prompt = PromptTemplates.format_rag_prompt(query, context, metadata)

        # 7. Get response from LLM (Groq)
        response_text = await self.query_groq(prompt, system_message)

        # 8. Prepare and return the final response with enhanced metadata
        sources = []
        student_ids = set()
        course_ids = set()

        for doc in optimized_docs:
            metadata = doc.get("metadata", {})
            doc_type = metadata.get("type", "unknown")

            if doc_type == "student_record" and "student_id" in metadata:
                student_ids.add(metadata["student_id"])
                sources.append({
                    "id": metadata["student_id"],
                    "type": "student",
                    "name": metadata.get("name", "Unknown Student"),
                    "relevance": doc.get("relevance_score", 0),
                    "snippet": doc["page_content"][:100] + "..." if len(doc["page_content"]) > 100 else doc[
                        "page_content"]
                })
            elif doc_type == "course_record" and "course_id" in metadata:
                course_ids.add(metadata["course_id"])
                sources.append({
                    "id": metadata["course_id"],
                    "type": "course",
                    "name": metadata.get("name", "Unknown Course"),
                    "relevance": doc.get("relevance_score", 0),
                    "snippet": doc["page_content"][:100] + "..." if len(doc["page_content"]) > 100 else doc[
                        "page_content"]
                })

        return {
            "answer": response_text,
            "sources": sources,
            "metadata": {
                "query_type": query_type,
                "student_count": len(student_ids),
                "course_count": len(course_ids),
                "context_length": len(context),
                "processing_time": "0.5s",  # Placeholder - would be actual timing in production
                "last_db_update": self.last_update_time.isoformat()
            },
            "confidence": 0.85  # Would be calculated in production
        }

    def refresh_vector_store(self):
        """Refresh the vector store with the latest data"""
        self.initialize_vector_store()