from typing import List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    query: str
    stream: bool = False


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    latency_ms: int
