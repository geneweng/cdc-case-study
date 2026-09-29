#!/usr/bin/env python3
"""Component rotations with linear circuit-offset completion.

See four-component-completion.md. The universal theorem is conditional on an
admissible first coordinate whose complement has at most four components.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
import explore as x
from balanced_completion import omega, ordered_circuits, rotate
from exhaustive_repair import OrbitSearch, subspaces
from first_coordinate_census import components

HERE = Path(__file__).parent


def xor(values):
    result = 0
    for v in values:
        result ^= v
    return result


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def rotate_row(row, state, width):
    return sum(rotate((row >> (2*j)) & 3, state) << (2*j) for j in range(width))


def partitions(items):
    if not items:
        yield []
        return
    first, *tail = items
    for part in partitions(tail):
        yield [[first]] + part
        for i in range(len(part)):
            yield part[:i] + [[first]+part[i]] + part[i+1:]


class WordSystem:
    def __init__(self, words, h):
        self.words, self.h, self.t = words, h, len(words)
        self.a = [[0]*self.t for _ in range(h)]
        for j, word in enumerate(words):
            for k, d in word:
                assert 0 <= k < h and d in (1, 2, 3)
                self.a[k][j] ^= d
        assert all(xor(row) == 0 for row in self.a)
        assert all(xor(row[j] for row in self.a) == 0 for j in range(self.t))
        self.rows = [sum(a << (2*j) for j, a in enumerate(row)) for row in self.a]

    def proof_case(self):
        rank = binary_rank(self.rows)
        if rank == self.h-1:
            return {"case": "full_offset_rank", "binary_rank": rank}
        if not rank:
            return {"case": "entrywise_balanced", "binary_rank": rank}
        if self.h == 4 and all(self.rows):
            orbit = {rotate_row(self.rows[0], s, self.t) for s in range(3)}
            if all(row in orbit for row in self.rows):
                return {"case": "four_collinear_rows", "binary_rank": rank}
        for part in partitions(list(range(self.h))):
            if not all(xor(self.rows[k] for k in group) == 0 and
                       binary_rank([self.rows[k] for k in group]) == len(group)-1 for group in part):
                continue
            target = self.h-len(part)
            if all(binary_rank([rotate_row(self.rows[k], states[g], self.t)
                                for g, group in enumerate(part) for k in group]) == target
                   for states in itertools.product(range(3), repeat=len(part))):
                return {"case": "stable_direct_sum", "binary_rank": rank, "groups": part}
        return {"case": "outside_proved_cases", "binary_rank": rank}

    def integrate(self, states, offsets=None):
        offsets = offsets if offsets is not None else [0]*self.t
        colors = []; defect = [0]*self.h
        for j, word in enumerate(self.words):
            start = current = offsets[j]; values = []
            for k, d in word:
                new = current ^ rotate(d, states[k])
                defect[k] ^= int(current == 0) ^ int(new == 0)
                values.append(new); current = new
            assert current == start
            colors.append(values)
        return colors, defect

    def fixed_states(self, states, verify_affine=False):
        a = [[rotate(v, states[k]) for v in row] for k, row in enumerate(self.a)]
        if any(xor(row[j] for row in a) for j in range(self.t)):
            return None
        colors, defect = self.integrate(states)
        rows = [sum((((v >> 1) & 1) | ((v & 1) << 1)) << (2*j) for j, v in enumerate(row)) for row in a]
        if verify_affine:
            for bit in range(2*self.t):
                offsets = [((1 << bit) >> (2*j)) & 3 for j in range(self.t)]
                _, actual = self.integrate(states, offsets)
                assert actual == [b ^ ((row >> bit) & 1) for row, b in zip(rows, defect)]
        info, solution = x.BASE.solve(list(zip(rows, defect)), 2*self.t)
        assert info["rank"] == binary_rank(rows)
        if solution is None:
            return {"consistent": False, "rank": info["rank"], "defect": defect,
                    "inconsistency": info}
        offsets = [(solution >> (2*j)) & 3 for j in range(self.t)]
        colors, actual = self.integrate(states, offsets)
        assert actual == [0]*self.h
        return {"consistent": True, "rank": info["rank"], "defect_before_offsets": defect,
                "states": list(states), "offsets": offsets, "circuit_colors": colors,
                "affine_dimension": info["affine_dimension"]}

    def search(self, exhaustive=False, verify_affine=False):
        valid = successful = offset_solutions = examined = 0; witness = None; hist = Counter()
        for states in itertools.product(range(3), repeat=self.h):
            examined += 1
            result = self.fixed_states(states, verify_affine)
            if result is None:
                continue
            valid += 1
            hist[f"rank={result['rank']},solvable={result['consistent']}"] += 1
            if result["consistent"]:
                successful += 1
                offset_solutions += 1 << result["affine_dimension"]
                if witness is None:
                    witness = result
                if not exhaustive:
                    break
        return {"rotations_examined": examined, "closure_assignments": valid,
                "solvable_rotation_assignments": successful, "successful_rotation_offset_pairs": offset_solutions,
                "exhaustive": exhaustive, "rank_outcome_histogram": dict(sorted(hist.items())), "witness": witness}


def from_flow(n, edges, f):
    inc = x.BASE.incidence(n, edges)
    assert all(0 < a < 8 for a in f)
    assert all(xor(f[e] for e in es) == 0 for es in inc)
    first = sum(1 << e for e, a in enumerate(f) if a & 4)
    hc = components(n, edges, first, keep=False)
    which = {v: k for k, comp in enumerate(hc) for v in comp}
    cs = ordered_circuits(n, edges, first)
    words = [[(which[v], f[next(e for e in inc[v] if not first >> e & 1)] & 3) for v in vs]
             for vs, _ in cs]
    return WordSystem(words, len(hc)), first, hc, which, cs


def graph_witness(n, edges, f, system, first, which, circuits, witness):
    result = [rotate(a & 3, witness["states"][which[edges[e][0]]]) if not first >> e & 1 else 0
              for e, a in enumerate(f)]
    for (_, es), values in zip(circuits, witness["circuit_colors"]):
        for e, value in zip(es, values):
            result[e] = 4 + value
    assert all(result) and all(xor(result[e] for e in es) == 0 for es in x.BASE.incidence(n, edges))
    assert x.defect(n, edges, result, 4) == 0
    lift = x.extra_coordinate_lift(n, edges, result)
    assert lift["cover"] is not None
    assert lift["cover"]["4"] == [e for e in range(len(edges)) if first >> e & 1]
    return {"flow": result, "lift": lift}


def graph_checks():
    records = json.loads((HERE / "exhaustive_repair_results.json").read_text())["graphs"]
    out = []; examples = {}; totals = Counter()
    for rec in [r for r in records if r["vertices"] <= 10]:
        n, edges = rec["vertices"], rec["edges"]
        search = OrbitSearch(n, edges); seen = set(); counts = Counter()
        for rank in (2, 3):
            for rows in subspaces(search.r, rank):
                f = search.flow(rows)
                if 0 in f:
                    continue
                for normal in range(1, 8):
                    ff = x.transform(f, normal)
                    first = sum(1 << e for e, a in enumerate(ff) if a & 4)
                    hc = components(n, edges, first, keep=False)
                    if len(hc) > 4:
                        continue
                    key = (first, tuple(a & 3 for e, a in enumerate(ff) if not first >> e & 1))
                    if key in seen:
                        continue
                    seen.add(key)
                    system, first, hc, which, circuits = from_flow(n, edges, ff)
                    case = system.proof_case()
                    assert case["case"] != "outside_proved_cases"
                    answer = system.search(verify_affine=True)
                    assert answer["witness"] is not None
                    cover = graph_witness(n, edges, ff, system, first, which, circuits, answer["witness"])
                    counts[case["case"]] += 1
                    if case["case"] not in examples:
                        examples[case["case"]] = {"vertices": n, "edges": edges, "starting_flow": ff,
                            "first_coordinate_mask": first, "boundary_table": system.a,
                            "proof_case": case, "search": answer, "repaired": cover}
        totals.update(counts)
        out.append({"vertices": n, "graph6": rec.get("graph6"), "distinct_restrictions_checked": len(seen), "case_counts": dict(counts)})
    return {"scope": "All flow classes and all normals on the 26 saved connected bridgeless simple cubic graphs through 10 vertices; complement size at most four; identical (F,q restricted to H) inputs deduplicated.",
            "graphs": out, "case_counts": dict(totals), "examples": examples,
            "every_repaired_flow_and_decoded_cover_verified": True}


def random_word_checks():
    rng = random.Random(20260930); counts = Counter(); examples = {}
    for h in range(1, 5):
        for trial in range(200):
            t = rng.randrange(1, 7)
            a = [[0]*t for _ in range(h)]
            for k in range(h-1):
                for j in range(t-1):
                    a[k][j] = rng.randrange(4)
                a[k][-1] = xor(a[k][:-1])
            for j in range(t):
                a[-1][j] = xor(a[k][j] for k in range(h-1))
            words = []
            for j in range(t):
                word = []
                for k in range(h):
                    if a[k][j]:
                        word.append((k, a[k][j]))
                    d = rng.randrange(1, 4)
                    word.extend([(k, d), (k, d)])
                rng.shuffle(word); words.append(word)
            system = WordSystem(words, h)
            case = system.proof_case()
            assert case["case"] != "outside_proved_cases"
            answer = system.search(exhaustive=True, verify_affine=True)
            assert answer["witness"] is not None
            counts[case["case"]] += 1
            if case["case"] not in examples:
                examples[case["case"]] = {"words": words, "boundary_table": a, "proof_case": case, "search": answer}
    return {"seed": 20260930, "systems_checked": sum(counts.values()), "case_counts": dict(counts),
            "all_rotation_assignments_exhausted": True, "all_offset_coefficients_verified_directly": True, "examples": examples}


def petersen_failure():
    n, edges = x.petersen(); first = sum(1 << e for e in list(range(5))+list(range(10,15)))
    # Matching colors 1,1,1,2,3 sum to zero on both pentagons.
    inc = x.BASE.incidence(n, edges); q = [0]*len(edges)
    q[5:10] = [1,1,1,2,3]
    for vs, es in ordered_circuits(n, edges, first):
        prefix = 0
        for v, e in zip(vs, es):
            prefix ^= q[next(j for j in inc[v] if not first >> j & 1)]
            q[e] = prefix
        assert prefix == 0
    f = [a + 4*((first >> e)&1) for e, a in enumerate(q)]
    system, _, hc, _, _ = from_flow(n, edges, f)
    answer = system.search(exhaustive=True, verify_affine=True)
    assert len(hc) == 5 and answer["witness"] is None
    assert answer["rotations_examined"] == 243 and answer["closure_assignments"] == 60
    return {"vertices": n, "edges": edges, "first_coordinate_mask": first,
            "starting_flow": f, "boundary_table": system.a, "search": answer,
            "independent_offset_enumeration": enumerate_offsets(system),
            "matching_component_rotations_cover_all_nonzero_colorings": True}


def enumerate_offsets(system):
    """Directly count offsets by zero-color incidences, without solving matrices."""
    closed = successful = tested = zero_offset_successes = 0
    hist = Counter()
    for states in itertools.product(range(3), repeat=system.h):
        if any(xor(rotate(d, states[k]) for k, d in word) for word in system.words):
            continue
        closed += 1
        for offsets in itertools.product(range(4), repeat=system.t):
            _, actual = system.integrate(states, offsets)
            tested += 1; hist[sum(actual)] += 1
            successful += not any(actual)
            zero_offset_successes += not any(actual) and not any(offsets)
    return {"closure_assignments": closed, "rotation_offset_pairs_checked": tested,
            "successful_pairs": successful, "successful_zero_offset_assignments": zero_offset_successes,
            "defect_histogram": dict(sorted(hist.items()))}


def offsets_are_essential():
    orders = [[0,1,2,3], [0,1,3,2], [0,2,1,3]]
    edges = []; q = []
    for j, order in enumerate(orders):
        prefix = 0
        for i, k in enumerate(order):
            edges.append((4*j+k, 4*j+order[(i+1)%4]))
            prefix ^= j+1; q.append(prefix)
    first = (1 << len(edges))-1
    for k in range(4):
        for j in range(3):
            edges.append((12+k, 4*j+k)); q.append(j+1)
    f = [a+4*((first >> e)&1) for e, a in enumerate(q)]
    system, _, hc, which, circuits = from_flow(16, edges, f)
    assert system.a == [[1,2,3]]*4
    answer = system.search(exhaustive=True, verify_affine=True)
    brute = enumerate_offsets(system)
    assert brute["successful_pairs"] == answer["successful_rotation_offset_pairs"] == 96
    assert brute["successful_zero_offset_assignments"] == 0
    assert answer["closure_assignments"] == 21 and answer["solvable_rotation_assignments"] == 3
    repaired = graph_witness(16, edges, f, system, first, which, circuits, answer["witness"])
    return {"vertices": 16, "edges": edges, "starting_flow": f,
            "first_coordinate_mask": first, "complement_components": hc,
            "boundary_table": system.a, "search": answer,
            "independent_offset_enumeration": brute, "repaired": repaired}


def boundary_case_audit():
    counts = Counter()
    possible = [(a, b, a ^ b) for a in range(4) for b in range(4)]
    for first in itertools.product(possible, repeat=3):
        a = list(first) + [tuple(xor(row[j] for row in first) for j in range(3))]
        # Realize each boundary entry by a nonzero occurrence if needed, plus
        # a cancelling pair so every component participates in every circuit.
        words = [[pair for k in range(4) for pair in ([(k, a[k][j])] if a[k][j] else [])+[(k,1),(k,1)]]
                 for j in range(3)]
        system = WordSystem(words, 4)
        case = system.proof_case()["case"]
        assert case != "outside_proved_cases"
        counts[case] += 1
    exceptional = []
    for matrix in range(16):
        def bilinear(a, b):
            return sum(((matrix >> (2*i+j))&1)*((a>>i)&1)*((b>>j)&1)
                       for i in range(2) for j in range(2)) % 2
        if all(bilinear(a,b) == 1 for a in (1,2,3) for b in (1,2,3) if a != b):
            assert all(bilinear(a,a) == 0 for a in (1,2,3))
            exceptional.append(matrix)
    assert exceptional == [6]
    return {"all_four_by_three_tables_with_zero_row_and_column_sums": sum(counts.values()),
            "case_counts": dict(counts), "all_sixteen_bilinear_forms_checked": True,
            "unique_form_without_an_off_diagonal_zero": "omega(a,b)"}


if __name__ == "__main__":
    result = {"graph_checks": graph_checks(), "abstract_word_checks": random_word_checks(),
              "sharp_five_component_failure": petersen_failure(),
              "offsets_are_essential": offsets_are_essential(), "boundary_case_audit": boundary_case_audit()}
    (HERE / "coupled_completion_results.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Graph cases:", result["graph_checks"]["case_counts"])
    print("Abstract cases:", result["abstract_word_checks"]["case_counts"])
    print("Petersen:", result["sharp_five_component_failure"]["search"]["closure_assignments"], "closed assignments, none repairable.")
