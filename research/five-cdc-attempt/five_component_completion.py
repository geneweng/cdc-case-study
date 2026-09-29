#!/usr/bin/env python3
"""Five complement components with boundary rank at least two over F_4.

See five-component-completion.md for the proof and its limits. This does not
prove the general five-cycle double cover conjecture.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from coupled_completion import (WordSystem, binary_rank, enumerate_offsets,
                                from_flow, graph_witness, rotate_row, xor)
from balanced_completion import rotate
import explore as x

HERE = Path(__file__).parent


def field_rank(rows, width):
    """F_4 span is the binary span of rows and their scalar multiples."""
    rank = binary_rank(rows + [rotate_row(r, 1, width) for r in rows])
    assert rank % 2 == 0
    return rank // 2


def field_rank_direct(rows, width):
    """Independent F_4 Gaussian elimination, used to audit rank conversion."""
    multiplication = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
    inverse = (0, 1, 3, 2)
    matrix = [[(row >> (2*j)) & 3 for j in range(width)] for row in rows]
    rank = 0
    for j in range(width):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scalar = inverse[matrix[rank][j]]
        matrix[rank] = [multiplication[scalar][v] for v in matrix[rank]]
        for i in range(rank+1, len(matrix)):
            scalar = matrix[i][j]
            matrix[i] = [a ^ multiplication[scalar][b] for a, b in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def classify(rows, width):
    assert len(rows) == 5 and xor(rows) == 0
    rank = binary_rank(rows)
    r4 = field_rank(rows, width)
    answer = {"binary_rank": rank, "field_rank": r4}
    if r4 < 2:
        return {**answer, "case": "outside_rank_hypothesis"}
    if rank == 4:
        return {**answer, "case": "full_offset_rank"}
    if rank == 3:
        # Nullity two: any proper nonzero dependency partitions the rows into
        # two minimal dependencies, of sizes 1+4 or 2+3.
        p = next([k for k in range(5) if mask >> k & 1]
                 for mask in range(1, 31)
                 if xor(rows[k] for k in range(5) if mask >> k & 1) == 0)
        q = [k for k in range(5) if k not in p]
        if len(p) > len(q):
            p, q = q, p
        assert all(binary_rank([rows[k] for k in g]) == len(g)-1 for g in (p, q))
        if len(p) == 1:
            return {**answer, "case": "stable_direct_sum", "groups": [p, q]}
        assert len(p) == 2 and rows[p[0]] == rows[p[1]]
        v = rows[p[0]]
        intersection = [(s, k) for s in (1, 2) for k in q
                        if rotate_row(v, s, width) == rows[k]]
        assert len(intersection) <= 1
        if not intersection:
            return {**answer, "case": "stable_direct_sum", "groups": [p, q]}
        state, k = intersection[0]
        states = [state if i in p else 0 for i in range(5)]
        return {**answer, "case": "normalize_to_triple", "preliminary_states": states,
                "triple": sorted(p+[k])}
    assert rank == 2
    counts = Counter(rows)
    triple = next(([i for i, v in enumerate(rows) if v == r]
                   for r, count in counts.items() if r and count == 3), None)
    if triple is not None:
        return {**answer, "case": "triple_pattern", "triple": triple}
    groups = [[i] for i, r in enumerate(rows) if not r]
    nonzero = {r: [i for i, v in enumerate(rows) if v == r] for r in counts if r}
    if len(nonzero) == 2:
        assert all(len(g) == 2 for g in nonzero.values())
        groups += list(nonzero.values())
    else:
        assert len(nonzero) == 3 and all(len(g) == 1 for g in nonzero.values())
        groups += [sorted(i for g in nonzero.values() for i in g)]
    return {**answer, "case": "stable_direct_sum", "groups": groups}


def construct(system):
    """Follow the proof's cases, rather than doing unrestricted search."""
    assert system.h == 5
    case = classify(system.rows, system.t)
    if case["case"] == "outside_rank_hypothesis":
        return None
    zero = [0]*5
    examined = 0

    def solve(states):
        nonlocal examined
        examined += 1
        return system.fixed_states(states, verify_affine=True)

    if case["case"] == "full_offset_rank":
        witness = solve(zero)
        route = "full_offset_rank"
    elif case["case"] == "stable_direct_sum":
        groups = case["groups"]
        witness = None
        for choices in itertools.product(range(3), repeat=len(groups)):
            states = [0]*5
            for group, state in zip(groups, choices):
                for k in group:
                    states[k] = state
            result = solve(states)
            assert result is not None
            assert result["rank"] == 5-len(groups)
            if result["consistent"]:
                witness = result
                break
        route = "stable_direct_sum"
    else:
        pre = case.get("preliminary_states", zero)
        triple = case["triple"]
        normalized = [rotate_row(r, s, system.t) for r, s in zip(system.rows, pre)]
        v = normalized[triple[0]]
        others = [k for k in range(5) if k not in triple]
        assert all(normalized[k] == v for k in triple)
        assert xor(normalized[k] for k in others) == v
        assert field_rank([v, normalized[others[0]]], system.t) == 2
        witness = None
        for pair in itertools.combinations(triple, 2):
            for a, b in itertools.permutations(range(3), 2):
                states = [(pre[k]+(a if k in pair else b)) % 3 for k in range(5)]
                result = solve(states)
                assert result is not None and result["rank"] == 3
                if result["consistent"]:
                    witness = result
                    break
            if witness is not None:
                break
        if witness is None:
            witness = solve(pre)
            assert witness["rank"] == 2
            route = "triple_common_state_fallback"
        else:
            route = "triple_unequal_group_states"
    assert witness is not None and witness["consistent"]
    return {"proof_case": case, "construction_route": route,
            "closed_states_examined": examined, "witness": witness}


