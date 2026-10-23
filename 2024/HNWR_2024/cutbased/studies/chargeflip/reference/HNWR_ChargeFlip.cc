#include <HNWR/HNWR_ChargeFlip.h>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

HNWR_ChargeFlip::HNWR_ChargeFlip() {}
HNWR_ChargeFlip::~HNWR_ChargeFlip() {}

void HNWR_ChargeFlip::CFRow::Reset() { *this = CFRow(); }

// ---------------------------------------------------------------------------
// setup
// ---------------------------------------------------------------------------
void HNWR_ChargeFlip::initializeAnalyzer() {
    // Triggers, myCorr and the object configuration (el_set / mu_set / jet_set)
    // come from the parent, so the selection below runs against the same cut
    // values as the main analyzer. The parent's systHelper is left in place but
    // never consulted: this analyzer is a single Central pass.
    HNWR::initializeAnalyzer();

    fHandle = Output().Book("Central/CF_Tree", AnalyzerCore::RNTupleOutputProfile::Sparse);
    fHandle.Field("channel", fRow.channel);
    for (int i = 0; i < 4; i++) {
        const std::string p = "l" + std::to_string(i + 1);
        auto &l = fRow.lep[i];
        fHandle.Field(p + "_pt", l.pt)
               .Field(p + "_eta", l.eta)
               .Field(p + "_scEta", l.scEta)
               .Field(p + "_phi", l.phi)
               .Field(p + "_charge", l.charge)
               .Field(p + "_tightCharge", l.tightCharge)
               .Field(p + "_genCharge", l.genCharge)
               .Field(p + "_genChargeIdx", l.genChargeIdx)
               .Field(p + "_genPt", l.genPt)
               .Field(p + "_genDR", l.genDR)
               .Field(p + "_genPtIdx", l.genPtIdx)
               .Field(p + "_genEta", l.genEta)
               .Field(p + "_genPhi", l.genPhi)
               .Field(p + "_genPartFlav", l.genPartFlav)
               .Field(p + "_convVeto", l.convVeto)
               .Field(p + "_lostHits", l.lostHits);
    }
    fHandle.Field("m_l1l2", fRow.m_l1l2)
           .Field("pt_l1l2", fRow.pt_l1l2)
           .Field("met_pt", fRow.met_pt)
           .Field("met_phi", fRow.met_phi)
           .Field("m_lljj", fRow.m_lljj)
           .Field("nJet", fRow.nJet)
           .Field("j1_pt", fRow.j1_pt).Field("j1_eta", fRow.j1_eta)
           .Field("j2_pt", fRow.j2_pt).Field("j2_eta", fRow.j2_eta)
           .Field("passResolved", fRow.passResolved)
           .Field("isDYCR", fRow.isDYCR)
           .Field("isSS", fRow.isSS)
           .Field("hasPair", fRow.hasPair)
           .Field("passBoosted", fRow.passBoosted).Field("isSSBoosted", fRow.isSSBoosted)
           .Field("m_l1l3", fRow.m_l1l3).Field("m_lfj", fRow.m_lfj)
           .Field("fj_pt", fRow.fj_pt).Field("fj_eta", fRow.fj_eta).Field("fj_sdm", fRow.fj_sdm).Field("fj_lsf3", fRow.fj_lsf3)
           .Field("isBoostedDYCR", fRow.isBoostedDYCR).Field("isSSBoostedDYCR", fRow.isSSBoostedDYCR).Field("l4_inFatJet", fRow.l4_inFatJet)
           .Field("m_l1l4", fRow.m_l1l4).Field("m_lN", fRow.m_lN)
           .Field("weight", fRow.weight)
           .Field("w_dy", fRow.w_dy)
           .Field("w_sf", fRow.w_sf);

    std::cout << "[HNWR_ChargeFlip] initialised: era " << DataEra << ", sample "
              << (IsDATA ? DataStream : MCSample) << (IsDATA ? " (data)" : " (MC)") << std::endl;
}

