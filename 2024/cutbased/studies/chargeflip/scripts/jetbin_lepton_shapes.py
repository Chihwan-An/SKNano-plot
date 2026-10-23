#!/usr/bin/env python3
"""Nominal DY OS lepton pT/eta: exactly 1 jet, >=2 jets, and resolved SR topology.

Read DY MC only, no charge-flip weights, no collision data. Outputs and the
small histogram/moment cache are portable with the chargeflip directory.
"""
import argparse
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
MLL = np.array([60,70,80,90,100,110,120,130,150,175,200,250,300,400,
                500,700,1000,1300,1600,2000,np.inf])
PT = np.array([53,60,70,80,100,130,170,220,300,400,600,1000,2000.])
ETA = np.array([0,.4,.8,1.1,1.4442,1.566,1.8,2.1,2.5])
CATS = ("1j", "ge2j", "SRtopology")
CHANNELS = ("EE", "MM")
REGIONS = {"inclusive": (60,np.inf), "Zwindow": (60,150),
           "sideband": (150,400), "highmass": (400,np.inf)}
FEATURES = ("mean_pt", "mean_abs_eta", "fraction_pt_ge150", "fraction_pt_ge400",
            "fraction_abs_eta_ge1p566", "fraction_pt_ge150_and_abs_eta_ge1p566")
TERMS = ("sumw", "sumw2", "sumwx", "sumw2x", "sumw2x2")
COLS = ("channel", "hasPair", "isSS", "nJet", "passResolved", "m_lljj", "m_l1l2",
        "weight", "l1_pt", "l2_pt", "l1_scEta", "l2_scEta")


def build(dumps, cache):
    files = sorted(dumps.glob("tree_Skim_HNWR_DYto2L*.npz"))
    if not files: raise ValueError(f"No DY NPZ in {dumps}")
    # channel, jet category, leg, mll, pT, abs eta
    shape = (2,3,2,len(MLL)-1,len(PT)-1,len(ETA)-1)
    h, v = np.zeros(shape), np.zeros(shape)
    counts = np.zeros(shape, dtype=np.int64)
    moments = np.zeros(shape[:4]+(len(FEATURES),len(TERMS)))
    sources = []
    for path in files:
        with np.load(path) as z:
            missing = set(COLS)-set(z.files)
            if missing: raise ValueError(f"{path.name}: missing {missing}")
            sel = (z["hasPair"]>0) & (z["isSS"]==0) & (z["m_l1l2"]>=60) & (z["nJet"]>=1)
            d = {k:z[k][sel] for k in COLS}
        if not all(np.all(np.isfinite(x)) for x in d.values()):
            raise ValueError(f"Invalid input: {path}")
        if np.any(d["weight"]<0): raise ValueError("Negative weights need a revised interpretation")
        masks = (d["nJet"]==1, d["nJet"]>=2,
                 (d["nJet"]>=2)&(d["passResolved"]>0)&(d["m_lljj"]>800))
        for ci,chid in enumerate((11,13)):
            for ki,cut in enumerate(masks):
                use = cut & (d["channel"]==chid)
                mass=d["m_l1l2"][use].astype(float); w=d["weight"][use].astype(float); w2=w*w
                bins=np.searchsorted(MLL,mass,side="right")-1
                for li in range(2):
                    pt=d[f"l{li+1}_pt"][use].astype(float)
                    eta=np.abs(d[f"l{li+1}_scEta"][use].astype(float))
                    if np.any(pt<PT[0]) or np.any(eta>ETA[-1]):
                        raise ValueError("Lepton outside histogram acceptance")
                    clipped=np.minimum(pt,np.nextafter(PT[-1],0))
                    coord=(mass,clipped,eta)
                    hh=np.histogramdd(coord,bins=(MLL,PT,ETA),weights=w)[0]
                    vv=np.histogramdd(coord,bins=(MLL,PT,ETA),weights=w2)[0]
                    nn=np.histogramdd(coord,bins=(MLL,PT,ETA))[0]
                    np.testing.assert_allclose(hh.sum(),w.sum(),rtol=1e-12)
                    assert int(nn.sum())==len(w)
                    h[ci,ki,li]+=hh; v[ci,ki,li]+=vv; counts[ci,ki,li]+=nn.astype(np.int64)
                    features=(pt,eta,pt>=150,pt>=400,eta>=1.566,(pt>=150)&(eta>=1.566))
                    for fi,x in enumerate(features):
                        x=np.asarray(x,dtype=float)
                        for ti,weight in enumerate((w,w2,w*x,w2*x,w2*x*x)):
                            moments[ci,ki,li,:,fi,ti]+=np.bincount(bins,weights=weight,minlength=len(MLL)-1)
        sources.append(dict(file=path.name,bytes=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns,
                            selected=int(sel.sum()),pt1_overflow=int((d["l1_pt"]>=2000).sum()),
                            pt2_overflow=int((d["l2_pt"]>=2000).sum())))
        print(f"{path.name}: {sel.sum():,} OS pairs with >=1 jet",flush=True)
    cache.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(cache,hist=h,var=v,counts=counts,moments=moments,
                        mll_edges=MLL,pt_edges=PT,eta_edges=ETA)
    cache.with_suffix(".json").write_text(json.dumps(dict(channels=CHANNELS,categories=CATS,
        features=FEATURES,moment_terms=TERMS,weight="stored nominal weight; DY corrections and lepton SF on; no charge-flip weight",
        selections=dict(base="hasPair, isSS==0, mll>=60",onejet="nJet==1",
            ge2jet="nJet>=2 (no additional passResolved/mlljj cut)",
            SRtopology="nJet>=2, passResolved>0, mlljj>800 (mll cut specified by region)"),
        overflow="pT>=2000 folded into final display bin; raw moments use unclipped pT",
        source_directory=str(dumps.resolve()),source_path_is_provenance_only=True,samples=sources),indent=2)+"\n")
    return h,v,counts,moments


