#!/usr/bin/env python3
"""Cross-check the C++ engine, then exhaust the six 20-vertex girth-five snarks.

Requires Python/NetworkX, geng, and a C++17 compiler. The temporary executable
is compiled with assertions enabled and removed automatically after use.
"""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
import networkx as nx
import explore as x
from exhaustive_repair import gaussian, certify_trap
from snark_repair import three_edge_colorable, cyclically_four_edge_connected

HERE = Path(__file__).parent


def run_graph(binary, n, edges):
    basis = x.BASE.cycle_basis(n, edges)
    masks = [sum(1 << e for e in c) for c in basis]
    lines = [f"{n} {len(edges)} {len(basis)}"]
    lines += [f"{u} {v}" for u, v in edges]
    lines += [str(b) for b in masks]
    proc = subprocess.run([str(binary)], input="\n".join(lines) + "\n", text=True,
                          capture_output=True, check=True)
    result = json.loads(proc.stdout)
    if result["counterexample"] is None:
        assert result["exhausted_all_flow_orbits"]
        for k in (2, 3):
            assert result["subspaces_enumerated_by_rank"][str(k)] == gaussian(len(basis), k)
    result["nz_labeled_flows_represented"] = (
        42 * result["nz_orbits_by_rank"]["2"] + 168 * result["nz_orbits_by_rank"]["3"])
    return result


def reference_checks(binary):
    records = []
    for name in ("exhaustive_repair_results.json", "snark_repair_results.json"):
        records += json.loads((HERE / name).read_text())["graphs"]
    start = time.monotonic()
    for i, old in enumerate(records):
        new = run_graph(binary, old["vertices"], old["edges"])
        for field in ("cycle_dimension", "circuit_count", "subspaces_enumerated_by_rank",
                      "bad_orbits_checked", "exhausted_all_flow_orbits", "counterexample"):
            assert new[field] == old[field], (i, field, new[field], old[field])
        for k in ("2", "3"):
            assert new["nz_orbits_by_rank"][k] == old["nz_orbits_by_rank"].get(k, 0)
        if (i + 1) % 100 == 0:
            print("Reference cross-check:", i + 1, "/", len(records), flush=True)
    return {"graphs_crosschecked": len(records), "all_counts_and_outcomes_agree": True,
            "elapsed_seconds": round(time.monotonic() - start, 3)}


def main():
    compiler = shutil.which("clang++") or shutil.which("g++")
    geng = shutil.which("geng") or shutil.which("nauty-geng")
    if not compiler or not geng:
        raise SystemExit("A C++17 compiler and nauty geng are required.")
    out = {"date": "2026-09-29", "python": platform.python_version(), "networkx": nx.__version__,
           "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
           "geng_version": subprocess.check_output([geng, "-version"], text=True).strip(),
           "scope": "All flow classes on the six cyclically 4-edge-connected 20-vertex snarks of girth >=5.",
           "graphs": [], "counterexample": None}
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="cdc-repair-") as tmp:
        binary = Path(tmp) / "repair"
        subprocess.run([compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
                        str(HERE / "repair_native.cpp"), "-o", str(binary)], check=True)
        out["reference_verification"] = reference_checks(binary)
        print("Native/Python agreement:", out["reference_verification"], flush=True)
        generated = subprocess.check_output([geng, "-cq", "-d3", "-D3", "-t", "-f", "20"]).splitlines()
        graphs = []
        for i, line in enumerate(generated):
            graph = nx.from_graph6_bytes(line)
            edges = sorted(tuple(sorted(e)) for e in graph.edges())
            if (not list(nx.bridges(graph)) and not three_edge_colorable(20, edges)
                    and cyclically_four_edge_connected(20, edges)):
                graphs.append((line.decode(), edges))
        assert len(generated) == 5783 and len(graphs) == 6
        out["connected_cubic_girth_five_graphs_generated"] = len(generated)
        out["qualifying_snarks"] = len(graphs)
        print("Generated", len(generated), "graphs; retained", len(graphs), "snarks", flush=True)
        for i, (code, edges) in enumerate(graphs):
            result = run_graph(binary, 20, edges)
            result.update({"graph6": code, "edges": edges})
            out["graphs"].append(result)
            if result["counterexample"]:
                out["counterexample"] = certify_trap(20, edges, result["counterexample"]["flow"])
                (HERE / "lex_native_trap_certificate.json").write_text(json.dumps(out["counterexample"], indent=2) + "\n")
            out["elapsed_seconds"] = round(time.monotonic() - start, 3)
            (HERE / "native_repair_results.json").write_text(json.dumps(out, indent=2) + "\n")
            print("Snark", i + 1, "NZ orbits", result["nz_orbits_by_rank"],
                  "bad", result["bad_orbits_checked"], "trap", bool(result["counterexample"]),
                  "elapsed", out["elapsed_seconds"], flush=True)
            if out["counterexample"]:
                break


if __name__ == "__main__":
    main()
