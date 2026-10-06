#!/usr/bin/env python3
"""Exact minimum-class replacements in coordinate fibers, without SAT."""
from collections import deque
from itertools import combinations
import hashlib
import json
from pathlib import Path

from minimum_color_obstruction import Graph
from minimum_matching_secondary import Constraints
from fiber_cut_obstructions import eliminate
from flow_space_components import circuit_components

HERE = Path(__file__).resolve().parent
SOURCES = [
    ('secondary_minimum_obstruction.json', 'f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5'),
    ('minimum_matching_secondary.json', '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec')]


def mask(edges):
    return sum(1 << e for e in edges)


def quotient(obj, flow, a, b):
    cost = [e for e, x in enumerate(flow) if x in (a, a ^ b)]
    zero = mask(e for e, x in enumerate(flow) if x not in (a, b, a ^ b))
    parts = sorted(obj.components(zero), key=lambda K: (K & -K).bit_length())
    component = {v: i for i, K in enumerate(parts) for v in range(obj.n) if K >> v & 1}
    columns = [(1 << component[obj.edges[e][0]]) ^ (1 << component[obj.edges[e][1]]) for e in cost]
    terminal = 0
    for e, column in zip(cost, columns):
        if flow[e] == a:
            terminal ^= column
    H = mask(e for e, x in enumerate(flow) if x != b)
    return {'increment': b, 'cost_edges': cost, 'zero_edges': zero,
            'zero_components': parts, 'edge_columns': columns, 'terminal_mask': terminal,
            'free_dimension': zero.bit_count()-obj.n+len(parts),
            'fiber_dimension': H.bit_count()-obj.n+len(obj.components(H))}


def replacements(row, k):
    result = []
    for size in range(k+1):
        for positions in combinations(range(len(row['cost_edges'])), size):
            parity = 0
            for j in positions:
                parity ^= row['edge_columns'][j]
            if parity == row['terminal_mask']:
                assert size == k
                result.append([row['cost_edges'][j] for j in positions])
    return result


def realize(obj, flow, a, row, target):
    original = {e for e, x in enumerate(flow) if x == a}
    change = original ^ set(target)
    equations = [(mask(es), 0) for es in obj.incident]
    equations += [(1 << e, 0) for e, x in enumerate(flow) if x == row['increment']]
    equations += [(1 << e, int(e in change)) for e in row['cost_edges']]
    C = eliminate(equations, obj.m)['solution']
    circuits = [cs for cs in circuit_components(C, obj.n, obj.edges) if original.intersection(cs)]
    current = flow
    for cs in circuits:
        move = obj.switch(current, row['increment'], cs)
        current = move['flow_after']
        assert current.count(a) == len(original)
    assert [e for e, x in enumerate(current) if x == a] == target
    return circuits


def intersection_builder(source, catalog, obj):
    groups = catalog['local_edge_groups']
    lookup = {(e, word): (F, t) for e, word, F, t in catalog['local_witnesses']}
    maps = [list(range(59*i, 59*(i+1))) + list(range(177+5*i, 182+5*i)) for i in range(3)]
    solver = Constraints(18, source['graph']['quotient_edges'])
    def build(target):
        selected = [next(e for e, g in enumerate(row) if g in target) for row in maps]
        kinds = [next(t for t, group in enumerate(groups) if e in group) for e in selected]
        domains = [7] * 30
        for i, t in enumerate(kinds):
            if 1 <= t <= 5:
                domains[5*i+t-1] = 6
            elif t >= 6:
                domains[5*i+t-6] = 8
        values = solver.solve(domains)
        assert values is not None
        full = [None] * 177 + values
        for i, e in enumerate(selected):
            word = sum(x << (2*j) for j, x in enumerate(values[5*i:5*i+5]))
            F, t = lookup[e, word]
            for le, ge in enumerate(maps[i]):
                value = ((F >> le) & 1) + 2*((t >> le) & 1)
                assert full[ge] is None or full[ge] == value
                full[ge] = value
        F = sum((x & 1) << e for e, x in enumerate(full))
        t = sum(((x >> 1) & 1) << e for e, x in enumerate(full))
        assert obj.even(F) and obj.even(t) and F & t == mask(target)
        return [F, t]
    return build


def cycle_lower_bounds(obj, matching):
    result = []
    for excluded in matching:
        u, v = obj.edges[excluded]
        distances = {u: 0}
        todo = deque([u])
        while todo:
            w = todo.popleft()
            for e in obj.incident[w]:
                if e == excluded:
                    continue
                x = obj.edges[e][0] ^ obj.edges[e][1] ^ w
                if x not in distances:
                    distances[x] = distances[w]+1
                    todo.append(x)
        result.append([excluded, distances[v]+1])
    return result


