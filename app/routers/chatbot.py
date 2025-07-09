# app/routers/chatbot.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional, List

from app.schemas.chatbot import ChatQuery, ChatResponse, ChatFeedback
from app.services.ai_service import AIService

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)

# Singleton instance of AIService
ai_service = AIService()


def get_ai_service():
    return ai_service


@router.post("/query", response_model=ChatResponse)
async def query_chatbot(
        query: ChatQuery,
        ai_service: AIService = Depends(get_ai_service)
):
    """
    Process a natural language query and return a response using RAG.

    Examples:
    - "Show me the top 5 students in math this semester"
    - "What is the average grade in Computer Science?"
    - "Who has the highest score in Physics?"
    - "Compare the performance of students in Biology versus Chemistry"
    """
    try:
        result = await ai_service.chat(query.query, query.user_id,
                                       user_role=query.context.get("user_role") if query.context else None)
        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources"),
            metadata=result.get("metadata", {"query_type": "academic", "processed_by": "groq-rag"}),
            confidence=result.get("confidence")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(feedback: ChatFeedback):
    """Submit feedback for a chatbot response to help improve the system"""
    # In a real system, this would store the feedback in a database
    # and potentially use it for model fine-tuning
    return {
        "success": True,
        "message": "Feedback received, thank you!",
        "feedback_id": "fb_" + feedback.response_id
    }


@router.post("/refresh-knowledge", response_model=Dict[str, Any])
async def refresh_knowledge(
        ai_service: AIService = Depends(get_ai_service)
):
    """
    Refresh the vector store with the latest data from the database.
    Should be called after significant data updates.
    """
    try:
        ai_service.refresh_vector_store()
        return {
            "success": True,
            "message": "Knowledge base refreshed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing knowledge base: {str(e)}")


@router.get("/suggest-queries", response_model=List[str])
async def suggest_queries(
        context: Optional[str] = Query(None,
                                       description="Context for query suggestions (e.g., 'grades', 'students', 'courses')"),
):
    """Provides suggested natural language queries based on the given context"""
    suggestions = {
        "grades": [
            "Show me the top 5 students in Mathematics this semester",
            "What's the average score in Computer Science?",
            "Which student has improved the most in Physics between semesters?",
            "Compare the grade distributions between Biology and Chemistry",
            "Show me students with failing grades who need intervention"
        ],
        "students": [
            "Who are the new students that enrolled this semester?",
            "Show me students participating in AI RAG projects",
            "Which students are excelling in multiple subjects?",
            "Give me a profile of student with ID XYZ including all their grades",
            "Find students who haven't submitted their projects yet"
        ],
        "courses": [
            "Which courses have the highest pass rates?",
            "Show me enrollment trends for Computer Science courses",
            "Compare student performance in introductory vs advanced courses",
            "Which course has the most even grade distribution?",
            "What's the most challenging course based on average grades?"
        ]
    }

    if not context or context not in suggestions:
        # Return a mix of suggestions if no valid context
        all_suggestions = []
        for category in suggestions.values():
            all_suggestions.extend(category[:2])  # Take 2 from each category
        return all_suggestions[:5]

    return suggestions[context]