// Loose ID without isolation (same bitmap decoding as jet_pt_reweight / HNWR).
bool HNWR_ChargeFlip::IsPassLooseNoIso(const ElectronView &el) {
    const int bitmap = Electron_vidNestedWPBitmap[el.rawIndex()];
    const int n_cuts = 10;
    const int bits_per_cut = 3;
    const int ignore_cut = 7;   // isolation
    const int id_level = 2;     // Loose
    const int mask = (1 << bits_per_cut) - 1;
    for (int cut_nr = 0; cut_nr < n_cuts; cut_nr++) {
        if (cut_nr == ignore_cut) continue;
        const int value = (bitmap >> (cut_nr * bits_per_cut)) & mask;
        if (value < id_level) return false;
    }
    return true;
}

// Closest status-1 gen lepton of the same flavour within dR < 0.1, skipping the
// two incoming partons and anything without a mother (ISR). Gen charge as
// -1/+1 (PID +11/+13 is the NEGATIVE lepton), -999 when unmatched or data.
// Same body as HNWR_BDT_presel::GenChargeOf (the v13 GetGenMatchedLepton).
int HNWR_ChargeFlip::GenChargeOf(const Lepton *lep, float *genPt, float *genDR, float *genEta, float *genPhi) const {
    if (genPt) *genPt = kMissingF;
    if (genDR) *genDR = kMissingF;
    if (genEta) *genEta = kMissingF;
    if (genPhi) *genPhi = kMissingF;
    if (!lep || IsDATA || !fHasGens || fGens.size() == 0) return kMissingI;

    int reco_PID = 0;
    if (lep->IsElectron())  reco_PID = 11;
    else if (lep->IsMuon()) reco_PID = 13;
    else return kMissingI;

    float min_dR = 0.1f;
    int matched_PID = 0;
    for (std::size_t i = 2; i < fGens.size(); i++) {
        const auto gen = fGens[i];
        if (gen.Status() != 1) continue;
        if (std::abs(gen.PID()) != reco_PID) continue;
        if (gen.MotherIndex() < 0) continue;
        const float dR = static_cast<float>(gen.P4().DeltaR(*lep));
        if (dR < min_dR) {
            min_dR = dR;
            matched_PID = gen.PID();
            if (genPt) *genPt = static_cast<float>(gen.Pt());
            if (genDR) *genDR = dR;
            if (genEta) *genEta = static_cast<float>(gen.Eta());
            if (genPhi) *genPhi = static_cast<float>(gen.Phi());
        }
    }
    if (matched_PID == 0) return kMissingI;
    return matched_PID > 0 ? -1 : +1;
}

// NanoAOD genPartFlav: 1 prompt, 15 from tau, 22 prompt photon (electrons),
// 5 from b, 4 from c, 3 light / unknown, 0 unmatched.
const char *HNWR_ChargeFlip::OriginOf(int flav) {
    switch (flav) {
        case 1:  return "prompt";
        case 15: return "tau";
        case 22: return "photon";
        default: return "nonprompt";
    }
}

