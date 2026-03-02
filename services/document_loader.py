"""
Document loader service.
Loads PDF and text files, extracts content with metadata for provenance tracking.
"""

import os
from pathlib import Path
from pypdf import PdfReader

from models.schemas import DocumentChunk
from config import DOCUMENTS_PATH


def load_documents(directory: str = DOCUMENTS_PATH) -> list[dict]:
    """
    Load all documents from a directory.
    Returns raw text with source metadata.
    
    Why metadata matters: In production, you need to trace answers back to sources.
    This is critical for auditability and debugging hallucinations.
    """
    documents = []
    doc_path = Path(directory)
    
    if not doc_path.exists():
        raise FileNotFoundError(f"Documents directory not found: {directory}")
    
    for file_path in doc_path.iterdir():
        if file_path.suffix.lower() == ".pdf":
            # Handle PDF files
            docs = _load_pdf(file_path)
            documents.extend(docs)
        elif file_path.suffix.lower() in [".txt", ".md"]:
            # Handle text files
            docs = _load_text(file_path)
            documents.extend(docs)
    
    return documents


def _load_pdf(file_path: Path) -> list[dict]:
    """
    Extract text from PDF, preserving page numbers.
    Each page becomes a separate document entry for granular retrieval.
    """
    documents = []
    reader = PdfReader(file_path)
    
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text and text.strip():  # Skip empty pages
            documents.append({
                "content": text.strip(),
                "source": file_path.name,
                "page_number": page_num
            })
    
    return documents


def _load_text(file_path: Path) -> list[dict]:
    """
    Load plain text file as a single document.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return [{
        "content": content.strip(),
        "source": file_path.name,
        "page_number": None  # Text files don't have pages
    }]