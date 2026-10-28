from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.services.llm_service import generate_response


app = FastAPI(
    title="AI Codebase Assistant",
    version="0.2.0"
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Codebase Assistant",
        "version": "0.2.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = await generate_response(request.message)

    return ChatResponse(answer=answer)