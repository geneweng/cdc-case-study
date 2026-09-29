#!/usr/bin/env python3
"""Exhaust the proposed repair lemma modulo GL(3,2), using nauty geng.

This checks a stronger candidate lemma, not the open conjecture itself.
Run: python3 research/five-cdc-attempt/exhaustive_repair.py --max-order 12
Requires NetworkX and geng (nauty). Results are written beside this script.
"""
import argparse
from collections import Counter
import itertools
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import networkx as nx
import explore as x

HERE = Path(__file__).parent


def subspaces(r, k):
    """Unique reduced row echelon basis for each k-subspace of F2^r."""
    for pivots in itertools.combinations(range(r), k):
        slots = [(i, j) for i, p in enumerate(pivots)
                 for j in range(p + 1, r) if j not in pivots]
        for assignment in range(1 << len(slots)):
            rows = [1 << p for p in pivots]
            for b, (i, j) in enumerate(slots):
                if assignment >> b & 1:
                    rows[i] |= 1 << j
            yield tuple(rows)


def canonical(rows):
    basis = {}
    for v in rows:
        for p in sorted(basis):
            if v >> p & 1:
                v ^= basis[p]
        if not v:
            continue
        p = (v & -v).bit_length() - 1
        for q, w in list(basis.items()):
            if w >> p & 1:
                basis[q] ^= v
        basis[p] = v
    return tuple(basis[p] for p in sorted(basis))


def gaussian(r, k):
    a = b = 1
    for i in range(k):
        a *= (1 << r) - (1 << i)
        b *= (1 << k) - (1 << i)
    return a // b


