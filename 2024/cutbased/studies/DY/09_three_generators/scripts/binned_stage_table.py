import sys, os, glob, numpy as np, uproot, importlib.util
spec = importlib.util.spec_from_file_location("m", "make_dy_cr_datamc.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
D3 = M.D3
B = "/gv0/Users/achihwan/SKNanoOutput_dy3gen/HNWR/"
REGION = sys.argv[1] if len(sys.argv) > 1 else "Resolved"
VARS = {"ll_pt": np.array([0,100,200,300,400,500,700,1000.]), "mlljj": np.array([800,1000,1200,1500,1800,2400,8000.]),
        "leading_fatjet_pt": np.array([200,300,400,500,600,800,1200,2000.])} if REGION == "Boosted" else {"pt": np.array([0,50,100,150,200,300,400,500,700,1000.]),
        "mlljj": np.array([800,1000,1200,1400,1600,2000,2400,2800,3200,4000,8000.]),
        "leading_jet_pt": np.array([40,100,200,300,400,600,800,1200,2000.])}
STAGES = {"1 C": "DYCR_COnly/Central", "2 CxEW": "DYCR_ZptOnly/Central", "3 CxEWxR": "DYCR_Full/Central"}
def load(base, want, hdirs):
    out = {}
    for path in sorted(glob.glob(os.path.join(B, base, "2024", "*.root"))):
        grp = D3.classify(os.path.basename(path)[:-5])
        if grp is None: continue
        g = "data" if grp.startswith("data") else grp
        if g not in want: continue
        f = uproot.open(path)
        for st, hd in hdirs.items():
          for ch in ("EE", "MM"):
            if (grp == "data_e" and ch != "EE") or (grp == "data_m" and ch != "MM"): continue
            for var, dst in VARS.items():
                try: h = f[f"{hd}/DYCR_{REGION}_{ch}_{var}"]
                except Exception: continue
                a = out.setdefault((g, st, ch, var), [np.zeros(len(dst)-1), np.zeros(len(dst)-1)])
                a[0] += M.rebin(h.values(), h.axis().edges(), dst); a[1] += M.rebin(h.variances(), h.axis().edges(), dst)
    return out
ref = load("DYCRSplit_NoDYCorr_WeightSystOnly", {"data", "nondy"}, {"x": "Central"})
DY = {"shipped(POWHEG)": "DYCRStudy_DYCRSplit_RFlav_WeightSystOnly", "FxFx jet-incl": "DYCRStudy_DYCRSplit_RFlav_ZptFxFxIncl_WeightSystOnly",
      "FxFx per-jet": "DYCRStudy_DYCRSplit_RFlav_ZptNJet_WeightSystOnly"}
dy = {k: load(v, {"LO"}, STAGES) for k, v in DY.items()}
for var, dst in VARS.items():
    print(f"\n################ {REGION} {var}   (data-nonDY)/DY, EE+MM")
    print("%-28s" % "bin" + "".join("%10s" % f"{int(a)}-{int(b)}" for a, b in zip(dst[:-1], dst[1:])))
    d = sum(ref[("data", "x", ch, var)][0] for ch in ("EE", "MM")); nd = sum(ref[("nondy", "x", ch, var)][0] for ch in ("EE", "MM"))
    for st in STAGES:
        for lab in DY:
            try: m = sum(dy[lab][("LO", st, ch, var)][0] for ch in ("EE", "MM"))
            except KeyError: print(st, lab, "missing"); continue
            print("%-28s" % f"{st:10s}{lab}" + "".join("%10.3f" % x for x in (d-nd)/np.where(m > 0, m, np.nan)))
        print()
    print("%-28s" % "data stat err" + "".join("%10.3f" % x for x in np.sqrt(d)/np.maximum(d-nd, 1e-9)))
