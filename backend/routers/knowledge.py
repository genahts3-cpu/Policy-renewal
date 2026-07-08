import os
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from schemas.schemas import KnowledgeUploadResponse
from services.auth_service import get_admin_customer
from rag.rag_engine import ingest_pdf, ingest_text

router = APIRouter()


@router.post("/upload-pdf", response_model=KnowledgeUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    _: Customer = Depends(get_admin_customer),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    os.makedirs("data/pdfs", exist_ok=True)
    file_path = f"data/pdfs/{file.filename}"

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    chunks = ingest_pdf(file_path)
    return KnowledgeUploadResponse(message="PDF ingested successfully", chunks_added=chunks, filename=file.filename)


@router.post("/upload-text", response_model=KnowledgeUploadResponse)
async def upload_text(
    text: str,
    source: str = "manual",
    _: Customer = Depends(get_admin_customer),
):
    chunks = ingest_text(text, metadata={"source": source})
    return KnowledgeUploadResponse(message="Text ingested successfully", chunks_added=chunks, filename=source)
