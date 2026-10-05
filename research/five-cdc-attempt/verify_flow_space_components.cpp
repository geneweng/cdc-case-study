// Independent enumeration via affine completion of lower-dimensional spaces.
// No constructor code is included. Success uses binary restriction matrices.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <unordered_map>
#include <vector>
using Word = uint64_t;
int vertices, edges_count, rank, dimension;
Word all_edges;
std::vector<std::pair<int,int>> edges;
std::vector<Word> cycles;
std::vector<unsigned> edge_rows;
std::vector<std::vector<Word>> consistency;

Word canonical(std::vector<unsigned> rows) {
    unsigned basis[16] = {};
    for (unsigned x : rows) {
        for (int p = rank-1; p >= 0; --p) if (x >> p & 1) {
            if (basis[p]) x ^= basis[p];
            else {
                basis[p] = x;
                for (int q = 0; q < rank; ++q) if (q != p && (basis[q] >> p & 1)) basis[q] ^= x;
                break;
            }
        }
    }
    // Reduce each new row against lower pivots, which need not be zero yet.
    for (int p = 0; p < rank; ++p) if (basis[p])
        for (int q = p+1; q < rank; ++q) if (basis[q] >> p & 1) basis[q] ^= basis[p];
    Word result = 0; int j = 0;
    for (int p = 0; p < rank; ++p) if (basis[p]) result |= Word(basis[p]) << (16*j++);
    assert(j == dimension);
    return result;
}
std::vector<unsigned> points(Word key) {
    std::vector<unsigned> result = {0};
    for (int j = 0; j < dimension; ++j) {
        unsigned row = key >> (16*j) & 65535;
        int count = result.size();
        for (int i = 0; i < count; ++i) result.push_back(result[i] ^ row);
    }
    std::sort(result.begin(), result.end()); return result;
}
bool has_lift(Word key) {
    if (dimension == 2) return true;
    auto p = points(key);
    for (unsigned first : p) if (first) {
        unsigned second = 0, third = 0;
        for (unsigned x : p) if (x && x != first) { second = x; break; }
        for (unsigned x : p) if (x && x != first && x != second && x != (first ^ second)) { third = x; break; }
        Word required = cycles[first] & ~(cycles[second] & cycles[third]);
        bool valid = true;
        for (Word equation : consistency[first]) if (__builtin_parityll(equation & required)) { valid = false; break; }
        if (valid) return true;
    }
    return false;
}

struct State { Word key; bool good; std::vector<int> fibers; };
std::vector<State> states;
std::vector<std::vector<int>> fibers;
std::unordered_map<Word,int> state_index;
uint64_t lower_spaces = 0;

void complete(unsigned a, unsigned b = 0) {
    ++lower_spaces;
    Word uncovered = all_edges & ~(cycles[a] | cycles[b]);
    assert(uncovered); // Independently excludes every lower-rank full-support space.
    unsigned equations[16] = {};
    bool impossible = false;
    for (int e = 0; e < edges_count; ++e) if (uncovered >> e & 1) {
        unsigned row = edge_rows[e] | (1u << rank);
        for (int p = rank-1; p >= 0; --p) if (row >> p & 1) {
            if (equations[p]) row ^= equations[p];
            else { equations[p] = row; row = 0; break; }
        }
        if (row) { impossible = true; break; }
    }
    if (impossible) return;
    auto solve = [&](unsigned free, bool homogeneous) {
        unsigned value = free;
        for (int p = 0; p < rank; ++p) if (equations[p]) {
            unsigned rhs = homogeneous ? 0 : equations[p] >> rank & 1;
            if (rhs ^ unsigned(__builtin_parity((equations[p] & ((1u << p)-1)) & value))) value |= 1u << p;
        }
        return value;
    };
    std::vector<unsigned> solutions = {solve(0, false)};
    for (int p = 0; p < rank; ++p) if (!equations[p]) {
        unsigned direction = solve(1u << p, true);
        int count = solutions.size();
        for (int i = 0; i < count; ++i) solutions.push_back(solutions[i] ^ direction);
    }
    std::vector<int> members;
    int fi = fibers.size();
    for (unsigned z : solutions) {
        if (z > (z ^ a) || (dimension == 3 && (z > (z ^ b) || z > (z ^ a ^ b)))) continue;
        assert(((cycles[a] | cycles[b] | cycles[z]) & all_edges) == all_edges);
        Word key = canonical(dimension == 2 ? std::vector<unsigned>{a,z} : std::vector<unsigned>{a,b,z});
        auto [it, added] = state_index.emplace(key, states.size());
        if (added) states.push_back({key, has_lift(key), {}});
        int at = it->second;
        members.push_back(at); states[at].fibers.push_back(fi);
    }
    assert(!members.empty()); fibers.push_back(members);
}

