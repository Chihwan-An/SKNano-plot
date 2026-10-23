# chargeflip plots (2026-09-12)

AN_rawcharge/                         CURRENT — AN 8.2 method: raw charge, no tightCharge (BDT/SR/test/scripts/chargeflip_ptshift.py)
  01_2region_barrel_endcap/           step1 energy shift, step2 rate P(eta6, pT) vs 1/pT, step3 MC closure, step4 data SF BB/EE/BE (SF 1.43 / 1.45)
  02_3region_innerB_outerB_endcap/    same steps, SF per inner barrel / outer barrel / endcap (1.22 / 1.73 / 1.45) -> ddss_ee_2024_an3.root, cards
  03_checks/                          fliprate_vs_pt_fine{,_allmll}, fliprate_vs_invpt (P smooth to 600 GeV, convex in 1/pT),
                                      sf_vs_pt_zpeak (SF flat in pT), sf_vs_mee_window (sidebands = fakes), sf_vs_signed_eta (eta sign)
  applied: ../EE/<obj>/SS_flip_an (2-region), SS_flip_an3 (3-region, DY CR); ../../sig/EE/<obj>/SS_flip_an3 (SR, blinded)

nonAN_tightcharge_unfold/             earlier own method (tightCharge categories, per-lepton pair unfolding) — superseded, reference only
  01_truth_hists/                     analyzer truth histograms {DYCR,Zwin}/{prompt,nonprompt}/{electron,muon}/{same,diff}/tc{0,1,2}
  02_method_v1_tightcharge/           v1 (analyzer dR<0.1 gen charge): method_{tc2,tc210,nojet_*} step1-7
  03_method_v2_genidx/                v2 (genPartIdx gen charge) + sign / signed-eta / fit-selection variants, region_test, ss_sign; used by dc1-dc3
  applied: ../EE/<obj>/SS_flip, SS_flip_tc2, SS_flip_pp, SS_flip_mm

Tables/JSON: BDT/SR/test/docs/chargeflip_*.md, BDT/SR/test/data/chargeflip/*.json; history docs/chargeflip_status_20260910.md
