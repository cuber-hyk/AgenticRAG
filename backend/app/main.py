import os
from fastapi import FastAPI, Request, Response
import time
import logging
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, upload, admin
from .utils.logging import setup_logging
from .config import Settings
from .services.llm_siliconcloud import SiliconCloudLLM

settings = Settings()
setup_logging(settings)

app = FastAPI(
    title="Agentic RAG API",
    version="0.1.0",
    description="FastAPI 服务，集成 Weaviate + LlamaIndex + langgraph 的 Agentic RAG 系统"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

logger = logging.getLogger("request")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = int((time.time() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} {response.status_code} {elapsed}ms")
    return response


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp: Response = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=()"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    if settings.environment == "production":
        resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return resp


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    # Initialize LLM and Embeddings globally
    try:
        SiliconCloudLLM(settings)
        logger.info("SiliconCloud LLM and Embeddings initialized")
    except Exception as e:
        logger.error(f"Failed to initialize SiliconCloud LLM: {e}")
