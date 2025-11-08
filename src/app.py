"""
Small Streamlit app to run autodoc over a local repo and explore results.
Usage: streamlit run src/app.py
"""
import streamlit as st
from pathlib import Path
from .parser import find_py_files, parse_file
from .chunker import chunk_by_functions, chunk_text
from .summarizer import summarize_chunks
from .graph import build_graph, export_pyvis
from .utils import save_json, load_json
import os

st.set_page_config(layout="wide", page_title="AutoDoc")

st.title("AutoDoc — Codebase Summarizer")

repo_path = st.text_input("Local repo path", value="examples/small_repo")
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
        if st.button("Summarize all"):
            # create chunks from parsed files
            all_chunks = []
            mapping = []
            for pf in parsed:
                chunks = chunk_by_functions(pf)
                for ch in chunks:
                    all_chunks.append(ch)
            results = summarize_chunks(all_chunks, repo_prefix=Path(repo_path).name)
            st.session_state["summaries"] = results
            save_json(Path(".autodoc_cache/summaries.json"), results)
            st.success("Summaries generated")
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
            st.info("No summaries yet. Click 'Summarize all'.")
    st.header("Dependency graph")
    if st.button("Build graph"):
        G = build_graph(parsed)
        path = export_pyvis(G, out_path=Path(".autodoc_cache/autodoc_graph.html"))
        st.write("Graph exported to", path)
        # display inline
        html = open(path, "r", encoding="utf-8").read()
        st.components.v1.html(html, height=800, scrolling=True)