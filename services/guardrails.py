"""
Guardrails service.
Post-generation checks to catch potential hallucinations.

This is hallucination reduction technique #3: OUTPUT VALIDATION
- Check if the LLM's answer is grounded in the retrieved context
- Detect hedging language that suggests uncertainty
- Flag responses that might be fabricated

Think of this as a "fact checker" that reviews the LLM's work.
"""

import re


# Phrases that suggest the LLM is uncertain or guessing
HEDGING_PHRASES = [
    "i think",
    "i believe", 
    "probably",
    "possibly",
    "might be",
    "could be",
    "it seems",
    "generally",
    "usually",
    "typically",
    "in most cases",
    "as far as i know",
    "i'm not sure",
    "i don't have specific",
]

# Phrases that indicate the LLM admitted it doesn't know
ADMISSION_PHRASES = [
    "i don't have enough information",
    "not covered in",
    "no information available",
    "cannot find",
    "don't have access",
    "not mentioned in",
    "unable to find",
]


def check_response_grounding(response: str, context: str) -> dict:
    """
    Check if the response appears to be grounded in the provided context.
    
    This is a simple heuristic approach:
    - Look for key terms from context appearing in response
    - Check for hedging language
    - Check if LLM admitted uncertainty
    
    Returns a dict with grounding assessment.
    """
    response_lower = response.lower()
    context_lower = context.lower()
    
    # Check 1: Did the LLM admit it doesn't know?
    admitted_uncertainty = any(
        phrase in response_lower for phrase in ADMISSION_PHRASES
    )
    
    # Check 2: Is the LLM hedging/guessing?
    hedging_detected = any(
        phrase in response_lower for phrase in HEDGING_PHRASES
    )
    
    # Check 3: Does response contain key numbers/facts from context?
    # Extract numbers from both and see if response numbers appear in context
    context_numbers = set(re.findall(r'\d+', context_lower))
    response_numbers = set(re.findall(r'\d+', response_lower))
    
    # Numbers in response should mostly come from context
    if response_numbers:
        numbers_from_context = response_numbers.intersection(context_numbers)
        number_grounding = len(numbers_from_context) / len(response_numbers)
    else:
        number_grounding = 1.0  # No numbers to check
    
    # Check 4: Does response cite sources?
    cites_sources = any(phrase in response_lower for phrase in [
        "according to",
        "handbook",
        "policy",
        "document",
        "states that",
        "mentioned in",
    ])
    
    # Overall grounding assessment
    is_grounded = (
        not admitted_uncertainty and  # Didn't say "I don't know"
        not hedging_detected and      # Isn't guessing
        number_grounding >= 0.5 and   # Numbers come from context
        cites_sources                  # References source documents
    )
    
    return {
        "is_grounded": is_grounded,
        "admitted_uncertainty": admitted_uncertainty,
        "hedging_detected": hedging_detected,
        "number_grounding_score": number_grounding,
        "cites_sources": cites_sources
    }


def apply_guardrails(
    response: str, 
    context: str, 
    has_sufficient_context: bool
) -> tuple[str, bool]:
    """
    Apply all guardrails and potentially modify the response.
    
    Returns:
        - Final response (possibly modified)
        - Boolean indicating if response is grounded/safe
    """
    
    # If we didn't have enough context to begin with, use fallback
    if not has_sufficient_context:
        fallback = (
            "I don't have enough information in the available documents "
            "to answer this question accurately."
        )
        return fallback, False
    
    # Check grounding of the response
    grounding = check_response_grounding(response, context)
    
    # If LLM admitted uncertainty, that's actually good (honest)
    if grounding["admitted_uncertainty"]:
        return response, False  # Not grounded but honest
    
    # If heavily hedging without citations, add a disclaimer
    if grounding["hedging_detected"] and not grounding["cites_sources"]:
        disclaimer = (
            "\n\n⚠️ Note: This response may not be fully supported by "
            "the available documents. Please verify with HR or the relevant team."
        )
        return response + disclaimer, False
    
    return response, grounding["is_grounded"]