from fastapi import APIRouter
from ..rag.vector_store import get_vector_store

router = APIRouter(tags=["admin"])


@router.post("/admin/reindex")
def reindex():
    vs = get_vector_store()
    vs.recreate_schema()
    return {"status": "ok"}