class OrbitSearch:
    def __init__(self, n, edges):
        self.n, self.edges = n, edges
        self.basis = x.BASE.cycle_basis(n, edges)
        self.r = len(self.basis)
        self.supports = [0]
        for c in self.basis:
            mask = sum(1 << e for e in c)
            self.supports += [s ^ mask for s in self.supports]
        self.full = (1 << len(edges)) - 1
        reverse = {s: i for i, s in enumerate(self.supports)}
        self.circuits = x.circuits(n, edges)
        self.circuit_codes = [reverse[sum(1 << e for e in c)] for c in self.circuits]
        self.cut_cache = {}
        self.potentials = {}
        self.crosschecks = 0

    def flow(self, rows):
        return [sum(((self.supports[b] >> e) & 1) << i for i, b in enumerate(rows))
                for e in range(len(self.edges))]

    def cuts(self, code):
        if code in self.cut_cache:
            return self.cut_cache[code]
        support = self.supports[code]
        parent = list(range(self.n))

        def root(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v

        for e, (u, v) in enumerate(self.edges):
            if not (support >> e & 1):
                parent[root(u)] = root(v)
        cuts = {}
        for e, (u, v) in enumerate(self.edges):
            u, v = root(u), root(v)
            if u != v:
                cuts[u] = cuts.get(u, 0) ^ (1 << e)
                cuts[v] = cuts.get(v, 0) ^ (1 << e)
        # Components with empty boundary have zero obstruction.
        result = list(cuts.values())
        self.cut_cache[code] = result
        return result

    def colors(self, rows):
        supports = [self.supports[b] for b in rows] + [0] * (3 - len(rows))
        return [self.full &
                (supports[0] if a & 1 else ~supports[0]) &
                (supports[1] if a & 2 else ~supports[1]) &
                (supports[2] if a & 4 else ~supports[2])
                for a in range(8)]

    def defects(self, rows):
        colors = self.colors(rows)
        result = []
        for normal in range(1, 8):
            code = 0
            for i, row in enumerate(rows):
                if normal >> i & 1:
                    code ^= row
            a = normal & -normal  # First value outside the normal's kernel.
            result.append(sum((cut & colors[a]).bit_count() & 1 for cut in self.cuts(code)))
        return result

    def potential(self, rows):
        key = canonical(rows)
        if key not in self.potentials:
            defects = self.defects(key)
            self.potentials[key] = min(defects), sum(defects)
        return self.potentials[key]

    def run(self):
        counts, seen, bad, checked, hist = Counter(), Counter(), 0, 0, Counter()
        trap = None
        for rank in (2, 3):
            for rows in subspaces(self.r, rank):
                seen[rank] += 1
                assert canonical(rows) == rows
                union = 0
                for b in rows:
                    union |= self.supports[b]
                if union != self.full:
                    continue
                counts[rank] += 1
                ds = self.defects(rows)
                potential = min(ds), sum(ds)
                self.potentials[rows] = potential
                hist[str(potential)] += 1
                if counts[rank] % 101 == 1:
                    assert ds == x.defects_fast(self.n, self.edges, self.flow(rows))
                    self.crosschecks += 1
                if not potential[0]:
                    continue
                assert rank == 3
                bad += 1
                colors = self.colors(rows)
                improved = False
                for q in self.circuit_codes:
                    support = self.supports[q]
                    for a in range(1, 8):
                        if support & colors[a]:
                            continue
                        neighbor = tuple(row ^ q if a >> i & 1 else row for i, row in enumerate(rows))
                        checked += 1
                        if self.potential(neighbor) < potential:
                            improved = True
                            break
                    if improved:
                        break
                if not improved:
                    trap = {"rows": rows, "flow": self.flow(rows), "defects": ds}
                    break
            if trap:
                break
            assert seen[rank] == gaussian(self.r, rank)
        return {"cycle_dimension": self.r, "circuit_count": len(self.circuits),
                "subspaces_enumerated_by_rank": dict(seen), "nz_orbits_by_rank": dict(counts),
                # There are 42 spanning 3-by-2 coordinate matrices and 168 bases of F2^3.
                "nz_labeled_flows_represented": 42 * counts[2] + 168 * counts[3],
                "bad_orbits_checked": bad, "neighbors_examined": checked,
                "independent_defect_crosschecks": self.crosschecks,
                "potential_histogram": dict(hist), "counterexample": trap,
                "exhausted_all_flow_orbits": trap is None}


def certify_trap(n, edges, flow):
    """Recheck a found trap with the older, separate edge-list implementation."""
    inc = x.BASE.incidence(n, edges)
    assert all(flow[es[0]] ^ flow[es[1]] ^ flow[es[2]] == 0 for es in inc)
    ds = x.defects_fast(n, edges, flow)
    assert ds == [x.defect(n, edges, flow, l) for l in range(1, 8)]
    potential = min(ds), sum(ds)
    cs = x.circuits(n, edges)
    hist, seen = Counter(), set()
    escape = None
    first = []
    for g, move in x.neighbors(flow, cs):
        seen.add(tuple(g))
        gd = x.defects_fast(n, edges, g)
        p = min(gd), sum(gd)
        hist[p] += 1
        assert p >= potential
        first.append((g, move, gd))
    assert len(seen) == sum(hist.values())
    assert not x.direct_check(n, edges, flow)
    for g, move, gd in sorted(first, key=lambda item: (min(item[2]), sum(item[2]))):
        for h, second in x.neighbors(g, cs):
            hd = x.defects_fast(n, edges, h)
            if not min(hd):
                normal = hd.index(0) + 1
                transformed = x.transform(h, normal)
                lift = x.extra_coordinate_lift(n, edges, transformed)
                assert lift["cover"] is not None
                escape = {"first_move": move, "intermediate_flow": g, "intermediate_defects": gd,
                          "second_move": second, "final_flow": h, "final_defects": hd,
                          "successful_normal": normal, "transformed_flow": transformed, "lift": lift}
                break
        if escape:
            break
    return {"vertices": n, "edges": edges, "flow": flow, "defects": ds,
            "potential": potential, "circuits": len(cs), "distinct_neighbors": len(seen),
            "neighbor_histogram": [{"potential": k, "count": v} for k, v in sorted(hist.items())],
            "two_move_escape": escape, "lexicographic_lemma_refuted": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-order", type=int, default=12)
    args = parser.parse_args()
    geng = shutil.which("geng") or shutil.which("nauty-geng")
    if not geng:
        raise SystemExit("Install nauty's geng or put it on PATH to reproduce the graph census.")
    version = subprocess.run([geng, "-version"], check=True, capture_output=True, text=True).stdout.strip()
    out = {"date": "2026-09-29", "python": platform.python_version(), "networkx": nx.__version__,
           "geng_version": version,
           "graph_scope": "Connected bridgeless simple cubic graphs, nauty geng -c -d3 -D3.",
           "flow_scope": "All nowhere-zero binary 3-flows modulo invertible changes of coordinates.",
           "requested_max_order": args.max_order, "orders": [], "graphs": [], "counterexample": None}
    start = time.monotonic()
    for n in range(4, args.max_order + 1, 2):
        process = subprocess.run([geng, "-cq", "-d3", "-D3", str(n)], check=True, capture_output=True)
        lines = process.stdout.splitlines()
        summary = {"vertices": n, "connected_cubic_graphs_generated": len(lines),
                   "bridgeless_graphs_checked": 0, "flow_orbits_checked": 0, "bad_orbits_checked": 0}
        for index, line in enumerate(lines):
            graph = nx.from_graph6_bytes(line)
            assert nx.is_connected(graph) and all(d == 3 for _, d in graph.degree())
            if list(nx.bridges(graph)):
                continue
            edges = sorted(tuple(sorted(e)) for e in graph.edges())
            search = OrbitSearch(n, edges)
            result = search.run()
            result.update({"vertices": n, "geng_index": index, "graph6": line.decode(), "edges": edges})
            out["graphs"].append(result)
            summary["bridgeless_graphs_checked"] += 1
            summary["flow_orbits_checked"] += sum(result["nz_orbits_by_rank"].values())
            summary["bad_orbits_checked"] += result["bad_orbits_checked"]
            if result["counterexample"]:
                out["counterexample"] = certify_trap(n, edges, result["counterexample"]["flow"])
                (HERE / "lex_trap_certificate.json").write_text(json.dumps(out["counterexample"], indent=2) + "\n")
                break
            if (index + 1) % 20 == 0:
                print(n, "vertices:", index + 1, "/", len(lines), "graphs;", round(time.monotonic()-start, 1), "sec", flush=True)
        summary["complete_order"] = out["counterexample"] is None
        out["orders"].append(summary)
        out["elapsed_seconds"] = round(time.monotonic() - start, 3)
        (HERE / "exhaustive_repair_results.json").write_text(json.dumps(out, indent=2) + "\n")
        print(summary, "elapsed", out["elapsed_seconds"], flush=True)
        if out["counterexample"]:
            print("LEXICOGRAPHIC COUNTEREXAMPLE:", json.dumps(out["counterexample"]), flush=True)
            break


if __name__ == "__main__":
    main()
