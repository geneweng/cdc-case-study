#!/usr/bin/env python3
"""Paired-cut certificates for affine coordinate completion; standard library."""
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'flow_space_components.json'


def parity(x):
    return x.bit_count() & 1


def span(rows):
    out = [0]
    for row in rows:
        out += [x ^ row for x in out]
    return sorted(out)


def space_key(rows):
    points = span(rows)
    return sum(points[1 << j] << (16*j) for j in range(len(rows)))


def planes(key):
    points = span([(key >> (16*j)) & 65535 for j in range(3)])[1:]
    return [(a,b) for a,b in itertools.combinations(points,2) if a ^ b > b]


def eliminate(equations, variables):
    """Return rank, solution, or an inconsistent row combination."""
    pivots = {}
    for index,(row,rhs) in enumerate(equations):
        tag = 1 << index
        for p in sorted(pivots,reverse=True):
            if row >> p & 1:
                x,b,t = pivots[p]; row ^= x; rhs ^= b; tag ^= t
        if row:
            pivots[row.bit_length()-1] = (row,rhs,tag)
        elif rhs:
            return {'contradiction':tag}
    value = 0
    for p in sorted(pivots):
        row,rhs,_ = pivots[p]
        if parity(row & value) != rhs:
            value |= 1 << p
    assert value < 1 << variables
    return {'rank':len(pivots),'solution':value}


class Analysis:
    def __init__(self,g):
        self.g = g
        self.n,self.edges,self.basis = g['vertices'],g['edges'],g['cycle_basis']
        self.r,self.m = len(self.basis),len(self.edges)
        self.all = (1 << self.m)-1
        self.cycles = [0]
        for b in self.basis:
            self.cycles += [s ^ b for s in self.cycles]
        self.edge_rows = [sum(((b >> e) & 1) << j for j,b in enumerate(self.basis)) for e in range(self.m)]

    def cut(self,A):
        return sum(((((A >> u) ^ (A >> v)) & 1) << e) for e,(u,v) in enumerate(self.edges))

    @lru_cache(None)
    def components(self,mask):
        adj = [[] for _ in range(self.n)]
        for e,(u,v) in enumerate(self.edges):
            if mask >> e & 1:
                adj[u].append(v); adj[v].append(u)
        seen,out = set(),[]
        for v in range(self.n):
            if v in seen: continue
            queue = [v]; seen.add(v)
            for u in queue:
                for w in adj[u]:
                    if w not in seen: seen.add(w); queue.append(w)
            out.append(sum(1 << u for u in queue))
        return tuple(out)

    def row(self,mask):
        result = 0
        while mask:
            bit = mask & -mask; mask ^= bit
            result ^= self.edge_rows[bit.bit_length()-1]
        return result

    def vertex_cut(self,mask):
        equations = [((1 << u) ^ (1 << v),(mask >> e) & 1) for e,(u,v) in enumerate(self.edges)]
        result = eliminate(equations,self.n)
        assert 'solution' in result
        X = result['solution']
        assert self.cut(X) == mask
        return X

    @lru_cache(None)
    def flag(self,Fcode,ycode):
        F,y = self.cycles[Fcode],self.cycles[ycode]
        S = self.all & ~(F | y)
        forced = [e for e in range(self.m) if S >> e & 1]
        base = [(self.edge_rows[e],1) for e in forced]
        feasible = eliminate(base,self.r)
        assert 'solution' in feasible
        K = self.components(self.all ^ F)
        beta = [self.row(self.cut(k) & y) for k in K]
        result = eliminate(base+[(row,0) for row in beta],self.r)
        d = self.r-feasible['rank']
        homogeneous = eliminate([(row,0) for row,_ in base]+[(row,0) for row in beta],self.r)
        rho = homogeneous['rank']-feasible['rank']
        out = {'F':Fcode,'y':ycode,'fiber_cycle_dimension':d,'complement_components':len(K),
               'completion_rank':rho,'dual_dimension':len(K)-rho}
        if 'solution' in result:
            z = result['solution']
            assert result['rank'] == self.r-d+rho
            fourth = eliminate([(self.edge_rows[e],1 ^ (((y & self.cycles[z]) >> e) & 1))
                                for e in range(self.m) if F >> e & 1],self.r)
            assert 'solution' in fourth
            out.update(completions=1 << (d-rho),z=z,fourth=fourth['solution'])
        else:
            tag = result['contradiction']
            A = 0
            for i,k in enumerate(K):
                if tag >> (len(forced)+i) & 1: A ^= k
            q = y & self.cut(A)
            s = sum(1 << e for i,e in enumerate(forced) if tag >> i & 1)
            X = self.vertex_cut(q ^ s)
            assert not (self.cut(A) & ~F)
            assert (self.cut(X) & ~S) == q
            assert parity(self.cut(X) & S) == 1 and parity(X) == 1
            out.update(completions=0,obstruction={'A':A,'X':X,'cut_A':self.cut(A),'cut_X':self.cut(X),
                                                  'shared_cut':q,'forced_odd_cut':s})
        return out

    @lru_cache(None)
    def plane(self,a,b):
        points = sorted((a,b,a ^ b))
        flags = [self.flag(F,next(y for y in points if y != F)) for F in points]
        colors = [((self.cycles[a] >> e) & 1)+2*((self.cycles[b] >> e) & 1) for e in range(self.m)]
        blockers = []
        for e,(u,v) in enumerate(self.edges):
            if colors[e]: continue
            ends = []
            for w in (u,v):
                values = [colors[f] for f,edge in enumerate(self.edges) if w in edge and f != e]
                assert len(values) == 2 and values[0] == values[1] != 0
                ends.append(values[0])
            if ends[0] == ends[1]: continue
            normal = next(x for x in (1,2,3) if all(parity(x & c) for c in ends))
            first = (a if normal & 1 else 0) ^ (b if normal & 2 else 0)
            assert next(f for f in flags if f['F']==first)['completions'] == 0
            blockers.append({'edge':e,'endpoint_colors':ends,'blocked_first_cycle':first})
        return {'cycles':[a,b],'flags':flags,'marked':any(x['completions'] for x in flags),'local_blockers':blockers}

    def state(self,key):
        ps = [self.plane(a,b) for a,b in planes(key)]
        return {'space_key':key,'marked_planes':sum(p['marked'] for p in ps),
                'consistent_flags':sum(bool(x['completions']) for p in ps for x in p['flags']),
                'planes':ps}

    def feasible_planes(self):
        for a in range(1,len(self.cycles)):
            for b in range(a+1,len(self.cycles)):
                if a ^ b < b: continue
                S = self.all & ~(self.cycles[a] | self.cycles[b])
                if 'solution' in eliminate([(self.edge_rows[e],1) for e in range(self.m) if S >> e & 1],self.r):
                    yield a,b

    def neighbors(self,key):
        out = set()
        for a,b in planes(key):
            S = self.all & ~(self.cycles[a] | self.cycles[b])
            for z,mask in enumerate(self.cycles):
                if mask & S == S:
                    out.add(space_key((a,b,z)))
        out.discard(key)
        return sorted(out)

    def successful_firsts(self,key):
        points = span([(key >> (16*j)) & 65535 for j in range(3)])[1:]
        out = []
        for F in points:
            y = next(p for p in points if p != F)
            z = next(p for p in points if p not in (F,y,F ^ y))
            required = self.cycles[F] & ~(self.cycles[y] & self.cycles[z])
            result = eliminate([(self.edge_rows[e],(required >> e) & 1)
                                for e in range(self.m) if self.cycles[F] >> e & 1],self.r)
            if 'solution' in result: out.append(F)
        return out


