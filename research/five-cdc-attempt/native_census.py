#!/usr/bin/env python3
"""Exhaust the repair lemma on a complete simple cubic graph order, default 16."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
import networkx as nx
from native_repair import run_graph
from exhaustive_repair import certify_trap

HERE = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", type=int, default=16)
    args = parser.parse_args()
    compiler = shutil.which("clang++") or shutil.which("g++")
    geng = shutil.which("geng") or shutil.which("nauty-geng")
    if not compiler or not geng:
        raise SystemExit("A C++17 compiler and nauty geng are required.")
    assert args.order % 2 == 0 and 4 <= args.order <= 30
    out = {"date": "2026-09-29", "vertices": args.order,
           "scope": "Connected bridgeless simple cubic graphs; all flow classes modulo GL(3,2).",
           "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
           "geng_version": subprocess.check_output([geng, "-version"], text=True).strip(),
           "graphs": [], "counterexample": None, "complete_order": False}
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="cdc-census-") as tmp:
        binary = Path(tmp) / "repair"
        subprocess.run([compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
                        str(HERE / "repair_native.cpp"), "-o", str(binary)], check=True)
        generated = subprocess.check_output([geng, "-cq", "-d3", "-D3", str(args.order)]).splitlines()
        out["connected_cubic_graphs_generated"] = len(generated)
        print("Generated", len(generated), "graphs", flush=True)
        for i, line in enumerate(generated):
            graph = nx.from_graph6_bytes(line)
            if list(nx.bridges(graph)):
                continue
            edges = sorted(tuple(sorted(e)) for e in graph.edges())
            result = run_graph(binary, args.order, edges)
            result.update({"graph6": line.decode(), "edges": edges, "geng_index": i})
            out["graphs"].append(result)
            if result["counterexample"]:
                out["counterexample"] = certify_trap(args.order, edges, result["counterexample"]["flow"])
                (HERE / "lex_census_trap_certificate.json").write_text(json.dumps(out["counterexample"], indent=2) + "\n")
                break
            if (i + 1) % 250 == 0:
                print("Checked generator index", i + 1, "/", len(generated),
                      "elapsed", round(time.monotonic() - start, 1), flush=True)
        out["complete_order"] = out["counterexample"] is None
        out["elapsed_seconds"] = round(time.monotonic() - start, 3)
        out["bridgeless_graphs_checked"] = len(out["graphs"])
        out["flow_orbits_checked"] = sum(sum(g["nz_orbits_by_rank"].values()) for g in out["graphs"])
        out["bad_orbits_checked"] = sum(g["bad_orbits_checked"] for g in out["graphs"])
        (HERE / f"native_census_{args.order}.json").write_text(json.dumps(out, indent=2) + "\n")
        print({k: v for k, v in out.items() if k not in ("graphs", "counterexample")}, flush=True)
        if out["counterexample"]:
            print("LEXICOGRAPHIC REPAIR COUNTEREXAMPLE FOUND", flush=True)


if __name__ == "__main__":
    main()
