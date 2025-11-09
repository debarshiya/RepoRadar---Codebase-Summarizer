"""
Build a dependency graph using AST-extracted imports and function calls.
Export an interactive HTML via pyvis.
"""
from typing import List, Dict
import networkx as nx
from pyvis.network import Network
from pathlib import Path

def build_graph(parsed_files: List[Dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    for pf in parsed_files:
        file_node = f"file:{Path(pf['path']).name}"
        G.add_node(file_node, label=Path(pf["path"]).name, type="file")
        # imports
        for imp in pf.get("imports", []):
            imp_node = f"mod:{imp.split('.')[0]}"
            G.add_node(imp_node, label=imp, type="module")
            G.add_edge(file_node, imp_node, kind="imports")
        # functions
        for fn in pf.get("functions", []):
            fn_node = f"func:{Path(pf['path']).name}::{fn['name']}"
            G.add_node(fn_node, label=fn['name'], type="function")
            G.add_edge(file_node, fn_node, kind="defines")
            # calls -> link to function nodes if present, else to modules
            for call in fn.get("calls", []):
                # naive mapping: if call contains dot assume module.func else plain name
                if "." in call:
                    target = f"call:{call}"
                else:
                    target = f"call:{call}"
                G.add_node(target, label=call, type="call")
                G.add_edge(fn_node, target, kind="calls")
    return G

def export_pyvis(G: nx.DiGraph, out_path: Path = Path("reporadar_graph.html")):
    net = Network(height="800px", width="100%", notebook=False, directed=True)
    for n, d in G.nodes(data=True):
        lbl = d.get("label", n)
        group = d.get("type", "node")
        net.add_node(n, label=lbl, title=str(d), group=group)
    for u, v, dd in G.edges(data=True):
        title = dd.get("kind", "")
        net.add_edge(u, v, title=title)
    net.toggle_physics(True)
    net.write_html(str(out_path), notebook=False)
    # net.show(str(out_path))
    return out_path