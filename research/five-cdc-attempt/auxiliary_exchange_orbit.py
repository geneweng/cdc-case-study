#!/usr/bin/env python3
"""Complete fixed-layer cover space and exchange distances for the native trap.

Vertex-triangle enumeration and split-path exchanges; see the independent
cycle-space verifier. No general neutral-escape theorem is asserted.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from actual_core_exchange_obstruction import seed
from eight_cycle_completion import example_seed, marked_test
from core_component_exchange import regions_for
from fourflow_quotient_repair import contracted
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from short_cycle_boundary import local_table

HERE = Path(__file__).resolve().parent
AUX = PAIRS[4:]


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def bad(rs):
    at, seen = 0, 0
    for r in rs:
        seen |= 1 << at
        at ^= r
    assert at == 0
    return seen.bit_count() == 8


def canonical(values):
    return min(word(PAIRS.index((r & 1) | sum(1 << p[i-1] for i in range(1, 5) if r >> i & 1))
                    for r in values) for p in itertools.permutations(range(1, 5)))


def factors_for(g):
    es, n = g['core']['edges'], g['core']['vertices']
    original = [PAIRS[int(c)] for c in g['original_core_cover_word']]
    inc = g['regions'][0]['incidences']
    adjacency = [[] for _ in range(n)]
    for e, uv in enumerate(es):
        for v in uv:
            adjacency[v].append(e)
    remaining, components = set(range(1, n)), []
    while remaining:
        seen, todo = {min(remaining)}, [min(remaining)]
        for v in todo:
            for e in adjacency[v]:
                w = es[e][0] ^ es[e][1] ^ v
                if w and w not in seen:
                    seen.add(w)
                    todo.append(w)
        remaining -= seen
        components.append(sorted(seen))
    triangles = [x for x in itertools.product(PAIRS, repeat=3) if x[0] ^ x[1] ^ x[2] == 0]
    factors = []
    for vertices in components:
        edges = sorted({e for v in vertices for e in adjacency[v]})
        index = {e: j for j, e in enumerate(edges)}
        stars = {v: [index[e] for e in adjacency[v]] for v in vertices}
        options = {v: [row for row in triangles if all((a & 1) == (original[edges[e]] & 1)
                                                      for a, e in zip(row, star))]
                   for v, star in stars.items()}
        values, states = [0]*len(edges), []
        def enumerate_vertices(todo):
            if not todo:
                states.append(tuple(values))
                return
            v = max(todo, key=lambda w: (sum(bool(values[e]) for e in stars[w]), -w))
            for row in options[v]:
                if any(values[e] and values[e] != a for e, a in zip(stars[v], row)):
                    continue
                free = [e for e in stars[v] if not values[e]]
                for e, a in zip(stars[v], row):
                    values[e] = a
                enumerate_vertices(todo-{v})
                for e in free:
                    values[e] = 0
        enumerate_vertices(set(vertices))
        states.sort()
        assert len(states) == len(set(states))
        lookup = {s: i for i, s in enumerate(states)}
        neighbors, singles, histogram = [], [], Counter()
        for values in states:
            rows, single_rows = [], []
            for t in AUX:
                active = {j for j, a in enumerate(values) if (a & t).bit_count() == 1}
                parts = []
                while active:
                    seen, todo = {min(active)}, [min(active)]
                    for j in todo:
                        for v in es[edges[j]]:
                            if not v:
                                continue
                            for k in stars[v]:
                                if k in active and k not in seen:
                                    seen.add(k)
                                    todo.append(k)
                    active -= seen
                    parts.append(sum(1 << j for j in seen))
                masks = [0]
                for m in parts:
                    masks += [s ^ m for s in masks]
                following = lambda m: lookup[tuple(a ^ t if m >> j & 1 else a for j, a in enumerate(values))]
                rows.append(sorted(following(m) for m in masks))
                single_rows.append(sorted(following(m) for m in parts))
                histogram[len(parts)] += 1
            neighbors.append(rows)
            singles.append(single_rows)
        remaining, sizes = set(range(len(states))), []
        while remaining:
            seen, todo = {min(remaining)}, [min(remaining)]
            for i in todo:
                for j in itertools.chain.from_iterable(singles[i]):
                    if j not in seen:
                        seen.add(j)
                        todo.append(j)
            remaining -= seen
            sizes.append(len(seen))
        factors.append({'vertices': vertices, 'edges': edges,
                        'ports': [[i, index[h//2]] for i, h in enumerate(inc) if h//2 in index],
                        'states': states, 'neighbors': neighbors, 'singles': singles,
                        'circuit_components': sorted(sizes), 'generator_histogram': sorted(histogram.items())})
    return factors


def global_cover(factors, state):
    i, j = divmod(state, len(factors[1]['states']))
    result = [0]*sum(len(f['edges']) for f in factors)
    for f, at in zip(factors, (i, j)):
        for e, a in zip(f['edges'], f['states'][at]):
            result[e] = a
    return result


def successors(factors, state, single):
    a, b = factors
    nb = len(b['states'])
    i, j = divmod(state, nb)
    for t in range(6):
        if single:
            for ii in a['singles'][i][t]:
                yield AUX[t], ii*nb+j
            for jj in b['singles'][j][t]:
                yield AUX[t], i*nb+jj
        else:
            for ii in a['neighbors'][i][t]:
                for jj in b['neighbors'][j][t]:
                    yield AUX[t], ii*nb+jj


def census(g):
    factors = factors_for(g)
    a, b = factors
    nb = len(b['states'])
    rejected, rs = set(), [0]*11
    for i, x in enumerate(a['states']):
        for p, j in a['ports']:
            rs[p] = x[j]
        for k, y in enumerate(b['states']):
            for p, j in b['ports']:
                rs[p] = y[j]
            if bad(rs):
                rejected.add(i*nb+k)
    total = len(a['states'])*nb
    histograms, distance = {}, None
    for single in (False, True):
        remaining, distance, depth = rejected.copy(), {}, 0
        hist = [[0, total-len(rejected)]]
        while remaining:
            depth += 1
            following = set()
            for state in remaining:
                if any(j not in remaining for _, j in successors(factors, state, single)):
                    distance[state] = depth
                else:
                    following.add(state)
            assert len(following) < len(remaining), 'A closed bad component was found.'
            hist.append([depth, len(remaining)-len(following)])
            remaining = following
        histograms['single_circuit' if single else 'even_subgraph'] = hist
    hard = sorted(word(PAIRS.index(a) for a in global_cover(factors, s)) for s, d in distance.items() if d == 2)
    classes = Counter(canonical([PAIRS[int(c)] for c in w]) for w in hard)
    representatives = []
    for cw, size in sorted(classes.items()):
        values = [PAIRS[int(c)] for c in cw]
        ids = [f['states'].index(tuple(values[e] for e in f['edges'])) for f in factors]
        at = ids[0]*nb+ids[1]
        moves = []
        for depth in (2, 1):
            candidates = []
            for t, nxt in successors(factors, at, True):
                if distance.get(nxt, 0) != depth-1:
                    continue
                after = global_cover(factors, nxt)
                changed = [e for e, (x, y) in enumerate(zip(values, after)) if x != y]
                candidates.append((len(changed), t, changed, nxt, after))
            _, t, edges, at, after = min(candidates)
            moves.append({'swap_pair': t, 'edges': edges,
                          'cover_word_after': word(PAIRS.index(a) for a in after)})
            values = after
        representatives.append({'cover_word': cw, 'label_orbit_size': size, 'moves': moves})
    summaries = [{k: v for k, v in f.items() if k not in ('states', 'neighbors', 'singles')}
                 | {'cover_words': [word(PAIRS.index(a) for a in s) for s in f['states']],
                    'neighbor_sha256': digest(f['neighbors']), 'single_neighbor_sha256': digest(f['singles'])}
                 for f in factors]
    return {'factors': summaries, 'total_covers': total, 'bad_covers': len(rejected),
            'bad_state_ids_sha256': digest(sorted(rejected)), 'distance_histograms': histograms,
            'distance_two_cover_words': hard, 'hard_representatives': representatives}


def lift_move(core, pairs, old_move, attachment):
    t, old_edges = old_move['swap_pair'], old_move['edges']
    if attachment is None:
        return old_edges
    selected = [e-1 for e in old_edges if e != 0]
    if 0 not in old_edges:
        return sorted(selected)
    inside = {core['vertex_map'][v] for v in attachment['vertices']}
    cut = attachment['core_cut_edges']
    ends = [next(v for v in core['edges'][e] if v in inside) for e in cut]
    parent, todo = {ends[0]: None}, [ends[0]]
    for u in todo:
        for e, (v, w) in enumerate(core['edges']):
            if v not in inside or w not in inside or (pairs[e] & t).bit_count() != 1:
                continue
            if u not in (v, w):
                continue
            other = v ^ w ^ u
            if other not in parent:
                parent[other] = (u, e)
                todo.append(other)
    at = ends[1]
    selected += cut
    while parent[at] is not None:
        at, e = parent[at]
        selected.append(e)
    return sorted(selected)


def full_example(kind, rep_id, representative, pet, table, fibers, domains, witnesses):
    old = seed(kind, table, fibers)
    old['rejected_core_cover_word'] = representative['cover_word']
    g, initial, original = example_seed(old, pet)
    core, pairs, moves = contracted(g), original.copy(), []
    for move in representative['moves']:
        selected = lift_move(core, pairs, move, g.get('petersen_two_sum'))
        pairs = [a ^ move['swap_pair'] if e in selected else a for e, a in enumerate(pairs)]
        moves.append({'swap_pair': move['swap_pair'], 'edges': selected,
                      'cover_word_after': word(PAIRS.index(a) for a in pairs)})
    changed = pairs.copy()
    pairs = dict(enumerate(changed))
    letters = [[changed[j['edges'][-1]], 15] for j in g['junctions']]
    _, allowed = marked_test(letters)
    h, prefix = min(allowed), 0
    for j, (r, z) in zip(g['junctions'], letters):
        for e, a in zip(j['edges'], table[r, z][h ^ prefix]):
            assert e not in pairs or pairs[e] == a
            pairs[e] = a
        prefix ^= r
    cover = ['?']*len(g['edges'])
    for e, a in pairs.items():
        cover[e] = str(PAIRS.index(a))
    flow, switches = initial.copy(), []
    for i, block in enumerate(g['blocks']):
        es = block['edge_representatives']
        repair = joint_repair([flow[e] for e in es], 1, [PAIRS.index(pairs[e]) for e in es[10:]],
                              fibers, domains, witnesses)
        for move in repair['moves']:
            selected = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            switches.append({'piece': i, 'edges': selected, 'increment': move['increment']})
            for e in selected:
                flow[e] ^= move['increment']
        for e, a in zip(es[:10], repair['cover_word'][:10]):
            cover[e] = a
    g.update({'name': 'petersen_attachment' if pet else 'native', 'representative': rep_id,
              'core': core, 'regions': regions_for(g, initial, original),
              'profile_names': ['11'], 'core_cover_moves': moves,
              'original_core_cover_word': word(PAIRS.index(a) for a in original),
              'changed_core_cover_word': word(PAIRS.index(a) for a in changed),
              'regional_extensions': [{'letters': letters, 'surviving_charges': allowed, 'chosen_charge': h}],
              'initial_flow_word': word(initial), 'quotient_cover_word': word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids']),
              'moves': switches, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    return g


# Three leaves adjacent twice to the target and once to a common cubic center.
CHERRIES = [((2, 6), 6), ((1, 7), 10), ((5, 8), 12)]
REST = [0, 3, 4, 9, 10]


def cherry_audit():
    histogram, maxima, records, hardest = Counter(), Counter(), [], []
    for prefix in itertools.product(AUX, repeat=4):
        last = 0
        for r in prefix:
            last ^= r
        if last not in AUX:
            continue
        rest = prefix+(last,)
        words, distances, queue = [], {}, deque()
        for bits in range(64):
            rs = [0]*11
            for p, r in zip(REST, rest):
                rs[p] = r
            for k, ((i, j), root) in enumerate(CHERRIES):
                a, b = [1 << v for v in range(1, 5) if root >> v & 1]
                others = [1 << v for v in range(1, 5) if not root >> v & 1]
                c = others[bits >> (2*k+1) & 1]
                if bits >> (2*k) & 1:
                    a, b = b, a
                rs[i], rs[j] = a | c, b | c
            words.append(rs)
            if not bad(rs):
                distances[bits] = 0
                queue.append(bits)
        assert queue
        while queue:
            at = queue.popleft()
            for bit in range(6):
                nxt = at ^ (1 << bit)
                if nxt not in distances:
                    distances[nxt] = distances[at]+1
                    queue.append(nxt)
        histogram.update(distances.values())
        maxima[max(distances.values())] += 1
        records.append([list(rest), ''.join(str(distances[i]) for i in range(64))])
        for bits, distance in sorted(distances.items()):
            assert distance <= 2
            if distance == 2:
                at, moves = bits, []
                for depth in (2, 1):
                    bit = next(b for b in range(6) if distances[at ^ (1 << b)] == depth-1)
                    ports, root = CHERRIES[bit//2]
                    at ^= 1 << bit
                    moves.append({'ports': list(ports), 'swap_pair': root if bit % 2 == 0 else 30 ^ root,
                                  'boundary_after': words[at]})
                hardest.append({'rest': list(rest), 'bits': bits, 'boundary': words[bits], 'moves': moves})
    return {'cherries': [[list(ports), root] for ports, root in CHERRIES], 'rest_ports': REST,
            'closed_rest_words': len(records), 'boundary_states': 64*len(records),
            'distance_histogram': sorted(histogram.items()), 'maximum_by_rest_histogram': sorted(maxima.items()),
            'distance_records_sha256': digest(records), 'distance_two_states': hardest}


def main():
    source = json.loads((HERE/'actual_core_exchange_obstruction.json').read_text())
    native = source['examples'][0]
    result = {'date': '2026-10-05',
              'scope': 'A universal two-circuit repair for a specified three-cherry eleven-port pattern, plus the complete fixed-layer cover space on one explicit core. No general neutral-escape theorem.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE/name).read_bytes()).hexdigest()}
                          for name in ('actual_core_exchange_obstruction.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'core': native['core'], 'target_incidences': native['regions'][0]['incidences'],
              'fixed_layer_edges': [e for e, c in enumerate(native['original_core_cover_word']) if PAIRS[int(c)] & 1],
              'census': census(native), 'cherry_audit': cherry_audit(), 'examples': []}
    print('Complete cover census:', result['census']['distance_histograms'], flush=True)
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE/'triangle_quotient_reduction.json').read_text())['petersen']
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        for rep_id, rep in enumerate(result['census']['hard_representatives']):
            for attached in (None, pet):
                g = full_example(kind, rep_id, rep, attached, table, fibers, domains, witnesses)
                result['examples'].append(g)
                print(kind, rep_id, g['name'], len(g['moves']), 'B pentagons', flush=True)
    (HERE/'auxiliary_exchange_orbit.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