// The per-lepton same / diff histograms.
//   <sel>/<ch>/<origin>/tc<k>_<same|diff>            TH2 pT x |eta|
//   <sel>/<ch>/<origin>/tc<k>_<same|diff>_pt         TH1 pT
//   <sel>/<ch>/<origin>/tc<k>_<same|diff>_abseta     TH1 |eta|
//   <sel>/<ch>/<origin>/tcAll_<same|diff>            TH2, tightCharge inclusive
//   <sel>/<ch>/unmatched                             TH2, no gen match (MC)
// |eta| is the supercluster eta for electrons.
void HNWR_ChargeFlip::FillLepton(const std::string &sel, const std::string &ch, const LepRow &l, float weight) {
    static const RVec<float> ptE  = {53., 60., 80., 100., 130., 170., 220., 300., 400., 600., 1000., 2000.};
    static const RVec<float> etaE = {0., 0.8, 1.479, 2.0, 2.5};
    static const RVec<float> etaM = {0., 0.9, 1.2, 2.1, 2.4};
    const RVec<float> &etaBins = (ch == "E") ? etaE : etaM;
    const float abseta = std::fabs((ch == "E") ? l.scEta : l.eta);
    const std::string base = sel + "/" + ch + "/";

    if (l.genCharge == kMissingI) {
        if (!IsDATA) FillHist(base + "unmatched", l.pt, abseta, weight, ptE, etaBins);
        return;
    }
    const std::string origin = OriginOf(l.genPartFlav);
    const std::string res = (l.genCharge == l.charge) ? "same" : "diff";
    const std::string tc = "tc" + std::to_string(l.tightCharge);
    FillHist(base + origin + "/" + tc + "_" + res, l.pt, abseta, weight, ptE, etaBins);
    FillHist(base + origin + "/" + tc + "_" + res + "_pt", l.pt, weight, ptE);
    FillHist(base + origin + "/" + tc + "_" + res + "_abseta", abseta, weight, etaBins);
    FillHist(base + origin + "/tcAll_" + res, l.pt, abseta, weight, ptE, etaBins);
}

