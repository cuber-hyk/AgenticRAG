import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import ChatRequest, ChatResponse
from ..services.session import get_session_store
from ..rag.pipeline import get_agent_pipeline
from ..utils.retry import with_retry_circuit

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, session_store=Depends(get_session_store)):
    start = time.time()
    session = session_store.get_or_create(req.session_id)
    agent = get_agent_pipeline()
    try:
        result = with_retry_circuit(agent.run)(query=req.query, session=session)
        elapsed = time.time() - start
        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            latency_ms=int(elapsed * 1000),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
