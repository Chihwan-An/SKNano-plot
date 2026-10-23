#!/usr/bin/env python3
"""Leave-one-out table: JES_2024 pull/constraint and the rateParams with each channel masked."""
import glob, os, re, sys
import ROOT
ROOT.gROOT.SetBatch(True)
H = os.path.dirname(os.path.abspath(__file__))
WATCH = ["JES_2024", "ResolvedDYReshapeBin4", "MuonTrig_2024"]
RP = ["R_TT_Resolved_2024", "R_DY_Resolved_2024"]
for ch in sys.argv[1:] or ["EE", "MM"]:
    rows = []
    for fp in sorted(glob.glob("%s/%s/fitDiagnostics.*.root" % (H, ch))):
        tag = re.sub(r"^fitDiagnostics\.|\.root$", "", os.path.basename(fp))
        f = ROOT.TFile.Open(fp); fb = f.Get("fit_b")
        if not fb or not fb.InheritsFrom("RooFitResult"):
            rows.append((tag, None)); continue
        p = fb.floatParsFinal(); d = {"status": fb.status(), "covQual": fb.covQual()}
        for n in WATCH + RP:
            q = p.find(n)
            d[n] = (q.getVal(), q.getError()) if q else None
        rows.append((tag, d)); f.Close()
    rows.sort(key=lambda r: (r[0] != "none", r[0]))
    print("\n=== %s card ===" % ch)
    print("%-22s%5s%4s  %-15s%-15s%-15s%-17s%-17s" % ("masked", "st", "cq", "JES pull(err)",
          "DYRshBin4", "MuonTrig", "R_TT_Res", "R_DY_Res"))
    for tag, d in rows:
        if d is None:
            print("%-22s  FIT FAILED" % tag); continue
        f = lambda n, rp=False: ("%.3f±%.3f" % d[n] if rp else "%+.2f (%.2f)" % d[n]) if d[n] else "-"
        print("%-22s%5d%4d  %-15s%-15s%-15s%-17s%-17s" % (tag.replace("no_", "−"), d["status"], d["covQual"],
              f("JES_2024"), f("ResolvedDYReshapeBin4"), f("MuonTrig_2024"),
              f("R_TT_Resolved_2024", True), f("R_DY_Resolved_2024", True)))
