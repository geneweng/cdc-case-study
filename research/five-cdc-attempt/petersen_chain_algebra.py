#!/usr/bin/env python3
"""Exact prescribed-layer algebra of serial Petersen four-poles.

Standard library only. The 36 nonzero relations form a finite semigroup
after adjoining the zero relation. See petersen-chain-algebra.md.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).parent
PAIRS = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
STATES = list(itertools.product(range(10), repeat=2))
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
ZERO = (0,)*100


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def compose(left, right):
    """Boolean matrix product, with rows stored as integer bitsets."""
    answer = []
    for row in left:
        value = 0
        for j in bits(row):
            value |= right[j]
        answer.append(value)
    return tuple(answer)


def swap_input(matrix):
    return tuple(matrix[10*b+a] for a, b in STATES)


def swap_output(matrix):
    return tuple(sum(1 << (10*STATES[j][1]+STATES[j][0]) for j in bits(row))
                 for row in matrix)


def load_relations():
    matrices, witnesses = {}, {}
    with gzip.open(HERE / "petersen_boundary_relation.txt.gz", "rt") as stream:
        for line in stream:
            mask, boundary, word = line.split()
            mask = int(mask)
            a, b, c, d = map(int, boundary)
            matrices.setdefault(mask, [0]*100)[10*a+b] |= 1 << (10*c+d)
            witnesses[mask, (a, b, c, d)] = word
    return {f: tuple(r) for f, r in sorted(matrices.items())}, witnesses


def closure(relations):
    words = {}
    for f, matrix in relations.items():
        words.setdefault(matrix, (f,))
    generators = list(words)
    frontier = generators
    while frontier:
        next_frontier = []
        for left in frontier:
            for right in generators:
                product = compose(left, right)
                if product != ZERO and product not in words:
                    words[product] = words[left]+words[right]
                    next_frontier.append(product)
        frontier = next_frontier
    return words


def membership(state):
    a, b = STATES[state]
    return int(bool(PAIRS[a] & 1))+2*int(bool(PAIRS[b] & 1))


def full_block(left_membership, right_membership, charge):
    right = sum(1 << j for j, (a, b) in enumerate(STATES)
                if membership(j) == right_membership and PAIRS[a] ^ PAIRS[b] == charge)
    return tuple(right if membership(i) == left_membership and PAIRS[a] ^ PAIRS[b] == charge
                 else 0 for i, (a, b) in enumerate(STATES))


def safe_boundary(mask):
    """One boundary that works for EVERY internal support with these port bits."""
    port_bits = mask >> 10
    # 0 means pair 01, 4 means 12, and 7 means 23 in the pair dictionary.
    off = 4 if (port_bits & 3) in (0, 3) else 7
    return tuple(0 if port_bits >> i & 1 else off for i in range(4))


def chain_witness(masks, boundary, relations, witnesses):
    """Backtrack a boundary assignment through a straight open chain."""
    a, b, c, d = boundary
    target = 10*c+d
    reachable = [{target}]
    for f in reversed(masks):
        allowed = sum(1 << i for i in reachable[-1])
        reachable.append({i for i, row in enumerate(relations[f]) if row & allowed})
    reachable.reverse()
    state = 10*a+b
    if state not in reachable[0]:
        return None
    words = []
    for k, f in enumerate(masks):
        following = min(j for j in reachable[k+1] if relations[f][state] >> j & 1)
        words.append(witnesses[f, STATES[state]+STATES[following]])
        state = following
    assert state == target
    return words


def necklace(masks, twists, witnesses):
    """Close a chain into a ring; a twist exchanges the two joined ports."""
    k = len(masks)
    assert k >= 1 and len(twists) == k and set(twists) <= {0, 1}
    local_words = [witnesses[f, safe_boundary(f)] for f in masks]
    edges, word, prescribed = [], [], []
    for i, (f, w) in enumerate(zip(masks, local_words)):
        edges.extend([(8*i+u-2, 8*i+v-2) for u, v in INTERNAL])
        word.extend(w[:10])
        prescribed.extend(bool(f >> e & 1) for e in range(10))
    for i, f in enumerate(masks):
        following = (i+1) % k
        g = masks[following]
        for j in range(2):
            h = j ^ twists[i]
            assert (f >> (12+j)) & 1 == (g >> (10+h)) & 1
            assert local_words[i][12+j] == local_words[following][10+h]
            edges.append((8*i+PORTS[2+j]-2, 8*following+PORTS[h]-2))
            word.append(local_words[i][12+j])
            prescribed.append(bool(f >> (12+j) & 1))
    return {"local_masks": masks, "twists": twists, "vertices": 8*k,
            "edges": edges, "cover_word": "".join(word),
            "prescribed_edges": [i for i, included in enumerate(prescribed) if included]}


def examples(relations, witnesses):
    records = []
    for f in relations:
        g = min(g for g in relations if (g >> 10) & 3 == f >> 12
                and g >> 12 == (f >> 10) & 3)
        records.append(necklace([f, g], [0, 0], witnesses))
    rng = random.Random(20260930)
    for k in (1, 3, 8, 17, 31):
        for odd in (False, True):
            incoming = [rng.choice((1, 2) if odd else (0, 3)) for _ in range(k)]
            twists = [rng.randrange(2) for _ in range(k)]
            masks = []
            for i in range(k):
                out = incoming[(i+1) % k]
                if twists[i]:
                    out = ((out & 1) << 1) | (out >> 1)
                candidates = [f for f in relations if f >> 10 == incoming[i] | (out << 2)]
                masks.append(rng.choice(candidates))
            records.append(necklace(masks, twists, witnesses))
    return records


def main():
    relations, witnesses = load_relations()
    words = closure(relations)
    assert len(relations) == 64 and len(set(relations.values())) == 27 and len(words) == 36
    assert Counter(map(len, words.values())) == {1: 27, 2: 7, 3: 2}
    matrices = list(words)+[ZERO]
    ids = {matrix: i for i, matrix in enumerate(matrices)}
    table = [[ids[compose(a, b)] for b in matrices] for a in matrices]
    # Closure under either interface twist needs no additional relation types.
    input_swap = [ids[swap_input(a)] for a in matrices]
    output_swap = [ids[swap_output(a)] for a in matrices]
    assert max(input_swap[:27]+output_swap[:27]) < 27
    universal = [{"mask": f, "boundary": list(safe_boundary(f)),
                  "cover_word": witnesses[f, safe_boundary(f)]} for f in relations]
    safe_products = 0
    for f, left in relations.items():
        for g, right in relations.items():
            if f >> 12 != (g >> 10) & 3:
                continue
            charge = 15 if ((f >> 10) & 3) in (1, 2) else 0
            required = full_block((f >> 10) & 3, g >> 12, charge)
            product = compose(left, right)
            assert any(required) and all(a & b == b for a, b in zip(product, required))
            safe_products += 1
    assert safe_products == 1024
    chains = []
    for k in (1, 2, 3, 8, 17, 64):
        boundary = (5, 7, 6, 8) if k % 2 else (5, 7, 5, 7)
        local = chain_witness([887]*k, boundary, relations, witnesses)
        assert local is not None
        chains.append({"local_masks": [887]*k, "boundary": boundary, "local_cover_words": local})
    source = HERE / "petersen_boundary_relation.txt.gz"
    result = {
        "date": "2026-09-30",
        "scope": "Exact conditional algebra for serial Petersen four-poles; not a proof of the general 5-CDC conjecture.",
        "pair_masks": PAIRS, "internal_edges": INTERNAL, "port_vertices": PORTS,
        "source_relation_file": source.name,
        "source_relation_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "local_supports": 64, "generator_types": 27, "nonzero_chain_types": 36,
        "zero_id": 36, "shortest_word_histogram": {"1": 27, "2": 7, "3": 2},
        "local_type_ids": [[f, ids[a]] for f, a in relations.items()],
        "types": [{"id": ids[a], "representative_masks": list(w),
                   "boundary_states": sum(r.bit_count() for r in a),
                   "rows_hex": [format(r, "x") for r in a]} for a, w in words.items()],
        "multiplication_table": table, "swap_input_ids": input_swap, "swap_output_ids": output_swap,
        "universal_boundary_witnesses": universal, "compatible_two_piece_checks": safe_products,
        "three_label_empty_word": "57745554774444",
        "parity_example": {"local_mask": 887, "charge": 6, "first_class": [[5, 7], [7, 5]],
                           "second_class": [[6, 8], [8, 6]],
                           "even_endpoint": [5, 7, 5, 7], "odd_endpoint": [5, 7, 6, 8]},
        "chain_examples": chains, "necklace_examples": examples(relations, witnesses)}
    (HERE / "petersen_chain_algebra.json").write_text(json.dumps(result, indent=2)+"\n")
    print("64 supports; 27 single-piece types; 36 nonzero chain types plus zero.")
    print("Minimal lengths:", dict(Counter(map(len, words.values()))))
    print("Checked 1,369 products, interface swaps, and 1,024 compatible two-piece safe blocks.")
    print("Saved 64 universal local witnesses,", len(chains), "chain witnesses, and",
          len(result["necklace_examples"]), "necklace covers.")


if __name__ == "__main__":
    main()
