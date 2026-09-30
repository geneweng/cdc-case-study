#!/usr/bin/env python3
"""One winding switch, bounded-length repair, and simultaneous piece lifting.

Certificate construction uses only the standard library. The embedded positive
cover was discovered with SAT; its verification does not depend on a solver.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
WINDING_VERTICES = [6, 0, 60, 12, 17, 15, 63, 1, 7, 8, 9, 10, 11, 6]
COVER = ('068471434652235910223718036114885022419735891763889441108267391873111287'
         '680186604343100618843652200539932233')
HARD_WORD = '23312221331111'
LOCAL_CIRCUIT = [0, 1, 2, 4, 7]


def word(f):
    return ''.join(map(str, f))


def components(vertices, edges):
    adjacency = [set() for _ in range(vertices)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    unseen = {v for v in range(vertices) if adjacency[v]}
    sizes = []
    while unseen:
        seen, todo = set(), [min(unseen)]
        while todo:
            v = todo.pop()
            if v not in seen:
                seen.add(v)
                todo.extend(adjacency[v]-seen)
        unseen -= seen
        sizes.append(len(seen))
    return sorted(sizes)


def lifted_edges(seed_edges, voltage, m):
    return [(72*s+u, 72*((s+voltage[e]) % m)+v)
            for s in range(m) for e, (u, v) in enumerate(seed_edges)]


def lifted_walk(seed_edges, voltage, m):
    lookup = {frozenset(edge): e for e, edge in enumerate(seed_edges)}
    sheet, result = 0, []
    for _ in range(m):
        for u, v in zip(WINDING_VERTICES, WINDING_VERTICES[1:]):
            e = lookup[frozenset((u, v))]
            if seed_edges[e] == [u, v]:
                result.append(108*sheet+e)
                sheet = (sheet+voltage[e]) % m
            else:
                sheet = (sheet-voltage[e]) % m
                result.append(108*sheet+e)
    assert sheet == 0 and len(set(result)) == 13*m
    return result


def family(seed, m):
    edges0 = seed['examples'][0]['edges']
    voltage = [int(e in (5, 106, 107)) for e in range(108)]
    edges = lifted_edges(edges0, voltage, m)
    initial = seed['examples'][0]['flow']*m
    chosen = lifted_walk(edges0, voltage, m)
    changed = initial.copy()
    for e in chosen:
        assert changed[e] != 1
        changed[e] ^= 1
    local_lift = [108*s+12+e for s in range(m) for e in LOCAL_CIRCUIT]
    obstructions = []
    for rec in seed['examples'][0]['normals']:
        w = rec['obstruction_junctions'][0]
        obstructions.append({'normal': rec['normal'],
                             'piece_pairs': [[(s, w['left_block']),
                                              ((s+1) % m if w['right_block'] == 0 else s,
                                               w['right_block'])] for s in range(m)]})
    # Use the winding circuit's normal 1; its support shrinks from 57m to 54m.
    return {'repetitions': m, 'vertices': 72*m, 'initial_flow_word': word(initial),
            'switch_edges_in_order': chosen, 'increment': 1, 'normal': 1,
            'repaired_flow_word': word(changed), 'cover_word': COVER*m,
            'support_size': sum(a & 1 for a in changed),
            'winding_lift_component_sizes': components(72*m, [edges[e] for e in chosen]),
            'local_pentagon_lift_component_sizes': components(72*m, [edges[e] for e in local_lift]),
            'disjoint_obstructions': obstructions,
            'unrestricted_repair_distance': 1,
            'repair_distance_for_length_limits_5_6_7': m}


def necklace(q):
    edges = [(8*i+x-2, 8*i+y-2) for i in range(q) for x, y in INTERNAL]
    edges += [(8*i+PORTS[j]-2, 8*((i+1) % q)+PORTS[j+2]-2)
              for i in range(q) for j in range(2)]
    local = list(map(int, HARD_WORD))
    initial = local[:10]*q+[1]*(2*q)
    flow, preparations = initial.copy(), []
    for i in range(q):
        circuit = [10*i+e for e in LOCAL_CIRCUIT]
        for e in circuit:
            flow[e] ^= 4
        preparations.append({'piece': i, 'edges': circuit, 'increment': 4})
    # The quotient circuit uses the first of the two parallel ring edges.
    quotient = [[i, (i+1) % q] for i in range(q)]
    global_edges = [10*i+e for i in range(q) for e in (0, 1)]
    global_edges += [10*q+2*i for i in range(q)]
    before = flow.copy()
    for e in global_edges:
        assert flow[e] != 2
        flow[e] ^= 2
    return {'pieces': q, 'vertices': 8*q, 'edges': edges,
            'initial_flow_word': word(initial), 'blocked_local_word': HARD_WORD,
            'blocked_increment': 2, 'selected_ports': [0, 2],
            'separating_vertex_set': [3, 4, 5, 8],
            'separating_local_edges': [0, 4, 5, 6],
            'quotient_circuit': quotient, 'quotient_increment': 2,
            'preparations': preparations, 'prepared_flow_word': word(before),
            'lifted_circuit_edges': global_edges, 'final_flow_word': word(flow),
            'internal_paths': [[10*i+1, 10*i] for i in range(q)],
            'internal_preparation_steps': q, 'total_steps_in_displayed_lift': q+1}


def main():
    source = HERE / 'junction_selection_obstruction.json'
    seed = json.loads(source.read_text())
    seed_edges = seed['examples'][0]['edges']
    voltage = [int(e in (5, 106, 107)) for e in range(108)]
    lookup = {frozenset(uv): e for e, uv in enumerate(seed_edges)}
    circuit = [lookup[frozenset(uv)] for uv in zip(WINDING_VERTICES, WINDING_VERTICES[1:])]
    winding = sum(voltage[e] if seed_edges[e] == [u, v] else -voltage[e]
                  for e, u, v in zip(circuit, WINDING_VERTICES, WINDING_VERTICES[1:]))
    assert winding == 1
    result = {'date': '2026-09-30',
              'scope': 'Exact unrestricted and short-circuit repair distances for the existing family, plus quantitative simultaneous lifting. No general 5-CDC proof or novelty claim.',
              'source_certificate': source.name,
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'seed_edges': seed_edges, 'edge_voltages': voltage,
              'seed_circuit_vertices': WINDING_VERTICES, 'seed_circuit_edges': circuit,
              'seed_winding': winding, 'seed_cover_word': COVER,
              'edge_numbering': 'For m sheets: vertex 72*s+v and edge 108*s+e; seed edge (u,v) goes from (s,u) to (s+voltage[e] mod m,v). This is isomorphic to the earlier family numbering.',
              'periodic_repairs': [family(seed, m) for m in (1, 2, 3, 10, 31)],
              'simultaneous_lifting_examples': [necklace(q) for q in (3, 6, 12)]}
    (HERE / 'global_circuit_repair.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved one winding switch and a five-layer cover for m = 1, 2, 3, 10, 31.')
    print('Circuit lengths are 13m; normal-1 support sizes are 54m.')
    print('Saved simultaneous lifting examples with 3, 6, 12 necessary piece preparations in the stated lifting model.')


if __name__ == '__main__':
    main()