def words_from_table(a, rng):
    words = []
    for j in range(len(a[0])):
        word = []
        for k, row in enumerate(a):
            if row[j]:
                word.append((k, row[j]))
            # Cancelling pairs test many orders with the same boundary data.
            for _ in range(rng.randrange(1, 3)):
                d = rng.randrange(1, 4)
                word.extend([(k, d), (k, d)])
        rng.shuffle(word)
        words.append(word)
    return words


def audit_tables():
    counts = Counter()
    possible = [a + (b << 2) + ((a ^ b) << 4) for a in range(4) for b in range(4)]
    for first in itertools.product(possible, repeat=4):
        rows = list(first)+[xor(first)]
        case = classify(rows, 3)
        assert case["field_rank"] == field_rank_direct(rows, 3)
        counts[case["case"]] += 1
        if case["case"] == "stable_direct_sum":
            groups = case["groups"]
            for states in itertools.product(range(3), repeat=len(groups)):
                transformed = [rotate_row(rows[k], states[g], 3)
                               for g, group in enumerate(groups) for k in group]
                assert xor(transformed) == 0
                assert binary_rank(transformed) == 5-len(groups)
        if case["case"] == "normalize_to_triple":
            transformed = [rotate_row(r, s, 3) for r, s in zip(rows, case["preliminary_states"])]
            assert xor(transformed) == 0 and binary_rank(transformed) == 2
    assert sum(counts.values()) == 65536
    return {"tables_checked": 65536, "scope": "Every 5 by 3 F_4 table with zero row and column sums.",
            "case_counts": dict(counts), "all_stable_group_rotations_checked": True,
            "field_rank_verified_by_independent_F4_elimination": True}


def word_checks():
    rng = random.Random(20260929)
    counts = Counter(); routes = Counter(); outcomes = Counter(); examples = {}
    for _ in range(6000):
        t = rng.randrange(2, 7)
        a = [[rng.randrange(4) for _ in range(t-1)] for _ in range(4)]
        a = [row+[xor(row)] for row in a]
        a.append([xor(row[j] for row in a) for j in range(t)])
        system = WordSystem(words_from_table(a, rng), 5)
        result = construct(system)
        if result is None:
            answer = system.search(exhaustive=True, verify_affine=True)
            outcomes[f"rank_below_two,success={answer['witness'] is not None}"] += 1
            continue
        counts[result["proof_case"]["case"]] += 1
        routes[result["construction_route"]] += 1
        outcomes["theorem_applies,success=True"] += 1
        key = result["proof_case"]["case"]+":"+result["construction_route"]
        examples.setdefault(key, {"words": system.words, "boundary_table": system.a, "construction": result})
    return {"seed": 20260929, "systems_checked": 6000, "case_counts": dict(counts),
            "route_counts": dict(routes), "outcomes": dict(outcomes), "examples": examples,
            "offset_coefficients_verified_by_direct_integration": True}


def make_graph(orders, row_colors):
    """Realize rows by three-leaf stars or same-colored single edges."""
    t = len(row_colors[0]); vertices = {}; edges = []; q = []; next_vertex = 0
    for j, order in enumerate(orders):
        assert set(order) == {k for k in range(5) if row_colors[k][j]}
        assert len(order) >= 3
        for k in order:
            vertices[k, j] = next_vertex
            next_vertex += 1
        prefix = 0
        for i, k in enumerate(order):
            prefix ^= row_colors[k][j]
            edges.append((vertices[k, j], vertices[order[(i+1) % len(order)], j]))
            q.append(prefix)
        assert prefix == 0
    first = (1 << len(edges))-1
    for k, row in enumerate(row_colors):
        js = [j for j in range(t) if row[j]]
        if len(js) == 2:
            assert row[js[0]] == row[js[1]]
            edges.append(tuple(vertices[k, j] for j in js)); q.append(row[js[0]])
        else:
            assert len(js) == 3 and set(row[j] for j in js) == {1, 2, 3}
            center = next_vertex; next_vertex += 1
            for j in js:
                edges.append((vertices[k, j], center)); q.append(row[j])
    f = [d+4*((first >> e) & 1) for e, d in enumerate(q)]
    return next_vertex, edges, f


