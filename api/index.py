from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import cohere
from .rag import Chatbot, Documents

app = FastAPI()

# Global state for RAG system
rag_system = {
    "api_key": None,
    "chatbot": None,
    "documents": None
}

class ChatRequest(BaseModel):
    message: str
    api_key: str

class ChatResponse(BaseModel):
    response: str
    is_stream: bool = False

SOURCES = [
    {
        "title": "Cryptography - Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Cryptography"
    }, 
    {
        "title": "History of Cryptography",
        "url": "https://en.wikipedia.org/wiki/History_of_cryptography"
    },
    {
        "title": "Crypto 101",
        "url": "https://www.crypto101.io/Crypto101.pdf"
    },
]

@app.post("/api/chat")
async def chat(request: ChatRequest):
    global rag_system

    # Initialize RAG if needed
    if rag_system["api_key"] != request.api_key or rag_system["chatbot"] is None:
        try:
            client = cohere.ClientV2(request.api_key)
            # Validate key
            client.chat(model="command-a-03-2025", messages=[{"role": "user", "content": "ping"}])
            
            # Initialize Pipeline
            documents = Documents(SOURCES, client)
            chatbot = Chatbot(documents, client)
            
            rag_system["api_key"] = request.api_key
            rag_system["documents"] = documents
            rag_system["chatbot"] = chatbot
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Initialization Failed: {str(e)}")

    chatbot = rag_system["chatbot"]

    from fastapi.responses import StreamingResponse

    async def response_generator():
        try:
            for text_chunk in chatbot.generate_response(request.message):
                yield text_chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(response_generator(), media_type="text/plain")

@app.get("/api/health")
def health():
    return {"status": "ok"}
