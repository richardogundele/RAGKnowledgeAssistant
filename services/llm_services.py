"""
LLM service using Ollama.
Sends prompts to a locally-running LLM and gets responses.

Why Ollama:
- Runs completely locally (no API keys, no costs, no data leaving your machine)
- Good for privacy-sensitive consulting environments
- Easy to swap models (llama3.2, mistral, etc.)

Make sure Ollama is running: `ollama serve`
And you have a model: `ollama pull llama3.2`
"""

import ollama

from config import OLLAMA_MODEL, LLM_TEMPERATURE


def generate_response(system_prompt: str, user_prompt: str) -> str:
    """
    Send a prompt to Ollama and get a response.
    
    Args:
        system_prompt: Instructions for how the LLM should behave
        user_prompt: The actual question with context
    
    Returns:
        The LLM's response text
    """
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "temperature": LLM_TEMPERATURE,  # Low = more factual, less creative
            }
        )
        
        # Extract the text from ollama's response
        return response["message"]["content"]
    
    except Exception as e:
        # If Ollama isn't running or model isn't available
        return f"Error connecting to LLM: {str(e)}. Make sure Ollama is running."


def check_ollama_status() -> dict:
    """
    Check if Ollama is running and the model is available.
    Useful for health checks.
    """
    try:
        # List available models
        models = ollama.list()
        model_names = [m["name"] for m in models.get("models", [])]
        
        # Check if our configured model is available
        model_available = any(OLLAMA_MODEL in name for name in model_names)
        
        return {
            "status": "connected",
            "available_models": model_names,
            "configured_model": OLLAMA_MODEL,
            "model_ready": model_available
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "configured_model": OLLAMA_MODEL,
            "model_ready": False
        }