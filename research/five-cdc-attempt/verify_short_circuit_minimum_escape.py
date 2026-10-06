#!/usr/bin/env python3
"""Audit the complete matching census and short-circuit escape independently.

No constructor imports or constraint solvers. Positive local/outer witnesses
and a direct negative obstruction cover every type and every actual matching.
"""
from collections import Counter
from itertools import product
import hashlib
import json
from pathlib import Path

from verify_secondary_minimum_obstruction import Check
from verify_neutral_minimum_quotient import forest_cycles, pivots, mask
from verify_minimum_matching_secondary import decode, code, even, labels

HERE = Path(__file__).resolve().parent


def check_cover(obj, flow, F, t, saved=None):
    obj.flow(flow)
    assert obj.support(flow, 4) == F
    w = t ^ obj.support(flow, 1) ^ obj.support(flow, 2)
    assert obj.even(w)
    transformed = [sum(((x & ell).bit_count() % 2) << j for j, ell in enumerate([2, 1, 4])) for x in flow]
    palette = [4, 5, 6, 15, 8]
    decode_pair = {x ^ y: (1 << i) | (1 << j) for i, x in enumerate(palette)
                   for j, y in enumerate(palette) if i < j}
    cover = [decode_pair[x + 8*((w >> e) & 1)] for e, x in enumerate(transformed)]
    assert all(v.bit_count() == 2 for v in cover)
    assert all(obj.even(mask(e for e, value in enumerate(cover) if value >> j & 1)) for j in range(5))
    if saved is not None:
        assert saved['coordinate_functionals'] == [2, 1, 4]
        assert saved['transformed_flow'] == transformed and saved['fourth_coordinate'] == w
        assert saved['cover_pairs'] == cover


