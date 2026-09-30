#!/usr/bin/env python3
"""Full component-color permutations and a finite layer-selection experiment.

The matrix classification is computer-assisted. The graph-level existence of
a suitable prescribed layer is not proved. See component-permutations.md.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from coupled_completion import WordSystem, from_flow, graph_witness, xor
from five_component_completion import construct, field_rank, words_from_table
from rank_one_obstruction import (CONJ, INV, MUL, analyze, factor, normalize,
                                  reflect_normalized, signature)
from verify_lex_trap import valid_flow, defects
import explore as x

HERE = Path(__file__).parent
PAIRS = list(itertools.combinations(range(5), 2))


def reduce_pair(d, e, active):
    u = [row[-1] for row in d]
    dd = [[0]*5 for _ in range(5)]; ee = [[0]*5 for _ in range(5)]
    for i, j in PAIRS:
        dd[i][j] = d[i][j] ^ (CONJ[u[j]] if active[i] else 0) ^ (u[i] if active[j] else 0)
        dd[j][i] = CONJ[dd[i][j]]
        ee[i][j] = ee[j][i] = e[i][j] ^ (u[j] if active[i] else 0) ^ (u[i] if active[j] else 0)
    assert all(not row[-1] for row in dd)
    return dd, ee


def pair_from_words(system):
    data = normalize(system)
    _, coefficients = factor(system)
    e = [[0]*5 for _ in range(5)]
    for word in system.words:
        prefix = [0]*5
        for k, color in word:
            color = MUL[INV[coefficients[k]]][color] if coefficients[k] else color
            for l, value in enumerate(prefix):
                if k != l:
                    e[k][l] ^= MUL[color][value]
            prefix[k] ^= color
    assert all(e[i][j] == e[j][i] for i in range(5) for j in range(5))
    order = data["component_order"]
    e = [[e[i][j] for j in order] for i in order]
    return data["matrix"], e, data["active"], order


def reflect_matrix(d, e, reflected):
    result = [[0]*5 for _ in range(5)]
    for i, j in PAIRS:
        if reflected[i] == reflected[j]:
            value = CONJ[d[i][j]] if reflected[i] else d[i][j]
        else:
            value = CONJ[e[i][j]] if reflected[i] else e[i][j]
        result[i][j] = value; result[j][i] = CONJ[value]
    return result


def reduced_signature(d, active):
    u = [row[-1] for row in d]
    reduced = [[0 if i == j else d[i][j] ^ (CONJ[u[j]] if active[i] else 0) ^ (u[i] if active[j] else 0)
                for j in range(5)] for i in range(5)]
    return signature(reduced, active)


def stable_form(d, e, active):
    if signature(d, active) is None:
        return None
    for eta in (0, 1):
        if all(e[i][j] == (CONJ[d[i][j]] ^ (eta*active[i]*active[j])) for i, j in PAIRS):
            return eta
    return None


def full_analysis(system, verify_words=False):
    d, e, active, order = pair_from_words(system)
    rd, re = reduce_pair(d, e, active)
    expected = stable_form(rd, re, active)
    outcomes = Counter(); first = None; comparisons = 0
    # Every reflection subset or its complement has size at most two. Global
    # conjugation preserves feasibility, so these 16 subsets are exhaustive.
    for size in range(3):
        for indices in itertools.combinations(range(5), size):
            mask = [int(i in indices) for i in range(5)]
            changed = reflect_matrix(d, e, mask)
            obstruction = reduced_signature(changed, active)
            outcomes[str(obstruction)] += 1
            original_indices = [order[i] for i in indices]
            if verify_words:
                words = reflect_normalized(system, original_indices)
                actual, _, aa, oo = pair_from_words(words)
                assert actual == changed and aa == active and oo == order
                comparisons += 1
            if obstruction is None and first is None:
                words = reflect_normalized(system, original_indices)
                completion = analyze(words, verify=True)
                assert completion["witness"] is not None
                first = {"reflected_components": original_indices,
                         "cyclic_completion_after_reflection": completion["witness"]}
    assert (first is None) == (expected is not None)
    return {"active_components": sum(active), "component_order": order,
            "reduced_D": rd, "reduced_E": re,
            "persistent_form_eta": expected,
            "reflection_class_outcomes": dict(outcomes), "first_completion": first,
            "reflected_matrices_checked_against_words": comparisons}


def canonical_matrix(m):
    active = [1]*(m-1)+[0]*(5-m)+[1]
    d = [[0]*5 for _ in range(5)]
    if m == 5:
        for i, j in ((0, 1), (1, 2), (2, 3)):
            d[i][j] = d[j][i] = 1
    else:
        assert m == 4
        for i, a in enumerate((1, 2, 3)):
            d[i][3] = a; d[3][i] = CONJ[a]
    return d, active


def finite_classification():
    records = []
    for m in (4, 5):
        d, active = canonical_matrix(m)
        incident = []; allowed = []
        for k in range(5):
            neighbors = [j for j in range(5) if j != k]
            incident.append([PAIRS.index(tuple(sorted((k, j)))) for j in neighbors])
            permitted = set()
            for entries in itertools.product(range(4), repeat=4):
                changed = [row[:] for row in d]
                for j, value in zip(neighbors, entries):
                    changed[k][j] = CONJ[value]; changed[j][k] = value
                if reduced_signature(changed, active) is not None:
                    permitted.add(entries)
            allowed.append(permitted)
        survivors = []
        for entries in itertools.product(range(4), repeat=10):
            if all(tuple(entries[index] for index in incident[k]) in allowed[k] for k in range(5)):
                survivors.append(entries)
        stable = []; orbit_counts = Counter(); survivor_records = []
        for entries in survivors:
            e = [[0]*5 for _ in range(5)]
            for (i, j), value in zip(PAIRS, entries):
                e[i][j] = e[j][i] = value
            bad = 0; good_masks = []
            for prefix in itertools.product(range(2), repeat=4):
                mask = prefix+(0,)
                failed = reduced_signature(reflect_matrix(d, e, mask), active) is not None
                bad += failed
                if not failed:
                    good_masks.append(list(mask))
            eta = stable_form(d, e, active)
            assert (bad == 16) == (eta is not None)
            orbit_counts[bad] += 1
            if bad == 16:
                stable.append({"E_upper_triangle": list(entries), "eta": eta})
            survivor_records.append({"E_upper_triangle": list(entries), "bad_reflection_classes": bad,
                                     "successful_reflection_masks": good_masks})
        assert len(stable) == 2
        records.append({"active_components": m, "canonical_D": d, "active": active,
                        "symmetric_E_matrices_enumerated": 4**10,
                        "per_vertex_allowed_single_reflection_patterns": list(map(len, allowed)),
                        "surviving_all_single_reflections": len(survivors),
                        "survivor_orbit_histogram": dict(orbit_counts),
                        "persistent_pairs": stable, "single_reflection_survivors": survivor_records})
    return records


def random_word_checks():
    rng = random.Random(20261002); counts = Counter(); examples = {}; comparisons = 0
    for m in (4, 5):
        for _ in range(250):
            t = rng.randrange(2, 6)
            while True:
                vector = [rng.randrange(2) for _ in range(t)]
                if sum(vector) and sum(vector) % 2 == 0:
                    break
            while True:
                cs = [rng.randrange(1, 4) for _ in range(m)]
                if xor(cs) == 0:
                    break
            cs += [0]*(5-m)
            a = [[MUL[c][v] for v in vector] for c in cs]
            system = WordSystem(words_from_table(a, rng), 5)
            answer = full_analysis(system, verify_words=True)
            first = answer["first_completion"]
            key = "persistent" if first is None else f"reflections={len(first['reflected_components'])}"
            counts[key] += 1; comparisons += answer["reflected_matrices_checked_against_words"]
            examples.setdefault(key, {"words": system.words, "analysis": answer})
    return {"seed": 20261002, "word_systems_checked": 500,
            "matrix_word_comparisons": comparisons, "counts": dict(counts), "examples": examples}


def realize_pair(d, e, active):
    """Realize any pair by words; no cubic-graph realization is asserted."""
    coefficients = [1, 1, 1, 2, 3] if sum(active) == 5 else [1, 1, 1, 0, 1]
    assert [int(c != 0) for c in coefficients] == active and xor(coefficients) == 0
    base = [(k, c) for k, c in enumerate(coefficients) if c]
    words = [base[:], base[:]]
    for k, c in enumerate(coefficients):
        if not c:
            words[0].extend([(k, 1), (k, 1)])
    tensors = list(itertools.product((1, 2), repeat=2))
    representations = {}
    for mask in range(16):
        dd = ee = 0
        for bit, (a, b) in enumerate(tensors):
            if mask >> bit & 1:
                dd ^= MUL[a][CONJ[b]]; ee ^= MUL[a][b]
        assert (dd, ee) not in representations
        representations[dd, ee] = mask
    for i, j in PAIRS:
        mask = representations[d[i][j], e[i][j]]
        for bit, (a, b) in enumerate(tensors):
            if mask >> bit & 1:
                aa = MUL[coefficients[i] or 1][a]
                bb = MUL[coefficients[j] or 1][b]
                words[0].extend([(i, aa), (j, bb), (i, aa), (j, bb)])
    system = WordSystem(words, 5)
    actual_d, actual_e, actual_active, _ = pair_from_words(system)
    assert actual_d == d and actual_e == e and actual_active == active
    return system


def targeted_checks(audit):
    records = []
    for rec in audit:
        d, active = rec["canonical_D"], rec["active"]
        targets = [(r, None) for r in rec["persistent_pairs"]]
        targets += [(next(r for r in rec["single_reflection_survivors"] if r["bad_reflection_classes"] < 16), 2)]
        for target, expected_reflections in targets:
            e = [[0]*5 for _ in range(5)]
            for (i, j), value in zip(PAIRS, target["E_upper_triangle"]):
                e[i][j] = e[j][i] = value
            system = realize_pair(d, e, active)
            answer = full_analysis(system, verify_words=True)
            found = answer["first_completion"]
            assert (found is None) == (expected_reflections is None)
            if found is not None:
                assert len(found["reflected_components"]) == expected_reflections
            records.append({"active_components": sum(active), "words": system.words,
                            "minimum_reflections_needed": expected_reflections, "analysis": answer})
    previous = json.loads((HERE / "rank_one_obstruction_results.json").read_text())["graph_reflection_example"]
    s, _, _, _, _ = from_flow(previous["vertices"], previous["edges"], previous["starting_flow"])
    answer = full_analysis(s, verify_words=True)
    assert len(answer["first_completion"]["reflected_components"]) == 1
    return {"constructed_word_systems": records, "previous_26_vertex_graph_analysis": answer,
            "scope": "Six algebraic word realizations and the previously certified 26-vertex graph; word realizations are not claimed to be cubic graphs."}


def verify_cover(n, edges, first, repaired):
    flow = repaired["flow"]; cover = repaired["lift"]["cover"]
    valid_flow(n, edges, flow)
    assert defects(n, edges, flow)[3] == 0
    assert set(cover["4"]) == {e for e in range(len(edges)) if first >> e & 1}
    for layer in cover.values():
        degrees = [0]*n
        for e in layer:
            u, v = edges[e]; degrees[u] += 1; degrees[v] += 1
        assert all(d in (0, 2) for d in degrees)
    assert all(sum(e in layer for layer in cover.values()) == 2 for e in range(len(edges)))


def saved_graph_checks():
    previous = json.loads((HERE / "rank_one_obstruction_results.json").read_text())["saved_failures"]["records"]
    old = json.loads((HERE / "first_coordinate_census.json").read_text())["graphs"]
    graphs = {g["graph6"]: g for g in old}
    persistent = Counter(); routes = Counter(); records = []; example = None
    for rec in previous:
        graph = graphs[rec["graph6"]]
        n, edges, f = graph["vertices"], graph["edges"], rec["starting_flow"]
        system, _, _, _, _ = from_flow(n, edges, f)
        original = full_analysis(system, verify_words=True)
        assert original["first_completion"] is None
        persistent[original["persistent_form_eta"]] += 1
        completed = None
        for normal in range(1, 8):
            if normal == 4:
                continue
            ff = x.transform(f, normal)
            s, first, hc, which, circuits = from_flow(n, edges, ff)
            rank = field_rank(s.rows, s.t)
            if len(hc) <= 4:
                route = "at_most_four_components"; answer = s.search()["witness"]
            elif rank == 0:
                route = "balanced_any_component_count"; answer = s.search()["witness"]
            elif len(hc) == 5 and rank >= 2:
                route = "five_components_field_rank_at_least_two"; answer = construct(s)["witness"]
            elif len(hc) == 5:
                vector, _ = factor(s)
                if max(vector) > 1:
                    continue  # Unneeded in this dataset; do not invent a witness.
                route = "five_components_cyclic_completion"; answer = analyze(s)["witness"]
                if answer is None:
                    continue
            else:
                continue
            assert answer is not None
            repaired = graph_witness(n, edges, ff, s, first, which, circuits, answer)
            verify_cover(n, edges, first, repaired)
            completed = {"normal": normal, "new_first_coordinate_mask": first,
                         "complement_components": len(hc), "circuits_in_new_layer": s.t,
                         "route": route, "repaired_flow": repaired["flow"],
                         "cover_edge_masks": [sum(1 << e for e in repaired["lift"]["cover"][str(k)]) for k in range(5)]}
            routes[route] += 1
            component_counts = [from_flow(n, edges, x.transform(f, k))[0].h for k in range(1, 8)]
            if len(hc) > 5 and example is None and all(h > 5 for k, h in enumerate(component_counts, 1) if k != 4):
                example = {"vertices": n, "edges": edges, "starting_flow": f,
                           "original_first_coordinate_mask": rec["first_coordinate_mask"],
                           "original_defects": defects(n, edges, f),
                           "components_by_normal": component_counts,
                           "changed_coordinate_flow": ff, "construction": answer,
                           "repaired": repaired, "selection": completed}
            break
        assert completed is not None
        records.append({"vertices": n, "graph6": rec["graph6"],
                        "original_first_coordinate_mask": rec["first_coordinate_mask"],
                        "persistent_form_eta": original["persistent_form_eta"], "completion": completed})
    assert len(records) == 215
    return {"scope": "The same one witnessing flow per failed support used in the preceding report; not all flows on these graphs.",
            "supports_checked": 215, "distinct_graphs": len({r["graph6"] for r in records}),
            "persistent_form_counts": dict(persistent), "selection_route_counts": dict(routes),
            "selected_complement_component_counts": dict(Counter(r["completion"]["complement_components"] for r in records)),
            "every_changed_layer_cover_independently_verified": True, "records": records,
            "example_with_no_other_coordinate_having_at_most_five_components": example}


if __name__ == "__main__":
    result = {}
    for name, function in (("finite_classification", finite_classification),
                           ("random_word_checks", random_word_checks), ("saved_graph_checks", saved_graph_checks)):
        result[name] = function()
        print(name, "complete", flush=True)
    result["targeted_checks"] = targeted_checks(result["finite_classification"])
    print("targeted_checks complete", flush=True)
    (HERE / "component_permutation_results.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Persistent forms:", result["saved_graph_checks"]["persistent_form_counts"])
    print("Layer selection:", result["saved_graph_checks"]["selection_route_counts"])
