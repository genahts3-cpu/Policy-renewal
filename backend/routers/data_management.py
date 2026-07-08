import os
import logging
import aiofiles
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from models.customer import Customer
from models.policy import Policy
from models.claim import Claim
from models.renewal import Renewal
from models.notification import Notification
from services.auth_service import get_admin_customer
from services.chroma_service import (
    get_collections, get_all_documents, get_statistics as chroma_stats,
    delete_document, delete_by_source, COLLECTIONS,
)
from services.dataset_service import import_dataset, get_import_statistics
from rag.rag_engine import get_embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_DOC_EXTENSIONS = {".pdf", ".txt", ".docx"}
ALLOWED_DATASET_EXTENSIONS = {".csv", ".xlsx"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _collection_for_file(filename: str) -> str:
    name = filename.lower()
    if "faq" in name:
        return "policy_faqs"
    if "claim" in name:
        return "claim_rules"
    if "brochure" in name:
        return "brochures"
    if "term" in name or "condition" in name:
        return "terms_conditions"
    return "insurance_policies"


def _extract_text(content: bytes, filename: str, file_path: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".txt":
        return content.decode("utf-8", errors="ignore")
    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.schema import Document
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return "\n\n".join(p.page_content for p in pages)
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            return content.decode("utf-8", errors="ignore")
    return content.decode("utf-8", errors="ignore")


# ── Document Upload ──────────────────────────────────────────────────────────

@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    collection: Optional[str] = Query(default=None),
    _: Customer = Depends(get_admin_customer),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_DOC_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_DOC_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20MB limit.")

    os.makedirs("data/pdfs", exist_ok=True)
    file_path = f"data/pdfs/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    text = _extract_text(content, file.filename, file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    col_name = collection if collection in COLLECTIONS else _collection_for_file(file.filename)

    try:
        embedder = get_embeddings()
        vectors = embedder.embed_documents(chunks)
        from services.chroma_service import add_document_chunks
        count = add_document_chunks(col_name, chunks, file.filename, vectors)
    except Exception as e:
        logger.error(f"Embedding/storage failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

    return {
        "status": "Indexed",
        "collection": col_name,
        "chunks": count,
        "embeddings": count,
        "documentName": file.filename,
    }


# ── Dataset Upload ───────────────────────────────────────────────────────────

@router.post("/upload/dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    _: Customer = Depends(get_admin_customer),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_DATASET_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_DATASET_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20MB limit.")

    result = import_dataset(content, file.filename, db)
    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ── Collections ──────────────────────────────────────────────────────────────

@router.get("/collections")
async def list_collections(_: Customer = Depends(get_admin_customer)):
    return get_collections()


@router.get("/collections/{collection_name}")
async def get_collection(
    collection_name: str,
    search: Optional[str] = Query(default=None),
    _: Customer = Depends(get_admin_customer),
):
    if collection_name not in COLLECTIONS:
        raise HTTPException(status_code=404, detail="Collection not found.")
    from services.chroma_service import get_collection_documents
    return get_collection_documents(collection_name, search)


# ── Documents ────────────────────────────────────────────────────────────────

@router.get("/documents")
async def list_documents(
    search: Optional[str] = Query(default=None),
    collection: Optional[str] = Query(default=None),
    _: Customer = Depends(get_admin_customer),
):
    return get_all_documents(search=search, collection=collection)


@router.delete("/documents/{document_id}")
async def remove_document(
    document_id: str,
    collection: str = Query(...),
    _: Customer = Depends(get_admin_customer),
):
    if collection not in COLLECTIONS:
        raise HTTPException(status_code=404, detail="Collection not found.")
    ok = delete_document(collection, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "deleted", "id": document_id}


# ── Database Statistics ──────────────────────────────────────────────────────

@router.get("/database/stats")
async def database_stats(
    _: Customer = Depends(get_admin_customer),
    db: Session = Depends(get_db),
):
    chroma = chroma_stats()
    sqlite = get_import_statistics(db)
    return {
        "customers": sqlite["customers"],
        "policies": sqlite["policies"],
        "claims": sqlite["claims"],
        "renewals": sqlite["renewals"],
        "notifications": sqlite["notifications"],
        "documents": chroma["total_chunks"],
        "embeddings": chroma["total_chunks"],
        "collections": chroma["collection_breakdown"],
    }


# ── Dataset Re-import ────────────────────────────────────────────────────────

@router.post("/datasets/reimport")
async def reimport_dataset(
    file: UploadFile = File(...),
    _: Customer = Depends(get_admin_customer),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_DATASET_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    content = await file.read()
    result = import_dataset(content, file.filename, db)
    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ── Dataset Status ───────────────────────────────────────────────────────────

@router.get("/datasets/status")
async def dataset_status(
    _: Customer = Depends(get_admin_customer),
    db: Session = Depends(get_db),
):
    return get_import_statistics(db)
