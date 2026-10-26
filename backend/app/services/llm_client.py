import os
import httpx
from typing import Optional

def call_live_llm(
    prompt: str,
    system_prompt: str = "You are an objective financial investment intelligence research assistant. Do not give direct buy/sell financial advice."
) -> Optional[str]:
    """
    Attempts to call live OpenAI or Gemini API if environment variables are set.
    Smoothly falls back to None if offline, unconfigured, or timed out.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if openai_key:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 500
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content")
                    if content:
                        return content.strip()
        except Exception:
            pass

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            with httpx.Client(timeout=5.0) as client:
                res = client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUser Request: {prompt}"}]}
                        ],
                        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500}
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and parts[0].get("text"):
                            return parts[0]["text"].strip()
        except Exception:
            pass

    return None
