#!/usr/bin/env python3
"""Reproduce the proof-attempt experiments; requires Python >=3.10 and networkx.

Run from any directory: python3 research/five-cdc-attempt/run_experiments.py
All outputs are written beside this script. These are finite experiments.
"""
import itertools
import json
import platform
import random
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
import networkx as nx
import explore as x

HERE = Path(__file__).parent


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def palette_search():
    graphs = [("Petersen", *x.petersen())] + [(f"Flower_{k}", *x.flower(k)) for k in (5, 7, 9)]
    for n in (10, 12, 14, 16, 18, 20, 24, 28, 32):
        for seed in range(3):
            g = nx.random_regular_graph(3, n, seed=seed)
            if nx.is_connected(g) and not list(nx.bridges(g)):
                graphs.append((f"random_{n}_{seed}", n, sorted(tuple(sorted(e)) for e in g.edges())))
    records = []
    for i, (name, n, edges) in enumerate(graphs):
        r = x.sampled_search(n, edges, 20260929+i)
        r["name"] = name
        records.append(r)
    save("palette_search.json", {"scope": "Samples, stopping at first all-palette failure or 100 NZ flows.",
                                  "graphs": records})
    print("Palette samples:", len(records), "graphs", flush=True)
    return records


def small_graph_search():
    wagner = nx.Graph([(i, (i+1) % 8) for i in range(8)] + [(i, i+4) for i in range(4)])
    graphs = [("K4", nx.complete_graph(4)), ("K33", nx.complete_bipartite_graph(3, 3)),
              ("Prism6", nx.circular_ladder_graph(3)), ("Cube", nx.cubical_graph()),
              ("Wagner8", wagner)]
    records = []
    for name, g in graphs:
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        r = x.sampled_search(len(g), edges, 77, wanted=1000)
        r["name"] = name
        records.append(r)
    save("small_graph_search.json", records)
    cube = next(r for r in records if r["name"] == "Cube")
    f, edges = cube["all_palettes_fail_witness"]["flow"], cube["edges"]
    rows, variables = x.BASE.alignment(8, edges, f, 3)
    result, solution = x.BASE.solve(rows, variables)
    cover = x.BASE.decode_and_verify(8, edges, f, 3, solution)
    assert result["affine_dimension"] == 3 and len(cover["used_labels"]) == 6
    # The eight global translations are distinct solutions; nullity three
    # proves they exhaust the solutions. Each retains six nonempty labels.
    for a in range(8):
        translated = solution
        for v in range(8):
            translated ^= a << (3*v)
        assert all(x.dot(mask, translated) == rhs for mask, rhs in rows)
        assert len(x.BASE.decode_and_verify(8, edges, f, 3, translated)["used_labels"]) == 6
    independent_lifts = {str(l): x.extra_coordinate_lift(8, edges, x.transform(f, l)) for l in range(1, 8)}
    assert all(r["cover"] is None for r in independent_lifts.values())
    save("cube_certificate.json", {"vertices": 8, "edges": edges, "flow": f,
                                   "ordinary_system": result, "ordinary_cover": cover,
                                   "all_eight_solutions_are_translations": True,
                                   "seven_extra_coordinate_systems": independent_lifts})
    print("Cube certificate: all eight lifts use six labels", flush=True)


