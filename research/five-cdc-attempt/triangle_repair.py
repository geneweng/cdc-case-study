#!/usr/bin/env python3
"""Verify the proved triangle-flattening reduction; see repair-obstruction.md."""
from collections import Counter
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import explore as x
from exhaustive_repair import OrbitSearch, subspaces

HERE = Path(__file__).parent


def cross(a, b):
    av = [(a >> i) & 1 for i in range(3)]
    bv = [(b >> i) & 1 for i in range(3)]
    return sum(((av[(i+1) % 3] * bv[(i+2) % 3]) ^
                (av[(i+2) % 3] * bv[(i+1) % 3])) << i for i in range(3))


def normal_identity(n, edges, f):
    incidence = x.BASE.incidence(n, edges)
    normals = [cross(f[es[0]], f[es[1]]) for es in incidence]
    assert all(normals)
    internal, ds = 0, []
    for l in range(1, 8):
        components = x.components(n, edges, f, l)
        for c in components:
            charge = 0
            for v in c["vertices"]:
                charge ^= normals[v]
            assert charge == (l if c["obstruction"] else 0)
            if any(normals[v] == l for v in c["vertices"]):
                internal += c["obstruction"]
            else:
                assert len(c["vertices"]) == 2
                u, v = c["vertices"]
                assert c["obstruction"] == int(normals[u] != normals[v])
        ds.append(sum(c["obstruction"] for c in components))
    disagreements = sum(normals[u] != normals[v] for u, v in edges)
    assert sum(ds) == disagreements + internal
    return {"vertex_normals": normals, "defects": ds,
            "edges_with_unequal_normals": disagreements, "remaining_obstructed_components": internal}


def triangle_data(edges, f, triangle):
    inside, external = [], {}
    for e, (u, v) in enumerate(edges):
        if u in triangle and v in triangle:
            inside.append(e)
        elif u in triangle:
            external[u] = e
        elif v in triangle:
            external[v] = e
    assert len(inside) == 3 and len(external) == 3
    difference = []
    for e in inside:
        u, v = edges[e]
        opposite = next(w for w in triangle if w not in (u, v))
        difference.append(f[e] ^ f[external[opposite]])
    assert len(set(difference)) == 1
    return inside, external, difference[0]


def flatten(edges, f, triangle):
    inside, _, added = triangle_data(edges, f, triangle)
    g = f.copy()
    if added:
        assert added not in {f[e] for e in inside}
        for e in inside:
            g[e] ^= added
    assert triangle_data(edges, g, triangle)[2] == 0
    return g, {"circuit_edges": inside, "added_value": added}


def contract(n, edges, f, triangle):
    retained = [e for e, (u, v) in enumerate(edges) if not (u in triangle and v in triangle)]
    representatives = sorted(set(range(n)) - set(triangle[1:]))
    renumber = {v: i for i, v in enumerate(representatives)}
    mapping = {v: renumber[triangle[0] if v in triangle else v] for v in range(n)}
    contracted = [(mapping[edges[e][0]], mapping[edges[e][1]]) for e in retained]
    return n - 2, contracted, [f[e] for e in retained], retained, mapping[triangle[0]]


def lift_move(edges, f, triangle, retained, change):
    inside, external, difference = triangle_data(edges, f, triangle)
    assert difference == 0
    circuit = [retained[e] for e in change["circuit_edges"]]
    ports = [v for v, e in external.items() if e in circuit]
    assert len(ports) in (0, 2)
    if ports:
        third = next(v for v in triangle if v not in ports)
        circuit += [e for e in inside if third in edges[e]]
    added = change["added_value"]
    assert added not in {f[e] for e in circuit}
    g = f.copy()
    for e in circuit:
        g[e] ^= added
    assert triangle_data(edges, g, triangle)[2] == 0
    return g, {"circuit_edges": sorted(circuit), "added_value": added}


