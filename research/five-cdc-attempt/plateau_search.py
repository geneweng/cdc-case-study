#!/usr/bin/env python3
"""Exhaust repair using neutral moves on a complete cubic graph order.

This tests existence of a nonincreasing path, not a bound on its length.
All plateau searches use GL(3,2) orbits; witnesses retain actual flow moves.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
import networkx as nx
import explore as x
from native_repair import run_graph
from verify_lex_trap import circuits_dfs, defects, valid_flow

HERE = Path(__file__).parent


def verify_escape(n, edges, witness):
    cs = set(circuits_dfs(n, edges))
    f = witness["initial_flow"].copy()
    valid_flow(n, edges, f)
    ds = defects(n, edges, f)
    initial = min(ds), sum(ds)
    assert initial[0] > 0
    neighbors = set()
    histogram = Counter()
    for c in cs:
        for a in range(1, 8):
            if a in {f[e] for e in c}:
                continue
            g = f.copy()
            for e in c:
                g[e] ^= a
            gd = defects(n, edges, g)
            p = min(gd), sum(gd)
            assert p >= initial
            neighbors.add(tuple(g))
            histogram[str(p)] += 1
    assert len(neighbors) == sum(histogram.values())
    path = [initial]
    for i, move in enumerate(witness["moves"]):
        c, a = move["circuit_edges"], move["added_value"]
        assert tuple(sorted(c)) in cs and a not in {f[e] for e in c}
        for e in c:
            f[e] ^= a
        valid_flow(n, edges, f)
        ds = defects(n, edges, f)
        value = min(ds), sum(ds)
        assert value == initial if i < len(witness["moves"]) - 1 else value < initial
        path.append(value)
    assert len(witness["moves"]) == witness["neutral_distance"] + 1
    return {"actual_move_path_independently_verified": True, "potentials": path,
            "final_flow": f, "circuits_enumerated_by_dfs": len(cs),
            "strict_neighbors_independently_checked": len(neighbors),
            "neighbor_potential_histogram": dict(sorted(histogram.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", type=int, default=16)
    args = parser.parse_args()
    compiler = shutil.which("clang++") or shutil.which("g++")
    geng = shutil.which("geng") or shutil.which("nauty-geng")
    if not compiler or not geng:
        raise SystemExit("A C++17 compiler and nauty geng are required.")
    start = time.monotonic()
    out = {"date": "2026-09-29", "vertices": args.order,
           "scope": "All connected bridgeless simple cubic graphs of this order, all NZ flow orbits.",
           "criterion": "Every positive-potential neutral component has an exit to smaller potential.",
           "geng_version": subprocess.check_output([geng, "-version"], text=True).strip(),
           "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
           "graphs": [], "counterexample": None, "complete_order": False}
    with tempfile.TemporaryDirectory(prefix="cdc-plateau-") as tmp:
        binary = Path(tmp) / "plateau"
        subprocess.run([compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
                        str(HERE / "plateau_native.cpp"), "-o", str(binary)], check=True)
        # Small completed graph records check that the shared enumeration is unchanged.
        references = json.loads((HERE / "exhaustive_repair_results.json").read_text())["graphs"]
        for old in [r for r in references if r["vertices"] <= 10]:
            r = run_graph(binary, old["vertices"], old["edges"])
            for k in ("2", "3"):
                assert r["nz_orbits_by_rank"][k] == old["nz_orbits_by_rank"].get(k, 0)
            assert r["bad_orbits_checked"] == old["bad_orbits_checked"]
            assert not r["counterexample"] and r["strict_local_minima"] == 0
        out["small_reference_graphs_checked"] = sum(r["vertices"] <= 10 for r in references)
        lines = subprocess.check_output([geng, "-cq", "-d3", "-D3", str(args.order)]).splitlines()
        out["connected_cubic_graphs_generated"] = len(lines)
        print("Generated", len(lines), "graphs", flush=True)
        for i, line in enumerate(lines):
            g = nx.from_graph6_bytes(line)
            if list(nx.bridges(g)):
                continue
            edges = sorted(tuple(sorted(e)) for e in g.edges())
            r = run_graph(binary, args.order, edges)
            r.update({"graph6": line.decode(), "edges": edges, "geng_index": i})
            if r["longest_escape"]:
                r["escape_verification"] = verify_escape(args.order, edges, r["longest_escape"])
            out["graphs"].append(r)
            if r["counterexample"]:
                out["counterexample"] = {"vertices": args.order, "edges": edges,
                                         **r["counterexample"], "quotient_plateau_size": r["closed_plateau_orbits"]}
                break
            if (i + 1) % 250 == 0:
                print("Graph index", i + 1, "/", len(lines), "local minima",
                      sum(g["strict_local_minima"] for g in out["graphs"]),
                      "elapsed", round(time.monotonic() - start, 1), flush=True)
        out["complete_order"] = out["counterexample"] is None
        out["elapsed_seconds"] = round(time.monotonic() - start, 3)
        out["bridgeless_graphs_checked"] = len(out["graphs"])
        out["flow_orbits_checked"] = sum(sum(g["nz_orbits_by_rank"].values()) for g in out["graphs"])
        out["bad_orbits_checked"] = sum(g["bad_orbits_checked"] for g in out["graphs"])
        out["strict_local_minima"] = sum(g["strict_local_minima"] for g in out["graphs"])
        hist = Counter()
        for g in out["graphs"]:
            hist.update(g["escape_neutral_distance_histogram"])
        out["escape_neutral_distance_histogram"] = dict(hist)
        (HERE / f"plateau_census_{args.order}.json").write_text(json.dumps(out, indent=2) + "\n")
        print({k: v for k, v in out.items() if k not in ("graphs", "counterexample")}, flush=True)
        if out["counterexample"]:
            print("CANDIDATE CLOSED BAD PLATEAU: independent verification required", flush=True)


if __name__ == "__main__":
    main()
