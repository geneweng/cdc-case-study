#!/usr/bin/env python3
"""Check parallel-pair normalization and the limits of a naive move lift."""
from collections import Counter
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import explore as x
from exhaustive_repair import OrbitSearch, subspaces

HERE = Path(__file__).parent


def expand(n, edges, f, e, b):
    u, v = edges[e]
    a = f[e]
    assert b and b != a
    ee = list(map(tuple, edges))
    ee[e] = (u, n)
    ee += [(n, n+1), (n, n+1), (n+1, v)]
    return ee, f + [b, a ^ b, a]


def validate(n, edges, f):
    assert all(0 < a < 8 for a in f)
    assert all(f[es[0]] ^ f[es[1]] ^ f[es[2]] == 0 for es in x.BASE.incidence(n, edges))


def potential(n, edges, f):
    ds = x.defects_fast(n, edges, f)
    return min(ds), sum(ds)


def normalization_checks():
    records = json.loads((HERE / "exhaustive_repair_results.json").read_text())["graphs"]
    cases = extensions = 0
    hist = Counter()
    for rec in records:
        n, edges = rec["vertices"], rec["edges"]
        if n > 8:
            continue
        search = OrbitSearch(n, edges)
        inc = x.BASE.incidence(n, edges)
        for rank in (2, 3):
            for rows in subspaces(search.r, rank):
                f = search.flow(rows)
                if 0 in f:
                    continue
                ds = x.defects_fast(n, edges, f)
                for e, (u, v) in enumerate(edges):
                    cases += 1
                    a = f[e]
                    exact = 0
                    for b in range(1, 8):
                        if b == a or b > (a ^ b):
                            continue
                        ee, ef = expand(n, edges, f, e, b)
                        validate(n+2, ee, ef)
                        ed = x.defects_fast(n+2, ee, ef)
                        assert all(old-new in (0, 2) for old, new in zip(ed, ds))
                        exact += ed == ds
                        extensions += 1
                        for endpoint in (u, v):
                            anchor = next(f[j] for j in inc[endpoint] if j != e)
                            added = b ^ anchor
                            ff = ef.copy()
                            if added:
                                assert added not in (ef[-3], ef[-2])
                                ff[-3] ^= added; ff[-2] ^= added
                            validate(n+2, ee, ff)
                            assert x.defects_fast(n+2, ee, ff) == ds
                    hist[exact] += 1
    assert cases == 2283 and extensions == 6849
    assert dict(hist) == {1: 797, 2: 1212, 3: 274}
    return {"base_flow_edge_pairs": cases, "unordered_parallel_color_pairs_tested": extensions,
            "normalization_to_both_endpoints_verified": True,
            "number_of_exact_choices_histogram": dict(sorted(hist.items()))}


def verify_lift_obstruction():
    r = json.loads((HERE / "parallel_lift_obstruction.json").read_text())
    n, edges, f = r["vertices"], r["edges"], r["flow"]
    e, move = r["expanded_edge"], r["base_move"]
    assert e == 6 and f[e] == 3 and move["added_value"] == 5
    assert sorted(move["circuit_edges"]) in x.circuits(n, edges)
    assert 5 not in {f[j] for j in move["circuit_edges"]}
    ee, ef = expand(n, edges, f, e, 1)
    assert ee == list(map(tuple, r["expanded_edges"])) and ef == r["expanded_initial_flow"]
    parallel = [len(edges), len(edges)+1]
    assert parallel in x.circuits(n+2, ee)
    assert sorted(move["circuit_edges"]) in x.circuits(n+2, ee)
    paths = []
    for order in ((move["circuit_edges"], parallel), (parallel, move["circuit_edges"])):
        current = ef.copy()
        path = [potential(n+2, ee, current)]
        for circuit in order:
            assert 5 not in {current[j] for j in circuit}
            for j in circuit:
                current[j] ^= 5
            validate(n+2, ee, current)
            path.append(potential(n+2, ee, current))
        assert path == [(2, 16), (2, 18), (0, 14)]
        assert current == r["expanded_final_flow"]
        paths.append(path)
    # This obstruction is to lifting that particular move, not global reachability.
    alt = r["alternative_improving_move"]
    current = ef.copy()
    assert alt["move"]["circuit_edges"] in x.circuits(n+2, ee)
    for j in alt["move"]["circuit_edges"]:
        assert current[j] != alt["move"]["added_value"]
        current[j] ^= alt["move"]["added_value"]
    assert current == alt["flow"] and potential(n+2, ee, current) < (2, 16)
    ds = x.defects_fast(n+2, ee, current)
    assert min(ds) == 0
    cover = x.extra_coordinate_lift(n+2, ee, x.transform(current, ds.index(0)+1))
    assert cover["cover"] is not None
    return {"both_orders_verified": paths, "alternative_improving_move_verified": True,
            "alternative_five_layer_cover": cover}


def even_move_check():
    r = json.loads((HERE / "lex_census_trap_certificate.json").read_text())
    n, edges, f = r["vertices"], r["edges"], r["flow"]
    masks = x.all_even_subgraphs(n, edges)
    assert len(masks) == len(set(masks)) == 512
    cs = {tuple(c) for c in x.circuits(n, edges)}
    counts = Counter()
    hist = Counter()
    for mask in masks[1:]:
        selected = [e for e in range(len(edges)) if mask >> e & 1]
        assert all(sum(v in edges[e] for e in selected) % 2 == 0 for v in range(n))
        for a in range(1, 8):
            if a in {f[e] for e in selected}:
                continue
            g = f.copy()
            for e in selected:
                g[e] ^= a
            validate(n, edges, g)
            p = potential(n, edges, g)
            assert p >= (2, 18)
            counts["circuit" if tuple(selected) in cs else "disconnected_even_subgraph"] += 1
            hist[str(p)] += 1
    assert counts == {"circuit": 175, "disconnected_even_subgraph": 242}
    return {"binary_even_subgraphs_including_empty": len(masks), "allowed_move_counts": dict(counts),
            "neighbor_potential_histogram": dict(sorted(hist.items())), "strict_improvements": 0}


if __name__ == "__main__":
    result = {"parallel_normalization": normalization_checks(),
              "lift_obstruction_verification": verify_lift_obstruction(),
              "even_subgraph_move_check": even_move_check()}
    (HERE / "parallel_reduction_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["parallel_normalization"], indent=2))
    print("Both orders of the failed lift, its alternative cover, and all 417 even-subgraph moves verified.")
