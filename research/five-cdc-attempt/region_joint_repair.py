#!/usr/bin/env python3
"""Joint extension and core-preserving regional flow repair, at any length.

Standard-library constructor. See region-joint-repair.md for general proofs;
the independent verifier imports none of these constructors.
"""
from collections import defaultdict, deque, Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from short_cycle_boundary import local_table, cap, EVEN
from joint_boundary_completion import (
    PAIRS, INTERNAL, PENTAGONS, joint_repair, load_covers, masks_and_flows, word,
)

HERE = Path(__file__).parent


def joint_table(kind):
    covers, _ = local_table(kind)
    flows = {}
    for a, b, c, d in itertools.product(range(1, 8), repeat=4):
        r = a ^ b ^ c ^ d
        if not r or (kind == 'semi' and b != d):
            continue
        if kind == 'blowup' and (a == c or b == d):
            continue
        z = (a & 1)+2*(b & 1)+4*(c & 1)+8*(d & 1)
        values = [a, b, c, d]+([a ^ c, b ^ d] if kind == 'blowup' else [])+[r]
        flows.setdefault((r, z, a ^ b), values)
    joint = {}
    for (p, z, h), flow in sorted(flows.items()):
        for (r, z1), witnesses in sorted(covers.items()):
            if z1 == z:
                for charge, cover in sorted(witnesses.items()):
                    joint.setdefault((p, r, h, charge), (flow, cover))
    expected = {(p, r, h, charge) for p in range(1, 8) for r in PAIRS
                for h in range(8) for charge in EVEN
                if (p & 1) == (r & 1) and (h & 1) == (charge & 1)}
    assert set(joint) == expected and len(joint) == 2176
    return joint


def joint_quotient(g, core_flow, core_cover, table, initial_charges=None):
    f = dict(enumerate(core_flow))
    c = {e: PAIRS[int(a)] for e, a in enumerate(core_cover)}
    offset = 0
    for j, cycle in enumerate(g['selected_cycles']):
        hf, hc = (0, 0) if initial_charges is None else initial_charges[j]
        original = hf, hc
        for junction in g['junctions'][offset:offset+len(cycle)]:
            ids = junction['edges']
            p, r = f[ids[-1]], c[ids[-1]]
            fv, cv = table[p, r, hf, hc]
            for e, a, b in zip(ids, fv, cv):
                assert e not in f or f[e] == a
                assert e not in c or c[e] == b
                f[e], c[e] = a, b
            hf ^= p
            hc ^= r
        assert (hf, hc) == original
        offset += len(cycle)
    kept = g['kept_edge_ids']
    return [f[e] for e in kept], word(PAIRS.index(c[e]) for e in kept)


def small_cycle(edges, allowed):
    adjacency = defaultdict(list)
    for e in sorted(allowed):
        u, v = edges[e]
        adjacency[u].append((v, e))
        adjacency[v].append((u, e))
    for length in range(1, 5):
        for start in sorted(adjacency):
            def visit(v, seen, ids):
                for w, e in adjacency[v]:
                    if e in ids:
                        continue
                    if w == start and len(ids)+1 == length:
                        return ids+[e]
                    if len(ids)+1 < length and w not in seen:
                        found = visit(w, seen | {w}, ids+[e])
                        if found:
                            return found
                return None
            found = visit(start, {start}, [])
            if found:
                return found
    return None


def contract(edges, chosen):
    vertices = {v for e in chosen for v in edges[e]}
    root = min(vertices)
    return {e: tuple(root if v in vertices else v for v in uv)
            for e, uv in edges.items() if e not in chosen}


def contraction_plan(edges, core_count):
    current, plan = dict(enumerate(edges)), []
    while len(current) > core_count:
        chosen = small_cycle(current, set(current)-set(range(core_count)))
        assert chosen is not None
        plan.append(chosen)
        current = contract(current, chosen)
    return plan


def path_in_edges(edges, selected, start, goal, flow=None, avoid=None):
    before, todo = {start: None}, deque([start])
    while todo and goal not in before:
        v = todo.popleft()
        for e in selected:
            if flow is not None and flow[e] == avoid:
                continue
            u, w = edges[e]
            if v not in (u, w):
                continue
            neighbor = w if v == u else u
            if neighbor not in before:
                before[neighbor] = (v, e)
                todo.append(neighbor)
    if goal not in before:
        return None
    result, at = [], goal
    while at != start:
        at, e = before[at]
        result.append(e)
    return list(reversed(result))


