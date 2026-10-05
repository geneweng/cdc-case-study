#!/usr/bin/env python3
"""Simultaneous fixed-layer completion through arbitrarily many eight-cycles.

Builds protected transition pairings, closed-trail cover exchanges, and B-only
flow repairs. Standard library only; an independent verifier accompanies it.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from eight_cycle_completion import (AUX, choose_pair, digest, example_seed,
                                   hamiltonian_words, marked_test, matchings, prefixes)
from fourflow_quotient_repair import build, contracted, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from short_cycle_boundary import local_table, quotient_assignment

HERE = Path(__file__).parent
PATTERN = [6, 10, 6, 18]
FRAGILE = [list(range(8)), [0, 1, 3, 2, 5, 4, 7, 6]]
REPEATED = [list(range(8)), [7, 4, 1, 2, 6, 0, 3, 5], [4, 7, 6, 0, 5, 1, 2, 3]]


@lru_cache(None)
def pairing_spans(mask):
    result = []
    for matching in matchings([i for i in range(8) if mask >> i & 1]):
        span = [0]
        for i, j in matching:
            span += [s ^ (1 << i) ^ (1 << j) for s in span]
        result.append((tuple(matching), tuple(sorted(span))))
    return result


@lru_cache(None)
def protected_pairing(rs, t):
    assert len(rs) == 8 and len(set(prefixes(rs))) < 8 and all(r in AUX for r in rs)
    mask = sum(1 << i for i, r in enumerate(rs) if (r & t).bit_count() == 1)
    for matching, span in pairing_spans(mask):
        if all(len(set(prefixes([r ^ t if s >> i & 1 else r for i, r in enumerate(rs)]))) < 8
               for s in span):
            return matching
    raise AssertionError('The protected-pairing lemma guarantees a matching')


def local_audit():
    # Auxiliary-label permutations reduce the new lemma to t={1,2}, mask 6.
    t, groups = 6, {}
    for rs in hamiltonian_words():
        mask = sum(1 << i for i, r in enumerate(rs) if (r & t).bit_count() == 1)
        key = tuple(min(r, r ^ t) if mask >> i & 1 else r for i, r in enumerate(rs))
        bits = sum(1 << i for i, r in enumerate(rs) if r != key[i])
        groups.setdefault((key, mask), set()).add(bits)
    records, histogram, states, unique = [], Counter(), 0, None
    for (key, mask), bads in sorted(groups.items()):
        base = min(bads)
        for bits in range(256):
            if bits & ~mask or (bits ^ base).bit_count() % 2:
                continue
            states += 1
            if bits in bads:
                continue
            safe = [matching for matching, span in pairing_spans(mask)
                    if all(bits ^ s not in bads for s in span)]
            assert safe
            histogram[len(safe)] += 1
            rs = tuple(r ^ t if bits >> i & 1 else r for i, r in enumerate(key))
            assert protected_pairing(rs, t) == safe[0]
            rec = [list(rs), len(safe), [list(ij) for ij in safe[0]]]
            records.append(rec)
            if len(safe) == 1 and unique is None:
                unique = {'boundary_pairs': list(rs), 'swap_pair': t, 'pairing': rec[2]}
    closed = 0
    for rs in itertools.product(AUX, repeat=7):
        total = 0
        for r in rs:
            total ^= r
        closed += total in AUX
    assert closed == 210048 and len(groups) == 462 and states == 10848 and len(records) == 9360
    return {'swap_pair': t, 'closed_boundary_words': closed, 'bad_words': 1488,
            'threat_groups': len(groups), 'states_in_threat_groups': states,
            'good_states_requiring_check': len(records), 'automatically_safe_good_states': closed-states,
            'protected_pairing_count_histogram': sorted(histogram.items()),
            'witness_sha256': digest(sorted(records)), 'unique_pairing_example': unique}


def region_records(g, initial, pairs):
    core = contracted(g)
    records, offset = [], 0
    for cycle in g['selected_cycles']:
        js = g['junctions'][offset:offset+len(cycle)]
        letters = [[pairs[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))]
                   for j in js]
        marked, _ = marked_test(letters)
        hs = [2*j['edges'][-1]+g['edges'][j['edges'][-1]].index(j['vertex']) for j in js]
        critical = len(cycle) == 8 and len(marked) == 8
        assert critical or len(marked) <= 7
        records.append({'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                        'marked_cuts': marked, 'critical': critical,
                        'junction_indices': list(range(offset, offset+len(cycle)))})
        offset += len(cycle)
    return records


def bad_regions(regions, pairs):
    return [i for i, r in enumerate(regions) if r['critical'] and
            len(set(prefixes([pairs[h//2] for h in r['incidences']]))) == 8]


def repair_core(core, regions, original):
    pairs, moves = original.copy(), []
    endpoints = [v for uv in core['edges'] for v in uv]
    at_vertex = [[] for _ in range(core['vertices'])]
    for h, v in enumerate(endpoints):
        at_vertex[v].append(h)
    while before := bad_regions(regions, pairs):
        target = before[0]
        rec = regions[target]
        hub, hs = rec['hub'], rec['incidences']
        rs = [pairs[h//2] for h in hs]
        t, _, _, _ = choose_pair(rs)
        protected, mate = [], {}
        for i, region in enumerate(regions):
            if not region['critical'] or i in before:
                continue
            ws = tuple(pairs[h//2] for h in region['incidences'])
            matching = protected_pairing(ws, t)
            protected.append({'region': i, 'pairs': [list(ij) for ij in matching]})
            for a, b in matching:
                u, v = region['incidences'][a], region['incidences'][b]
                mate[u], mate[v] = v, u
        for v in range(core['vertices']):
            if v == hub:
                continue
            at = [h for h in at_vertex[v] if (pairs[h//2] & t).bit_count() == 1]
            assert len(at) % 2 == 0
            if at and at[0] in mate:
                assert all(h in mate for h in at)
                continue
            for a, b in zip(at[::2], at[1::2]):
                mate[a], mate[b] = b, a
        terminals = {h: i for i, h in enumerate(hs) if (pairs[h//2] & t).bit_count() == 1}
        consumed, chosen = set(), None
        for start in sorted(terminals):
            if start in consumed:
                continue
            h, path = start, []
            while True:
                path.append(h)
                h ^= 1
                if h in terminals:
                    break
                h = mate[h]
                assert len(path) <= len(pairs)
            consumed.update((start, h))
            i, j = terminals[start], terminals[h]
            changed = rs.copy()
            changed[i] ^= t
            changed[j] ^= t
            if len(set(prefixes(changed))) < 8:
                chosen = (path, [i, j])
                break
        assert chosen is not None
        path, ports = chosen
        es = [h//2 for h in path]
        assert len(es) == len(set(es))
        for e in es:
            pairs[e] ^= t
        after = bad_regions(regions, pairs)
        assert set(after) < set(before) and target not in after
        moves.append({'target_region': target, 'swap_pair': t, 'trail_incidences': path,
                      'ports': ports, 'protected_pairings': protected,
                      'bad_before': before, 'bad_after': after,
                      'cover_word_after': word(PAIRS.index(a) for a in pairs)})
    return pairs, moves


def seed(kind, orders, table, fibers):
    m = len(orders)
    core_edges = [(i, (i+1) % m) for i in range(m) for _ in range(4)]
    slots = {}
    for i, order in enumerate(orders):
        hs = [2*(4*((i-1) % m)+j)+1 for j in range(4)]+[2*(4*i+j) for j in range(4)]
        for j, index in enumerate(order):
            slots[hs[index]] = 8*i+j
    cycles = [list(range(8*i, 8*i+8)) for i in range(m)]
    base = [(c[j], c[(j+1) % 8]) for c in cycles for j in range(8)]
    base += [(slots[2*e], slots[2*e+1]) for e in range(len(core_edges))]
    g = build(8*m, base, cycles, kind)
    quotient_flow(g, [1]*len(core_edges))
    pairs = PATTERN*m
    letters = [[pairs[j['edges'][-1]], 15] for j in g['junctions']]
    support, _ = quotient_assignment(g, letters, table)
    hf = [2*int(a)+(support >> i & 1) for i, a in enumerate(g['quotient_four_flow_word'])]
    values = dict(zip(g['kept_edge_ids'], hf))
    for block in g['blocks']:
        es = block['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    g['initial_flow_word'] = word(values[e] for e in range(len(g['edges'])))
    g['rejected_core_cover_word'] = word(PAIRS.index(a) for a in pairs)
    return g


def full_example(kind, name, orders, pet, table, fibers, domains, witnesses):
    old = seed(kind, orders, table, fibers)
    g, initial, original = example_seed(old, pet)
    core = contracted(g)
    regions = region_records(g, initial, original)
    changed, cover_moves = repair_core(core, regions, original)
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
            selected = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            moves.append({'piece': i, 'edges': selected, 'increment': move['increment']})
            for e in selected:
                flow[e] ^= move['increment']
        for e, a in zip(es[:10], repair['cover_word'][:10]):
            cover[e] = a
    g.update({'name': name, 'core': core, 'regions': regions, 'port_orders': orders,
              'original_core_cover_word': word(PAIRS.index(a) for a in original),
              'core_cover_moves': cover_moves, 'changed_core_cover_word': word(PAIRS.index(a) for a in changed),
              'regional_extensions': charges, 'initial_flow_word': word(initial),
              'quotient_cover_word': word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids']),
              'moves': moves, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    if name == 'fragile_good_region':
        naive = [r ^ 12 if e in (0, 1) else r for e, r in enumerate(original)]
        assert bad_regions(regions, original) == [0] and bad_regions(regions, naive) == [1]
        g['unprotected_exchange'] = {'swap_pair': 12, 'edges': [0, 1], 'bad_before': [0], 'bad_after': [1],
                                     'cover_word_after': word(PAIRS.index(a) for a in naive)}
    return g


def main():
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE / 'triangle_quotient_reduction.json').read_text())['petersen']
    result = {'date': '2026-10-05',
              'scope': 'Prescribed-layer completion reduces exactly to the core for any number of selected cycles of lengths three through eight. Other regions may have arbitrary lengths if they have at most seven marked cuts. No general 5-CDC proof or result for obstructed longer regions is claimed.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                          for name in ('eight_cycle_completion.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'local_protection': local_audit(), 'examples': []}
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        for name, orders, attached in (
                ('two_bad_regions', [list(range(8))]*2, None),
                ('fragile_good_region', FRAGILE, None),
                ('repeated_good_vertex', REPEATED, None),
                ('eight_bad_regions_no_four_flow', [list(range(8))]*8, pet)):
            g = full_example(kind, name, orders, attached, table, fibers, domains, witnesses)
            result['examples'].append(g)
            print(kind, name, g['vertices'], 'vertices;', len(g['core_cover_moves']),
                  'cover exchanges;', len(g['moves']), 'B pentagons', flush=True)
    (HERE / 'simultaneous_eight_completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved protected pairings for all 9,360 threatened good states and eight full completions.')


if __name__ == '__main__':
    main()
