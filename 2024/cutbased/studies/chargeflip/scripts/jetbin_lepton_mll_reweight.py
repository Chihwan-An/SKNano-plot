#!/usr/bin/env python3
"""Match nominal DY OS 1j to >=2j in mll, then compare lepton kinematics.

Uses the portable histogram/moment cache from jetbin_lepton_shapes.py.
This is a same-sample conditional-shape diagnostic, not an independent closure.
"""
import argparse
import json

import numpy as np

from jetbin_lepton_shapes import BASE, MLL, PT, ETA, CATS, CHANNELS, REGIONS, FEATURES, estimate


def normalized(h, cov):
    n = h.sum()
    jac = np.eye(len(h))/n - np.outer(h, np.ones(len(h)))/n**2
    return h/n, jac @ cov @ jac.T, jac


def comparison(s, vs, t, vt):
    """Input axes: mll, observable bin. Include fitted-factor correlations."""
    sm, tm = s.sum(axis=1), t.sum(axis=1)
    if np.any(sm <= 0) or np.any(tm <= 0):
        raise ValueError("Empty mll bin: merge bins before reweighting")
    ps, factors = s/sm[:, None], tm/sm
    pred = (factors[:, None]*s).sum(axis=0)
    cp = np.zeros((s.shape[1], s.shape[1]))
    cross = np.zeros_like(cp)
    for p, v, w, f in zip(ps, vs, vt, factors):
        cp += f*f*(np.diag(v)-np.outer(p,v)-np.outer(v,p)+np.outer(p,p)*v.sum())
        cp += np.outer(p,p)*w.sum()
        cross += np.outer(p,w)
    before, cb, _ = normalized(s.sum(axis=0), np.diag(vs.sum(axis=0)))
    after, ca, ja = normalized(pred, cp)
    target, ct, jt = normalized(t.sum(axis=0), np.diag(vt.sum(axis=0)))
    cross = ja @ cross @ jt.T
    ratios, errors = [], []
    for p, c, x in ((before,cb,np.zeros_like(cross)),(after,ca,cross)):
        ok = target > 0
        r, e = np.full_like(p,np.nan), np.full_like(p,np.nan)
        r[ok] = p[ok]/target[ok]
        v = np.diag(c)[ok]/target[ok]**2 + p[ok]**2*np.diag(ct)[ok]/target[ok]**4
        v -= 2*p[ok]*np.diag(x)[ok]/target[ok]**3
        e[ok] = np.sqrt(np.maximum(v,0))
        ratios.append(r); errors.append(e)
    return dict(before=before,after=after,target=target,cov_before=cb,cov_after=ca,
                cov_target=ct,cov_after_target=cross,ratios=np.array(ratios),
                errors=np.array(errors),tv_before=float(.5*np.abs(before-target).sum()),
                tv_after=float(.5*np.abs(after-target).sum()))


def weighted_feature(source, target):
    """Rows are per-mll sumw, sumw2, sumwx, sumw2x, sumw2x2."""
    sm, sv, sx, svx, svxx = source.T
    tm, tv, _, _, _ = target.T
    mu = sx/sm
    n = tm.sum()
    mean = np.dot(tm,mu)/n
    variance = np.sum((tm/(n*sm))**2*(svxx-2*mu*svx+mu*mu*sv))
    variance += np.sum(tv*(mu-mean)**2)/n**2
    return dict(value=float(mean),error=float(np.sqrt(max(variance,0))))


