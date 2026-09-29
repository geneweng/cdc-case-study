// Exhaust which prescribed first coordinates admit a flow or a five-layer lift.
// A positive census is finite evidence only, not a proof of a universal claim.
#define CDC_REPAIR_LIBRARY
#include "repair_native.cpp"

struct FirstCoordinateSearch : Search {
    std::vector<uint64_t> admissible, successful;

    void observe(const Rows& rows, const Supports& s, int rank) {
        ++enumerated[rank];
        if ((s[0]|s[1]|s[2]) != full) return;
        ++nz[rank];
        auto d=defects(rows,s);
        // Every normal occurs 24 times in a rank-three orbit, six in rank two.
        uint64_t weight=rank==3?24:6;
        for (unsigned l=1; l<8; ++l) {
            unsigned code=0;
            for (unsigned j=0; j<3; ++j) if ((l>>j)&1) code^=rows[j];
            admissible[code]+=weight;
            if (!d[l-1]) successful[code]+=weight;
        }
    }

    void block(const std::vector<int>& pivots) {
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
            observe(rows,s,k);
        }
    }

    void run_fibers() {
        admissible.resize(supports.size()); successful.resize(supports.size());
        for (int p=0; p<r; ++p) for (int q=p+1; q<r; ++q) block({p,q});
        for (int p=0; p<r; ++p) for (int q=p+1; q<r; ++q) for (int t=q+1; t<r; ++t) block({p,q,t});
    }

    void write_fibers() const {
        std::cout<<"{\"subspaces_enumerated_by_rank\":{\"2\":"<<enumerated[2]
                 <<",\"3\":"<<enumerated[3]<<"},\"nz_orbits_by_rank\":{\"2\":"<<nz[2]
                 <<",\"3\":"<<nz[3]<<"},\"first_coordinates\":[";
        for (unsigned code=0; code<supports.size(); ++code) {
            if (code) std::cout<<',';
            std::cout<<"{\"support_mask\":"<<supports[code]<<",\"admissible_flows\":"
                     <<admissible[code]<<",\"successful_flows\":"<<successful[code]<<'}';
        }
        std::cout<<"]}\n";
    }
};

int main() { FirstCoordinateSearch s; s.read(); s.run_fibers(); s.write_fibers(); }
