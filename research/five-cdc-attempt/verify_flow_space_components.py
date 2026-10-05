#!/usr/bin/env python3
"""Verify the independent affine enumeration and all concrete certificates.

No constructor or previous verifier is imported. Binary cycle bases, graph
structure, actual circuit neighborhoods, and decoded covers are checked here.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def parity(values):
    out = 0
    for value in values: out ^= value
    return out


def valid(n, edges, values, alphabet):
    assert len(values) == len(edges) and all(v in alphabet for v in values)
    assert all(parity(values[e] for e,uv in enumerate(edges) if v in uv) == 0 for v in range(n))


def graph_properties(g):
    n, edges = g['vertices'], g['edges']
    assert len(edges) == len({tuple(sorted(e)) for e in edges}) == 3*n//2
    assert all(0 <= u < n and 0 <= v < n and u != v for u,v in edges)
    assert Counter(v for uv in edges for v in uv) == Counter({v:3 for v in range(n)})
    def component(removed):
        adjacency = [set() for _ in range(n)]
        for e,(u,v) in enumerate(edges):
            if e not in removed: adjacency[u].add(v); adjacency[v].add(u)
        seen, queue = {0}, [0]
        for v in queue:
            for w in adjacency[v]-seen: seen.add(w); queue.append(w)
        return seen
    assert len(component(set())) == n
    for size in range(1,5 if 'flower5_vertex_map' in g else 4):
        for removed in itertools.combinations(range(len(edges)),size):
            count = len(component(set(removed)))
            assert count == n or size == 3 and count in (1,n-1) or size == 4 and count in (1,2,n-2,n-1)
    adj = [set() for _ in range(n)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    girth = n+1
    for root in range(n):
        distance, parent, queue = {root:0}, {root:-1}, [root]
        for v in queue:
            for w in adj[v]:
                if w not in distance: distance[w] = distance[v]+1; parent[w] = v; queue.append(w)
                elif parent[v] != w: girth = min(girth,distance[v]+distance[w]+1)
    if g['flow_dimension'] == 3: assert girth >= 5
    return girth


def count_four_poles(n, edges):
    # Build Petersen independently, then delete its adjacent vertices 0 and 1.
    pe = [(i,(i+1)%5) for i in range(5)]+[(i,i+5) for i in range(5)]+[(i+5,(i+2)%5+5) for i in range(5)]
    pa = {v:set() for v in range(2,10)}
    for u,v in pe:
        if min(u,v) >= 2: pa[u].add(v); pa[v].add(u)
    adj = [set() for _ in range(n)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    found, mapping = set(), {}
    def extend():
        if len(mapping) == 8:
            found.add(tuple(sorted(mapping.values()))); return
        v = max((v for v in pa if v not in mapping),key=lambda v:(len(pa[v] & mapping.keys()),len(pa[v]),-v))
        candidates = set(range(n))-set(mapping.values())
        for u,w in mapping.items():
            candidates &= adj[w] if u in pa[v] else set(range(n))-adj[w]
        for w in sorted(candidates): mapping[v] = w; extend(); del mapping[v]
    extend()
    return len(found)


def subspace_key(rows):
    basis = {}
    for x in rows:
        for p in sorted(basis,reverse=True):
            if x >> p & 1: x ^= basis[p]
        if x: basis[x.bit_length()-1] = x
    for p in sorted(basis):
        for q in sorted(basis):
            if q > p and basis[q] >> p & 1: basis[q] ^= basis[p]
    return sum(basis[p] << (16*i) for i,p in enumerate(sorted(basis)))


def all_cycles(basis,n,edges):
    masks = [0]
    for b in basis: masks.extend([v ^ b for v in masks.copy()])
    assert len(basis) == len(edges)-n+1 and len(set(masks)) == len(masks)
    for mask in masks:
        assert all(sum(mask >> e & 1 for e,uv in enumerate(edges) if v in uv) % 2 == 0 for v in range(n))
    return masks


def circuit(n,edges,selected):
    degree = Counter(v for e in selected for v in edges[e])
    if not degree or set(degree.values()) != {2}: return False
    reached, queue = {next(iter(degree))}, [next(iter(degree))]
    for v in queue:
        for e in selected:
            if v in edges[e]:
                for w in edges[e]:
                    if w not in reached: reached.add(w); queue.append(w)
    return reached == set(degree)


def has_lift(flow,n,edges):
    # Direct graph-component demands for the fourth coordinate.
    for first in range(1,8):
        second = next(x for x in range(1,8) if x != first)
        third = next(x for x in range(1,8) if x not in (first,second,first ^ second))
        fixed = [e for e,x in enumerate(flow) if (x & first).bit_count() % 2]
        rhs = [0]*n
        for e in fixed:
            x = flow[e]
            value = 1 ^ (((x & second).bit_count() % 2) * ((x & third).bit_count() % 2))
            for v in edges[e]: rhs[v] ^= value
        adjacency = [set() for _ in range(n)]
        for e,(u,v) in enumerate(edges):
            if e not in fixed: adjacency[u].add(v); adjacency[v].add(u)
        pending, good = set(range(n)), True
        while pending:
            root = min(pending); pending.remove(root); queue = [root]
            for v in queue:
                for w in adjacency[v] & pending: pending.remove(w); queue.append(w)
            if parity(rhs[v] for v in queue): good = False; break
        if good: return True
    return False


def verify_lift(w,n,edges):
    valid(n,edges,w['flow'],range(1,8))
    forms = w['coordinate_functionals']
    assert len({parity(forms[i] for i in range(3) if mask >> i & 1) for mask in range(8)}) == 8
    transformed = [sum(((x & form).bit_count() % 2) << i for i,form in enumerate(forms)) for x in w['flow']]
    assert transformed == w['transformed_flow']
    palette = [4,5,6,15,8]
    for e,(value,pair) in enumerate(zip(transformed,w['cover_pairs'])):
        assert pair.bit_count() == 2 and 0 < pair < 32
        assert parity(palette[i] for i in range(5) if pair >> i & 1) == value ^ (8*(w['fourth_coordinate_mask'] >> e & 1))
    valid(n,edges,[w['fourth_coordinate_mask'] >> e & 1 for e in range(len(edges))],(0,1))
    valid(n,edges,w['cover_pairs'],[x for x in range(32) if x.bit_count() == 2])
    assert has_lift(w['flow'],n,edges)


def circuit_crosscheck(g,cycles,records):
    n,edges,k = g['vertices'],g['edges'],g['flow_dimension']
    cs = [(q,[e for e in range(len(edges)) if mask >> e & 1]) for q,mask in enumerate(cycles) if mask]
    cs = [(q,s) for q,s in cs if circuit(n,edges,s)]
    labels = {state:component for state,component,d in struct.iter_unpack('<QQQ',records)}
    adjacency = {state:set() for state in labels}
    for state in labels:
        rows = [state >> (16*i) & 65535 for i in range(k)]
        flow = [sum(((cycles[row] >> e) & 1) << i for i,row in enumerate(rows)) for e in range(len(edges))]
        for q,selected in cs:
            used = {flow[e] for e in selected}
            for change in set(range(1,1 << k))-used:
                nxt = subspace_key([row ^ q if change >> i & 1 else row for i,row in enumerate(rows)])
                assert nxt in adjacency
                adjacency[state].add(nxt)
    pending, found = set(labels), []
    while pending:
        at = min(pending); pending.remove(at); queue = [at]
        for s in queue:
            for t in adjacency[s] & pending: pending.remove(t); queue.append(t)
        assert all(labels[s] == min(queue) for s in queue)
        found.append(len(queue))
    return sorted(found)


def verify_hard(g,cycles,records):
    n,edges = g['vertices'],g['edges']; w = g['hard_flow_repair']
    distances = {state:d-1 for state,c,d in struct.iter_unpack('<QQQ',records)}
    assert distances[w['initial_space']] == 2
    current = w['initial_flow']; valid(n,edges,current,range(1,8)); assert not has_lift(current,n,edges)
    reverse = {mask:code for code,mask in enumerate(cycles)}
    def flow_space(flow):
        return subspace_key([reverse[sum(1 << e for e,x in enumerate(flow) if x >> i & 1)] for i in range(3)])
    assert flow_space(current) == w['initial_space']
    neighbors = 0
    for mask in cycles[1:]:
        selected = [e for e in range(len(edges)) if mask >> e & 1]
        if not circuit(n,edges,selected): continue
        for change in set(range(1,8))-{current[e] for e in selected}:
            after = [x ^ change if e in selected else x for e,x in enumerate(current)]
            assert not has_lift(after,n,edges)
            neighbors += 1
    for i,move in enumerate(w['moves']):
        assert circuit(n,edges,move['edges'])
        assert all(current[e] != move['increment'] for e in move['edges'])
        current = [x ^ move['increment'] if e in move['edges'] else x for e,x in enumerate(current)]
        assert current == move['flow_after']; valid(n,edges,current,range(1,8))
        if i+1 == len(w['moves']) or w['moves'][i+1]['round'] != move['round']:
            assert flow_space(current) == w['rounds'][move['round']-1]['target_space']
    assert current == w['final_lift']['flow'] and len(w['moves']) == 2
    verify_lift(w['final_lift'],n,edges)
    # Check the two reported shared planes and their decreasing fiber distances.
    previous = w['initial_space']
    for i,step in enumerate(w['rounds']):
        def space(state):
            rows = [state >> (16*j) & 65535 for j in range(3)]
            return {parity(rows[j] for j in range(3) if mask >> j & 1) for mask in range(8)}
        assert set(step['fixed_cycles']) <= space(previous) & space(step['target_space'])
        assert distances[step['target_space']] == 1-i
        assert step['circuits'] == sum(m['round'] == i+1 for m in w['moves'])
        previous = step['target_space']
    print('Directly excluded all',neighbors,'one-circuit repairs; verified the two-circuit escape and cover.',flush=True)


def gaussian(n,k):
    a = b = 1
    for i in range(k): a *= (1 << n)-(1 << i); b *= (1 << k)-(1 << i)
    return a//b


def main():
    saved = json.loads((HERE/'flow_space_components.json').read_text())
    for source in saved['sources']:
        assert hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256']
    compiler = shutil.which('c++') or shutil.which('g++')
    with tempfile.TemporaryDirectory(prefix='cdc-flow-component-check-') as directory:
        binary, record_path = Path(directory)/'verifier', Path(directory)/'states.bin'
        subprocess.run([compiler,'-std=c++17','-O3','-Wall','-Wextra','-pedantic',str(HERE/'verify_flow_space_components.cpp'),'-o',str(binary)],check=True)
        for g in saved['graphs']:
            n,edges,basis,k = g['vertices'],g['edges'],g['cycle_basis'],g['flow_dimension']
            girth = graph_properties(g)
            assert count_four_poles(n,edges) == g['petersen_four_poles']
            cycles = all_cycles(basis,n,edges)
            data = '\n'.join([f'{n} {len(edges)} {len(basis)} {k}']+[f'{u} {v}' for u,v in edges]+list(map(str,basis)))+'\n'
            result = json.loads(subprocess.check_output([str(binary),str(record_path)],input=data,text=True))
            old = g['census']
            for field in ('full_support_spaces','fibers','components','fiber_distance_histogram','fiber_size_histogram'):
                assert result[field] == old[field],(g['name'],field)
            assert result['lower_spaces_enumerated'] == gaussian(len(basis),k-1)
            assert old['subspaces_enumerated'] == gaussian(len(basis),k)
            records = record_path.read_bytes()
            assert len(records) == 24*old['full_support_spaces']
            assert hashlib.sha256(records).hexdigest() == old['state_records_sha256']
            assert [state for state,c,d in struct.iter_unpack('<QQQ',records) if d > 2] == old['hard_spaces']
            components = {c[2] for c in result['components']}
            assert {w['component_key'] for w in g['component_cover_witnesses']} == components
            wanted = {w['space_key'] for w in g['component_cover_witnesses']}
            selected = {state:(c,d) for state,c,d in struct.iter_unpack('<QQQ',records) if state in wanted}
            for witness in g['component_cover_witnesses']:
                assert selected[witness['space_key']] == (witness['component_key'],1)
                rows = [witness['space_key'] >> (16*i) & 65535 for i in range(k)]
                assert witness['flow'] == [sum(((cycles[row] >> e) & 1) << i for i,row in enumerate(rows)) for e in range(len(edges))]
                verify_lift(witness,n,edges)
            if n <= 10:
                check = circuit_crosscheck(g,cycles,records)
                assert check == sorted(c[0] for c in result['components'])
            if 'flower5_vertex_map' in g:
                target = []
                for i in range(5): target += [(4*i,4*i+j) for j in (1,2,3)]+[(4*i+1,4*((i+1)%5)+1)]
                for i in range(4): target += [(4*i+j,4*(i+1)+j) for j in (2,3)]
                target += [(18,3),(19,2)]
                mapping = g['flower5_vertex_map']
                assert sorted(mapping) == list(range(20))
                assert {tuple(sorted((mapping[u],mapping[v]))) for u,v in edges} == {tuple(sorted(e)) for e in target}
                assert girth == 5 and g['petersen_four_poles'] == 0
                ring = {v for v in range(20) if mapping[v] % 4 == 1}
                assert sum((u in ring) != (v in ring) for u,v in edges) == g['cyclic_edge_connectivity'] == 5
                assert sum(u in ring and v in ring for u,v in edges) == len(ring) == 5
                assert sum(u not in ring and v not in ring for u,v in edges) >= 20-len(ring)
                verify_hard(g,cycles,records)
            print('Independent affine/circuit verification:',g['name'],result['full_support_spaces'],'spaces,',len(components),'components.',flush=True)
    print('All component records, affine distances, graph restrictions, and cover certificates pass.',flush=True)


if __name__ == '__main__':
    main()
