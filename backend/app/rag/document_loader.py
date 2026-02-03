from typing import List, Dict
from fastapi import UploadFile, HTTPException

async def parse_files(files: List[UploadFile]) -> List[Dict]:
    docs = []
    for f in files:
        name = (f.filename or "unknown").lower()
        if not (name.endswith(".md") or name.endswith(".pdf") or name.endswith(".docx") or name.endswith(".txt")):
            raise HTTPException(status_code=400, detail="仅支持上传 md/pdf/docx/txt 文件")
        content = await f.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="文件过大（>10MB）")
        text = ""
        if name.endswith(".md") or name.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")
        elif name.endswith(".pdf"):
            try:
                import io
                from PyPDF2 import PdfReader
                reader = PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception:
                text = ""
        elif name.endswith(".docx"):
            try:
                import io
                from docx import Document
                doc = Document(io.BytesIO(content))
                text = "\n".join([p.text for p in doc.paragraphs])
            except Exception:
                text = ""
        if text.strip():
            docs.append({"text": text, "source": f.filename or "unknown"})
    return docs
