#!/usr/bin/env python3
"""Sharp failure of the universal auxiliary escape lemma at length eleven.

Finite pairing witnesses and positive full graph completions. Standard library
only. This is not a counterexample to prescribed-layer completion or 5-CDC.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from eight_cycle_completion import example_seed, marked_test
from fourflow_quotient_repair import build, contracted, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from nine_cycle_completion import AUX, bad_regions, pairing_spans, rejected
from short_cycle_boundary import local_table, quotient_assignment

HERE = Path(__file__).resolve().parent
WORDS = {
    'two_trails': (6, 10, 6, 12, 20, 6, 10, 20, 18, 12, 20),
    'blocked_unions': (6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18),
}
MARKED = tuple(range(11))


def classification():
    classes = Counter()
    for n in range(4):
        for missing in itertools.combinations(range(11), n):
            marked = 2047 ^ sum(1 << i for i in missing)
            for values in itertools.product((0, 1), repeat=n):
                odd = sum(v << i for v, i in zip(values, missing))
                images = [(sum(1 << ((d*i+s) % 11) for i in range(11) if marked >> i & 1),
                           sum(1 << ((d*i+s) % 11) for i in range(11) if odd >> i & 1))
                          for d in (-1, 1) for s in range(11)]
                classes[min(images)] += 1
    assert len(classes) == 88 and sum(classes.values()) == 1563
    return [{'marked_mask': m, 'odd_cut_mask': o, 'labelled_patterns': n}
            for (m, o), n in sorted(classes.items())]


def boundary_record(rs):
    assert rejected(rs, MARKED)
    records = []
    for t in AUX:
        active = tuple(i for i, r in enumerate(rs) if (r & t).bit_count() == 1)
        hist, blocked, no_single, tested = Counter(), [], [], 0
        for matching, span in pairing_spans(active):
            escaping = []
            for bits in span:
                tested += 1
                after = tuple(r ^ t if bits >> i & 1 else r for i, r in enumerate(rs))
                if not rejected(after, MARKED):
                    escaping.append(bits.bit_count()//2)
            minimum = min(escaping, default=-1)
            hist[minimum] += 1
            if minimum != 1:
                no_single.append([list(ij) for ij in matching])
            if minimum == -1:
                blocked.append([list(ij) for ij in matching])
        records.append({'swap_pair': t, 'affected_ports': list(active),
                        'matchings': sum(hist.values()), 'subsets_checked': tested,
                        'minimum_trails_histogram': sorted(hist.items()),
                        'no_single_escape_pairings': no_single,
                        'fully_blocked_pairings': blocked})
    assert all(r['no_single_escape_pairings'] for r in records)
    return {'word': list(rs), 'marked_cuts': list(MARKED), 'swaps': records}


def seed(kind, rs, table, fibers):
    cycles = [list(range(11)), list(range(11, 22))]
    base = [(c[i], c[(i+1) % 11]) for c in cycles for i in range(11)]
    base += [(i, i+11) for i in range(11)]
    g = build(22, base, cycles, kind)
    quotient_flow(g, [1]*9+[2, 3])
    letters = [[rs[j['edges'][-1]], 15] for j in g['junctions']]
    support, _ = quotient_assignment(g, letters, table)
    hf = [2*int(a)+(support >> i & 1) for i, a in enumerate(g['quotient_four_flow_word'])]
    values = dict(zip(g['kept_edge_ids'], hf))
    for block in g['blocks']:
        es = block['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    g['initial_flow_word'] = word(values[e] for e in range(len(g['edges'])))
    g['rejected_core_cover_word'] = word(PAIRS.index(a) for a in rs)
    return g


def regions_for(g):
    core = contracted(g)
    regions = []
    for offset, cycle in zip((0, 11), g['selected_cycles']):
        js = g['junctions'][offset:offset+11]
        hs = [2*j['edges'][-1]+g['edges'][j['edges'][-1]].index(j['vertex']) for j in js]
        regions.append({'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                        'marked_cuts': list(MARKED), 'critical': True,
                        'junction_indices': list(range(offset, offset+11))})
    return regions


def terminal_trails(core, regions, pairs, t, matching):
    target, other = regions
    mate = {}
    for i, j in matching:
        a, b = other['incidences'][i], other['incidences'][j]
        mate[a], mate[b] = b, a
    for v in range(core['vertices']):
        if v in (target['hub'], other['hub']):
            continue
        hs = [2*e+s for e, uv in enumerate(core['edges']) for s, w in enumerate(uv)
              if w == v and (pairs[e] & t).bit_count() == 1]
        assert len(hs) % 2 == 0
        for a, b in zip(hs[::2], hs[1::2]):
            mate[a], mate[b] = b, a
    terminals = {h: i for i, h in enumerate(target['incidences']) if (pairs[h//2] & t).bit_count() == 1}
    used, trails = set(), []
    for start in sorted(terminals, key=terminals.get):
        if start in used:
            continue
        h, path = start, []
        while True:
            path.append(h)
            h ^= 1
            if h in terminals:
                break
            h = mate[h]
            assert len(path) <= len(pairs)
        used.update((start, h))
        trails.append({'ports': [terminals[start], terminals[h]], 'incidences': path})
    assert sorted(tuple(sorted(r['ports'])) for r in trails) == sorted(tuple(p) for p in matching)
    return trails


def exchanged(pairs, t, trails, selected):
    es = [h//2 for i in selected for h in trails[i]['incidences']]
    assert len(es) == len(set(es))
    return [r ^ t if e in es else r for e, r in enumerate(pairs)]


def full_example(kind, name, attached, local, table, fibers, domains, witnesses):
    g, initial, original = example_seed(seed(kind, WORDS[name], table, fibers), attached)
    core, regions = contracted(g), regions_for(g)
    trials = []
    if name == 'two_trails':
        t, matching = 18, [[0, 1], [2, 4], [5, 6], [7, 10]]
    else:
        for rec in local['swaps']:
            matching = rec['fully_blocked_pairings'][0]
            trials.append({'swap_pair': rec['swap_pair'], 'outside_matching': matching,
                           'trails': terminal_trails(core, regions, original, rec['swap_pair'], matching)})
        t, matching = 6, [[2, 7], [6, 8], [9, 10]]
    trails = terminal_trails(core, regions, original, t, matching)
    options = []
    for n in range(1, len(trails)+1):
        for selected in itertools.combinations(range(len(trails)), n):
            changed = exchanged(original, t, trails, selected)
            if not bad_regions(regions, changed):
                options.append((selected, changed))
        if options:
            break
    selected, changed = options[0]
    assert len(selected) == (2 if name == 'two_trails' else 1)
    g.update({'name': name, 'core': core, 'regions': regions, 'profile_names': [name]*2,
              'pairing_trials': trials,
              'core_exchange': {'swap_pair': t, 'outside_matching': matching, 'trails': trails,
                                'selected_trails': list(selected), 'bad_before': [0, 1], 'bad_after': [],
                                'cover_word_after': word(PAIRS.index(a) for a in changed)}})
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
    local = {name: boundary_record(rs) for name, rs in WORDS.items()}
    assert all(r['fully_blocked_pairings'] for r in local['blocked_unions']['swaps'])
    assert [r['swap_pair'] for r in local['two_trails']['swaps'] if not r['fully_blocked_pairings']] == [18]
    result = {'date': '2026-10-05',
              'scope': 'The universal auxiliary escape lemma fails at length eleven, even with arbitrary unions of paired trails. The conditional completion theorem remains proved only through length ten; all full graph examples below have positive completions.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE/name).read_bytes()).hexdigest()}
                          for name in ('ten_cycle_completion.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'pattern_classification': classification(), 'local_witnesses': local, 'examples': []}
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE/'triangle_quotient_reduction.json').read_text())['petersen']
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        for name in WORDS:
            for attached in (None, pet):
                g = full_example(kind, name, attached, local[name], table, fibers, domains, witnesses)
                result['examples'].append(g)
                print(kind, name, g['vertices'], 'vertices;', len(g['core_exchange']['selected_trails']),
                      'selected trails;', len(g['moves']), 'B pentagons', flush=True)
    (HERE/'eleven_cycle_obstruction.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved two local witnesses and eight positive full graph completions.')


if __name__ == '__main__':
    main()