def main():
    data = json.loads((HERE / 'short_circuit_minimum_escape.json').read_text())
    assert data['sources'] == [
        {'file': 'secondary_minimum_obstruction.json', 'sha256': 'f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5'},
        {'file': 'minimum_matching_secondary.json', 'sha256': '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec'},
        {'file': 'neutral_minimum_quotient.json', 'sha256': 'cd19d33ccb19649d6f39b5daf8d7b74d76317f9f2c328d9eb059c27e083ed754'}]
    for record in data['sources']:
        assert hashlib.sha256((HERE / record['file']).read_bytes()).hexdigest() == record['sha256']
    source, catalog, previous = [json.loads((HERE / r['file']).read_text()) for r in data['sources']]
    obj = Check(source['graph'])
    assert data['minimum_size'] == source['minimum_color_multiplicity'] == 3
    assert source['girth_certificate']['girth'] == 5
    Y = source['local_poles']['Y']
    local_edges = Y['edges'] + [[v, -1] for v in Y['ports']]
    groups = [[] for _ in range(11)]
    for e in range(59):
        ports = [q for q, p in enumerate(Y['ports']) if p in local_edges[e]]
        assert len(ports) <= 1
        groups[1+ports[0] if ports else 0].append(e)
    for q in range(5):
        groups[6+q] = [59+q]
    assert groups == catalog['local_edge_groups']
    required = set()
    for e in range(64):
        for boundary in product(range(4), repeat=5):
            if any((x == 3) != (e == 59+q) for q, x in enumerate(boundary)):
                continue
            total = 0
            for x in boundary:
                total ^= x
            if total or (e < 59 and any(boundary[q] == 0 for q, p in enumerate(Y['ports']) if p in local_edges[e])):
                continue
            required.add((e, code(boundary, 4)))
    lookup = {}
    for e, word, F, t in catalog['local_witnesses']:
        assert (e, word) not in lookup
        assert even(41, local_edges, F) and even(41, local_edges, t) and F & t == 1 << e
        assert tuple(labels(F, t, 64)[59:]) == decode(word, 4, 5)
        lookup[e, word] = F, t
    assert set(lookup) == required and len(lookup) == 3489

    census = data['classification']
    maps = []
    for i in range(3):
        assert obj.edges[59*i:59*(i+1)] == [[u+41*i, v+41*i] for u, v in Y['edges']]
        boundary = []
        for p in Y['ports']:
            found = [e for e, uv in enumerate(obj.edges) if 41*i+p in uv and any(v >= 123 for v in uv)]
            assert len(found) == 1
            boundary.extend(found)
        maps.append(list(range(59*i, 59*(i+1))) + boundary)
    assert maps == census['local_to_global']
    assert len(set(e for row in maps for e in row)) == 192
    for i, row in enumerate(maps):
        assert set(row) == set(source['graph']['regions'][i]['charged_edges'])
    reduced = [[u//41 if u < 123 else u-120, v//41 if v < 123 else v-120] for u, v in obj.edges[177:]]
    assert reduced == census['reduced_edges'] and len(reduced) == 30
    positive = {r[0]: r[1:] for r in census['outer_witnesses']}
    invalid = dict(census['invalid_types'])
    negative = dict(census['unsuitable_types'])
    assert len(positive) == len(census['outer_witnesses']) == 1286
    assert len(invalid) == len(census['invalid_types']) == 44 and len(negative) == 1
    assert len(set(positive) | set(invalid) | set(negative)) == 1331
    assert set(positive) | set(invalid) | set(negative) == set(range(1331))
    assert census['type_counts'] == {'suitable': 1286, 'not_matching': 44, 'unsuitable': 1}
    for kind_code, (F, t) in positive.items():
        kinds = decode(kind_code, 11, 3)
        assert even(18, reduced, F) and even(18, reduced, t)
        values = labels(F, t, 30)
        allowed_common = {5*i+kind-6 for i, kind in enumerate(kinds) if kind >= 6}
        assert {e for e in range(30) if (F & t) >> e & 1} == allowed_common
        full = [None]*177 + values
        selected = []
        for i, kind in enumerate(kinds):
            word = code(values[5*i:5*i+5], 4)
            # One checked boundary works for every actual edge of this type.
            assert all((e, word) in lookup for e in groups[kind])
            target = groups[kind][0]
            selected.append(maps[i][target])
            for e, value in enumerate(labels(*lookup[target, word], 64)):
                ge = maps[i][e]
                assert full[ge] is None or full[ge] == value
                full[ge] = value
        A = sum((x & 1) << e for e, x in enumerate(full))
        B = sum(((x >> 1) & 1) << e for e, x in enumerate(full))
        assert obj.even(A) and obj.even(B) and A & B == mask(selected)

    # Enumerate actual choices independently of the constructor's weights.
    kind_of = {e: k for k, group in enumerate(groups) for e in group}
    endpoint_masks = [sum(1 << v for v in uv) for uv in obj.edges]
    counts, bad = Counter(), []
    for local in product(range(64), repeat=3):
        K = [maps[i][e] for i, e in enumerate(local)]
        types = tuple(kind_of[e] for e in local)
        kcode = code(types, 11)
        endpoints = endpoint_masks[K[0]] | endpoint_masks[K[1]] | endpoint_masks[K[2]]
        if endpoints.bit_count() != 6:
            assert kcode in invalid
            v = invalid[kcode]
            assert v >= 123 and sum(v in obj.edges[e] for e in K) == 2
            counts['not_matching'] += 1
        elif kcode in positive:
            counts['suitable'] += 1
        else:
            assert kcode in negative and negative[kcode] == K
            bad.append(K)
            counts['unsuitable'] += 1
    assert counts == census['weighted_counts'] == {'suitable': 261887, 'not_matching': 256, 'unsuitable': 1}
    assert bad == [data['unique_unsuitable_matching']] == [[178, 183, 189]]
    M = mask(bad[0])
    D, B, _, parts = obj.unmatched(M)
    assert parts == [B] and B.bit_count() == 132
    forced = mask(e for e, (u, v) in enumerate(obj.edges) if not M >> e & 1 and (D >> u & 1 or D >> v & 1))
    obstruction = mask(data['forced_obstruction_circuit'])
    assert obj.circuits(obstruction) == [sorted(data['forced_obstruction_circuit'])]
    assert obstruction & forced == obstruction
    vertices = {v for e in data['forced_obstruction_circuit'] for v in obj.edges[e]}
    assert len(vertices) == 6 and sum(D >> v & 1 for v in vertices) == 3
    print('PASS: 262,144 actual choices; 261,887 suitable matchings and exactly one unsuitable matching.', flush=True)

    # Independent short-word audit: try all six possible increments directly,
    # including words ruled out by cardinality minimality.
    audited, nonsaturated = [], 0
    for length in range(2, 7):
        neutral_counts = Counter()
        for tail in product([1, 2, 3, 5, 6, 7], repeat=length-1):
            word = (4,) + tail
            changes = []
            for b in (1, 2, 3, 5, 6, 7):
                if b not in word:
                    changes.append(sum((x ^ b) == 4 for x in word)-1)
            if {x & 3 for x in tail} != {1, 2, 3}:
                assert min(changes) == -1
                nonsaturated += 1
            else:
                assert min(changes) == 0
                neutral_counts[changes.count(0)] += 1
        if length >= 4:
            audited.append({'circuit_length': length, 'cases': sum(neutral_counts.values()),
                            'singleton_counts': [[k, count] for k, count in sorted(neutral_counts.items())]})
    words = data['local_words']
    assert audited == words['general_audit'] and sum(r['cases'] for r in audited) == 5424
    assert nonsaturated == words['decreasing_word_cases'] == 3906
    assert nonsaturated + sum(r['cases'] for r in audited) == words['total_word_cases'] == 9330
    C = mask(data['escape_circuit'])
    path = data['escape_path_order']
    assert path == [142, 146, 148, 190, 194]
    assert data['escape_circuit'] == [142, 146, 148, 189, 190, 194]
    assert len(obj.circuits(C)) == 1 and C & M == 1 << 189
    walk = [99, 101, 104, 103, 123, 124]
    assert all(set(obj.edges[e]) == {u, v} for e, u, v in zip(path, walk, walk[1:]))
    assert all(not D >> v & 1 for v in walk[1:-1])
    assert 194 not in set(e for row in maps for e in row)
    targets = {}
    for record in data['escape_targets']:
        new = record['added_edge']
        K = sorted([178, 183, new])
        assert record['matching'] == K and new not in targets
        F, t = record['first'], record['partner']
        assert obj.even(F) and obj.even(t) and F & t == mask(K)
        assert all(P.bit_count() % 2 == 0 for P in obj.unmatched(mask(K))[3])
        targets[new] = F, t
    assert set(targets) == {142, 146, 148, 190}

    examples = {}
    high = obj.support(source['initial_flow'], 4)
    for record in data['examples']:
        initial = record['flow']
        obj.flow(initial)
        assert mask(e for e, x in enumerate(initial) if x == 4) == M
        assert record['projected_coordinates'] == [obj.support(initial, ell) for ell in (1, 2)]
        assert obj.support(initial, 4) == high
        word = tuple(initial[e] & 3 for e in path)
        assert list(word) == record['projection_word'] and word not in examples
        examples[word] = initial
        new = record['added_matching_edge']
        repair = record['repair']
        assert (repair['intersection_first'], repair['intersection_partner']) == targets[new]
        current = initial
        for j, move in enumerate(repair['moves']):
            S, b = mask(move['edges']), move['increment']
            assert len(move['edges']) == len(set(move['edges'])) and len(obj.circuits(S)) == 1
            assert all(current[e] != b for e in move['edges'])
            if j == 0:
                assert S == C and b == (4 ^ initial[new])
            else:
                assert b == 4
            current = [x ^ b if S >> e & 1 else x for e, x in enumerate(current)]
            obj.flow(current)
            assert move['flow_after'] == current and move['color_sizes'] == [current.count(x) for x in range(1, 8)]
            assert mask(e for e, x in enumerate(current) if x == 4) == mask([178, 183, new])
            assert min(move['color_sizes']) == 3
        check_cover(obj, current, *targets[new], saved=repair)
    assert [list(word) for word in examples] == words['normalized_projection_words'] and len(examples) == 6

    cycles = forest_cycles(obj, obj.full ^ M)
    assert len(cycles) == data['source_fiber_dimension'] == 67
    project = lambda X: sum(((X >> e) & 1) << i for i, e in enumerate(path))
    assert len(pivots(project(X) for X in cycles)) == data['path_restriction_rank'] == 5
    lifts = {0: 0}
    for X in cycles:
        for word, Y in list(lifts.items()):
            lifts.setdefault(word ^ project(X), Y ^ X)
    assert set(lifts) == set(range(32))
    local_patterns, projections, branches = 0, set(), Counter()
    for word in product([1, 2, 3, 5, 6, 7], repeat=5):
        low = tuple(x & 3 for x in word)
        if set(low) != {1, 2, 3} or any(x == y for x, y in zip(low, low[1:])):
            continue
        singleton = [i for i, x in enumerate(low) if low.count(x) == 1]
        if 4 in singleton:
            continue
        order = [low[0], low[1], next(x for x in (1, 2, 3) if x not in low[:2])]
        normalize = {x: i+1 for i, x in enumerate(order)}
        base = examples[tuple(normalize[x] for x in low)]
        permute = {0: 0, **{i+1: x for i, x in enumerate(order)}}
        full = [(x & 4) + permute[x & 3] for x in base]
        difference = sum((((full[e] ^ x) >> 2) & 1) << i for i, (e, x) in enumerate(zip(path, word)))
        X = lifts[difference]
        full = [x ^ 4 if X >> e & 1 else x for e, x in enumerate(full)]
        assert tuple(full[e] for e in path) == word
        obj.flow(full)
        new = path[singleton[0]]
        b = 4 ^ full[new]
        assert all(full[e] != b for e in data['escape_circuit'])
        after = [x ^ b if C >> e & 1 else x for e, x in enumerate(full)]
        obj.flow(after)
        assert mask(e for e, x in enumerate(after) if x == 4) == mask([178, 183, new])
        F, t = targets[new]
        repair_cycle = F ^ obj.support(after, 4)
        assert obj.even(repair_cycle) and not repair_cycle & mask([178, 183, new])
        final = [x ^ 4 if repair_cycle >> e & 1 else x for e, x in enumerate(after)]
        check_cover(obj, final, F, t)
        local_patterns += 1
        projections.add(low)
        branches[new] += 1
    assert local_patterns == words['full_word_count'] == 1152
    assert len(projections) == words['projection_word_count'] == 36
    assert words['chosen_target_counts'] == [[e, count] for e, count in sorted(branches.items())]
    assert dict(branches) == {142: 192, 146: 384, 148: 384, 190: 192}
    print('PASS: short-circuit lemma audit, all 1,152 realized local patterns, and all resulting five-layer covers.', flush=True)

    lower = []
    for excluded in bad[0]:
        u, v = obj.edges[excluded]
        seen, frontier, distance = {v}, {v}, 0
        while u not in seen:
            frontier = {w for x in frontier for w, e in obj.adj[x] if e != excluded and w not in seen}
            assert frontier
            seen |= frontier
            distance += 1
        lower.append([excluded, distance+1])
    assert lower == data['matching_edge_cycle_lower_bounds'] == previous['matching_edge_cycle_lower_bounds']
    assert min(length for _, length in lower) == 6
    assert data['maximum_matching_escape_switches'] == 1
    assert data['maximum_cover_fiber_rounds'] == 2
    assert data['maximum_cover_circuit_switches'] == 1+obj.n//5 == 28
    print('PASS: every global minimum class lies in the census; the sole unsuitable class has uniform shortest escape.')
    print('Scope: all globally minimizing flows on this graph; no claim for nonminimum flows or arbitrary graphs.')


if __name__ == '__main__':
    main()
