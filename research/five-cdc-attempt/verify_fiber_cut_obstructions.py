#!/usr/bin/env python3
"""Independent finite check: enumerate cycles and fourth-bit restrictions.

Imports no constructor code. Dual dimensions on the saved path are also
checked by signed-edge propagation over every union of complement components.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(records):
    return hashlib.sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest()


def dimension(power):
    assert power > 0 and power & (power-1) == 0
    return power.bit_length()-1


def canonical(rows):
    basis = {}
    for x in rows:
        while x:
            p = x.bit_length()-1
            if p in basis: x ^= basis[p]
            else: basis[p] = x; break
    for p in sorted(basis):
        for q in sorted(basis):
            if q > p and basis[q] >> p & 1: basis[q] ^= basis[p]
    assert len(basis) == 3
    return sum(basis[p] << (16*j) for j,p in enumerate(sorted(basis)))


def points(key):
    rows = [(key >> (16*j)) & 65535 for j in range(3)]
    return sorted({0,rows[0],rows[1],rows[2],rows[0]^rows[1],rows[0]^rows[2],
                   rows[1]^rows[2],rows[0]^rows[1]^rows[2]})[1:]


def planes(key):
    return [(a,b) for a,b in itertools.combinations(points(key),2) if b < a ^ b]


class Check:
    def __init__(self,g):
        self.n,self.edges = g['vertices'],g['edges']
        self.m = len(self.edges); self.full = (1 << self.m)-1
        basis = g['cycle_basis']
        self.cycles = []
        for code in range(1 << len(basis)):
            mask = 0
            for j,b in enumerate(basis):
                if code >> j & 1: mask ^= b
            self.cycles.append(mask)
        assert len(set(self.cycles)) == len(self.cycles)
        assert len(basis) == self.m-self.n+1
        assert len(self.components(self.full)) == 1
        for mask in self.cycles:
            degrees = [0]*self.n
            for e,(u,v) in enumerate(self.edges):
                if mask >> e & 1: degrees[u] ^= 1; degrees[v] ^= 1
            assert not any(degrees)
        degree = Counter(v for edge in self.edges for v in edge)
        assert set(degree.values()) == {3}
        assert all(u != v for u,v in self.edges)
        assert len({tuple(sorted(e)) for e in self.edges}) == self.m
        self.restrictions = [{s & F for s in self.cycles} for F in self.cycles]

    def cut(self,A):
        result = 0
        for e,(u,v) in enumerate(self.edges):
            if bool(A >> u & 1) != bool(A >> v & 1): result |= 1 << e
        return result

    @lru_cache(None)
    def components(self,mask):
        parent = list(range(self.n))
        def root(u):
            while parent[u] != u: u = parent[u]
            return u
        for e,(u,v) in enumerate(self.edges):
            if mask >> e & 1: parent[root(u)] = root(v)
        groups = {}
        for u in range(self.n): groups[root(u)] = groups.get(root(u),0) | (1 << u)
        return tuple(sorted(groups.values()))

    @lru_cache(None)
    def feasible(self,a,b):
        S = self.full & ~(self.cycles[a] | self.cycles[b])
        return tuple(z for z,s in enumerate(self.cycles) if s & S == S)

    @lru_cache(None)
    def flag(self,Fcode,ycode):
        F,y = self.cycles[Fcode],self.cycles[ycode]
        S = self.full & ~(F | y)
        zs = self.feasible(Fcode,ycode)
        assert zs
        homogeneous = [s for s in self.cycles if s & S == 0]
        assert len(homogeneous) == len(zs)
        K = self.components(self.full ^ F)
        boundaries = [self.cut(k) & y for k in K]
        image = {sum(((s & cut).bit_count() % 2) << j for j,cut in enumerate(boundaries)) for s in homogeneous}
        rho = dimension(len(image))
        count = sum((F & ~(y & self.cycles[z])) in self.restrictions[Fcode] for z in zs)
        assert count in (0,len(zs)//len(image))
        return {'completions':count,'completion_rank':rho,'dual_dimension':len(K)-rho,
                'fiber_cycle_dimension':dimension(len(zs)),'complement_components':len(K)}

    @lru_cache(None)
    def plane(self,a,b):
        ps = sorted((a,b,a ^ b))
        return [(F,self.flag(F,next(y for y in ps if y != F))) for F in ps]

    def local_blockers(self,a,b):
        S = self.full & ~(self.cycles[a] | self.cycles[b]); ps = sorted((a,b,a ^ b))
        result = []
        for e,(u,v) in enumerate(self.edges):
            if not (S >> e & 1): continue
            for first in ps:
                y = next(x for x in ps if x != first)
                others = [[f for f,edge in enumerate(self.edges) if w in edge and f != e] for w in (u,v)]
                if not all(self.cycles[first] >> f & 1 for pair in others for f in pair): continue
                bits = [[(self.cycles[y] >> f)&1 for f in pair] for pair in others]
                assert all(x[0] == x[1] for x in bits)
                if bits[0][0] == bits[1][0]: continue
                assert self.flag(first,y)['completions'] == 0
                colors = [((self.cycles[a] >> pair[0])&1)+2*((self.cycles[b] >> pair[0])&1) for pair in others]
                result.append({'edge':e,'endpoint_colors':colors,'blocked_first_cycle':first})
        return result

    def marked_count(self,key):
        return sum(any(f['completions'] for _,f in self.plane(a,b)) for a,b in planes(key))

    def good_firsts(self,key):
        ps = points(key); out = []
        for a in ps:
            b = next(x for x in ps if x != a)
            c = next(x for x in ps if x not in (a,b,a ^ b))
            if (self.cycles[a] & ~(self.cycles[b] & self.cycles[c])) in self.restrictions[a]: out.append(a)
        return out

    def dual_counts(self,Fcode,ycode):
        F,y = self.cycles[Fcode],self.cycles[ycode]
        S = self.full & ~(F | y); T = self.full ^ S
        K = self.components(self.full ^ F)
        # Feasible fibers have even components of T in a cubic graph.
        assert all(k.bit_count() % 2 == 0 for k in self.components(T))
        counts = [0,0]
        for selector in range(1 << len(K)):
            A = sum(k for j,k in enumerate(K) if selector >> j & 1)
            q = y & self.cut(A)
            adjacent = [[] for _ in range(self.n)]
            for e,(u,v) in enumerate(self.edges):
                if T >> e & 1:
                    adjacent[u].append((v,(q >> e) & 1)); adjacent[v].append((u,(q >> e) & 1))
            labels = {}; valid = True
            for root in range(self.n):
                if root in labels: continue
                labels[root] = 0; queue = [root]
                for u in queue:
                    for v,bit in adjacent[u]:
                        want = labels[u] ^ bit
                        if v in labels:
                            if labels[v] != want: valid = False; break
                        else: labels[v] = want; queue.append(v)
                    if not valid: break
                if not valid: break
            if valid:
                X = sum(1 << v for v,bit in labels.items() if bit)
                assert self.cut(X) & T == q
                chi = (self.cut(X) & S).bit_count() % 2
                assert chi == X.bit_count() % 2
                counts[chi] += 1
        return counts

    def saved_flag(self,f):
        a,b = f['F'],f['y']; expected = self.flag(a,b)
        assert all(f[k] == v for k,v in expected.items())
        even,odd = self.dual_counts(a,b)
        assert even+odd == 1 << f['dual_dimension']
        assert (odd == 0) == bool(f['completions'])
        if odd: assert even == odd
        F,y = self.cycles[a],self.cycles[b]; S = self.full & ~(F | y)
        if f['completions']:
            z,t = self.cycles[f['z']],self.cycles[f['fourth']]
            assert z & S == S and t & F == F & ~(y & z)
            palette = [4,5,6,15,8]
            decode = {x ^ yy:(1 << i)|(1 << j) for i,x in enumerate(palette) for j,yy in enumerate(palette) if i < j}
            cover = [decode[4*((F >> e)&1)+2*((y >> e)&1)+((z >> e)&1)+8*((t >> e)&1)] for e in range(self.m)]
            boundary = [0]*self.n
            for pair,(u,v) in zip(cover,self.edges):
                assert pair.bit_count() == 2; boundary[u] ^= pair; boundary[v] ^= pair
            assert not any(boundary)
        else:
            w = f['obstruction']; A,X = w['A'],w['X']
            assert 0 <= A < 1 << self.n and 0 <= X < 1 << self.n
            assert self.cut(A) == w['cut_A'] and self.cut(X) == w['cut_X']
            assert self.cut(A) & ~F == 0
            assert (self.cut(X) & ~S) == (self.cut(A) & y) == w['shared_cut']
            assert (self.cut(X) & S) == w['forced_odd_cut']
            assert w['forced_odd_cut'].bit_count() % 2 == 1 and X.bit_count() % 2 == 1


def audit(check,plane_list):
    records = []; marked = flags = successful = local_flags = fully_local = no_local = 0; ranks = Counter()
    for a,b in sorted(set(plane_list)):
        fs = check.plane(a,b)
        good = any(f['completions'] for _,f in fs); marked += good
        blocked = {w['blocked_first_cycle'] for w in check.local_blockers(a,b)}
        local_flags += len(blocked); fully_local += len(blocked) == 3; no_local += not good and not blocked
        for F,f in fs:
            flags += bool(f['completions']); successful += f['completions']; ranks[f['completion_rank']] += 1
            records.append([a,b,F,f['completions'],f['completion_rank'],f['dual_dimension']])
    return {'planes':len(records)//3,'marked_planes':marked,'consistent_flags':flags,'successful_z_sum':successful,
            'completion_rank_histogram':[list(x) for x in sorted(ranks.items())],'flag_records_sha256':digest(records),
            'locally_blocked_flags':local_flags,'failed_flags_without_local_blocker':len(records)-flags-local_flags,
            'unmarked_planes_with_all_three_local_blockers':fully_local,'unmarked_planes_without_local_blockers':no_local}


def main():
    data = json.loads((HERE/'fiber_cut_obstructions.json').read_text())
    source = HERE/data['source']['file']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == data['source']['sha256']
    graphs = json.loads(source.read_text())['graphs']
    p = Check(next(g for g in graphs if g['name']=='Petersen'))
    pplanes = [(a,b) for a in range(1,len(p.cycles)) for b in range(a+1,len(p.cycles))
               if b < a ^ b and p.feasible(a,b)]
    assert audit(p,pplanes) == data['petersen_audit']
    pspaces = {canonical((a,b,z)) for a,b in pplanes for z in p.feasible(a,b)}
    assert len(pspaces) == 170 and all(p.good_firsts(key) for key in pspaces)
    print('Petersen: all 400 feasible planes, 1,200 flags, and 170 successful spaces verified.',flush=True)
    g = next(g for g in graphs if g['name']=='Snark20_0'); j = Check(g)
    repair = g['hard_flow_repair']; keys = [repair['initial_space']]+[r['target_space'] for r in repair['rounds']]
    saved_count = 0
    for key,state in zip(keys,data['flower_states'],strict=True):
        assert key == state['space_key']
        assert [p['cycles'] for p in state['planes']] == [list(x) for x in planes(key)]
        assert state['marked_planes'] == j.marked_count(key)
        consistent = 0
        for pl in state['planes']:
            a,b = pl['cycles']; ps = sorted((a,b,a ^ b))
            assert [(f['F'],f['y']) for f in pl['flags']] == [(F,next(y for y in ps if y != F)) for F in ps]
            assert pl['marked'] == any(f['completions'] for _,f in j.plane(a,b))
            assert pl['local_blockers'] == j.local_blockers(a,b)
            for f in pl['flags']:
                j.saved_flag(f); saved_count += 1; consistent += bool(f['completions'])
        assert consistent == state['consistent_flags']
    assert [bool(j.good_firsts(key)) for key in keys] == [False,False,True]
    flow = repair['initial_flow']
    for i,key in enumerate(keys):
        coordinate_codes = []
        for bit in range(3):
            mask = sum(((x >> bit)&1) << e for e,x in enumerate(flow))
            coordinate_codes.append(j.cycles.index(mask))
        assert canonical(coordinate_codes) == key
        if i < len(repair['moves']):
            move = repair['moves'][i]; circuit = sum(1 << e for e in move['edges'])
            assert circuit in j.cycles and len(set(move['edges'])) == len(move['edges'])
            nonisolated = [k for k in j.components(circuit) if k.bit_count() > 1]
            assert len(nonisolated) == 1
            assert all(flow[e] != move['increment'] for e in move['edges'])
            flow = [x ^ move['increment'] if circuit >> e & 1 else x for e,x in enumerate(flow)]
            assert flow == move['flow_after']
    neighbors = sorted({canonical((a,b,z)) for a,b in planes(keys[0]) for z in j.feasible(a,b)}-{keys[0]})
    records = [[key,j.marked_count(key)] for key in neighbors]
    assert all(not j.good_firsts(key) for key in neighbors)
    assert keys[1] in neighbors
    summary = {'count':len(neighbors),'marked_plane_histogram':[list(x) for x in sorted(Counter(c for _,c in records).items())],
               'records_sha256':digest(records)}
    assert summary == data['initial_neighbors']
    plane_list = [ab for key in keys+neighbors for ab in planes(key)]
    assert audit(j,plane_list) == data['flower_audit']
    w = data['unmarked_successful_fiber']; a,b = w['cycles']
    extensions = sorted({canonical((a,b,z)) for z in j.feasible(a,b)})
    assert not any(f['completions'] for _,f in j.plane(a,b))
    assert len(extensions) == w['extension_spaces']
    assert [key for key in extensions if j.good_firsts(key)] == w['successful_extensions']
    assert w['successful_space'] == keys[-1] and keys[-1] in extensions
    assert w['successful_first_cycle'] in j.good_firsts(keys[-1])
    assert w['successful_first_cycle'] not in (a,b,a ^ b)
    print(f'J5: 1,076 planes, 3,228 flags, {saved_count} explicit completion/dual witnesses, and 185 neighbors verified.')
    print('Signed graph propagation checks every dual component-union choice for all 63 saved flags.')
    print('Unmarked fiber: exactly 9 of 64 extensions successful; path marked-plane counts 0, 0, 3.')


if __name__ == '__main__':
    main()
