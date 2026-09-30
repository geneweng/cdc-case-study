#!/usr/bin/env python3
"""Check the 34-vertex result without SAT or third-party libraries.

Every positive cover is checked directly. Three nonexistence proofs are
checked by reverse unit propagation. Omitted supports are otherwise treated
as unknown, so their alleged UNSAT status is not needed for the positive
coordinate-selection theorem.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from verify_layer_selection_obstruction import components
from verify_lex_trap import valid_flow


class RUPChecker:
    """Keep every proved clause; ignoring deletions is sound for DRUP."""
    def __init__(self, clauses):
        self.clauses = []
        self.occurrences = {}
        self.units = []
        for clause in clauses:
            self.add(clause)

    def add(self, clause):
        clause = tuple(dict.fromkeys(clause))
        index = len(self.clauses)
        self.clauses.append(clause)
        for literal in clause:
            self.occurrences.setdefault(literal, []).append(index)
        if len(clause) == 1:
            self.units.append(clause[0])

    def unit_conflict(self, assumptions):
        remaining = list(map(len, self.clauses))
        if 0 in remaining:
            return True
        satisfied = [False]*len(remaining)
        assigned = set()
        pending = self.units+list(assumptions)
        while pending:
            literal = pending.pop()
            if -literal in assigned:
                return True
            if literal in assigned:
                continue
            assigned.add(literal)
            for index in self.occurrences.get(literal, ()):
                satisfied[index] = True
            for index in self.occurrences.get(-literal, ()):
                if satisfied[index]:
                    continue
                remaining[index] -= 1
                if remaining[index] == 0:
                    return True
                if remaining[index] == 1:
                    unit = next((v for v in self.clauses[index] if v not in assigned and -v not in assigned), None)
                    assert unit is not None
                    pending.append(unit)
        return False

    def verify(self, proof, variables):
        additions = deletions = 0
        empty = False
        for line in proof.splitlines():
            parts = line.split()
            assert parts
            deletion = parts[0] == "d"
            if deletion:
                parts = parts[1:]
            clause = list(map(int, parts))
            assert clause.pop() == 0
            assert all(0 < abs(v) <= variables for v in clause)
            if deletion:
                deletions += 1
                continue
            assert self.unit_conflict(-v for v in clause), "Invalid RUP inference"
            self.add(clause)
            additions += 1
            empty |= not clause
        assert empty, "No empty clause was derived"
        return additions, deletions


def reconstruct_cnf(n, edges):
    clauses = []
    var = lambda e, label: 5*e+label+1
    for e in range(len(edges)):
        clauses += [[var(e, label) for label in range(5) if label != missing] for missing in range(5)]
        clauses += [[-var(e, label) for label in triple] for triple in itertools.combinations(range(5), 3)]
    for v in range(n):
        incident = [e for e, endpoints in enumerate(edges) if v in endpoints]
        assert len(incident) == 3
        for label in range(5):
            ids = [var(e, label) for e in incident]
            for odd_bits in (1, 2, 4, 7):
                clauses.append([-a if odd_bits >> j & 1 else a for j, a in enumerate(ids)])
    return clauses


def check_encoding():
    # Truth tables establish what the clauses mean, independently of a solver.
    edge = [[j+1 for j in range(5) if j != i] for i in range(5)]
    edge += [[-v for v in triple] for triple in itertools.combinations(range(1, 6), 3)]
    parity = [[-(j+1) if bits >> j & 1 else j+1 for j in range(3)] for bits in (1, 2, 4, 7)]
    def holds(clauses, bits):
        return all(any(bool(bits >> (abs(v)-1) & 1) == (v > 0) for v in clause) for clause in clauses)
    assert all(holds(edge, bits) == (bits.bit_count() == 2) for bits in range(32))
    assert all(holds(parity, bits) == (bits.bit_count() % 2 == 0) for bits in range(8))
    # Small semantic checks of the checker itself, including an invalid step.
    assert RUPChecker([[1], [-1]]).unit_conflict([])
    assert not RUPChecker([[1, 2]]).unit_conflict([-1])
    assert RUPChecker([[1, 2], [-2]]).unit_conflict([-1])


def verify_graph(saved):
    n, edges = saved["vertices"], saved["edges"]
    assert n == 34 and len(edges) == 51
    assert len({tuple(sorted(e)) for e in edges}) == 51
    assert all(u != v and 0 <= u < n and 0 <= v < n for u, v in edges)
    inc = [[e for e, endpoints in enumerate(edges) if v in endpoints] for v in range(n)]
    assert all(len(es) == 3 for es in inc)
    assert len(components(n, edges, range(51))) == 1
    cut_count = examined = 0
    for size in (1, 2, 3):
        for removed in itertools.combinations(range(51), size):
            examined += 1
            cc = components(n, edges, set(range(51))-set(removed))
            if len(cc) > 1:
                assert size == 3 and sorted(map(len, cc)) == [1, 33]
                cut_count += 1
    assert examined == 22151 and cut_count == 34
    for k in range(3):
        block = set(range(4+8*k, 12+8*k))
        cut = {e for e, (u, v) in enumerate(edges) if (u in block) != (v in block)}
        assert len(cut) == 4
        cc = components(n, edges, set(range(51))-cut)
        assert sorted(map(len, cc)) == [8, 26]
        assert all(sum(u in part and v in part for u, v in edges) >= len(part) for part in cc)
    # Thus there is no cyclic cut of size <=3, and a cyclic cut of size 4 exists.
    return inc


def verify_spans(rejected, supports, full):
    # A subspace is visited through its numerically smallest nonzero vector,
    # then the smallest vector outside its span, then the smallest outside
    # that plane. This describes every rank-two/three subspace exactly once.
    pool = set(rejected)-{0}
    lines = planes = 0
    histogram = Counter()
    for a in sorted(pool):
        paired = {b for b in pool if a ^ b in pool}
        representatives = sorted(b for b in paired if a < b and b < (a ^ b))
        for b in representatives:
            lines += 1
            assert supports[a] | supports[b] != full
        for i, b in enumerate(representatives):
            for c in representatives[i+1:]:
                if b ^ c not in paired:
                    continue
                outside_plane = {c, c ^ a, c ^ b, c ^ a ^ b}
                if c != min(outside_plane) or b >= min(outside_plane):
                    continue
                # a is smaller than both representatives and their translates;
                # check the two remaining vectors explicitly.
                if min(c ^ b, c ^ a ^ b) <= a:
                    continue
                planes += 1
                missing = (full ^ (supports[a] | supports[b] | supports[c])).bit_count()
                assert missing > 0
                histogram[missing] += 1
    return lines, planes, histogram


def main():
    directory = Path(__file__).parent
    saved = json.loads((directory / "cyclic_core_completion.json").read_text())
    n, edges = saved["vertices"], saved["edges"]
    inc = verify_graph(saved)
    valid_flow(n, edges, saved["witness_flow"])
    check_encoding()
    clauses = reconstruct_cnf(n, edges)
    assert len(clauses) == saved["cnf_clauses_before_fixed_layer"] == 1445
    assert saved["cnf_variables"] == 255
    pairs = [sum(1 << i for i in pair) for pair in itertools.combinations(range(5), 2)]
    def check_word(word, first):
        assert len(word) == 51 and all(ch in "0123456789" for ch in word)
        masks = [pairs[ord(ch)-48] for ch in word]
        assert all(masks[a] ^ masks[b] ^ masks[c] == 0 for a, b, c in inc)
        assert sum(1 << e for e, mask in enumerate(masks) if mask & 1) == first
    proof_totals = [0, 0]
    for normal, rec in enumerate(saved["witness_normals"], 1):
        first = sum(1 << e for e, value in enumerate(saved["witness_flow"]) if (value & normal).bit_count() % 2)
        assert first == rec["support_mask"] and normal == rec["normal"]
        assert [c for c in components(n, edges, [e for e in range(51) if first >> e & 1]) if len(c) > 1] == [sorted(c) for c in rec["support_components"]]
        assert components(n, edges, [e for e in range(51) if not first >> e & 1]) == [sorted(c) for c in rec["complement_components"]]
        if normal <= 3:
            assert rec["cover_word"] is None
            raw = (directory / rec["proof_file"]).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == rec["proof_sha256"]
            assert len(raw.decode().splitlines()) == rec["proof_lines"]
            units = [[5*e+1 if first >> e & 1 else -(5*e+1)] for e in range(51)]
            stats = RUPChecker(clauses+units).verify(raw.decode(), 255)
            proof_totals = [a+b for a, b in zip(proof_totals, stats)]
        else:
            check_word(rec["cover_word"], first)
    assert saved["witness_normals"][0]["support_mask"] ^ saved["witness_normals"][1]["support_mask"] == saved["witness_normals"][2]["support_mask"]
    print("Cyclic edge connectivity 4 and all three nonexistence proofs verified:", proof_totals, flush=True)

    basis = saved["binary_cycle_basis"]
    assert len(basis) == len(edges)-n+1 == 18
    assert all(all(sum(mask >> e & 1 for e in es) % 2 == 0 for es in inc) for mask in basis)
    supports = [0]
    for mask in basis:
        assert 0 < mask < 1 << 51
        supports += [s ^ mask for s in supports]
    assert len(set(supports)) == 262144  # Independent basis, hence the full cycle space.
    census = saved["census"]
    omitted = set(census["omitted_support_codes"])
    assert len(omitted) == len(census["omitted_support_codes"]) == 4506
    assert 0 in omitted and all(0 <= code < len(supports) for code in omitted)
    path = directory / census["cover_file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == census["cover_file_sha256"]
    expected = (code for code in range(len(supports)) if code not in omitted)
    count = 0
    with gzip.open(path, "rt", encoding="ascii") as stream:
        for line in stream:
            code, word = line.split()
            code = int(code)
            assert code == next(expected)
            check_word(word, supports[code])
            count += 1
    assert next(expected, None) is None
    assert count == census["cover_certificates"] == 257638
    assert count+len(omitted) == census["binary_supports"] == 262144
    print("All", count, "explicit covers verified; omitted supports are treated as unknown.", flush=True)
    lines, planes, hist = verify_spans(omitted, supports, (1 << 51)-1)
    assert lines == census["rejected_rank_two_subspaces"]
    assert planes == census["rejected_rank_three_subspaces"]
    assert hist == {int(k): v for k, v in census["rank_three_missing_edge_histogram"].items()}
    assert census["full_support_rank_two_subspaces"] == census["full_support_rank_three_subspaces"] == 0
    print("Checked", lines, "rank-two and", planes, "rank-three omitted subspaces; none has full edge support.", flush=True)
    print("Every nowhere-zero three-bit flow on this graph therefore has a certified completable coordinate.", flush=True)


if __name__ == "__main__":
    main()