def apply(flow, ids, increment):
    for e in ids:
        assert flow[e] != increment
        flow[e] ^= increment


def reconfigure(edges, first, target, plan):
    """Lift a contraction recursion; global edge IDs never change."""
    if not plan:
        assert first == target
        return []
    chosen = plan[0]
    reduced = contract(edges, chosen)
    f = first.copy()
    smaller = reconfigure(reduced, {e: f[e] for e in reduced},
                          {e: target[e] for e in reduced}, plan[1:])
    vertices = {v for e in chosen for v in edges[e]}
    moves = []
    for move in smaller:
        a, ids = move['increment'], move['edges']
        ends = [v for e in ids for v in edges[e] if v in vertices]
        assert len(ends) in (0, 2)
        path = [] if not ends else path_in_edges(edges, chosen, *ends)
        assert path is not None
        t = next(t for t in range(8)
                 if all(f[e] != t for e in chosen) and all(f[e] ^ t != a for e in path))
        if t and path:
            apply(f, chosen, t)
            moves.append({'edges': chosen.copy(), 'increment': t})
        lifted = ids+path
        apply(f, lifted, a)
        moves.append({'edges': lifted, 'increment': a})
    differences = {f[e] ^ target[e] for e in chosen}
    assert len(differences) == 1
    a = differences.pop()
    if a:
        apply(f, chosen, a)
        moves.append({'edges': chosen.copy(), 'increment': a})
    assert f == target
    return moves


def lift_through_pieces(g, initial, quotient_moves):
    flow, moves = initial.copy(), []
    local_edges = dict(enumerate(INTERNAL))
    ports = [4, 5, 2, 6]
    for move in quotient_moves:
        ids = [g['kept_edge_ids'][e] for e in move['edges']]
        lifted, a = ids.copy(), move['increment']
        for i, block in enumerate(g['blocks']):
            es = block['edge_representatives']
            selected = [j for j, e in enumerate(es[10:]) if e in ids]
            if not selected:
                continue
            assert len(selected) == 2
            local = {j: flow[e] for j, e in enumerate(es[:10])}
            endpoints = [ports[j] for j in selected]
            path = path_in_edges(local_edges, range(10), *endpoints, local, a)
            if path is None:
                for mask, increment in itertools.product(PENTAGONS, range(1, 8)):
                    cs = [e for e in range(10) if mask >> e & 1]
                    if any(local[e] == increment for e in cs):
                        continue
                    after = local.copy()
                    apply(after, cs, increment)
                    path = path_in_edges(local_edges, range(10), *endpoints, after, a)
                    if path is not None:
                        chosen = [es[e] for e in cs]
                        apply(flow, chosen, increment)
                        moves.append({'kind': 'piece_preparation', 'piece': i,
                                      'edges': chosen, 'increment': increment})
                        break
                assert path is not None
            lifted.extend(es[e] for e in path)
        apply(flow, lifted, a)
        moves.append({'kind': 'lifted_quotient', 'edges': lifted, 'increment': a})
    return flow, moves


def finish(g, flow, qc, fibers, domains, witnesses):
    flow, cover, moves = flow.copy(), ['?']*len(flow), []
    pairs = dict(zip(g['kept_edge_ids'], map(int, qc)))
    for e, c in pairs.items():
        cover[e] = str(c)
    for i, block in enumerate(g['blocks']):
        es = block['edge_representatives']
        rec = joint_repair([flow[e] for e in es], 1, [pairs[e] for e in es[10:]],
                           fibers, domains, witnesses)
        for move in rec['moves']:
            ids = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            apply(flow, ids, move['increment'])
            moves.append({'kind': 'piece_completion', 'piece': i, 'edges': ids,
                          'increment': move['increment']})
        for e, c in zip(es[:10], rec['cover_word'][:10]):
            cover[e] = c
    assert '?' not in cover
    return flow, ''.join(cover), moves


