#!/usr/bin/env python3
"""Rank-one boundary completion and its finite Hermitian obstruction model.

The finite classification concerns component rotations and circuit offsets for
a fixed boundary coloring. It is not a nonexistence test for graph-level 5-CDC.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from coupled_completion import WordSystem, from_flow, xor
from five_component_completion import construct, field_rank, words_from_table
import explore as x

HERE = Path(__file__).parent
MUL = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
CONJ = (0, 1, 3, 2)
INV = (0, 1, 3, 2)
TRACE = (0, 0, 1, 1)
STATE = (None, 0, 1, 2)
PAIRS = list(itertools.combinations(range(4), 2))


def factor(system):
    assert field_rank(system.rows, system.t) == 1
    row = next(row for row in system.a if any(row))
    pivot = next(j for j, d in enumerate(row) if d)
    vector = [MUL[INV[row[pivot]]][d] for d in row]
    coefficients = [row[pivot] for row in system.a]
    assert system.a == [[MUL[c][d] for d in vector] for c in coefficients]
    assert xor(coefficients) == xor(vector) == 0
    return vector, coefficients


def conjugation_escape(system):
    """Proved escape when the generator is not proportional to a binary vector."""
    vector, coefficients = factor(system)
    assert any(d > 1 for d in vector)
    nonzero = [k for k, c in enumerate(coefficients) if c]
    assert len(nonzero) in (4, 5)
    pair = next(pair for pair in itertools.combinations(nonzero, 2)
                if coefficients[pair[0]] == coefficients[pair[1]])
    words = [[(k, CONJ[d] if k in pair else d) for k, d in word] for word in system.words]
    changed = WordSystem(words, system.h)
    assert field_rank(changed.rows, changed.t) == 2
    answer = construct(changed)
    assert answer is not None
    return {"conjugated_components": list(pair), "new_boundary_table": changed.a,
            "construction_after_conjugation": answer}


def interaction(words, h):
    matrix = [[0]*h for _ in range(h)]
    for word in words:
        prefix = [0]*h
        for k, d in word:
            for l, value in enumerate(prefix):
                if k != l:
                    matrix[k][l] ^= MUL[d][CONJ[value]]
            prefix[k] ^= d
    assert all(matrix[k][l] == CONJ[matrix[l][k]] for k in range(h) for l in range(h))
    return matrix


def normalize(system):
    vector, coefficients = factor(system)
    assert set(vector) <= {0, 1} and sum(vector) % 2 == 0
    words = [[(k, MUL[INV[coefficients[k]]][d] if coefficients[k] else d)
              for k, d in word] for word in system.words]
    # Normalized words need not be closed until component scalars are chosen.
    active = [int(c != 0) for c in coefficients]
    matrix = interaction(words, system.h)
    pivot = max(k for k, e in enumerate(active) if e)
    order = [k for k, e in enumerate(active) if e and k != pivot]
    order += [k for k, e in enumerate(active) if not e]
    order += [pivot]
    matrix = [[matrix[k][l] for l in order] for k in order]
    active = [active[k] for k in order]
    gauge = [row[-1] for row in matrix]
    reduced = [[0]*system.h for _ in range(system.h)]
    for k in range(system.h):
        for l in range(system.h):
            if k != l:
                reduced[k][l] = matrix[k][l] ^ (CONJ[gauge[l]] if active[k] else 0) ^ (gauge[k] if active[l] else 0)
    assert all(not row[-1] for row in reduced) and not any(reduced[-1])
    return {"generator": vector, "coefficients": coefficients, "active": active,
            "component_order": order, "matrix": matrix, "gauge": gauge, "reduced_matrix": reduced}


def closed_states(active):
    # The last component is active; quotient out simultaneous scalar rotation.
    assert active[-1] == 1
    return [prefix+(1,) for prefix in itertools.product((1, 2, 3), repeat=len(active)-1)
            if xor(d for d, e in zip(prefix+(1,), active) if e) == 0]


def bits(matrix, states):
    return [xor(TRACE[MUL[MUL[a][CONJ[b]]][matrix[k][l]]]
                for l, b in enumerate(states) if l != k) for k, a in enumerate(states)]


def offset_image(active, states, z):
    return [TRACE[MUL[d][z]] if e else 0 for d, e in zip(states, active)]


def model_solutions(matrix, active):
    result = []
    for states in closed_states(active):
        obstruction = bits(matrix, states)
        offsets = [z for z in range(4) if obstruction == offset_image(active, states, z)]
        if offsets:
            result.append({"scalars": list(states), "aggregate_offsets": offsets})
    return result


def signature(matrix, active):
    """Explicit finite obstruction families, checked exhaustively below."""
    assert len(active) == 5 and active[-1] == 1
    m = sum(active)
    if m == 5 and all(matrix[i][j] in (0, 1) for i, j in PAIRS):
        es = [(i, j) for i, j in PAIRS if matrix[i][j]]
        degrees = [sum(i in e for e in es) for i in range(4)]
        if len(es) == 3 and sorted(degrees) == [1, 1, 2, 2]:
            return "binary_four_vertex_path"
    if m == 4:
        assert active == [1, 1, 1, 0, 1]
        triangle = [matrix[i][j] for i, j in itertools.combinations(range(3), 2)]
        star = [matrix[i][3] for i in range(3)]
        if triangle in ([0, 0, 0], [1, 1, 1]) and sorted(star) == [1, 2, 3]:
            return "three_color_star_with_uniform_triangle"
    return None


def analyze(system, verify=False):
    data = normalize(system)
    active, matrix, reduced = data["active"], data["matrix"], data["reduced_matrix"]
    solutions = model_solutions(reduced, active)
    failure = signature(reduced, active)
    assert bool(solutions) == (failure is None)
    witness = None
    examined = 0
    for states in closed_states(active):
        scalars = [0]*system.h
        for k, original in enumerate(data["component_order"]):
            c = data["coefficients"][original]
            scalars[original] = MUL[states[k]][INV[c]] if c else states[k]
        original_states = [STATE[a] for a in scalars]
        predicted = bits(matrix, states)
        reduced_bits = bits(reduced, states)
        z = xor(MUL[CONJ[d]][CONJ[u]] for d, u in zip(states, data["gauge"]))
        assert reduced_bits == [a ^ b for a, b in zip(predicted, offset_image(active, states, z))]
        if verify:
            _, actual = system.integrate(original_states)
            assert predicted == [actual[k] for k in data["component_order"]]
            answer = system.fixed_states(original_states, verify_affine=True)
            assert answer is not None
            assert answer["consistent"] == any(reduced_bits == offset_image(active, states, z) for z in range(4))
            examined += 1
            if witness is None and answer["consistent"]:
                witness = answer
        elif witness is None and any(reduced_bits == offset_image(active, states, z) for z in range(4)):
            witness = system.fixed_states(original_states)
    assert (witness is not None) == bool(solutions)
    return {**data, "active_components": sum(active), "failure_signature": failure,
            "successful_states_modulo_global_rotation": len(solutions),
            "states_verified_by_direct_integration": examined, "witness": witness}


def finite_audit():
    output = []
    for m in range(2, 6):
        active = [1]*(m-1)+[0]*(5-m)+[1]
        counts = Counter(); failures = []
        for labels in itertools.product(range(4), repeat=6):
            matrix = [[0]*5 for _ in range(5)]
            for (i, j), d in zip(PAIRS, labels):
                matrix[i][j] = d; matrix[j][i] = CONJ[d]
            solutions = model_solutions(matrix, active)
            expected = signature(matrix, active)
            assert (not solutions) == (expected is not None)
            counts[len(solutions)] += 1
            if expected:
                failures.append({"upper_triangle": labels, "signature": expected})
        output.append({"active_components": m, "matrices_checked": 4096,
                       "closed_states_modulo_global_rotation": len(closed_states(active)),
                       "success_count_histogram": dict(sorted(counts.items())), "failures": failures})
    assert [len(r["failures"]) for r in output] == [0, 0, 12, 12]
    return output


def random_checks():
    rng = random.Random(20260930)
    counts = Counter(); examples = {}; verified = 0
    for m in range(2, 6):
        for trial in range(400):
            t = rng.randrange(2, 7)
            while True:
                vector = [rng.randrange(2) for _ in range(t)]
                if sum(vector) and sum(vector) % 2 == 0:
                    break
            while True:
                coefficients = [rng.randrange(1, 4) for _ in range(m)]
                if xor(coefficients) == 0:
                    break
            coefficients += [0]*(5-m)
            rng.shuffle(coefficients)
            a = [[MUL[c][d] for d in vector] for c in coefficients]
            system = WordSystem(words_from_table(a, rng), 5)
            result = analyze(system, verify=True)
            key = f"active={m},signature={result['failure_signature']}"
            counts[key] += 1; verified += result["states_verified_by_direct_integration"]
            examples.setdefault(key, {"words": system.words, "analysis": result})
    escaped = 0; escape_example = None
    for trial in range(800):
        t = rng.randrange(3, 7)
        while True:
            vector = [rng.randrange(4) for _ in range(t-1)]
            vector += [xor(vector)]
            nonzero = {d for d in vector if d}
            if len(nonzero) > 1:
                break
        m = rng.choice((4, 5))
        while True:
            coefficients = [rng.randrange(1, 4) for _ in range(m)]
            if xor(coefficients) == 0:
                break
        coefficients += [0]*(5-m)
        rng.shuffle(coefficients)
        a = [[MUL[c][d] for d in vector] for c in coefficients]
        system = WordSystem(words_from_table(a, rng), 5)
        result = conjugation_escape(system)
        escaped += 1
        if escape_example is None:
            escape_example = {"words": system.words, "original_boundary_table": system.a, "escape": result}
    return {"seed": 20260930, "binary_generator_systems": 1600,
            "case_counts": dict(counts), "direct_state_checks": verified, "examples": examples,
            "nonbinary_generator_systems_repaired_by_conjugation": escaped,
            "conjugation_example": escape_example}


def first_flow(n, edges, first):
    incidence = [(sum(1 << e for e in es), 0) for es in x.BASE.incidence(n, edges)]
    for second in x.all_even_subgraphs(n, edges):
        constraints = incidence+[(1 << e, 1) for e in range(len(edges)) if not (first | second) >> e & 1]
        _, third = x.BASE.solve(constraints, len(edges))
        if third is not None:
            return [4*((first >> e)&1)+2*((second >> e)&1)+((third >> e)&1) for e in range(len(edges))]
    raise AssertionError("Saved admissible support has no flow")


def saved_failures():
    old = json.loads((HERE / "first_coordinate_census.json").read_text())
    counts = Counter(); records = []
    for graph in old["graphs"]:
        for f in graph["failed_admissible_first_coordinates"]:
            if len(f["complement_components"]) != 5:
                continue
            n, edges, mask = graph["vertices"], graph["edges"], f["support_mask"]
            flow = first_flow(n, edges, mask)
            system, _, _, _, _ = from_flow(n, edges, flow)
            result = analyze(system, verify=True)
            assert result["failure_signature"] is not None
            counts[result["failure_signature"]] += 1
            records.append({"vertices": n, "graph6": graph.get("graph6"), "first_coordinate_mask": mask,
                            "starting_flow": flow, "boundary_table": system.a,
                            "component_order": result["component_order"],
                            "reduced_matrix": result["reduced_matrix"],
                            "failure_signature": result["failure_signature"]})
    assert len(records) == 215
    return {"supports_checked": len(records), "scope": "One constructed witnessing flow for each saved failed support with five complement components.",
            "signature_counts": dict(counts), "records": records}


def reflect_normalized(system, reflected):
    """Reflect normalized colors but restore the original boundary rows."""
    _, coefficients = factor(system)
    words = []
    for word in system.words:
        out = []
        for k, d in word:
            if k in reflected:
                c = coefficients[k] or 1
                d = MUL[c][CONJ[MUL[INV[c]][d]]]
            out.append((k, d))
        words.append(out)
    result = WordSystem(words, system.h)
    assert result.a == system.a
    return result


def reflection_example():
    rng = random.Random(20261001)
    a = [[c, c] for c in (1, 1, 1, 2, 3)]
    for trial in range(1, 20001):
        system = WordSystem(words_from_table(a, rng), 5)
        start = analyze(system)
        if start["failure_signature"] is None:
            continue
        for k in range(5):
            changed = reflect_normalized(system, [k])
            result = analyze(changed, verify=True)
            if result["witness"] is not None:
                return {"seed": 20261001, "trials_to_example": trial,
                        "scope": "An abstract word system; graph realization is not asserted.",
                        "words": system.words, "rotation_only_analysis": start,
                        "reflected_component": k, "reflected_words": changed.words,
                        "analysis_after_reflection": result}
    raise AssertionError("No reflection escape found within the stated search")


def graph_reflection_example():
    """A 26-vertex graph separates cyclic recoloring from all permutations."""
    from functools import lru_cache
    import networkx as nx
    from balanced_completion import rotate
    from coupled_completion import enumerate_offsets
    from verify_lex_trap import valid_flow, defects

    # Seeded search 992 found these orders on its 51st trial. Each of the first
    # two components has six leaves; the remaining three are matching edges.
    words = [[(2,1),(1,2),(3,2),(0,1),(4,3),(1,1),(1,2),(0,2),(0,2)],
             [(2,1),(0,1),(1,2),(4,3),(3,2),(0,2),(1,1),(0,2),(1,2)]]
    pending = [[] for _ in range(5)]; edges = []; colors = []; next_vertex = 0
    for word in words:
        vertices = list(range(next_vertex, next_vertex+len(word)))
        next_vertex += len(word); prefix = 0
        for i, (k, d) in enumerate(word):
            pending[k].append((vertices[i], d))
            prefix ^= d
            edges.append((vertices[i], vertices[(i+1) % len(word)])); colors.append(prefix)
        assert prefix == 0
    first = (1 << len(edges))-1

    @lru_cache(None)
    def tree_plan(counts):
        if sum(counts) == 2:
            return () if max(counts) == 2 else None
        for a, b in itertools.combinations((1, 2, 3), 2):
            if counts[a-1] and counts[b-1]:
                new = list(counts); new[a-1] -= 1; new[b-1] -= 1; new[(a ^ b)-1] += 1
                tail = tree_plan(tuple(new))
                if tail is not None:
                    return ((a, b),)+tail
        return None

    for leaves in pending:
        plan = tree_plan(tuple(sum(d == c for _, d in leaves) for c in (1, 2, 3)))
        assert plan is not None
        for a, b in plan:
            u = next(item for item in leaves if item[1] == a); leaves.remove(u)
            v = next(item for item in leaves if item[1] == b); leaves.remove(v)
            edges.extend(((u[0], next_vertex), (v[0], next_vertex))); colors.extend((a, b))
            leaves.append((next_vertex, a ^ b)); next_vertex += 1
        assert len(leaves) == 2 and leaves[0][1] == leaves[1][1]
        edges.append((leaves[0][0], leaves[1][0])); colors.append(leaves[0][1])
    n = next_vertex
    assert n == 26
    graph = nx.Graph(edges)
    assert len(edges) == graph.number_of_edges() and nx.is_connected(graph) and not list(nx.bridges(graph))
    f = [d+4*((first >> e)&1) for e, d in enumerate(colors)]
    valid_flow(n, edges, f)
    system, _, hc, which, circuits = from_flow(n, edges, f)
    initial = analyze(system, verify=True)
    assert initial["failure_signature"] == "binary_four_vertex_path"
    reflected = which[3]  # Vertex 3 is the first occurrence of original component 0.
    changed = reflect_normalized(system, [reflected])
    answer = analyze(changed, verify=True)
    witness = answer["witness"]
    assert witness is not None
    _, coefficients = factor(system)
    result = [0]*len(edges)
    for e, (u, _) in enumerate(edges):
        if first >> e & 1:
            continue
        k = which[u]; d = f[e] & 3
        if k == reflected:
            c = coefficients[k] or 1
            d = MUL[c][CONJ[MUL[INV[c]][d]]]
        result[e] = rotate(d, witness["states"][k])
    for (_, es), values in zip(circuits, witness["circuit_colors"]):
        for e, d in zip(es, values):
            result[e] = 4+d
    valid_flow(n, edges, result)
    assert defects(n, edges, result)[3] == 0
    lift = x.extra_coordinate_lift(n, edges, result)
    cover = lift["cover"]
    assert cover is not None and cover["4"] == [e for e in range(len(edges)) if first >> e & 1]
    assert all(sum(e in layer for layer in cover.values()) == 2 for e in range(len(edges)))
    assert all(sum(e in layer for e in es) in (0, 2) for es in x.BASE.incidence(n, edges) for layer in cover.values())
    before, after = enumerate_offsets(system), enumerate_offsets(changed)
    assert before["successful_pairs"] == 0 and after["successful_pairs"] > 0
    return {"vertices": n, "edges": edges, "starting_flow": f, "first_coordinate_mask": first,
            "complement_components": hc, "original_analysis": initial,
            "reflected_component": reflected, "analysis_after_reflection": answer,
            "direct_offset_enumeration_before": before, "direct_offset_enumeration_after": after,
            "repaired_flow": result, "verified_lift": lift,
            "simple_connected_bridgeless_cubic_verified": True,
            "decoded_cover_edge_multiplicity_and_even_degrees_verified": True}


if __name__ == "__main__":
    result = {}
    for name, function in (("finite_audit", finite_audit), ("random_checks", random_checks),
                           ("saved_failures", saved_failures), ("reflection_example", reflection_example),
                           ("graph_reflection_example", graph_reflection_example)):
        result[name] = function()
        print(name, "complete", flush=True)
    (HERE / "rank_one_obstruction_results.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Failure signatures:", result["saved_failures"]["signature_counts"])
    print("Random cases:", result["random_checks"]["case_counts"])
