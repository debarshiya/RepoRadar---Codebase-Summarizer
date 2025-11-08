"""
Chunk code/text into manageable pieces for LLM summarization.
We chunk by functions first, then by file-level sliding windows (by lines or chars).
"""
from typing import List, Dict
import re

DEFAULT_CHUNK_CHARS = 3000  # tuneable

def chunk_by_functions(parsed_file: Dict) -> List[Dict]:
    chunks = []
    for fn in parsed_file.get("functions", []):
        chunks.append({"type": "function", "name": fn["name"], "text": fn["snippet"], "meta": {"start": fn["start"], "end": fn["end"]}, "file_path": parsed_file["path"]})
    for cl in parsed_file.get("classes", []):
        chunks.append({"type": "class", "name": cl["name"], "text": cl["snippet"], "meta": {"start": cl["start"], "end": cl["end"]}, "file_path": parsed_file["path"]})
    # fallback: whole file chunk
    if not chunks:
        chunks.append({"type": "file", "name": parsed_file["path"], "text": parsed_file["source"], "meta": {}, "file_path": parsed_file["path"]})
    return chunks

def chunk_text(text: str, max_chars: int = DEFAULT_CHUNK_CHARS) -> List[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    # try split by blank line boundaries
    parts = re.split(r"\n{2,}", text)
    out = []
    current = ""
    for p in parts:
        if len(current) + len(p) + 2 <= max_chars:
            current += (p + "\n\n")
        else:
            if current:
                out.append(current)
            if len(p) <= max_chars:
                current = p + "\n\n"
            else:
                # split by lines
                lines = p.splitlines(True)
                cur2 = ""
                for L in lines:
                    if len(cur2) + len(L) <= max_chars:
                        cur2 += L
                    else:
                        out.append(cur2)
                        cur2 = L
                if cur2:
                    current = cur2
                else:
                    current = ""
    if current:
        out.append(current)
    return out