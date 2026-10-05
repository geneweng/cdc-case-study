#!/usr/bin/env python3
"""Exact protected auxiliary exchanges from core connected components.

A general reachability criterion, complete partitions of the two eleven-port
witnesses, and full graph certificates. No general length-eleven theorem.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from eight_cycle_completion import example_seed, marked_test, matchings
from eleven_cycle_obstruction import WORDS
from fourflow_quotient_repair import build, contracted, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from nine_cycle_completion import AUX, bad_regions, protected_pairing, rejected
from short_cycle_boundary import local_table, quotient_assignment

HERE = Path(__file__).resolve().parent
SPECS = {
    'blocked': (list(WORDS['blocked_unions']), [15]*11, (1, 3)),
    'eight': ([6, 10, 6, 18]*2, [15]*8, (0, 2)),
    'ten': ([6, 6, 10, 6, 18, 6, 6, 10, 6, 18], [15]*10, (1, 3)),
}
RIM = [(0, 9, 2), (1, 2, 2), (3, 10, 2), (5, 7, 2), (0, 3, 4),
       (1, 6, 4), (5, 8, 4), (2, 6, 8), (4, 9, 8), (4, 10, 16), (7, 8, 16)]


def even_partitions(xs):
    if not xs:
        yield ()
        return
    first, *rest = xs
    for size in range(1, len(rest)+1, 2):
        for chosen in itertools.combinations(rest, size):
            block = (first,)+chosen
            for tail in even_partitions(tuple(i for i in rest if i not in chosen)):
                yield (block,)+tail


def reachable_masks(blocks):
    span = [0]
    for block in blocks:
        for j in block[1:]:
            span += [s ^ (1 << block[0]) ^ (1 << j) for s in span]
    return sorted(span)


def partition_audit():
    result = {}
    for name, rs in WORDS.items():
        rows, outcomes = [], {}
        for t in AUX:
            active = tuple(i for i, a in enumerate(rs) if (a & t).bit_count() == 1)
            blocked, histogram, count, tested = [], Counter(), 0, 0
            for blocks in even_partitions(active):
                count += 1
                span = reachable_masks(blocks)
                tested += len(span)
                escaping = [s.bit_count()//2 for s in span
                            if not rejected([a ^ t if s >> i & 1 else a for i, a in enumerate(rs)], range(11))]
                minimum = min(escaping, default=-1)
                histogram[minimum] += 1
                if t in (18, 12):
                    outcomes[t, blocks] = minimum
                if not escaping:
                    blocked.append([list(b) for b in blocks])
            rows.append({'swap_pair': t, 'affected_ports': list(active), 'partitions': count,
                         'subsets_checked': tested, 'minimum_terminal_pairs_histogram': sorted(histogram.items()),
                         'blocked_partitions': sorted(blocked)})
        joint = Counter()
        for t, blocks in outcomes:
            if t == 18:
                possibilities = [outcomes[s, blocks] for s in (18, 12) if outcomes[s, blocks] >= 0]
                joint[min(possibilities, default=-1)] += 1
        result[name] = {'word': list(rs), 'swaps': rows,
                        'shared_partition_14_23_histogram': sorted(joint.items())}
    return result


def rim_census():
    rs, colors = WORDS['blocked_unions'], (2, 4, 8, 16)
    options = [list(matchings([i for i, r in enumerate(rs) if r & c])) for c in colors]
    escaping = {t: {ij for ij in itertools.combinations([i for i, r in enumerate(rs) if (r & t).bit_count() == 1], 2)
                    if not rejected([r ^ t if i in ij else r for i, r in enumerate(rs)], range(11))} for t in AUX}
    histogram, candidates, simple, hardest = Counter(), 0, 0, []
    for choice in itertools.product(*options):
        candidates += 1
        edges = [(i, j, c) for c, matching in zip(colors, choice) for i, j in matching]
        if len({tuple(sorted((i, j))) for i, j, _ in edges}) != 11:
            continue
        simple += 1
        choices, rows = 0, []
        for t in AUX:
            adjacency = [[] for _ in rs]
            for i, j, c in edges:
                if c & t:
                    adjacency[i].append(j)
                    adjacency[j].append(i)
            active = {i for i, r in enumerate(rs) if (r & t).bit_count() == 1}
            blocks = []
            while active:
                start, previous = min(active), -1
                at = start
                while True:
                    nxt = next(v for v in adjacency[at] if v != previous)
                    previous, at = at, nxt
                    if len(adjacency[at]) == 1:
                        break
                active.difference_update((start, at))
                blocks.append((start, at))
            good_pairs = sorted(set(blocks) & escaping[t])
            choices += bool(good_pairs)
            rows.append({'swap_pair': t, 'component_ports': [list(b) for b in blocks],
                         'escaping_single_pairs': [list(p) for p in good_pairs]})
        assert choices >= 2
        histogram[choices] += 1
        if choices == 2:
            hardest.append({'rim_edges': [list(e) for e in edges], 'swaps': rows})
    assert len(hardest) == 1 and hardest[0]['rim_edges'] == [list(e) for e in RIM]
    return {'boundary_word': list(rs), 'colored_pairings': candidates, 'simple_rim_realizations': simple,
            'single_escape_swap_histogram': sorted(histogram.items()), 'hardest': hardest[0]}


def split_forest(core, regions, pairs, target, swap, protected):
    affected = [e for e, a in enumerate(pairs) if (a & swap).bit_count() == 1]
    halfedges = [2*e+s for e in affected for s in (0, 1)]
    parent = {h: h for h in halfedges}
    def root(h):
        while parent[h] != h:
            parent[h] = parent[parent[h]]
            h = parent[h]
        return h
    def join(a, b):
        a, b = root(a), root(b)
        if a != b:
            parent[max(a, b)] = min(a, b)
    fixed_hubs = set()
    for rec in protected:
        region = regions[rec['region']]
        fixed_hubs.add(region['hub'])
        for i, j in rec['pairs']:
            join(region['incidences'][i], region['incidences'][j])
    hub = regions[target]['hub']
    for v in range(core['vertices']):
        if v == hub or v in fixed_hubs:
            continue
        hs = [h for h in halfedges if core['edges'][h//2][h % 2] == v]
        for h in hs[1:]:
            join(hs[0], h)
    adjacency = {root(h): [] for h in halfedges}
    for e in affected:
        a, b = root(2*e), root(2*e+1)
        adjacency[a].append((b, e))
        adjacency[b].append((a, e))
    terminals = {root(h): i for i, h in enumerate(regions[target]['incidences']) if h in parent}
    visited, forest, components = set(), [], []
    for start in sorted(adjacency):
        if start in visited:
            continue
        visited.add(start)
        tree_parent, order = {start: None}, [start]
        for u in order:
            for v, e in adjacency[u]:
                if v not in visited:
                    visited.add(v)
                    tree_parent[v] = (u, e)
                    order.append(v)
        block = sorted(terminals[v] for v in order if v in terminals)
        assert len(block) % 2 == 0
        if block:
            components.append(block)
        forest.append((order, tree_parent))
    return sorted(components), terminals, forest


def realize_mask(mask, terminals, forest):
    selected = []
    for order, tree_parent in forest:
        parity = {v: int(v in terminals and bool(mask >> terminals[v] & 1)) for v in order}
        for v in reversed(order[1:]):
            if parity[v]:
                u, e = tree_parent[v]
                selected.append(e)
                parity[u] ^= 1
        assert parity[order[0]] == 0
    assert len(selected) == len(set(selected))
    return sorted(selected)


def attempt(core, regions, pairs, target, swap, protected):
    blocks, terminals, forest = split_forest(core, regions, pairs, target, swap, protected)
    rs = [pairs[h//2] for h in regions[target]['incidences']]
    marked = regions[target]['marked_cuts']
    reachable = reachable_masks(blocks)
    escaping = [s for s in reachable if not rejected([a ^ swap if s >> i & 1 else a for i, a in enumerate(rs)], marked)]
    record = {'target_region': target, 'swap_pair': swap, 'protected_pairings': protected,
              'component_ports': blocks, 'reachable_masks': len(reachable),
              'escaping_masks': len(escaping),
              'escape_size_histogram': sorted(Counter(s.bit_count() for s in escaping).items()),
              'realizations': [[s, realize_mask(s, terminals, forest)] for s in reachable]}
    if not escaping:
        return record, None
    mask = min(escaping, key=lambda s: (s.bit_count(), s))
    edges = realize_mask(mask, terminals, forest)
    changed = [a ^ swap if e in edges else a for e, a in enumerate(pairs)]
    record.update({'selected_ports': [i for i in range(len(rs)) if mask >> i & 1],
                   'edges': edges, 'cover_word_after': word(PAIRS.index(a) for a in changed)})
    return record, changed


def repair_core(core, regions, original, first_swap=None):
    pairs, moves = original.copy(), []
    while before := bad_regions(regions, pairs):
        target = before[0]
        trials = []
        priority = ([first_swap]+[t for t in AUX if t != first_swap]) if first_swap else AUX
        for t in priority:
            protected = []
            for i, region in enumerate(regions):
                if region['critical'] and i not in before:
                    rs = tuple(pairs[h//2] for h in region['incidences'])
                    # This is an explicitly checked witness, not an assumed
                    # universal protection lemma at length eleven.
                    matching = protected_pairing(rs, t, tuple(region['marked_cuts']))
                    protected.append({'region': i, 'pairs': [list(p) for p in matching]})
            rec, changed = attempt(core, regions, pairs, target, t, protected)
            trials.append(rec)
            if changed is not None:
                after = bad_regions(regions, changed)
                assert set(after) < set(before) and target not in after
                moves.append({'bad_before': before, 'bad_after': after, 'attempts': trials})
                pairs = changed
                break
        else:
            raise RuntimeError('No repair with these protected pairings; no general existence theorem is asserted.')
        first_swap = None
    return pairs, moves


def initialize(g, core_pairs, zs, four, table, fibers):
    quotient_flow(g, four)
    letters = [[core_pairs[j['edges'][-1]], z] for j, z in zip(g['junctions'], zs)]
    support, _ = quotient_assignment(g, letters, table)
    support |= sum((a & 1) << e for e, a in enumerate(core_pairs))
    values = {e: 2*int(a)+(support >> i & 1) for i, (e, a) in enumerate(zip(g['kept_edge_ids'], g['quotient_four_flow_word']))}
    for block in g['blocks']:
        es = block['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    g['initial_flow_word'] = word(values[e] for e in range(len(g['edges'])))
    g['rejected_core_cover_word'] = word(PAIRS.index(a) for a in core_pairs)
    return g


def cell_seed(kind, profiles, table, fibers, protect=False):
    cycles, zs, entries, n = [], [], {}, 0
    for cell, profile in enumerate(profiles):
        rs, bits, _ = SPECS[profile]
        k = len(rs)
        cs = [list(range(n, n+k)), list(range(n+k, n+2*k))]
        cycles.extend(cs)
        zs.extend(bits*2)
        four = [1]*k if k % 2 == 0 else [1]*(k-2)+[2, 3]
        positions = list(range(k))
        if protect:
            assert profiles == ['blocked']
            positions[0], positions[2] = 2, 0
        for i, (r, a) in enumerate(zip(rs, four)):
            entries[cell, i] = ([cs[0][i], cs[1][positions[i]]], r, a)
        n += 2*k
    joined = []
    for cell in range(len(profiles)-1):
        left = entries.pop((cell, SPECS[profiles[cell]][2][1]))
        right = entries.pop((cell+1, SPECS[profiles[cell+1]][2][0]))
        assert left[1:] == right[1:] == (6, 1)
        (u, v), _, _ = left
        (x, y), _, _ = right
        joined.extend([([u, x], 6, 1), ([v, y], 6, 1)])
    outside = list(entries.values())+joined
    base = [(c[i], c[(i+1) % len(c)]) for c in cycles for i in range(len(c))]
    base.extend(uv for uv, _, _ in outside)
    return initialize(build(n, base, cycles, kind), [r for _, r, _ in outside], zs,
                      [a for _, _, a in outside], table, fibers)


def loop_seed(kind, table, fibers):
    outside = [(0, 3), (1, 5), (2, 9), (7, 10), (4, 11), (6, 11), (8, 11)]
    pairs = [6, 6, 10, 18, 24, 12, 20]
    four = [1, 1, 2, 3, 1, 3, 2]
    base = [(i, (i+1) % 11) for i in range(11)]+outside
    return initialize(build(12, base, [list(range(11))], kind), pairs, [15]*11, four, table, fibers)


def rim_seed(kind, table, fibers):
    adjacency = [[] for _ in range(11)]
    for i, j, _ in RIM:
        adjacency[i].append(j)
        adjacency[j].append(i)
    seen, coloring = set(), {}
    for start in range(11):
        if start in seen:
            continue
        cycle, previous, at = [], -1, start
        while at not in seen:
            cycle.append(at)
            seen.add(at)
            nxt = next(v for v in adjacency[at] if v != previous)
            previous, at = at, nxt
        colors = [1+i % 2 for i in range(len(cycle))]
        if len(cycle) % 2:
            colors[-1] = 3
        coloring.update({frozenset((cycle[i], cycle[(i+1) % len(cycle)])): a for i, a in enumerate(colors)})
    rim_four = [coloring[frozenset((i, j))] for i, j, _ in RIM]
    stems = [0]*11
    for (i, j, _), a in zip(RIM, rim_four):
        stems[i] ^= a
        stems[j] ^= a
    outside = [(i, i+11) for i in range(11)]+[(i+11, j+11) for i, j, _ in RIM]
    pairs = list(WORDS['blocked_unions'])+[1 | c for _, _, c in RIM]
    base = [(i, (i+1) % 11) for i in range(11)]+outside
    return initialize(build(22, base, [list(range(11))], kind), pairs, [15]*11,
                      stems+rim_four, table, fibers)


def regions_for(g, initial, pairs):
    core = contracted(g)
    records, offset = [], 0
    for cycle in g['selected_cycles']:
        js = g['junctions'][offset:offset+len(cycle)]
        letters = [[pairs[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))] for j in js]
        marked, _ = marked_test(letters)
        hs = [2*j['edges'][-1]+g['edges'][j['edges'][-1]].index(j['vertex']) for j in js]
        records.append({'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                        'marked_cuts': marked, 'critical': len(marked) >= 8,
                        'junction_indices': list(range(offset, offset+len(cycle)))})
        offset += len(cycle)
    return records


def full_example(kind, name, old, attached, table, fibers, domains, witnesses):
    g, initial, original = example_seed(old, attached)
    core = contracted(g)
    regions = regions_for(g, initial, original)
    first = 18 if name.startswith('native_rim') else 10 if name == 'protected_neighbor' else None
    changed, moves = repair_core(core, regions, original, first)
    g.update({'name': name, 'core': core, 'regions': regions,
              'profile_names': [str(len(c)) for c in g['selected_cycles']],
              'core_cover_moves': moves})
    if name == 'protected_neighbor':
        es = [g['junctions'][i]['edges'][-1] for i in (0, 1)]
        naive = [a ^ 10 if e in es else a for e, a in enumerate(original)]
        assert bad_regions(regions, original) == [0] and bad_regions(regions, naive) == [1]
        g['unprotected_exchange'] = {'swap_pair': 10, 'edges': es, 'bad_before': [0], 'bad_after': [1],
                                     'cover_word_after': word(PAIRS.index(a) for a in naive)}
    pairs, charges = dict(enumerate(changed)), []
    for region in regions:
        js = [g['junctions'][i] for i in region['junction_indices']]
        letters = [[changed[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))]
                   for j in js]
        _, allowed = marked_test(letters)
        assert allowed
        h, prefix = min(allowed), 0
        charges.append({'letters': letters, 'surviving_charges': allowed, 'chosen_charge': h})
        for j, (r, z) in zip(js, letters):
            for e, a in zip(j['edges'], table[r, z][h ^ prefix]):
                assert e not in pairs or pairs[e] == a
                pairs[e] = a
            prefix ^= r
    cover = ['?']*len(g['edges'])
    for e, a in pairs.items():
        cover[e] = str(PAIRS.index(a))
    flow, moves = initial.copy(), []
    for i, block in enumerate(g['blocks']):
        es = block['edge_representatives']
        repair = joint_repair([flow[e] for e in es], 1, [PAIRS.index(pairs[e]) for e in es[10:]],
                              fibers, domains, witnesses)
        for move in repair['moves']:
            selected_edges = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            moves.append({'piece': i, 'edges': selected_edges, 'increment': move['increment']})
            for e in selected_edges:
                flow[e] ^= move['increment']
        for e, a in zip(es[:10], repair['cover_word'][:10]):
            cover[e] = a
    g.update({'original_core_cover_word': word(PAIRS.index(a) for a in original),
              'changed_core_cover_word': word(PAIRS.index(a) for a in changed),
              'regional_extensions': charges, 'initial_flow_word': word(initial),
              'quotient_cover_word': word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids']),
              'moves': moves, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    return g


def main():
    result = {'date': '2026-10-05',
              'scope': 'Exact reachability for one auxiliary-label exchange under specified protected transitions, with two classified eleven-port witnesses and positive graph examples. No universal length-eleven completion theorem is asserted.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE/name).read_bytes()).hexdigest()}
                          for name in ('eleven_cycle_obstruction.json', 'ten_cycle_completion.json',
                                       'triangle_quotient_reduction.json', 'petersen_boundary_relation.txt.gz')],
              'component_partitions': partition_audit(), 'rim_census': rim_census(), 'examples': []}
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE/'triangle_quotient_reduction.json').read_text())['petersen']
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        cases = [
            ('free_neighbor', cell_seed(kind, ['blocked'], table, fibers), None),
            ('protected_neighbor', cell_seed(kind, ['blocked'], table, fibers, True), None),
            ('core_loops', loop_seed(kind, table, fibers), None),
            ('native_rim', rim_seed(kind, table, fibers), None),
            ('native_rim_no_four_flow', rim_seed(kind, table, fibers), pet),
            ('mixed_no_four_flow', cell_seed(kind, ['blocked', 'blocked', 'eight', 'ten'], table, fibers), pet),
        ]
        for name, old, attached in cases:
            g = full_example(kind, name, old, attached, table, fibers, domains, witnesses)
            result['examples'].append(g)
            print(kind, name, g['vertices'], 'vertices;', len(g['core_cover_moves']),
                  'core exchanges;', len(g['moves']), 'B pentagons', flush=True)
    (HERE/'core_component_exchange.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved component partitions and twelve full graph completions.')


if __name__ == '__main__':
    main()
