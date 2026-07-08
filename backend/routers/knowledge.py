import os
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from schemas.schemas import KnowledgeUploadResponse
from services.auth_service import get_admin_customer
from services.rate_limiter import check_rate_limit
from services.audit_service import write_audit_log
from rag.rag_engine import ingest_pdf, ingest_text

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
BLOCKED_EXTENSIONS = {".exe", ".zip", ".js", ".bat", ".sh"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload-pdf", response_model=KnowledgeUploadResponse)
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    current: Customer = Depends(get_admin_customer),
    db: Session = Depends(get_db),
):
    check_rate_limit(current.id)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        write_audit_log(db=db, user_id=current.id, agent_name="KnowledgeRouter",
                        action="upload", question=file.filename, status="blocked")
        raise HTTPException(status_code=400, detail="Invalid File: file type not allowed.")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid File: only {', '.join(ALLOWED_EXTENSIONS)} are allowed.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Invalid File: file exceeds 20MB limit.")

    os.makedirs("data/pdfs", exist_ok=True)
    file_path = f"data/pdfs/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    chunks = ingest_pdf(file_path) if ext == ".pdf" else ingest_text(content.decode("utf-8", errors="ignore"), {"source": file.filename})

    write_audit_log(
        db=db, user_id=current.id, agent_name="KnowledgeRouter",
        action="upload", question=file.filename,
        response=f"{chunks} chunks ingested", status="success",
        ip_address=request.client.host if request.client else None,
    )
    return KnowledgeUploadResponse(message="File ingested successfully", chunks_added=chunks, filename=file.filename)


@router.post("/upload-text", response_model=KnowledgeUploadResponse)
async def upload_text(
    text: str,
    source: str = "manual",
    current: Customer = Depends(get_admin_customer),
    db: Session = Depends(get_db),
):
    chunks = ingest_text(text, metadata={"source": source})
    write_audit_log(db=db, user_id=current.id, agent_name="KnowledgeRouter",
                    action="upload_text", question=source, response=f"{chunks} chunks", status="success")
    return KnowledgeUploadResponse(message="Text ingested successfully", chunks_added=chunks, filename=source)
