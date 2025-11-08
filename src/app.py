"""
Small Streamlit app to run autodoc over a local repo and explore results.
Usage: streamlit run src/app.py
"""
import streamlit as st
from pathlib import Path
from parser import find_py_files, parse_file
from chunker import chunk_by_functions, chunk_text
from summarizer import summarize_chunks
from graph import build_graph, export_pyvis
from utils import save_json, load_json
import os
import shutil
import stat
from git import Repo

EXAMPLES_DIR = "examples"

def handle_remove_readonly(func, path, exc):
    """Fix for Windows read-only files (WinError 5) when deleting folder."""
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise
    
def clone_repo(repo_url: str) -> str:
    """Clone a GitHub repository into the examples folder, replacing existing repos."""
    if not os.path.exists(EXAMPLES_DIR):
        os.makedirs(EXAMPLES_DIR)
    else:
        # Delete all existing repos inside examples/
        for folder in os.listdir(EXAMPLES_DIR):
            folder_path = os.path.join(EXAMPLES_DIR, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path, onerror=handle_remove_readonly)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    dest_path = os.path.join(EXAMPLES_DIR, repo_name)

    try:
        Repo.clone_from(repo_url, dest_path)
        return dest_path
    except Exception as e:
        raise RuntimeError(f"Failed to clone repository: {e}")

# =============================
# Streamlit UI
# =============================
st.set_page_config(page_title="AutoDoc - Codebase Summarizer", layout="wide")
st.title("AutoDoc - Codebase Summarizer")

st.markdown(
    """
    Paste a **GitHub repository link** below to automatically clone it into the `examples/` folder.
    All existing functionality (summarizer, chunker, parser, graph) remains unchanged.
    """
)

# ----------------------------
# GitHub repository cloning
# ----------------------------
repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/username/repo-name")

# if st.button("Clone Repository"):
#     if repo_url.strip():
#         with st.spinner("Cloning repository..."):
#             try:
#                 repo_path = clone_repo(repo_url.strip())
#                 st.success(f"Repository cloned successfully to `{repo_path}`")

#                 # ===================================================
#                 # Use 'repo_path' with your existing functionality
#                 # ===================================================
#                 # Example placeholders for your current workflow:
#                 # parsed_data = parser.parse_repo(repo_path)
#                 # chunks = chunker.create_chunks(parsed_data)
#                 # summaries = summarizer.summarize(chunks)
#                 # graph.generate(parsed_data)
#                 #
#                 # Nothing else needs to be changed — just pass 'repo_path'.

#             except Exception as e:
#                 st.error(f"{e}")
#     else:
#         st.warning("Please enter a valid GitHub repository URL.")

# After a repo is successfully cloned:
if st.button("Clone Repository"):
    if repo_url.strip():
        with st.spinner("Cloning repository..."):
            try:
                repo_path = clone_repo(repo_url.strip())
                st.success(f"Repository cloned successfully to `{repo_path}`")
                st.session_state["last_repo_path"] = repo_path
            except Exception as e:
                st.error(f"{e}")

# ----------------------------
# Show already cloned repositories
# ----------------------------
st.markdown("### Already Cloned Repositories")
if os.path.exists(EXAMPLES_DIR):
    repos = os.listdir(EXAMPLES_DIR)
    if repos:
        st.write(repos)
    else:
        st.write("No repositories cloned yet.")

st.set_page_config(layout="wide", page_title="AutoDoc")

st.title("AutoDoc — Codebase Summarizer")

# repo_path = st.text_input("Local repo path", value="examples/micrograd")
default_path = st.session_state.get("last_repo_path", "examples/micrograd")
repo_path = st.text_input("Local repo path", value=default_path)
if st.button("Analyze repository"):
    p = Path(repo_path)
    if not p.exists():
        st.error("Path not found")
    else:
        files = find_py_files(p)
        st.write(f"Found {len(files)} python files")
        parsed = []
        for f in files:
            parsed.append(parse_file(f))
        st.session_state["parsed"] = parsed
        save_json(Path(".autodoc_cache/parsed.json"), parsed)
        st.success("Parsed files — you can now generate summaries and graph")

if "parsed" not in st.session_state:
    parsed_cache = Path(".autodoc_cache/parsed.json")
    if parsed_cache.exists():
        st.session_state["parsed"] = load_json(parsed_cache)

if st.session_state.get("parsed"):
    parsed = st.session_state["parsed"]
    col1, col2 = st.columns([1,2])
    with col1:
        st.header("Files")
        file_select = st.selectbox("Choose a file", [p["path"] for p in parsed])
        file_obj = next(p for p in parsed if p["path"] == file_select)
        st.subheader("Imports")
        st.write(file_obj.get("imports", []))
        st.subheader("Functions")
        for fn in file_obj.get("functions", []):
            st.markdown(f"- **{fn['name']}** (calls: {', '.join(fn.get('calls',[]))})")
    with col2:
        st.header("Summaries")
        if st.button("Summarize selected file"):
            # only chunk the file selected in dropdown
            chunks = chunk_by_functions(file_obj)
            for ch in chunks:
                ch["file_path"] = file_obj["path"]
            results = summarize_chunks(chunks, repo_prefix=Path(repo_path).name)
            st.session_state["summaries"] = results
            save_json(Path(".autodoc_cache/summaries.json"), results)
            st.success("Summaries generated for selected file")
        if st.button("Summarize all"):
            # create chunks from parsed files
            all_chunks = []
            mapping = []
            for pf in parsed:
                chunks = chunk_by_functions(pf)
                for ch in chunks:
                    ch["file_path"] = pf["path"] 
                    all_chunks.append(ch)
            results = summarize_chunks(all_chunks, repo_prefix=Path(repo_path).name)
            st.session_state["summaries"] = results
            save_json(Path(".autodoc_cache/summaries.json"), results)
            st.success("Summaries generated for all files in repo")
        if st.session_state.get("summaries"):
            for item in st.session_state["summaries"]:
                ch = item["chunk"]
                summary = item["summary"]
                st.subheader(f"{ch['type']} — {ch.get('name')}")
                st.markdown(f"**One-liner:** {summary.get('one_liner')}")
                st.markdown(f"**Description:** {summary.get('description')}")
                st.markdown(f"**Docstring suggestion:** `{summary.get('docstring')}`")
                if summary.get("notes"):
                    st.markdown(f"**Notes:** {summary.get('notes')}")
                with st.expander("View code snippet"):
                    st.code(ch["text"][:5000], language="python")
        else:
            st.info("No summaries yet. Click a Summarize Button.")
    st.header("Dependency graph")
    if st.button("Build graph"):
        G = build_graph(parsed)
        path = export_pyvis(G, out_path=Path(".autodoc_cache/autodoc_graph.html"))
        st.write("Graph exported to", path)
        # display inline
        html = open(path, "r", encoding="utf-8").read()
        st.components.v1.html(html, height=800, scrolling=True)