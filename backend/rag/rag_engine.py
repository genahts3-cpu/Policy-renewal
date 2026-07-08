import logging
import os
import httpx
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# SSL-disabled HTTP client for TCS internal proxy
_http_client = httpx.Client(verify=False)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.embedding_model,
        http_client=_http_client,
    )


def get_vectorstore() -> Chroma:
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    return Chroma(
        collection_name="policy_knowledge",
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def ingest_pdf(file_path: str) -> int:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    logger.info(f"Ingested {len(chunks)} chunks from {file_path}")
    return len(chunks)


def ingest_text(text: str, metadata: Optional[dict] = None) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = splitter.create_documents([text], metadatas=[metadata or {}])
    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)
    return len(docs)


def retrieve_context(query: str, k: int = 4) -> List[Document]:
    try:
        vectorstore = get_vectorstore()
        return vectorstore.similarity_search(query, k=k)
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        return []


def get_context_text(query: str, k: int = 4) -> str:
    docs = retrieve_context(query, k)
    if not docs:
        return ""
    return "\n\n---\n\n".join(d.page_content for d in docs)
