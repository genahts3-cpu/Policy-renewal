#!/usr/bin/env python3
"""
Startup script: seeds RAG knowledge base from policy text files.
Run once after first launch: python scripts/seed_rag.py
"""
import os
import sys

backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv()

from rag.rag_engine import ingest_text

POLICY_DIR = os.path.join(backend_dir, "data", "pdfs")

def main():
    if not os.path.exists(POLICY_DIR):
        print(f"No policy files found at {POLICY_DIR}. Run generate_pdfs.py first.")
        return

    files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".txt") or f.endswith(".pdf")]
    if not files:
        print("No policy files to ingest.")
        return

    for fname in files:
        fpath = os.path.join(POLICY_DIR, fname)
        if fname.endswith(".txt"):
            with open(fpath, "r") as f:
                content = f.read()
            source = fname.replace(".txt", "").replace("_", " ").title()
            chunks = ingest_text(content, metadata={"source": source, "filename": fname})
            print(f"Ingested {chunks} chunks from {fname}")
        elif fname.endswith(".pdf"):
            from rag.rag_engine import ingest_pdf
            chunks = ingest_pdf(fpath)
            print(f"Ingested {chunks} chunks from {fname}")

    print("RAG knowledge base ready.")

if __name__ == "__main__":
    main()