def cap_examples(kind, table, rng):
    alphabet = [(p, r) for p in range(1, 8) for r in PAIRS if (p & 1) == (r & 1)]
    result = []
    for k in (3, 4, 5, 7, 8, 9, 16, 31, 64):
        while True:
            boundary = [rng.choice(alphabet) for _ in range(k-1)]
            p = r = 0
            for a, b in boundary:
                p ^= a
                r ^= b
            if (p, r) in alphabet:
                boundary.append((p, r))
                break
        charges = rng.choice([(h, c) for h in range(8) for c in EVEN if h & 1 == c & 1])
        g = cap(kind, k)
        f, cw = joint_quotient(g, [a for a, _ in boundary], word(PAIRS.index(b) for _, b in boundary), table, [charges])
        result.append({'length': k, 'vertices': g['quotient_vertices'], 'edges': g['quotient_edges'],
                       'flow_word': word(f), 'cover_word': cw, 'initial_charges': charges,
                       'contractions': contraction_plan(g['quotient_edges'], k)})
    return result


def short_cycle_audit():
    result = []
    for size in (2, 3, 4):
        histogram = Counter()
        for values in itertools.product(range(1, 8), repeat=size):
            for start in range(size):
                for length in range(1, size//2+1):
                    path = [(start+j) % size for j in range(length)]
                    for a in range(1, 8):
                        allowed = [t for t in range(8) if t not in values
                                   and all(values[e] ^ t != a for e in path)]
                        assert allowed
                        histogram[len(allowed), int(0 not in allowed)] += 1
        result.append({'cycle_length': size, 'cases': sum(histogram.values()),
                       'allowed_count_preparation_histogram': [[*key, count] for key, count in sorted(histogram.items())]})
    return result


def main():
    source = HERE / 'short_cycle_boundary.json'
    previous = json.loads(source.read_text())
    _, fibers = masks_and_flows()
    domains, witnesses = load_covers()
    rng = random.Random(20260930)
    result = {'date': '2026-09-30',
              'scope': 'Arbitrary-length joint region extension and repair preserving all core-edge flow values. Regional layer membership may change. Fixed-layer existential equivalence beyond length seven remains unresolved.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                          for name in (source.name, 'joint_boundary_completion.json', 'petersen_flow_repair.json')],
              'junctions': {}, 'caps': {}, 'repairs': [],
              'short_cycle_audit': short_cycle_audit()}
    for kind in ('blowup', 'semi'):
        table = joint_table(kind)
        result['junctions'][kind] = [[*key, fv, cv] for key, (fv, cv) in sorted(table.items())]
        result['caps'][kind] = cap_examples(kind, table, rng)
        g = next(g for g in previous['cubic_examples'] if g['construction'] == kind)
        initial = list(map(int, g['initial_flow_word']))
        m = len(g['outside_base_edge_ids'])
        qf, qc = joint_quotient(g, initial[:m], g['rejected_core_cover_word'], table)
        plan = contraction_plan(g['quotient_edges'], m)
        old_qf = [initial[e] for e in g['kept_edge_ids']]
        qm = reconfigure(dict(enumerate(g['quotient_edges'])), dict(enumerate(old_qf)), dict(enumerate(qf)), plan)
        flow, moves = lift_through_pieces(g, initial, qm)
        assert [flow[e] for e in g['kept_edge_ids']] == qf
        flow, cover, final_moves = finish(g, flow, qc, fibers, domains, witnesses)
        moves += final_moves
        assert flow[:m] == initial[:m] and cover[:m] == g['rejected_core_cover_word']
        result['repairs'].append({'construction': kind, 'source_example': kind,
                                  'core_cover_word': g['rejected_core_cover_word'], 'normal': 1,
                                  'target_quotient_flow_word': word(qf), 'quotient_cover_word': qc,
                                  'contractions': plan, 'quotient_moves': qm, 'moves': moves,
                                  'final_flow_word': word(flow), 'cover_word': cover})
        print(kind, '2176 joint states;', len(qm), 'quotient switches;',
              dict(Counter(m['kind'] for m in moves)), flush=True)
    (HERE / 'region_joint_repair.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved joint extension tables, 18 cap certificates through length 64, and two core-preserving repairs.')


if __name__ == '__main__':
    main()
