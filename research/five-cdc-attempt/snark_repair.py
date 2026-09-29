#!/usr/bin/env python3
"""Generate the two 18-vertex girth-five snarks and exhaust their flow orbits.

Uses geng -c -d3 -D3 -t -f 18, exact edge-coloring backtracking, and cut checks.
This is an additional finite test of the proposed lexicographic repair lemma.
"""
import json
import itertools
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import networkx as nx
from exhaustive_repair import OrbitSearch, certify_trap

HERE = Path(__file__).parent


def three_edge_colorable(n, edges):
    incident = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        incident[u].append(i)
        incident[v].append(i)
    used, assigned = [0] * n, [0] * len(edges)
    # Color symmetry allows these three incident edges to be fixed.
    for color, e in zip((1, 2, 4), incident[0]):
        u, v = edges[e]
        used[u] |= color
        used[v] |= color
        assigned[e] = color

    def visit(remaining):
        if not remaining:
            return True
        choice, choices, size = None, 0, 4
        for e in remaining:
            u, v = edges[e]
            possible = 7 & ~(used[u] | used[v])
            count = possible.bit_count()
            if not count:
                return False
            if count < size:
                choice, choices, size = e, possible, count
        u, v = edges[choice]
        tail = [e for e in remaining if e != choice]
        while choices:
            color = choices & -choices
            choices ^= color
            used[u] |= color
            used[v] |= color
            assigned[choice] = color
            if visit(tail):
                return True
            used[u] ^= color
            used[v] ^= color
            assigned[choice] = 0
        return False

    result = visit([e for e, a in enumerate(assigned) if not a])
    if result:
        assert all({assigned[e] for e in es} == {1, 2, 4} for es in incident)
    return result


def cyclically_four_edge_connected(n, edges):
    """In a bridgeless cubic graph, a nontrivial cut of size <=3 is cyclic."""
    adjacency = [0] * n
    for u, v in edges:
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    for size in (2, 3):
        for removed in itertools.combinations(edges, size):
            adj = adjacency.copy()
            for u, v in removed:
                adj[u] ^= 1 << v
                adj[v] ^= 1 << u
            seen, pending = 1, 1
            while pending:
                bit = pending & -pending
                pending ^= bit
                new = adj[bit.bit_length() - 1] & ~seen
                seen |= new
                pending |= new
            if 1 < seen.bit_count() < n - 1:
                return False
    return True


def main():
    geng = shutil.which("geng") or shutil.which("nauty-geng")
    if not geng:
        raise SystemExit("nauty geng is required")
    version = subprocess.run([geng, "-version"], check=True, capture_output=True, text=True).stdout.strip()
    process = subprocess.run([geng, "-cq", "-d3", "-D3", "-t", "-f", "18"],
                             capture_output=True, check=True)
    lines = process.stdout.splitlines()
    graphs = []
    for line in lines:
        g = nx.from_graph6_bytes(line)
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        if (list(nx.bridges(g)) or three_edge_colorable(18, edges)
                or not cyclically_four_edge_connected(18, edges)):
            continue
        graphs.append((line.decode(), edges))
    assert len(lines) == 455 and len(graphs) == 2
    out = {"date": "2026-09-29", "python": platform.python_version(), "networkx": nx.__version__,
           "geng_version": version, "generated_connected_cubic_girth_at_least_five_graphs": len(lines),
           "cyclically_four_edge_connected_non_three_edge_colorable_graphs": len(graphs), "graphs": [],
           "counterexample": None}
    start = time.monotonic()
    print("Generated", len(lines), "graphs; exact colorability filter retained", len(graphs), flush=True)
    for code, edges in graphs:
        print("Exhausting", code, flush=True)
        result = OrbitSearch(18, edges).run()
        result.update({"graph6": code, "vertices": 18, "edges": edges})
        out["graphs"].append(result)
        if result["counterexample"]:
            out["counterexample"] = certify_trap(18, edges, result["counterexample"]["flow"])
            (HERE / "snark_lex_trap_certificate.json").write_text(json.dumps(out["counterexample"], indent=2) + "\n")
        out["elapsed_seconds"] = round(time.monotonic() - start, 3)
        (HERE / "snark_repair_results.json").write_text(json.dumps(out, indent=2) + "\n")
        print("Checked", result["nz_orbits_by_rank"], "NZ flow orbits; bad:", result["bad_orbits_checked"],
              "trap:", bool(result["counterexample"]), "elapsed:", out["elapsed_seconds"], flush=True)
        if result["counterexample"]:
            break


if __name__ == "__main__":
    main()
