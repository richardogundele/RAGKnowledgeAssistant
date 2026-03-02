"""
Retriever service.
Finds relevant chunks and decides if they're good enough to use.

This is where hallucination reduction technique #1 happens:
- If no chunk passes our quality threshold, we DON'T generate an answer
- We say "I don't know" instead of letting the LLM guess
"""

from models.schemas import DocumentChunk, RetrievedContext
from services.embeddings import embed_query
from services.vector_store import get_vector_store
from config import TOP_K, SIMILARITY_THRESHOLD


def retrieve(query: str) -> tuple[list[RetrievedContext], bool]:
    """
    Find relevant chunks for a query.
    
    Returns:
        - List of retrieved contexts (chunks + scores)
        - Boolean: True if we have enough context, False if insufficient
    
    The boolean is crucial for hallucination prevention:
    - True = "We found good context, safe to generate"
    - False = "Context is weak, should say 'I don't know'"
    """
    # Step 1: Convert question to numbers (embedding)
    query_embedding = embed_query(query)
    
    # Step 2: Find similar chunks in our database
    store = get_vector_store()
    results = store.search(query_embedding, top_k=TOP_K)
    
    # Step 3: Filter out low-quality matches
    # This is the key to reducing hallucinations!
    filtered_results = []
    for chunk, score in results:
        if score >= SIMILARITY_THRESHOLD:
            filtered_results.append(RetrievedContext(
                chunk=chunk,
                similarity_score=score
            ))
    
    # Step 4: Decide if we have enough context
    # If nothing passed our threshold, we don't have good context
    has_sufficient_context = len(filtered_results) > 0
    
    return filtered_results, has_sufficient_context


def get_confidence_level(contexts: list[RetrievedContext]) -> str:
    """
    Assess confidence based on retrieval quality.
    
    This helps users understand how reliable the answer is:
    - "high": We found very relevant context (scores > 0.7)
    - "medium": Context is decent but not perfect (scores 0.5-0.7)
    - "low": Context is weak (scores 0.3-0.5)
    - "insufficient": Nothing relevant found
    """
    if not contexts:
        return "insufficient"
    
    # Use the best (highest) score to judge confidence
    best_score = max(ctx.similarity_score for ctx in contexts)
    
    if best_score >= 0.7:
        return "high"
    elif best_score >= 0.5:
        return "medium"
    else:
        return "low"


def format_context_for_prompt(contexts: list[RetrievedContext]) -> str:
    """
    Format retrieved chunks into a string for the LLM prompt.
    
    Each chunk includes its source so the LLM can cite it.
    This encourages grounded responses.
    """
    if not contexts:
        return "No relevant context found."
    
    formatted_parts = []
    for i, ctx in enumerate(contexts, 1):
        source_info = f"[Source: {ctx.chunk.source}"
        if ctx.chunk.page_number:
            source_info += f", Page {ctx.chunk.page_number}"
        source_info += "]"
        
        formatted_parts.append(
            f"--- Context {i} {source_info} ---\n{ctx.chunk.content}"
        )
    
    return "\n\n".join(formatted_parts)