def norm(h,v):
    total=h.sum()
    if total<=0: raise ValueError("Empty category")
    p=h/total
    diag=v/total**2-2*h*v/total**3+h*h*v.sum()/total**4
    return p,np.maximum(diag,0)


def compare(source,sourcevar,target,targetvar):
    a,va=norm(source,sourcevar); b,vb=norm(target,targetvar)
    ratio=np.full(a.shape,np.nan); err=np.full(a.shape,np.nan); ok=a>0
    ratio[ok]=b[ok]/a[ok]
    err[ok]=np.sqrt(vb[ok]/a[ok]**2+b[ok]**2*va[ok]/a[ok]**4)
    return ratio,err,float(.5*np.abs(a-b).sum())


def estimate(row):
    sw,sw2,swx,sw2x,sw2x2=row
    mean=swx/sw
    variance=max(0.,(sw2x2-2*mean*sw2x+mean*mean*sw2)/sw**2)
    return dict(value=float(mean),error=float(np.sqrt(variance)))


def draw_1d(ROOT,dest,ch,region,h,v):
    canvas=ROOT.TCanvas("leptons","",1250,1050)
    keep=[]
    names=("1 jet", "#geq2 jets (nJet only)", "#geq2 jets, resolved, m_{lljj}>800")
    colors=(ROOT.kBlack,ROOT.kAzure+2,ROOT.kRed+1)
    for panel,(leg,var) in enumerate(((0,"pt"),(0,"eta"),(1,"pt"),(1,"eta"))):
        col=panel%2; row=panel//2
        x0,x1=.01+.49*col,.50+.49*col
        y0,y1=(.48,.92) if row==0 else (.015,.455)
        canvas.cd()
        parent=ROOT.TPad(f"outer{panel}","",x0,y0,x1,y1); parent.Draw(); parent.cd(); keep.append(parent)
        top=ROOT.TPad(f"top{panel}","",0,.32,1,1); top.SetBottomMargin(.025); top.SetTopMargin(.14); top.SetLeftMargin(.14)
        bot=ROOT.TPad(f"bot{panel}","",0,0,1,.32); bot.SetTopMargin(.025); bot.SetBottomMargin(.32); bot.SetLeftMargin(.14)
        if var=="pt": top.SetLogx(); top.SetLogy(); bot.SetLogx()
        bot.SetLogy(); top.Draw(); bot.Draw(); keep += [top,bot]
        edges=PT if var=="pt" else ETA
        hs=h[:,leg].sum(axis=2 if var=="pt" else 1)
        vs=v[:,leg].sum(axis=2 if var=="pt" else 1)
        top.cd()
        legend=ROOT.TLegend(.44,.66 if var=="pt" else .58,.9,.84)
        legend.SetBorderSize(0); legend.SetTextSize(.033 if var=="pt" else .037)
        normalized=[norm(hh,vv) for hh,vv in zip(hs,vs)]
        ymax=max(a.max() for a,b in normalized)*(50 if var=="pt" else 1.7)
        for ki,(a,b) in enumerate(normalized):
            hh=ROOT.TH1D(f"h{panel}_{ki}",";;fraction / bin",len(edges)-1,edges)
            for i in range(len(a)): hh.SetBinContent(i+1,a[i]); hh.SetBinError(i+1,np.sqrt(b[i]))
            hh.SetLineColor(colors[ki]); hh.SetMarkerColor(colors[ki]); hh.SetLineWidth(2)
            hh.GetXaxis().SetLabelSize(0); hh.GetYaxis().SetTitleSize(.055); hh.GetYaxis().SetLabelSize(.045); hh.GetYaxis().SetTitleOffset(1.05)
            hh.SetMinimum(1e-5 if var=="pt" else 0); hh.SetMaximum(ymax)
            hh.Draw("hist e"+(" same" if ki else "")); legend.AddEntry(hh,names[ki],"l"); keep.append(hh)
        legend.Draw(); keep.append(legend)
        label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.048)
        variable="p_{T}" if var=="pt" else ("|#eta_{SC}|" if ch=="EE" else "|#eta|")
        label.DrawLatex(.14,.92,f"{'Leading' if leg==0 else 'Subleading'} lepton {variable}"); keep.append(label)
        bot.cd()
        xtitle=f"{variable}"+(" [GeV]" if var=="pt" else "")
        frame=ROOT.TH1D(f"rframe{panel}",f";{xtitle};target / 1j",len(edges)-1,edges)
        ratios=[compare(hs[0],vs[0],hs[ki],vs[ki]) for ki in (1,2)]
        rmax=max(np.max(r[np.isfinite(r)]) for r,e,tv in ratios)
        rmin=min(np.min(r[np.isfinite(r)&(r>0)]) for r,e,tv in ratios)
        ymax_ratio=next((x for x in (2,5,10,20,50,100,200,500) if x>rmax*1.1),rmax*1.2)
        ymin_ratio=min(.5,max((x for x in (.005,.01,.02,.05,.1,.2,.5) if x<rmin/1.1),default=rmin/1.2))
        frame.SetMinimum(ymin_ratio); frame.SetMaximum(ymax_ratio)
        frame.GetYaxis().SetNdivisions(505); frame.GetYaxis().SetTitleSize(.10); frame.GetYaxis().SetTitleOffset(.6); frame.GetYaxis().SetLabelSize(.085)
        frame.GetXaxis().SetTitleSize(.12); frame.GetXaxis().SetLabelSize(.10); frame.Draw("axis"); keep.append(frame)
        for ki,(ratio,err,_) in zip((1,2),ratios):
            g=ROOT.TGraphErrors()
            for i in np.flatnonzero(np.isfinite(ratio)&(ratio>0)):
                j=g.GetN(); g.SetPoint(j,.5*(edges[i]+edges[i+1]),ratio[i]); g.SetPointError(j,.5*(edges[i+1]-edges[i]),err[i])
            g.SetLineColor(colors[ki]); g.SetMarkerColor(colors[ki]); g.SetMarkerStyle(20); g.SetMarkerSize(.5); g.Draw("P SAME"); keep.append(g)
        line=ROOT.TLine(edges[0],1,edges[-1],1); line.SetLineStyle(2); line.Draw(); keep.append(line)
    canvas.cd(); label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.026)
    lo,hi=REGIONS[region]
    label.DrawLatex(.06,.975,f"{ch} DY OS MC; nominal DY corrections; {lo:g} #leq m_{{ll}} < {hi:g} GeV")
    label.SetTextSize(.020); label.DrawLatex(.06,.94,"Unit area per category; no charge-flip weights; last p_{T} bin includes #geq2000 GeV")
    for ext in ("png","pdf"): canvas.SaveAs(str(dest/f"lepton_shapes_{ch}.{ext}"))
    canvas.Close()


