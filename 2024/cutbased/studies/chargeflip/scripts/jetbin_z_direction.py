#!/usr/bin/env python3
"""Unit-area reco dilepton eta and rapidity in exclusive 0/1/2 jet DY OS.

The input HT>=40 sample is NOT inclusive DY, especially for the 0-jet bin.
No transfer, angular, or charge-flip weights are applied.
"""
import argparse
import json
from pathlib import Path
import numpy as np

from jetbin_lepton_shapes import BASE, MLL, CHANNELS, REGIONS, estimate, norm

REGIONS=dict(REGIONS,Zpeak=(80,100))
CATS=('0j','1j','2j','ge2j')
MODES=('nominal','noDY')
ZPT=np.array([0,25,50,100,150,200,300,500,np.inf])
EDGES={'eta':np.linspace(-6,6,49),'rapidity':np.linspace(-2.5,2.5,41),
       'abs_eta':np.linspace(0,6,25),'abs_y':np.linspace(0,2.5,21)}
LABELS={'eta':'#eta_{ll}','rapidity':'y_{ll}','abs_eta':'|#eta_{ll}|','abs_y':'|y_{ll}|'}
FEATURES=('mean_abs_eta','mean_abs_y','fraction_abs_eta_lt1','fraction_abs_y_lt1',
          'mean_zpt','mean_mll','fraction_abs_eta_ge6','fraction_y_negative')
COLS=('hasPair','isSS','m_l1l2','nJet','channel','weight','w_dy','pt_l1l2',
      'l1_pt','l2_pt','l1_eta','l2_eta','l1_phi','l2_phi')


def reconstruct(d):
    """Use momentum eta, never supercluster eta. Stable massive rapidity."""
    p1=d['l1_pt'].astype(float); p2=d['l2_pt'].astype(float)
    px=p1*np.cos(d['l1_phi'].astype(float))+p2*np.cos(d['l2_phi'].astype(float))
    py=p1*np.sin(d['l1_phi'].astype(float))+p2*np.sin(d['l2_phi'].astype(float))
    q=np.hypot(px,py)
    pz=p1*np.sinh(d['l1_eta'].astype(float))+p2*np.sinh(d['l2_eta'].astype(float))
    m=d['m_l1l2'].astype(float)
    y=np.arcsinh(pz/np.hypot(m,q))
    eta=np.full_like(q,np.nan); good=q>0
    eta[good]=np.arcsinh(pz[good]/q[good])
    np.testing.assert_allclose(q,d['pt_l1l2'],rtol=2e-5,atol=.005)
    return q,y,eta


