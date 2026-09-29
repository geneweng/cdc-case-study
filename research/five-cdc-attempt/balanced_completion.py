#!/usr/bin/env python3
"""Construct a five-layer lift from componentwise balanced boundary colors.

Uses the three-state parity lemma discussed in balanced-completion.md.
The general existence of a balanced starting configuration is NOT established.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
import explore as x
from first_coordinate_census import components
from isotropic_completion import cut_masks

HERE = Path(__file__).parent
ROTATE = (0, 2, 3, 1)


def rotate(a, state):
    for _ in range(state):
        a = ROTATE[a]
    return a


def omega(a, b):
    return ((a & 1) * ((b >> 1) & 1)) ^ (((a >> 1) & 1) * (b & 1))


def ordered_circuits(n, edges, mask):
    inc = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        if mask >> e & 1:
            inc[u].append(e); inc[v].append(e)
    assert all(len(es) in (0, 2) for es in inc)
    unused = {e for e in range(len(edges)) if mask >> e & 1}
    out = []
    while unused:
        first = min(unused); start = edges[first][0]; v = start; e = first
        vertices = []; path = []
        while True:
            vertices.append(v); path.append(e); unused.remove(e)
            a, b = edges[e]; v = a ^ b ^ v
            if v == start:
                break
            e = next(j for j in inc[v] if j != e)
        out.append((vertices, path))
    return out


def construct(n, edges, first, q):
    """q is a two-bit flow nonzero outside first; return None if not balanced."""
    inc = x.BASE.incidence(n, edges)
    assert all(0 <= a < 4 for a in q)
    assert all(q[es[0]] ^ q[es[1]] ^ q[es[2]] == 0 for es in inc)
    assert all(q[e] for e in range(len(edges)) if not first >> e & 1)
    hc = components(n, edges, first, keep=False)
    which = {v: k for k, vs in enumerate(hc) for v in vs}
    cs = ordered_circuits(n, edges, first)
    demand = {v: q[next(e for e in inc[v] if not first >> e & 1)]
              for vs, _ in cs for v in vs}
    balances = []
    for vs, _ in cs:
        row = [0]*len(hc)
        for v in vs:
            row[which[v]] ^= demand[v]
        balances.append(row)
    if any(any(row) for row in balances):
        return None
    h = len(hc)
    interaction = [[[[0]*3 for _ in range(3)] for _ in range(h)] for _ in range(h)]
    for vs, _ in cs:
        for i, v in enumerate(vs):
            k = which[v]
            for w in vs[:i]:
                l = which[w]
                if k == l:
                    continue
                for a in range(3):
                    for b in range(3):
                        interaction[k][l][a][b] ^= omega(rotate(demand[v], a), rotate(demand[w], b))
    for k in range(h):
        for l in range(h):
            for a in range(3):
                assert sum(interaction[k][l][a]) % 2 == 0
                for b in range(3):
                    assert interaction[k][l][a][b] == interaction[l][k][b][a]
    cuts = cut_masks(n, edges, first)
    successful = 0; witness = None; defects_hist = Counter()
    for states in itertools.product(range(3), repeat=h):
        qq = [rotate(a, states[which[edges[e][0]]]) if not first >> e & 1 else 0
              for e, a in enumerate(q)]
        for vs, es in cs:
            prefix = 0
            for v, e in zip(vs, es):
                prefix ^= rotate(demand[v], states[which[v]])
                qq[e] = prefix
            assert prefix == 0
        assert all(qq[es[0]] ^ qq[es[1]] ^ qq[es[2]] == 0 for es in inc)
        f = [a + 4*((first >> e) & 1) for e, a in enumerate(qq)]
        assert 0 not in f
        actual = [sum(qq[e] == 0 for e in range(len(edges)) if cut >> e & 1) % 2 for cut in cuts]
        predicted = [sum(interaction[k][l][states[k]][states[l]] for l in range(h)) % 2 for k in range(h)]
        assert actual == predicted
        defects_hist[sum(actual)] += 1
        if not any(actual):
            successful += 1
            if witness is None:
                cover = x.extra_coordinate_lift(n, edges, f)
                assert cover["cover"] is not None
                assert cover["cover"]["4"] == [e for e in range(len(edges)) if first >> e & 1]
                witness = {"states": states, "flow": f, "lift": cover}
    assert successful % 2 == 1
    return {"complement_components": hc, "circuit_component_count": len(cs),
            "boundary_balance_table": balances, "states_checked": 3**h,
            "successful_states": successful, "defect_histogram": dict(sorted(defects_hist.items())),
            "all_interaction_predictions_verified": True, "witness": witness}


def pair_checks(names=None):
    """Every balanced q|H arising from (F,y,z) on the four specified graphs."""
    import networkx as nx
    two_k4 = [(u+shift, v+shift) for shift in (0, 4) for u, v in nx.complete_graph(4).edges()
              if (u, v) != (0, 1)] + [(0, 4), (1, 5)]
    graphs = [("K4", 4, list(nx.complete_graph(4).edges())),
              ("Cube", 8, sorted(tuple(sorted(e)) for e in nx.cubical_graph().edges())),
              ("Petersen", *x.petersen()), ("Two K4s", 8, two_k4)]
    results = []
    for name, n, edges in graphs:
        if names is not None and name not in names:
            continue
        supports = x.all_even_subgraphs(n, edges); full = (1 << len(edges))-1
        checked = states = nontrivial = single = multiple = 0
        example = None
        # One input for each distinct restriction q|H suffices: construction
        # ignores old colors on F, and ordered generators otherwise repeat work.
        for first in supports[1:]:
            seen = set()
            for y in supports:
                for z in supports:
                    if (first | y | z) != full:
                        continue
                    key = (y & ~first, z & ~first)
                    if key in seen:
                        continue
                    seen.add(key)
                    q = [2*((y >> e)&1)+((z >> e)&1) for e in range(len(edges))]
                    result = construct(n, edges, first, q)
                    if result is None:
                        continue
                    checked += 1; states += result["states_checked"]
                    single += result["circuit_component_count"] == 1
                    multiple += result["circuit_component_count"] > 1
                    bad_identity = result["defect_histogram"].get(0, 0) < result["states_checked"]
                    nontrivial += bad_identity
                    if bad_identity and (example is None or result["circuit_component_count"] > example["construction"]["circuit_component_count"]):
                        example = {"vertices": n, "edges": edges, "first_coordinate_mask": first,
                                   "starting_two_bit_flow": q, "construction": result}
        results.append({"name": name, "balanced_complement_colorings_checked": checked,
                        "single_circuit_cases": single, "multiple_circuit_cases": multiple,
                        "rotation_assignments_checked": states, "cases_with_unsuccessful_rotations": nontrivial,
                        "example": example})
        print(name, checked, "balanced restrictions;", states, "rotation assignments", flush=True)
    return results


def abstract_parity_checks():
    # All pair-interaction systems on 2 and 3 variables, and seeded larger cases.
    def bilinear(matrix, a, b):
        return sum(((matrix >> (2*i+j)) & 1)*((a >> i)&1)*((b >> j)&1)
                   for i in range(2) for j in range(2)) % 2
    result = []
    rng = random.Random(20260929)
    for n in range(2, 7):
        pairs = list(itertools.combinations(range(n), 2))
        matrices = itertools.product(range(16), repeat=len(pairs)) if n <= 3 else (
            [rng.randrange(16) for _ in pairs] for _ in range(40))
        tested = 0
        for ms in matrices:
            count = 0
            for values in itertools.product((1, 2, 3), repeat=n):
                parity = [0]*n
                for (i, j), m in zip(pairs, ms):
                    b = bilinear(m, values[i], values[j]); parity[i] ^= b; parity[j] ^= b
                count += not any(parity)
            assert count % 2 == 1
            tested += 1
        result.append({"variables": n, "systems": tested, "exhaustive": n <= 3})
    return result


def multiple_circuit_example():
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
             (8,0),(9,2),(8,4),(9,6),(8,9),(1,3),(5,7)]
    q = [1,3,2,0,2,3,1,0,1,1,2,2,3,2,1]
    first = (1 << 8)-1
    result = construct(10, edges, first, q)
    assert result is not None and result["circuit_component_count"] == 2
    assert len(result["complement_components"]) == 3
    assert x.defect(10, edges, [a+4*(e<8) for e,a in enumerate(q)], 4) == 2
    return {"vertices": 10, "edges": edges, "first_coordinate_mask": first,
            "starting_two_bit_flow": q, "starting_defect": 2, "construction": result}


if __name__ == "__main__":
    result = {"graph_constructions": pair_checks(), "abstract_parity_checks": abstract_parity_checks(),
              "multiple_circuit_example": multiple_circuit_example()}
    (HERE / "balanced_completion_results.json").write_text(json.dumps(result, indent=2)+"\n")
    print("All parity counts, interaction identities and decoded covers verified.")
