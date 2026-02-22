import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from models.database import Base, engine
from api.ingestion import router as ingestion_router
from api.conversation import router as conversation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RAG Backend API",
    description="Document Ingestion + Conversational RAG with interview booking",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ingestion_router)
app.include_router(conversation_router)


@app.get("/")
def root():
    return {"message": "RAG Backend is running!", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": traceback.format_exc()}
    )