def small_checks():
    records = json.loads((HERE / "exhaustive_repair_results.json").read_text())["graphs"]
    classes = extensions = nonflat = 0
    delta_hist = Counter()
    for record in records:
        n, edges = record["vertices"], record["edges"]
        if n > 8:
            continue
        search = OrbitSearch(n, edges)
        for rank in (2, 3):
            for rows in subspaces(search.r, rank):
                f = search.flow(rows)
                if 0 in f:
                    continue
                classes += 1
                ds = normal_identity(n, edges, f)["defects"]
                for v in range(n):
                    incident = [e for e, pair in enumerate(edges) if v in pair]
                    ports = [v, n, n+1]
                    expanded = list(map(tuple, edges))
                    for port, e in zip(ports, incident):
                        u, w = edges[e]
                        expanded[e] = (port, w) if u == v else (u, port)
                    expanded += [(v, n), (v, n+1), (n, n+1)]
                    a, b, c = [f[e] for e in incident]
                    assert a ^ b ^ c == 0
                    for q in range(1, 8):
                        if q in (a, b):
                            continue
                        ef = f + [q, q ^ a, q ^ b]
                        before = x.defects_fast(n+2, expanded, ef)
                        ff, move = flatten(expanded, ef, ports)
                        after = x.defects_fast(n+2, expanded, ff)
                        assert after == ds
                        assert all(old-new in (0, 2) for old, new in zip(before, after))
                        if move["added_value"]:
                            nonflat += 1
                        extensions += 1
                        delta_hist[sum(before)-sum(after)] += 1
    assert classes == 195 and extensions == 7610 and nonflat == 6088
    return {"base_flow_classes": classes, "all_five_triangle_extensions_at_each_vertex": extensions,
            "nonflat_extensions": nonflat, "sum_defect_decrease_histogram": dict(sorted(delta_hist.items())),
            "componentwise_monotonicity_and_contraction_identity_verified": True}


def trap_example():
    saved = json.loads((HERE / "lex_census_trap_certificate.json").read_text())
    n, edges, f = saved["vertices"], saved["edges"], saved["flow"]
    triangle = [0, 7, 9]
    identity = normal_identity(n, edges, f)
    ff, first = flatten(edges, f, triangle)
    assert first["added_value"] == 4
    assert x.defects_fast(n, edges, ff) == saved["defects"]
    cn, ce, cf, retained, vertex = contract(n, edges, ff, triangle)
    assert cn == 14 and x.defects_fast(cn, ce, cf) == saved["defects"]
    cs = x.circuits(cn, ce)
    path = []
    for _ in range(100):
        old_ds = x.defects_fast(cn, ce, cf)
        old = min(old_ds), sum(old_ds)
        if not old[0]:
            break
        improvement = None
        for g, change in x.neighbors(cf, cs):
            gd = x.defects_fast(cn, ce, g)
            if (min(gd), sum(gd)) < old:
                improvement = g, change, gd
                break
        assert improvement is not None
        g, change, gd = improvement
        ff, lifted_move = lift_move(edges, ff, triangle, retained, change)
        assert sorted(lifted_move["circuit_edges"]) in x.circuits(n, edges)
        assert x.defects_fast(n, edges, ff) == gd
        path.append({"contracted_move": change, "lifted_move": lifted_move,
                     "contracted_flow": g, "expanded_flow": ff.copy(), "defects": gd})
        cf = g
    else:
        raise AssertionError("Unexpectedly long finite descent")
    ds = x.defects_fast(n, edges, ff)
    assert min(ds) == 0
    normal = ds.index(0) + 1
    cover = x.extra_coordinate_lift(n, edges, x.transform(ff, normal))
    assert cover["cover"] is not None
    return {"triangle": triangle, "normal_identity": identity, "flattening_move": first,
            "flattening_preserves_all_seven_defect_counts": True, "contracted_vertices": cn,
            "contracted_edges": ce, "contracted_vertex": vertex,
            "initial_contracted_flow": [saved["flow"][e] for e in retained],
            "lifted_repair_path": path, "final_lift": cover}


if __name__ == "__main__":
    result = {"small_extension_checks": small_checks(), "trap_triangle_repair": trap_example()}
    (HERE / "triangle_repair_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["small_extension_checks"], indent=2))
    print("Triangle example: neutral flattening, then",
          len(result["trap_triangle_repair"]["lifted_repair_path"]), "lifted moves to a verified five-cover")