int main(int argc, char **argv) {
    assert(argc == 2);
    std::cin >> vertices >> edges_count >> rank >> dimension;
    assert(std::cin && rank <= 15 && edges_count < 64 && (dimension == 2 || dimension == 3));
    all_edges = (Word(1) << edges_count)-1;
    for (int e = 0; e < edges_count; ++e) { int u,v; std::cin >> u >> v; edges.push_back({u,v}); }
    cycles = {0}; edge_rows.resize(edges_count);
    for (int i = 0; i < rank; ++i) {
        Word basis; std::cin >> basis;
        for (int e = 0; e < edges_count; ++e) if (basis >> e & 1) edge_rows[e] |= 1u << i;
        int count = cycles.size();
        for (int j = 0; j < count; ++j) cycles.push_back(cycles[j] ^ basis);
    }
    consistency.resize(cycles.size());
    for (unsigned code = 1; code < cycles.size(); ++code) {
        unsigned basis[16] = {}; Word tags[16] = {};
        for (int e = 0; e < edges_count; ++e) if (cycles[code] >> e & 1) {
            unsigned row = edge_rows[e]; Word tag = Word(1) << e;
            for (int p = rank-1; p >= 0; --p) if (row >> p & 1) {
                if (basis[p]) { row ^= basis[p]; tag ^= tags[p]; }
                else { basis[p] = row; tags[p] = tag; tag = 0; break; }
            }
            if (tag) consistency[code].push_back(tag);
        }
    }
    for (unsigned a = 1; a < cycles.size(); ++a) {
        if (dimension == 2) complete(a);
        else for (unsigned b = a+1; b < cycles.size(); ++b) if ((a ^ b) > b) complete(a,b);
    }
    std::vector<int> component(states.size(), -1), distance(states.size(), -1);
    std::vector<std::array<Word,3>> summaries;
    std::vector<bool> used(fibers.size());
    for (int start = 0; start < int(states.size()); ++start) if (component[start] < 0) {
        int id = summaries.size(); std::array<Word,3> summary{0,0,states[start].key};
        std::vector<int> queue = {start}; component[start] = id;
        for (size_t q = 0; q < queue.size(); ++q) {
            int at = queue[q]; ++summary[0]; summary[1] += states[at].good;
            summary[2] = std::min(summary[2], states[at].key);
            for (int fi : states[at].fibers) if (!used[fi]) {
                used[fi] = true;
                for (int next : fibers[fi]) if (component[next] < 0) { component[next] = id; queue.push_back(next); }
            }
        }
        summaries.push_back(summary);
    }
    std::queue<int> queue;
    for (int i = 0; i < int(states.size()); ++i) if (states[i].good) { distance[i] = 0; queue.push(i); }
    used.assign(fibers.size(), false);
    while (!queue.empty()) {
        int at = queue.front(); queue.pop();
        for (int fi : states[at].fibers) if (!used[fi]) {
            used[fi] = true;
            for (int next : fibers[fi]) if (distance[next] < 0) { distance[next] = distance[at]+1; queue.push(next); }
        }
    }
    std::vector<std::array<Word,3>> records;
    std::map<int,Word> histogram, sizes;
    for (int at = 0; at < int(states.size()); ++at) {
        assert(states[at].fibers.size() == unsigned((1 << dimension)-1));
        records.push_back({states[at].key,summaries[component[at]][2],Word(distance[at]+1)});
        ++histogram[distance[at]];
    }
    for (auto &fiber : fibers) ++sizes[fiber.size()];
    std::sort(records.begin(), records.end());
    std::ofstream output(argv[1], std::ios::binary);
    for (auto record : records) for (Word x : record)
        for (int b = 0; b < 8; ++b) output.put(char(x >> (8*b) & 255));
    output.close();
    std::sort(summaries.begin(), summaries.end(), [](auto a,auto b){return a[2]<b[2];});
    std::cout << "{\"full_support_spaces\":" << states.size() << ",\"fibers\":" << fibers.size()
              << ",\"lower_spaces_enumerated\":" << lower_spaces << ",\"components\":[";
    bool comma = false;
    for (auto c : summaries) {
        if (comma) std::cout << ','; comma = true; std::cout << '[' << c[0] << ',' << c[1] << ',' << c[2] << ']';
    }
    std::cout << "],\"fiber_distance_histogram\":["; comma = false;
    for (auto [d,count] : histogram) {
        if (comma) std::cout << ','; comma = true; std::cout << '[' << d << ',' << count << ']';
    }
    std::cout << "],\"fiber_size_histogram\":["; comma = false;
    for (auto [d,count] : sizes) {
        if (comma) std::cout << ','; comma = true; std::cout << '[' << d << ',' << count << ']';
    }
    std::cout << "]}\n";
}