def graph_checks():
    import networkx as nx
    cases = Counter(); routes = Counter(); examples = {}; checked = 0
    templates = [([[1, 2, 3]]*3+[[1, 1, 0], [0, 3, 3]]),
                 ([[1, 2, 3]]*3+[[1, 3, 2], [0, 1, 1]])]
    for rows in templates:
        supports = [[k for k in range(5) if rows[k][j]] for j in range(3)]
        # Fix the first order, fix one position on each remaining circuit.
        for tails in itertools.product(*(itertools.permutations(s[1:]) for s in supports[1:])):
            orders = [supports[0]]+[[s[0]]+list(tail) for s, tail in zip(supports[1:], tails)]
            n, edges, f = make_graph(orders, rows)
            graph = nx.Graph(edges)
            assert len(edges) == graph.number_of_edges() and nx.is_connected(graph)
            assert not list(nx.bridges(graph))
            system, first, hc, which, circuits = from_flow(n, edges, f)
            assert len(hc) == 5 and system.t == 3
            result = construct(system)
            repaired = graph_witness(n, edges, f, system, first, which, circuits, result["witness"])
            # Verify the decoded layers directly, independently of matrix ranks.
            cover = repaired["lift"]["cover"]
            inc = x.BASE.incidence(n, edges)
            assert all(sum(e in es for es in cover.values()) == 2 for e in range(len(edges)))
            assert all(sum(e in layer for e in es) % 2 == 0 for es in inc for layer in cover.values())
            checked += 1; cases[n] += 1; routes[result["construction_route"]] += 1
            key = str(n)+":"+result["construction_route"]
            if key not in examples:
                exhaustive = system.search(exhaustive=True, verify_affine=True)
                direct = enumerate_offsets(system)
                assert direct["successful_pairs"] == exhaustive["successful_rotation_offset_pairs"]
                examples[key] = {"vertices": n, "edges": edges, "starting_flow": f,
                    "first_coordinate_mask": first, "boundary_table": system.a,
                    "construction": result, "exhaustive_search": exhaustive,
                    "independent_offset_enumeration": direct, "repaired": repaired}
    return {"instances_checked": checked, "counts_by_vertices": dict(cases),
            "scope": "Two specified families of circuit orders, with labeled duplicates possible; not a census of all graphs.",
            "route_counts": dict(routes), "examples": examples,
            "all_graphs_simple_connected_bridgeless_and_cubic_verified": True,
            "every_decoded_cover_directly_verified": True}


def three_circuit_failures():
    """Independently inspect every labeled low flow on the six saved exceptions."""
    old = json.loads((HERE / "first_coordinate_census.json").read_text())
    records = []
    for graph in old["graphs"]:
        for first in graph["failed_admissible_first_coordinates"]:
            if len(first["complement_components"]) != 5 or len(first["support_components"]) != 3:
                continue
            n, edges = graph["vertices"], graph["edges"]
            mask = first["support_mask"]
            basis = x.BASE.cycle_basis(n, edges)
            counts = Counter(); admissible = 0; seen = set(); example = None
            for coefficients in itertools.product(range(4), repeat=len(basis)):
                q = [0]*len(edges)
                for circuit, color in zip(basis, coefficients):
                    for e in circuit:
                        q[e] ^= color
                if any(not a for e, a in enumerate(q) if not mask >> e & 1):
                    continue
                admissible += 1
                key = tuple(a for e, a in enumerate(q) if not mask >> e & 1)
                f = [a+4*((mask >> e) & 1) for e, a in enumerate(q)]
                assert x.defect(n, edges, f, 4) > 0
                if key in seen:
                    continue
                seen.add(key)
                system, _, hc, _, _ = from_flow(n, edges, f)
                rank = field_rank(system.rows, system.t)
                assert rank == 1
                counts[rank] += 1
                if example is None:
                    answer = system.search(exhaustive=True, verify_affine=True)
                    assert answer["witness"] is None
                    example = {"starting_flow": f, "boundary_table": system.a, "exhaustive_search": answer}
            assert admissible == first["admissible_flows"] and not first["successful_flows"]
            records.append({"vertices": n, "edges": edges, "graph6": graph["graph6"],
                            "first_coordinate_mask": mask, "labeled_low_flows_examined": 4**len(basis),
                            "admissible_low_flows": admissible, "distinct_restrictions": len(seen),
                            "field_rank_counts": dict(counts), "every_admissible_flow_obstructed": True,
                            "example": example})
    assert len(records) == 6
    return records


if __name__ == "__main__":
    result = {}
    for name, function in (("boundary_table_audit", audit_tables), ("word_checks", word_checks),
                           ("graph_checks", graph_checks), ("three_circuit_failures", three_circuit_failures)):
        result[name] = function()
        print(name, "complete", flush=True)
    (HERE / "five_component_completion_results.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Table cases:", result["boundary_table_audit"]["case_counts"])
    print("Word routes:", result["word_checks"]["route_counts"])
    print("Graph routes:", result["graph_checks"]["route_counts"])
