"""
CodeGenie AI Editor — Chat Endpoint
POST /api/v1/chat — Send a message to Gemini AI (RAG-enhanced)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.api_key_auth import get_current_api_key
from app.models.models import APIKey, Conversation, Message
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.ai_service import ai_service
from app.services.vector_store import vector_store

router = APIRouter(prefix="/chat", tags=["AI Chat"])


async def _build_rag_context(query: str) -> str:
    """Retrieve relevant code from FAISS and format as context."""
    if vector_store.total_chunks == 0:
        return ""

    try:
        results = await vector_store.search(query, top_k=3)
        if not results:
            return ""

        context_parts = ["### Relevant code from the repository:\n"]
        for r in results:
            if r["score"] > 0.3:  # Only include reasonably relevant results
                context_parts.append(
                    f"**{r['file_path']}** (lines {r['line_start']}-{r['line_end']}):\n"
                    f"```{r['language']}\n{r['content']}\n```\n"
                )

        return "\n".join(context_parts) if len(context_parts) > 1 else ""
    except Exception:
        return ""


@router.post("", response_model=ChatResponse)
async def chat_with_ai(
    payload: ChatRequest,
    current_key: APIKey = Depends(get_current_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the Gemini AI and get a response.
    Automatically enriches with RAG context from indexed code.
    Requires a valid API key via X-API-Key header.
    """
    try:
        # Get or create conversation
        if payload.conversation_id:
            conversation_id = payload.conversation_id
        else:
            conversation = Conversation(
                api_key_id=current_key.id,
                title=payload.message[:50] + "..." if len(payload.message) > 50 else payload.message,
            )
            db.add(conversation)
            await db.flush()
            await db.refresh(conversation)
            conversation_id = conversation.id

        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=payload.message,
        )
        db.add(user_msg)

        # Build RAG context from indexed code
        rag_context = await _build_rag_context(payload.message)
        combined_context = ""
        if rag_context:
            combined_context += rag_context + "\n"
        if payload.context:
            combined_context += payload.context

        # Call Gemini AI with RAG-enhanced context
        ai_response = await ai_service.chat_completion(
            message=payload.message,
            context=combined_context or None,
        )

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
        )
        db.add(assistant_msg)
        await db.flush()

        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            model=settings.gemini_model,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}",
        )

