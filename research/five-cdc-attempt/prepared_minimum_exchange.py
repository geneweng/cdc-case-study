#!/usr/bin/env python3
"""Classify neutral replacements throughout one complete coordinate fiber.

Contracted incidence and T-join component tests construct the certificate.
The independent verifier instead projects binary cycle spaces.
"""
from collections import Counter, deque
from itertools import combinations
import hashlib
import json
from pathlib import Path

from minimum_color_obstruction import Graph
from neutral_minimum_quotient import intersection_builder, mask
from fiber_cut_obstructions import eliminate
from flow_space_components import cycle_basis, circuit_components

HERE = Path(__file__).resolve().parent
SOURCES = [
    ('secondary_minimum_obstruction.json', 'f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5'),
    ('minimum_matching_secondary.json', '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec'),
    ('neutral_minimum_quotient.json', 'cd19d33ccb19649d6f39b5daf8d7b74d76317f9f2c328d9eb059c27e083ed754')]


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def rank_basis(rows):
    basis = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                break
    return list(basis.values())


def source_cycles(obj, matching):
    edges = [e for e in range(obj.m) if e not in matching]
    return [mask(edges[j] for j in range(len(edges)) if C >> j & 1)
            for C in cycle_basis(obj.n, [obj.edges[e] for e in edges])]


def full_plane(obj, flow, a, b):
    P = [e for e, x in enumerate(flow) if x in (a, b, a ^ b)]
    Z = obj.full ^ mask(P)
    parts = obj.components(Z)
    component = {v: i for i, C in enumerate(parts) for v in range(obj.n) if C >> v & 1}
    endpoints = [[component[u], component[v]] for e, (u, v) in enumerate(obj.edges) if e in P]
    columns = [(1 << u) ^ (1 << v) for u, v in endpoints]
    terminal = 0
    for e, col in zip(P, columns):
        if flow[e] == a:
            terminal ^= col
    return {'increments': [b, a ^ b], 'plane_edges': P, 'zero_edges': Z,
            'zero_components': parts, 'quotient_endpoints': endpoints,
            'edge_columns': columns, 'terminal_mask': terminal,
            'zero_cycle_dimension': Z.bit_count()-obj.n+len(parts)}


