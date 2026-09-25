from fastapi import APIRouter, HTTPException, status
from ..models.document import ChatRequest, ChatResponse
from ..services.chat_service import answer_question

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Ask a question about uploaded documents and receive an answer with source citations."""
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    try:
        result = answer_question(request.question)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your question: {e}"
        )
