#!/usr/bin/env python3
"""Reproduce the finite checks in the CDC research report (standard library only).

The alignment system is from the supplied CDC proof / Oum exposition.
The five-label specialization is Observation 3.15 of Husek--Samal,
https://arxiv.org/html/2607.24724v1. This is a fresh implementation.
Finite examples illustrate the method; they do not prove an open conjecture.
Run: python3 research/verify_algebra.py > research/verification_results.json
"""

import json
import random
from collections import deque


def dot(a, b):
    return (a & b).bit_count() % 2


def local_parity_check(k):
    valid = failures = 0
    first = None
    for p in range(1, 1 << k):
        for q in range(1, 1 << k):
            if p == q:
                continue
            for a in range(1 << k):
                for b in range(1 << k):
                    c = a ^ b
                    if dot(a, p) or dot(b, q) or dot(c, p ^ q):
                        continue
                    valid += 1
                    lam = dot(b, p)
                    parity = sum(h != 0 for h in (a, b, c)) % 2
                    if lam != parity:
                        failures += 1
                        if first is None:
                            first = {"flow_triple": [p, q, p ^ q],
                                     "dual_triple": [a, b, c],
                                     "lambda": lam, "nonzero_parity": parity}
    return {"dimension": k, "valid_local_configurations": valid,
            "identity_failures": failures, "first_failure": first}


def incidence(n, edges):
    inc = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        inc[u].append(e)
        inc[v].append(e)
    assert all(len(es) == 3 for es in inc)
    return inc


def cycle_basis(n, edges):
    parent = list(range(n))

    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v

    tree = [[] for _ in range(n)]
    chords = []
    for e, (u, v) in enumerate(edges):
        ru, rv = root(u), root(v)
        if ru == rv:
            chords.append(e)
        else:
            parent[ru] = rv
            tree[u].append((v, e))
            tree[v].append((u, e))
    basis = []
    for e in chords:
        u, v = edges[e]
        paths = {u: []}
        queue = deque([u])
        while v not in paths:
            w = queue.popleft()
            for z, f in tree[w]:
                if z not in paths:
                    paths[z] = paths[w] + [f]
                    queue.append(z)
        basis.append(paths[v] + [e])
    return basis


def sample_flow(edges, basis, k, rng):
    f = [0] * len(edges)
    for cycle in basis:
        value = rng.randrange(1 << k)
        for e in cycle:
            f[e] ^= value
    return f


def alignment(n, edges, f, k, five=False):
    inc = incidence(n, edges)
    next_edge = {(v, e): es[(j + 1) % 3]
                 for v, es in enumerate(inc) for j, e in enumerate(es)}
    rows = []
    for e, (u, v) in enumerate(edges):
        rhs = f[next_edge[u, e]] ^ f[next_edge[v, e]]
        for bit in range(k):
            mask = (1 << (k * u + bit)) ^ (1 << (k * v + bit))
            if (f[e] >> bit) & 1:
                mask ^= 1 << (k * n + e)
            rows.append((mask, (rhs >> bit) & 1))
    if five:
        assert k == 3
        for v, es in enumerate(inc):
            first_coordinate_edges = [e for e in es if f[e] & 4]
            assert len(first_coordinate_edges) in (0, 2)
            if first_coordinate_edges:
                other = next(e for e in es if not (f[e] & 4))
                target = 4 ^ f[other]
                rows.extend((1 << (3 * v + bit), (target >> bit) & 1)
                            for bit in range(3))
            else:
                rows.append((1 << (3 * v + 2), 0))
    return rows, k * n + len(edges)


def solve(rows, variables):
    pivots = {}
    contradiction = None
    for i, (mask, rhs) in enumerate(rows):
        provenance = 1 << i
        while mask:
            pivot = (mask & -mask).bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (mask, rhs, provenance)
                break
            pm, pr, pp = pivots[pivot]
            mask ^= pm
            rhs ^= pr
            provenance ^= pp
        if mask == 0 and rhs and contradiction is None:
            contradiction = provenance
    result = {"equations": len(rows), "variables": variables,
              "rank": len(pivots), "consistent": contradiction is None}
    if contradiction is not None:
        indices = [i for i in range(len(rows)) if (contradiction >> i) & 1]
        combined_mask = combined_rhs = 0
        for i in indices:
            combined_mask ^= rows[i][0]
            combined_rhs ^= rows[i][1]
        assert combined_mask == 0 and combined_rhs == 1
        result["contradiction_row_indices"] = indices
        result["certificate_verified"] = True
        return result, None
    x = 0
    for pivot in sorted(pivots, reverse=True):
        mask, rhs, _ = pivots[pivot]
        if dot(mask, x) != rhs:
            x ^= 1 << pivot
    assert all(dot(mask, x) == rhs for mask, rhs in rows)
    result["affine_dimension"] = variables - len(pivots)
    return result, x


