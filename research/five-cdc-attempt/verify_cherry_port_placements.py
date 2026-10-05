#!/usr/bin/env python3
"""Independent all-placement verification: cycle spaces and junction tables.

Imports no constructor or earlier verifier. Leaf distances are Hamming
distances; star distance two is checked by explicit neighborhoods, not BFS.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = [sum(1 << i for i in pair) for pair in itertools.combinations(range(5), 2)]
AUX = sorted(r for r in PAIRS if not r & 1)
ROOTS = (6, 10, 12)
EDGES = [(0, 1), (0, 1), (0, 2), (0, 2), (0, 3), (0, 3), (1, 4), (2, 4), (3, 4)]


def xor(values):
    result = 0
    for r in values:
        result ^= r
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def placement_orbits():
    pending = {tuple(chords) for chords in itertools.combinations(list(itertools.combinations(range(11), 2)), 3)
               if len(set(sum(chords, ()))) == 6}
    assert len(pending) == 6930
    rows = []
    while pending:
        pairs = min(pending)
        orbit = {tuple(sorted(tuple(sorted(((sign*a+k) % 11, (sign*b+k) % 11))) for a, b in pairs))
                 for k in range(11) for sign in (-1, 1)}
        assert orbit <= pending
        pending -= orbit
        rows.append((pairs, len(orbit)))
    return rows


def star_space():
    stars = [[e for e, uv in enumerate(EDGES) if v in uv] for v in range(5)]
    cycles = [mask for mask in range(1 << 9) if all(sum(mask >> e & 1 for e in star) % 2 == 0 for star in stars)]
    assert len(cycles) == 32
    states = set()
    for a, b, c in itertools.product(cycles, repeat=3):
        layers = (a, b, c, a ^ b ^ c)
        if all(sum(mask >> e & 1 for mask in layers) == 2 for e in range(9)):
            states.add(tuple(sum((2 << label) for label, mask in enumerate(layers) if mask >> e & 1) for e in range(9)))
    states = sorted(states)
    assert len(states) == 1536
    index = {state: i for i, state in enumerate(states)}
    circuits = []
    for mask in cycles[1:]:
        support = [e for e in range(9) if mask >> e & 1]
        degree = Counter(v for e in support for v in EDGES[e])
        if set(degree.values()) != {2}:
            continue
        reached = {next(iter(degree))}
        while True:
            bigger = reached | {v for e in support if set(EDGES[e]) & reached for v in EDGES[e]}
            if bigger == reached:
                break
            reached = bigger
        if reached == set(degree):
            circuits.append((mask, support))
    assert len(circuits) == 15
    graph = []
    for values in states:
        row = []
        assert all(xor(values[e] for e in star) == 0 for star in stars)
        for swap in AUX:
            affected = sum(1 << e for e, r in enumerate(values) if (r & swap).bit_count() == 1)
            for mask, support in circuits:
                if mask & affected == mask:
                    after = tuple(r ^ swap if mask >> e & 1 else r for e, r in enumerate(values))
                    row.append((index[after], swap, support))
        graph.append(sorted(row))
    reached, queue = {0}, [0]
    for at in queue:
        for nxt, _, _ in graph[at]:
            if nxt not in reached:
                reached.add(nxt)
                queue.append(nxt)
    assert len(reached) == 1536
    return states, graph


def junction_masks():
    tables = []
    for kind in ('blowup', 'semi'):
        table = {r: set() for r in AUX}
        for a, b, c, d in itertools.product(PAIRS, repeat=4):
            if any(not r & 1 for r in (a, b, c, d)):
                continue
            r = a ^ b ^ c ^ d
            if r not in AUX:
                continue
            if kind == 'semi' and b != d:
                continue
            if kind == 'blowup' and (a ^ c not in PAIRS or b ^ d not in PAIRS):
                continue
            table[r].add(a ^ b)
        tables.append(table)
    assert tables[0] == tables[1]
    charges = [h for h in range(0, 32, 2) if h.bit_count() % 2 == 0]
    assert len(charges) == 8
    return sum(1 << h for h in charges), {(p, r): sum(1 << h for h in charges if h ^ p in tables[0][r])
                                         for p in charges for r in AUX}


def verify_realized_trap(saved, states, graph, initial, masks):
    rec = saved['realized_trap']
    n, edges, ports = rec['vertices'], rec['edges'], rec['port_edge_ids']
    assert n == 10 and len(edges) == 19 and edges[:9] == [list(e) for e in EDGES]
    assert sorted(ports) == list(range(6))+list(range(9, 14))
    assert all(edges[e][0] == 0 for e in ports)
    assert Counter(v for uv in edges for v in uv) == Counter({0: 11, **{v: 3 for v in range(1, 10)}})
    stars = [[e for e, uv in enumerate(edges) if v in uv] for v in range(n)]

    def valid(values):
        assert len(values) == len(edges) and all(v in PAIRS for v in values)
        assert all(xor(values[e] for e in star) == 0 for star in stars)
        assert [e for e, v in enumerate(values) if v & 1] == rec['fixed_layer_edges'] == list(range(14, 19))

    def allowed(values):
        prefix, out = 0, initial
        for e in ports:
            r = values[e]
            out &= masks[prefix, r]
            prefix ^= r
        assert prefix == 0
        return [h for h in range(32) if out >> h & 1]

    def apply(values, move):
        selected, swap = move['edges'], move['swap_pair']
        degree = Counter(v for e in selected for v in edges[e])
        assert set(degree.values()) == {2}
        reached, queue = {next(iter(degree))}, [next(iter(degree))]
        for v in queue:
            for e in selected:
                if v in edges[e]:
                    for w in edges[e]:
                        if w not in reached:
                            reached.add(w)
                            queue.append(w)
        assert reached == set(degree)
        assert all((values[e] & swap).bit_count() == 1 for e in selected)
        after = [r ^ swap if e in selected else r for e, r in enumerate(values)]
        valid(after)
        return after

    values = rec['initial_cover']
    witness = saved['witnesses']['star:2']
    assert values[:9] == list(states[witness['initial_state']])
    assert [values[e] for e in ports] == witness['boundary']
    valid(values)
    assert not allowed(values)
    for state in saved['cube_state_ids']:
        assert not allowed(list(states[state])+values[9:])
    for nxt, _, _ in graph[witness['initial_state']]:
        assert not allowed(list(states[nxt])+values[9:])
    assert len(rec['moves']) == 2
    for k, move in enumerate(rec['moves']):
        assert all(e < 9 for e in move['edges'])
        values = apply(values, move)
        assert move['cover_after'] == values and move['boundary_after'] == [values[e] for e in ports]
        assert move['surviving_charges'] == allowed(values)
        assert bool(allowed(values)) == bool(k)
    assert allowed(apply(rec['initial_cover'], rec['outside_one_move']))
    base = rec['base_edges']
    assert rec['base_vertices'] == 20 and rec['selected_cycle'] == list(range(11))
    assert len(base) == len({tuple(sorted(uv)) for uv in base}) == 30
    assert all(u != v for u, v in base)
    assert Counter(v for uv in base for v in uv) == Counter({v: 3 for v in range(20)})
    assert base[:11] == [[i, (i+1) % 11] for i in range(11)]
    mapped = [[0 if v < 11 else v-10 for v in uv] for uv in base[11:]]
    assert mapped == edges
    assert all(base[11+e][0] == p for p, e in enumerate(ports))
    print('Verified the realized trapped cube on a 20-vertex simple cubic base, both star repairs, and the outside shortcut.', flush=True)


def main():
    saved = json.loads((HERE/'cherry_port_placements.json').read_text())
    for source in saved['sources']:
        assert hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256']
    assert saved['auxiliary_pairs'] == AUX and saved['central_pairs'] == list(ROOTS)
    assert saved['star_edges'] == [list(e) for e in EDGES]
    orbits = placement_orbits()
    assert saved['placement_count'] == sum(size for _, size in orbits) == 6930
    assert saved['placement_classes'] == len(orbits) == len(saved['placements']) == 350
    assert saved['orbit_size_histogram'] == [list(x) for x in sorted(Counter(size for _, size in orbits).items())]
    states, graph = star_space()
    assert saved['star_cover_count'] == len(states)
    assert saved['star_covers_sha256'] == digest(states)
    assert saved['star_circuit_graph_sha256'] == digest(graph)
    index = {s: i for i, s in enumerate(states)}
    domains = [sorted((a, b) for a, b in itertools.product(AUX, repeat=2) if a ^ b == r) for r in ROOTS]
    cube = [index[sum((domains[k][b >> (2*k) & 3] for k in range(3)), ())+ROOTS] for b in range(64)]
    assert saved['cube_state_ids'] == cube
    for b, at in enumerate(cube):
        for bit in range(6):
            swap = ROOTS[bit//2] if bit % 2 == 0 else 30 ^ ROOTS[bit//2]
            assert (cube[b ^ (1 << bit)], swap, [2*(bit//2), 2*(bit//2)+1]) in graph[at]
    # Every ordered auxiliary triangle has exactly one normalizing permutation.
    relabeled = {tuple(sum(1 << p[i-1] for i in range(1, 5) if r >> i & 1) for r in ROOTS)
                 for p in itertools.permutations(range(1, 5))}
    assert len(relabeled) == 24
    assert relabeled == {tuple(v[6:]) for v in states}
    rest_words = [w for w in itertools.product(AUX, repeat=5) if xor(w) == 0]
    assert len(rest_words) == saved['closed_rest_words'] == 960
    initial, masks = junction_masks()
    totals, weighted = [Counter(), Counter()], [Counter(), Counter()]
    witness_checks = set()
    for placement_id, ((pairs, size), row) in enumerate(zip(orbits, saved['placements'])):
        rest_ports = sorted(set(range(11))-set(sum(pairs, ())))
        assert row['pairs'] == [list(p) for p in pairs] and row['orbit_size'] == size
        assert row['rest_ports'] == rest_ports
        hist, maxima = [Counter(), Counter()], [Counter(), Counter()]
        records, trapped = bytearray(), []
        for rest in rest_words:
            cache = {}

            def word(at):
                rs = [0]*11
                for p, r in zip(rest_ports, rest):
                    rs[p] = r
                for k, (i, j) in enumerate(pairs):
                    rs[i], rs[j] = states[at][2*k:2*k+2]
                return rs

            def accept(at):
                if at not in cache:
                    allowed, prefix = initial, 0
                    for r in word(at):
                        allowed &= masks[prefix, r]
                        prefix ^= r
                    assert prefix == 0
                    cache[at] = bool(allowed)
                return cache[at]

            good_bits = [b for b, at in enumerate(cube) if accept(at)]
            if not good_bits:
                distances = [-1]*64
                trapped.append(list(rest))
            else:
                distances = [0 if accept(at) else min((b ^ g).bit_count() for g in good_bits)
                             for b, at in enumerate(cube)]
            full = distances.copy()
            for b, at in enumerate(cube):
                if distances[b] == -1 or distances[b] >= 2:
                    neighbors = {nxt for nxt, _, _ in graph[at]}
                    if any(accept(nxt) for nxt in neighbors):
                        full[b] = 1
                    else:
                        assert any(accept(end) for nxt in neighbors for end, _, _ in graph[nxt]), (placement_id, rest, b)
                        full[b] = 2
            for key, witness in saved['witnesses'].items():
                if witness['placement_id'] != placement_id or witness['rest'] != list(rest):
                    continue
                b = witness['bits']
                assert witness['initial_state'] == cube[b] and witness['boundary'] == word(cube[b])
                assert witness['cherry_distance'] == distances[b] and witness['star_distance'] == full[b]
                d = distances[b] if key.startswith('cherry:') else full[b]
                assert int(key.split(':')[1]) == d
                if d == -1:
                    assert not witness['moves'] and not good_bits
                else:
                    assert len(witness['moves']) == d
                    at = cube[b]
                    for move in witness['moves']:
                        nxt = move['state_after']
                        assert (nxt, move['swap_pair'], move['edges']) in graph[at]
                        if key.startswith('cherry:'):
                            assert len(move['edges']) == 2
                        at = nxt
                    assert accept(at)
                witness_checks.add(key)
            for i, ds in enumerate((distances, full)):
                hist[i].update(ds)
                maxima[i][max(ds)] += 1
                records.extend(d if d >= 0 else 255 for d in ds)
        assert row['closed_bad_rest_words'] == trapped
        assert row['distance_records_sha256'] == hashlib.sha256(records).hexdigest()
        for i, name in enumerate(('cherry', 'star')):
            assert row['distance_histograms'][name] == [list(x) for x in sorted(hist[i].items())]
            assert row['maximum_by_rest_histograms'][name] == [list(x) for x in sorted(maxima[i].items())]
            totals[i].update(hist[i])
            weighted[i].update({d: n*size for d, n in hist[i].items()})
        if placement_id % 50 == 0:
            print('Independently verified placement', placement_id, '/', len(orbits), flush=True)
    assert witness_checks == set(saved['witnesses'])
    for i, name in enumerate(('cherry', 'star')):
        assert saved['representative_distance_histograms'][name] == [list(x) for x in sorted(totals[i].items())]
        assert saved['labelled_placement_distance_histograms'][name] == [list(x) for x in sorted(weighted[i].items())]
        maxima = Counter(-1 if r['distance_histograms'][name][0][0] == -1 else max(d for d, n in r['distance_histograms'][name])
                         for r in saved['placements'])
        assert saved['class_maximum_histograms'][name] == [list(x) for x in sorted(maxima.items())]
    verify_realized_trap(saved, states, graph, initial, masks)
    print('All 350 placement classes and 21,504,000 normalized states independently verified.', flush=True)
    print('Star circuit distances:', sorted(totals[1].items()), flush=True)


if __name__ == '__main__':
    main()
