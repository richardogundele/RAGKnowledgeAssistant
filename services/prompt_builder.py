"""
Prompt builder service.
Constructs prompts that force the LLM to stay grounded in retrieved context.

This is hallucination reduction technique #2: GROUNDED PROMPTING
- We explicitly tell the LLM: "Only use the provided context"
- We tell it to say "I don't know" if context doesn't have the answer
- We tell it to cite sources

The prompt is like giving instructions to a careful employee:
"Only answer from these documents. If it's not in there, say so."
"""


# System prompt that enforces grounded behavior
SYSTEM_PROMPT = """You are a helpful internal knowledge assistant for GMCA Corporation.

CRITICAL RULES - YOU MUST FOLLOW THESE:

1. ONLY use information from the PROVIDED CONTEXT below to answer questions.

2. If the context does NOT contain enough information to answer the question, 
   you MUST say: "I don't have enough information in the available documents to answer this question."

3. DO NOT use any knowledge from your training data. Pretend you know nothing except what's in the context.

4. When you answer, cite which source document the information came from.
   Example: "According to the Employee Handbook, you receive 20 days of PTO."

5. If you're unsure, say so. Never guess or make assumptions.

6. Keep answers concise and direct.

Your goal is to be ACCURATE, not impressive. A short accurate answer is better than a long wrong one."""


def build_prompt(query: str, context: str, has_sufficient_context: bool) -> dict:
    """
    Build the full prompt for the LLM.
    
    Returns a dict with 'system' and 'user' messages.
    This format works with most LLM APIs (OpenAI, Ollama, etc.)
    """
    
    if not has_sufficient_context:
        # If we don't have good context, tell the LLM upfront
        # This makes it more likely to say "I don't know"
        user_message = f"""Question: {query}

CONTEXT STATUS: No relevant documents were found for this question.

Since no relevant context is available, please respond that you don't have 
enough information to answer this question accurately."""
    
    else:
        # Normal case: we have context
        user_message = f"""Question: {query}

CONTEXT FROM COMPANY DOCUMENTS:
{context}

END OF CONTEXT

Please answer the question using ONLY the information provided in the context above.
Remember to cite which document your answer comes from."""
    
    return {
        "system": SYSTEM_PROMPT,
        "user": user_message
    }


def build_insufficient_context_response() -> str:
    """
    Standard response when we don't have enough context.
    Used as a fallback to ensure consistent messaging.
    """
    return (
        "I don't have enough information in the available documents to answer "
        "this question. Please try rephrasing your question, or this topic may "
        "not be covered in the current knowledge base."
    )