def petersen_exhaustive():
    n, edges = x.petersen()
    basis = x.BASE.cycle_basis(n, edges)
    supports = {}
    histogram = Counter()
    nz = 0
    lifted = 0
    for coefficients in itertools.product(range(8), repeat=len(basis)):
        f = [0] * len(edges)
        for circuit, a in zip(basis, coefficients):
            for e in circuit:
                f[e] ^= a
        if 0 in f:
            continue
        nz += 1
        mask = sum(1 << e for e in range(len(edges)) if f[e] & 4)
        ds = x.defects_fast(n, edges, f)
        histogram[ds.count(0)] += 1
        if mask not in supports:
            supports[mask] = {"flows": 0, "good_flows": 0, "witness": f}
        supports[mask]["flows"] += 1
        supports[mask]["good_flows"] += int(ds[3] == 0)
        lift = x.extra_coordinate_lift(n, edges, f)
        assert (lift["cover"] is not None) == (ds[3] == 0)
        lifted += int(lift["cover"] is not None)
    bad = [{"first_coordinate_edges": [e for e in range(len(edges)) if mask >> e & 1], **r}
           for mask, r in supports.items() if r["good_flows"] == 0]
    assert nz == 28560 and len(bad) == 6 and lifted == 4560
    save("petersen_exhaustive.json", {
        "vertices": n, "edges": edges, "cycle_space_dimension": len(basis),
        "all_binary_3_flows_examined_including_zero_edges": 8 ** len(basis),
        "nz_flows": nz, "good_normal_histogram": dict(histogram),
        "first_coordinate_supports": len(supports), "supports_with_no_good_flow": bad,
        "extra_coordinate_crosschecks": nz, "canonical_extra_coordinate_successes": lifted})
    print("Petersen: all", nz, "NZ flows checked; six unrepairable fixed supports", flush=True)


def one_move_search(records):
    results = []
    for r in records:
        if r["vertices"] > 24 or not r["all_palettes_fail_witness"]:
            continue
        n, edges = r["vertices"], r["edges"]
        f = r["all_palettes_fail_witness"]["flow"]
        cs = x.circuits(n, edges)
        old = x.defects_fast(n, edges, f)
        best, move, checked = min(old), None, 0
        for g, change in x.neighbors(f, cs):
            checked += 1
            ds = x.defects_fast(n, edges, g)
            if min(ds) < best:
                best, move = min(ds), {"change": change, "flow": g, "defects": ds}
                if best == 0:
                    break
        results.append({"name": r["name"], "vertices": n, "edges": edges, "original_flow": f,
                        "original_defects": old, "circuits": len(cs), "neighbors_checked": checked,
                        "best_defect": best, "improving_move": move})
    save("cycle_move_search.json", results)


def descent_search(records, lex=False):
    results = []
    for r in records:
        if r["vertices"] > 24 or not r["all_palettes_fail_witness"]:
            continue
        n, edges = r["vertices"], r["edges"]
        basis, cs = x.BASE.cycle_basis(n, edges), x.circuits(n, edges)
        rng = random.Random((442 if lex else 129) + n)
        checked = bad = 0
        trap = None
        for tries in range(100000):
            f = x.BASE.sample_flow(edges, basis, 3, rng)
            if 0 in f:
                continue
            checked += 1
            ds = x.defects_fast(n, edges, f)
            value = (min(ds), sum(ds)) if lex else min(ds)
            if min(ds) == 0:
                continue
            bad += 1
            count, improved, histogram = 0, False, Counter()
            for g, _ in x.neighbors(f, cs):
                count += 1
                gd = x.defects_fast(n, edges, g)
                potential = (min(gd), sum(gd)) if lex else min(gd)
                histogram[str(potential) if lex else potential] += 1
                if potential < value:
                    improved = True
                    break
            if not improved:
                trap = {"flow": f, "defects": ds, "neighbor_count": count,
                        "neighbor_potential_histogram" if lex else "neighbor_defect_histogram": dict(histogram)}
                break
            if bad >= (200 if lex else 100):
                break
        results.append({"name": r["name"], "vertices": n, "edges": edges, "random_trials": tries+1,
                        "nz_flows_checked": checked, "bad_flows_checked": bad, "circuit_count": len(cs),
                        "lex_descent_counterexample" if lex else "strict_descent_counterexample": trap})
        if trap:
            break
    save("lex_descent_search.json" if lex else "descent_search.json", results)
    print("Lexicographic" if lex else "Strict minimum", "descent:",
          sum(r["bad_flows_checked"] for r in results), "bad flows tested; trap:", bool(trap), flush=True)
    return results


