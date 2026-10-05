#!/usr/bin/env python3
"""All placements of a six-port cubic star beside an eleven-cycle.

Enumerate leaf matchings up to dihedral symmetry, fix a central auxiliary
triangle, and compute exact cherry-only and whole-star circuit distances.
The independent verifier uses cycle spaces and local junction relations.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUX = (6, 10, 12, 18, 20, 24)
ROOTS = (6, 10, 12)
EDGES = [(0, k+1) for k in range(3) for _ in range(2)] + [(k+1, 4) for k in range(3)]
PATHS = [(i, j) if i//2 == j//2 else (i, 6+i//2, 6+j//2, j)
         for i in range(6) for j in range(i+1, 6)]


def xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def matchings(ports):
    if not ports:
        yield ()
    else:
        for j in range(1, len(ports)):
            for rest in matchings(ports[1:j]+ports[j+1:]):
                yield ((ports[0], ports[j]),)+rest


def canonical(pairs):
    return min(tuple(sorted(tuple(sorted(((sign*a+k) % 11, (sign*b+k) % 11)))
                            for a, b in pairs)) for sign in (1, -1) for k in range(11))


def placements():
    return Counter(canonical(pairs) for ports in itertools.combinations(range(11), 6)
                   for pairs in matchings(ports))


def leaf_domain(root):
    a, b = [1 << i for i in range(1, 5) if root >> i & 1]
    other = [1 << i for i in range(1, 5) if not root >> i & 1]
    return [(a | c, b | c) if orientation == 0 else (b | c, a | c)
            for c in other for orientation in (0, 1)]


def covers():
    triangles = sorted((a, b, a ^ b) for a in AUX for b in AUX if a ^ b in AUX)
    return sorted(tuple(sum(leaves, ()))+triangle for triangle in triangles
                  for leaves in itertools.product(*(leaf_domain(r) for r in triangle)))


def exchange_graph(states):
    index = {s: i for i, s in enumerate(states)}
    graph = []
    for values in states:
        row = []
        for swap in AUX:
            for path in PATHS:
                if all((values[e] & swap).bit_count() == 1 for e in path):
                    changed = tuple(r ^ swap if e in path else r for e, r in enumerate(values))
                    row.append((index[changed], swap, tuple(sorted(path))))
        graph.append(sorted(row))
    return graph


def good(word):
    prefix = seen = 0
    for r in word:
        seen |= 1 << prefix
        prefix ^= r
    assert prefix == 0
    return seen.bit_count() < 8


def boundary(pairs, rest_ports, rest, values):
    result = [0]*11
    for p, r in zip(rest_ports, rest):
        result[p] = r
    for k, (i, j) in enumerate(pairs):
        result[i], result[j] = values[2*k:2*k+2]
    return result


def cube_distances(good_bits):
    distances = [-1]*64
    queue = deque(good_bits)
    for b in good_bits:
        distances[b] = 0
    while queue:
        b = queue.popleft()
        for bit in range(6):
            c = b ^ (1 << bit)
            if distances[c] < 0:
                distances[c] = distances[b]+1
                queue.append(c)
    return distances


def shortest_path(start, graph, accept):
    queue, parent = deque([start]), {start: None}
    while queue:
        at = queue.popleft()
        if accept(at):
            path = []
            while parent[at] is not None:
                prev, swap, edges = parent[at]
                path.append({'swap_pair': swap, 'edges': list(edges), 'state_after': at})
                at = prev
            return path[::-1]
        for nxt, swap, edges in graph[at]:
            if nxt not in parent:
                parent[nxt] = (at, swap, edges)
                queue.append(nxt)
    raise AssertionError('No good cover in the star exchange component')


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def realized_trap(witness, rows, states):
    """Realize the saved trapped cube with a five-cycle outside component."""
    row = rows[witness['placement_id']]
    assert row['pairs'] == ((0, 1), (2, 3), (6, 7))
    assert witness['rest'] == [6, 24, 6, 12, 20]
    order, walk = [0, 3, 1, 4, 2], [1, 2, 3, 4, 2, 1]
    edges = EDGES+[(0, 5+i) for i in range(5)]
    edges += [(5+order[i], 5+order[(i+1) % 5]) for i in range(5)]
    values = list(states[witness['initial_state']])+witness['rest']+[1 | (1 << label) for label in walk[1:]]
    ports = [None]*11
    for k, pair in enumerate(row['pairs']):
        for i, p in enumerate(pair):
            ports[p] = 2*k+i
    for i, p in enumerate(row['rest_ports']):
        ports[p] = 9+i
    outside = [(ports.index(e) if u == 0 else u+10, ports.index(e) if v == 0 else v+10)
               for e, (u, v) in enumerate(edges)]
    base = [(i, (i+1) % 11) for i in range(11)]+outside
    steps = []
    for move in witness['moves']:
        values_after = [r ^ move['swap_pair'] if e in move['edges'] else r for e, r in enumerate(values)]
        boundary_after = [values_after[e] for e in ports]
        prefix, forbidden = 0, set()
        for r in boundary_after:
            forbidden.add(30 ^ prefix)
            prefix ^= r
        charges = [h for h in range(0, 32, 2) if h.bit_count() % 2 == 0 and h not in forbidden]
        steps.append({**move, 'cover_after': values_after, 'boundary_after': boundary_after, 'surviving_charges': charges})
        values = values_after
    return {'vertices': 10, 'edges': edges, 'port_edge_ids': ports, 'fixed_layer_edges': list(range(14, 19)),
            'initial_cover': list(states[witness['initial_state']])+witness['rest']+[1 | (1 << label) for label in walk[1:]],
            'moves': steps, 'base_vertices': 20, 'base_edges': base, 'selected_cycle': list(range(11)),
            'outside_one_move': {'swap_pair': 10, 'edges': [10, 12, 15]},
            'scope': 'Cherry-only trapping and exact distance two for circuits confined to the four-vertex star. An outside triangle repairs in one move.'}


def main():
    states = covers()
    assert len(states) == len(set(states)) == 1536
    index = {s: i for i, s in enumerate(states)}
    graph = exchange_graph(states)
    domains = [leaf_domain(r) for r in ROOTS]
    cube = [index[sum((domains[k][b >> (2*k) & 3] for k in range(3)), ())+ROOTS] for b in range(64)]
    rest_words = [w+(xor(w),) for w in itertools.product(AUX, repeat=4) if xor(w) in AUX]
    assert len(rest_words) == 960
    orbit_sizes = placements()
    total, weighted = [Counter(), Counter()], [Counter(), Counter()]
    rows, witnesses = [], {}
    for placement_id, (pairs, multiplicity) in enumerate(sorted(orbit_sizes.items())):
        rest_ports = sorted(set(range(11))-set(sum(pairs, ())))
        hist, maxima = [Counter(), Counter()], [Counter(), Counter()]
        records, trapped = bytearray(), []
        for rest in rest_words:
            cache = {}

            def accept(at):
                if at not in cache:
                    cache[at] = good(boundary(pairs, rest_ports, rest, states[at]))
                return cache[at]

            ds = cube_distances([b for b, at in enumerate(cube) if accept(at)])
            if ds[0] == -1:
                assert ds == [-1]*64
                trapped.append(list(rest))
            full = ds.copy()
            for b, distance in enumerate(ds):
                path = None
                if distance == -1 or distance >= 2:
                    path = shortest_path(cube[b], graph, accept)
                    full[b] = len(path)
                for kind, d in (('cherry', distance), ('star', full[b])):
                    key = kind+':'+str(d)
                    if (d == -1 or d >= 2) and key not in witnesses:
                        if kind == 'cherry' and d == -1:
                            moves = []
                        elif kind == 'cherry':
                            at, moves = b, []
                            while ds[at]:
                                bit = next(i for i in range(6) if ds[at ^ (1 << i)] == ds[at]-1)
                                root = ROOTS[bit//2]
                                at ^= 1 << bit
                                moves.append({'swap_pair': root if bit % 2 == 0 else 30 ^ root,
                                              'edges': [2*(bit//2), 2*(bit//2)+1], 'state_after': cube[at]})
                        else:
                            moves = path
                        witnesses[key] = {'placement_id': placement_id, 'rest': list(rest), 'bits': b,
                                          'initial_state': cube[b], 'boundary': boundary(pairs, rest_ports, rest, states[cube[b]]),
                                          'cherry_distance': distance, 'star_distance': full[b], 'moves': moves}
            for i, distances in enumerate((ds, full)):
                hist[i].update(distances)
                maxima[i][max(distances)] += 1
                records.extend(d if d >= 0 else 255 for d in distances)
        rows.append({'pairs': pairs, 'orbit_size': multiplicity, 'rest_ports': rest_ports,
                     'distance_histograms': {'cherry': sorted(hist[0].items()), 'star': sorted(hist[1].items())},
                     'maximum_by_rest_histograms': {'cherry': sorted(maxima[0].items()), 'star': sorted(maxima[1].items())},
                     'distance_records_sha256': hashlib.sha256(records).hexdigest(),
                     'closed_bad_rest_words': trapped})
        for i in range(2):
            total[i].update(hist[i])
            weighted[i].update({d: n*multiplicity for d, n in hist[i].items()})
        if placement_id % 50 == 0:
            print('Placement', placement_id, '/', len(orbit_sizes), 'distances', rows[-1]['distance_histograms'], flush=True)
    result = {'date': '2026-10-05',
              'scope': 'All cyclic placements of a six-port cubic star at a distinguished-layer-free eleven-region; circuit moves remain inside that star.',
              'sources': [{'file': 'auxiliary_exchange_orbit.json',
                           'sha256': hashlib.sha256((HERE/'auxiliary_exchange_orbit.json').read_bytes()).hexdigest()}],
              'auxiliary_pairs': AUX, 'central_pairs': ROOTS, 'star_edges': EDGES,
              'star_cover_count': len(states), 'star_covers_sha256': digest(states),
              'star_circuit_graph_sha256': digest(graph), 'cube_state_ids': cube,
              'closed_rest_words': len(rest_words), 'placement_count': sum(orbit_sizes.values()),
              'placement_classes': len(rows), 'orbit_size_histogram': sorted(Counter(orbit_sizes.values()).items()),
              'representative_distance_histograms': {name: sorted(total[i].items()) for i, name in enumerate(('cherry', 'star'))},
              'labelled_placement_distance_histograms': {name: sorted(weighted[i].items()) for i, name in enumerate(('cherry', 'star'))},
              'class_maximum_histograms': {name: sorted(Counter(-1 if r['distance_histograms'][name][0][0] == -1
                                                               else max(d for d, n in r['distance_histograms'][name]) for r in rows).items())
                                           for name in ('cherry', 'star')},
              'witnesses': witnesses, 'placements': rows,
              'realized_trap': realized_trap(witnesses['star:2'], rows, states)}
    (HERE/'cherry_port_placements.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Representative totals:', result['representative_distance_histograms'], flush=True)
    print('Placement-class maxima:', result['class_maximum_histograms'], flush=True)


if __name__ == '__main__':
    main()
