"""
Evaluation service.
Measures the quality of retrieval and responses.

Why evaluation matters:
- You can't improve what you don't measure
- In production, you track these metrics over time
- Helps debug when answers are bad (is it retrieval? is it generation?)

This is a simple version. Production systems use more sophisticated methods.
"""

from models.schemas import RetrievedContext, QueryResponse


def evaluate_retrieval(
    query: str, 
    contexts: list[RetrievedContext]
) -> dict:
    """
    Evaluate the quality of retrieved contexts.
    
    Metrics:
    - retrieval_count: How many chunks were retrieved
    - avg_similarity: Average similarity score
    - max_similarity: Best match score
    - has_relevant_context: Did we find anything useful?
    """
    if not contexts:
        return {
            "retrieval_count": 0,
            "avg_similarity": 0.0,
            "max_similarity": 0.0,
            "has_relevant_context": False,
            "assessment": "No relevant documents found"
        }
    
    scores = [ctx.similarity_score for ctx in contexts]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    
    # Assess quality based on scores
    if max_score >= 0.7:
        assessment = "Strong match - high confidence retrieval"
    elif max_score >= 0.5:
        assessment = "Moderate match - acceptable retrieval"
    elif max_score >= 0.3:
        assessment = "Weak match - low confidence retrieval"
    else:
        assessment = "Poor match - retrieval may be unreliable"
    
    return {
        "retrieval_count": len(contexts),
        "avg_similarity": round(avg_score, 3),
        "max_similarity": round(max_score, 3),
        "has_relevant_context": max_score >= 0.3,
        "assessment": assessment
    }


def evaluate_response(response: QueryResponse) -> dict:
    """
    Evaluate the overall quality of a RAG response.
    
    Combines retrieval quality with response characteristics.
    """
    # Basic response stats
    answer_length = len(response.answer)
    word_count = len(response.answer.split())
    
    # Quality indicators
    has_sources = response.retrieval_count > 0
    is_grounded = response.is_grounded
    confidence = response.confidence
    
    # Score from 0-100
    quality_score = 0
    
    # Points for retrieval
    if response.retrieval_count >= 3:
        quality_score += 30
    elif response.retrieval_count >= 1:
        quality_score += 15
    
    # Points for confidence
    confidence_points = {
        "high": 30,
        "medium": 20,
        "low": 10,
        "insufficient": 0
    }
    quality_score += confidence_points.get(confidence, 0)
    
    # Points for grounding
    if is_grounded:
        quality_score += 25
    
    # Points for reasonable length (not too short, not too long)
    if 20 <= word_count <= 200:
        quality_score += 15
    elif 10 <= word_count <= 300:
        quality_score += 10
    
    return {
        "quality_score": quality_score,
        "answer_length": answer_length,
        "word_count": word_count,
        "has_sources": has_sources,
        "is_grounded": is_grounded,
        "confidence": confidence,
        "retrieval_count": response.retrieval_count
    }


def run_test_suite(query_fn) -> list[dict]:
    """
    Run a set of test queries to evaluate system performance.
    
    This is a simple test suite. In production, you'd have:
    - Golden dataset with expected answers
    - Human ratings
    - A/B test results
    
    query_fn: A function that takes a question and returns a QueryResponse
    """
    test_cases = [
        # Questions that SHOULD be answerable from GMCA/AI/Risk docs
        {
            "question": "What is GMCA's approach to artificial intelligence?",
            "expected_topic": "GMCA AI",
            "should_find_answer": True
        },
        {
            "question": "What are the main risks identified in the document?",
            "expected_topic": "risk",
            "should_find_answer": True
        },
        {
            "question": "How should AI systems be governed according to the policy?",
            "expected_topic": "AI governance",
            "should_find_answer": True
        },
        {
            "question": "What risk mitigation strategies are recommended?",
            "expected_topic": "risk mitigation",
            "should_find_answer": True
        },
        # Questions that should NOT be answerable (test "I don't know")
        {
            "question": "What is the organization's annual revenue?",
            "expected_topic": "revenue",
            "should_find_answer": False
        },
        {
            "question": "What is the weather forecast for tomorrow?",
            "expected_topic": "weather",
            "should_find_answer": False
        },
    ]
    
    results = []
    for test in test_cases:
        response = query_fn(test["question"])
        eval_result = evaluate_response(response)
        
        # Check if system correctly identified answerable vs not
        correctly_handled = (
            (test["should_find_answer"] and response.is_grounded) or
            (not test["should_find_answer"] and not response.is_grounded)
        )
        
        results.append({
            "question": test["question"],
            "expected_answerable": test["should_find_answer"],
            "system_grounded": response.is_grounded,
            "correctly_handled": correctly_handled,
            "quality_score": eval_result["quality_score"],
            "confidence": response.confidence
        })
    
    return results