def digest(records):
    return hashlib.sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest()


def summarize(analysis,plane_list):
    records = []
    marked,flags,solutions,local_flags,fully_local,no_local = 0,0,0,0,0,0
    ranks = Counter()
    for a,b in sorted(set(plane_list)):
        p = analysis.plane(a,b); marked += p['marked']
        blocked = {w['blocked_first_cycle'] for w in p['local_blockers']}
        local_flags += len(blocked)
        fully_local += len(blocked) == 3
        no_local += not p['marked'] and not blocked
        for f in p['flags']:
            records.append([a,b,f['F'],f['completions'],f['completion_rank'],f['dual_dimension']])
            flags += bool(f['completions']); solutions += f['completions']
            ranks[f['completion_rank']] += 1
    return {'planes':len(records)//3,'marked_planes':marked,'consistent_flags':flags,
            'successful_z_sum':solutions,'completion_rank_histogram':sorted(ranks.items()),
            'locally_blocked_flags':local_flags,'failed_flags_without_local_blocker':len(records)-flags-local_flags,
            'unmarked_planes_with_all_three_local_blockers':fully_local,'unmarked_planes_without_local_blockers':no_local,
            'flag_records_sha256':digest(records)}


def main():
    old = json.loads(SOURCE.read_text())
    petersen = next(g for g in old['graphs'] if g['name']=='Petersen')
    flower = next(g for g in old['graphs'] if g['name']=='Snark20_0')
    p,j = Analysis(petersen),Analysis(flower)
    P = summarize(p,list(p.feasible_planes()))
    repair = flower['hard_flow_repair']
    keys = [repair['initial_space']]+[r['target_space'] for r in repair['rounds']]
    states = [j.state(key) for key in keys]
    neighbors = j.neighbors(keys[0])
    histogram = Counter(j.state(key)['marked_planes'] for key in neighbors)
    neighborhood_records = [[key,j.state(key)['marked_planes']] for key in neighbors]
    all_planes = [ab for key in keys+neighbors for ab in planes(key)]
    J = summarize(j,all_planes)
    witness_plane = j.plane(*repair['rounds'][1]['fixed_cycles'])
    assert not witness_plane['marked'] and states[2]['marked_planes']
    a,b = witness_plane['cycles']
    S = j.all & ~(j.cycles[a] | j.cycles[b])
    extensions = sorted({space_key((a,b,z)) for z,s in enumerate(j.cycles) if s & S == S})
    successful = [key for key in extensions if j.successful_firsts(key)]
    out = {'date':'2026-10-05','source':{'file':SOURCE.name,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
           'scope':'General cut duality; all feasible Petersen planes and the first fiber neighborhood of one hard J5 state.',
           'petersen_audit':P,'flower_audit':J,'flower_states':states,
           'initial_neighbors':{'count':len(neighbors),'marked_plane_histogram':sorted(histogram.items()),
                                'records_sha256':digest(neighborhood_records)},
           'unmarked_successful_fiber':{'cycles':witness_plane['cycles'],'successful_space':keys[-1],
                                       'successful_first_cycle':577,'extension_spaces':len(extensions),
                                       'successful_extensions':successful}}
    (HERE/'fiber_cut_obstructions.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('petersen_audit','flower_audit','initial_neighbors')},indent=2))
    print('Path marked-plane counts:',[s['marked_planes'] for s in states])


if __name__ == '__main__':
    main()
