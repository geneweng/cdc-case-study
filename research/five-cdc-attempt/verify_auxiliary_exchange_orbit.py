#!/usr/bin/env python3
"""Independent cycle-space census, cherry audit, and full graph verification.

No constructor or earlier verifier is imported. Fixed-layer covers are
reconstructed from three binary cycles, not vertex-triangle assignments.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
Q = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
AUX = Q[4:]
EVEN = [h for h in range(32) if h.bit_count() % 2 == 0]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]


def xor(xs):
    a = 0
    for x in xs:
        a ^= x
    return a


def prefixes(rs):
    assert xor(rs) == 0
    return [xor(rs[:i]) for i in range(len(rs))]


def bad(rs, marked=None):
    p = prefixes(rs)
    return len({p[i] for i in (range(len(rs)) if marked is None else marked)}) == 8


def decode(cw):
    return [Q[int(c)] for c in cw]


def stars(n, edges):
    result = [[] for _ in range(n)]
    for e, uv in enumerate(edges):
        for v in uv:
            assert 0 <= v < n
            result[v].append(e)
    return result


def valid(n, edges, values, alphabet):
    assert len(values) == len(edges) and all(a in alphabet for a in values)
    assert all(xor(values[e] for e in s) == 0 for s in stars(n, edges))


def circuit(edges):
    degree = Counter(v for uv in edges for v in uv)
    assert degree and set(degree.values()) == {2}
    seen, todo = set(), [next(iter(degree))]
    while todo:
        v = todo.pop()
        if v in seen:
            continue
        seen.add(v)
        for u, w in edges:
            if u == v and w not in seen:
                todo.append(w)
            if w == v and u not in seen:
                todo.append(u)
    assert seen == set(degree)


def junction_table(kind):
    triangles = [(a, b, c) for a, b, c in itertools.product(Q, repeat=3) if a ^ b ^ c == 0]
    if kind == 'semi':
        states = [(a, b, c, b, r) for a, c, r in triangles for b in Q]
    else:
        ends = {r: [(a, b) for a, b, c in triangles if c == r] for r in Q}
        states = [(a, b, c, d, x, y, r) for x, y, r in triangles
                  for a, c in ends[x] for b, d in ends[y]]
    table = defaultdict(set)
    for row in states:
        z = sum((a & 1) << i for i, a in enumerate(row[:4]))
        table[row[-1], z].add(row[0] ^ row[1])
    for (r, z), allowed in table.items():
        p = (z & 1) ^ (z >> 1 & 1)
        expected = {h for h in EVEN if h & 1 == p}
        if z & 3 == 3:
            expected.discard(30)
        if z & 12 == 12:
            expected.discard(30 ^ r)
        assert allowed == expected
    assert len(table) == (80 if kind == 'blowup' else 40)
    return table


def reconstruct(g):
    n, base, cycles = g['base_vertices'], g['base_edges'], g['selected_cycles']
    q = sum(map(len, cycles))
    assert g['pieces'] == q and all(3 <= len(c) <= 11 for c in cycles)
    assert len(g['blocks']) == len(g['junctions']) == q
    assert len(g['regions']) == len(g['regional_extensions']) == len(g['profile_names']) == len(cycles)
    assert len({v for c in cycles for v in c}) == q
    assert all(len(s) == 3 for s in stars(n, base))
    assert len({tuple(sorted(e)) for e in base}) == len(base) and all(u != v for u, v in base)
    seen, todo = {0}, [0]
    adjacency = [[] for _ in range(n)]
    for u, v in base:
        adjacency[u].append(v)
        adjacency[v].append(u)
    for u in todo:
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    assert len(seen) == n
    removed = {tuple(sorted((c[i], c[(i+1) % len(c)]))) for c in cycles for i in range(len(c))}
    outside = [i for i, uv in enumerate(base) if tuple(sorted(uv)) not in removed]
    assert outside == g['outside_base_edge_ids']
    edges, js = [tuple(base[e]) for e in outside], []
    m = len(edges)
    for i in range(q):
        edges.extend((n+8*i+u-2, n+8*i+v-2) for u, v in INTERNAL)
    offset = 0
    for cycle in cycles:
        for j, v in enumerate(cycle):
            i, prev = offset+j, offset+(j-1) % len(cycle)
            a, b, c, d = n+8*prev+2, n+8*prev+3, n+8*i, n+8*i+4
            start = len(edges)
            stem = next(e for e in range(m) if v in edges[e])
            if g['construction'] == 'blowup':
                u, w = n+8*q+2*i, n+8*q+2*i+1
                edges.extend([(a, u), (b, w), (c, u), (d, w), (u, v), (w, v)])
                ids = list(range(start, start+6))+[stem]
            else:
                edges.extend([(a, v), (b, d), (c, v)])
                ids = [start, start+1, start+2, start+1, stem]
            js.append({'vertex': v, 'left_piece': prev, 'right_piece': i, 'edges': ids})
        offset += len(cycle)
    owner = list(range(n))+[n+i for i in range(q) for _ in range(8)]
    if g['construction'] == 'blowup':
        owner.extend(range(n+q, n+3*q))
    assert g['edges'] == [list(uv) for uv in edges] and g['junctions'] == js
    assert g['vertices'] == len(owner) and g['vertex_map'] == owner
    assert all(len(s) == 3 for s in stars(len(owner), edges))
    assert len({tuple(sorted(e)) for e in edges}) == len(edges) and all(u != v for u, v in edges)
    for i, b in enumerate(g['blocks']):
        assert b['vertices'] == list(range(n+8*i, n+8*i+8))
        assert b['edge_representatives'][:10] == list(range(m+10*i, m+10*i+10))
        for e, v in zip(b['edge_representatives'][10:], (n+8*i+2, n+8*i+3, n+8*i, n+8*i+4)):
            assert v in edges[e] and e >= m+10*q
    kept = list(range(m))+list(range(m+10*q, len(edges)))
    assert g['kept_edge_ids'] == kept
    assert g['quotient_edges'] == [[owner[edges[e][0]], owner[edges[e][1]]] for e in kept]
    assert g['quotient_vertices'] == max(owner)+1
    co = list(range(n))
    for c in cycles:
        for v in c:
            co[v] = min(c)
    names = {v: i for i, v in enumerate(sorted(set(co)))}
    co = [names[v] for v in co]
    assert g['core'] == {'vertices': len(names), 'vertex_map': co,
                         'edges': [[co[u], co[v]] for u, v in edges[:m]]}
    return m


def survivors(rs, table):
    allowed = {h for h in EVEN if not h & 1}
    at = 0
    for r in rs:
        allowed &= {h ^ at for h in table[r, 15]}
        at ^= r
    assert at == 0
    return allowed


def kernel_image(core, regions, pairs, rec):
    t, target = rec['swap_pair'], regions[rec['target_region']]
    affected = [e for e, a in enumerate(pairs) if (a & t).bit_count() == 1]
    index = {e: j for j, e in enumerate(affected)}
    rows = []
    for star in stars(core['vertices'], core['edges']):
        rows.append(xor(1 << index[e] for e in star if e in index))
    for fixed in rec['protected_pairings']:
        hs = regions[fixed['region']]['incidences']
        rows.extend((1 << index[hs[i]//2]) ^ (1 << index[hs[j]//2]) for i, j in fixed['pairs'])
    echelon = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot in echelon:
                row ^= echelon[pivot]
            else:
                echelon[pivot] = row
                break
    image = {0}
    for free in range(len(affected)):
        if free in echelon:
            continue
        vector = 1 << free
        for pivot in sorted(echelon):
            if (vector & echelon[pivot]).bit_count() % 2:
                vector |= 1 << pivot
        assert all((vector & row).bit_count() % 2 == 0 for row in rows)
        boundary = sum(1 << i for i, h in enumerate(target['incidences'])
                       if h//2 in index and vector >> index[h//2] & 1)
        image |= {s ^ boundary for s in image}
    return image, affected, index, rows

def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def cycle_space(n, edges):
    echelon = {}
    for row in [xor(1 << e for e in star) for star in stars(n, edges)]:
        while row:
            p = row.bit_length()-1
            if p not in echelon:
                echelon[p] = row
                break
            row ^= echelon[p]
    space = [0]
    for free in range(len(edges)):
        if free in echelon:
            continue
        v = 1 << free
        for p in sorted(echelon):
            if (v & echelon[p]).bit_count() % 2:
                v |= 1 << p
        space += [a ^ v for a in space]
    return sorted(space)


def is_circuit(edges):
    degrees = Counter(v for uv in edges for v in uv)
    if not degrees or set(degrees.values()) != {2}:
        return False
    seen, todo = {next(iter(degrees))}, [next(iter(degrees))]
    for u in todo:
        for v, w in edges:
            if u in (v, w):
                other = v ^ w ^ u
                if other not in seen:
                    seen.add(other)
                    todo.append(other)
    return len(seen) == len(degrees)


def verify_factor(core, fixed, rec):
    edges = [core['edges'][e] for e in rec['edges']]
    support = sum(1 << j for j, e in enumerate(rec['edges']) if e in fixed)
    space = cycle_space(core['vertices'], edges)
    assert support in space
    covers, full = [], (1 << len(edges))-1
    for a, b, c in itertools.product(space, repeat=3):
        d = support ^ a ^ b ^ c
        # XOR fixes whether the auxiliary edge count is odd or even.
        # Excluding zero and counts >=3 leaves exactly 1 on F, 2 elsewhere.
        if a | b | c | d != full or (a & b & (c | d)) | (c & d & (a | b)):
            continue
        covers.append(tuple((support >> e & 1) | (2*(a >> e & 1)) | (4*(b >> e & 1))
                            | (8*(c >> e & 1)) | (16*(d >> e & 1)) for e in range(len(edges))))
    covers.sort()
    assert len(covers) == len(set(covers))
    assert [''.join(str(Q.index(a)) for a in row) for row in covers] == rec['cover_words']
    lookup = {c: i for i, c in enumerate(covers)}
    neighbors, singles, hist = [], [], Counter()
    for values in covers:
        rows, one = [], []
        for t in AUX:
            active = [i for i, a in enumerate(values) if (a & t).bit_count() == 1]
            kernel = cycle_space(core['vertices'], [edges[i] for i in active])
            row, single = [], []
            for vector in kernel:
                selected = {e for j, e in enumerate(active) if vector >> j & 1}
                after = tuple(a ^ t if e in selected else a for e, a in enumerate(values))
                row.append(lookup[after])
                if is_circuit([edges[e] for e in selected]):
                    single.append(lookup[after])
            rows.append(sorted(row))
            one.append(sorted(single))
            hist[len(kernel).bit_length()-1] += 1
        neighbors.append(rows)
        singles.append(one)
    assert digest(neighbors) == rec['neighbor_sha256']
    assert digest(singles) == rec['single_neighbor_sha256']
    assert [list(x) for x in sorted(hist.items())] == rec['generator_histogram']
    seen, todo = {0}, [0]
    for i in todo:
        for j in itertools.chain.from_iterable(singles[i]):
            if j not in seen:
                seen.add(j)
                todo.append(j)
    assert len(seen) == len(covers) and rec['circuit_components'] == [len(covers)]
    print('Factor:',len(covers),'covers; independently reconstructed from',len(space),'binary cycles.',flush=True)
    return {'edges': rec['edges'], 'ports': rec['ports'], 'states': covers,
            'neighbors': neighbors, 'singles': singles}


def verify_census(saved, table):
    rec, core = saved['census'], saved['core']
    factors = [verify_factor(core, set(saved['fixed_layer_edges']), f) for f in rec['factors']]
    a, b = factors
    assert [len(f['states']) for f in factors] == [1536, 864]
    assert sorted(e for f in factors for e in f['edges']) == list(range(len(core['edges'])))
    outside = [{v for e in f['edges'] for v in core['edges'][e] if v} for f in factors]
    assert not outside[0] & outside[1] and outside[0] | outside[1] == set(range(1,core['vertices']))
    assert [sorted(vs) for vs in outside] == [f['vertices'] for f in rec['factors']]
    assert sorted(i for f in factors for i, _ in f['ports']) == list(range(11))
    for f in factors:
        assert f['ports'] == [[i, f['edges'].index(h//2)] for i,h in enumerate(saved['target_incidences']) if h//2 in f['edges']]
    nb = len(b['states'])
    allowed_table = {(r, p):sum(1 << (h ^ p) for h in table[r,15]) for r in AUX for p in EVEN if not p & 1}
    rejected, rs = set(), [0]*11
    for i, x in enumerate(a['states']):
        for p, j in a['ports']:
            rs[p] = x[j]
        for k, y in enumerate(b['states']):
            for p, j in b['ports']:
                rs[p] = y[j]
            allowed, prefix = sum(1 << h for h in EVEN if not h & 1), 0
            for r in rs:
                allowed &= allowed_table[r,prefix]
                prefix ^= r
            assert prefix == 0
            if not allowed:
                rejected.add(i*nb+k)
    assert len(rejected) == rec['bad_covers'] == 183768
    assert digest(sorted(rejected)) == rec['bad_state_ids_sha256']
    def cover(state):
        i,j = divmod(state,nb)
        values = [0]*len(core['edges'])
        for f, at in ((a,i),(b,j)):
            for e,r in zip(f['edges'],f['states'][at]):
                values[e] = r
        return values
    def single_neighbors(state):
        i,j = divmod(state,nb)
        return {ii*nb+j for row in a['singles'][i] for ii in row} | {i*nb+jj for row in b['singles'][j] for jj in row}
    hard = {s for s in rejected if single_neighbors(s) <= rejected}
    assert len(hard) == 48
    for state in hard:
        i,j = divmod(state,nb)
        assert all(ii*nb+jj in rejected for t in range(6) for ii in a['neighbors'][i][t] for jj in b['neighbors'][j][t])
        assert single_neighbors(state)-hard  # These neighbors are bad with a one-circuit escape.
    words = sorted(''.join(str(Q.index(x)) for x in cover(s)) for s in hard)
    assert words == rec['distance_two_cover_words']
    assert rec['total_covers'] == len(a['states'])*nb == 1327104
    histogram = [[0,1143336],[1,183720],[2,48]]
    assert rec['distance_histograms'] == {'even_subgraph':histogram,'single_circuit':histogram}
    canonical = lambda values:min(''.join(str(Q.index((r&1)|sum(1<<p[i-1] for i in range(1,5) if r>>i&1))) for r in values)
                                for p in itertools.permutations(range(1,5)))
    classes = Counter(canonical(decode(w)) for w in words)
    assert sorted(classes.items()) == [(r['cover_word'],r['label_orbit_size']) for r in rec['hard_representatives']]
    assert len(classes) == 2 and set(classes.values()) == {24}
    for r in rec['hard_representatives']:
        values = decode(r['cover_word'])
        assert len(r['moves']) == 2
        for step, move in enumerate(r['moves']):
            assert all((values[e] & move['swap_pair']).bit_count() == 1 for e in move['edges'])
            circuit([core['edges'][e] for e in move['edges']])
            values = [x ^ move['swap_pair'] if e in move['edges'] else x for e,x in enumerate(values)]
            valid(core['vertices'],core['edges'],values,Q)
            assert values == decode(move['cover_word_after'])
            assert bool(survivors([values[h//2] for h in saved['target_incidences']],table)) == bool(step)
    print('All 1,327,104 covers: distance histogram',histogram,'for both move types.',flush=True)


def verify_cherries(rec, table):
    cherries = [((2,6),6),((1,7),10),((5,8),12)]
    rest_ports = [0,3,4,9,10]
    assert rec['cherries'] == [[list(p),t] for p,t in cherries] and rec['rest_ports'] == rest_ports
    domains = [sorted((a,a^root) for a in AUX if a^root in AUX) for _,root in cherries]
    assert all(len(x)==4 for x in domains)
    hist, maxima, records, hard = Counter(), Counter(), [], []
    for rest in itertools.product(AUX,repeat=5):
        if xor(rest):
            continue
        words, good = [], []
        for bits in range(64):
            rs = [0]*11
            for i,r in zip(rest_ports,rest):
                rs[i] = r
            for k,((i,j),_) in enumerate(cherries):
                rs[i],rs[j] = domains[k][bits>>(2*k)&3]
            words.append(rs)
            if survivors(rs,table):
                good.append(bits)
        assert good
        distances = [min((bits ^ g).bit_count() for g in good) for bits in range(64)]
        for bits,rs in enumerate(words):
            for bit in range(6):
                ports,root = cherries[bit//2]
                t = root if bit%2==0 else 30^root
                assert words[bits^(1<<bit)] == [r^t if i in ports else r for i,r in enumerate(rs)]
            if distances[bits] == 2:
                hard.append((list(rest),bits,rs))
        hist.update(distances)
        maxima[max(distances)] += 1
        records.append([list(rest),''.join(map(str,distances))])
    assert rec['closed_rest_words'] == len(records) == 960
    assert rec['boundary_states'] == 61440
    assert rec['distance_histogram'] == [list(r) for r in sorted(hist.items())] == [[0,53314],[1,8109],[2,17]]
    assert rec['maximum_by_rest_histogram'] == [list(r) for r in sorted(maxima.items())] == [[0,65],[1,886],[2,9]]
    assert rec['distance_records_sha256'] == digest(records)
    assert [(r['rest'],r['bits'],r['boundary']) for r in rec['distance_two_states']] == hard
    for row in rec['distance_two_states']:
        rs = row['boundary']
        assert len(row['moves']) == 2
        for k,move in enumerate(row['moves']):
            rs = [r ^ move['swap_pair'] if i in move['ports'] else r for i,r in enumerate(rs)]
            assert rs == move['boundary_after'] and bool(survivors(rs,table)) == bool(k)
    print('Independent local-relation/Hamming-distance check: all 61,440 cherry states need at most two moves.',flush=True)


def verify_full(g, representative, table):
    m = reconstruct(g)
    core, edges, n = g['core'], g['edges'], g['vertices']
    initial, values = list(map(int,g['initial_flow_word'])), decode(g['original_core_cover_word'])
    valid(n,edges,initial,range(1,8))
    valid(core['vertices'],core['edges'],values,Q)
    assert [a&1 for a in values] == [a&1 for a in initial[:m]]
    assert g['selected_cycles'] == [list(range(11))]
    incidences = [2*j['edges'][-1]+edges[j['edges'][-1]].index(j['vertex']) for j in g['junctions']]
    assert g['regions'] == [{'hub':0,'incidences':incidences,'marked_cuts':list(range(11)),
                             'critical':True,'junction_indices':list(range(11))}]
    for j in g['junctions']:
        assert sum((initial[e]&1)<<i for i,e in enumerate(j['edges'][:4])) == 15
    def project(pairs):
        if g['name']=='native':
            return pairs
        cut = g['petersen_two_sum']['core_cut_edges']
        assert pairs[cut[0]] == pairs[cut[1]]
        return [pairs[cut[0]]]+pairs[:21]
    assert project(values) == decode(representative['cover_word'])
    assert not survivors([values[h//2] for h in incidences],table)
    checked = 0
    for t in AUX:
        image,_,_,_ = kernel_image(core,g['regions'],values,{'swap_pair':t,'target_region':0,'protected_pairings':[]})
        rs = [values[h//2] for h in incidences]
        for mask in image:
            assert not survivors([r^t if mask>>i&1 else r for i,r in enumerate(rs)],table)
            checked += 1
    assert len(g['core_cover_moves']) == 2
    for step,(move,rep_move) in enumerate(zip(g['core_cover_moves'],representative['moves'])):
        t, selected = move['swap_pair'],move['edges']
        assert t==rep_move['swap_pair'] and selected==sorted(set(selected))
        assert all((values[e]&t).bit_count()==1 for e in selected)
        circuit([core['edges'][e] for e in selected])
        following = [a^t if e in selected else a for e,a in enumerate(values)]
        valid(core['vertices'],core['edges'],following,Q)
        assert [a&1 for a in values] == [a&1 for a in following]
        assert following == decode(move['cover_word_after'])
        assert project(following) == decode(rep_move['cover_word_after'])
        assert bool(survivors([following[h//2] for h in incidences],table)) == bool(step)
        values = following
    assert values == decode(g['changed_core_cover_word'])
    quotient = decode(g['quotient_cover_word'])
    valid(g['quotient_vertices'],g['quotient_edges'],quotient,Q)
    assert quotient[:m] == values and [a&1 for a in quotient] == [initial[e]&1 for e in g['kept_edge_ids']]
    extension = g['regional_extensions'][0]
    letters = [[values[j['edges'][-1]],15] for j in g['junctions']]
    allowed = survivors([r for r,z in letters],table)
    assert extension['letters'] == letters and extension['surviving_charges'] == sorted(allowed)
    assert extension['chosen_charge'] in allowed
    flow = initial.copy()
    assert len(g['moves']) <= 2*g['pieces'] == 22
    for move in g['moves']:
        selected,delta = move['edges'],move['increment']
        assert len(selected)==len(set(selected))==5 and 1<=delta<=7
        assert set(selected)<=set(g['blocks'][move['piece']]['edge_representatives'][:10])
        circuit([edges[e] for e in selected])
        for e in selected:
            assert flow[e]!=delta
            flow[e]^=delta
        valid(n,edges,flow,range(1,8))
    assert flow==list(map(int,g['final_flow_word']))
    assert all(flow[e]==initial[e] for e in g['kept_edge_ids'])
    cover = decode(g['cover_word'])
    valid(n,edges,cover,Q)
    assert [a&1 for a in cover] == [a&1 for a in flow]
    assert [cover[e] for e in g['kept_edge_ids']] == quotient
    if g['core_has_four_flow']:
        assert g['name']=='native'
        valid(core['vertices'],core['edges'],list(map(int,g['core_four_flow_word'])),(1,2,3))
    else:
        assert g['name']=='petersen_attachment'
        attachment = g['petersen_two_sum']
        local = {core['vertex_map'][v]:i for i,v in enumerate(attachment['vertices'])}
        cut = [e for e,(u,v) in enumerate(core['edges']) if (u in local)!=(v in local)]
        assert cut==attachment['core_cut_edges'] and len(cut)==2
        restored = [tuple(sorted((local[u],local[v]))) for u,v in core['edges'] if u in local and v in local]
        restored.append(tuple(sorted(local[next(v for v in core['edges'][e] if v in local)] for e in cut)))
        pet = [(i,(i+1)%5) for i in range(5)]+[(i,i+5) for i in range(5)]+[(i+5,(i+2)%5+5) for i in range(5)]
        assert sorted(restored)==sorted(tuple(sorted(e)) for e in pet)
        evens = cycle_space(10,pet)
        assert len(evens)==64 and not any(a|b==(1<<15)-1 for a in evens for b in evens)
    print(g['construction'],'class',g['representative'],g['name'],n,'vertices;',len(g['moves']),'internal pentagons.',flush=True)
    return checked


def main():
    saved = json.loads((HERE/'auxiliary_exchange_orbit.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE/src['file']).read_bytes()).hexdigest() == src['sha256']
    old = json.loads((HERE/'actual_core_exchange_obstruction.json').read_text())['examples'][0]
    assert saved['core']==old['core'] and saved['target_incidences']==old['regions'][0]['incidences']
    assert saved['fixed_layer_edges']==[e for e,a in enumerate(decode(old['original_core_cover_word'])) if a&1]
    tables = {k:junction_table(k) for k in ('blowup','semi')}
    assert all(tables['blowup'][r,15]==tables['semi'][r,15] for r in AUX)
    verify_census(saved,tables['blowup'])
    verify_cherries(saved['cherry_audit'],tables['semi'])
    reps = saved['census']['hard_representatives']
    assert [(g['construction'],g['representative'],g['name']) for g in saved['examples']] == [
        (k,i,name) for k in ('blowup','semi') for i in range(2) for name in ('native','petersen_attachment')]
    for g in saved['examples']:
        if g['name']=='native':
            assert g['core']==saved['core'] and g['base_edges']==old['base_edges']
    checks = sum(verify_full(g,reps[g['representative']],tables[g['construction']]) for g in saved['examples'])
    print('Full-graph initial exchange images checked:',checks)
    print('PASS: complete cover space, exact circuit distances, universal cherry audit, and eight graph completions.')


if __name__=='__main__':
    main()
