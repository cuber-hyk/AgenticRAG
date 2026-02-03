from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..rag.document_loader import parse_files
from ..rag.vector_store import get_vector_store

router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    try:
        docs = await parse_files(files)
        vs = get_vector_store()
        vs.upsert_documents(docs)
        return {"status": "ok", "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
