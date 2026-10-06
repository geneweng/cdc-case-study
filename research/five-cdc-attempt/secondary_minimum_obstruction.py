#!/usr/bin/env python3
"""Certify failure of the odd-component secondary objective at cyclic connectivity five.

Fixed discovery witnesses are checked and completed using the standard library.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path

from minimum_color_obstruction import Graph
from cyclic_five_minimum_obstruction import local_poles, local_audit, connectivity, girth_certificate
from flow_space_components import circuit_components
from fiber_cut_obstructions import eliminate

HERE = Path(__file__).resolve().parent
QUOTIENT = [[0, 9], [0, 14], [0, 11], [0, 15], [0, 5], [1, 17], [1, 10], [1, 16], [1, 8], [1, 15], [2, 16], [2, 11], [2, 4], [2, 3], [2, 9], [13, 8], [12, 17], [4, 3], [3, 10], [4, 6], [11, 9], [5, 8], [7, 14], [13, 12], [7, 10], [14, 6], [13, 7], [15, 5], [6, 12], [17, 16]]
INITIAL = [3, 2, 5, 1, 3, 3, 6, 2, 5, 3, 2, 3, 2, 1, 1, 2, 2, 1, 3, 6, 1, 2, 3, 2, 3, 1, 1, 3, 2, 2, 3, 1, 2, 2, 3, 3, 1, 1, 2, 3, 1, 2, 3, 1, 2, 3, 2, 1, 1, 6, 3, 7, 2, 5, 7, 3, 2, 3, 1, 1, 2, 6, 3, 1, 1, 7, 3, 1, 6, 3, 1, 2, 2, 5, 2, 3, 3, 1, 7, 2, 2, 1, 3, 1, 2, 3, 1, 2, 3, 1, 3, 2, 2, 1, 1, 3, 3, 2, 1, 3, 2, 1, 3, 2, 1, 6, 1, 7, 2, 5, 3, 2, 1, 3, 7, 2, 1, 3, 2, 1, 3, 3, 1, 2, 2, 1, 3, 2, 2, 1, 1, 3, 3, 2, 1, 3, 2, 1, 3, 2, 1, 6, 2, 1, 1, 3, 3, 2, 5, 2, 5, 7, 1, 3, 6, 2, 3, 7, 2, 1, 7, 6, 2, 1, 2, 3, 3, 1, 2, 2, 1, 3, 2, 1, 1, 1, 3, 1, 4, 1, 1, 5, 3, 4, 2, 2, 7, 3, 3, 4, 7, 3, 1, 2, 6, 1, 2, 2, 3, 7, 3, 5, 3, 2, 6, 1, 1]
NEUTRAL_CIRCUIT = [0, 1, 5, 7, 9, 12, 16, 18, 19, 50, 52, 54, 60, 62, 80, 85, 87, 90, 91, 92, 95, 96, 97, 99, 100, 102, 103, 108, 110, 115, 117, 178, 181, 182, 186, 193, 199, 200, 203, 204]
INTERSECTION = [681915355426539777851842128950214260766139806013238397632512, 184108488516759424751147684002861686770996047105571519872305812]


def graph(poles):
    Y = poles['Y']
    edges = [(u + 41*i, v + 41*i) for i in range(3) for u, v in Y['edges']]
    used = [0, 0, 0]
    for u, v in QUOTIENT:
        if u < 3:
            edges.append((41*u + Y['ports'][used[u]], v + 120))
            used[u] += 1
        else:
            edges.append((u + 120, v + 120))
    assert used == [5, 5, 5]
    regions = []
    for i in range(3):
        vertices = list(range(41*i, 41*(i+1)))
        charged = [e for e, uv in enumerate(edges) if set(vertices).intersection(uv)]
        regions.append({'vertices': vertices, 'ports': [41*i+p for p in Y['ports']],
                        'charged_edges': charged})
    return {'name': 'ThreeY1Hexagon138', 'vertices': 138, 'edges': edges,
            'regions': regions, 'quotient_edges': QUOTIENT}


def unmatched(obj, M):
    D = sum(1 << v for v in {v for e, uv in enumerate(obj.edges) if M >> e & 1 for v in uv})
    B = ((1 << obj.n)-1) ^ D
    induced = sum((bool(B >> u & 1 and B >> v & 1)) << e for e, (u, v) in enumerate(obj.edges))
    parts = sorted(K for K in obj.components(induced) if K & B)
    return D, B, induced, parts


def obstruction(obj):
    M = sum((x == 4) << e for e, x in enumerate(INITIAL))
    D, B, induced, parts = unmatched(obj, M)
    assert M.bit_count() == 3 and D.bit_count() == 6 and parts == [B] and B.bit_count() == 132
    forced = sum((not (M >> e & 1) and bool(D >> u & 1 or D >> v & 1)) << e
                 for e, (u, v) in enumerate(obj.edges))
    cycle_vertices = [124, 123, 130, 127, 134, 126]
    index = {tuple(sorted(uv)): e for e, uv in enumerate(obj.edges)}
    cycle_edges = [index[tuple(sorted((u, v)))]
                   for u, v in zip(cycle_vertices, cycle_vertices[1:] + cycle_vertices[:1])]
    C = sum(1 << e for e in cycle_edges)
    assert C & forced == C and obj.even(C)
    assert sum(bool(D >> v & 1) for v in cycle_vertices) == 3
    assert all(bool(D >> v & 1) == (i % 2 == 0) for i, v in enumerate(cycle_vertices))
    equations = [(sum(1 << e for e in row), 0) for row in obj.incident]
    equations += [(1 << e, 0) for e in range(obj.m) if M >> e & 1]
    equations += [(1 << e, 1) for e in range(obj.m) if forced >> e & 1]
    solution = eliminate(equations, obj.m)
    L = solution['solution']
    circuits = circuit_components(L, obj.n, obj.edges)
    dimension = induced.bit_count() - B.bit_count() + len(parts)
    assert obj.m - solution['rank'] == dimension == 61
    cuts = []
    for vertices in ([123, 124, 130], [124, 126, 134], [127, 130, 134]):
        X = sum(1 << v for v in vertices)
        boundary = obj.cut(X) & ~M
        assert boundary.bit_count() == 3 and (X & D).bit_count() == 2
        cuts.append({'vertices': vertices, 'terminal_vertices': [v for v in vertices if D >> v & 1],
                     'boundary_in_H': [e for e in range(obj.m) if boundary >> e & 1]})
    terminals = [v for v in range(obj.n) if D >> v & 1]
    for rest in combinations(terminals[1:], 2):
        S = sum(1 << v for v in (terminals[0],) + rest)
        assert any(2 * abs((S & sum(1 << v for v in cut['vertices'])).bit_count()
                          - ((D ^ S) & sum(1 << v for v in cut['vertices'])).bit_count())
                   > len(cut['boundary_in_H']) for cut in cuts)
    return {'matching': M, 'matching_edges': [e for e in range(obj.m) if M >> e & 1],
            'endpoints': terminals, 'unmatched_vertices': B, 'unmatched_components': parts,
            'unmatched_internal_edges': induced.bit_count(), 'odd_component_count': 0,
            'forced_edges': forced, 'forced_circuit_vertices': cycle_vertices,
            'forced_circuit_edges': cycle_edges, 'forced_circuit_terminal_count': 3,
            'candidate': L, 'candidate_dimension': dimension,
            'candidate_circuits': circuits,
            'candidate_terminal_counts': [len({v for e in row for v in obj.edges[e] if D >> v & 1}) for row in circuits],
            'terminal_cut_obstruction': cuts, 'balanced_signings_excluded': 10}


def repair(obj):
    first = obj.switch(INITIAL, 1, NEUTRAL_CIRCUIT)
    after = first['flow_after']
    F, t = INTERSECTION
    M = sum((x == 4) << e for e, x in enumerate(after))
    assert obj.even(F) and obj.even(t) and F & t == M and M.bit_count() == 3
    moves = [first]
    for circuit in circuit_components(F ^ obj.support(after, 4), obj.n, obj.edges):
        move = obj.switch(after, 4, circuit)
        moves.append(move)
        after = move['flow_after']
    assert obj.support(after, 4) == F
    y, z = obj.support(after, 1), obj.support(after, 2)
    fourth = t ^ y ^ z
    forms = [2, 1, 4]
    transformed = [sum(((x & ell).bit_count() % 2) << i for i, ell in enumerate(forms)) for x in after]
    palette = (4, 5, 6, 15, 8)
    decode = {x ^ y: (1 << i) | (1 << j) for i, x in enumerate(palette)
              for j, y in enumerate(palette) if i < j}
    cover = [decode[x + 8*((fourth >> e) & 1)] for e, x in enumerate(transformed)]
    assert obj.even(fourth) and all(cover[a] ^ cover[b] ^ cover[c] == 0 for a, b, c in obj.incident)
    for move in moves:
        assert min(move['color_sizes']) == move['color_sizes'][3] == 3
        matching = sum((x == 4) << e for e, x in enumerate(move['flow_after']))
        assert all(K.bit_count() % 2 == 0 for K in unmatched(obj, matching)[3])
    return {'moves': moves, 'intersection_first': F, 'intersection_partner': t,
            'first_functional': 4, 'target_color': 4,
            'final_lift': {'coordinate_functionals': forms, 'transformed_flow': transformed,
                           'fourth_coordinate': fourth, 'cover_pairs': cover}}


def main():
    sources = []
    for name, expected in [
        ('cyclic_five_minimum_obstruction.json', 'e8ee46bb12c877499e3b631a3cac412f679b562cce48a9f4484a7e23197e2dd0'),
        ('minimum_matching_secondary.json', '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec')]:
        value = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        assert value == expected
        sources.append({'file': name, 'sha256': value})
    poles = local_poles()
    g = graph(poles)
    obj = Graph(g)
    assert obj.valid_flow(INITIAL)
    charged = [set(r['charged_edges']) for r in g['regions']]
    assert all(len(row) == 64 for row in charged)
    assert all(a.isdisjoint(b) for a, b in combinations(charged, 2))
    result = {'date': '2026-10-06',
              'scope': 'A globally minimizing pair (class size, odd unmatched component count) can be unsuitable, even at cyclic edge connectivity five.',
              'sources': sources, 'local_poles': poles, 'local_audits': local_audit(poles),
              'graph': g, 'connectivity': connectivity(obj), 'girth_certificate': girth_certificate(obj),
              'initial_flow': INITIAL, 'initial_color_sizes': [INITIAL.count(a) for a in range(1, 8)],
              'minimum_color_multiplicity': 3, 'secondary_minimum': [3, 0],
              'obstruction': obstruction(obj), 'repair': repair(obj)}
    path = HERE / 'secondary_minimum_obstruction.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print('Graph:', obj.n, obj.m, 'girth', result['girth_certificate']['girth'], 'cyclic connectivity 5')
    print('Global secondary minimum:', result['secondary_minimum'], 'sizes:', result['initial_color_sizes'])
    print('Unmatched component orders:', [K.bit_count() for K in result['obstruction']['unmatched_components']])
    print('Forced hexagon:', result['obstruction']['forced_circuit_vertices'], 'with 3 terminals')
    print('Candidate dimension:', result['obstruction']['candidate_dimension'])
    print('Candidate circuit lengths:', list(map(len, result['obstruction']['candidate_circuits'])),
          'terminal counts:', result['obstruction']['candidate_terminal_counts'])
    print('Repair lengths:', [len(move['edges']) for move in result['repair']['moves']])
    print('Bytes:', path.stat().st_size, 'SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
