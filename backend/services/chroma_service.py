import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional
import chromadb
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

COLLECTIONS = [
    "insurance_policies",
    "policy_faqs",
    "claim_rules",
    "brochures",
    "terms_conditions",
]


def _get_client() -> chromadb.PersistentClient:
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def ensure_collections():
    client = _get_client()
    for name in COLLECTIONS:
        client.get_or_create_collection(name)


def get_collections() -> List[dict]:
    client = _get_client()
    result = []
    for name in COLLECTIONS:
        try:
            col = client.get_or_create_collection(name)
            result.append({"name": name, "documents": col.count()})
        except Exception as e:
            logger.warning(f"Could not get collection {name}: {e}")
            result.append({"name": name, "documents": 0})
    return result


def get_collection_documents(collection_name: str, search: Optional[str] = None) -> List[dict]:
    if collection_name not in COLLECTIONS:
        return []
    client = _get_client()
    col = client.get_or_create_collection(collection_name)
    try:
        if search:
            results = col.query(query_texts=[search], n_results=min(20, max(col.count(), 1)))
            ids = results.get("ids", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            documents = results.get("documents", [[]])[0]
        else:
            data = col.get()
            ids = data.get("ids", [])
            metadatas = data.get("metadatas", []) or [{}] * len(ids)
            documents = data.get("documents", []) or [""] * len(ids)

        return [
            {
                "id": ids[i],
                "collection": collection_name,
                "source_file": (metadatas[i] or {}).get("source", ""),
                "page": (metadatas[i] or {}).get("page", ""),
                "chunk": (metadatas[i] or {}).get("chunk_number", i),
                "created_at": (metadatas[i] or {}).get("created_at", ""),
                "preview": (documents[i] or "")[:120],
            }
            for i in range(len(ids))
        ]
    except Exception as e:
        logger.error(f"get_collection_documents failed: {e}")
        return []


def get_all_documents(search: Optional[str] = None, collection: Optional[str] = None) -> List[dict]:
    targets = [collection] if collection and collection in COLLECTIONS else COLLECTIONS
    docs = []
    for col_name in targets:
        docs.extend(get_collection_documents(col_name, search))
    return docs


def add_document_chunks(
    collection_name: str,
    chunks: List[str],
    source_file: str,
    embeddings: List[List[float]],
) -> int:
    if collection_name not in COLLECTIONS:
        collection_name = COLLECTIONS[0]
    client = _get_client()
    col = client.get_or_create_collection(collection_name)
    now = datetime.utcnow().isoformat()
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [
        {"source": source_file, "chunk_number": i, "created_at": now}
        for i in range(len(chunks))
    ]
    col.add(ids=ids, documents=chunks, metadatas=metadatas, embeddings=embeddings)
    return len(chunks)


def delete_document(collection_name: str, document_id: str) -> bool:
    if collection_name not in COLLECTIONS:
        return False
    client = _get_client()
    col = client.get_or_create_collection(collection_name)
    try:
        col.delete(ids=[document_id])
        return True
    except Exception as e:
        logger.error(f"delete_document failed: {e}")
        return False


def delete_by_source(collection_name: str, source_file: str) -> int:
    if collection_name not in COLLECTIONS:
        return 0
    client = _get_client()
    col = client.get_or_create_collection(collection_name)
    try:
        data = col.get(where={"source": source_file})
        ids = data.get("ids", [])
        if ids:
            col.delete(ids=ids)
        return len(ids)
    except Exception as e:
        logger.error(f"delete_by_source failed: {e}")
        return 0


def get_statistics() -> dict:
    collections = get_collections()
    total_docs = sum(c["documents"] for c in collections)
    return {
        "collections": len(collections),
        "total_chunks": total_docs,
        "collection_breakdown": collections,
    }