def draw_maps(ROOT,dest,ch,region,h,v):
    canvas=ROOT.TCanvas("maps","",1300,1050); canvas.Divide(2,2)
    keep=[]
    ROOT.gStyle.SetPaintTextFormat(".2f")
    for panel,(leg,ki) in enumerate(((0,1),(0,2),(1,1),(1,2))):
        pad=canvas.cd(panel+1); pad.SetLogx(); pad.SetLogz(); pad.SetRightMargin(.16); pad.SetTopMargin(.16); pad.SetBottomMargin(.12)
        ratio,err,tv=compare(h[0,leg],v[0,leg],h[ki,leg],v[ki,leg])
        neffs=[np.divide(h[k,leg]**2,v[k,leg],out=np.zeros_like(h[k,leg]),where=v[k,leg]>0) for k in (0,ki)]
        good=np.isfinite(ratio)&(neffs[0]>=20)&(neffs[1]>=20)&(ratio>0)
        plot=ROOT.TH2D(f"map{panel}",";lepton p_{T} [GeV];"+("|#eta_{SC}|" if ch=="EE" else "|#eta|")+";normalized target / 1 jet",
                       len(PT)-1,PT,len(ETA)-1,ETA)
        text=plot.Clone(f"maptext{panel}")
        for i,j in zip(*np.where(good)):
            plot.SetBinContent(int(i+1),int(j+1),float(np.clip(ratio[i,j],.250001,3.99999)))
            text.SetBinContent(int(i+1),int(j+1),float(ratio[i,j]))
        plot.SetMinimum(.25); plot.SetMaximum(4); plot.GetZaxis().SetTitleOffset(1.1); plot.Draw("COLZ")
        text.SetMarkerSize(.8); text.Draw("TEXT SAME")
        label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.035)
        label.DrawLatex(.10,.955,f"{ch} OS {'leading' if leg==0 else 'subleading'}; {CATS[ki]} / 1j; {region}")
        label.SetTextSize(.027); label.DrawLatex(.10,.902,f"DY corrected; unit area; TV={tv:.3f}; blank: N_{{eff}}<20")
        keep += [plot,text,label]
    for ext in ("png","pdf"): canvas.SaveAs(str(dest/f"pt_eta_ratios_{ch}.{ext}"))
    canvas.Close()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dumps",type=Path)
    ap.add_argument("--cache",type=Path,default=BASE/"data/jetbin_lepton_histograms.npz")
    ap.add_argument("--out-dir",type=Path,default=BASE/"AN_rawcharge/10_1jet_2jet_os_leptons")
    a=ap.parse_args()
    if a.dumps: hist,var,counts,moments=build(a.dumps,a.cache)
    else:
        if not a.cache.exists(): ap.error("Supply --dumps once to build the local cache")
        with np.load(a.cache) as z:
            for key,ref in (("mll_edges",MLL),("pt_edges",PT),("eta_edges",ETA)):
                np.testing.assert_array_equal(z[key],ref)
            hist,var,counts,moments=z["hist"],z["var"],z["counts"],z["moments"]
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary={}
    for ci,ch in enumerate(CHANNELS):
        for region,(lo,hi) in REGIONS.items():
            sel=(MLL[:-1]>=lo)&(MLL[1:]<=hi)
            h=hist[ci][:,:,sel].sum(axis=2); v=var[ci][:,:,sel].sum(axis=2)
            n=counts[ci][:,:,sel].sum(axis=2); mom=moments[ci][:,:,sel].sum(axis=2)
            dest=a.out_dir/region; dest.mkdir(parents=True,exist_ok=True)
            draw_1d(ROOT,dest,ch,region,h,v); draw_maps(ROOT,dest,ch,region,h,v)
            record={}
            for ki,cat in enumerate(CATS):
                record[cat]=dict(yield_nominal=float(h[ki,0].sum()),mc_entries=int(n[ki,0].sum()))
                for leg in range(2):
                    record[cat][f"l{leg+1}"]={f:estimate(mom[ki,leg,fi]) for fi,f in enumerate(FEATURES)}
                    if ki:
                        ratio,error,tv=compare(h[0,leg],v[0,leg],h[ki,leg],v[ki,leg])
                        record[cat][f"l{leg+1}"]["joint_pt_eta_TV"]=tv
                        record[cat][f"l{leg+1}"]["pt_TV"]=compare(h[0,leg].sum(axis=1),v[0,leg].sum(axis=1),h[ki,leg].sum(axis=1),v[ki,leg].sum(axis=1))[2]
                        record[cat][f"l{leg+1}"]["eta_TV"]=compare(h[0,leg].sum(axis=0),v[0,leg].sum(axis=0),h[ki,leg].sum(axis=0),v[ki,leg].sum(axis=0))[2]
                        np.savez_compressed(dest/f"pt_eta_ratio_{ch}_l{leg+1}_{cat}.npz",ratio=ratio,error=error,
                            source=h[0,leg],source_var=v[0,leg],target=h[ki,leg],target_var=v[ki,leg],pt_edges=PT,eta_edges=ETA)
            summary[f"{ch}/{region}"]=record
    (a.out_dir/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
    lines=["# DY OS: lepton pT/eta in 1 jet vs >=2 jets", "",
           "Nominal DY corrections and lepton SF are included. No charge-flip weight; no collision data.",
           "1j: nJet==1; ge2j: nJet>=2 only; SRtopology: nJet>=2, passResolved, mlljj>800.",
           "Every category is normalized to unit area separately inside each mll region. No mll reweighting.",
           "Errors are weighted MC statistics including normalization. Moments use raw (unclipped) lepton pT.",
           "EE uses |eta_SC|; MM uses the same stored field (=eta for muons). The >=1.566 fraction is an electron endcap diagnostic.","",
           "| channel/mll region | category | mean pT1 | mean pT2 | mean abs eta1 | mean abs eta2 | eta1>=1.566 [%] | eta2>=1.566 [%] |", "|---|---|---|---|---|---|---|---|"]
    for key,r in summary.items():
        for cat,c in r.items():
            vals=[]
            for leg,feat,factor in ((1,"mean_pt",1),(2,"mean_pt",1),(1,"mean_abs_eta",1),(2,"mean_abs_eta",1),
                                    (1,"fraction_abs_eta_ge1p566",100),(2,"fraction_abs_eta_ge1p566",100)):
                x=c[f"l{leg}"][feat]; vals.append(f"{x['value']*factor:.3f} +/- {x['error']*factor:.3f}")
            lines.append(f"| {key} | {cat} | "+" | ".join(vals)+" |")
    lines += ["", "Joint pT/eta TV = 0.5*sum(abs(normalized_target-normalized_1j)), evaluated on the stored binning (0 identical, 1 disjoint).",
              "2D ratio maps show only cells with source and target effective entries >=20; colors are clipped to 0.25-4, numbers are the actual ratios.",
              "ge2j and SRtopology overlap, so their errors must not be treated as independent of each other. Both are disjoint from 1j.",
              "The cache retains fine mll bins for later conditional studies. These comparisons alone do not validate a 1j->2j charge-flip transfer."]
    (a.out_dir/"RESULTS.md").write_text("\n".join(lines)+"\n")
    print("Finished:",a.out_dir,flush=True)


if __name__=="__main__": main()