def cover(obj, flow, first, pair):
    moves = [obj.switch(flow, first['increment'], first['edges'])]
    after = moves[0]['flow_after']
    F, t = pair
    for C in circuit_components(F ^ obj.support(after, 4), obj.n, obj.edges):
        moves.append(obj.switch(after, 4, C))
        after = moves[-1]['flow_after']
    assert obj.support(after, 4) == F
    w = t ^ obj.support(after, 1) ^ obj.support(after, 2)
    forms = [2, 1, 4]
    transformed = [sum(((x & ell).bit_count() % 2) << i for i, ell in enumerate(forms)) for x in after]
    palette = [4, 5, 6, 15, 8]
    decode = {x ^ y: (1 << i) | (1 << j) for i, x in enumerate(palette)
              for j, y in enumerate(palette) if i < j}
    layers = [decode[x + 8*((w >> e) & 1)] for e, x in enumerate(transformed)]
    assert obj.even(w) and all(layers[u] ^ layers[v] ^ layers[z] == 0 for u, v, z in obj.incident)
    return {'moves': moves, 'intersection_first': F, 'intersection_partner': t,
            'coordinate_functionals': forms, 'transformed_flow': transformed,
            'fourth_coordinate': w, 'cover_pairs': layers}


def main():
    for name, expected in SOURCES:
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected
    source = json.loads((HERE / SOURCES[0][0]).read_text())
    catalog = json.loads((HERE / SOURCES[1][0]).read_text())
    obj = Graph(source['graph'])
    flow, a = source['initial_flow'], 4
    original = [e for e, x in enumerate(flow) if x == a]
    assert len(original) == source['minimum_color_multiplicity'] == 3
    builder = intersection_builder(source, catalog, obj)
    rows, positive, candidates = [], {}, []
    for b in [1, 2, 3, 5, 6, 7]:
        row = quotient(obj, flow, a, b)
        records = []
        for target in replacements(row, 3):
            circuits = realize(obj, flow, a, row, target)
            if target != original:
                key = tuple(target)
                if key not in positive:
                    positive[key] = builder(target)
                assert len(circuits) == 1
                candidates.append((len(circuits[0]), b, circuits[0], target))
            else:
                assert not circuits
            records.append({'matching': target, 'circuits': circuits})
        row['replacements'] = records
        row['optimal_flow_count'] = len(records) * (1 << row['free_dimension'])
        rows.append(row)
    shortest, b, circuit, target = min(candidates)
    lower = cycle_lower_bounds(obj, original)
    assert shortest == min(length for _, length in lower) == 6
    first = {'increment': b, 'edges': circuit, 'matching_after': target}
    result = {'date': '2026-10-06',
              'scope': 'An exact quotient test for neutral minimum-class exchanges; complete neighboring fibers of the saved 138-vertex flow.',
              'sources': [{'file': name, 'sha256': sha} for name, sha in SOURCES],
              'target_color': a, 'minimum_size': 3, 'original_matching': original,
              'fibers': rows,
              'suitable_replacements': [{'matching': list(K), 'first': F, 'partner': t}
                                        for K, (F, t) in sorted(positive.items())],
              'distinct_replacement_matchings': len(positive)+1,
              'tagged_optimal_flow_count': sum(row['optimal_flow_count'] for row in rows),
              'suitable_target_flow_count': sum((len(row['replacements'])-1)*(1 << row['free_dimension']) for row in rows),
              'matching_edge_cycle_lower_bounds': lower, 'shortest_neutral_escape': first,
              'repair': cover(obj, flow, first, positive[tuple(target)])}
    assert len(positive) == 29
    path = HERE / 'neutral_minimum_quotient.json'
    path.write_text(json.dumps(result, indent=2)+'\n')
    for row in rows:
        print('Increment', row['increment'], 'quotient vertices/edges', len(row['zero_components']), len(row['cost_edges']),
              'dimensions', row['fiber_dimension'], row['free_dimension'],
              'matchings', len(row['replacements']), 'minimum flows', row['optimal_flow_count'])
    print('Distinct matchings:', len(positive)+1, 'suitable:', len(positive))
    print('Shortest neutral escape:', shortest, 'edge lower bounds:', lower)
    print('Cover switch lengths:', [len(move['edges']) for move in result['repair']['moves']])
    print('Bytes:', path.stat().st_size, 'SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
