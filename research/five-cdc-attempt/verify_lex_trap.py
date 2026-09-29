#!/usr/bin/env python3
"""Independent, standard-library-only verification of the 16-vertex trap.

Uses simple-path DFS to enumerate circuits, rather than cycle-space enumeration.
Does not import the search code or use NetworkX.
"""
from collections import Counter
import json
from pathlib import Path

HERE = Path(__file__).parent


def circuits_dfs(n, edges):
    adj = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        adj[u].append((v, e)); adj[v].append((u, e))
    result = set()
    for start in range(n):
        def visit(v, vertices, path):
            for w, e in adj[v]:
                if w == start and len(vertices) >= 3:
                    result.add(tuple(sorted(path + [e])))
                elif w > start and w not in vertices:
                    visit(w, vertices | {w}, path + [e])
        visit(start, {start}, [])
    return sorted(result)


def defects(n, edges, f):
    result = []
    for normal in range(1, 8):
        adj = [[] for _ in range(n)]
        for e, (u, v) in enumerate(edges):
            if (normal & f[e]).bit_count() % 2 == 0:
                adj[u].append(v); adj[v].append(u)
        remaining = set(range(n))
        count = 0
        while remaining:
            start = min(remaining)
            component, pending = {start}, [start]
            remaining.remove(start)
            while pending:
                for v in adj[pending.pop()]:
                    if v in remaining:
                        remaining.remove(v); component.add(v); pending.append(v)
            colors = Counter(f[e] for e, (u, v) in enumerate(edges)
                             if (u in component) != (v in component))
            parities = [colors[a] % 2 for a in range(1, 8) if (a & normal).bit_count() % 2]
            assert len(set(parities)) == 1
            count += parities[0]
        result.append(count)
    return result


def valid_flow(n, edges, f):
    assert len(f) == len(edges) and all(0 < a < 8 for a in f)
    sums = [0] * n
    for a, (u, v) in zip(f, edges):
        sums[u] ^= a; sums[v] ^= a
    assert sums == [0] * n


def main():
    saved = json.loads((HERE / "lex_census_trap_certificate.json").read_text())
    n, edges, f = saved["vertices"], saved["edges"], saved["flow"]
    assert n == 16 and len(edges) == 24 and len({tuple(e) for e in edges}) == 24
    assert all(sum(v in e for e in edges) == 3 for v in range(n))
    valid_flow(n, edges, f)
    cs = circuits_dfs(n, edges)
    # Edge on a circuit iff it is not a bridge; also verify connectedness.
    assert set(e for c in cs for e in c) == set(range(len(edges)))
    reached = {0}
    while True:
        new = reached | {v for u, v in edges if u in reached} | {u for u, v in edges if v in reached}
        if new == reached:
            break
        reached = new
    assert len(reached) == n
    ds = defects(n, edges, f)
    assert ds == saved["defects"] == [2, 4, 2, 2, 2, 2, 4]
    old = min(ds), sum(ds)
    seen, histogram = set(), Counter()
    for c in cs:
        for a in range(1, 8):
            if a in {f[e] for e in c}:
                continue
            g = f.copy()
            for e in c:
                g[e] ^= a
            valid_flow(n, edges, g)
            seen.add(tuple(g))
            gd = defects(n, edges, g)
            p = min(gd), sum(gd)
            assert p >= old
            histogram[p] += 1
    assert len(cs) == saved["circuits"] == 229
    assert len(seen) == sum(histogram.values()) == saved["distinct_neighbors"] == 175
    assert [{"potential": list(k), "count": v} for k, v in sorted(histogram.items())] == saved["neighbor_histogram"]
    escape = saved["two_move_escape"]
    current = f.copy()
    potentials = [old]
    for prefix in ("first", "second"):
        move = escape[f"{prefix}_move"]
        c, a = move["circuit_edges"], move["added_value"]
        assert tuple(sorted(c)) in cs and a not in {current[e] for e in c}
        for e in c:
            current[e] ^= a
        valid_flow(n, edges, current)
        gd = defects(n, edges, current)
        potentials.append((min(gd), sum(gd)))
        assert current == escape["intermediate_flow" if prefix == "first" else "final_flow"]
    assert potentials == [(2, 18), (2, 18), (0, 18)]
    layers = escape["lift"]["cover"]
    assert len(layers) == 5
    assert all(sum(e in layer for layer in layers.values()) == 2 for e in range(len(edges)))
    assert all(sum(v in edges[e] for e in layer) % 2 == 0 for layer in layers.values() for v in range(n))
    result = {"independent_dfs_circuit_count": len(cs), "distinct_neighbors": len(seen),
              "neutral_neighbors": histogram[old], "improving_neighbors": 0,
              "two_move_escape_potentials": potentials, "exact_five_layer_cover_verified": True,
              "simple_connected_bridgeless_cubic_graph_verified": True, "all_checks_passed": True}
    (HERE / "independent_trap_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