def decode_and_verify(n, edges, f, k, x):
    inc = incidence(n, edges)
    translations = [(x >> (k * v)) & ((1 << k) - 1) for v in range(n)]
    pairs = []
    for e, (u, v) in enumerate(edges):
        pu = {translations[u] ^ f[j] for j in inc[u] if j != e}
        pv = {translations[v] ^ f[j] for j in inc[v] if j != e}
        assert pu == pv and len(pu) == 2
        pairs.append(sorted(pu))
    for label in range(1 << k):
        assert all(sum(label in pairs[e] for e in es) in (0, 2) for es in inc)
    return {"vertex_translations": translations, "edge_label_pairs": pairs,
            "used_labels": sorted(set().union(*(set(p) for p in pairs))),
            "exact_double_coverage_and_even_degrees_verified": True}


def five_component_parities(n, edges, f):
    """Independent combinatorial test from Husek--Samal, Theorem 3.16."""
    adj = [[] for _ in range(n)]
    marked = set()
    for e, (u, v) in enumerate(edges):
        if not (f[e] & 4):
            adj[u].append(v)
            adj[v].append(u)
        if f[e] == 4:
            marked.update((u, v))
    unseen = set(range(n))
    components = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        component = [start]
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    component.append(v)
                    queue.append(v)
        z = sorted(marked.intersection(component))
        components.append({"vertices": sorted(component), "marked_vertices": z,
                           "marked_parity": len(z) % 2})
    return components


def find_examples(n, edges, k, seed, want_five=False, want_failure=False):
    rng = random.Random(seed)
    basis = cycle_basis(n, edges)
    inc = incidence(n, edges)
    found = {}
    checked = 0
    for _ in range(10000):
        f = sample_flow(edges, basis, k, rng)
        if 0 in f:
            continue
        assert all(f[es[0]] ^ f[es[1]] ^ f[es[2]] == 0 for es in inc)
        checked += 1
        rows, variables = alignment(n, edges, f, k)
        base, x = solve(rows, variables)
        if want_failure and not base["consistent"]:
            indices = set(base["contradiction_row_indices"])
            h = [sum(1 << bit for bit in range(k) if k * e + bit in indices)
                 for e in range(len(edges))]
            assert all(dot(f[e], h[e]) == 0 for e in range(len(edges)))
            assert all(h[es[0]] ^ h[es[1]] ^ h[es[2]] == 0 for es in inc)
            found["inconsistent_alignment"] = {"flow": f, "dual_flow": h,
                                                "system": base}
            break
        if want_five:
            assert base["consistent"]
            five_rows, five_vars = alignment(n, edges, f, k, five=True)
            specialized, y = solve(five_rows, five_vars)
            components = five_component_parities(n, edges, f)
            assert specialized["consistent"] == all(c["marked_parity"] == 0
                                                      for c in components)
            key = "five_label_success" if specialized["consistent"] else "five_label_failure"
            if key not in found:
                example = {"flow": f, "ordinary_system": base,
                           "five_label_system": specialized,
                           "component_parity_test": components,
                           "ordinary_cover": decode_and_verify(n, edges, f, k, x)}
                if y is not None:
                    example["five_label_cover"] = decode_and_verify(n, edges, f, k, y)
                    assert set(example["five_label_cover"]["used_labels"]) <= {0, 1, 2, 3, 4}
                found[key] = example
            if len(found) == 2:
                break
    if want_five:
        assert len(found) == 2, "Did not find both five-label examples"
    if want_failure:
        assert "inconsistent_alignment" in found
    return {"vertices": n, "edges_in_order": edges, "seed": seed,
            "nowhere_zero_flows_checked_until_examples_found": checked, "examples": found}


def main():
    local = [local_parity_check(k) for k in (3, 4)]
    assert local[0]["identity_failures"] == 0
    assert local[1]["identity_failures"] > 0
    petersen = ([(i, (i + 1) % 5) for i in range(5)]
                + [(i, i + 5) for i in range(5)]
                + [(i + 5, (i + 2) % 5 + 5) for i in range(5)])
    k33 = [(u, v) for u in range(3) for v in range(3, 6)]
    simplex_weights = [sum(dot(a, v) for v in range(1, 8)) for a in range(1, 8)]
    assert simplex_weights == [4] * 7 and (2 * 7) % 4 != 0
    result = {
        "scope": "Finite checks and examples, not proofs of open conjectures.",
        "bit_convention": "Integers represent binary vectors; bit 2 is the first coordinate in the five-label test.",
        "local_parity": local,
        "petersen_fixed_flow_five_label_test": find_examples(10, petersen, 3, 20260929, want_five=True),
        "k33_dimension_four_obstruction": find_examples(6, k33, 4, 20260929, want_failure=True),
        "dual_fano_obstruction": {"nonzero_cycle_weights": simplex_weights,
                                  "required_total_for_double_cover": 14,
                                  "divisibility_obstruction_verified": True},
        "nonaffine_exact_two_example": {"vectors": ["1100", "1010", "1001"],
                                         "xor": "1111", "xor_weight": 4}
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
