"""
Maps to 01_Agent_Runner workflow.
Generic reusable AI caller for the LLM Gateway.
"""

import os
import re
import json
from backend.config_registry import CONFIG

def get_groq_client(api_key: str = ""):
    """Initializes and returns the Groq client securely."""
    try:
        from groq import Groq
        key = api_key or os.environ.get("GROQ_API_KEY", "")
        if not key:
            return None
        return Groq(api_key=key)
    except ImportError:
        return None

def run_agent(client, system: str, user_msg: str, max_tokens: int = 900, expect_json: bool = True):
    """Reusable API wrapper enforcing payload boundaries and JSON structure."""
    if client is None:
        err = {"error": "Groq client not initialised — check GROQ_API_KEY"}
        return err if expect_json else "⚠️ Groq client not initialised."
    try:
        resp = client.chat.completions.create(
            model=CONFIG["model"],
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user_msg}],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        content = resp.choices[0].message.content.strip()
        if not expect_json:
            return content
        clean = re.sub(r"