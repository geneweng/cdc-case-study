#!/usr/bin/env python3
"""Exploratory five-CDC proof attempts; no general theorem is asserted.

Uses the fixed-flow criterion of Husek--Samal, Theorem 3.16,
https://arxiv.org/html/2607.24724v1, generalized to all seven hyperplanes
by change of basis. See attempt.md for the derivation and limitations.
"""
import importlib.util
import itertools
import json
import random
from collections import Counter, deque
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("cdc_verify", Path(__file__).parents[1] / "verify_algebra.py")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
dot = BASE.dot


def components(n, edges, f, normal):
    adj = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        if not dot(f[e], normal):
            adj[u].append(v)
            adj[v].append(u)
    unseen = set(range(n))
    result = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        queue = deque([start])
        component = {start}
        while queue:
            for v in adj[queue.popleft()]:
                if v in unseen:
                    unseen.remove(v)
                    component.add(v)
                    queue.append(v)
        cut = [e for e, (u, v) in enumerate(edges) if (u in component) != (v in component)]
        colors = Counter(f[e] for e in cut)
        outside = [a for a in range(1, 8) if dot(a, normal)]
        parity = [colors[a] % 2 for a in outside]
        assert len(set(parity)) == 1, (normal, parity)
        result.append({"vertices": sorted(component), "cut_edges": cut,
                       "outside_values": outside, "cut_color_counts": [colors[a] for a in outside],
                       "obstruction": parity[0]})
    return result


def good_normals(n, edges, f):
    return [l for l in range(1, 8) if all(not c["obstruction"] for c in components(n, edges, f, l))]


def defect(n, edges, f, normal):
    return sum(c["obstruction"] for c in components(n, edges, f, normal))


