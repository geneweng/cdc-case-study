#!/usr/bin/env python3
"""Solver-free independent verification of the cyclically-five-connected minimum-color obstruction.

No constructor imports. Local proper colorings, DFS fundamental cycles,
all triples of edges, cut identities, and direct flow/cover checks are used.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()


class Check:
    def __init__(self,g):
        self.n,self.edges = g['vertices'],g['edges']; self.m = len(self.edges)
        self.full = (1 << self.m)-1
        assert self.n == 130 and self.m == 195
        assert len({tuple(sorted(uv)) for uv in self.edges}) == self.m
        assert all(u != v and 0 <= u < self.n and 0 <= v < self.n for u,v in self.edges)
        self.adj = [[(v if u == w else u,e) for e,(u,v) in enumerate(self.edges) if w in (u,v)] for w in range(self.n)]
        assert all(len(row) == 3 for row in self.adj)
        assert len(self.components(self.full)) == 1

    def components(self,mask):
        parent = list(range(self.n))
        def root(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]; v = parent[v]
            return v
        for e,(u,v) in enumerate(self.edges):
            if mask >> e & 1: parent[root(u)] = root(v)
        parts = {}
        for v in range(self.n): parts[root(v)] = parts.get(root(v),0) | (1 << v)
        return list(parts.values())

    def cut(self,A):
        return sum((bool(A >> u & 1) != bool(A >> v & 1)) << e for e,(u,v) in enumerate(self.edges))

    def even(self,mask):
        assert mask & ~self.full == 0
        return all(sum((mask >> e)&1 for _,e in row)%2 == 0 for row in self.adj)

    def circuit(self,mask):
        assert mask and self.even(mask)
        touched = sum(1 << v for v,row in enumerate(self.adj) if any(mask >> e & 1 for _,e in row))
        assert sum(bool(K & touched) for K in self.components(mask)) == 1

    def flow(self,values):
        assert len(values) == self.m and all(1 <= x <= 7 for x in values)
        for row in self.adj:
            x = 0
            for _,e in row: x ^= values[e]
            assert x == 0

    def support(self,values,ell):
        return sum(((x & ell).bit_count()%2) << e for e,x in enumerate(values))

    def connectivity(self,record):
        # DFS gives a spanning tree different from the constructor's BFS tree.
        parent = {0:(-1,-1)}; stack = [0]; tree = set()
        while stack:
            v = stack.pop()
            for w,e in reversed(self.adj[v]):
                if w not in parent:
                    parent[w] = (v,e); tree.add(e); stack.append(w)
        assert len(parent) == self.n and len(tree) == self.n-1
        def root_path(v):
            mask = 0
            while v:
                v,e = parent[v]; mask ^= 1 << e
            return mask
        chords = [e for e in range(self.m) if e not in tree]
        basis = [root_path(self.edges[e][0]) ^ root_path(self.edges[e][1]) ^ (1 << e) for e in chords]
        assert len(basis) == 66 and all(self.even(C) for C in basis)
        assert all([e for e in chords if C >> e & 1] == [chord] for chord,C in zip(chords,basis))
        columns = [sum(((C >> e)&1) << j for j,C in enumerate(basis)) for e in range(self.m)]
        assert 0 not in columns and len(set(columns)) == self.m
        triples = [[a,b,c] for a,b,c in itertools.combinations(range(self.m),3) if columns[a] ^ columns[b] ^ columns[c] == 0]
        stars = sorted(sorted(e for _,e in row) for row in self.adj)
        assert triples == stars and len(triples) == 130
        # Independent exhaustive four-subset check, not a pair-sum lookup.
        quads = [[a,b,c,d] for a,b,c,d in itertools.combinations(range(self.m),4)
                 if columns[a] ^ columns[b] ^ columns[c] ^ columns[d] == 0]
        edge_sides = sorted(sorted(set(e for _,e in self.adj[u]) ^ set(e for _,e in self.adj[v])) for u,v in self.edges)
        assert quads == edge_sides and len(quads) == 195
        side = record['five_cut_side']; boundary = self.cut(side)
        assert boundary == record['five_cut_edges'] and boundary.bit_count() == 5
        pieces = self.components(self.full ^ boundary)
        assert len(pieces) == 2 and side in pieces
        assert all(sum(bool(K >> u & 1 and K >> v & 1) for u,v in self.edges) >= K.bit_count() for K in pieces)
        assert record == {'cycle_dimension':66,'distinct_nonzero_columns':195,'three_edge_cuts':130,
                          'three_cut_records_sha256':digest(triples),'four_edge_cuts':195,
                          'four_cut_records_sha256':digest(quads),'five_cut_side':side,
                          'five_cut_edges':boundary,'cyclic_edge_connectivity':5}
        girth = self.n
        for start in range(self.n):
            distance = {start:0}; previous = {start:-1}; queue = deque([start])
            while queue:
                v = queue.popleft()
                for w,e in self.adj[v]:
                    if w not in distance:
                        distance[w] = distance[v]+1; previous[w] = v; queue.append(w)
                    elif previous[v] != w and previous[w] != v:
                        girth = min(girth,distance[v]+distance[w]+1)
        assert girth == 5
        return math.comb(self.m,3),math.comb(self.m,4)


def local_structure(poles):
    def es(p): return {tuple(sorted(uv)) for uv in p['edges']}
    def shift(p,k): return {tuple(sorted((u+k,v+k))) for u,v in p['edges']}
    assert set(poles) == {'M','N','Z','Y'}
    M,N,Z,Y = [poles[k] for k in ('M','N','Z','Y')]
    # Explicit internal adjacency specifications, independent of construction.
    adjacency_M = [[1,2],[0,3],[0,5,6],[1,4,6],[3,5],[2,4],[2,3]]
    adjacency_N = [[2,5],[4,6],[0,7],[5,6],[1,8],[0,3,8],[1,3,7],[2,6,8],[4,5,7]]
    assert es(M) == {(v,w) for v,row in enumerate(adjacency_M) for w in row if v < w}
    assert es(N) == {(v,w) for v,row in enumerate(adjacency_N) for w in row if v < w}
    assert M['ports'] == [0,4,1,5,6] and N['ports'] == [0,1,2,3,4]
    assert es(Z) == es(M) | shift(N,7) | {(1,7),(5,8),(6,16),(11,16)}
    assert Z['ports'] == [0,4,9,10,16]
    assert es(Y) == es(Z) | shift(Z,17) | shift(M,34) | {(9,38),(10,34),(26,39),(27,35),(16,33)}
    assert Y['ports'] == [0,4,17,21,40]
    for name,n,m in (('M',7,8),('N',9,11),('Z',17,23),('Y',41,59)):
        p = poles[name]
        assert p['vertices'] == n and len(p['edges']) == m == len(es(p))
        assert all(0 <= u < n and 0 <= v < n and u != v for u,v in p['edges'])
        assert len(p['ports']) == len(set(p['ports'])) == 5
        assert all(sum(v in uv for uv in p['edges'])+(v in p['ports']) == 3 for v in range(n))


def local_audit(poles):
    audits,boundaries = {},{}
    for name in ('M','N','Z'):
        p = poles[name]; n = p['vertices']
        edges = p['edges']+[(v,-j-1) for j,v in enumerate(p['ports'])]
        used = [set() for _ in range(n)]; values = []; rows = []
        def visit(e):
            if e == len(edges):
                rows.append(values.copy()); return
            vertices = [v for v in edges[e] if v >= 0]
            for color in (1,2,3):
                if any(color in used[v] for v in vertices): continue
                for v in vertices: used[v].add(color)
                values.append(color); visit(e+1); values.pop()
                for v in vertices: used[v].remove(color)
        visit(0)
        hist = Counter(tuple(row[-5:]) for row in rows)
        boundaries[name] = sorted(hist)
        pivots = {}
        for v in range(n):
            row = sum(1 << e for e,uv in enumerate(edges) if v in uv)
            while row:
                bit = row.bit_length()-1
                if bit in pivots: row ^= pivots[bit]
                else: pivots[bit] = row; break
        assert len(pivots) == n
        audits[name] = {'binary_flows':1 << (len(edges)-n),'nowhere_zero_two_bit_flows':len(rows),
                        'records_sha256':digest(sorted(rows)),
                        'boundary_histogram':[list(k)+[v] for k,v in sorted(hist.items())]}
    assert [audits[name]['nowhere_zero_two_bit_flows'] for name in ('M','N','Z')] == [36,42,72]
    assert all(p[0] == p[1] or p[2] == p[3] for p in boundaries['M'])
    assert all(p[0] != p[1] for p in boundaries['N'])
    assert all(p[0] == p[1] and set(p[2:]) == {1,2,3} for p in boundaries['Z'])
    # Join boundary assignments using the five actual linking edges in Y.
    allowed = 0; total = 0
    for z,zz,m in itertools.product(boundaries['Z'],boundaries['Z'],boundaries['M']):
        colors = dict(zip([0,4,9,10,16],z))
        colors.update(zip([17,21,26,27,33],zz)); colors.update(zip([34,38,35,39,40],m))
        total += 1
        if all(colors[u] == colors[v] for u,v in ((9,38),(10,34),(26,39),(27,35),(16,33))): allowed += 1
    assert total == 11664 and allowed == 0
    audits['Y'] = {'boundary_combinations':total,'zero_free_compatible_combinations':allowed}
    return audits


def construction_and_bound(obj,data):
    g = data['graph']; Y = data['local_poles']['Y']; regions = g['regions']
    expected = set(); charged = []
    assert len(regions) == 3 and g['center'] == 123
    assert g['center_neighbors'] == [124,125,126] and g['other_junctions'] == [127,128,129]
    for i,region in enumerate(regions):
        vs = set(range(41*i,41*i+41))
        assert region['vertices'] == sorted(vs)
        assert region['ports'] == [v+41*i for v in [0,4,17,21,40]]
        expected.update(tuple(sorted((u+41*i,v+41*i))) for u,v in Y['edges'])
        p = region['ports']; next_first = 41*((i+1)%3)
        expected.update(tuple(sorted(uv)) for uv in [(p[4],124+i),(next_first,124+i),(124+i,123),(p[1],127),(p[2],128),(p[3],129)])
        row = [e for e,uv in enumerate(obj.edges) if vs.intersection(uv)]
        assert row == region['charged_edges'] and len(row) == 64
        assert sum(data['initial_flow'][e] == 4 for e in row) == 1
        charged.append(set(row))
    assert expected == set(map(tuple,map(sorted,obj.edges)))
    assert all(a.isdisjoint(b) for a,b in itertools.combinations(charged,2))
    # Each restriction to Y is a two-bit flow; the local audit proves it
    # has a zero. Disjoint charged sets force at least three global zeros.
    # Quotienting by a three-bit color makes precisely that class zero.
    for a in range(1,8):
        fixed = [q for q in range(1,8) if (q & a).bit_count()%2 == 0]
        y,z = fixed[:2]
        assert [x for x in range(8) if (x & y).bit_count()%2 == (x & z).bit_count()%2 == 0] == [0,a]


def failures(obj,data):
    f = data['initial_flow']
    assert [r['color'] for r in data['matching_failures']] == list(range(1,8))
    for r in data['matching_failures']:
        M = sum((x == r['color']) << e for e,x in enumerate(f))
        assert M == r['matching'] and M.bit_count() == r['size']
        endpoints = [v for e,uv in enumerate(obj.edges) if M >> e & 1 for v in uv]
        assert len(endpoints) == len(set(endpoints))
        D = sum(1 << v for v in endpoints); K = r['odd_unmatched_component']
        assert K and K & D == 0 and K.bit_count()%2
        assert r['component_vertices'] == [v for v in range(obj.n) if K >> v & 1]
        induced = sum(1 << e for e,(u,v) in enumerate(obj.edges) if K >> u & 1 and K >> v & 1)
        assert K in obj.components(induced)
        for e,(u,v) in enumerate(obj.edges):
            if obj.cut(K) >> e & 1:
                outside = v if K >> u & 1 else u
                assert D >> outside & 1
        assert obj.cut(K).bit_count()%2 == 1
    expected = {(a,b,ell) for a,b in itertools.combinations(range(1,8),2) if a ^ b > b for ell in (a,b,a ^ b)}
    actual = set()
    for r in data['failed_flags']:
        a,b = r['plane_functionals']; ell,yy = r['first'],r['second']
        assert ell in (a,b,a ^ b) and yy in (a,b,a ^ b) and yy != ell
        actual.add((a,b,ell))
        F,y = obj.support(f,ell),obj.support(f,yy); S = obj.full & ~(F | y)
        dA,dX = obj.cut(r['A']),obj.cut(r['X'])
        assert dA & ~F == 0 and dX & ~S == dA & y
        assert (dX & S).bit_count()%2 == r['X'].bit_count()%2 == 1
    assert actual == expected and len(data['failed_flags']) == 21


def verify_repair(obj,data):
    r = data['repair']; current = data['initial_flow']
    assert len(r['moves']) == 2 and [m['increment'] for m in r['moves']] == [6,4]
    for j,move in enumerate(r['moves']):
        C = sum(1 << e for e in move['edges']); obj.circuit(C)
        assert len(move['edges']) == (12,101)[j]
        assert all(current[e] != move['increment'] for e in move['edges'])
        after = [x ^ move['increment'] if C >> e & 1 else x for e,x in enumerate(current)]
        assert after == move['flow_after']; obj.flow(after)
        counts = [after.count(a) for a in range(1,8)]
        assert counts == move['color_sizes'] and min(counts) == counts[3] == 3
        if j == 0:
            oldM = {e for e,x in enumerate(current) if x == 4}
            newM = {e for e,x in enumerate(after) if x == 4}
            assert oldM-newM == {189} and newM-oldM == {138}
        if j == 0: assert counts == data['initial_color_sizes']
        current = after
    F,t = r['intersection_first'],r['intersection_partner']
    assert obj.even(F) and obj.even(t)
    assert F & t == sum((x == 4) << e for e,x in enumerate(current))
    assert r['target_color'] == 4 and r['first_functional'] == 4
    assert obj.support(current,4) == F
    previous = r['moves'][0]['flow_after']
    assert obj.support(previous,4) ^ F == sum(1 << e for e in r['moves'][1]['edges'])
    out = r['final_lift']; forms = out['coordinate_functionals']
    assert forms == [2,1,4]
    assert len({0,*forms,forms[0]^forms[1],forms[0]^forms[2],forms[1]^forms[2],forms[0]^forms[1]^forms[2]}) == 8
    transformed = [sum(((x & q).bit_count()%2) << i for i,q in enumerate(forms)) for x in current]
    assert transformed == out['transformed_flow']
    fourth = t ^ obj.support(current,1) ^ obj.support(current,2)
    assert fourth == out['fourth_coordinate'] and obj.even(fourth)
    palette = (4,5,6,15,8)
    decode = {palette[i] ^ palette[j]:(1 << i)|(1 << j) for i,j in itertools.combinations(range(5),2)}
    pairs = [decode[x+8*((fourth >> e)&1)] for e,x in enumerate(transformed)]
    assert pairs == out['cover_pairs'] and all(x.bit_count() == 2 for x in pairs)
    for row in obj.adj:
        xor = 0
        for _,e in row: xor ^= pairs[e]
        assert xor == 0


def main():
    data = json.loads((HERE/'cyclic_five_minimum_obstruction.json').read_text())
    for source in data['sources']:
        assert hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256']
    obj = Check(data['graph']); obj.flow(data['initial_flow'])
    local_structure(data['local_poles'])
    assert local_audit(data['local_poles']) == data['local_audits']
    construction_and_bound(obj,data)
    assert data['minimum_color_multiplicity'] == 3
    counts = [data['initial_flow'].count(a) for a in range(1,8)]
    assert counts == data['initial_color_sizes'] and min(counts) == counts[3] == 3
    triples,quads = obj.connectivity(data['connectivity'])
    girth = data['girth_certificate']
    assert girth['girth'] == 5 and len(girth['shortest_circuit_edges']) == 5
    obj.circuit(sum(1 << e for e in girth['shortest_circuit_edges']))
    failures(obj,data); verify_repair(obj,data)
    assert [len(r['component_vertices']) for r in data['matching_failures']] == [5,11,17,1,1,1,1]
    print('130-vertex simple cubic graph: connected, girth five, cyclic edge connectivity exactly five.')
    print('Local proper-coloring counts 36, 42, 72; all 11664 boundary triples fail on the 41-vertex five-pole.')
    print('Three disjoint uncolorable regions prove every flow color has at least three edges; the saved flow attains three.')
    print('All',triples,'edge triples and',quads,'edge quadruples checked.')
    print('Exactly 130 three-cuts and 195 four-cuts, all isolating a vertex or an adjacent pair; no Petersen four-pole.')
    print('Seven odd unmatched-component obstructions and all 21 paired-cut certificates verified.')
    print('Twelve-circuit plus 101-circuit repair verified; first switch preserves the entire color-size vector.')
    print('Final five-layer cover and minimum three verified.')


if __name__ == '__main__':
    main()
