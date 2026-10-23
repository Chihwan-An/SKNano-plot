#!/usr/bin/env python3
"""Test whether matching resolved DY OS to SS in mll also matches mlljj.

MC only. Independent random 50/50 training/validation within every sample.
Training determines the mll-only SS/OS ratio, validation tests both masses.
No collision data, 1-jet transfer, charge-flip SF or momentum shift is used.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2

BASE = Path(__file__).resolve().parents[1]
MLL = np.unique(np.r_[np.arange(60, 151, 5), np.arange(160, 201, 10),
                     np.arange(225, 401, 25), np.arange(450, 1001, 50),
                     1200, 1400, 1600, 2000, 3000, 5000, 10000, np.inf])
MJJ = np.array([800, 1000, 1200, 1400, 1600, 2000, 2400, 2800, 3200, 8000.])
MODES = ("nominal", "noDY")
KINDS = ("reco_all", "prompt_singleflip")
CHANNELS = ("EE", "MM")
REGIONS = {"inclusive": (60, np.inf), "Zwindow": (60, 150),
           "sideband": (150, 400), "SR": (400, np.inf)}
COLS = ("channel", "hasPair", "nJet", "passResolved", "m_lljj", "m_l1l2",
        "weight", "w_dy", "isSS", "l1_charge", "l2_charge",
        "l1_genChargeIdx", "l2_genChargeIdx", "l1_genPtIdx", "l2_genPtIdx",
        "l1_genPartFlav", "l2_genPartFlav")


def build_cache(dumps, cache, seed):
    paths = sorted(dumps.glob("tree_Skim_HNWR_DYto2L*.npz"))
    if not paths:
        raise ValueError(f"No DY NPZ files in {dumps}")
    # mode, truth category, channel, fold, reco sign, mll, mlljj
    shape = (2, 2, 2, 2, 2, len(MLL)-1, len(MJJ)-1)
    hist, var = np.zeros(shape), np.zeros(shape)
    count = np.zeros(shape[1:], dtype=np.int64)
    sources = []
    for path in paths:
        with np.load(path) as z:
            missing = set(COLS) - set(z.files)
            if missing:
                raise ValueError(f"{path.name}: missing {missing}")
            keep = ((z["hasPair"] > 0) & (z["nJet"] >= 2) & (z["passResolved"] > 0)
                    & (z["m_lljj"] > 800) & (z["m_l1l2"] >= 60))
            d = {k: z[k][keep] for k in COLS}
        if not all(np.all(np.isfinite(d[k])) for k in COLS):
            raise ValueError(f"Nonfinite values: {path}")
        if np.any(d["w_dy"] <= 0) or np.any(d["weight"] < 0):
            raise ValueError("Invalid DY factor or negative weights: adapt statistical treatment")
        n = len(d["weight"])
        key = int.from_bytes(hashlib.sha256(path.name.encode()).digest()[:8], "little")
        fold = np.random.default_rng(seed ^ key).integers(0, 2, n, dtype=np.int8)
        ss = d["isSS"] > 0
        np.testing.assert_array_equal(ss, d["l1_charge"] * d["l2_charge"] > 0)
        truth = np.ones(n, dtype=bool)
        nflip = np.zeros(n, dtype=np.int8)
        for i in (1, 2):
            gc = d[f"l{i}_genChargeIdx"]
            truth &= (np.abs(gc) == 1) & (d[f"l{i}_genPtIdx"] > 0)
            truth &= np.isin(d[f"l{i}_genPartFlav"], [1, 15])
            nflip += (d[f"l{i}_charge"] != gc).astype(np.int8)
        truth &= d["l1_genChargeIdx"] * d["l2_genChargeIdx"] < 0
        weights = (d["weight"].astype(float), d["weight"].astype(float) / d["w_dy"])
        # Fold >=8000 into the final plotting bin and record it explicitly.
        massjj = np.minimum(d["m_lljj"], np.nextafter(MJJ[-1], 0))
        for ki in range(2):
            for ci, chid in enumerate((11, 13)):
                for fi in range(2):
                    for si in range(2):
                        sel = (d["channel"] == chid) & (fold == fi) & (ss == bool(si))
                        if ki:
                            sel &= truth & (nflip == si)
                        x, y = d["m_l1l2"][sel], massjj[sel]
                        count[ki, ci, fi, si] += np.histogram2d(x, y, (MLL, MJJ))[0].astype(np.int64)
                        for mi, w in enumerate(weights):
                            h = np.histogram2d(x, y, (MLL, MJJ), weights=w[sel])[0]
                            v = np.histogram2d(x, y, (MLL, MJJ), weights=w[sel]**2)[0]
                            hist[mi, ki, ci, fi, si] += h
                            var[mi, ki, ci, fi, si] += v
        sources.append(dict(file=path.name, bytes=path.stat().st_size,
                            mtime_ns=path.stat().st_mtime_ns, selected=n,
                            ss=int(ss.sum()), truth_singleflip_ss=int((truth & ss & (nflip == 1)).sum()),
                            overflow_mlljj=int((d["m_lljj"] >= 8000).sum()),
                            exactly_mll400=int((d["m_l1l2"] == 400).sum())))
        print(f"{path.name}: selected={n:,}, SS={ss.sum():,}", flush=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, hist=hist, var=var, count=count, mll_edges=MLL, mlljj_edges=MJJ)
    metadata = dict(seed=seed, modes=MODES, kinds=KINDS, channels=CHANNELS,
                    folds=["train", "validation"], signs=["OS", "SS"],
                    selection="hasPair, nJet>=2, passResolved, mlljj>800, mll>=60; no tightCharge",
                    prompt_singleflip="genPartIdx lepton match, genPtIdx>0, genPartFlav in {1,15}, gen OS; reco OS has 0 flips, reco SS has 1 flip",
                    noDY="weight/w_dy; all other nominal weights retained",
                    overflow="mlljj>=8000 included in final 3200-8000 display bin",
                    source_directory=str(dumps.resolve()), source_path_is_provenance_only=True, sources=sources)
    cache.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    return hist, var, count


def effective(h, v):
    return h*h/v if v > 0 else 0.


def group_mll(train, trainvar, min_neff):
    """Merge low-stat training mll bins; never cross 100, 150 or 400 GeV."""
    groups = []
    for lo, hi in ((60, 100), (100, 150), (150, 400), (400, np.inf)):
        inds = np.flatnonzero((MLL[:-1] >= lo) & (MLL[1:] <= hi))
        segment, pending = [], []
        for i in inds:
            pending.append(int(i))
            sh, sv = train[:, pending].sum(axis=(1, 2)), trainvar[:, pending].sum(axis=(1, 2))
            if all(effective(sh[s], sv[s]) >= min_neff for s in (0, 1)):
                segment.append(pending); pending = []
        if pending:
            if segment:
                segment[-1] += pending
            else:
                segment.append(pending)
        groups.extend(segment)
    return groups


def normalized(h, cov):
    total = h.sum()
    if total <= 0:
        return None
    jac = np.eye(len(h))/total - np.outer(h, np.ones(len(h)))/total**2
    return h/total, jac @ cov @ jac.T


def shape_test(pred, pcov, target, tcov):
    pp, tt = normalized(pred, pcov), normalized(target, tcov)
    if pp is None or tt is None:
        return dict(status="empty"), None
    p, vp = pp; t, vt = tt
    # Exclude bins too sparse for a Gaussian chi2. Normalization is still over
    # the full mass range, so use the actual rank of the retained covariance.
    neff = np.divide(target**2, np.diag(tcov), out=np.zeros(len(target)), where=np.diag(tcov)>0)
    valid = (neff >= 10) & (p > 0) & (t > 0)
    cov = (vp + vt)[np.ix_(valid, valid)]
    delta = (p-t)[valid]
    tolerance = max(1e-14, np.max(np.diag(cov))*1e-10) if cov.size else 1e-14
    rank = int(np.linalg.matrix_rank(cov, tol=tolerance)) if cov.size else 0
    value = float(delta @ np.linalg.pinv(cov, rcond=1e-10) @ delta) if rank else None
    prob = float(chi2.sf(value, rank)) if rank else None
    r, er = np.full(len(p), np.nan), np.full(len(p), np.nan)
    good = t > 0
    r[good] = p[good]/t[good]
    er[good] = np.sqrt(np.maximum(0, np.diag(vp)[good]/t[good]**2 + p[good]**2*np.diag(vt)[good]/t[good]**4))
    return dict(status="ok", chi2=value, ndf=rank, p_value=prob,
                gaussian_bins=np.flatnonzero(valid).tolist(),
                prediction_total=float(pred.sum()), target_total=float(target.sum()),
                yield_ratio=float(pred.sum()/target.sum()),
                yield_ratio_error=float(np.sqrt(max(0,pcov.sum()/target.sum()**2
                       + pred.sum()**2*tcov.sum()/target.sum()**4)))), (p, vp, t, vt, r, er)


def evaluate(h, v, groups, lo, hi):
    """h/v: fold, sign, fine mll, mlljj. Factor uncertainty is correlated across mlljj."""
    groups = [g for g in groups if MLL[g[0]] >= lo and MLL[g[-1]+1] <= hi]
    # Explicit stacking avoids NumPy advanced-index axis surprises.
    tr = np.array([[h[0, s][g].sum() for s in (0, 1)] for g in groups])
    tv = np.array([[v[0, s][g].sum() for s in (0, 1)] for g in groups])
    if np.any(tr <= 0):
        return None, dict(status="unconstrained training bin", training_yields=tr.tolist())
    r = tr[:, 1]/tr[:, 0]
    vr = tv[:, 1]/tr[:, 0]**2 + tr[:, 1]**2*tv[:, 0]/tr[:, 0]**4
    os = np.array([h[1, 0][g].sum(axis=0) for g in groups])
    osv = np.array([v[1, 0][g].sum(axis=0) for g in groups])
    ss = np.array([h[1, 1][g].sum(axis=0) for g in groups])
    ssv = np.array([v[1, 1][g].sum(axis=0) for g in groups])
    pred = (os*r[:, None]).sum(axis=0)
    pcov = np.diag((osv*r[:, None]**2).sum(axis=0)) + os.T @ np.diag(vr) @ os
    target = ss.sum(axis=0); tcov = np.diag(ssv.sum(axis=0))
    before = os.sum(axis=0); bcov = np.diag(osv.sum(axis=0))
    # Check mll closure on the independent validation sample, in the fitted bins.
    pm = os.sum(axis=1)*r
    pmcov = np.diag(osv.sum(axis=1)*r*r + os.sum(axis=1)**2*vr)
    tm = ss.sum(axis=1); tmcov = np.diag(ssv.sum(axis=1))
    bm = os.sum(axis=1); bmcov = np.diag(osv.sum(axis=1))
    stats, data = shape_test(pred, pcov, target, tcov)
    beforestats, beforedata = shape_test(before, bcov, target, tcov)
    massstats, massdata = shape_test(pm, pmcov, tm, tmcov)
    _, massbefore = shape_test(bm, bmcov, tm, tmcov)
    edges = np.array([MLL[g[0]] for g in groups] + [MLL[groups[-1][-1]+1]])
    info = dict(status="ok", mlljj=stats, mlljj_before=beforestats, mll=massstats,
                training_mll_bins=[[float(MLL[g[0]]), None if np.isinf(MLL[g[-1]+1]) else float(MLL[g[-1]+1])] for g in groups],
                training_neff_ss=[effective(tr[i, 1], tv[i, 1]) for i in range(len(groups))],
                factors=r.tolist(), factor_errors=np.sqrt(vr).tolist())
    info["mlljj_bins"] = []
    if data is not None:
        for i,(low,high) in enumerate(zip(MJJ[:-1],MJJ[1:])):
            info["mlljj_bins"].append(dict(low=float(low),high=float(high),
                includes_overflow=bool(i==len(MJJ)-2),
                shape_ratio=float(data[4][i]) if np.isfinite(data[4][i]) else None,
                shape_ratio_error=float(data[5][i]) if np.isfinite(data[5][i]) else None,
                target_neff=effective(target[i],tcov[i,i])))
    arrays = dict(mlljj_pred=pred, mlljj_pred_cov=pcov, mlljj_ss=target, mlljj_ss_cov=tcov,
                  mlljj_before=before, mlljj_before_cov=bcov, mll_pred=pm, mll_pred_cov=pmcov,
                  mll_ss=tm, mll_ss_cov=tmcov, mll_before=bm, mll_before_cov=bmcov,
                  mll_edges=edges, mlljj_edges=MJJ, factors=r, factor_var=vr)
    return (data, beforedata, massdata, massbefore, edges, arrays), info


def draw(ROOT, stem, edges, data, before, title, subtitle, stats, massname):
    if data is None:
        return
    p, vp, t, vt, r, er = data
    b, vb = before[:2]
    edges = edges.copy()
    overflow = not np.isfinite(edges[-1])
    if overflow:
        edges[-1] = max(edges[-2]*1.5, 2000)
    c = ROOT.TCanvas("closure", "", 880, 840)
    top = ROOT.TPad("top", "", 0, .31, 1, 1); top.SetBottomMargin(.03); top.SetTopMargin(.22)
    top.SetLogx(); top.SetLogy(); top.Draw()
    bot = ROOT.TPad("bot", "", 0, 0, 1, .31); bot.SetTopMargin(.025); bot.SetBottomMargin(.31); bot.SetLogx(); bot.Draw()
    top.cd(); keep = []
    legend = ROOT.TLegend(.47, .56, .89, .75); legend.SetBorderSize(0); legend.SetTextSize(.028)
    for i, (y, cov, label, color) in enumerate(((t, vt, "SS validation MC", ROOT.kBlack),
            (b, vb, "OS: normalization only", ROOT.kAzure+1),
            (p, vp, "OS #times T(m_{ll})", ROOT.kRed+1))):
        hh = ROOT.TH1D(f"h{i}", ";;unit-area events / bin", len(edges)-1, edges)
        for j in range(len(y)):
            hh.SetBinContent(j+1, y[j]); hh.SetBinError(j+1, np.sqrt(max(0,cov[j,j])))
        hh.SetLineColor(color); hh.SetMarkerColor(color); hh.SetLineWidth(2); hh.SetMarkerStyle(20)
        hh.GetXaxis().SetLabelSize(0); hh.GetYaxis().SetTitleOffset(1.25)
        hh.SetMaximum(max(t.max(), b.max(), p.max())*30); hh.SetMinimum(1e-5)
        if i == 1: hh.SetLineStyle(2)
        hh.Draw(("E1" if i == 0 else "hist") + (" same" if i else ""))
        legend.AddEntry(hh, label, "lep" if i == 0 else "l"); keep.append(hh)
    legend.Draw()
    tx = ROOT.TLatex(); tx.SetNDC(); tx.SetTextFont(42); tx.SetTextSize(.033)
    tx.DrawLatex(.10, .955, title); tx.SetTextSize(.026); tx.DrawLatex(.10, .905, subtitle)
    testlabel = "Insufficient statistics for Gaussian shape test"
    if stats.get("ndf"):
        testlabel = f"Shape #chi^{{2}}/ndf = {stats['chi2']:.1f}/{stats['ndf']}, p = {stats['p_value']:.2g}"
    tx.DrawLatex(.10, .855, testlabel)
    tx.SetTextSize(.022); tx.DrawLatex(.10, .805, "Independent 50% validation; band includes T(m_{ll}) statistics")
    bot.cd()
    frame = ROOT.TH1D("frame", f";{massname} [GeV];prediction / SS", len(edges)-1, edges)
    finite_r = r[np.isfinite(r)]
    ymax = max(2., min(5., float(finite_r.max())*1.2 if len(finite_r) else 2.))
    frame.SetMinimum(0); frame.SetMaximum(ymax)
    frame.GetYaxis().SetNdivisions(505); frame.GetYaxis().SetTitleSize(.09); frame.GetYaxis().SetTitleOffset(.5); frame.GetYaxis().SetLabelSize(.08)
    frame.GetXaxis().SetTitleSize(.11); frame.GetXaxis().SetLabelSize(.09); frame.Draw("axis")
    band = ROOT.TGraphErrors(); obs = ROOT.TGraphErrors(); raw = ROOT.TGraph()
    for j in np.flatnonzero(t > 0):
        x = (edges[j]+edges[j+1])/2; dx = (edges[j+1]-edges[j])/2
        n = band.GetN(); band.SetPoint(n,x,r[j]); band.SetPointError(n,dx,np.sqrt(max(0,vp[j,j]))/t[j])
        obs.SetPoint(n,x,1); obs.SetPointError(n,0,np.sqrt(max(0,vt[j,j]))/t[j])
        raw.SetPoint(n,x,b[j]/t[j])
    band.SetFillColorAlpha(ROOT.kRed-9,.7); band.SetLineColor(ROOT.kRed+1); band.Draw("2 SAME")
    mid = ROOT.TGraph()
    for j in np.flatnonzero(np.isfinite(r)):
        mid.SetPoint(mid.GetN(),(edges[j]+edges[j+1])/2,r[j])
    mid.SetLineColor(ROOT.kRed+1); mid.SetMarkerColor(ROOT.kRed+1); mid.SetMarkerStyle(20); mid.SetMarkerSize(.6); mid.Draw("LP SAME")
    obs.SetMarkerStyle(20); obs.SetMarkerSize(.6); obs.Draw("P SAME")
    raw.SetLineColor(ROOT.kAzure+1); raw.SetLineStyle(2); raw.SetLineWidth(2); raw.Draw("L SAME")
    line = ROOT.TLine(edges[0],1,edges[-1],1); line.SetLineStyle(2); line.Draw()
    for ext in ("png","pdf"):
        c.SaveAs(str(stem.with_suffix("."+ext)))
    c.Close()


def write_report(dest, results):
    lines = ["# mll-only OS -> SS reweighting: mlljj closure", "",
             "Resolved DY MC only; nJet>=2, passResolved, mlljj>800. Raw charge, no tightCharge requirement.",
             "Independent random half for training T(mll)=SS/OS, half for validation; no data used.",
             "All shapes normalized to unit area in the displayed region. No extra mlljj reweighting.",
             "Shape covariance includes training-factor correlations between mlljj bins and unit-area normalization.",
             "Gaussian chi2 uses only bins with SS effective entries >=10; low-stat results are descriptive.",
             "Last mlljj bin includes overflow >=8000 GeV. Nominal DY corrections are the primary result; noDY is a crosscheck.", "",
             "| mode | target | channel | region | mll chi2/ndf (p) | mlljj before (p) | mlljj after (p) | predicted/SS yield |",
             "|---|---|---|---|---|---|---|---|"]
    def fmt(s):
        if not s.get("ndf"): return "insufficient stats"
        return f"{s['chi2']:.2f}/{s['ndf']} ({s['p_value']:.3g})"
    for key, r in results.items():
        if r["status"] != "ok":
            lines.append(f"| {' | '.join(key.split('/'))} | {r['status']} | | | |")
            continue
        yr=r['mlljj'].get('yield_ratio'); ye=r['mlljj'].get('yield_ratio_error')
        yield_text=f"{yr:.3f} +/- {ye:.3f}" if yr is not None else "empty validation target"
        lines.append(f"| {' | '.join(key.split('/'))} | {fmt(r['mll'])} | {fmt(r['mlljj_before'])} | {fmt(r['mlljj'])} | {yield_text} |")
    lines += ["", "A successful mll check alone does not imply mlljj closure. A failure after successful mll validation rejects this mll-only OS kernel at the tested binning/statistics.",
              "This tests the conditional mlljj shape of 2-jet OS vs SS. It does not construct a second jet from a 1-jet event or validate a 1j->2j transfer.",
              "prompt_singleflip requires both leptons matched to prompt/tau-origin gen leptons with gen OS; OS has zero flips and SS exactly one flip.",
              "reco_all uses the full reconstructed DY OS/SS populations, including unmatched or nonprompt leptons."]
    (dest/"RESULTS.md").write_text("\n".join(lines)+"\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dumps", type=Path)
    ap.add_argument("--cache", type=Path, default=BASE/"data/mll_to_mlljj_histograms.npz")
    ap.add_argument("--out-dir", type=Path, default=BASE/"AN_rawcharge/09_mll_to_mlljj_closure")
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--min-train-neff", type=float, default=30)
    ap.add_argument("--validation-fold", type=int, choices=(0,1), default=1)
    ap.add_argument("--channels", nargs="+", choices=CHANNELS, default=list(CHANNELS))
    ap.add_argument("--modes", nargs="+", choices=MODES, default=list(MODES))
    ap.add_argument("--kinds", nargs="+", choices=KINDS, default=list(KINDS))
    a = ap.parse_args()
    if a.dumps:
        hist, var, count = build_cache(a.dumps,a.cache,a.seed)
    else:
        if not a.cache.exists(): ap.error("Supply --dumps once to build the local histogram cache")
        with np.load(a.cache) as z:
            np.testing.assert_array_equal(z["mll_edges"],MLL); np.testing.assert_array_equal(z["mlljj_edges"],MJJ)
            hist,var,count=z["hist"],z["var"],z["count"]
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    results={}
    for mi,mode in enumerate(MODES):
        if mode not in a.modes: continue
        for ki,kind in enumerate(KINDS):
            if kind not in a.kinds: continue
            for ci,ch in enumerate(CHANNELS):
                if ch not in a.channels: continue
                h,v=hist[mi,ki,ci],var[mi,ki,ci]
                if a.validation_fold == 0:
                    h,v=h[::-1],v[::-1]
                groups=group_mll(h[0],v[0],a.min_train_neff)
                for region,(lo,hi) in REGIONS.items():
                    key=f"{mode}/{kind}/{ch}/{region}"
                    payload,info=evaluate(h,v,groups,lo,hi)
                    results[key]=info
                    if payload is None:
                        print(key,info["status"],flush=True); continue
                    dest=a.out_dir/key; dest.mkdir(parents=True,exist_ok=True)
                    data,before,mass,massbefore,edges,arrays=payload
                    np.savez_compressed(dest/"histograms.npz",**arrays)
                    (dest/"summary.json").write_text(json.dumps(info,indent=2,allow_nan=False)+"\n")
                    title=f"{ch} DY MC, {mode}, {'reco OS/SS' if ki==0 else 'prompt single charge flip'}"
                    subtitle=f"#geq2 jets, m_{{lljj}}>800; {lo:g} #leq m_{{ll}} < {hi:g} GeV"
                    draw(ROOT,dest/"mlljj_closure",MJJ,data,before,title,subtitle,info["mlljj"],"m_{lljj}")
                    draw(ROOT,dest/"mll_validation",edges,mass,massbefore,title,subtitle,info["mll"],"m_{ll}")
                    print(key,"mll",info["mll"],"mlljj",info["mlljj"],flush=True)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    (a.out_dir/"summary.json").write_text(json.dumps(results,indent=2,allow_nan=False)+"\n")
    (a.out_dir/"run_config.json").write_text(json.dumps(dict(validation_fold=a.validation_fold,
        min_train_neff=a.min_train_neff, channels=a.channels, modes=a.modes, kinds=a.kinds),indent=2)+"\n")
    write_report(a.out_dir,results)


if __name__ == "__main__":
    main()
