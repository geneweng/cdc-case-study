#!/usr/bin/env python3
"""Independent standard-library check of the complete 16,384-matrix lemma.

Uses polynomial-bit multiplication, adds each Hermitian edge to both endpoint
bits, and solves the two-variable offset equations by binary elimination.
Does not import the classification or graph-search implementation.
"""
from collections import Counter
import itertools
import json
from pathlib import Path


def multiply(a, b):
    product = 0
    for bit in range(2):
        if b >> bit & 1:
            product ^= a << bit
    if product & 4:
        product ^= 7  # alpha^2+alpha+1 = 0
    return product


def conjugate(a):
    return multiply(a, a)


def trace(a):
    return a ^ conjugate(a)


def consistent(bits, states, active):
    pivots = {}
    for b, s, a in zip(bits, states, active):
        row = ((s >> 1) | (((s & 1) ^ (s >> 1)) << 1)) if a else 0
        augmented = row | (b << 2)
        for bit in (0, 1):
            if augmented >> bit & 1:
                if bit in pivots:
                    augmented ^= pivots[bit]
                else:
                    pivots[bit] = augmented
                    break
        else:
            if augmented & 4:
                return False
    return True


def main():
    path = Path(__file__).with_name("rank_one_obstruction_results.json")
    saved = json.loads(path.read_text())["finite_audit"]
    pairs = list(itertools.combinations(range(4), 2))
    for m, record in zip(range(2, 6), saved):
        active = [int(i < m-1 or i == 4) for i in range(5)]
        states = []
        for prefix in itertools.product((1, 2, 3), repeat=4):
            state = prefix+(1,); total = 0
            for a, s in zip(active, state):
                if a:
                    total ^= s
            if not total:
                states.append(state)
        histogram = Counter(); failures = set()
        for labels in itertools.product(range(4), repeat=6):
            count = 0
            for state in states:
                bits = [0]*5
                for (i, j), label in zip(pairs, labels):
                    contribution = trace(multiply(multiply(state[i], conjugate(state[j])), label))
                    assert contribution in (0, 1)
                    bits[i] ^= contribution; bits[j] ^= contribution
                count += consistent(bits, state, active)
            histogram[count] += 1
            if not count:
                failures.add(labels)
        assert histogram == {int(k): v for k, v in record["success_count_histogram"].items()}
        assert failures == {tuple(r["upper_triangle"]) for r in record["failures"]}
        print(m, "active components:", 4096, "matrices checked;", len(failures), "failures")


if __name__ == "__main__":
    main()
