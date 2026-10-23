#!/usr/bin/env python3
"""2026-10-01 binning vs charge-split decomposition of cbv15_an2_ref_v3_ss3200 (D = both on).

  C  cbv15_decomp_split_run2bin : v3_ss3200 with every SR at the Run 2 (EXO-20-002) edges
                                  (bEESR/bMuMuSR ...,1800,8000; rEESR_OS/rMuMuSR_OS ...,3200,8000; SS already Run 2).
  A  cbv15_decomp_incl_run2bin  : C with each OS/SS pair merged into one charge-inclusive bin.
  D' cbv15_decomp_split_newbin : charge split like v3_ss3200 but both SS SRs at the OS tail edges (the B binning, not merged).
  Dn cbv15_decomp_split_ssne10 : D with the cbv15_raw_ne10 SS edges -- rEESR_SS ...,3200,4000,8000 (ddss_dyonly_sf_ss4000.root
                                  + cbv15_tmp_ss4000sig), rMuMuSR_SS ...,2000,2400,8000 (merged from v3); OS/boosted/CR as D.
  B  cbv15_decomp_incl_newbin   : v3_ss3200 binning (boosted 2617/3021, resolved tails) charge-inclusive. The SS SRs are
                                  first brought to the OS tail edges: rMuMuSR_SS from v3 (tail edges, superset),
                                  rEESR_SS rebuilt like build_v3_ss3200.py (bkg = ddss_dyonly_sf_tail.root, signal =
                                  cbv15_tmp_tailsig, data_obs = Asimov).

"Charge-inclusive" keeps the background model of v3_ss3200 unchanged: the OS and SS processes of a pair stay
separate processes (<proc>_OS, <proc>_SS; signal _OS index 0, _SS index -1) inside one bin, so every nuisance /
rateParam keeps exactly its v3 assignment -- only the categorisation changes.  Pairs: rEESR, rMuMuSR, rDYEECR, rDYMuMuCR.
"""
import array, glob, os, re, sys
import ROOT
ROOT.gROOT.SetBatch(True); ROOT.TH1.AddDirectory(False)

B = "/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/combine/scenarios/test"
H = os.path.dirname(os.path.abspath(__file__))
SRC = "cbv15_an2_ref_v3_ss3200"
V3 = "cbv15_an2_ref_v3"
R2R = [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000]
R2B = [800, 1000, 1200, 1500, 1800, 8000]
TAIL_EE = [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 3561, 4643, 5533, 8000]
TAIL_MM = [800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 3496, 4685, 5231, 8000]
PAIRS = {"rEESR": ("rEESR_OS", "rEESR_SS"), "rMuMuSR": ("rMuMuSR_OS", "rMuMuSR_SS"),
         "rDYEECR": ("rDYEECR_OS", "rDYEECR_SS"), "rDYMuMuCR": ("rDYMuMuCR_OS", "rDYMuMuCR_SS")}
BKG = ["Flip", "TT", "DYJets", "Nonprompt", "Others"]


def shp(tag): return f"{B}/{tag}/shapes_2024_{tag}.root"
def edges_of(h): return [round(h.GetBinLowEdge(i), 3) for i in range(1, h.GetNbinsX() + 2)]


def rebin_to(h, eds, n):
    assert all(float(e) in edges_of(h) for e in eds), (n, edges_of(h), eds)
    r = h.Rebin(len(eds) - 1, n, array.array("d", [float(e) for e in eds])); r.SetDirectory(0)
    assert abs(r.Integral() - h.Integral()) <= 1e-9 * max(1.0, abs(h.Integral())), n
    return r


def load(path):
    f = ROOT.TFile.Open(path); out = {}
    for k in f.GetListOfKeys():
        d = f.Get(k.GetName()); out[k.GetName()] = {}
        for kk in d.GetListOfKeys():
            h = kk.ReadObj(); h.SetDirectory(0); out[k.GetName()][kk.GetName()] = h
    f.Close(); return out