def draw(ROOT, dest, ch, region, cat, panels, matching="m_{ll}", independent=False):
    canvas = ROOT.TCanvas("matched_leptons","",1250,1050)
    keep = []
    colors = (ROOT.kBlack, ROOT.kAzure+2, ROOT.kRed+1)
    names = ("2j target", "1j before matching", f"1j after {matching} matching")
    for panel,(leg,var) in enumerate(((0,"pt"),(0,"eta"),(1,"pt"),(1,"eta"))):
        d = panels[f"l{leg+1}_{var}"]
        col, row = panel%2, panel//2
        y0,y1 = (.48,.92) if row==0 else (.015,.455)
        canvas.cd()
        outer = ROOT.TPad(f"outer{panel}","",.01+.49*col,y0,.50+.49*col,y1)
        outer.Draw(); outer.cd(); keep.append(outer)
        top = ROOT.TPad(f"top{panel}","",0,.32,1,1)
        bot = ROOT.TPad(f"bot{panel}","",0,0,1,.32)
        top.SetBottomMargin(.025); top.SetTopMargin(.14); top.SetLeftMargin(.14)
        bot.SetTopMargin(.025); bot.SetBottomMargin(.32); bot.SetLeftMargin(.14)
        if var=="pt": top.SetLogx(); top.SetLogy(); bot.SetLogx()
        if var=="pt": bot.SetLogy()
        top.Draw(); bot.Draw(); keep += [top,bot]
        edges = PT if var=="pt" else ETA
        variable = "p_{T}" if var=="pt" else ("|#eta_{SC}|" if ch=="EE" else "|#eta|")
        top.cd()
        legend = ROOT.TLegend(.43,.64,.90,.84); legend.SetBorderSize(0); legend.SetTextSize(.038)
        ymax = max(d[k].max() for k in ("target","before","after"))*(50 if var=="pt" else 1.7)
        for idx,key in enumerate(("target","before","after")):
            hh = ROOT.TH1D(f"h{panel}_{idx}",";;fraction / bin",len(edges)-1,edges)
            for i,value in enumerate(d[key]):
                hh.SetBinContent(i+1,float(value)); hh.SetBinError(i+1,float(np.sqrt(max(0,d[f"cov_{key}"][i,i]))))
            hh.SetLineColor(colors[idx]); hh.SetMarkerColor(colors[idx]); hh.SetLineWidth(2)
            if key=="before": hh.SetLineStyle(2)
            hh.GetXaxis().SetLabelSize(0); hh.GetYaxis().SetTitleSize(.055)
            hh.GetYaxis().SetLabelSize(.045); hh.GetYaxis().SetTitleOffset(1.05)
            hh.SetMinimum(1e-5 if var=="pt" else 0); hh.SetMaximum(ymax)
            hh.Draw("hist e"+(" same" if idx else "")); legend.AddEntry(hh,names[idx],"l"); keep.append(hh)
        legend.Draw(); keep.append(legend)
        label = ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.048)
        label.DrawLatex(.14,.92,f"{'Leading' if leg==0 else 'Subleading'} lepton {variable}"); keep.append(label)
        bot.cd()
        frame = ROOT.TH1D(f"frame{panel}",f";{variable}"+(" [GeV]" if var=="pt" else "")+";1j / target",len(edges)-1,edges)
        values = d["ratios"][np.isfinite(d["ratios"]) & (d["ratios"]>0)]
        rmin,rmax = values.min(),values.max()
        frame.SetMinimum(min(.5,rmin/1.4) if var=="pt" else min(.9,rmin*.95))
        frame.SetMaximum(max(2.,rmax*1.4) if var=="pt" else max(1.1,rmax*1.05))
        frame.GetYaxis().SetMoreLogLabels(); frame.GetYaxis().SetNoExponent()
        frame.GetYaxis().SetNdivisions(505); frame.GetYaxis().SetTitleSize(.10)
        frame.GetYaxis().SetTitleOffset(.6); frame.GetYaxis().SetLabelSize(.085)
        frame.GetXaxis().SetTitleSize(.12); frame.GetXaxis().SetLabelSize(.10)
        frame.Draw("axis"); keep.append(frame)
        for idx,(ratio,error) in enumerate(zip(d["ratios"],d["errors"])):
            g = ROOT.TGraphErrors()
            for i in np.flatnonzero(np.isfinite(ratio)&(ratio>0)):
                j=g.GetN(); g.SetPoint(j,float((edges[i]+edges[i+1])/2),float(ratio[i]))
                g.SetPointError(j,float((edges[i+1]-edges[i])/2),float(error[i]))
            g.SetLineColor(colors[idx+1]); g.SetMarkerColor(colors[idx+1]); g.SetMarkerStyle(20+idx)
            g.SetMarkerSize(.5); g.Draw("P SAME"); keep.append(g)
        line=ROOT.TLine(edges[0],1,edges[-1],1); line.SetLineStyle(2); line.Draw(); keep.append(line)
    canvas.cd(); label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.024)
    lo,hi=REGIONS[region]
    target = "nJet#geq2" if cat=="ge2j" else "nJet#geq2, resolved, m_{lljj}>800"
    label.DrawLatex(.04,.976,f"{ch} DY OS; target: {target}; {lo:g} #leq m_{{ll}} < {hi:g} GeV")
    label.SetTextSize(.019)
    label.DrawLatex(.04,.94,"Nominal DY; unit area; no charge flip; "+
                    ("independent test half; factor errors included" if independent else "same sample; fitted-weight correlations included"))
    for ext in ("png","pdf"): canvas.SaveAs(str(dest/f"lepton_shapes_{ch}.{ext}"))
    canvas.Close()


