#!/usr/bin/env python3
"""Certify coordinate selection on one cyclically four-edge-connected snark.

The graph is Hagglund's Blowup(K4, triangle), not a new graph construction.
Every binary cycle support is tested. Positive covers and three DRUP proofs
are saved for independent verification. No general 5-CDC theorem is claimed.
Requires NetworkX and python-sat; the verifier needs only the standard library.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import pysat
from pysat.solvers import Solver
import explore as x
from first_coordinate_census import components

HERE = Path(__file__).parent
PAIRS = list(itertools.combinations(range(5), 2))
PAIR_MASKS = [sum(1 << i for i in pair) for pair in PAIRS]
FIRST = 47827614721998
SECOND = 2139617360067696
THIRD = 92676805206309


def blowup():
    """Construction 2 of arXiv:1203.2015, on the triangle 0,1,2 of K4.

    A Petersen four-pole removes adjacent vertices 0,1. Its two port pairs
    are a=(4,5), b=(2,6), using this repository's Petersen vertex labels.
    """
    edges = [(0, 3), (1, 3), (2, 3)]
    _, pe = x.petersen()
    blocks = []
    for j in range(3):
        mapping = {v: 4+8*j+v-2 for v in range(2, 10)}
        blocks.append(mapping)
        edges.extend((mapping[u], mapping[v]) for u, v in pe if u >= 2 and v >= 2)
    for j in range(3):
        u, w = 28+2*j, 29+2*j
        next_u, next_w = 28+2*((j+1) % 3), 29+2*((j+1) % 3)
        edges.extend([(j, u), (j, w), (u, blocks[j][2]), (w, blocks[j][6]),
                      (blocks[j][4], next_u), (blocks[j][5], next_w)])
    assert len(edges) == 51
    return 34, edges


def parity_clauses(a, b, c):
    return [[-a, b, c], [a, -b, c], [a, b, -c], [-a, -b, -c]]


class CoverSolver:
    def __init__(self, n, edges):
        self.ids = [[5*e+i+1 for i in range(5)] for e in range(len(edges))]
        clauses = []
        for ids in self.ids:
            clauses.extend([v for j, v in enumerate(ids) if j != i] for i in range(5))
            clauses.extend([-v for v in triple] for triple in itertools.combinations(ids, 3))
        for incident in x.BASE.incidence(n, edges):
            for label in range(5):
                clauses.extend(parity_clauses(*(self.ids[e][label] for e in incident)))
        self.clauses = clauses
        self.solver = Solver(name="g4", bootstrap_with=clauses)

    def units(self, first):
        return [ids[0] if first >> e & 1 else -ids[0] for e, ids in enumerate(self.ids)]

    def solve(self, first):
        if not self.solver.solve(assumptions=self.units(first)):
            return None
        model = set(v for v in self.solver.get_model() if v > 0)
        masks = [sum(1 << i for i, var in enumerate(ids) if var in model) for ids in self.ids]
        assert all(mask in PAIR_MASKS for mask in masks)
        return "".join(str(PAIR_MASKS.index(mask)) for mask in masks)

    def unsat_proof(self, first):
        # Start a fresh solver; all fixed-layer units belong to the base CNF.
        with Solver(name="g4", bootstrap_with=self.clauses+[[v] for v in self.units(first)],
                    with_proof=True) as solver:
            assert not solver.solve()
            proof = solver.get_proof()
            assert proof[-1] == "0"
            return "\n".join(proof)+"\n"


def audit_spans(rejected, supports, full):
    """All rejected binary lines and planes, with canonical least bases."""
    bad = set(rejected)-{0}
    lines = full_lines = full_planes = planes = 0
    missing = Counter()
    for a in sorted(bad):
        translates = {b for b in bad if a ^ b in bad}
        representatives = sorted(b for b in translates if a < b < (a ^ b))
        for b in representatives:
            lines += 1
            full_lines += supports[a] | supports[b] == full
        for b, c in itertools.combinations(representatives, 2):
            if b ^ c not in translates:
                continue
            span = {a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c}
            if len(span) != 7 or min(span) != a or b != min(span-{a}) or c != min(span-{a, b, a ^ b}):
                continue
            planes += 1
            absent = (full ^ (supports[a] | supports[b] | supports[c])).bit_count()
            missing[absent] += 1
            full_planes += absent == 0
    assert full_lines == full_planes == 0
    return {"rejected_rank_two_subspaces": lines, "full_support_rank_two_subspaces": full_lines,
            "rejected_rank_three_subspaces": planes, "full_support_rank_three_subspaces": full_planes,
            "rank_three_missing_edge_histogram": dict(sorted(missing.items()))}


def main():
    n, edges = blowup()
    solver = CoverSolver(n, edges)
    basis = [sum(1 << e for e in c) for c in x.BASE.cycle_basis(n, edges)]
    assert len(basis) == 18
    supports = [0]
    for circuit in basis:
        supports += [s ^ circuit for s in supports]
    assert len(set(supports)) == 2**18
    rejected = []
    certificate_path = HERE / "cyclic_core_covers.txt.gz"
    with certificate_path.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as stream:
            for code, first in enumerate(supports):
                word = solver.solve(first)
                if word is None:
                    rejected.append(code)
                else:
                    stream.write(f"{code} {word}\n".encode("ascii"))
                if (code+1) % 65536 == 0:
                    print("Supports:", code+1, "/", len(supports), "omitted:", len(rejected), flush=True)
    assert len(rejected) == 4506
    span_audit = audit_spans(rejected, supports, (1 << len(edges))-1)
    flow = [((FIRST >> e) & 1) | (((SECOND >> e) & 1) << 1) | (((THIRD >> e) & 1) << 2)
            for e in range(len(edges))]
    assert 0 not in flow
    assert all(flow[a] ^ flow[b] ^ flow[c] == 0 for a, b, c in x.BASE.incidence(n, edges))
    proof_dir = HERE / "cyclic_core_proofs"
    proof_dir.mkdir(exist_ok=True)
    normal_records = []
    for normal in range(1, 8):
        first = sum(1 << e for e, value in enumerate(flow) if x.dot(value, normal))
        word = solver.solve(first)
        rec = {"normal": normal, "support_mask": first,
               "support_components": components(n, edges, first),
               "complement_components": components(n, edges, first, keep=False), "cover_word": word}
        if normal <= 3:
            assert word is None
            proof = solver.unsat_proof(first)
            path = proof_dir / f"normal-{normal}.drup"
            path.write_text(proof)
            rec.update(proof_file=str(path.relative_to(HERE)),
                       proof_sha256=hashlib.sha256(proof.encode()).hexdigest(),
                       proof_lines=len(proof.splitlines()))
        else:
            assert word is not None
        normal_records.append(rec)
    assert FIRST ^ SECOND == normal_records[2]["support_mask"]
    result = {"date": "2026-09-29", "scope": "Every nowhere-zero binary three-flow on this one specified 34-vertex graph has a completable coordinate; no universal graph theorem is asserted.",
              "source": "https://arxiv.org/html/1203.2015v1#S2", "pysat_version": pysat.__version__,
              "solver": "Glucose 4.1", "vertices": n, "edges": edges, "binary_cycle_basis": basis,
              "witness_flow": flow, "witness_normals": normal_records,
              "cnf_variables": 5*len(edges), "cnf_clauses_before_fixed_layer": len(solver.clauses),
              "census": {"binary_supports": len(supports), "cover_certificates": len(supports)-len(rejected),
                         "omitted_support_codes": rejected, "cover_file": certificate_path.name,
                         "cover_file_sha256": hashlib.sha256(certificate_path.read_bytes()).hexdigest(),
                         "encoding": "One line: binary support code, space, then 51 pair indices in lexicographic order of the ten unordered pairs from labels 0..4. Layer 0 equals the prescribed support.",
                         "omitted_supports_note": "The independent positive theorem treats these as unclassified; it does not need to trust their solver UNSAT status.",
                         **span_audit}}
    (HERE / "cyclic_core_completion.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Saved", result["census"]["cover_certificates"], "cover witnesses and three DRUP proofs.", flush=True)
    print("Rejected-subspace audit:", span_audit, flush=True)


if __name__ == "__main__":
    main()