def join_components(n, edges, terminal):
    parent = list(range(n))
    def root(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for u, v in edges:
        parent[root(u)] = root(v)
    parity = {}
    for v in range(n):
        r = root(v)
        parity[r] = parity.get(r, 0) ^ ((terminal >> v) & 1)
    return not any(parity.values()), len(parity)


def exchange_circuit(obj, row, original, target):
    change = mask(set(original) ^ set(target))
    equations = [(mask(es), 0) for es in obj.incident]
    equations += [(1 << e, (change >> e) & 1) for e in row['plane_edges']]
    base = eliminate(equations, obj.m)['solution']
    # Z is itself even, and hence is a disjoint union of circuits here.
    assert obj.even(row['zero_edges'])
    zero_cycles = [mask(C) for C in circuit_components(row['zero_edges'], obj.n, obj.edges)]
    assert len(zero_cycles) == row['zero_cycle_dimension']
    completions = [0]
    for C in zero_cycles:
        completions += [X ^ C for X in completions]
    candidates = []
    for X in completions:
        active = [C for C in circuit_components(base ^ X, obj.n, obj.edges) if set(C) & set(original)]
        if len(active) == 1 and mask(active[0]) & mask(row['plane_edges']) == change:
            candidates.append(active[0])
    assert candidates
    return min(candidates, key=lambda C: (len(C), C))


def shortest_preparation(obj, original, required):
    u, v = obj.edges[required]
    parent, queue = {u: None}, deque([u])
    while v not in parent:
        assert queue
        w = queue.popleft()
        for e in obj.incident[w]:
            if e in original or e == required:
                continue
            x = obj.edges[e][0] ^ obj.edges[e][1] ^ w
            if x not in parent:
                parent[x] = (w, e)
                queue.append(x)
    edges = [required]
    while v != u:
        v, e = parent[v]
        edges.append(e)
    return sorted(edges)


def main():
    for name, sha in SOURCES:
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == sha
    source, catalog, previous = [json.loads((HERE / name).read_text()) for name, _ in SOURCES]
    obj, a = Graph(source['graph']), 4
    flow = source['initial_flow']
    assert obj.valid_flow(flow)
    original = [e for e, x in enumerate(flow) if x == a]
    assert original == [178, 183, 189]
    cycles = source_cycles(obj, original)
    assert len(cycles) == len(rank_basis(cycles)) == 67
    build_pair = intersection_builder(source, catalog, obj)
    rows, pairs = [], {}
    for b in (1, 2, 3):
        row = full_plane(obj, flow, a, b)
        records, excluded = [], []
        for size in range(len(original)+1):
            for indices in combinations(range(len(row['plane_edges'])), size):
                boundary = 0
                for j in indices:
                    boundary ^= row['edge_columns'][j]
                if boundary != row['terminal_mask']:
                    continue
                K = [row['plane_edges'][j] for j in indices]
                remaining = [uv for e, uv in zip(row['plane_edges'], row['quotient_endpoints'])
                             if e not in original and e not in K]
                ok, components = join_components(len(row['zero_components']), remaining, row['terminal_mask'])
                if not ok:
                    excluded.append(K)
                    continue
                assert size == 3
                r = len(remaining)-len(row['zero_components'])+components
                record = {'matching': K, 'remaining_cycle_dimension': r,
                          'eligible_lift_dimension_per_increment': r+row['zero_cycle_dimension']}
                if K != original:
                    pairs[tuple(K)] = build_pair(K)
                    record['exchange_circuit'] = exchange_circuit(obj, row, original, K)
                else:
                    record['exchange_circuit'] = []
                records.append(record)
        row.update(replacements=records, excluded_parity_joins=excluded)
        rows.append(row)
    assert len(pairs) == 37 and all(not r['excluded_parity_joins'] for r in rows)

    observed = sorted({e for K in pairs for e in K if e not in original})
    compress = lambda C: sum(((C >> e) & 1) << j for j, e in enumerate(observed))
    reduced = rank_basis(compress(C) for C in cycles)
    patterns = [0]
    for X in reduced:
        patterns += [p ^ X for p in patterns]
    assert len(reduced) == 10 and len(patterns) == len(set(patterns)) == 1024
    profiles, pattern_table, coverage = Counter(), [], Counter()
    for p in sorted(patterns):
        values = {e: flow[e] ^ (a if p >> j & 1 else 0) for j, e in enumerate(observed)}
        counts, union = [], set()
        for row in rows:
            eligible, increments = [], set()
            for record in row['replacements']:
                K = record['matching']
                if K == original:
                    continue
                new_values = {values[e] for e in K if e not in original}
                if len(new_values) == 1:
                    eligible.append(K)
                    union.add(tuple(K))
                    increments.add(a ^ next(iter(new_values)))
            counts.append(len(eligible))
            coverage.update(increments)
        assert len(union) == sum(counts)
        profiles[tuple(counts)] += 1
        pattern_table.append([p] + counts)
    profile_data = {'observed_edges': observed, 'restriction_rank': len(reduced),
                    'pattern_count': len(patterns), 'lifts_per_pattern': 1 << (len(cycles)-len(reduced)),
                    'pattern_table_sha256': digest(pattern_table),
                    'distribution': [{'plane_counts': list(counts), 'replacement_count': sum(counts),
                                      'patterns': number} for counts, number in sorted(profiles.items())],
                    'increment_coverage_patterns': [[b, coverage[b]] for b in (1, 2, 3, 5, 6, 7)]}

    first = previous['shortest_neutral_escape']
    C = mask(first['edges'])
    old, new = 189, 148
    target = first['matching_after']
    image = [X ^ (C if X >> new & 1 else 0) for X in cycles]
    assert all(obj.even(Y) and not Y & mask(target) for Y in image)
    assert all(Y ^ (C if Y >> old & 1 else 0) == X for X, Y in zip(cycles, image))
    assert len(rank_basis(image)) == len(source_cycles(obj, target)) == 67
    transport = {'circuit': first['edges'], 'removed_edge': old, 'added_edge': new,
                 'increments': [1, 5], 'canonical_increment': first['increment'],
                 'target_matching': target, 'image_rank': len(rank_basis(image)),
                 'target_fiber_dimension': 67,
                 'canonical_target_flow': previous['repair']['moves'][0]['flow_after'],
                 'canonical_successful_flow': previous['repair']['moves'][-1]['flow_after'],
                 'cover_repair_switch_bound': 1 + obj.n // 5}

    preparation_edges = shortest_preparation(obj, original, 190)
    preparation = obj.switch(flow, a, preparation_edges)
    exchange_edges = next(r['exchange_circuit'] for r in rows[2]['replacements'] if r['matching'] != original)
    exchange = obj.switch(preparation['flow_after'], 7, exchange_edges)
    assert len(preparation_edges) == 14 and len(exchange_edges) == 6
    assert [e for e, x in enumerate(exchange['flow_after']) if x == a] == [178, 183, 190]
    demonstration = {'previously_rigid_increment': 7, 'required_preparation_edge': 190,
                     'shortest_single_preparation_length': 14,
                     'preparation': preparation, 'exchange': exchange,
                     'target_matching': [178, 183, 190]}
    result = {'date': '2026-10-06',
              'scope': 'Complete minimum-matching exchanges from all lifts of the saved projection modulo color 4 on the 138-vertex graph.',
              'sources': [{'file': name, 'sha256': sha} for name, sha in SOURCES],
              'target_color': a, 'minimum_size': 3, 'original_matching': original,
              'source_fiber_dimension': len(cycles), 'source_flow_count': 1 << len(cycles),
              'planes': rows,
              'suitable_replacements': [{'matching': list(K), 'first': F, 'partner': t}
                                        for K, (F, t) in sorted(pairs.items())],
              'lift_profiles': profile_data, 'universal_transport': transport,
              'prepared_increment_demo': demonstration}
    path = HERE / 'prepared_minimum_exchange.json'
    path.write_text(json.dumps(result, indent=2)+'\n')
    print('Source lifts: 2^67. Potential suitable replacements:', len(pairs))
    for row in rows:
        print('Plane', row['increments'], 'quotient vertices/edges:',
              len(row['zero_components']), len(row['plane_edges']),
              'minimum matchings:', len(row['replacements']),
              'free dimension:', row['zero_cycle_dimension'])
    print('Profiles:', profile_data['distribution'])
    print('Fixed-increment coverage:', profile_data['increment_coverage_patterns'])
    print('Universal transport rank:', transport['image_rank'], 'preparation lengths:', len(preparation_edges), len(exchange_edges))
    print('Bytes:', path.stat().st_size, 'SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