def defects_fast(n, edges, f):
    result = []
    for normal in range(1, 8):
        parent = list(range(n))

        def root(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u

        for e, (u, v) in enumerate(edges):
            if not dot(f[e], normal):
                parent[root(u)] = root(v)
        a = next(a for a in range(1, 8) if dot(a, normal))
        parity = [0] * n
        for e, (u, v) in enumerate(edges):
            if f[e] == a:
                parity[root(u)] ^= 1
                parity[root(v)] ^= 1
        result.append(sum(parity))
    return result


def all_even_subgraphs(n, edges):
    basis = BASE.cycle_basis(n, edges)
    masks = [sum(1 << e for e in c) for c in basis]
    sets = [0]
    for mask in masks:
        sets += [s ^ mask for s in sets]
    return sets


def circuits(n, edges):
    result = []
    for mask in all_even_subgraphs(n, edges)[1:]:
        selected = [e for e in range(len(edges)) if mask >> e & 1]
        vertices = {v for e in selected for v in edges[e]}
        # An even subgraph in a cubic graph is a disjoint union of circuits.
        adj = {v: [] for v in vertices}
        for e in selected:
            u, v = edges[e]
            adj[u].append(v)
            adj[v].append(u)
        seen = {min(vertices)}
        queue = deque(seen)
        while queue:
            for v in adj[queue.popleft()]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if seen == vertices:
            result.append(selected)
    return result


def neighbors(f, circuit_list):
    for c in circuit_list:
        for a in range(1, 8):
            if any(f[e] == a for e in c):
                continue
            g = f.copy()
            for e in c:
                g[e] ^= a
            yield g, {"circuit_edges": c, "added_value": a}


def transform(f, normal):
    for b in range(1, 8):
        for c in range(1, 8):
            images = [(dot(normal, x) << 2) | (dot(b, x) << 1) | dot(c, x) for x in range(8)]
            if len(set(images)) == 8:
                return [images[x] for x in f]
    raise AssertionError("No invertible basis change")


def direct_check(n, edges, f):
    good = []
    for l in range(1, 8):
        transformed = transform(f, l)
        rows, variables = BASE.alignment(n, edges, transformed, 3, five=True)
        result, x = BASE.solve(rows, variables)
        if x is not None:
            good.append(l)
            cover = BASE.decode_and_verify(n, edges, transformed, 3, x)
            assert len(cover["used_labels"]) <= 5
    assert good == good_normals(n, edges, f)
    return good


def extra_coordinate_lift(n, edges, f):
    """Independently construct a 5-CDC by completing one binary flow coordinate.

    Forbidden 4-bit vectors are C={4,5,6,15,8}, a five-element circuit.
    A lift f | (z << 3) avoids C exactly when z=1 on values 4,5,6,
    and z=0 on value 7. Values 1,2,3 leave z free.
    """
    inc = BASE.incidence(n, edges)
    rows = [(sum(1 << e for e in es), 0) for es in inc]
    rows += [(1 << e, int(f[e] != 7)) for e in range(len(edges)) if f[e] & 4]
    result, z = BASE.solve(rows, len(edges))
    if z is None:
        return {"system": result, "cover": None}
    forbidden = [4, 5, 6, 15, 8]
    lookup = {forbidden[i] ^ forbidden[j]: [i, j] for i in range(5) for j in range(i+1, 5)}
    assert len(lookup) == 10
    assert set(lookup) == set(range(1, 16)) - set(forbidden)
    lifted = [a | (((z >> e) & 1) << 3) for e, a in enumerate(f)]
    assert all(a in lookup for a in lifted)
    assert all(lifted[es[0]] ^ lifted[es[1]] ^ lifted[es[2]] == 0 for es in inc)
    pairs = [lookup[a] for a in lifted]
    layers = {str(i): [e for e, pair in enumerate(pairs) if i in pair] for i in range(5)}
    assert all(sum(i in pairs[e] for e in es) in (0, 2) for i in range(5) for es in inc)
    assert all(sum(e in layer for layer in layers.values()) == 2 for e in range(len(edges)))
    return {"system": result, "new_binary_coordinate": [(z >> e) & 1 for e in range(len(edges))],
            "four_bit_flow": lifted, "cover": layers,
            "exact_double_coverage_and_even_degrees_verified": True}


def petersen():
    return 10, ([(i, (i + 1) % 5) for i in range(5)]
                + [(i, i + 5) for i in range(5)]
                + [(i + 5, (i + 2) % 5 + 5) for i in range(5)])


def flower(k):
    edges = [(4*i, 4*i+j) for i in range(k) for j in (1, 2, 3)]
    edges += [(4*i+1, 4*((i+1) % k)+1) for i in range(k)]
    edges += [(4*i+j, 4*(i+1)+j) for i in range(k-1) for j in (2, 3)]
    edges += [(4*(k-1)+2, 3), (4*(k-1)+3, 2)]
    return 4*k, edges


def sampled_search(n, edges, seed, wanted=100, budget=100000):
    basis = BASE.cycle_basis(n, edges)
    rng = random.Random(seed)
    histogram = Counter()
    witness = None
    checked = 0
    for tries in range(1, budget+1):
        f = BASE.sample_flow(edges, basis, 3, rng)
        if 0 in f:
            continue
        good = good_normals(n, edges, f)
        histogram[len(good)] += 1
        checked += 1
        if not good:
            assert direct_check(n, edges, f) == []
            witness = {"flow": f, "normal_obstructions": {
                str(l): [c for c in components(n, edges, f, l) if c["obstruction"]]
                for l in range(1, 8)}}
            break
        if checked == wanted:
            break
    return {"vertices": n, "edges": edges, "seed": seed, "random_trials": tries,
            "nz_flows_checked": checked, "good_normal_histogram": dict(sorted(histogram.items())),
            "all_palettes_fail_witness": witness}


if __name__ == "__main__":
    import networkx as nx
    out = {"scope": "Exploratory samples, not exhaustive graph verification.", "graphs": []}
    graphs = [("Petersen", *petersen())] + [(f"Flower_{k}", *flower(k)) for k in (5, 7, 9)]
    for n in (10, 12, 14, 16, 18, 20, 24, 28, 32):
        for seed in range(3):
            g = nx.random_regular_graph(3, n, seed=seed)
            if nx.is_connected(g) and not list(nx.bridges(g)):
                graphs.append((f"random_{n}_{seed}", n, sorted(tuple(sorted(e)) for e in g.edges())))
    for i, (name, n, edges) in enumerate(graphs):
        result = sampled_search(n, edges, 20260929+i)
        result["name"] = name
        out["graphs"].append(result)
        print(name, result["nz_flows_checked"], result["good_normal_histogram"],
              "COUNTEREXAMPLE" if result["all_palettes_fail_witness"] else "", flush=True)
        Path(__file__).with_name("palette_search.json").write_text(json.dumps(out, indent=2)+"\n")
