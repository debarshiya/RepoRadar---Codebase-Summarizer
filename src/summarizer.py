"""
LLM summarizer wrapper + caching. Uses OpenAI python package as example.
"""
import os
import time
from pathlib import Path
from typing import Dict, Optional
from utils import save_json, load_json
from tqdm import tqdm

# Lazy import to avoid failing if openai not installed during linting
try:
    import openai
except Exception:
    openai = None

CACHE_DIR = Path(".autodoc_cache/summaries")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.environ.get("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")

SYSTEM_PROMPT = """You are RepoRadar: an assistant that produces concise developer-friendly summaries and docstrings.
Rules:
- Provide a short one-line summary ( <= 20 words).
- Provide a 2-4 sentence description of purpose.
- List inputs, outputs, side-effects if clear.
- Suggest a short one-line docstring string the function or file.
- If code appears incomplete or suspicious, add a note.
Output JSON with keys: one_liner, description, inputs_outputs, docstring, notes.
"""

def _client():
    if openai is None:
        raise RuntimeError("openai package not installed")
    openai.api_key = API_KEY
    return openai

def _cache_path_for(key: str) -> Path:
    safe = key.replace("/", "_").replace(" ", "_")[:200]
    return CACHE_DIR / f"{safe}.json"

def summarize_text(text: str, key: str, max_retries: int = 3, temperature: float = 0.0) -> Dict:
    """
    Summarize text using the configured LLM. Uses caching by key (e.g., file path + start line)
    """
    cp = _cache_path_for(key)
    cached = load_json(cp)
    if cached:
        return cached
    client = _client()
    prompt = SYSTEM_PROMPT + "\n\nCode:\n" + text + "\n\nRespond only with valid JSON."
    for attempt in range(max_retries):
        try:
            resp = client.ChatCompletion.create(
                model=MODEL,
                messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":text}],
                temperature=temperature,
                max_tokens=600
            )
            out = resp["choices"][0]["message"]["content"].strip()
            # attempt parse JSON
            import json
            parsed = json.loads(out)
            save_json(cp, parsed)
            # tiny delay to be polite
            time.sleep(0.2)
            return parsed
        except Exception as e:
            print("LLM error:", e)
            time.sleep(1 + attempt * 2)
    # fallback simple heuristic summary
    fallback = {"one_liner": text.strip().splitlines()[0][:80], "description": "Auto-generated fallback summary.", "inputs_outputs": [], "docstring": "", "notes": "fallback used"}
    save_json(cp, fallback)
    return fallback

def summarize_chunks(chunks, repo_prefix="repo"):
    results = []
    for i, ch in enumerate(tqdm(chunks)):
        key = f"{repo_prefix}_{ch.get('type')}_{ch.get('name')}_{i}"
        summary = summarize_text(ch["text"], key=key)
        results.append({"chunk": ch, "summary": summary})
    return results