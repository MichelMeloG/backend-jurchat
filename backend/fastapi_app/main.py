from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
from dotenv import load_dotenv
from services.parser import DocumentParser
from services.ai import AIService
from config import settings

# Load environment variables
load_dotenv()

app = FastAPI(
    title=settings.APP_NAME,
    description="Microserviço de IA para processamento de documentos jurídicos",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
document_parser = DocumentParser()
ai_service = AIService()


# Pydantic models
class SummarizeResponse(BaseModel):
    document_id: str
    extracted_text: str
    summary: str
    tokens_used: int
    processing_time: float


class ChatRequest(BaseModel):
    message: str
    document_id: str
    document_content: str
    document_summary: str
    conversation_history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    response: str
    tokens_used: int
    metadata: Dict = {}


class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services={
            "parser": "active",
            "ai": "active"
        }
    )


@app.post("/ai/summarize", response_model=SummarizeResponse)
async def summarize_document(
    file: UploadFile = File(...),
    document_id: str = Form(...),
    user_id: int = Form(...)
):
    """
    Extract text from document and generate AI summary
    """
    try:
        # Validate file type
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from document
        extracted_text = document_parser.extract_text(file_content, file.content_type)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from document"
            )
        
        # Generate AI summary
        summary_result = await ai_service.generate_summary(
            text=extracted_text,
            document_type="legal"
        )
        
        return SummarizeResponse(
            document_id=document_id,
            extracted_text=extracted_text,
            summary=summary_result["summary"],
            tokens_used=summary_result["tokens_used"],
            processing_time=summary_result["processing_time"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/ai/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    """
    Process chat message with document context
    """
    try:
        # Generate AI response
        chat_result = await ai_service.generate_chat_response(
            user_message=request.message,
            document_content=request.document_content,
            document_summary=request.document_summary,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            response=chat_result["response"],
            tokens_used=chat_result["tokens_used"],
            metadata=chat_result.get("metadata", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/ai/analyze")
async def analyze_document_specific(
    document_type: str,
    analysis_type: str,
    document_content: str
):
    """
    Perform specific analysis on document
    """
    try:
        analysis_result = await ai_service.analyze_document(
            document_content=document_content,
            document_type=document_type,
            analysis_type=analysis_type
        )
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.get("/ai/models")
async def list_available_models():
    """
    List available AI models
    """
    return {
        "models": ai_service.get_available_models(),
        "current_model": ai_service.get_current_model()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