def save(regs, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = ROOT.TFile.Open(path, "RECREATE")
    for r, objs in regs.items():
        d = f.mkdir(r)
        for n, h in objs.items(): d.WriteTObject(h, n)
    f.Close()


def merge_pairs(regs):
    out = {}
    for r, objs in regs.items():
        new = next((m for m, p in PAIRS.items() if r in p), None)
        if new is None: out[r] = objs; continue
        suf = "_OS" if r.endswith("_OS") else "_SS"
        d = out.setdefault(new, {})
        for n, h in objs.items():
            if n == "data_obs":
                if "data_obs" in d: d["data_obs"].Add(h)
                else: d["data_obs"] = h.Clone("data_obs"); d["data_obs"].SetDirectory(0)
                continue
            p, _, s = n.partition("_")
            nn = p + suf + ("_" + s if s else "")
            assert nn not in d, nn
            h = h.Clone(nn); h.SetDirectory(0); d[nn] = h
    for m, (a, b) in PAIRS.items():
        if m in out:
            ea, eb = edges_of(regs[a]["data_obs"]), edges_of(regs[b]["data_obs"])
            assert ea == eb, (m, ea, eb)
    return out


# ---------------------------------------------------------------- cards
def parse(path):
    L = open(path).read().split("\n")
    i_obs = next(i for i, l in enumerate(L) if l.startswith("observation"))
    obs_bins, obs = L[i_obs - 1].split()[1:], L[i_obs].split()[1:]
    i_b = next(i for i, l in enumerate(L) if i > i_obs and l.startswith("bin"))
    cb, cp, ci, cr = (L[i_b + k].split()[1:] for k in range(4))
    nuis, rest = [], []
    for l in L[i_b + 4:]:
        t = l.split()
        if not t or l.startswith("-"): continue
        if len(t) == len(cb) + 2 and t[1] in ("lnN", "shape", "lnU", "gmN"): nuis.append((t[0], t[1], t[2:]))
        else: rest.append(t)
    head = [l for l in L[:i_obs - 1] if l.startswith("#")]
    return dict(head=head, obs_bins=obs_bins, obs=obs, cb=cb, cp=cp, ci=ci, cr=cr, nuis=nuis, rest=rest)


def fmt(rows):
    w = [max(len(r[j]) for r in rows if j < len(r)) for j in range(max(map(len, rows)))]
    return ["  ".join(x.ljust(w[j]) for j, x in enumerate(r)).rstrip() for r in rows]


def write_card(c, shapes_path, out, merge):
    def newbin(b): return next((m for m, p in PAIRS.items() if b in p), b) if merge else b
    def newproc(b, p): return (p + ("_OS" if b.endswith("_OS") else "_SS")) if merge and newbin(b) != b else p
    bins, obs = [], {}
    for b, o in zip(c["obs_bins"], c["obs"]):
        nb = newbin(b)
        if nb not in obs: bins.append(nb); obs[nb] = float(o)
        else: obs[nb] += float(o)
    cb = [newbin(b) for b in c["cb"]]; cp = [newproc(b, p) for b, p in zip(c["cb"], c["cp"])]
    sig = {}; bkg = {}
    for p, i in zip(cp, c["ci"]):
        if int(i) <= 0: sig.setdefault(p, None)
        else: bkg.setdefault(p, None)
    idx = {p: -k for k, p in enumerate(sorted(sig, key=lambda s: ("_SS" in s, "_OS" in s)))}
    idx.update({p: k + 1 for k, p in enumerate(bkg)})
    o = list(c["head"]) + [f"# {os.path.basename(out)}: build_decomp.py {'charge-inclusive merge of ' + ','.join(PAIRS) if merge else ''}",
                           f"imax {len(bins)}  number of channels", f"jmax {len(idx) - 1}  number of processes minus 1", "kmax *", "-" * 80]
    o += fmt([["shapes", "*", b, shapes_path, f"{b}/$PROCESS", f"{b}/$PROCESS_$SYSTEMATIC"] for b in bins]) + ["-" * 80]
    o += fmt([["bin"] + bins, ["observation"] + [("%g" % obs[b]) if obs[b] >= 0 else "-1" for b in bins]]) + ["-" * 80]
    o += fmt([["bin"] + cb, ["process"] + cp, ["process"] + [str(idx[p]) for p in cp], ["rate"] + c["cr"]]) + ["-" * 80]
    o += fmt([[n, t] + v for n, t, v in c["nuis"]])
    rp, ams = [], {}
    for t in c["rest"]:
        if len(t) >= 4 and t[1] == "rateParam":
            t = [t[0], t[1], newbin(t[2]), newproc(t[2], t[3])] + t[4:]; rp.append(t)
        elif len(t) >= 2 and t[1] == "autoMCStats":
            ams.setdefault(newbin(t[0]), [newbin(t[0])] + t[1:])
        else: sys.exit(f"unhandled card line {t}")
    o += fmt(rp) + fmt(list(ams.values()))
    os.makedirs(os.path.dirname(out), exist_ok=True); open(out, "w").write("\n".join(o) + "\n")


def cards(tag, merge):
    n = 0
    for c in sorted(glob.glob(f"{B}/{SRC}/datacards/2024/*/card_*.txt")):
        ch = c.split("/")[-2]
        write_card(parse(c), shp(tag), f"{B}/{tag}/datacards/2024/{ch}/{os.path.basename(c)}", merge); n += 1
    print(f"  {tag}: {n} cards")


# ---------------------------------------------------------------- scenarios
def build_C():
    regs = load(shp(SRC))
    E = {"bEESR": R2B, "bMuMuSR": R2B, "rEESR_OS": R2R, "rMuMuSR_OS": R2R}
    for r, eds in E.items(): regs[r] = {n: rebin_to(h, eds, n) for n, h in regs[r].items()}
    return regs


def build_Bpre(ee=TAIL_EE, mm=TAIL_MM, dd_file="ddss_dyonly_sf_tail.root", sig_tag="cbv15_tmp_tailsig"):
    regs = load(shp(SRC)); v3 = load(shp(V3))
    regs["rMuMuSR_SS"] = {n: rebin_to(h, mm, n) for n, h in v3["rMuMuSR_SS"].items()}
    dd = load(H + "/" + dd_file)["rEESR_SS"]; sg = load(f"{B}/{sig_tag}/shapes_2024_{sig_tag}.root")["rEESR_SS"]
    old = regs["rEESR_SS"]; new = {}
    for n in old:
        if n == "data_obs": continue
        new[n] = sg[n] if n.startswith("WR") else dd[n]
        assert edges_of(new[n]) == [float(e) for e in ee], (n, edges_of(new[n]))
        assert abs(new[n].Integral() - old[n].Integral()) <= 1e-3 * max(1.0, abs(old[n].Integral())), \
            ("rEESR_SS yield changed", n, new[n].Integral(), old[n].Integral())
    tot = None
    for n in BKG:
        if tot is None: tot = new[n].Clone("data_obs"); tot.SetDirectory(0)
        else: tot.Add(new[n])
    new["data_obs"] = tot
    regs["rEESR_SS"] = new
    return regs


if __name__ == "__main__":
    which = sys.argv[1:] or ["C", "A", "B"]
    if "C" in which or "A" in which:
        C = build_C()
        if "C" in which:
            save(C, shp("cbv15_decomp_split_run2bin")); cards("cbv15_decomp_split_run2bin", False)
        if "A" in which:
            save(merge_pairs(C), shp("cbv15_decomp_incl_run2bin")); cards("cbv15_decomp_incl_run2bin", True)
    if "Dn" in which:
        save(build_Bpre([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 4000, 8000], [800, 1000, 1200, 1400, 1600, 2000, 2400, 8000],
                        "ddss_dyonly_sf_ss4000.root", "cbv15_tmp_ss4000sig"), shp("cbv15_decomp_split_ssne10"))
        cards("cbv15_decomp_split_ssne10", False)
    if "B" in which or "Dp" in which:
        Bpre = build_Bpre()
        if "Dp" in which:
            save(Bpre, shp("cbv15_decomp_split_newbin")); cards("cbv15_decomp_split_newbin", False)
        if "B" in which:
            save(merge_pairs(Bpre), shp("cbv15_decomp_incl_newbin")); cards("cbv15_decomp_incl_newbin", True)
