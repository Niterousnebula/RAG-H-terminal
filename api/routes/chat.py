from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.controller import Controller

router = APIRouter()
controller = Controller()


class ChatRequest(BaseModel):
    message: str
    file_path: str | None = None


def stream_generator(message, file_path):
    for token in controller.run_stream(message, file_path):
        yield token


@router.post("/chat")
def chat(req: ChatRequest):
    result = controller.run(req.message, req.file_path)
    return {"response": result}


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    return StreamingResponse(
        stream_generator(req.message, req.file_path),
        media_type="text/plain"
    )