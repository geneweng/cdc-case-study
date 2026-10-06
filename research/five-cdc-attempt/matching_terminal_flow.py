#!/usr/bin/env python3
"""Terminal max-flow certificates for matching repair; standard library only."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations
import hashlib
import json
from pathlib import Path

from matching_fiber_repair import Matching, cover_from_intersection, digest
from flow_space_components import circuit_components, cycle_basis
from fiber_cut_obstructions import planes

HERE = Path(__file__).resolve().parent
SOURCES = ['flow_space_components.json', 'matching_fiber_repair.json']


class TerminalFlow(Matching):
    def __init__(self, g):
        super().__init__(g)
        # The matrix network below is for the simple graphs in this audit.
        assert all(u != v for u,v in self.edges)
        assert len({tuple(sorted(e)) for e in self.edges}) == self.m

    def signings(self, M):
        D = self.endpoint_mask(M)
        vertices = [v for v in range(self.n) if D >> v & 1]
        if not vertices:
            return [0]
        return [sum(1 << v for v in (vertices[0],)+rest)
                for rest in combinations(vertices[1:], len(vertices)//2-1)]

    def network(self, M, S):
        """Edmonds--Karp with antisymmetric unit capacities on G-M."""
        D = self.endpoint_mask(M)
        assert S & D == S and 2*S.bit_count() == D.bit_count()
        source, sink = self.n, self.n+1
        size = self.n+2
        capacity = [[0]*size for _ in range(size)]
        for e, (u, v) in enumerate(self.edges):
            if not M >> e & 1:
                capacity[u][v] += 1
                capacity[v][u] += 1
        for v in range(self.n):
            if S >> v & 1:
                capacity[source][v] = 2
            elif D >> v & 1:
                capacity[v][sink] = 2
        residual = [row[:] for row in capacity]
        value = 0
        while True:
            previous = [-1]*size
            previous[source] = source
            queue = deque([source])
            while queue and previous[sink] < 0:
                u = queue.popleft()
                for v in range(size):
                    if residual[u][v] and previous[v] < 0:
                        previous[v] = u
                        queue.append(v)
            if previous[sink] < 0:
                break
            amount, v = 2, sink
            while v != source:
                u = previous[v]
                amount = min(amount, residual[u][v])
                v = u
            v = sink
            while v != source:
                u = previous[v]
                residual[u][v] -= amount
                residual[v][u] += amount
                v = u
            value += amount
        target = D.bit_count()
        net = [0 if M >> e & 1 else capacity[u][v]-residual[u][v]
               for e, (u, v) in enumerate(self.edges)]
        assert all(x in (-1, 0, 1) for x in net)
        record = {'sources': S, 'value': value, 'target': target, 'net_flow': net}
        if value < target:
            A = sum(1 << v for v in range(self.n) if previous[v] >= 0)
            boundary = self.cut(A) & ~M
            imbalance = (A & S).bit_count() - (A & (D ^ S)).bit_count()
            deficit = 2*imbalance-boundary.bit_count()
            assert deficit == target-value > 0
            record.update(cut_vertices=A, cut_edges=boundary, deficit=deficit)
        else:
            L = sum((x != 0) << e for e, x in enumerate(net))
            # Remove irrelevant directed circuits containing no terminal.
            for C in circuit_components(L, self.n, self.edges):
                if not any(D >> v & 1 for e in C for v in self.edges[e]):
                    for e in C:
                        net[e] = 0
                        L ^= 1 << e
            F = M
            for C in circuit_components(L, self.n, self.edges):
                F |= self.split_circuit(C, D)
            t = F ^ L
            assert F in self.code and t in self.code and F & t == M
            record.update(circuit_union=L,
                          first_cycle=self.code[F], partner_cycle=self.code[t])
        return record

    @lru_cache(None)
    def terminals(self, M):
        records = [self.network(M, S) for S in self.signings(M)]
        return {'matching': M, 'repairable': any(r['value'] == r['target'] for r in records),
                'signings': records}


def audit(obj, matchings):
    rows, sizes = [], Counter()
    successes = 0
    for M in sorted(set(matchings)):
        record = obj.terminals(M)
        assert record['repairable'] == obj.matching(M)['repairable']
        successes += record['repairable']
        for r in record['signings']:
            passes = int(r['value'] == r['target'])
            rows.append([M, r['sources'], passes])
            sizes[M.bit_count(), passes] += 1
    return {'matchings': len(set(matchings)), 'repairable_matchings': successes,
            'terminal_partitions': len(rows), 'feasible_partitions': sum(r[2] for r in rows),
            'size_and_feasibility_histogram': [list(k)+[v] for k,v in sorted(sizes.items())],
            'partition_records_sha256': digest(rows)}


def switch_audit(obj, flow):
    matchings = [0]+[sum((x == b) << e for e,x in enumerate(flow)) for b in range(1,8)]
    D = [obj.endpoint_mask(M) for M in matchings]
    rows, hist = [], Counter()
    for a in range(1,8):
        for C in obj.cycles[1:]:
            if C & matchings[a] or len(circuit_components(C,obj.n,obj.edges)) != 1:
                continue
            after = [x ^ a if C >> e & 1 else x for e,x in enumerate(flow)]
            updated, good = [], []
            for b in range(1,8):
                M = sum((x == b) << e for e,x in enumerate(after))
                Q = 0 if a == b else C & (matchings[b] | matchings[a ^ b])
                boundary = 0
                for e,(u,v) in enumerate(obj.edges):
                    if Q >> e & 1: boundary ^= (1 << u) | (1 << v)
                assert M == matchings[b] ^ Q
                assert obj.endpoint_mask(M) == D[b] ^ boundary
                if a != b:
                    assert M.bit_count()-matchings[b].bit_count() == (C & matchings[a ^ b]).bit_count()-(C & matchings[b]).bit_count()
                updated.append(M)
                if obj.matching(M)['repairable']: good.append(b)
            minimum = min(M.bit_count() for M in updated)
            hist[minimum,len(good)] += 1
            rows.append([a,C,minimum,good])
    old_minimum = min(M.bit_count() for M in matchings[1:])
    return {'moves':len(rows), 'matching_updates':7*len(rows),
            'moves_creating_repairable_matching':sum(bool(r[3]) for r in rows),
            'moves_lowering_smallest_class':sum(r[2] < old_minimum for r in rows),
            'lowering_moves_without_repairable_matching':sum(r[2] < old_minimum and not r[3] for r in rows),
            'size_and_good_count_histogram':[list(k)+[v] for k,v in sorted(hist.items())],
            'records_sha256':digest(rows)}


def counterexample(n, edges, selected, name=None):
    g = {'name':name or f'TwoEdgeObstruction{n}', 'vertices':n, 'edges':edges,
         'cycle_basis':cycle_basis(n,edges)}
    obj = TerminalFlow(g)
    M = sum(1 << e for e in selected)
    y,z = next((y,z) for y in range(1,len(obj.cycles)) for z in range(y+1,len(obj.cycles))
               if (obj.cycles[y] | obj.cycles[z]) == obj.all ^ M)
    F = next(c for c,mask in enumerate(obj.cycles) if mask & M == M)
    flow = [4*((obj.cycles[F] >> e)&1)+2*((obj.cycles[y] >> e)&1)+((obj.cycles[z] >> e)&1)
            for e in range(obj.m)]
    assert sum((x == 4) << e for e,x in enumerate(flow)) == M
    terminal = obj.terminals(M)
    assert not terminal['repairable']
    cuts = [A for A in range(1,1 << (n-1)) if obj.cut(A).bit_count() == 3
            and A.bit_count() > 1 and (n-A.bit_count()) > 1]
    return {'graph':g, 'matching_edges':selected, 'flow':flow, 'flow_cycle_codes':[z,y,F],
            'terminal_certificate':terminal, 'matching_certificate':obj.matching(M),
            'nontrivial_three_edge_cuts':[{'vertices':A,'edges':obj.cut(A)} for A in cuts]}


def two_edge_escape(obj,flow):
    for a in range(1,8):
        for C in obj.cycles[1:]:
            if len(circuit_components(C,obj.n,obj.edges)) != 1 or any(x == a and C >> e & 1 for e,x in enumerate(flow)):
                continue
            after = [x ^ a if C >> e & 1 else x for e,x in enumerate(flow)]
            for b in range(1,8):
                es = [e for e,x in enumerate(after) if x == b]
                if len(es) != 2: continue
                M = sum(1 << e for e in es)
                S = sum(1 << v for v in obj.edges[es[0]])
                record = obj.network(M,S)
                assert record['value'] == 4
                ell = next(x for x in range(1,8) if (x & b).bit_count()%2)
                repair = cover_from_intersection(obj,after,b,ell,record['first_cycle'],record['partner_cycle'])
                return {'initial_flow':flow,
                        'first_switch':{'increment':a,'edges':[e for e in range(obj.m) if C >> e & 1],'flow_after':after},
                        'matching':M,'sources':S,'terminal_certificate':obj.terminals(M),
                        'repair':repair}
    raise AssertionError('The saved flower state must have a two-edge escape.')


def main():
    old = json.loads((HERE/SOURCES[0]).read_text())
    p = TerminalFlow(next(g for g in old['graphs'] if g['name'] == 'Petersen'))
    j = TerminalFlow(next(g for g in old['graphs'] if g['name'] == 'Snark20_0'))
    repair = j.g['hard_flow_repair']
    keys = [repair['initial_space']]+[r['target_space'] for r in repair['rounds']]
    ps = list(p.feasible_planes())
    js = [ab for key in keys+j.neighbors(keys[0]) for ab in planes(key)]
    audits = [audit(obj, [obj.all & ~(obj.cycles[a] | obj.cycles[b]) for a,b in plane_list])
              for obj,plane_list in ((p,ps),(j,js))]
    pair_audits = []
    for g in old['graphs']:
        obj = p if g['name'] == 'Petersen' else j if g['name'] == 'Snark20_0' else TerminalFlow(g)
        rows = []
        for e,d in combinations(range(obj.m),2):
            if set(obj.edges[e]) & set(obj.edges[d]): continue
            M = (1 << e) | (1 << d)
            S = sum(1 << v for v in obj.edges[e])
            r = obj.network(M,S)
            assert r['value'] == 4
            assert all(len(circuit_components(obj.cycles[r[field]],obj.n,obj.edges)) == 1
                       for field in ('first_cycle','partner_cycle'))
            rows.append([M,S,1])
        pair_audits.append({'graph':g['name'],'matchings':len(rows),'records_sha256':digest(rows)})
    path = json.loads((HERE/SOURCES[1]).read_text())['flower_path']
    detailed = [{'space_key':state['space_key'],
                 'matchings':[dict(increment=r['increment'], **j.terminals(r['matching_mask']))
                              for r in state['matchings']]} for state in path]
    controls = [counterexample(12,[[0,5],[0,7],[0,9],[1,6],[1,7],[1,8],[2,6],[2,7],[2,8],
                                   [3,9],[3,10],[3,11],[4,9],[4,10],[4,11],[5,8],[5,11],[6,10]],[0,3]),
                counterexample(14,[[0,6],[0,9],[0,13],[1,7],[1,8],[1,9],[2,7],[2,8],[2,9],
                                   [3,8],[3,10],[3,11],[4,10],[4,12],[4,13],[5,11],[5,12],[5,13],
                                   [6,11],[6,12],[7,10]],[3,11])]
    bad_three = next(M for M in sorted({p.all & ~(p.cycles[a] | p.cycles[b]) for a,b in ps})
                     if M.bit_count() == 3 and p.matching(M)['candidate_even_subgraphs'] and not p.matching(M)['repairable'])
    core_limit = counterexample(p.n,p.edges,[e for e in range(p.m) if bad_three >> e & 1],
                               'PetersenThreeEdgeObstruction')
    result = {'date':'2026-10-05',
              'sources':[{'file':name,'sha256':hashlib.sha256((HERE/name).read_bytes()).hexdigest()} for name in SOURCES],
              'scope':'Balanced terminal max-flow criterion, two-edge matching theorem, and exact switch transport.',
              'petersen_audit':audits[0], 'flower_audit':audits[1],
              'two_edge_core_audits':pair_audits, 'flower_path':detailed,
              'flower_first_switches':switch_audit(j,repair['initial_flow']),
              'flower_two_edge_escape':two_edge_escape(j,repair['initial_flow']),
              'core_three_edge_obstruction':core_limit,
              'two_edge_counterexamples':controls}
    (HERE/'matching_terminal_flow.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('petersen_audit','flower_audit','flower_first_switches')},indent=2))
    print('Two-edge core matchings:',sum(r['matchings'] for r in pair_audits))


if __name__ == '__main__':
    main()
