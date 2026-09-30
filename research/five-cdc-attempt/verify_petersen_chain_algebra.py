#!/usr/bin/env python3
"""Independent standard-library check of the conditional chain algebra.

No constructor imports, no SAT solver, and no trust in saved negative states.
Local relations are rebuilt by exhaustively selecting binary even layers.
Composition uses sets of ordered state pairs, not integer matrix rows.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
EDGES = INTERNAL+[(v, None) for v in PORTS]
PAIRS = [sum(1 << i for i in pair) for pair in itertools.combinations(range(5), 2)]
STATES = list(itertools.product(range(10), repeat=2))


def even_supports():
    stars = [sum(1 << e for e, ends in enumerate(EDGES) if v in ends) for v in range(2, 10)]
    return [s for s in range(1 << 14) if all((s & star).bit_count() % 2 == 0 for star in stars)]


def rebuild_local(evens):
    """Three chosen even layers determine the symmetric difference of the last two."""
    relations = {f: set() for f in evens}
    even_set = set(evens)
    full = (1 << 14)-1
    count = 0
    for a in evens:
        for b in evens:
            once_ab, twice_ab = a ^ b, a & b
            for c in evens:
                if c & twice_ab:
                    continue
                once = once_ab ^ c
                twice = twice_ab | (once_ab & c)
                zero = full ^ (once | twice)
                for d in evens:
                    if d & twice or d & zero != zero:
                        continue
                    e = d ^ once
                    if e not in even_set:
                        continue
                    rows = [a, b, c, d, e]
                    boundary = [PAIRS.index(sum(1 << label for label, row in enumerate(rows)
                                                if row >> edge & 1)) for edge in range(10, 14)]
                    p, q, r, s = boundary
                    relations[a].add((10*p+q, 10*r+s))
                    count += 1
    assert count == 14700
    return {f: frozenset(r) for f, r in relations.items()}


def product(left, right):
    index = defaultdict(set)
    for middle, end in right:
        index[middle].add(end)
    return frozenset((start, end) for start, middle in left for end in index[middle])


def local_word(mask, boundary, word):
    assert len(word) == 14 and tuple(map(int, word[10:])) == tuple(boundary)
    values = [PAIRS[int(c)] for c in word]
    assert sum(1 << e for e, a in enumerate(values) if a & 1) == mask
    for v in range(2, 10):
        incident = [a for ends, a in zip(EDGES, values) if v in ends]
        assert len(incident) == 3
        for label in range(5):
            assert sum(a >> label & 1 for a in incident) in (0, 2)


def status(state):
    a, b = STATES[state]
    return bool(PAIRS[a] & 1)+2*bool(PAIRS[b] & 1)


def charged_states(port_bits, charge):
    return {i for i, (a, b) in enumerate(STATES)
            if status(i) == port_bits and PAIRS[a] ^ PAIRS[b] == charge}


def check_necklace(rec):
    masks, twists = rec["local_masks"], rec["twists"]
    k = len(masks)
    assert k >= 1 and len(twists) == k and set(twists) <= {0, 1}
    assert rec["vertices"] == 8*k
    expected, first = [], []
    for i, f in enumerate(masks):
        expected.extend([[8*i+u-2, 8*i+v-2] for u, v in INTERNAL])
        first.extend(bool(f >> e & 1) for e in range(10))
    for i, f in enumerate(masks):
        following = (i+1) % k
        for j in range(2):
            h = j ^ twists[i]
            assert (f >> (12+j)) & 1 == (masks[following] >> (10+h)) & 1
            expected.append([8*i+PORTS[2+j]-2, 8*following+PORTS[h]-2])
            first.append(bool(f >> (12+j) & 1))
    assert expected == rec["edges"] and len(expected) == 12*k
    assert len({tuple(sorted(e)) for e in expected}) == len(expected)
    assert all(u != v for u, v in expected)
    assert rec["prescribed_edges"] == [e for e, member in enumerate(first) if member]
    values = [PAIRS[int(c)] for c in rec["cover_word"]]
    assert len(values) == len(expected)
    assert [bool(a & 1) for a in values] == first
    for v in range(8*k):
        incident = [a for ends, a in zip(expected, values) if v in ends]
        assert len(incident) == 3
        for label in range(5):
            assert sum(a >> label & 1 for a in incident) in (0, 2)


def main():
    data = json.loads((HERE / "petersen_chain_algebra.json").read_text())
    assert data["pair_masks"] == PAIRS
    assert data["internal_edges"] == [list(e) for e in INTERNAL] and data["port_vertices"] == PORTS
    source = HERE / data["source_relation_file"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == data["source_relation_sha256"]
    evens = even_supports()
    assert len(evens) == data["local_supports"] == 64
    local = rebuild_local(evens)
    assert sum(map(len, local.values())) == 4220 and all(local.values())
    generators = list(dict.fromkeys(local.values()))
    assert len(generators) == data["generator_types"] == 27
    print("Independent binary-layer enumeration rebuilt all 4,220 conditional states.")

    # Breadth-first exhaustion proves both closure and the minimum chain lengths.
    shortest = dict.fromkeys(generators, 1)
    frontier = generators
    while frontier:
        following = []
        for a in frontier:
            for b in generators:
                result = product(a, b)
                if result and result not in shortest:
                    shortest[result] = shortest[a]+1
                    following.append(result)
        frontier = following
    assert len(shortest) == data["nonzero_chain_types"] == 36
    assert Counter(shortest.values()) == {1: 27, 2: 7, 3: 2}
    assert data["shortest_word_histogram"] == {"1": 27, "2": 7, "3": 2}
    relations = []
    for index, rec in enumerate(data["types"]):
        assert rec["id"] == index
        masks = rec["representative_masks"]
        relation = local[masks[0]]
        for f in masks[1:]:
            relation = product(relation, local[f])
        assert relation in shortest and len(masks) == shortest[relation]
        assert len(relation) == rec["boundary_states"]
        assert len(rec["rows_hex"]) == 100
        saved = frozenset((i, j) for i, row in enumerate(rec["rows_hex"])
                          for j in range(100) if int(row, 16) >> j & 1)
        assert all(0 <= int(row, 16) < 1 << 100 for row in rec["rows_hex"])
        assert relation == saved and relation not in relations
        relations.append(relation)
    assert set(relations) == set(shortest)
    assert relations[:27] == generators
    assert data["zero_id"] == 36
    relations.append(frozenset())
    ids = {relation: i for i, relation in enumerate(relations)}
    assert data["local_type_ids"] == [[f, ids[r]] for f, r in local.items()]
    assert len(data["multiplication_table"]) == 37
    for i, a in enumerate(relations):
        assert len(data["multiplication_table"][i]) == 37
        for j, b in enumerate(relations):
            assert data["multiplication_table"][i][j] == ids[product(a, b)]
            if a and b:
                out = {status(t) for _, t in a}
                ins = {status(s) for s, _ in b}
                assert len(out) == len(ins) == 1
                assert bool(product(a, b)) == (out == ins)
    for key, input_side in (("swap_input_ids", True), ("swap_output_ids", False)):
        assert len(data[key]) == 37
        for i, a in enumerate(relations):
            swapped = frozenset((10*(s % 10)+s//10, t) if input_side
                                else (s, 10*(t % 10)+t//10) for s, t in a)
            assert data[key][i] == ids[swapped]
        assert all(v < 27 for v in data[key][:27])
    print("Verified all 1,369 semigroup products, minimum lengths, zero cases, and port swaps.")

    # Verify the local bounds used in the safe-charge proof, on every charge.
    for f, relation in local.items():
        left, right = (f >> 10) & 3, f >> 12
        odd = left in (1, 2)
        charges = [q for q in range(32) if q & 1 and q.bit_count() == 4] if odd else [0]
        for q in charges:
            starts, ends = charged_states(left, q), charged_states(right, q)
            restricted = relation & frozenset(itertools.product(starts, ends))
            if odd or left != 0 or right != 0:
                assert restricted == frozenset(itertools.product(starts, ends))
            else:
                assert len(starts) == len(ends) == 6
                assert min(sum((s, t) in restricted for t in ends) for s in starts) >= 5
                assert min(sum((s, t) in restricted for s in starts) for t in ends) >= 5
    compatible = safe_blocks = 0
    for f, a in local.items():
        for g, b in local.items():
            if f >> 12 != (g >> 10) & 3:
                continue
            compatible += 1
            composed = product(a, b)
            odd = ((f >> 10) & 3) in (1, 2)
            charges = [q for q in range(32) if q & 1 and q.bit_count() == 4] if odd else [0]
            for q in charges:
                required = frozenset(itertools.product(charged_states((f >> 10) & 3, q),
                                                      charged_states(g >> 12, q)))
                assert required and required <= composed
                safe_blocks += 1
    assert compatible == data["compatible_two_piece_checks"] == 1024
    assert safe_blocks == 2560
    seen = set()
    for rec in data["universal_boundary_witnesses"]:
        f = rec["mask"]
        assert f in evens and f not in seen
        off = 7 if ((f >> 10) & 3) in (1, 2) else 4
        boundary = [0 if f >> (10+i) & 1 else off for i in range(4)]
        assert boundary == rec["boundary"]
        local_word(f, boundary, rec["cover_word"])
        seen.add(f)
    assert seen == set(evens)
    empty_word = data["three_label_empty_word"]
    local_word(0, [4, 4, 4, 4], empty_word)
    assert set(empty_word) <= set("457")  # Only the pairs 12,13,23.
    print("Checked 2,560 safe charge blocks and 64 universal local witnesses.")

    example = data["parity_example"]
    assert example == {"local_mask": 887, "charge": 6, "first_class": [[5, 7], [7, 5]],
                       "second_class": [[6, 8], [8, 6]],
                       "even_endpoint": [5, 7, 5, 7], "odd_endpoint": [5, 7, 6, 8]}
    a = {10*p+q for p, q in example["first_class"]}
    b = {10*p+q for p, q in example["second_class"]}
    assert a | b == charged_states(0, 6)
    restricted = frozenset((s, t) for s, t in local[887] if s in a | b)
    crossing = frozenset(itertools.product(a, b)) | frozenset(itertools.product(b, a))
    parallel = frozenset(itertools.product(a, a)) | frozenset(itertools.product(b, b))
    assert restricted == crossing
    assert product(crossing, crossing) == parallel
    assert product(parallel, crossing) == crossing
    for rec in data["chain_examples"]:
        masks, words = rec["local_masks"], rec["local_cover_words"]
        assert len(masks) == len(words) > 0
        assert list(map(int, words[0][10:12]+words[-1][12:])) == rec["boundary"]
        for f, word in zip(masks, words):
            local_word(f, tuple(map(int, word[10:])), word)
        assert all(left[12:] == right[10:12] for left, right in zip(words, words[1:]))
    assert len(data["chain_examples"]) == 6
    print("Verified the persistent odd/even obstruction and six reconstructed chain covers.")
    for rec in data["necklace_examples"]:
        assert set(rec["local_masks"]) <= set(evens)
        check_necklace(rec)
    assert len(data["necklace_examples"]) == 74
    assert set(f for rec in data["necklace_examples"] for f in rec["local_masks"]) == set(evens)
    print("Verified 74 necklace covers, including twists, all local supports, and graphs up to 248 vertices.")


if __name__ == "__main__":
    main()