def build(dumps,cache):
    files=sorted(dumps.glob('tree_Skim_HNWR_DYto2L*.npz'))
    if not files: raise ValueError('No DY input')
    # mode, channel, category, mll, qT, observable bin
    shape=(2,2,len(CATS),len(MLL)-1,len(ZPT)-1)
    hist={k:np.zeros(shape+(len(e)-1,)) for k,e in EDGES.items()}
    var={k:np.zeros_like(a) for k,a in hist.items()}
    moments=np.zeros(shape+(len(FEATURES),5)); counts=np.zeros(shape[1:],dtype=np.int64)
    sources=[]
    for path in files:
        with np.load(path) as z:
            use=(z['hasPair']>0)&(z['isSS']==0)&(z['m_l1l2']>=60)
            d={k:z[k][use] for k in COLS}
        if any(not np.all(np.isfinite(x)) for x in d.values()): raise ValueError('Nonfinite inputs')
        if np.any(d['weight']<0) or np.any(d['w_dy']<=0): raise ValueError('Invalid weights')
        q,y,eta=reconstruct(d); good=np.isfinite(eta)
        if np.any(np.abs(y)>2.50001): raise ValueError('Rapidity outside expected lepton acceptance')
        obs=dict(eta=eta,rapidity=y,abs_eta=np.abs(eta),abs_y=np.abs(y))
        feats=(np.abs(eta),np.abs(y),np.where(good,np.abs(eta)<1,np.nan),np.abs(y)<1,
               q,d['m_l1l2'],np.where(good,np.abs(eta)>=6,np.nan),y<0)
        masks=(d['nJet']==0,d['nJet']==1,d['nJet']==2,d['nJet']>=2)
        for ci,chid in enumerate((11,13)):
            for ki,cut in enumerate(masks):
                take=cut&(d['channel']==chid)
                mb=np.searchsorted(MLL,d['m_l1l2'][take],side='right')-1
                zb=np.searchsorted(ZPT,q[take],side='right')-1
                idx=np.ravel_multi_index((mb,zb),shape[3:])
                ncell=int(np.prod(shape[3:])); w=d['weight'][take].astype(float)
                counts[ci,ki]+=np.bincount(idx,minlength=ncell).reshape(shape[3:])
                for wi,ww in enumerate((w,w/d['w_dy'][take].astype(float))):
                    ww2=ww*ww
                    for key,e in EDGES.items():
                        x=obs[key][take]; ok=np.isfinite(x); nb=len(e)-1
                        bins=np.clip(np.searchsorted(e,x[ok],side='right')-1,0,nb-1)
                        for dest,weight in ((hist,ww),(var,ww2)):
                            dest[key][wi,ci,ki]+=np.bincount(idx[ok]*nb+bins,weights=weight[ok],
                                minlength=ncell*nb).reshape(shape[3:]+(nb,))
                    for fi,x in enumerate(feats):
                        x=np.asarray(x[take],dtype=float); ok=np.isfinite(x)
                        for ti,weight in enumerate((ww,ww2,ww*x,ww2*x,ww2*x*x)):
                            moments[wi,ci,ki,...,fi,ti]+=np.bincount(idx[ok],weights=weight[ok],minlength=ncell).reshape(shape[3:])
        sources.append(dict(file=path.name,bytes=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns,
            selected=int(use.sum()),zero_qt=int((~good).sum()),eta_overflow=int((np.abs(eta)>=6).sum())))
        print(path.name,'selected',int(use.sum()),'0j',int(masks[0].sum()),flush=True)
    for key,fi in (('eta',0),('abs_eta',0),('rapidity',1),('abs_y',1)):
        np.testing.assert_allclose(hist[key].sum(axis=-1),moments[...,fi,0],rtol=1e-12)
        np.testing.assert_allclose(var[key].sum(axis=-1),moments[...,fi,1],rtol=1e-12)
    cache.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(cache,**{f'h_{k}':x for k,x in hist.items()},**{f'v_{k}':x for k,x in var.items()},
        moments=moments,counts=counts,mll_edges=MLL,zpt_edges=ZPT,**{f'edges_{k}':x for k,x in EDGES.items()})
    cache.with_suffix('.json').write_text(json.dumps(dict(samples=sources,channels=CHANNELS,categories=CATS,modes=MODES,
        features=FEATURES,source_directory=str(dumps.resolve()),source_path_is_provenance_only=True,
        selections='hasPair, isSS==0, mll>=60. No passResolved or mlljj cut. Exclusive 0/1/2 jets; ge2j supplementary.',
        reconstruction='pz=sum pt*sinh(momentum eta); q=hypot(sum px,sum py); eta=asinh(pz/q); y=asinh(pz/hypot(mll,q))',
        zero_qt='q==0 excluded from eta only, not from rapidity; record counts above',
        weights='nominal=weight; noDY=weight/w_dy; no transfer or charge flip',
        caveat='Only generator HT>=40 samples; selected reco leptons. 0j is not inclusive generator DY.',
        overflow='|eta|>=6 folded to outer display bins; raw means untruncated'),indent=2)+'\n')
    return hist,var,moments,counts


