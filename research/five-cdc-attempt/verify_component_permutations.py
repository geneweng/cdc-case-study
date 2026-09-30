#!/usr/bin/env python3
"""Independent full-permutation matrix audit.

Uses direct scalar/offset equations with polynomial-bit field arithmetic.
It does not call the obstruction-signature classifier or its gauge reduction.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from verify_rank_one_obstruction import conjugate, consistent, multiply, trace

PAIRS = list(itertools.combinations(range(5), 2))


def has_completion(matrix, active):
    for prefix in itertools.product((1, 2, 3), repeat=4):
        state = prefix+(1,); total = 0
        for a, s in zip(active, state):
            if a:
                total ^= s
        if total:
            continue
        bits = [0]*5
        for i, j in PAIRS:
            value = trace(multiply(multiply(state[i], conjugate(state[j])), matrix[i][j]))
            bits[i] ^= value; bits[j] ^= value
        if consistent(bits, state, active):
            return True
    return False


def reflect(d, e, mask):
    matrix = [[0]*5 for _ in range(5)]
    for i, j in PAIRS:
        source = d[i][j] if mask[i] == mask[j] else e[i][j]
        matrix[i][j] = conjugate(source) if mask[i] else source
        matrix[j][i] = conjugate(matrix[i][j])
    return matrix


def main():
    directory = Path(__file__).parent
    saved = json.loads((directory / "component_permutation_results.json").read_text())
    for record in saved["finite_classification"]:
        d, active = record["canonical_D"], record["active"]
        allowed = []; positions = []
        for k in range(5):
            neighbors = [j for j in range(5) if j != k]
            positions.append([PAIRS.index(tuple(sorted((k, j)))) for j in neighbors])
            permitted = set()
            for entries in itertools.product(range(4), repeat=4):
                matrix = [row[:] for row in d]
                for j, value in zip(neighbors, entries):
                    matrix[k][j] = conjugate(value); matrix[j][k] = value
                if not has_completion(matrix, active):
                    permitted.add(entries)
            allowed.append(permitted)
        assert list(map(len, allowed)) == record["per_vertex_allowed_single_reflection_patterns"]
        survivors = []
        for entries in itertools.product(range(4), repeat=10):
            if all(tuple(entries[index] for index in positions[k]) in allowed[k] for k in range(5)):
                survivors.append(entries)
        assert set(survivors) == {tuple(r["E_upper_triangle"]) for r in record["single_reflection_survivors"]}
        persistent = set(); histogram = Counter()
        for entries in survivors:
            e = [[0]*5 for _ in range(5)]
            for (i, j), value in zip(PAIRS, entries):
                e[i][j] = e[j][i] = value
            bad = 0
            for prefix in itertools.product(range(2), repeat=4):
                bad += not has_completion(reflect(d, e, prefix+(0,)), active)
            histogram[bad] += 1
            if bad == 16:
                persistent.add(entries)
        assert histogram == {int(k): v for k, v in record["survivor_orbit_histogram"].items()}
        assert persistent == {tuple(r["E_upper_triangle"]) for r in record["persistent_pairs"]}
        print(record["active_components"], "active components:", 4**10,
              "E matrices checked;", len(survivors), "single-reflection survivors;",
              len(persistent), "full-permutation obstructions", flush=True)
    graphs = {g["graph6"]: g for g in json.loads((directory / "first_coordinate_census.json").read_text())["graphs"]}
    inputs = {(r["graph6"], r["first_coordinate_mask"]): r["starting_flow"] for r in
              json.loads((directory / "rank_one_obstruction_results.json").read_text())["saved_failures"]["records"]}
    records = saved["saved_graph_checks"]["records"]
    for record in records:
        graph = graphs[record["graph6"]]
        n, edges = graph["vertices"], graph["edges"]
        result = record["completion"]; f = result["repaired_flow"]
        assert len(f) == len(edges) and all(0 < a < 8 for a in f)
        sums = [0]*n
        for a, (u, v) in zip(f, edges):
            sums[u] ^= a; sums[v] ^= a
        assert not any(sums)
        first = result["new_first_coordinate_mask"]
        original = inputs[record["graph6"], record["original_first_coordinate_mask"]]
        assert first == sum(1 << i for i, a in enumerate(original) if (a & result["normal"]).bit_count() % 2)
        assert first == sum(1 << i for i, a in enumerate(f) if a & 4)
        covers = result["cover_edge_masks"]
        assert len(covers) == 5 and covers[4] == first
        assert all(sum((mask >> i) & 1 for mask in covers) == 2 for i in range(len(edges)))
        for mask in covers:
            degree = [0]*n
            for i, (u, v) in enumerate(edges):
                if mask >> i & 1:
                    degree[u] += 1; degree[v] += 1
            assert all(d in (0, 2) for d in degree)
    assert len(records) == 215 and len({r["graph6"] for r in records}) == 35
    print("All 215 changed-layer cover certificates on 35 graphs verified independently.", flush=True)


if __name__ == "__main__":
    main()