// ---------------------------------------------------------------------------
// event loop
// ---------------------------------------------------------------------------
void HNWR_ChargeFlip::executeEvent() {
    ElectronViewCollection all_electrons = GetAllElectronViews(/*skipCrack=*/true);
    MuonViewCollection all_muons = GetAllMuonViews();
    JetViewCollection all_jets = GetAllJetViews();

    fHasGens = false;
    if (!IsDATA) {
        fGens = GetAllGenViews();
        fHasGens = true;
        gen_set.gens = fGens;   // HNWR::GetGenZpT reads the parent's collection
    }

    Event ev = GetEvent();
    const Particle METv = ev.GetMETVector(Event::MET_Type::PUPPI, SKNano::Variation::nom, Event::MET_Syst::CENTRAL);

    const MyCorrection::variation nomVar = MyCorrection::variation::nom;
    float weight = 1.0;
    if (!IsDATA) {
        weight *= MCweight();
        weight *= ev.GetTriggerLumi("HLT_Mu50");
        weight *= myCorr->GetPUWeight(ev.nTrueInt(), nomVar);
    }

    if (!PassNoiseFilter(all_jets, ev, Event::MET_Type::PUPPI)) return;

    const bool pass_trig_muon = ev.PassTrigger(mu_set.Muon_Trigger);
    const bool pass_trig_elec = ev.PassTrigger(el_set.Ele_Trigger);

    // --- leptons: pt/eta preselection, then Tight / Loose as in the parent
    std::vector<std::size_t> elPos, muPos;
    for (std::size_t i = 0; i < all_electrons.size(); i++) {
        const auto el = all_electrons[i];
        if (!(el.Pt() > el_set.Electron_MinPt)) continue;
        if (!(std::fabs(el.Eta()) < 2.5)) continue;
        elPos.push_back(i);
    }
    for (std::size_t i = 0; i < all_muons.size(); i++) {
        const auto mu = all_muons[i];
        if (!(mu.HighPtPt() > mu_set.Muon_MinPt)) continue;
        if (!(std::fabs(mu.Eta()) < 2.4)) continue;
        muPos.push_back(i);
    }
    std::sort(elPos.begin(), elPos.end(), [&](std::size_t a, std::size_t b) {
        return all_electrons[a].Pt() > all_electrons[b].Pt();
    });
    std::sort(muPos.begin(), muPos.end(), [&](std::size_t a, std::size_t b) {
        return all_muons[a].HighPtPt() > all_muons[b].HighPtPt();
    });

    std::vector<Lepton> lepSnap;
    std::vector<std::size_t> lepViewPos;
    lepSnap.reserve(elPos.size() + muPos.size());
    lepViewPos.reserve(elPos.size() + muPos.size());
    auto viewPosOf = [&](const Lepton *lep) {
        return lepViewPos[static_cast<std::size_t>(lep - lepSnap.data())];
    };

    std::vector<Lepton *> Tight_electrons, Tight_muons, Tight_leps, Loose_leps;
    for (const std::size_t pos : elPos) {
        const auto el = all_electrons[pos];
        Lepton snap = MakeLeptonSnapshot(el);
        snap.SetPtEtaPhiM(el.Pt(), el.Eta(), el.Phi(), el.M());
        lepSnap.push_back(snap);
        lepViewPos.push_back(pos);
        Lepton *lep = &lepSnap.back();
        if (el.PassID(el_set.Electron_Tight_ID[0])) {
            Tight_electrons.push_back(lep);
            Tight_leps.push_back(lep);
        }
        const bool passLooseNoIso = IsPassLooseNoIso(el);
        const bool passHEEP = el.PassID(ElectronView::ElectronID::POG_HEEP);
        if (passLooseNoIso || passHEEP) Loose_leps.push_back(lep);
    }
    for (const std::size_t pos : muPos) {
        const auto mu = all_muons[pos];
        Lepton snap = MakeLeptonSnapshot(mu);
        snap.SetPtEtaPhiM(mu.HighPtPt(), mu.Eta(), mu.Phi(), mu.M());
        lepSnap.push_back(snap);
        lepViewPos.push_back(pos);
        Lepton *lep = &lepSnap.back();
        if (mu.PassID(mu_set.Muon_Tight_ID[0]) && (mu.TkRelIso() < mu_set.Muon_Iso_Cut)) {
            Tight_muons.push_back(lep);
            Tight_leps.push_back(lep);
        }
        if (mu.PassID(mu_set.Muon_Loose_ID[0])) Loose_leps.push_back(lep);
    }
    std::sort(Tight_leps.begin(), Tight_leps.end(), PtComparingPtr);
    const int n_Tight_leptons = static_cast<int>(Tight_electrons.size() + Tight_muons.size());

    // --- leading tight lepton: trigger, trigger-safe pT, data stream (2026-09-17: the boosted candidate needs only
    // one tight lepton, so the exactly-two requirement moved into hasPair below)
    if (Tight_leps.empty()) return;
    Lepton *LeadLep = Tight_leps[0];
    if (!(LeadLep->Pt() > 60.0)) return;
    const bool isEE = LeadLep->IsElectron(), isMM = LeadLep->IsMuon();
    if (isEE && LeadLep->Pt() < el_set.Ele_Trigger_Safe_Pt_Cut) return;
    if (isMM && LeadLep->Pt() < mu_set.Muon_Trigger_Safe_Pt_Cut) return;
    const bool trig = isEE ? pass_trig_elec : pass_trig_muon;
    if (!trig) return;
    // Data: one stream per channel, so an event is never counted from both.
    if (IsDATA) {
        if (isEE && !DataStream.Contains("EGamma")) return;
        if (isMM && !DataStream.Contains("Muon")) return;
    }
    // resolved dilepton requirement: exactly two tight leptons, same flavour, sub-leading pT > 53
    const bool hasPair = (n_Tight_leptons == 2) && (Tight_leps[1]->IsElectron() == isEE) && (Tight_leps[1]->Pt() > 53.0);
    Lepton *SubLeadLep = hasPair ? Tight_leps[1] : nullptr;

    // --- jets (cleaned against loose leptons), resolved dR cuts, m(lljj)
    if (Run == 3 && !PassJetVetoMap(all_jets, "jetvetomap")) return;
    std::vector<std::size_t> jetIndices = SelectJetIndices(all_jets, jet_set.Jet_ID[0],
                                                           jet_set.Jet_MinPt, jet_set.Jet_MaxEta,
                                                           nomVar, nomVar);
    SelectedJetViewCollection selJets = SelectJetViews(all_jets, jetIndices, nomVar, nomVar);
    std::vector<TLorentzVector> selected_jets;
    for (std::size_t i = 0; i < selJets.size(); i++) {
        const TLorentzVector p4 = selJets[i].P4();
        bool isDRtoLepton = false;
        for (const Lepton *lep : Loose_leps) {
            if (p4.DeltaR(*lep) < 0.4) { isDRtoLepton = true; break; }
        }
        if (isDRtoLepton) continue;
        selected_jets.push_back(p4);
    }
    std::sort(selected_jets.begin(), selected_jets.end(),
              [](const TLorentzVector &a, const TLorentzVector &b) { return a.Pt() > b.Pt(); });

    const TLorentzVector ll = hasPair ? (*LeadLep + *SubLeadLep) : (*LeadLep);
    const float mll = hasPair ? static_cast<float>(ll.M()) : kMissingF;

    bool passResolved = false;
    float mlljj = kMissingF;
    if (hasPair && selected_jets.size() >= 2) {
        const bool dRLeadJetLep = (selected_jets[0].DeltaR(*LeadLep) > 0.4) && (selected_jets[0].DeltaR(*SubLeadLep) > 0.4);
        const bool dRSubLeadJetLep = (selected_jets[1].DeltaR(*LeadLep) > 0.4) && (selected_jets[1].DeltaR(*SubLeadLep) > 0.4);
        const bool dRTwoLepton = (LeadLep->DeltaR(*SubLeadLep) > 0.4);
        const bool dRTwoJets = (selected_jets[0].DeltaR(selected_jets[1]) > 0.4);
        if (dRLeadJetLep && dRSubLeadJetLep && dRTwoLepton && dRTwoJets) {
            passResolved = true;
            mlljj = static_cast<float>((ll + selected_jets[0] + selected_jets[1]).M());
        }
    }
    const bool inZwin = hasPair && (mll >= 60.) && (mll < 150.);
    const bool isDYCR = passResolved && inZwin && (mlljj > 800.);
    const bool isSS = hasPair && (LeadLep->Charge() * SubLeadLep->Charge() > 0);

    // --- boosted candidates (2026-09-17), transcribed from the parent's boosted SR / DY CR paths. Fatjets on the
    // nominal lane (ObjectLanes default), the parent's cuts (fatjet_set: pT > 200, |eta| < 2.5, SDM > 40, TIGHT ID).
    struct FJ { TLorentzVector p4; float sdm = 0.f, lsf3 = 0.f; };
    std::vector<FJ> fatjets, fatjets_LSF;
    {
        const HNWR::ObjectLanes lanes;
        const FatJetViewCollection all_fatjets = GetAllFatJets();
        for (std::size_t i = 0; i < all_fatjets.size(); i++) {
            const auto fj = all_fatjets[i];
            const float fj_pt = FatJetLanePt(fj, lanes);
            const float fj_sdm = FatJetLaneSDMass(fj, lanes);
            if (!((fj_pt > fatjet_set.FatJet_MinPt) && (std::fabs(fj.Eta()) < fatjet_set.FatJet_MaxEta) && (fj_sdm > fatjet_set.FatJet_SDM))) continue;
            if (!myCorr->PassFatJetID(fj, fatjet_set.FatJet_ID)) continue;
            FJ c; c.p4 = FatJetLaneP4(fj, lanes); c.sdm = fj_sdm; c.lsf3 = fj.LSF3();
            fatjets.push_back(c);
            if (c.lsf3 > fatjet_set.Fatjet_LSF) fatjets_LSF.push_back(c);
        }
        auto desc = [](const FJ &a, const FJ &b) { return a.p4.Pt() > b.p4.Pt(); };
        std::sort(fatjets.begin(), fatjets.end(), desc); std::sort(fatjets_LSF.begin(), fatjets_LSF.end(), desc);
    }
    std::vector<Lepton *> Loose_SF_leps, Loose_OF_leps;
    for (Lepton *lep : Loose_leps) (lep->IsElectron() == isEE ? Loose_SF_leps : Loose_OF_leps).push_back(lep);
    std::sort(Loose_SF_leps.begin(), Loose_SF_leps.end(), PtComparingPtr);
    std::sort(Loose_OF_leps.begin(), Loose_OF_leps.end(), PtComparingPtr);

    // boosted SR candidate: LSF3-tagged away fatjet, SF loose lepton inside, no OF loose lepton inside, no extra tight lepton
    bool passBoosted = false; Lepton *InJetLep = nullptr; FJ SRFatJet;
    {
        bool hasFJ = false;
        for (const FJ &fj : fatjets_LSF) { if (std::fabs(LeadLep->DeltaPhi(fj.p4)) > 2.0) { SRFatJet = fj; hasFJ = true; break; } }
        if (hasFJ) {
            for (Lepton *lep : Loose_SF_leps) {
                if (LeadLep->DeltaR(*lep) < 0.01) continue;
                if (lep->Pt() < 53.0) continue;
                if (SRFatJet.p4.DeltaR(*lep) < 0.8) { InJetLep = lep; break; }
            }
            bool hasOF = false;
            for (Lepton *lep : Loose_OF_leps) {
                if (LeadLep->DeltaR(*lep) < 0.01) continue;
                if (lep->Pt() < 53.0) continue;
                if (SRFatJet.p4.DeltaR(*lep) < 0.8) { hasOF = true; break; }
            }
            int nExtraTight = 0;
            for (Lepton *lep : Tight_leps) { if (lep == LeadLep || lep == InJetLep) continue; nExtraTight++; }
            passBoosted = InJetLep && !hasOF && (nExtraTight == 0);
        }
    }
    // boosted DY CR pairing (parent): first SF loose lepton with 60 < m(lead, l) < 150, first fatjet (no LSF3 cut) back to back
    bool isBoostedDYCR = false, l4_in = false; Lepton *DYLep = nullptr; float m_l1l4 = kMissingF, m_lN = kMissingF;
    for (Lepton *lep : Loose_SF_leps) {
        if (lep == LeadLep || LeadLep->DeltaR(*lep) < 0.01) continue;
        const double m = ((*LeadLep) + (*lep)).M();
        if (m > 60. && m < 150.) { DYLep = lep; m_l1l4 = static_cast<float>(m); break; }
    }
    if (DYLep) {
        for (const FJ &fj : fatjets) {
            if (std::fabs(LeadLep->DeltaPhi(fj.p4)) > 2.0) {
                l4_in = fj.p4.DeltaR(*DYLep) < 0.8;
                const TLorentzVector N = l4_in ? fj.p4 : (fj.p4 + (*DYLep));
                m_lN = static_cast<float>(((*LeadLep) + N).M());
                isBoostedDYCR = m_lN > 800.;
                break;
            }
        }
    }
    if (!hasPair && !passBoosted && !isBoostedDYCR) return;

    // --- the parent's nominal event weight: DY corrections and lepton SFs
    float w_dy = 1.f, w_sf = 1.f;
    if (!IsDATA) {
        if (dycorr.apply) {
            const float gen_zpt = GetGenZpT();
            w_dy *= GetZptWeight(gen_zpt, "ZPTReweight") * GetZptEW(gen_zpt);
            const int rflav = dycorr.flav_split ? (isEE ? 1 : 2) : 0;
            if (passResolved) w_dy *= GetJetPtR(true, selected_jets[0].Pt(), -1, 0, rflav);
            else if (passBoosted) w_dy *= GetJetPtR(false, SRFatJet.p4.Pt(), -1, 0, rflav);   // boosted-only rows: the parent's boosted R
        }
        // lepton SFs of the tight leptons (lead only when there is no resolved pair; the in-jet loose lepton carries none)
        const int nTightSF = hasPair ? 2 : 1;
        if (isEE) {
            for (int i = 0; i < nTightSF; i++) {
                const auto el = all_electrons[viewPosOf(Tight_leps[i])];
                w_sf *= GetElectronHEEPIDSF_TnP(el.ScEta(), el.Pt(), nomVar);
                w_sf *= myCorr->GetElectronRECOSF(el.ScEta(), el.Pt(), el.Phi(), nomVar);
            }
            const auto el0 = all_electrons[viewPosOf(Tight_leps[0])];
            if (DataEra != "2017") w_sf *= GetElectronTriggerSF_TnP(el0.ScEta(), el0.Pt(), nomVar);
        } else {
            for (int i = 0; i < nTightSF; i++) {
                const auto mu = all_muons[viewPosOf(Tight_leps[i])];
                w_sf *= myCorr->GetMuonHighPtSF("NUM_HighPtID_DEN_GlobalMuonProbes", mu.Eta(), mu.HighPtPt(), nomVar);
                w_sf *= myCorr->GetMuonHighPtRECOSF(mu.Eta(), mu.HighPtMomentum(), nomVar);
                w_sf *= myCorr->GetMuonHighPtSF("NUM_probe_LooseRelTkIso_DEN_HighPtProbes", mu.Eta(), mu.HighPtPt(), nomVar);
                w_sf *= myCorr->GetMuonHighPtSF("NUM_HLT_DEN_HighPtLooseRelIsoProbes", mu.Eta(), mu.HighPtPt(), nomVar);
            }
        }
    }
    weight *= w_dy * w_sf;

    // --- fill the row
    fRow.Reset();
    fRow.channel = isEE ? 11 : 13;
    for (int i = 0; i < 4; i++) {
        Lepton *lep = (i == 0) ? LeadLep : (i == 1) ? SubLeadLep : (i == 2) ? InJetLep : DYLep;
        if (!lep) continue;
        auto &l = fRow.lep[i];
        l.pt = lep->Pt();
        l.eta = lep->Eta();
        l.phi = lep->Phi();
        l.charge = static_cast<int>(lep->Charge());
        l.genCharge = GenChargeOf(lep, &l.genPt, &l.genDR, &l.genEta, &l.genPhi);
        auto genChargeFromIdx = [&](int gidx) -> int {
            if (IsDATA || !fHasGens || gidx < 0 || static_cast<std::size_t>(gidx) >= fGens.size()) return kMissingI;
            const auto &g = fGens[static_cast<std::size_t>(gidx)];
            l.genPtIdx = static_cast<float>(g.Pt());
            const int pid = g.PID();
            if (std::abs(pid) == 11 || std::abs(pid) == 13) return pid > 0 ? -1 : +1;
            return 0;   // photon (or other) match: no charge
        };
        if (isEE) {
            const auto el = all_electrons[viewPosOf(lep)];
            l.genChargeIdx = genChargeFromIdx(static_cast<int>(el.GenPartIdx()));
            l.scEta = el.ScEta();
            l.tightCharge = static_cast<int>(el.TightCharge());
            l.genPartFlav = IsDATA ? kMissingI : static_cast<int>(el.GenPartFlav());
            l.convVeto = el.ConvVeto() ? 1 : 0;
            l.lostHits = static_cast<int>(el.LostHits());
        } else {
            const std::size_t pos = viewPosOf(lep);
            const auto mu = all_muons[pos];
            l.genChargeIdx = genChargeFromIdx(static_cast<int>(mu.GenPartIdx()));
            l.scEta = lep->Eta();
            l.tightCharge = static_cast<int>(Muon_tightCharge[all_muons.rawIndex(pos)]);
            l.genPartFlav = IsDATA ? kMissingI : static_cast<int>(mu.GenPartFlav());
        }
    }
    fRow.m_l1l2 = mll;
    fRow.pt_l1l2 = hasPair ? static_cast<float>(ll.Pt()) : kMissingF;
    fRow.met_pt = static_cast<float>(METv.Pt());
    fRow.met_phi = static_cast<float>(METv.Phi());
    fRow.m_lljj = mlljj;
    fRow.nJet = static_cast<int>(selected_jets.size());
    if (selected_jets.size() > 0) { fRow.j1_pt = static_cast<float>(selected_jets[0].Pt()); fRow.j1_eta = static_cast<float>(selected_jets[0].Eta()); }
    if (selected_jets.size() > 1) { fRow.j2_pt = static_cast<float>(selected_jets[1].Pt()); fRow.j2_eta = static_cast<float>(selected_jets[1].Eta()); }
    fRow.passResolved = passResolved;
    fRow.isDYCR = isDYCR;
    fRow.isSS = isSS;
    fRow.hasPair = hasPair;
    fRow.passBoosted = passBoosted;
    if (passBoosted) {
        fRow.isSSBoosted = LeadLep->Charge() * InJetLep->Charge() > 0;
        fRow.m_l1l3 = static_cast<float>(((*LeadLep) + (*InJetLep)).M());
        fRow.m_lfj = static_cast<float>(((*LeadLep) + SRFatJet.p4).M());
        fRow.fj_pt = static_cast<float>(SRFatJet.p4.Pt()); fRow.fj_eta = static_cast<float>(SRFatJet.p4.Eta());
        fRow.fj_sdm = SRFatJet.sdm; fRow.fj_lsf3 = SRFatJet.lsf3;
    }
    fRow.isBoostedDYCR = isBoostedDYCR;
    if (isBoostedDYCR) {
        fRow.isSSBoostedDYCR = LeadLep->Charge() * DYLep->Charge() > 0;
        fRow.l4_inFatJet = l4_in; fRow.m_l1l4 = m_l1l4; fRow.m_lN = m_lN;
    }
    fRow.weight = weight;
    fRow.w_dy = w_dy;
    fRow.w_sf = w_sf;
    fHandle.Fill();

    // --- histograms (resolved pair only)
    if (!hasPair) return;
    const std::string ch = isEE ? "E" : "M";
    const std::string chEv = isEE ? "EE" : "MM";
    const std::string cs = isSS ? "SS" : "OS";
    const char *sels[2] = {"Zwin", "DYCR"};
    const bool pass[2] = {inZwin, isDYCR};
    for (int s = 0; s < 2; s++) {
        if (!pass[s]) continue;
        const std::string sel = sels[s];
        // event-level SS / OS (data and MC alike), for the data/MC scale factor
        FillHist(sel + "/" + chEv + "/" + cs + "/m_l1l2", mll, weight, 90, 60., 150.);
        FillHist(sel + "/" + chEv + "/" + cs + "/lead_pt", LeadLep->Pt(), weight, 100, 0., 1000.);
        FillHist(sel + "/" + chEv + "/" + cs + "/sublead_pt", SubLeadLep->Pt(), weight, 100, 0., 1000.);
        if (passResolved) FillHist(sel + "/" + chEv + "/" + cs + "/m_lljj", mlljj, weight, 80, 0., 8000.);
        // event category by tightCharge of the two leptons: min(tc1, tc2)
        const int tcmin = std::min(fRow.lep[0].tightCharge, fRow.lep[1].tightCharge);
        FillHist(sel + "/" + chEv + "/" + cs + "/tcmin", static_cast<float>(tcmin), weight, 3, 0., 3.);
        // per-lepton truth comparison (MC)
        if (!IsDATA) {
            FillLepton(sel, ch, fRow.lep[0], weight);
            FillLepton(sel, ch, fRow.lep[1], weight);
        }
    }
}
