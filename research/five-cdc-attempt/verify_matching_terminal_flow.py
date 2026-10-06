#!/usr/bin/env python3
"""Independent verification by circuit enumeration; no max-flow or constructor imports."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(rows):
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


class Graph:
    def __init__(self,g):
        self.name, self.n, self.edges = g['name'], g['vertices'], g['edges']
        self.m = len(self.edges)
        self.full = (1 << self.m)-1
        self.adj = [[(e,v if u == w else u) for e,(u,v) in enumerate(self.edges) if w in (u,v)]
                    for w in range(self.n)]
        assert all(len(es) == 3 for es in self.adj)
        assert all(u != v for u,v in self.edges)
        assert len({tuple(sorted(e)) for e in self.edges}) == self.m
        self.cycles = []
        for code in range(1 << len(g['cycle_basis'])):
            mask = 0
            for k,b in enumerate(g['cycle_basis']):
                if code >> k & 1: mask ^= b
            assert all(sum((mask >> e)&1 for e,_ in es)%2 == 0 for es in self.adj)
            self.cycles.append(mask)
        assert len(set(self.cycles)) == 1 << (self.m-self.n+1)
        assert len(self.components(self.full)) == 1
        self.parts = [self.circuit_orders(L) for L in self.cycles]
        self.covered = [sum(1 << v for v in {v for order in orders for v in order}) for orders in self.parts]

    def endpoints(self,M):
        ends = [v for e,edge in enumerate(self.edges) if M >> e & 1 for v in edge]
        assert len(ends) == len(set(ends))
        return sum(1 << v for v in ends)

    def components(self,mask):
        unseen = set(range(self.n))
        out = []
        while unseen:
            v = min(unseen); unseen.remove(v); queue = [v]
            for u in queue:
                for e,w in self.adj[u]:
                    if mask >> e & 1 and w in unseen:
                        unseen.remove(w); queue.append(w)
            out.append(sum(1 << u for u in queue))
        return out

    def cut(self,A):
        return sum((bool(A >> u & 1) != bool(A >> v & 1)) << e for e,(u,v) in enumerate(self.edges))

    def circuit_orders(self,L):
        remaining = {e for e in range(self.m) if L >> e & 1}
        orders = []
        while remaining:
            first = min(remaining); remaining.remove(first)
            start,at = self.edges[first]; order = [start]
            while at != start:
                order.append(at)
                choices = [(e,w) for e,w in self.adj[at] if e in remaining]
                assert len(choices) == 1
                e,at = choices[0]; remaining.remove(e)
            orders.append(order)
        return orders

    @lru_cache(None)
    def feasible_signings(self,M):
        """Alternate terminal signs on all eligible circuit unions."""
        D = self.endpoints(M)
        if not D: return frozenset({0})
        out = set()
        for L,orders,covered in zip(self.cycles,self.parts,self.covered):
            if M & L or covered & D != D: continue
            choices = {0}
            for order in orders:
                terminals = [v for v in order if D >> v & 1]
                if len(terminals)%2:
                    choices = set(); break
                if terminals:
                    even = sum(1 << v for v in terminals[::2])
                    odd = sum(1 << v for v in terminals[1::2])
                    choices = {S | part for S in choices for part in (even,odd)}
            out.update(S for S in choices if S & (D & -D))
        return frozenset(out)

    def signings(self,M):
        D = self.endpoints(M)
        vs = [v for v in range(self.n) if D >> v & 1]
        return [0] if not vs else [sum(1 << v for v in (vs[0],)+rest) for rest in combinations(vs[1:],len(vs)//2-1)]

    def detail(self,record):
        M = record['matching']; D = self.endpoints(M)
        good = self.feasible_signings(M)
        assert record['repairable'] == bool(good)
        assert [r['sources'] for r in record['signings']] == self.signings(M)
        for r in record['signings']:
            S = r['sources']; N = D ^ S
            assert r['target'] == D.bit_count()
            divergence = [0]*self.n
            assert len(r['net_flow']) == self.m
            for e,((u,v),x) in enumerate(zip(self.edges,r['net_flow'])):
                assert x in (-1,0,1) and (not (M >> e & 1) or x == 0)
                divergence[u] += x; divergence[v] -= x
            assert all(0 <= divergence[v] <= 2 if S >> v & 1 else
                       -2 <= divergence[v] <= 0 if N >> v & 1 else divergence[v] == 0
                       for v in range(self.n))
            assert sum(divergence[v] for v in range(self.n) if S >> v & 1) == r['value']
            passes = r['value'] == r['target']
            assert passes == (S in good)
            if passes:
                L = sum((x != 0) << e for e,x in enumerate(r['net_flow']))
                F,t = (self.cycles[r[k]] for k in ('first_cycle','partner_cycle'))
                assert L == r['circuit_union'] == F ^ t and F & t == M
            else:
                A = r['cut_vertices']; boundary = self.cut(A) & ~M
                imbalance = (A & S).bit_count()-(A & N).bit_count()
                assert boundary == r['cut_edges']
                assert 2*imbalance-boundary.bit_count() == r['deficit'] == r['target']-r['value'] > 0

    def core_cuts(self):
        checked = 0
        for k in (1,2,3):
            for removed in combinations(range(self.m),k):
                pieces = self.components(self.full ^ sum(1 << e for e in removed))
                assert len(pieces) == 1 or (k == 3 and len(pieces) == 2 and min(K.bit_count() for K in pieces) == 1)
                checked += 1
        return checked


def audit(obj,matchings):
    rows, sizes = [], Counter()
    successes = 0
    for M in sorted(set(matchings)):
        feasible = obj.feasible_signings(M)
        successes += bool(feasible)
        for S in obj.signings(M):
            passes = int(S in feasible)
            rows.append([M,S,passes]); sizes[M.bit_count(),passes] += 1
    return {'matchings':len(set(matchings)), 'repairable_matchings':successes,
            'terminal_partitions':len(rows),'feasible_partitions':sum(r[2] for r in rows),
            'size_and_feasibility_histogram':[list(k)+[v] for k,v in sorted(sizes.items())],
            'partition_records_sha256':digest(rows)}


def state_planes(key):
    points = {0}
    for k in range(3): points |= {x ^ ((key >> (16*k)) & 65535) for x in list(points)}
    return [(a,b) for a,b in combinations(sorted(points-{0}),2) if a ^ b > b]


def key(rows):
    points = {0}
    for row in rows: points |= {x ^ row for x in list(points)}
    assert len(points) == 8
    ps = sorted(points)
    return ps[1] | (ps[2] << 16) | (ps[4] << 32)


def switches(obj,flow):
    rows, hist = [], Counter()
    original = [0]+[sum((x == b) << e for e,x in enumerate(flow)) for b in range(1,8)]
    for a in range(1,8):
        for C,parts in zip(obj.cycles,obj.parts):
            if len(parts) != 1 or C & original[a]: continue
            after = [x ^ a if C >> e & 1 else x for e,x in enumerate(flow)]
            ms = [sum((x == b) << e for e,x in enumerate(after)) for b in range(1,8)]
            assert all(sum(after[e] == b for e,_ in es) <= 1 for es in obj.adj for b in range(1,8))
            for b,M in enumerate(ms,1):
                Q = 0 if a == b else C & (original[b] | original[a ^ b])
                boundary = sum((sum((Q >> e)&1 for e,_ in es)%2) << v for v,es in enumerate(obj.adj))
                assert original[b] ^ Q == M
                assert obj.endpoints(M) == obj.endpoints(original[b]) ^ boundary
                if a != b:
                    assert M.bit_count()-original[b].bit_count() == (C & original[a ^ b]).bit_count()-(C & original[b]).bit_count()
            good = [b for b,M in enumerate(ms,1) if obj.feasible_signings(M)]
            minimum = min(M.bit_count() for M in ms)
            hist[minimum,len(good)] += 1; rows.append([a,C,minimum,good])
    initial = min(M.bit_count() for M in original[1:])
    return {'moves':len(rows),'matching_updates':7*len(rows),
            'moves_creating_repairable_matching':sum(bool(r[3]) for r in rows),
            'moves_lowering_smallest_class':sum(r[2] < initial for r in rows),
            'lowering_moves_without_repairable_matching':sum(r[2] < initial and not r[3] for r in rows),
            'size_and_good_count_histogram':[list(k)+[v] for k,v in sorted(hist.items())],
            'records_sha256':digest(rows)}


def verify_escape(obj,example,initial):
    assert example['initial_flow'] == initial
    flow = initial
    w = example['repair']
    before = example['first_switch']
    for move in [before]+w['moves']:
        C = sum(1 << e for e in move['edges']); a = move['increment']
        assert C in obj.cycles and len(obj.parts[obj.cycles.index(C)]) == 1
        assert all(x != a for e,x in enumerate(flow) if C >> e & 1)
        flow = [x ^ a if C >> e & 1 else x for e,x in enumerate(flow)]
        assert flow == move['flow_after']
        assert all(flow[es[0][0]] ^ flow[es[1][0]] ^ flow[es[2][0]] == 0 for es in obj.adj)
    assert w['initial_flow'] == before['flow_after']
    M = example['matching']; assert M.bit_count() == 2
    assert M == sum((x == w['increment']) << e for e,x in enumerate(before['flow_after']))
    obj.detail(example['terminal_certificate'])
    cert = next(r for r in example['terminal_certificate']['signings'] if r['sources'] == example['sources'])
    assert cert['value'] == 4 and cert['first_cycle'] == w['target_first_cycle'] and cert['partner_cycle'] == w['intersection_partner']
    F,t = obj.cycles[w['target_first_cycle']],obj.cycles[w['intersection_partner']]
    assert F & t == M
    assert all(len(obj.parts[obj.cycles.index(mask)]) == 1 for mask in (F,t))
    out = w['final_lift']; assert out['flow'] == flow
    forms = out['coordinate_functionals']; assert len(forms) == 3 and all(forms)
    assert len({0,*forms,forms[0]^forms[1],forms[0]^forms[2],forms[1]^forms[2],forms[0]^forms[1]^forms[2]}) == 8
    assert forms[2] == w['first_functional']
    a = w['increment']
    assert [(a & x).bit_count()%2 for x in forms] == [0,0,1]
    coordinates = [sum(((x & c).bit_count()%2) << e for e,c in enumerate(flow)) for x in forms]
    assert coordinates[2] == F
    old = sum(((forms[2] & x).bit_count()%2) << e for e,x in enumerate(w['initial_flow']))
    assert old ^ F == obj.cycles[w['difference_cycle_code']]
    fourth = t ^ coordinates[0] ^ coordinates[1]
    assert fourth == out['fourth_coordinate_mask'] and fourth in obj.cycles
    transformed = [sum(((x & c).bit_count()%2) << k for k,x in enumerate(forms)) for c in flow]
    assert transformed == out['transformed_flow']
    palette = [4,5,6,15,8]
    decode = {u ^ v:(1 << i) | (1 << j) for i,u in enumerate(palette) for j,v in enumerate(palette) if i < j}
    pairs = [decode[c+8*((fourth >> e)&1)] for e,c in enumerate(transformed)]
    assert pairs == out['cover_pairs'] and all(x.bit_count() == 2 for x in pairs)
    assert all(pairs[es[0][0]] ^ pairs[es[1][0]] ^ pairs[es[2][0]] == 0 for es in obj.adj)


def main():
    data = json.loads((HERE/'matching_terminal_flow.json').read_text())
    for source in data['sources']:
        assert hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256']
    old = json.loads((HERE/'flow_space_components.json').read_text())
    p = Graph(next(g for g in old['graphs'] if g['name'] == 'Petersen'))
    jg = next(g for g in old['graphs'] if g['name'] == 'Snark20_0'); j = Graph(jg)
    # Independently rebuild the original plane scopes.
    ps = [(a,b) for a in range(1,len(p.cycles)) for b in range(a+1,len(p.cycles))
          if a ^ b > b and any(F & (p.full & ~(p.cycles[a] | p.cycles[b])) == (p.full & ~(p.cycles[a] | p.cycles[b])) for F in p.cycles)]
    repair = jg['hard_flow_repair']; first = repair['initial_space']
    states = {first} | {r['target_space'] for r in repair['rounds']}
    for a,b in state_planes(first):
        M = j.full & ~(j.cycles[a] | j.cycles[b])
        states.update(key((a,b,z)) for z,F in enumerate(j.cycles) if F & M == M)
    js = [ab for state in states for ab in state_planes(state)]
    for obj,planes,name in ((p,ps,'petersen_audit'),(j,js,'flower_audit')):
        matchings = {obj.full & ~(obj.cycles[a] | obj.cycles[b]) for a,b in planes}
        assert audit(obj,matchings) == data[name]
        print(obj.name,': terminal signings agree with independent circuit enumeration.',flush=True)
    cut_tests = 0
    for g,row in zip(old['graphs'],data['two_edge_core_audits'],strict=True):
        obj = p if g['name'] == p.name else j if g['name'] == j.name else Graph(g)
        cut_tests += obj.core_cuts()
        rows = []
        for e,d in combinations(range(obj.m),2):
            if set(obj.edges[e]) & set(obj.edges[d]): continue
            M = (1 << e) | (1 << d); D = obj.endpoints(M)
            S = sum(1 << v for v in obj.edges[e])
            canonical = S if S & (D & -D) else D ^ S
            assert canonical in obj.feasible_signings(M)
            rows.append([M,S,1])
        assert row == {'graph':g['name'],'matchings':len(rows),'records_sha256':digest(rows)}
    print('All 2,940 two-edge core matchings and',cut_tests,'edge-deletion checks verified.',flush=True)
    path = json.loads((HERE/'matching_fiber_repair.json').read_text())['flower_path']
    for state,saved in zip(path,data['flower_path'],strict=True):
        assert state['space_key'] == saved['space_key']
        for matching,record in zip(state['matchings'],saved['matchings'],strict=True):
            assert matching['increment'] == record['increment']
            assert matching['matching_mask'] == record['matching']
            j.detail(record)
    assert switches(j,repair['initial_flow']) == data['flower_first_switches']
    verify_escape(j,data['flower_two_edge_escape'],repair['initial_flow'])
    for example in data['two_edge_counterexamples']+[data['core_three_edge_obstruction']]:
        obj = Graph(example['graph']); M = sum(1 << e for e in example['matching_edges'])
        flow = example['flow']; assert all(1 <= x <= 7 for x in flow)
        assert all(flow[es[0][0]] ^ flow[es[1][0]] ^ flow[es[2][0]] == 0 for es in obj.adj)
        assert sum((x == 4) << e for e,x in enumerate(flow)) == M
        H = obj.full ^ M
        assert len(obj.components(H)) == 1
        assert all(len(obj.components(H ^ (1 << e))) == 1 for e in range(obj.m) if H >> e & 1)
        assert all(sum(((obj.cycles[c] >> e)&1) << k for k,c in enumerate(example['flow_cycle_codes'])) == x for e,x in enumerate(flow))
        obj.detail(example['terminal_certificate']); assert not obj.feasible_signings(M)
        old_record = example['matching_certificate']; assert old_record['matching_mask'] == M and not old_record['repairable']
        D = obj.endpoints(M); B = ((1 << obj.n)-1) ^ D
        free = sum(1 << e for e,(u,v) in enumerate(obj.edges) if B >> u & 1 and B >> v & 1)
        odd = [K for K in obj.components(free) if K & B and K.bit_count()%2]
        assert odd == old_record['odd_unmatched_components']
        candidates = []
        for code,(L,covered,orders) in enumerate(zip(obj.cycles,obj.covered,obj.parts)):
            if M & L or covered & D != D: continue
            candidates.append(code)
            counts = [sum((D >> v)&1 for v in order) for order in orders]
            assert any(c%2 for c in counts)
            saved = next(r for r in old_record['candidate_even_subgraphs'] if r['cycle_code'] == code)
            assert counts == saved['matching_endpoint_counts']
        assert candidates == [r['cycle_code'] for r in old_record['candidate_even_subgraphs']]
        cuts = [{'vertices':A,'edges':obj.cut(A)} for A in range(1,1 << (obj.n-1))
                if obj.cut(A).bit_count() == 3 and 1 < A.bit_count() < obj.n-1]
        assert cuts == example['nontrivial_three_edge_cuts']
        if example is data['core_three_edge_obstruction']:
            assert obj.edges == p.edges and M.bit_count() == 3 and not cuts and candidates
        else:
            assert M.bit_count() == 2 and cuts
    print('All path network witnesses, deficient cuts, 4,270 matching updates, both two-edge obstructions, the three-edge Petersen obstruction, and the new flower cover verified.')


if __name__ == '__main__':
    main()
