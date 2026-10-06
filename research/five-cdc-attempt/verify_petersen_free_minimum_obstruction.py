#!/usr/bin/env python3
"""Solver-free independent verification of the Petersen-free minimum-color obstruction.

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
        assert self.n == 214 and self.m == 321
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
        assert len(basis) == 108 and all(self.even(C) for C in basis)
        assert all([e for e in chords if C >> e & 1] == [chord] for chord,C in zip(chords,basis))
        columns = [sum(((C >> e)&1) << j for j,C in enumerate(basis)) for e in range(self.m)]
        assert 0 not in columns and len(set(columns)) == self.m
        triples = [[a,b,c] for a,b,c in itertools.combinations(range(self.m),3) if columns[a] ^ columns[b] ^ columns[c] == 0]
        stars = sorted(sorted(e for _,e in row) for row in self.adj)
        assert triples == stars and len(triples) == 214
        side = record['four_cut_side']; boundary = self.cut(side)
        assert boundary == record['four_cut_edges'] and boundary.bit_count() == 4
        pieces = self.components(self.full ^ boundary)
        assert len(pieces) == 2 and side in pieces
        assert all(sum(bool(K >> u & 1 and K >> v & 1) for u,v in self.edges) >= K.bit_count() for K in pieces)
        assert record == {'cycle_dimension':108,'distinct_nonzero_columns':321,'three_edge_cuts':214,
                          'three_cut_records_sha256':digest(triples),'four_cut_side':side,
                          'four_cut_edges':boundary,'cyclic_edge_connectivity':4}
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
        assert girth == 6
        return math.comb(self.m,3)


def flower_structure(g):
    # Construct J5 as a 5-cycle on b, a twisted 10-cycle on c,d, and
    # five stars with centers a. This uses a different ring description.
    stars = [(4*i,4*i+j) for i in range(5) for j in (1,2,3)]
    b_ring = [4*i+1 for i in range(5)]
    cd_ring = [4*i+2 for i in range(5)]+[4*i+3 for i in range(5)]
    expected = {tuple(sorted(uv)) for uv in stars}
    for ring in (b_ring,cd_ring):
        expected.update(tuple(sorted((v,ring[(j+1)%len(ring)]))) for j,v in enumerate(ring))
    assert len(g['flower_edges']) == 30
    assert set(map(tuple,map(sorted,g['flower_edges']))) == expected
    assert g['deleted_flower_vertices'] == [0,1]
    remaining = {uv for uv in expected if not set(uv) & {0,1}}
    internal = g['fourpole_internal_edges']
    assert len(internal) == 25 and set(map(tuple,map(sorted,internal))) == remaining
    assert g['ports'] == [2,3,5,17]
    assert {v for uv in expected if 0 in uv for v in uv if v not in (0,1)} == {2,3}
    assert {v for uv in expected if 1 in uv for v in uv if v not in (0,1)} == {5,17}
    return internal


def local_audit(g):
    # Independent proper-coloring DFS, with four separate dangling ends.
    internal = flower_structure(g)
    edges = internal+[(2,-1),(3,-2),(5,-3),(17,-4)]
    used = {v:set() for v in range(2,20)}; values = []; rows = []
    def visit(e):
        if e == len(edges):
            rows.append(values.copy()); return
        vertices = [v for v in edges[e] if v >= 2]
        for color in (1,2,3):
            if any(color in used[v] for v in vertices): continue
            for v in vertices: used[v].add(color)
            values.append(color); visit(e+1); values.pop()
            for v in vertices: used[v].remove(color)
    visit(0)
    assert len(rows) == 108 and all(r[25] == r[26] and r[27] == r[28] for r in rows)
    pivots = {}
    for v in range(2,20):
        row = sum(1 << e for e,uv in enumerate(edges) if v in uv)
        while row:
            p = row.bit_length()-1
            if p in pivots: row ^= pivots[p]
            else: pivots[p] = row; break
    assert len(pivots) == 18
    boundary = Counter(tuple(r[25:]) for r in rows)
    assert len(boundary) == 9 and set(boundary.values()) == {12}
    return {'binary_flows':1 << (29-len(pivots)),'nowhere_zero_two_bit_flows':len(rows),
            'records_sha256':digest(sorted(rows)),
            'boundary_histogram':[list(k)+[v] for k,v in sorted(boundary.items())]}


def construction_and_bound(obj,g,initial):
    internal = flower_structure(g)
    spokes = [(0,10),(5,10),(2,10),(1,11),(6,11),(8,11),(3,12),(7,12),(4,13),(9,13)]
    expected = {tuple(sorted(e)) for e in spokes+[(12,13)]}
    index = {tuple(sorted(uv)):e for e,uv in enumerate(obj.edges)}
    base = expected | {tuple(sorted((offset+j,offset+(j+1)%5))) for offset in (0,5) for j in range(5)}
    assert set(map(tuple,map(sorted,g['base_edges']))) == base
    charges = []
    for r,region in enumerate(g['regions']):
        assert region['base_vertices'] == list(range(5*r,5*r+5))
        blocks = [{v:14+100*r+18*j+v-2 for v in range(2,20)} for j in range(5)]
        junctions = [[104+100*r+2*j,105+100*r+2*j] for j in range(5)]
        assert region['blocks'] == [{str(v):w for v,w in b.items()} for b in blocks]
        assert region['junctions'] == junctions
        local_edges = []
        for j,b in enumerate(blocks):
            u,w = junctions[j]; nu,nw = junctions[(j+1)%5]
            local = [(b[x],b[y]) for x,y in internal]+[(b[2],nu),(b[3],nw),(b[5],u),(b[17],w)]
            expected.update(tuple(sorted(e)) for e in local+[(5*r+j,u),(5*r+j,w)])
            local_edges.append([index[tuple(sorted(e))] for e in local])
        assert local_edges == region['block_edges']
        ss = [next(index[tuple(sorted(e))] for e in spokes if v in e) for v in region['base_vertices']]
        assert ss == region['spoke_edges']
        sets = [sorted(set(local_edges[j-1]+local_edges[j]+[ss[j]])) for j in range(5)]
        assert sets == region['zero_hitting_sets']
        charged = set.union(*(set(row) for row in sets))
        assert sorted(charged) == region['charged_edges'] and len(charged) == 150
        incidence = Counter(e for row in sets for e in row)
        assert max(incidence.values()) == 2 and len(sets) == 5
        # If the two blocks have nonzero projections, the paired ports are
        # alpha,alpha and beta,beta. Kirchhoff forces the spoke to zero.
        for alpha,beta in itertools.product((1,2,3),repeat=2):
            left = alpha ^ beta; right = alpha ^ beta
            assert left ^ right == 0
        assert region['lower_bound'] == (len(sets)+1)//2 == 3
        assert sum(initial[e] == 4 for e in charged) == 3
        assert all(any(initial[e] == 4 for e in row) for row in sets)
        charges.append(charged)
    assert len(charges) == 2 and charges[0].isdisjoint(charges[1])
    assert expected == set(index)
    # For any nonzero target, a quotient has precisely that nonzero value
    # in its kernel. Thus the six-zero lower bound applies to every color.
    for a in range(1,8):
        fixed = [q for q in range(1,8) if (q & a).bit_count()%2 == 0]
        y,z = fixed[:2]
        assert y ^ z == fixed[2]
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
    assert len(r['moves']) == 2 and [m['increment'] for m in r['moves']] == [3,4]
    for j,move in enumerate(r['moves']):
        C = sum(1 << e for e in move['edges']); obj.circuit(C)
        assert len(move['edges']) == (8,155)[j]
        assert all(current[e] != move['increment'] for e in move['edges'])
        after = [x ^ move['increment'] if C >> e & 1 else x for e,x in enumerate(current)]
        assert after == move['flow_after']; obj.flow(after)
        counts = [after.count(a) for a in range(1,8)]
        assert counts == move['color_sizes'] and min(counts) == counts[3] == 6
        if j == 0:
            oldM = {e for e,x in enumerate(current) if x == 4}
            newM = {e for e,x in enumerate(after) if x == 4}
            assert oldM-newM == {164} and newM-oldM == {112}
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
    data = json.loads((HERE/'petersen_free_minimum_obstruction.json').read_text())
    for source in data['sources']:
        assert hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256']
    obj = Check(data['graph']); obj.flow(data['initial_flow'])
    assert local_audit(data['graph']) == data['local_fourpole_audit']
    construction_and_bound(obj,data['graph'],data['initial_flow'])
    assert data['minimum_color_multiplicity'] == 6
    counts = [data['initial_flow'].count(a) for a in range(1,8)]
    assert counts == data['initial_color_sizes'] and min(counts) == counts[3] == 6
    tests = obj.connectivity(data['connectivity'])
    girth = data['girth_certificate']
    assert girth['girth'] == 6 and len(girth['shortest_circuit_edges']) == 6
    obj.circuit(sum(1 << e for e in girth['shortest_circuit_edges']))
    assert girth['petersen_four_poles'] == 0
    # The standard Petersen four-pole contains this pentagon. No graph
    # of girth six can contain the four-pole, even as a noninduced subgraph.
    petersen = {(2,3),(3,4),(2,7),(3,8),(4,9),(5,7),(6,8),(7,9),(5,8),(6,9)}
    pentagon = [2,3,8,5,7]
    assert all(tuple(sorted((v,pentagon[(i+1)%5]))) in petersen for i,v in enumerate(pentagon))
    failures(obj,data); verify_repair(obj,data)
    assert all(len(r['component_vertices']) == 1 for r in data['matching_failures'])
    print('214-vertex simple cubic graph: connected, girth six, cyclic edge connectivity exactly four.')
    print('No Petersen four-pole: its pentagon is forbidden by girth.')
    print('Independent proper-coloring enumeration: 108 local flows; all paired ports agree.')
    print('Two disjoint regions prove every flow color has at least six edges; the saved flow attains six.')
    print('All',tests,'edge triples checked: exactly 214 cuts, all vertex stars; no one- or two-edge cut.')
    print('Seven singleton unmatched-component obstructions and all 21 paired-cut certificates verified.')
    print('Eight-circuit plus 155-circuit repair verified, retaining minimum six and producing a five-layer cover.')


if __name__ == '__main__':
    main()