def draw(ROOT,dest,ch,mode,region,slice_name,h,v,subtitle=None):
    canvas=ROOT.TCanvas('z_direction','',1250,1000); keep=[]
    colors=(ROOT.kBlack,ROOT.kAzure+2,ROOT.kRed+1)
    for panel,key in enumerate(EDGES):
        col,row=panel%2,panel//2; y0,y1=(.49,.90) if row==0 else (.02,.45)
        canvas.cd(); outer=ROOT.TPad(f'outer{panel}','',.01+.49*col,y0,.50+.49*col,y1); outer.Draw(); outer.cd(); keep.append(outer)
        top=ROOT.TPad(f'top{panel}','',0,.30,1,1); bot=ROOT.TPad(f'bot{panel}','',0,0,1,.30)
        top.SetLeftMargin(.14); top.SetBottomMargin(.02); top.SetTopMargin(.23)
        bot.SetLeftMargin(.14); bot.SetBottomMargin(.32); bot.SetTopMargin(.025)
        top.Draw(); bot.Draw(); keep.extend((top,bot)); top.cd()
        e=EDGES[key]; shape=[norm(h[key][k],v[key][k]) for k in range(3)]
        legend=ROOT.TLegend(.54,.78,.91,.99); legend.SetBorderSize(0); legend.SetTextSize(.045)
        ymax=max(float((x+np.sqrt(c)).max()) for x,c in shape)*1.15
        ymin=min(0.,min(float(x.min()) for x,c in shape)*1.15)
        for k,(x,cov) in enumerate(shape):
            hh=ROOT.TH1D(f'h{panel}_{k}',';;fraction / bin',len(e)-1,e)
            for i,val in enumerate(x): hh.SetBinContent(i+1,float(val)); hh.SetBinError(i+1,float(np.sqrt(cov[i])))
            hh.SetLineColor(colors[k]); hh.SetMarkerColor(colors[k]); hh.SetLineWidth(2)
            hh.GetXaxis().SetLabelSize(0); hh.GetYaxis().SetTitleSize(.055); hh.GetYaxis().SetLabelSize(.045)
            hh.SetMaximum(ymax); hh.SetMinimum(ymin); hh.Draw('hist e'+(' same' if k else ''))
            legend.AddEntry(hh,f'exactly {k} jet'+('s' if k!=1 else ''),'l'); keep.append(hh)
        legend.Draw(); keep.append(legend); bot.cd()
        frame=ROOT.TH1D(f'r{panel}',f';{LABELS[key]};Njet / 1jet',len(e)-1,e)
        frame.SetMinimum(0); frame.SetMaximum(3)
        frame.GetYaxis().SetNdivisions(505); frame.GetYaxis().SetTitleSize(.10); frame.GetYaxis().SetTitleOffset(.6); frame.GetYaxis().SetLabelSize(.085)
        frame.GetXaxis().SetTitleSize(.12); frame.GetXaxis().SetLabelSize(.10)
        ratios=[]
        for k in (0,2):
            x,c=shape[k]; b,bc=shape[1]
            nn=[np.divide(h[key][j]**2,v[key][j],out=np.zeros_like(h[key][j]),where=v[key][j]>0) for j in (1,k)]
            ok=(b>0)&(nn[0]>=20)&(nn[1]>=20)
            ratio=np.full_like(x,np.nan); error=np.full_like(x,np.nan)
            ratio[ok]=x[ok]/b[ok]; error[ok]=np.sqrt(c[ok]/b[ok]**2+x[ok]**2*bc[ok]/b[ok]**4)
            ratios.append((k,ratio,error,ok))
        maxratio=max((float(r[ok].max()) for k,r,err,ok in ratios if ok.any()),default=2.)
        frame.SetMaximum(max(2.,maxratio*1.15)); frame.Draw('axis'); keep.append(frame)
        for k,ratio,error,ok in ratios:
            g=ROOT.TGraphErrors()
            for i in np.flatnonzero(ok):
                j=g.GetN(); g.SetPoint(j,float((e[i]+e[i+1])/2),float(ratio[i])); g.SetPointError(j,float((e[i+1]-e[i])/2),float(error[i]))
            g.SetLineColor(colors[k]); g.SetMarkerColor(colors[k]); g.SetMarkerStyle(20); g.SetMarkerSize(.4); g.Draw('P SAME'); keep.append(g)
        line=ROOT.TLine(e[0],1,e[-1],1); line.SetLineStyle(2); line.Draw(); keep.append(line)
    canvas.cd(); label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.024)
    lo,hi=REGIONS[region]
    label.DrawLatex(.04,.977,f'{ch} DY OS; {mode}; {lo:g}#leqm_{{ll}}<{hi:g} GeV; {slice_name}; unit area')
    label.SetTextSize(.020); label.DrawLatex(.04,.94,subtitle or 'HT#geq40 inputs only; selected leptons; NO SR topology cut; eta tails folded; ratio N_{eff}#geq20')
    for ext in ('png','pdf'): canvas.SaveAs(str(dest/f'z_direction_{ch}.{ext}'))
    canvas.Close()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dumps',type=Path)
    ap.add_argument('--cache',type=Path,default=BASE/'data/jetbin_z_direction.npz')
    ap.add_argument('--out-dir',type=Path,default=BASE/'AN_rawcharge/14_jetbin_z_direction')
    a=ap.parse_args()
    if a.dumps: h,v,mom,counts=build(a.dumps,a.cache)
    else:
        with np.load(a.cache) as z:
            for key,e in [('mll_edges',MLL),('zpt_edges',ZPT)]+[(f'edges_{k}',e) for k,e in EDGES.items()]: np.testing.assert_array_equal(z[key],e)
            h={k:z[f'h_{k}'] for k in EDGES}; v={k:z[f'v_{k}'] for k in EDGES}; mom=z['moments']; counts=z['counts']
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary={}
    # Primary no-qT-cut plots, plus fixed-qT cross-checks for geometry vs production.
    slices={'all_zpt':(0,np.inf),'zpt_50to100':(50,100),'zpt_100to150':(100,150)}
    for wi,mode in enumerate(MODES):
        for ci,ch in enumerate(CHANNELS):
            for region,(lo,hi) in REGIONS.items():
                ms=(MLL[:-1]>=lo)&(MLL[1:]<=hi)
                for slice_name,(ql,qh) in slices.items():
                    zs=(ZPT[:-1]>=ql)&(ZPT[1:]<=qh)
                    hh={k:x[wi,ci][:,ms][:,:,zs].sum(axis=(1,2)) for k,x in h.items()}
                    vv={k:x[wi,ci][:,ms][:,:,zs].sum(axis=(1,2)) for k,x in v.items()}
                    mm=mom[wi,ci][:,ms][:,:,zs].sum(axis=(1,2)); nn=counts[ci][:,ms][:,:,zs].sum(axis=(1,2))
                    if any(x.sum()<=0 for x in hh['rapidity'][:3]): continue
                    dest=a.out_dir/mode/region/slice_name; dest.mkdir(parents=True,exist_ok=True)
                    draw(ROOT,dest,ch,mode,region,slice_name,hh,vv)
                    rec={}
                    for ki,cat in enumerate(CATS):
                        rec[cat]=dict(mc_entries=int(nn[ki]),sumw=float(mm[ki,1,0]),neff=float(mm[ki,1,0]**2/mm[ki,1,1]),
                            eta_valid_sumw=float(mm[ki,0,0]),**{f:estimate(mm[ki,fi]) for fi,f in enumerate(FEATURES)})
                    summary[f'{mode}/{ch}/{region}/{slice_name}']=rec
                    np.savez_compressed(dest/f'distributions_{ch}.npz',**{f'h_{k}':x for k,x in hh.items()},
                        **{f'v_{k}':x for k,x in vv.items()},**{f'edges_{k}':e for k,e in EDGES.items()})
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    lines=['# Z direction by reconstructed jet multiplicity','',
        'DY OS MC with hasPair and mll>=60. EXACTLY 0/1/2 jets in plots; ge2j supplementary in numeric files.',
        'No passResolved/mlljj cut; no transfer, angular or charge-flip weights. Each category has unit area.',
        'nominal = stored weight. noDY = weight/w_dy; other normalization and lepton SF retained.',
        'eta is reco dilepton momentum pseudorapidity, NOT lepton eta or supercluster eta. y is massive dilepton rapidity.',
        'HT>=40 DY samples only: especially 0j is not an inclusive DY prediction. Lepton trigger/pT/eta selections remain.',
        'eta overflows at |eta|>=6 are folded into edge bins, but raw moments are unclipped. qT==0 excluded from eta only.',
        'Weighted MC statistical errors include normalization; no systematic uncertainties.',
        '', '| mode/channel/mll/qT | category | mean abs eta | mean abs y | fraction abs eta<1 [%] | fraction abs y<1 [%] | mean qT [GeV] |',
        '|---|---|---|---|---|---|---|']
    for key,r in summary.items():
        if not key.endswith('/all_zpt'): continue
        for cat,c in r.items():
            vals=[]
            for feat,scale in [('mean_abs_eta',1),('mean_abs_y',1),('fraction_abs_eta_lt1',100),('fraction_abs_y_lt1',100),('mean_zpt',1)]:
                q=c[feat]; vals.append(f"{scale*q['value']:.4f} +/- {scale*q['error']:.4f}")
            lines.append(f'| {key} | {cat} | '+' | '.join(vals)+' |')
    (a.out_dir/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('Finished:',a.out_dir)


if __name__=='__main__': main()
