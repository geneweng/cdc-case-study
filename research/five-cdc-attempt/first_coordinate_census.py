#!/usr/bin/env python3
"""Classify prescribed first coordinates; finite data do not prove 5-CDC.

Uses the already saved complete graph census through order 16 and the eight
specified 18/20-vertex snarks. Keeps every failed admissible first coordinate.
"""
from collections import Counter
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
from exhaustive_repair import gaussian

HERE = Path(__file__).parent


def run_graph(binary, n, edges):
    basis = x.BASE.cycle_basis(n, edges)
    lines = [f"{n} {len(edges)} {len(basis)}"]
    lines += [f"{u} {v}" for u, v in edges]
    lines += [str(sum(1 << e for e in c)) for c in basis]
    a = json.loads(subprocess.check_output([str(binary)], input="\n".join(lines)+"\n", text=True))
    for k in (2, 3):
        assert a["subspaces_enumerated_by_rank"][str(k)] == gaussian(len(basis), k)
    assert len(a["first_coordinates"]) == 1 << len(basis)
    assert sum(f["admissible_flows"] for f in a["first_coordinates"]) == (
        42*a["nz_orbits_by_rank"]["2"] + 168*a["nz_orbits_by_rank"]["3"])
    return a


def components(n, edges, mask, keep=True):
    adjacency = [[] for _ in range(n)]
    active = set(range(n)) if not keep else set()
    for i, (u, v) in enumerate(edges):
        if bool(mask >> i & 1) == keep:
            adjacency[u].append(v); adjacency[v].append(u)
            active.update((u, v))
    out = []
    while active:
        start = min(active); active.remove(start)
        stack = [start]; seen = [start]
        while stack:
            for v in adjacency[stack.pop()]:
                if v in active:
                    active.remove(v); stack.append(v); seen.append(v)
        out.append(sorted(seen))
    return out


def summarize(old, a):
    n, edges = old["vertices"], old["edges"]
    for k in ("2", "3"):
        assert a["nz_orbits_by_rank"][k] == old["nz_orbits_by_rank"].get(k, 0)
    bad = []; totals = Counter(); hist = Counter(); nonseparating_witness = None
    for f in a["first_coordinates"]:
        mask = f["support_mask"]
        hc = components(n, edges, mask, keep=False)
        fc = components(n, edges, mask)
        admitted = bool(f["admissible_flows"]); success = bool(f["successful_flows"])
        assert f["admissible_flows"] >= f["successful_flows"]
        totals["first_coordinates"] += 1
        totals["admissible_first_coordinates"] += admitted
        totals["successful_first_coordinates"] += success
        if len(hc) == 1:
            assert f["admissible_flows"] == f["successful_flows"]
            totals["nonseparating_first_coordinates"] += 1
            totals["successful_nonseparating_first_coordinates"] += success
            if success and nonseparating_witness is None:
                nonseparating_witness = f
        if admitted and not success:
            bad.append({**f, "complement_components": hc, "support_components": fc})
            hist[f"H={len(hc)},F={len(fc)}"] += 1
    return {"vertices": n, "graph6": old.get("graph6"), "edges": edges,
            "subspaces_enumerated_by_rank": a["subspaces_enumerated_by_rank"],
            "nz_orbits_by_rank": a["nz_orbits_by_rank"], "counts": dict(totals),
            "failed_admissible_first_coordinates": bad, "failure_component_histogram": dict(hist),
            "nonseparating_witness": nonseparating_witness}


def main():
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        raise SystemExit("C++17 compiler required")
    old = []
    for name in ("exhaustive_repair_results.json", "plateau_census_16.json",
                 "snark_repair_results.json", "native_repair_results.json"):
        old += json.loads((HERE / name).read_text())["graphs"]
    assert len(old) == 4469
    start = time.monotonic()
    out = {"date": "2026-09-29", "python": platform.python_version(), "networkx": nx.__version__,
           "scope": "All 4461 connected bridgeless simple cubic graphs through 16 vertices, plus the specified two 18-vertex and six 20-vertex snarks.",
           "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
           "graphs": []}
    with tempfile.TemporaryDirectory(prefix="cdc-first-coordinate-") as tmp:
        binary = Path(tmp) / "first_coordinate"
        subprocess.run([compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
                        str(HERE / "first_coordinate_native.cpp"), "-o", str(binary)], check=True)
        # Independent labeled pair counts from the earlier full enumeration.
        checks = []
        for rec in json.loads((HERE / "isotropic_completion_results.json").read_text()):
            a = run_graph(binary, rec["vertices"], rec["edges"])
            assert sum(f["successful_flows"] for f in a["first_coordinates"]) == rec["successful_labeled_flows_counted_by_affine_dimension"]
            expected = {sum(1 << e for e in es) for es in rec["first_cycles_with_no_completion"]}
            assert {f["support_mask"] for f in a["first_coordinates"] if not f["successful_flows"]} == expected
            checks.append({"name": rec["name"], "all_failed_first_coordinates_and_total_lift_count_agree": True})
        out["independent_reference_checks"] = checks
        for i, rec in enumerate(old):
            a = run_graph(binary, rec["vertices"], rec["edges"])
            out["graphs"].append(summarize(rec, a))
            if (i+1) % 500 == 0 or i+1 == len(old):
                print("Graphs", i+1, "/", len(old), "elapsed", round(time.monotonic()-start, 1), flush=True)
    totals = Counter(); hist = Counter()
    for rec in out["graphs"]:
        totals.update(rec["counts"]); hist.update(rec["failure_component_histogram"])
    out.update(graphs_checked=len(old), counts=dict(totals), failure_component_histogram=dict(sorted(hist.items())),
               failed_admissible_first_coordinates=sum(len(g["failed_admissible_first_coordinates"]) for g in out["graphs"]),
               graphs_without_nonseparating_success=sum(g["nonseparating_witness"] is None for g in out["graphs"]),
               elapsed_seconds=round(time.monotonic()-start, 3))
    (HERE / "first_coordinate_census.json").write_text(json.dumps(out, indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k != "graphs"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