def draw_mass(ROOT, dest, ch, cat, source, target, factor, factor_error):
    canvas=ROOT.TCanvas("mass_match","",1100,800); canvas.Divide(1,2); keep=[]
    edges=MLL.copy(); edges[-1]=3000  # >=2000 overflow display bin, not a 3000 GeV selection.
    pad=canvas.cd(1); pad.SetLogx(); pad.SetLogy(); pad.SetBottomMargin(.14)
    legend=ROOT.TLegend(.48,.65,.88,.88); legend.SetBorderSize(0)
    for idx,(values,label,color) in enumerate(((target,"2j target",ROOT.kBlack),
            (source*target.sum()/source.sum(),"1j before (total normalized)",ROOT.kAzure+2),
            (source*factor,"1j after m_{ll} matching",ROOT.kRed+1))):
        h=ROOT.TH1D(f"mass{idx}",f"{ch} DY OS, target={cat};m_{{ll}} [GeV];weighted events / bin",len(edges)-1,edges)
        for i,v in enumerate(values): h.SetBinContent(i+1,float(v))
        h.SetLineWidth(3 if idx==0 else 2); h.SetLineColor(color)
        if idx==2: h.SetLineStyle(2)
        h.SetMinimum(target.min()*.2); h.SetMaximum(max(target.max(),values.max())*10)
        h.Draw("hist"+(" same" if idx else "")); legend.AddEntry(h,label,"l"); keep.append(h)
    legend.Draw(); keep.append(legend)
    pad=canvas.cd(2); pad.SetLogx(); pad.SetBottomMargin(.18)
    h=ROOT.TH1D("factors", ";m_{ll} [GeV];N_{2j} / N_{1j}",len(edges)-1,edges)
    for i,(v,e) in enumerate(zip(factor,factor_error)):
        h.SetBinContent(i+1,float(v)); h.SetBinError(i+1,float(e))
    h.SetMinimum(0); h.Draw("e1"); keep.append(h)
    label=ROOT.TLatex(); label.SetNDC(); label.SetTextSize(.035)
    label.DrawLatex(.13,.84,"m_{ll} matched by construction; last bin: #geq2000 GeV")
    label.DrawLatex(.13,.78,"Nominal DY weights; no charge-flip weight")
    for ext in ("png","pdf"): canvas.SaveAs(str(dest/f"mll_matching_{ch}.{ext}"))
    canvas.Close()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache",type=str,default=str(BASE/"data/jetbin_lepton_histograms.npz"))
    ap.add_argument("--out-dir",type=str,default=str(BASE/"AN_rawcharge/11_1jet_2jet_mll_reweighted"))
    args=ap.parse_args()
    from pathlib import Path
    out=Path(args.out_dir)
    with np.load(args.cache) as z:
        for key,ref in (("mll_edges",MLL),("pt_edges",PT),("eta_edges",ETA)):
            np.testing.assert_array_equal(z[key],ref)
        hist,var,moments=z["hist"],z["var"],z["moments"]
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary={}; factors={}
    for ci,ch in enumerate(CHANNELS):
        for ki,cat in enumerate(CATS[1:],1):
            dest=out/cat; dest.mkdir(parents=True,exist_ok=True)
            sm=hist[ci,0,0].sum(axis=(1,2)); tm=hist[ci,ki,0].sum(axis=(1,2))
            sv=var[ci,0,0].sum(axis=(1,2)); tv=var[ci,ki,0].sum(axis=(1,2))
            f=tm/sm; fe=np.sqrt(tv/sm**2+tm**2*sv/sm**4)
            np.testing.assert_allclose(sm*f,tm,rtol=1e-12)
            factors[f"{ch}/{cat}"]=[dict(low=float(MLL[i]),high=float(MLL[i+1]) if np.isfinite(MLL[i+1]) else None,
                factor=float(f[i]),error=float(fe[i]),source=float(sm[i]),target=float(tm[i]),
                source_neff=float(sm[i]**2/sv[i]),target_neff=float(tm[i]**2/tv[i])) for i in range(len(f))]
            np.savez_compressed(dest/f"mll_factors_{ch}.npz",mll_edges=MLL,factor=f,error=fe,
                                source=sm,target=tm,after=sm*f)
            draw_mass(ROOT,dest,ch,cat,sm,tm,f,fe)
            for region,(lo,hi) in REGIONS.items():
                sel=(MLL[:-1]>=lo)&(MLL[1:]<=hi)
                rd=dest/region; rd.mkdir(exist_ok=True)
                panels={}; record={}
                for leg in range(2):
                    s=hist[ci,0,leg,sel]; vs=var[ci,0,leg,sel]
                    t=hist[ci,ki,leg,sel]; vt=var[ci,ki,leg,sel]
                    rec={}
                    for obs in ("pt","eta","joint"):
                        arrays=[a.reshape(len(a),-1) if obs=="joint" else a.sum(axis=2 if obs=="pt" else 1) for a in (s,vs,t,vt)]
                        d=comparison(*arrays); panels[f"l{leg+1}_{obs}"]=d
                        rec[f"{obs}_TV"]={k:d[f"tv_{k}"] for k in ("before","after")}
                        np.savez_compressed(rd/f"comparison_{ch}_l{leg+1}_{obs}.npz",**d,pt_edges=PT,eta_edges=ETA)
                    for fi,feature in enumerate(FEATURES):
                        ms=moments[ci,0,leg,sel,fi]; mt=moments[ci,ki,leg,sel,fi]
                        rec[feature]=dict(before=estimate(ms.sum(axis=0)),after=weighted_feature(ms,mt),target=estimate(mt.sum(axis=0)))
                    record[f"l{leg+1}"]=rec
                summary[f"{ch}/{cat}/{region}"]=record
                draw(ROOT,rd,ch,region,cat,panels)
    (out/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    (out/"mll_factors.json").write_text(json.dumps(factors,indent=2,allow_nan=False)+"\n")
    lines=["# 1j OS -> 2j OS: mll matching, then lepton-shape comparison", "",
        "Nominal DY corrections and lepton SF on. No charge-flip weights, no collision data.",
        "Source: nJet==1. ge2j target: nJet>=2 only. SRtopology target: nJet>=2, passResolved, mlljj>800.",
        "In each mll bin, multiply the original 1j weight by sumw(target)/sumw(1j). Factors are channel/target specific.",
        "mll edges [GeV]: "+", ".join(f"{x:g}" for x in MLL)+".",
        "Plots compare unit-area shapes in each mll region; the unnormalized reweighted mll yield also equals the target in every bin.",
        "Matching uses the same samples: exact binned mll agreement is by construction, not an independent closure test.",
        "Errors include weighted MC statistics, fitted-factor uncertainty and its correlation with the target. No systematics.",
        "pT moments are unclipped; final plotted pT bin includes >=2000 GeV. EE uses abs eta_SC, MM abs eta.",
        "TV = half the sum of absolute differences of normalized bins; 0 identical, 1 disjoint. Finite MC and binning affect TV.",
        "", "| channel/target/region | leg | mean pT: before -> after -> target [GeV] | eta>=1.566: before -> after -> target [%] | joint pT/eta TV before -> after |",
        "|---|---|---|---|---|"]
    for key,r in summary.items():
        for leg,c in r.items():
            cols=[]
            for feat,scale in (("mean_pt",1),("fraction_abs_eta_ge1p566",100)):
                cols.append(" -> ".join(f"{c[feat][k]['value']*scale:.3f} +/- {c[feat][k]['error']*scale:.3f}" for k in ("before","after","target")))
            cols.append(f"{c['joint_TV']['before']:.4f} -> {c['joint_TV']['after']:.4f}")
            lines.append(f"| {key} | {leg} | "+" | ".join(cols)+" |")
    (out/"RESULTS.md").write_text("\n".join(lines)+"\n")
    print("Finished:",out)


if __name__=="__main__":
    main()