def trap_certificate(records):
    r = next(r for r in records if r["strict_descent_counterexample"])
    n, edges, f = r["vertices"], r["edges"], r["strict_descent_counterexample"]["flow"]
    cs, original = x.circuits(n, edges), x.defects_fast(n, edges, f)
    seen, histogram, first_moves = {tuple(f)}, Counter(), []
    for g, move in x.neighbors(f, cs):
        if tuple(g) in seen:
            continue
        seen.add(tuple(g))
        ds = x.defects_fast(n, edges, g)
        histogram[(min(ds), sum(ds))] += 1
        assert min(ds) >= min(original)
        if min(ds) == min(original):
            first_moves.append((g, move, ds))
    escape = None
    for g, move, ds in first_moves:
        for h, second_move in x.neighbors(g, cs):
            hs = x.defects_fast(n, edges, h)
            if min(hs) == 0:
                normal = hs.index(0) + 1
                transformed = x.transform(h, normal)
                lift = x.extra_coordinate_lift(n, edges, transformed)
                assert lift["cover"] is not None
                escape = {"first_change": move, "intermediate_flow": g, "intermediate_defects": ds,
                          "second_change": second_move, "final_flow": h, "final_defects": hs,
                          "successful_normal": normal, "transformed_flow": transformed,
                          "extra_coordinate_lift": lift}
                break
        if escape:
            break
    assert escape is not None
    save("descent_trap_certificate.json", {
        "vertices": n, "edges": edges, "flow": f, "defects": original, "circuit_count": len(cs),
        "distinct_neighbors": len(seen)-1,
        "neighbor_histogram": [{"min_defect": k[0], "sum_defects": k[1], "count": v}
                               for k, v in sorted(histogram.items())], "two_step_escape": escape})
    print("Strict-descent trap: full neighborhood checked; two-step escape certified", flush=True)


def further_lex_search():
    _, ep = x.petersen()
    joined = ([e for i, e in enumerate(ep) if i != 0]
              + [(u+10, v+10) for i, (u, v) in enumerate(ep) if i != 0]
              + [(0, 10), (1, 11)])
    graphs = [("Petersen_two_edge_sum", 20, joined), ("Flower_7", *x.flower(7))]
    results = []
    for name, n, edges in graphs:
        cs, basis = x.circuits(n, edges), x.BASE.cycle_basis(n, edges)
        rng = random.Random(893+n)
        checked = bad = 0
        trap = None
        for tries in range(500000):
            f = x.BASE.sample_flow(edges, basis, 3, rng)
            if 0 in f:
                continue
            checked += 1
            ds = x.defects_fast(n, edges, f)
            value = (min(ds), sum(ds))
            if not value[0]:
                continue
            bad += 1
            changed, histogram = False, Counter()
            for g, _ in x.neighbors(f, cs):
                gd = x.defects_fast(n, edges, g)
                potential = (min(gd), sum(gd))
                histogram[str(potential)] += 1
                if potential < value:
                    changed = True
                    break
            if not changed:
                trap = {"flow": f, "defects": ds, "neighbor_histogram": dict(histogram)}
                break
            if bad >= 200:
                break
        results.append({"name": name, "vertices": n, "edges": edges, "seed": 893+n,
                        "trials": tries+1, "nz_flows_checked": checked, "bad_flows_checked": bad,
                        "circuit_count": len(cs), "counterexample": trap})
    save("further_lex_search.json", results)
    print("Additional lexicographic tests:", sum(r["bad_flows_checked"] for r in results), flush=True)


if __name__ == "__main__":
    records = palette_search()
    small_graph_search()
    petersen_exhaustive()
    one_move_search(records)
    strict = descent_search(records)
    descent_search(records, lex=True)
    trap_certificate(strict)
    further_lex_search()
    save("environment.json", {"python": platform.python_version(), "networkx": nx.__version__,
                              "date": "2026-09-29", "all_assertions_passed": True})
    print("All experiments and certificate checks completed.", flush=True)
