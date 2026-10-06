#!/usr/bin/env python3
"""Independent cycle-space audit of all prepared minimum exchanges.

No constructor imports. The previous graph, minimum-size proof, and girth
are inherited from pinned certificates; all new witnesses are checked here.
"""
from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path

from verify_secondary_minimum_obstruction import Check
from verify_neutral_minimum_quotient import forest_cycles, pivots, belongs, mask

HERE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def switch(obj, flow, b, edges):
    assert edges == sorted(set(edges)) and len(obj.circuits(mask(edges))) == 1
    assert all(flow[e] != b for e in edges)
    C = set(edges)
    after = [x ^ b if e in C else x for e, x in enumerate(flow)]
    obj.flow(after)
    return after


def main():
    data = json.loads((HERE / 'prepared_minimum_exchange.json').read_text())
    assert data['sources'] == [
        {'file': 'secondary_minimum_obstruction.json', 'sha256': 'f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5'},
        {'file': 'minimum_matching_secondary.json', 'sha256': '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec'},
        {'file': 'neutral_minimum_quotient.json', 'sha256': 'cd19d33ccb19649d6f39b5daf8d7b74d76317f9f2c328d9eb059c27e083ed754'}]
    for record in data['sources']:
        assert hashlib.sha256((HERE / record['file']).read_bytes()).hexdigest() == record['sha256']
    source = json.loads((HERE / data['sources'][0]['file']).read_text())
    previous = json.loads((HERE / data['sources'][2]['file']).read_text())
    obj, a = Check(source['graph']), data['target_color']
    flow = source['initial_flow']
    obj.flow(flow)
    original = tuple(e for e, x in enumerate(flow) if x == a)
    M = mask(original)
    assert a == 4 and list(original) == data['original_matching'] == [178, 183, 189]
    assert len(original) == data['minimum_size'] == source['minimum_color_multiplicity'] == 3
    assert source['girth_certificate']['girth'] == 5
    assert all(K.bit_count() % 2 == 0 for K in obj.unmatched(M)[3])
    cycles = forest_cycles(obj, obj.full ^ M)
    assert len(cycles) == data['source_fiber_dimension'] == 67
    assert data['source_flow_count'] == 1 << 67
    all_cycles = forest_cycles(obj, obj.full)
    pairs = {}
    for record in data['suitable_replacements']:
        K = tuple(record['matching'])
        assert K == tuple(sorted(set(K))) and len(K) == 3 and K not in pairs
        F, t = record['first'], record['partner']
        assert obj.even(F) and obj.even(t) and F & t == mask(K)
        assert all(C.bit_count() % 2 == 0 for C in obj.unmatched(mask(K))[3])
        pairs[K] = F, t
    assert len(pairs) == 37 and original not in pairs

    assert [row['increments'] for row in data['planes']] == [[1, 5], [2, 6], [3, 7]]
    expected = [(6, 70, 5, 35), (8, 72, 5, 3), (9, 71, 7, 2)]
    union = set()
    for row, expected_row in zip(data['planes'], expected):
        b, c = row['increments']
        P_edges = [e for e, x in enumerate(flow) if x in (a, b, c)]
        P, Z = mask(P_edges), obj.full ^ mask(P_edges)
        assert row['plane_edges'] == P_edges and row['zero_edges'] == Z and obj.even(Z)
        # Order quotient vertices by their least original vertex, as saved.
        parts = sorted(obj.components(Z), key=lambda C: (C & -C).bit_length())
        assert row['zero_components'] == parts
        component = {v: i for i, C in enumerate(parts) for v in range(obj.n) if C >> v & 1}
        endpoints = [[component[obj.edges[e][0]], component[obj.edges[e][1]]] for e in P_edges]
        columns = [(1 << u) ^ (1 << v) for u, v in endpoints]
        assert endpoints == row['quotient_endpoints'] and columns == row['edge_columns']
        boundaries = []
        for color in (a, b, c):
            boundary = 0
            for e, col in zip(P_edges, columns):
                if flow[e] == color:
                    boundary ^= col
            boundaries.append(boundary)
        assert boundaries == [row['terminal_mask']] * 3
        rZ = len(forest_cycles(obj, Z))
        assert rZ == row['zero_cycle_dimension']

        # A prescribed exchange extends through Z iff it belongs to this
        # projection of Z(G). Preparation existence is a separate linear
        # restriction of Z(G-M) onto the new matching edges.
        exchange_space = pivots(C & P for C in all_cycles)
        reachable, excluded = {}, []
        for size in range(4):
            for K in combinations(P_edges, size):
                if not belongs(M ^ mask(K), exchange_space):
                    continue
                new = mask(e for e in K if e not in original)
                preparation_space = pivots(X & new for X in cycles)
                prescribed = mask(e for e in K if e not in original and flow[e] != c)
                if not belongs(prescribed, preparation_space):
                    excluded.append(list(K))
                    continue
                assert size == 3
                dimension = len(cycles)-len(preparation_space)
                reachable[K] = dimension
                # The partner increment has the same number of preparations.
                assert belongs(new ^ prescribed, preparation_space)
        records = {tuple(record['matching']): record for record in row['replacements']}
        assert len(records) == len(row['replacements']) and set(records) == set(reachable)
        assert excluded == row['excluded_parity_joins'] == [] and original in records
        for K, dimension in reachable.items():
            record = records[K]
            assert dimension == record['eligible_lift_dimension_per_increment']
            assert dimension-rZ == record['remaining_cycle_dimension']
            new_count = len(set(K)-set(original))
            assert dimension == 67-new_count
            C = record['exchange_circuit']
            if K == original:
                assert C == []
            else:
                assert K in pairs and C == sorted(set(C))
                assert len(obj.circuits(mask(C))) == 1
                assert mask(C) & P == M ^ mask(K)
        assert (len(parts), len(P_edges), rZ, len(records)) == expected_row
        union |= set(records)
    assert union == {original} | set(pairs)
    print('PASS: independent linear tests recover all three prepared replacement sets and multiplicities.', flush=True)

    profiles = data['lift_profiles']
    observed = sorted({e for K in pairs for e in K if e not in original})
    assert observed == profiles['observed_edges'] == [6, 7, 143, 144, 148, 163, 174, 175, 177, 179, 180, 181, 190]
    def compress(X):
        return sum(((X >> e) & 1) << j for j, e in enumerate(observed))
    restriction_rank = len(pivots(compress(X) for X in cycles))
    assert restriction_rank == profiles['restriction_rank'] == 10
    # Enumerate image patterns while retaining one full even-subgraph lift
    # of each, independently of the constructor's reduced-basis traversal.
    representatives = {0: 0}
    for X in cycles:
        projection = compress(X)
        for pattern, Y in list(representatives.items()):
            representatives.setdefault(pattern ^ projection, Y ^ X)
    assert len(representatives) == profiles['pattern_count'] == 1024
    assert profiles['lifts_per_pattern'] == 1 << 57
    distribution, table, coverage = Counter(), [], Counter()
    for pattern, X in sorted(representatives.items()):
        current = [x ^ a if X >> e & 1 else x for e, x in enumerate(flow)]
        obj.flow(current)
        assert tuple(e for e, x in enumerate(current) if x == a) == original
        counts, combined = [], set()
        for row in data['planes']:
            eligible, available = set(), set()
            for record in row['replacements']:
                K = tuple(record['matching'])
                if K == original:
                    continue
                for b in row['increments']:
                    if all(current[e] == (a ^ b) for e in K if e not in original):
                        C = record['exchange_circuit']
                        assert all(current[e] != b for e in C)
                        changed = set(C)
                        after = [x ^ b if e in changed else x for e, x in enumerate(current)]
                        obj.flow(after)
                        assert tuple(e for e, x in enumerate(after) if x == a) == K
                        eligible.add(K)
                        available.add(b)
            counts.append(len(eligible))
            combined |= eligible
            coverage.update(available)
        assert len(combined) == sum(counts)
        distribution[tuple(counts)] += 1
        table.append([pattern] + counts)
    expected_distribution = {(18, 2, 1): 192, (22, 2, 1): 640, (26, 2, 1): 192}
    assert dict(distribution) == expected_distribution
    assert profiles['distribution'] == [
        {'plane_counts': list(cs), 'replacement_count': sum(cs), 'patterns': count}
        for cs, count in sorted(distribution.items())]
    assert digest(table) == profiles['pattern_table_sha256']
    assert profiles['increment_coverage_patterns'] == [[b, coverage[b]] for b in (1, 2, 3, 5, 6, 7)]
    assert dict(coverage) == {1: 1024, 2: 1024, 3: 512, 5: 1024, 6: 1024, 7: 512}
    print('PASS: all 1,024 image patterns; exactly 21, 25, or 29 suitable single-circuit replacements per lift.', flush=True)

    transport = data['universal_transport']
    old, new = transport['removed_edge'], transport['added_edge']
    assert (old, new) == (189, 148)
    C = mask(transport['circuit'])
    assert transport['circuit'] == [142, 146, 148, 189, 190, 194]
    assert len(obj.circuits(C)) == 1 and C & M == 1 << old
    P = mask(data['planes'][0]['plane_edges'])
    assert C & (P ^ M) == 1 << new
    assert transport['increments'] == [1, 5] and transport['canonical_increment'] == (a ^ flow[new]) == 1
    K = M ^ (1 << old) ^ (1 << new)
    assert K == mask(transport['target_matching']) and tuple(transport['target_matching']) in pairs
    canonical = switch(obj, flow, 1, transport['circuit'])
    assert canonical == transport['canonical_target_flow'] == previous['repair']['moves'][0]['flow_after']
    target_cycles = forest_cycles(obj, obj.full ^ K)
    images = [X ^ (C if X >> new & 1 else 0) for X in cycles]
    assert all(obj.even(Y) and not Y & K for Y in images)
    assert all((Y ^ (C if Y >> old & 1 else 0)) == X for X, Y in zip(cycles, images))
    assert len(pivots(images)) == transport['image_rank'] == 67
    assert len(target_cycles) == transport['target_fiber_dimension'] == 67
    for Y in target_cycles:
        X = Y ^ (C if Y >> old & 1 else 0)
        assert obj.even(X) and not X & M
        assert X ^ (C if X >> new & 1 else 0) == Y
    # Check the nonlinear-looking adaptive switch against its affine formula
    # on every source basis direction; linearity handles all 2^67 choices.
    for X, Y in zip(cycles, images):
        current = [x ^ a if X >> e & 1 else x for e, x in enumerate(flow)]
        after = switch(obj, current, a ^ current[new], transport['circuit'])
        assert after == [x ^ a if Y >> e & 1 else x for e, x in enumerate(canonical)]
    successful = transport['canonical_successful_flow']
    assert successful == previous['repair']['moves'][-1]['flow_after']
    obj.flow(successful)
    assert all(x ^ y in (0, a) for x, y in zip(canonical, successful))
    difference = mask(e for e, (x, y) in enumerate(zip(canonical, successful)) if x != y)
    assert obj.even(difference) and not difference & K
    F, t = pairs[tuple(transport['target_matching'])]
    assert obj.support(successful, 4) == F
    w = t ^ obj.support(successful, 1) ^ obj.support(successful, 2)
    assert obj.even(w) and w == previous['repair']['fourth_coordinate']
    palette = [4, 5, 6, 15, 8]
    cover = previous['repair']['cover_pairs']
    assert len(cover) == obj.m and all(0 <= x < 32 and x.bit_count() == 2 for x in cover)
    for e, value in enumerate(cover):
        i, j = [j for j in range(5) if value >> j & 1]
        transformed = sum(((successful[e] & ell).bit_count() % 2) << j for j, ell in enumerate([2, 1, 4]))
        assert palette[i] ^ palette[j] == transformed + 8*((w >> e) & 1)
    assert all(obj.even(mask(e for e, value in enumerate(cover) if value >> layer & 1)) for layer in range(5))
    assert transport['cover_repair_switch_bound'] == 1+obj.n//5 == 28
    print('PASS: the fixed six-circuit bijects all 2^67 source lifts with a suitable target fiber; cover verified.', flush=True)

    demo = data['prepared_increment_demo']
    assert demo['previously_rigid_increment'] == 7 and demo['required_preparation_edge'] == 190
    candidates = [r['matching'] for r in data['planes'][2]['replacements'] if r['matching'] != list(original)]
    assert candidates == [[178, 183, 190]]
    assert flow[190] == 7  # This target is initially blocked for increment 7.
    current = flow
    for j, name in enumerate(['preparation', 'exchange']):
        record = demo[name]
        assert record['increment'] == [4, 7][j]
        current = switch(obj, current, record['increment'], record['edges'])
        assert current == record['flow_after']
        assert record['color_sizes'] == [current.count(x) for x in range(1, 8)]
        assert current.count(a) == min(record['color_sizes']) == 3
        assert [e for e, x in enumerate(current) if x == a] == [list(original), candidates[0]][j]
        assert all(C.bit_count() % 2 == 0 for C in obj.unmatched(mask([list(original), candidates[0]][j]))[3])
    assert demo['target_matching'] == candidates[0] and tuple(candidates[0]) in pairs
    assert len(demo['exchange']['edges']) == 6 and current.count(a) == 3
    # Independent breadth-first layers give the shortest circuit through
    # required edge 190 in G-M, hence the sharp single-preparation bound.
    required = 190
    u, v = obj.edges[required]
    seen, frontier, distance = {v}, {v}, 0
    while u not in seen:
        frontier = {w for x in frontier for w, e in obj.adj[x]
                    if e not in original and e != required and w not in seen}
        assert frontier
        seen |= frontier
        distance += 1
    assert distance+1 == len(demo['preparation']['edges']) == demo['shortest_single_preparation_length'] == 14
    print('PASS: a shortest 14-edge color-4 preparation unlocks the rigid increment 7, followed by a six-circuit.')
    print('Scope: one complete fixed-projection family, not all projections or a universal escape theorem.')


if __name__ == '__main__':
    main()
