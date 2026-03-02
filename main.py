"""
FastAPI application for the RAG Knowledge Assistant.
This is the entry point that exposes the API endpoints.

Endpoints:
- POST /ingest - Load and index documents
- POST /query - Ask a question, get an answer
- GET /health - Check system status
- POST /evaluate - Run test suite
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from models.schemas import (
    QueryRequest, 
    QueryResponse, 
    IngestResponse,
    RetrievedContext
)
from services.document_loader import load_documents
from services.chunker import chunk_documents, get_chunk_stats
from services.embeddings import embed_chunks
from services.vector_store import get_vector_store
from services.retriever import retrieve, get_confidence_level, format_context_for_prompt
from services.prompt_builder import build_prompt, build_insufficient_context_response
from services.llm_services import generate_response, check_ollama_status
from services.guardrails import apply_guardrails
from services.evaluator import evaluate_retrieval, evaluate_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown logic.
    Loads existing vector store on startup if available.
    """
    # Startup: try to load existing index
    store = get_vector_store()
    print(f"Vector store loaded with {store.count} chunks")
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="RAG Knowledge Assistant for GMCA",
    description="Internal knowledge Q&A system with hallucination reduction",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file."""
    return FileResponse("index.html")


@app.get("/health")
async def health_check():
    """
    Check system health including Ollama connection.
    """
    store = get_vector_store()
    ollama_status = check_ollama_status()
    
    return {
        "status": "healthy",
        "vector_store_chunks": store.count,
        "ollama": ollama_status
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents():
    """
    Load documents from data/sample_docs and index them.
    
    This:
    1. Loads PDFs and text files
    2. Chunks them into smaller pieces
    3. Embeds each chunk into a vector
    4. Stores vectors in FAISS for fast search
    """
    try:
        # Step 1: Load documents
        documents = load_documents()
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found in data/sample_docs")
        
        # Step 2: Chunk documents
        chunks = chunk_documents(documents)
        chunk_stats = get_chunk_stats(chunks)
        print(f"Created {chunk_stats['count']} chunks from {len(documents)} documents")
        
        # Step 3: Embed chunks
        embeddings = embed_chunks(chunks)
        print(f"Generated embeddings with shape {embeddings.shape}")
        
        # Step 4: Store in vector store
        store = get_vector_store()
        store.clear()  # Clear existing data
        store.add_chunks(chunks, embeddings)
        store.save()  # Persist to disk
        
        return IngestResponse(
            documents_processed=len(documents),
            chunks_created=len(chunks),
            status="success"
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Answer a question using RAG.
    
    The full pipeline:
    1. Retrieve relevant chunks from vector store
    2. Check if context is sufficient
    3. Build grounded prompt
    4. Generate response with LLM
    5. Apply guardrails
    6. Return answer with metadata
    """
    question = request.question
    
    # Step 1: Retrieve relevant context
    contexts, has_sufficient_context = retrieve(question)
    
    # Step 2: Get confidence level based on retrieval quality
    confidence = get_confidence_level(contexts)
    
    # Step 3: Format context for prompt
    context_text = format_context_for_prompt(contexts)
    
    # Step 4: Build the prompt
    prompt = build_prompt(question, context_text, has_sufficient_context)
    
    # Step 5: Generate response from LLM
    if has_sufficient_context:
        raw_response = generate_response(prompt["system"], prompt["user"])
    else:
        # Don't even call LLM if we have no context - just return fallback
        raw_response = build_insufficient_context_response()
    
    # Step 6: Apply guardrails (check for hallucinations)
    final_response, is_grounded = apply_guardrails(
        raw_response, 
        context_text, 
        has_sufficient_context
    )
    
    return QueryResponse(
        answer=final_response,
        sources=contexts,
        confidence=confidence,
        retrieval_count=len(contexts),
        is_grounded=is_grounded
    )


@app.post("/evaluate")
async def run_evaluation():
    """
    Run the test suite to evaluate system performance.
    Returns results for each test case.
    """
    def query_fn(question: str) -> QueryResponse:
        """Wrapper to call query endpoint logic"""
        contexts, has_sufficient_context = retrieve(question)
        confidence = get_confidence_level(contexts)
        context_text = format_context_for_prompt(contexts)
        prompt = build_prompt(question, context_text, has_sufficient_context)
        
        if has_sufficient_context:
            raw_response = generate_response(prompt["system"], prompt["user"])
        else:
            raw_response = build_insufficient_context_response()
        
        final_response, is_grounded = apply_guardrails(
            raw_response, context_text, has_sufficient_context
        )
        
        return QueryResponse(
            answer=final_response,
            sources=contexts,
            confidence=confidence,
            retrieval_count=len(contexts),
            is_grounded=is_grounded
        )
    
    # Import here to avoid circular import
    from services.evaluator import run_test_suite
    results = run_test_suite(query_fn)
    
    # Calculate summary stats
    total = len(results)
    correct = sum(1 for r in results if r["correctly_handled"])
    
    return {
        "summary": {
            "total_tests": total,
            "correct": correct,
            "accuracy": f"{(correct/total)*100:.1f}%"
        },
        "results": results
    }


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)