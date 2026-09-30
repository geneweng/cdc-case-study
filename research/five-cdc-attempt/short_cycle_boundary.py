#!/usr/bin/env python3
"""Exact charge automata for prescribed cover boundaries in cycle quotients.

Standard library only. The independent verifier imports none of this code.
See short-cycle-boundary.md for the reduction and its precise limitations.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from fourflow_quotient_repair import build, quotient_flow, repair
from joint_boundary_completion import PAIRS, load_covers, masks_and_flows, word

HERE = Path(__file__).parent
EVEN = [h for h in range(32) if h.bit_count() % 2 == 0]


def local_table(kind):
    table, assignments = {}, 0
    for a, b, c, d in itertools.product(PAIRS, repeat=4):
        r = a ^ b ^ c ^ d
        if r not in PAIRS:
            continue
        if kind == 'semi' and b != d:
            continue
        if kind == 'blowup' and (a ^ c not in PAIRS or b ^ d not in PAIRS):
            continue
        z = (a & 1)+2*(b & 1)+4*(c & 1)+8*(d & 1)
        values = [a, b, c, d]+([a ^ c, b ^ d] if kind == 'blowup' else [])+[r]
        table.setdefault((r, z), {}).setdefault(a ^ b, values)
        assignments += 1
    return table, assignments


def left_bit(z):
    return (z & 1) ^ (z >> 1 & 1)


def state_digest(dist):
    records = sorted((r, [h for h in EVEN if m >> h & 1], d)
                     for (r, m), d in dist.items())
    return hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()


def automaton(table, parity):
    initial = sum(1 << h for h in EVEN if h & 1 == parity)
    start = (0, initial)
    distance, parent, queue = {start: 0}, {}, deque([start])
    steps = {p: [(r, z, set(allowed)) for (r, z), allowed in sorted(table.items())
                 if left_bit(z) == p] for p in (0, 1)}
    while queue:
        prefix, mask = queue.popleft()
        for r, z, allowed in steps[parity ^ (prefix & 1)]:
            following = (prefix ^ r, mask & sum(1 << (h ^ prefix) for h in allowed))
            if following not in distance:
                distance[following] = distance[prefix, mask]+1
                parent[following] = ((prefix, mask), [r, z])
                queue.append(following)

    def path(state):
        result = []
        while state != start:
            state, letter = parent[state]
            result.append(letter)
        return list(reversed(result))

    shortest = [min(d for (r, m), d in distance.items() if r == 0 and m.bit_count() == n)
                for n in range(9)]
    positive = []
    for k in range(3, 8):
        state = min((s for s, d in distance.items() if s[0] == 0 and d == k and s[1]),
                    key=lambda s: (s[1].bit_count(), s))
        positive.append(path(state))
    bad = (0, 0)
    assert len(distance) == 4096 and shortest[0] == 8+parity
    return {'initial_parity': parity, 'reachable_states': len(distance),
            'distance_histogram': sorted(Counter(distance.values()).items()),
            'shortest_closed_by_survivor_count': shortest,
            'distance_sha256': state_digest(distance), 'shortest_rejected_word': path(bad)}, positive


def filter_word(table, letters):
    parity = left_bit(letters[0][1])
    survivors = {h for h in EVEN if h & 1 == parity}
    prefix, trace = 0, [sorted(survivors)]
    for r, z in letters:
        assert left_bit(z) == parity ^ (prefix & 1)
        survivors &= {h ^ prefix for h in table[r, z]}
        trace.append(sorted(survivors))
        prefix ^= r
    assert prefix == 0
    return trace


def quotient_assignment(g, letters, table, h=None):
    """Return F on kept edges, and optionally a cover for surviving charge h."""
    bits, pairs, prefix = {}, {}, 0
    for junction, (r, z) in zip(g['junctions'], letters):
        a, b, c, d = [z >> j & 1 for j in range(4)]
        values = [a, b, c, d]
        if g['construction'] == 'blowup':
            values += [a ^ c, b ^ d]
        values += [r & 1]
        for e, v in zip(junction['edges'], values):
            assert e not in bits or bits[e] == v
            bits[e] = v
        if h is not None:
            for e, v in zip(junction['edges'], table[r, z][h ^ prefix]):
                assert e not in pairs or pairs[e] == v
                pairs[e] = v
        prefix ^= r
    support = sum(1 << i for i, e in enumerate(g['kept_edge_ids']) if bits.get(e, 0))
    cover = None if h is None else word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids'])
    return support, cover


def cap(kind, k):
    edges = [(i, (i+1) % k) for i in range(k)]+[(i, k) for i in range(k)]
    return build(k+1, edges, [list(range(k))], kind)


def boundary_record(kind, table, letters):
    g = cap(kind, len(letters))
    trace = filter_word(table, letters)
    support, cover = quotient_assignment(g, letters, table, min(trace[-1]) if trace[-1] else None)
    return {'length': len(letters), 'letters': letters, 'survivor_trace': trace,
            'vertices': g['quotient_vertices'], 'edges': g['quotient_edges'],
            'support': support, 'cover_word': cover}


def cubic_counterexample(kind, table, letters, fibers, domains, witnesses):
    k, perm = 8, [0, 1, 5, 2, 3, 7, 4, 6]
    inverse = {v: i for i, v in enumerate(perm)}
    base = [(off+i, off+(i+1) % k) for off in (0, k) for i in range(k)]
    base += [(i, k+inverse[i]) for i in range(k)]
    g = build(16, base, [list(range(k))], kind)
    quotient_flow(g, [1, 2]*4+[3]*8)
    first, _ = quotient_assignment(g, letters, table)
    rim, previous = [], 10
    for j in perm:
        previous ^= letters[j][0]
        assert previous in PAIRS
        rim.append(previous)
    assert previous == 10
    core_cover = word(PAIRS.index(a) for a in rim+[r for r, _ in letters])
    four = list(map(int, g['quotient_four_flow_word']))
    quotient_values = [2*a+(first >> i & 1) for i, a in enumerate(four)]
    values = dict(zip(g['kept_edge_ids'], quotient_values))
    for b in g['blocks']:
        es = b['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    initial = [values[e] for e in range(len(g['edges']))]
    completion = repair(g, initial, 1, fibers, domains, witnesses)
    assert completion['quotient_cover_word'][:16] != core_cover
    g.update({'rejected_letters': letters, 'quotient_support': first,
              'rejected_core_cover_word': core_cover, 'initial_flow_word': word(initial),
              'alternative_completion': completion})
    return g


def square_switch():
    g = cap('semi', 4)
    quotient_flow(g, [1]*4)
    flow = list(map(int, g['quotient_four_flow_word']))
    prep = {'edges': [4, 5, 6], 'increment': 1}
    after = flow.copy()
    for e in prep['edges']:
        after[e] ^= prep['increment']
    lift = {'edges': [0, 2, 4, 14, 12], 'increment': 2}
    final = after.copy()
    for e in lift['edges']:
        final[e] ^= lift['increment']
    return {'vertices': g['quotient_vertices'], 'edges': g['quotient_edges'],
            'flow_word': word(flow), 'cap_vertex': 4, 'core_edges': [0, 1, 2, 3],
            'selected_core_edges': [0, 2], 'increment': 2,
            'initial_port_components_avoiding_increment': [[0, 1], [2, 3]],
            'preparation': prep, 'prepared_flow_word': word(after),
            'lifted_switch': lift, 'final_flow_word': word(final),
            'minimum_internal_preparations_for_this_lift': 1}


def main():
    _, fibers = masks_and_flows()
    domains, witnesses = load_covers()
    result = {'date': '2026-09-30',
              'scope': 'All compatible prescribed cover boundaries extend for cycle lengths 3 through 7; first failure at 8. This does not disprove existential completion equivalence at 8 or the general 5-CDC conjecture.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                          for name in ('petersen_boundary_relation.txt.gz', 'joint_boundary_completion.json')],
              'constructions': {}, 'cubic_examples': [], 'square_switch': square_switch()}
    for kind in ('blowup', 'semi'):
        table, count = local_table(kind)
        records, positives = [], []
        for parity in (0, 1):
            audit, words = automaton(table, parity)
            records.append(audit)
            positives += [boundary_record(kind, table, letters) for letters in words]
        bad = [[r, 3 if kind == 'blowup' else (15 if i % 2 else 0)]
               for i, r in enumerate([6, 10, 6, 18, 6, 10, 6, 18])]
        rejected = boundary_record(kind, table, bad)
        assert not rejected['survivor_trace'][-1]
        result['constructions'][kind] = {
            'junction_assignments': count, 'local_key_count': len(table),
            'domain_size_histogram': sorted(Counter(map(len, table.values())).items()),
            'local_table': [{'r': r, 'z': z, 'witnesses': [[h, values] for h, values in sorted(allowed.items())]}
                            for (r, z), allowed in sorted(table.items())],
            'automata': records, 'positive_caps': positives, 'rejected_octagon': rejected}
        ex = cubic_counterexample(kind, table, bad, fibers, domains, witnesses)
        result['cubic_examples'].append(ex)
        print(kind, len(table), 'local keys; 8192 automaton states;', ex['vertices'],
              'vertices in cubic example;', len(ex['alternative_completion']['moves']), 'internal repairs', flush=True)
    (HERE / 'short_cycle_boundary.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved all finite-state audits, 20 positive caps, two rejected octagons, two cubic completions, and a square switch diagnostic.')


if __name__ == '__main__':
    main()
