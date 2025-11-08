"""
Parse a Python repository using ast to extract:
- file-level code text
- function and class definitions with source snippet
- imports per file
- (best-effort) function calls inside functions
"""

import ast
import asttokens
from pathlib import Path
from typing import Dict, List, Tuple

def find_py_files(repo_path: Path) -> List[Path]:
    return sorted([p for p in repo_path.rglob("*.py") if "venv" not in str(p) and ".git" not in str(p)])

def parse_file(path: Path) -> Dict:
    source = path.read_text(encoding="utf-8")
    try:
        atok = asttokens.ASTTokens(source, parse=True)
        tree = atok.tree
    except SyntaxError:
        # fallback: return raw file
        return {"path": str(path), "source": source, "functions": [], "classes": [], "imports": []}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # import names
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            else:
                module = node.module or ""
                for n in node.names:
                    imports.append(f"{module}.{n.name}" if module else n.name)
        elif isinstance(node, ast.FunctionDef):
            start, end = atok.get_text_range(node)
            snippet = source[start:end]
            name = node.name
            calls = _extract_calls(node)
            functions.append({"name": name, "start": node.lineno, "end": node.end_lineno if hasattr(node, "end_lineno") else None, "snippet": snippet, "calls": calls})
        elif isinstance(node, ast.ClassDef):
            start, end = atok.get_text_range(node)
            snippet = source[start:end]
            classes.append({"name": node.name, "start": node.lineno, "end": node.end_lineno if hasattr(node, "end_lineno") else None, "snippet": snippet})

    return {"path": str(path), "source": source, "functions": functions, "classes": classes, "imports": list(set(imports))}

def _extract_calls(func_node: ast.FunctionDef) -> List[str]:
    calls = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            # try to get a name
            func = node.func
            if isinstance(func, ast.Name):
                calls.append(func.id)
            elif isinstance(func, ast.Attribute):
                # e.g., module.func or self.func
                attr_chain = []
                cur = func
                while isinstance(cur, ast.Attribute):
                    attr_chain.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    attr_chain.append(cur.id)
                calls.append(".".join(reversed(attr_chain)))
    return list(set(calls))