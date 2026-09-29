// Exhaust neutral components only when strict single-move descent fails.
#define CDC_REPAIR_LIBRARY
#include "repair_native.cpp"
#include <map>
#include <unordered_set>

struct PlateauSearch : Search {
    struct Node { Rows rows; Supports s; int parent, depth; unsigned circuit, added; };
    struct Move { unsigned circuit, added; };
    uint64_t local_minima=0, states_examined=0, closed_orbits=0;
    std::map<int,uint64_t> escape_histogram;
    int longest=-1;
    Rows longest_source{};
    std::vector<Move> longest_moves;

    uint64_t key(Rows rows) const {
        for (int i=0; i<3; ++i) {
            int pick=-1, lowest=32;
            for (int j=i; j<3; ++j) if (rows[j] && __builtin_ctz(rows[j])<lowest) {
                pick=j; lowest=__builtin_ctz(rows[j]);
            }
            if (pick<0) break;
            std::swap(rows[i],rows[pick]);
            unsigned bit=1u<<lowest;
            for (int j=0; j<3; ++j) if (j!=i && (rows[j]&bit)) rows[j]^=rows[i];
        }
        return uint64_t(rows[0])|(uint64_t(rows[1])<<16)|(uint64_t(rows[2])<<32);
    }

    bool plateau_escape(const Rows& source, const Supports& ss) {
        auto value=potential(source,ss);
        std::vector<Node> queue={{source,ss,-1,0,0,0}};
        std::unordered_set<uint64_t> seen={key(source)};
        for (size_t index=0; index<queue.size(); ++index) {
            Node node=queue[index];  // Queue growth must not invalidate this node.
            ++states_examined;
            std::array<Mask,8> colors{};
            for (unsigned a=1; a<8; ++a) {
                colors[a]=full;
                for (unsigned j=0; j<3; ++j) colors[a]&=((a>>j)&1)?node.s[j]:~node.s[j];
            }
            for (unsigned q:circuits) for (unsigned a=1; a<8; ++a) {
                Mask mask=supports[q];
                if (mask&colors[a]) continue;
                Rows next=node.rows; Supports ns=node.s;
                for (unsigned j=0; j<3; ++j) if ((a>>j)&1) { next[j]^=q; ns[j]^=mask; }
                auto p=potential(next,ns);
                if (p<value) {
                    ++escape_histogram[node.depth];
                    if (node.depth>longest) {
                        longest=node.depth; longest_source=source;
                        longest_moves={{q,a}};
                        int cursor=int(index);
                        while (queue[cursor].parent>=0) {
                            longest_moves.push_back({queue[cursor].circuit,queue[cursor].added});
                            cursor=queue[cursor].parent;
                        }
                        std::reverse(longest_moves.begin(),longest_moves.end());
                    }
                    return true;
                }
                if (p==value && seen.insert(key(next)).second)
                    queue.push_back({next,ns,int(index),node.depth+1,q,a});
            }
        }
        closed_orbits=seen.size();
        return false;
    }

    bool check_extended(const Rows& rows, const Supports& s, int rank) {
        if (Search::check(rows,s,rank)) return true;
        ++local_minima;
        if (!plateau_escape(rows,s)) return false;
        found=false;
        return true;
    }

    bool pivot_extended(const std::vector<int>& pivots) {
        int k=int(pivots.size()); Rows rows{}; Supports s{};
        std::vector<std::pair<int,int>> slots;
        for (int i=0; i<k; ++i) {
            rows[i]=1u<<pivots[i]; s[i]=supports[rows[i]];
            for (int j=pivots[i]+1; j<r; ++j)
                if (std::find(pivots.begin(),pivots.end(),j)==pivots.end()) slots.emplace_back(i,j);
        }
        uint64_t total=uint64_t(1)<<slots.size();
        for (uint64_t step=0; step<total; ++step) {
            if (step) {
                auto [row,col]=slots[__builtin_ctzll(step)];
                rows[row]^=1u<<col; s[row]^=supports[1u<<col];
            }
            if (!check_extended(rows,s,k)) return false;
        }
        return true;
    }

    void run_extended() {
        for (int p=0; p<r; ++p) for (int q=p+1; q<r; ++q)
            if (!pivot_extended({p,q})) return;
        for (int p=0; p<r; ++p) for (int q=p+1; q<r; ++q) for (int t=q+1; t<r; ++t)
            if (!pivot_extended({p,q,t})) return;
    }

    void print_flow(const Rows& rows) const {
        Supports s={supports[rows[0]],supports[rows[1]],supports[rows[2]]};
        std::cout << '[';
        for (int e=0; e<m; ++e) {
            if (e) std::cout << ',';
            std::cout << (((s[0]>>e)&1)+2*((s[1]>>e)&1)+4*((s[2]>>e)&1));
        }
        std::cout << ']';
    }

    void write_extended() const {
        std::cout << "{\"vertices\":"<<n<<",\"cycle_dimension\":"<<r
          <<",\"circuit_count\":"<<circuits.size()
          <<",\"subspaces_enumerated_by_rank\":{\"2\":"<<enumerated[2]<<",\"3\":"<<enumerated[3]
          <<"},\"nz_orbits_by_rank\":{\"2\":"<<nz[2]<<",\"3\":"<<nz[3]
          <<"},\"bad_orbits_checked\":"<<bad<<",\"strict_local_minima\":"<<local_minima
          <<",\"plateau_states_examined\":"<<states_examined
          <<",\"exhausted_all_flow_orbits\":"<<(found?"false":"true")
          <<",\"closed_plateau_orbits\":"<<closed_orbits<<",\"escape_neutral_distance_histogram\":{";
        bool first=true;
        for (auto [distance,count]:escape_histogram) {
            if (!first) std::cout<<',';
            first=false; std::cout<<'"'<<distance<<"\":"<<count;
        }
        std::cout<<"},\"counterexample\":";
        if (!found) std::cout<<"null";
        else { std::cout<<"{\"flow\":"; print_flow(trap); std::cout<<'}'; }
        std::cout<<",\"longest_escape\":";
        if (longest<0) std::cout<<"null";
        else {
            std::cout<<"{\"neutral_distance\":"<<longest<<",\"initial_flow\":";
            print_flow(longest_source); std::cout<<",\"moves\":[";
            for (size_t i=0; i<longest_moves.size(); ++i) {
                if (i) std::cout<<',';
                auto move=longest_moves[i];
                std::cout<<"{\"added_value\":"<<move.added<<",\"circuit_edges\":[";
                bool first_edge=true;
                for (int e=0; e<m; ++e) if ((supports[move.circuit]>>e)&1) {
                    if (!first_edge) std::cout<<',';
                    first_edge=false; std::cout<<e;
                }
                std::cout<<"]}";
            }
            std::cout<<"]}";
        }
        std::cout<<"}\n";
    }
};

int main() { PlateauSearch search; search.read(); search.run_extended(); search.write_extended(); }
