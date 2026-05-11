"""
Placement Reality Check — Gemini LLM Client with retry + model fallback.
"""

import time
from google import genai
from config import GEMINI_API_KEY, MODELS, MAX_RETRIES, RETRY_DELAY

client = genai.Client(api_key=GEMINI_API_KEY)


def llm_call(prompt: str) -> str:
    """
    Call Gemini API with retry logic and model fallback.
    Retries up to MAX_RETRIES times per model, with exponential backoff.
    Falls back to the next model if all retries fail.
    """
    last_error = None

    for model in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                time.sleep(1)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text

            except Exception as e:
                last_error = e
                error_str = str(e)
                print(f"⚠️ {model} attempt {attempt + 1}/{MAX_RETRIES} failed: {error_str}")

                if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"   Non-retryable error, trying next model...")
                    break

        print(f"❌ All retries exhausted for {model}")

    print(f"❌ All models failed. Last error: {last_error}")
    return "⚠️ AI model is currently unavailable. Please try again in a few seconds."
