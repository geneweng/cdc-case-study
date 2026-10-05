#!/usr/bin/env python3
"""Fixed-layer completion with at most one eight-cycle region.

Standard library only. Produces a finite boundary lemma and six full graph
certificates. The independent verifier imports none of this code.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from fourflow_quotient_repair import build, contracted, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from short_cycle_boundary import EVEN, filter_word, left_bit, local_table, quotient_assignment

HERE = Path(__file__).parent
AUX = [r for r in PAIRS if not r & 1]
SPACE = [h for h in EVEN if not h & 1]


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def prefixes(rs):
    result, at = [], 0
    for r in rs:
        result.append(at)
        at ^= r
    assert at == 0
    return result


def marked_test(letters):
    """A cut before junction i is marked by either adjoining F-port pair."""
    rs = [r for r, _ in letters]
    pref = prefixes(rs)
    p = left_bit(letters[0][1])
    marked = [i for i, (_, z) in enumerate(letters)
              if z & 3 == 3 or letters[i-1][1] & 12 == 12]
    forbidden = {30 ^ pref[i] for i in marked}
    candidates = {h for h in EVEN if h & 1 == p}
    assert forbidden <= candidates
    return marked, sorted(candidates-forbidden)


def local_audit(kind, table, count):
    rows = []
    for (r, z), allowed in sorted(table.items()):
        excluded = ({30} if z & 3 == 3 else set()) | ({30 ^ r} if z & 12 == 12 else set())
        candidates = {h for h in EVEN if h & 1 == left_bit(z)}
        assert set(allowed) == candidates-excluded
        rows.append([r, z, sorted(allowed)])
    return {'assignments': count, 'keys': len(table), 'relation_sha256': digest(rows)}


def hamiltonian_words():
    def visit(path):
        if len(path) == 8:
            if path[-1] in AUX:
                yield tuple(path[i] ^ path[(i+1) % 8] for i in range(8))
            return
        for v in SPACE:
            if v not in path and v ^ path[-1] in AUX:
                yield from visit(path+[v])
    return sorted(visit([0]))


def matchings(xs):
    if not xs:
        yield []
    else:
        for j in range(1, len(xs)):
            for rest in matchings(xs[1:j]+xs[j+1:]):
                yield [(xs[0], xs[j])]+rest


def pair_data(rs, t):
    pref = prefixes(rs)
    affected = [i for i, r in enumerate(rs) if (r & t).bit_count() == 1]
    safe = []
    for i, j in itertools.combinations(affected, 2):
        arc = set(pref[i+1:j+1])
        if {h ^ t for h in arc} == arc:
            safe.append((i, j))
    matching_count, safe_count = 0, 0
    for matching in matchings(affected):
        matching_count += 1
        safe_count += all(ij in safe for ij in matching)
    return affected, safe, matching_count, safe_count


def choose_pair(rs):
    options = []
    for t in AUX:
        affected, safe, total, safe_count = pair_data(rs, t)
        if not safe_count:
            options.append((len(safe), -len(affected), t, affected, safe, total))
    _, _, t, affected, safe, total = min(options)
    return t, affected, safe, total


def relabel(mask, permutation):
    return sum(1 << permutation[i-1] for i in range(1, 5) if mask >> i & 1)


def canonical(rs):
    return min(tuple(relabel(r, p) for r in rr[s:]+rr[:s])
               for p in itertools.permutations(range(1, 5))
               for rr in (rs, rs[::-1]) for s in range(8))


def boundary_audit():
    words = hamiltonian_words()
    classes, histogram, records = Counter(), Counter(), []
    tested_matchings = 0
    for rs in words:
        classes[canonical(rs)] += 1
        data = [pair_data(rs, t) for t in AUX]
        forcing = sum(d[3] == 0 for d in data)
        histogram[forcing] += 1
        records.append([list(rs), [d[3] for d in data]])
        t, affected, safe, total = choose_pair(rs)
        assert len(safe) <= 1 and len(affected) >= 4
        tested_matchings += total
        for matching in matchings(affected):
            i, j = next(ij for ij in matching if ij not in safe)
            changed = list(rs)
            changed[i] ^= t
            changed[j] ^= t
            assert all(r in AUX for r in changed) and len(set(prefixes(changed))) < 8
    representatives = []
    for rs, size in sorted(classes.items()):
        t, affected, safe, total = choose_pair(rs)
        representatives.append({'boundary_pairs': list(rs), 'orbit_size': size,
                                'swap_pair': t, 'affected_ports': affected,
                                'non_escaping_pairs': [list(ij) for ij in safe],
                                'outside_pairings_checked': total})
    assert len(words) == 1488 and len(classes) == 11
    return {'words': len(words), 'orbits': representatives,
            'forcing_pair_histogram': sorted(histogram.items()),
            'safe_matching_counts_sha256': digest(records),
            'chosen_pair_matchings_checked': tested_matchings}


def core_swap(core, core_pairs, hub, stems):
    """Find a simple auxiliary-layer Kempe circuit through the eight-port hub."""
    rs = [core_pairs[e] for e in stems]
    assert len(set(prefixes(rs))) == 8
    t, affected, safe, _ = choose_pair(rs)
    edges = core['edges']
    adjacency = [[] for _ in range(core['vertices'])]
    for e, (u, v) in enumerate(edges):
        if hub not in (u, v) and (core_pairs[e] & t).bit_count() == 1:
            adjacency[u].append((v, e))
            adjacency[v].append((u, e))
    for i, j in itertools.combinations(affected, 2):
        if (i, j) in safe:
            continue
        ei, ej = stems[i], stems[j]
        if ei == ej:
            assert edges[ei] == [hub, hub]
            circuit = [ei]
        else:
            if edges[ei] == [hub, hub] or edges[ej] == [hub, hub]:
                continue
            u = next(v for v in edges[ei] if v != hub)
            v = next(v for v in edges[ej] if v != hub)
            parent, todo = {u: None}, deque([u])
            while todo and v not in parent:
                at = todo.popleft()
                for following, e in adjacency[at]:
                    if following not in parent:
                        parent[following] = (at, e)
                        todo.append(following)
            if v not in parent:
                continue
            circuit = [ej]
            while v != u:
                v, e = parent[v]
                circuit.append(e)
            circuit.append(ei)
        changed = core_pairs.copy()
        for e in circuit:
            changed[e] ^= t
        assert len(set(prefixes([changed[e] for e in stems]))) < 8
        return {'swap_pair': t, 'edges': sorted(circuit), 'ports': [i, j]}, changed
    raise AssertionError('The finite pairing lemma guarantees a circuit')


def transfer_initial(old, g, outside):
    oldf = list(map(int, old['initial_flow_word']))
    values = dict(enumerate(outside))
    for ob, nb in zip(old['blocks'], g['blocks']):
        for oe, ne in zip(ob['edge_representatives'][:10], nb['edge_representatives'][:10]):
            values[ne] = oldf[oe]
    for oj, nj in zip(old['junctions'], g['junctions']):
        for oe, ne in zip(oj['edges'][:-1], nj['edges'][:-1]):
            values[ne] = oldf[oe]
    return [values[e] for e in range(len(g['edges']))]


def example_seed(old, pet=None):
    kind = old['construction']
    original_pairs = [PAIRS[int(d)] for d in old['rejected_core_cover_word']]
    if pet is None:
        g = build(old['base_vertices'], old['base_edges'], old['selected_cycles'], kind)
        initial = list(map(int, old['initial_flow_word']))
        g['core_has_four_flow'] = True
        g['core_four_flow_word'] = old['contracted_base']['four_flow_word']
    else:
        # Two-edge sum along bottom rim edge 0 and a non-F Petersen edge.
        pc = [PAIRS[int(d)] for d in pet['positive_covers'][0]['cover_word']]
        pe = next(e for e, a in enumerate(pc) if not a & 1)
        permutation = next(p for p in itertools.permutations(range(1, 5))
                           if relabel(pc[pe], p) == original_pairs[0])
        pc = [(a & 1) | relabel(a & 30, permutation) for a in pc]
        vectors = [1, 0, 2, 4, 6]
        pf = [0]*len(pc)
        for e, a in enumerate(pc):
            for i in range(5):
                if a >> i & 1:
                    pf[e] ^= vectors[i]
        oldf = list(map(int, old['initial_flow_word']))
        linear = next(p for p in itertools.permutations((1, 2, 3)) if 2*p[pf[pe]//2-1] == oldf[0])
        pf = [(a & 1) + (2*linear[a//2-1] if a//2 else 0) for a in pf]
        be = old['outside_base_edge_ids'][0]
        u, v = old['base_edges'][be]
        x, y = pet['edges'][pe]
        n = old['base_vertices']
        base = [uv for e, uv in enumerate(old['base_edges']) if e != be]
        base += [[n+a, n+b] for e, (a, b) in enumerate(pet['edges']) if e != pe]
        base += [[u, n+x], [v, n+y]]
        g = build(n+10, base, old['selected_cycles'], kind)
        outside = oldf[1:len(original_pairs)]+[a for e, a in enumerate(pf) if e != pe]+[oldf[0]]*2
        initial = transfer_initial(old, g, outside)
        original_pairs = original_pairs[1:]+[a for e, a in enumerate(pc) if e != pe]+[original_pairs[0]]*2
        g['core_has_four_flow'] = False
        g['petersen_two_sum'] = {'vertices': list(range(n, n+10)), 'removed_edge': [n+x, n+y],
                                 'core_cut_edges': [len(original_pairs)-2, len(original_pairs)-1],
                                 'petersen_edges': pet['edges']}
    return g, initial, original_pairs


def loop_seed(kind, table, fibers):
    base = [(i, (i+1) % 8) for i in range(8)]+[(i, i+4) for i in range(4)]
    g = build(8, base, [list(range(8))], kind)
    quotient_flow(g, [1]*4)
    core_pairs = [6, 10, 6, 18]
    letters = [[core_pairs[j['edges'][-1]], 15] for j in g['junctions']]
    support, _ = quotient_assignment(g, letters, table)
    hf = [2*int(a)+(support >> i & 1) for i, a in enumerate(g['quotient_four_flow_word'])]
    values = dict(zip(g['kept_edge_ids'], hf))
    for block in g['blocks']:
        es = block['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    g['initial_flow_word'] = word(values[e] for e in range(len(g['edges'])))
    g['rejected_core_cover_word'] = word(PAIRS.index(a) for a in core_pairs)
    return g


def complete_example(old, pet, table, fibers, domains, witnesses):
    g, initial, original = example_seed(old, pet)
    core = contracted(g)
    hub = core['vertex_map'][g['selected_cycles'][0][0]]
    stems = [j['edges'][-1] for j in g['junctions']]
    letters = [[original[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))]
               for j in g['junctions']]
    marked, allowed = marked_test(letters)
    assert marked == list(range(8)) and not allowed and not filter_word(table, letters)[-1]
    move, changed = core_swap(core, original, hub, stems)
    changed_letters = [[changed[j['edges'][-1]], z] for j, (_, z) in zip(g['junctions'], letters)]
    _, allowed = marked_test(changed_letters)
    assert allowed == filter_word(table, changed_letters)[-1]
    h, prefix, pairs = min(allowed), 0, dict(enumerate(changed))
    for j, (r, z) in zip(g['junctions'], changed_letters):
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
        for m in repair['moves']:
            selected = [es[j] for j in range(10) if m['circuit_mask'] >> j & 1]
            moves.append({'piece': i, 'edges': selected, 'increment': m['increment']})
            for e in selected:
                flow[e] ^= m['increment']
        for e, a in zip(es[:10], repair['cover_word'][:10]):
            cover[e] = a
    g.update({'core': core, 'hub': hub, 'core_stems': stems, 'letters': letters,
              'marked_cuts': marked, 'initial_flow_word': word(initial),
              'original_core_cover_word': word(PAIRS.index(a) for a in original),
              'core_cover_swap': move, 'changed_core_cover_word': word(PAIRS.index(a) for a in changed),
              'changed_letters': changed_letters, 'surviving_charges': allowed, 'chosen_charge': h,
              'quotient_cover_word': word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids']),
              'moves': moves, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    return g


def main():
    old = json.loads((HERE / 'short_cycle_boundary.json').read_text())
    pet = json.loads((HERE / 'triangle_quotient_reduction.json').read_text())['petersen']
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    result = {'date': '2026-10-05',
              'scope': 'Prescribed-layer completion is equivalent to core completion when at most one selected cycle has length eight and all others have lengths three through seven. The core cover may change; the quotient layer stays fixed. Multiple eight-cycles, longer cycles, and the general 5-CDC conjecture are not resolved.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                          for name in ('short_cycle_boundary.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'local_relations': {}, 'boundary_lemma': boundary_audit(), 'examples': []}
    for kind in ('blowup', 'semi'):
        table, count = local_table(kind)
        result['local_relations'][kind] = local_audit(kind, table, count)
        seed = next(g for g in old['cubic_examples'] if g['construction'] == kind)
        for attached in (None, pet):
            g = complete_example(seed, attached, table, fibers, domains, witnesses)
            result['examples'].append(g)
            print(kind, g['vertices'], 'vertices; core four-flow:', g['core_has_four_flow'],
                  '; core cover circuit:', g['core_cover_swap']['edges'], '; B switches:', len(g['moves']), flush=True)
        g = complete_example(loop_seed(kind, table, fibers), None, table, fibers, domains, witnesses)
        result['examples'].append(g)
        assert len(g['core_cover_swap']['edges']) == 1
        print(kind, g['vertices'], 'vertices; one-loop core cover exchange; B switches:', len(g['moves']), flush=True)
    (HERE / 'eight_cycle_completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved 1,488 boundary words in 11 orbits and six fixed-layer completions.')


if __name__ == '__main__':
    main()
