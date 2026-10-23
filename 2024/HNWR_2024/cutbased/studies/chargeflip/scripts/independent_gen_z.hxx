#include <ROOT/RVec.hxx>
#include <Math/Vector4D.h>
#include <cmath>
#include <limits>
#include <vector>

namespace IndependentDY {
using ROOT::VecOps::RVec;
using P4 = ROOT::Math::PtEtaPhiMVector;
template<class PID, class STATUS, class FLAGS>
RVec<double> direction(const RVec<float>& pt, const RVec<float>& eta,
 const RVec<float>& phi, const RVec<float>& mass, const PID& pid,
 const STATUS& status, const FLAGS& flags, const RVec<float>& jpt,
 const RVec<float>& jeta, const RVec<float>& jphi) {
    const double nan=std::numeric_limits<double>::quiet_NaN();
    P4 z;
    std::vector<unsigned> bosons, hard, prompt;
    for (unsigned i=0;i<pt.size();++i) {
        const bool charged=std::abs(pid[i])==11 || std::abs(pid[i])==13;
        if (charged && (flags[i]&(1<<7))) hard.push_back(i);
        if (charged && status[i]==1 && (flags[i]&1)) prompt.push_back(i);
        if (pid[i]==23 && (status[i]==62 ||
            ((flags[i]&(1<<13)) && (flags[i]&((1<<7)|(1<<8)))))) bosons.push_back(i);
    }
    int source=0;
    if (bosons.size()==1) {
        const unsigned i=bosons[0];
        z=P4(pt[i],eta[i],phi[i],mass[i]);
        source=status[i]==62 ? 1 : 2;
    } else if (bosons.empty() && hard.size()==2 && pid[hard[0]]==-pid[hard[1]]) {
        const unsigned a=hard[0], b=hard[1];
        z=P4(pt[a],eta[a],phi[a],mass[a])+P4(pt[b],eta[b],phi[b],mass[b]);
        source=3;
    }
    int n25=0, n50=0;
    for (unsigned j=0;j<jpt.size();++j) {
        if (!(jpt[j]>40 && std::abs(jeta[j])<5)) continue;
        bool overlap=false;
        for (unsigned l:prompt) {
            const double dp=std::remainder(double(jphi[j])-phi[l],2*M_PI);
            const double de=double(jeta[j])-eta[l];
            if (dp*dp+de*de<.16) { overlap=true; break; }
        }
        if (overlap) continue;
        ++n50;
        if (std::abs(jeta[j])<2.5) ++n25;
    }
    if (!source) return {nan,nan,nan,nan,nan,0.,double(n25),double(n50),double(bosons.size())};
    const double q=z.Pt(), pz=z.Pz(), m=z.M();
    return {m,q,pz,q>0 ? std::asinh(pz/q) : nan,
            std::asinh(pz/std::hypot(m,q)),double(source),double(n25),double(n50),double(bosons.size())};
}
}
