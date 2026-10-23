#!/usr/bin/env python3
"""High-mass DY OS conditional lepton asymmetry/angle and binning diagnosis.

No new angular weights: only mll/reco-Zpt transfer weights are applied.
The random split is identical to study 12.
"""
import argparse
import json
from pathlib import Path
import numpy as np

from jetbin_lepton_shapes import BASE, PT, CHANNELS, CATS, estimate
from jetbin_lepton_zpt_reweight import SEED, ZPT as OLD_ZPT, make_groups, aggregate, independent_comparison, independent_feature

MASS=np.r_[np.arange(400,701,25),np.arange(750,1001,50),np.inf].astype(float)
ZPT=np.unique(np.r_[np.arange(0,201,10),np.arange(225,501,25),OLD_ZPT])
OLD_MASS=np.array([400,500,700,1000,np.inf])
EDGES={'asymmetry':np.linspace(0,1,21),'dphi':np.linspace(0,np.pi,21),'pt1':PT,'pt2':PT}
LABELS={'asymmetry':'A_{p_{T}}=(p_{T1}-p_{T2})/(p_{T1}+p_{T2})',
        'dphi':'|#Delta#phi_{ll}| [rad]','pt1':'leading p_{T} [GeV]','pt2':'subleading p_{T} [GeV]'}
FEATURES=('asymmetry','dphi','pt1','pt2','mll','zpt')
COLS=('hasPair','isSS','m_l1l2','nJet','channel','passResolved','m_lljj','weight',
      'pt_l1l2','l1_pt','l2_pt','l1_phi','l2_phi')


def build(dumps,cache):
    files=sorted(dumps.glob('tree_Skim_HNWR_DYto2L*.npz'))
    if not files: raise ValueError('No DY files')
    shape=(2,3,2,len(MASS)-1,len(ZPT)-1)
    h={k:np.zeros(shape+(len(e)-1,)) for k,e in EDGES.items()}
    v={k:np.zeros_like(a) for k,a in h.items()}
    mom=np.zeros(shape+(len(FEATURES),5)); sources=[]
    for fi,path in enumerate(files):
        with np.load(path) as z:
            take=(z['hasPair']>0)&(z['isSS']==0)&(z['m_l1l2']>=400)&(z['nJet']>=1)
            d={k:z[k][take] for k in COLS}
            fold=np.random.default_rng(SEED+fi).integers(0,2,size=len(take),dtype=np.int8)[take]
        if any(not np.all(np.isfinite(x)) for x in d.values()): raise ValueError('Nonfinite inputs')
        if np.any(d['weight']<0): raise ValueError('Negative weights')
        p1=d['l1_pt'].astype(float); p2=d['l2_pt'].astype(float)
        if np.any(p1<p2) or np.any(p2<53): raise ValueError('Lepton ordering/acceptance')
        delta=d['l1_phi'].astype(float)-d['l2_phi'].astype(float)
        obs=dict(asymmetry=(p1-p2)/(p1+p2),dphi=np.abs(np.arctan2(np.sin(delta),np.cos(delta))),
                 pt1=p1,pt2=p2,mll=d['m_l1l2'].astype(float),zpt=d['pt_l1l2'].astype(float))
        reco=np.hypot(p1*np.cos(d['l1_phi'])+p2*np.cos(d['l2_phi']),p1*np.sin(d['l1_phi'])+p2*np.sin(d['l2_phi']))
        np.testing.assert_allclose(reco,obs['zpt'],rtol=2e-5,atol=.005)
        masks=(d['nJet']==1,d['nJet']>=2,(d['nJet']>=2)&(d['passResolved']>0)&(d['m_lljj']>800))
        for ci,ch in enumerate((11,13)):
            for ki,cut in enumerate(masks):
                keep=cut&(d['channel']==ch)
                mb=np.searchsorted(MASS,obs['mll'][keep],side='right')-1
                zb=np.searchsorted(ZPT,obs['zpt'][keep],side='right')-1
                idx=np.ravel_multi_index((fold[keep],mb,zb),shape[2:])
                w=d['weight'][keep].astype(float); w2=w*w
                for oi,key in enumerate(FEATURES):
                    x=obs[key][keep]
                    for ti,ww in enumerate((w,w2,w*x,w2*x,w2*x*x)):
                        mom[ci,ki,...,oi,ti]+=np.bincount(idx,weights=ww,minlength=int(np.prod(shape[2:]))).reshape(shape[2:])
                    if key not in EDGES: continue
                    edges=EDGES[key]; n=len(edges)-1
                    bins=np.clip(np.searchsorted(edges,x,side='right')-1,0,n-1)
                    for dest,ww in ((h,w),(v,w2)):
                        dest[key][ci,ki]+=np.bincount(idx*n+bins,weights=ww,
                            minlength=int(np.prod(shape[2:]))*n).reshape(shape[2:]+(n,))
        sources.append(dict(file=path.name,bytes=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns,selected=int(take.sum())))
        print(path.name,int(take.sum()),flush=True)
    for key in EDGES:
        np.testing.assert_allclose(h[key].sum(axis=-1),mom[...,0,0],rtol=1e-12)
        np.testing.assert_allclose(v[key].sum(axis=-1),mom[...,0,1],rtol=1e-12)
    cache.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(cache,**{f'h_{k}':a for k,a in h.items()},**{f'v_{k}':a for k,a in v.items()},
                        moments=mom,mll_edges=MASS,zpt_edges=ZPT,**{f'edges_{k}':a for k,a in EDGES.items()})
    cache.with_suffix('.json').write_text(json.dumps(dict(samples=sources,source_directory=str(dumps.resolve()),
        source_path_is_provenance_only=True,seed=SEED,split='same original-row split as study 12',
        axes='channel,category,fold,mll,zpt,observable',features=FEATURES,
        definition='hasPair, OS, mll>=400, nominal DY; 1j / ge2j / SRtopology; no charge flip'),indent=2)+'\n')
    return h,v,mom


def coarse_groups(train,minimum):
    mi=np.searchsorted(OLD_MASS,MASS[:-1],side='right')-1
    zi=np.searchsorted(OLD_ZPT,ZPT[:-1],side='right')-1
    nz=len(OLD_ZPT)-1
    cell=(mi[:,None]*nz+zi[None,:]).ravel()
    mapping=[np.flatnonzero(cell==i) for i in range((len(OLD_MASS)-1)*nz)]
    coarse=[aggregate(x,mapping).reshape(len(OLD_MASS)-1,nz) for x in train]
    groups=make_groups(*coarse,'mll_zpt',minimum)
    return [np.concatenate([mapping[i] for i in g]) for g in groups]


def draw(ROOT,dest,title,panels,curves):
    canvas=ROOT.TCanvas('conditional','',1250,1050); keep=[]
    colors={'target':ROOT.kBlack,'before':ROOT.kAzure+2,'coarse':ROOT.kOrange+7,'fine':ROOT.kRed+1}
    names={'target':'2j target','before':'1j before transfer','coarse':'1j coarse (m_{ll}, p_{T}^{ll})','fine':'1j fine (m_{ll}, p_{T}^{ll})'}
    for panel,key in enumerate(EDGES):
        col,row=panel%2,panel//2; y0,y1=(.49,.92) if row==0 else (.02,.45)
        canvas.cd(); outer=ROOT.TPad(f'outer{panel}','',.01+.49*col,y0,.50+.49*col,y1)
        outer.Draw(); outer.cd(); keep.append(outer)
        top=ROOT.TPad(f'top{panel}','',0,.30,1,1); bot=ROOT.TPad(f'bot{panel}','',0,0,1,.30)
        top.SetLeftMargin(.14); top.SetBottomMargin(.025); top.SetTopMargin(.26)
        bot.SetLeftMargin(.14); bot.SetBottomMargin(.32); bot.SetTopMargin(.03)
        if key.startswith('pt'): top.SetLogx(); top.SetLogy(); bot.SetLogx(); bot.SetLogy()
        top.Draw(); bot.Draw(); keep.extend((top,bot)); top.cd()
        edges=EDGES[key]; d=panels[key]; values=d['values']; covs=d['covs']
        legend=ROOT.TLegend(.43,.755,.91,.99); legend.SetBorderSize(0); legend.SetTextSize(.034)
        ymax=max(values[c].max() for c in curves)*(3 if key.startswith('pt') else 1.15)
        for i,c in enumerate(curves):
            hh=ROOT.TH1D(f'h{panel}_{c}',';;fraction / bin',len(edges)-1,edges)
            for j,x in enumerate(values[c]): hh.SetBinContent(j+1,float(x)); hh.SetBinError(j+1,float(np.sqrt(max(covs[c][j,j],0))))
            hh.SetLineColor(colors[c]); hh.SetMarkerColor(colors[c]); hh.SetLineWidth(2)
            if c=='before': hh.SetLineStyle(2)
            hh.GetXaxis().SetLabelSize(0); hh.GetYaxis().SetLabelSize(.045); hh.GetYaxis().SetTitleSize(.055)
            hh.SetMaximum(ymax); hh.SetMinimum(1e-5 if key.startswith('pt') else 0)
            hh.Draw('hist e'+(' same' if i else '')); legend.AddEntry(hh,names[c],'l'); keep.append(hh)
        legend.Draw(); keep.append(legend); bot.cd()
        frame=ROOT.TH1D(f'frame{panel}',f';{LABELS[key]};1j / target',len(edges)-1,edges)
        rr=np.concatenate([d['ratios'][c][np.isfinite(d['ratios'][c])&(d['ratios'][c]>0)&d['ratio_mask']] for c in curves if c!='target'])
        if not len(rr): rr=np.array([1.])
        low=min(.8,rr.min()*.85); high=max(1.2,rr.max()*1.15)
        frame.SetMinimum(max(.05,low) if key.startswith('pt') else max(0,low)); frame.SetMaximum(high)
        frame.GetYaxis().SetNdivisions(505); frame.GetYaxis().SetMoreLogLabels(); frame.GetYaxis().SetNoExponent()
        frame.GetYaxis().SetTitleSize(.10); frame.GetYaxis().SetTitleOffset(.6); frame.GetYaxis().SetLabelSize(.085)
        frame.GetXaxis().SetTitleSize(.11); frame.GetXaxis().SetLabelSize(.10); frame.Draw('axis'); keep.append(frame)
        for c in curves:
            if c=='target': continue
            g=ROOT.TGraphErrors(); r=d['ratios'][c]; error=d['errors'][c]
            for i in np.flatnonzero(np.isfinite(r)&(r>0)&d['ratio_mask']):
                j=g.GetN(); g.SetPoint(j,float((edges[i]+edges[i+1])/2),float(r[i]))
                g.SetPointError(j,float((edges[i+1]-edges[i])/2),float(error[i]))
            g.SetMarkerStyle(20); g.SetMarkerSize(.4); g.SetLineColor(colors[c]); g.SetMarkerColor(colors[c]); g.Draw('P SAME'); keep.append(g)
        line=ROOT.TLine(edges[0],1,edges[-1],1); line.SetLineStyle(2); line.Draw(); keep.append(line)
    canvas.cd(); label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.023)
    label.DrawLatex(.04,.978,title); label.SetTextSize(.020)
    label.DrawLatex(.04,.94,'DY OS; test half; nominal weights; no angular/CF weights; ratios: source/target N_{eff}#geq20')
    for ext in ('png','pdf'): canvas.SaveAs(str(dest.with_suffix('.'+ext)))
    canvas.Close()


def panel_record(results):
    ref=next(iter(results.values()))
    p=dict(values={'target':ref['target'],'before':ref['before']},
           covs={'target':ref['cov_target'],'before':ref['cov_before']},
           ratios={'before':ref['ratios'][0]},errors={'before':ref['errors'][0]},ratio_mask=ref['ratio_mask'])
    for name,d in results.items():
        p['values'][name]=d['after']; p['covs'][name]=d['cov_after']
        p['ratios'][name]=d['ratios'][1]; p['errors'][name]=d['errors'][1]
    return p


def compare_arrays(arrays,f,fv):
    d=independent_comparison(*arrays,f,fv)
    s,sv,t,tv=[x.sum(axis=0) for x in arrays]
    ns=np.divide(s*s,sv,out=np.zeros_like(s),where=sv>0)
    nt=np.divide(t*t,tv,out=np.zeros_like(t),where=tv>0)
    d['ratio_mask']=(ns>=20)&(nt>=20)
    return d


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dumps',type=Path)
    ap.add_argument('--cache',type=Path,default=BASE/'data/jetbin_conditional_angles.npz')
    ap.add_argument('--out-dir',type=Path,default=BASE/'AN_rawcharge/13_conditional_lepton_angles')
    ap.add_argument('--min-train-neff',type=float,default=50)
    a=ap.parse_args()
    if a.dumps: h,v,mom=build(a.dumps,a.cache)
    else:
        with np.load(a.cache) as z:
            for name,e in [('mll_edges',MASS),('zpt_edges',ZPT)]+[(f'edges_{k}',x) for k,x in EDGES.items()]:
                np.testing.assert_array_equal(z[name],e)
            h={k:z[f'h_{k}'] for k in EDGES}; v={k:z[f'v_{k}'] for k in EDGES}; mom=z['moments']
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    a.out_dir.mkdir(parents=True,exist_ok=True); summary={}; boxes={}
    for ci,ch in enumerate(CHANNELS):
        for ki,cat in enumerate(CATS[1:],1):
            dest=a.out_dir/cat; dest.mkdir(exist_ok=True)
            train=[x['pt1'][ci,k,0].sum(axis=-1) for k in (0,ki) for x in (h,v)]
            strategies={'coarse':coarse_groups(train,a.min_train_neff),
                        'fine':make_groups(*train,'mll_zpt',a.min_train_neff)}
            rec={}; panels={key:{} for key in EDGES}
            for mode,groups in strategies.items():
                ts,vs,tt,vt=[aggregate(x,groups) for x in train]
                f=tt/ts; fv=vt/ts**2+tt**2*vs/ts**4
                data={'groups':len(groups),'features':{},'TV':{}}
                ms,mt=[aggregate(mom[ci,k,1],groups) for k in (0,ki)]
                for i,key in enumerate(FEATURES):
                    data['features'][key]=dict(before=estimate(ms[:,i].sum(axis=0)),
                        after=independent_feature(ms[:,i],f,fv),target=estimate(mt[:,i].sum(axis=0)))
                for key in EDGES:
                    arrays=[aggregate(x[key][ci,k,1],groups) for k in (0,ki) for x in (h,v)]
                    d=compare_arrays(arrays,f,fv); panels[key][mode]=d
                    data['TV'][key]=dict(before=d['tv_before'],after=d['tv_after'])
                    np.savez_compressed(dest/f'{ch}_{mode}_{key}.npz',**d,edges=EDGES[key])
                mapping=np.empty(train[0].size,dtype=int)
                for gi,g in enumerate(groups): mapping[g]=gi
                np.savez_compressed(dest/f'{ch}_{mode}_factors.npz',factor=f,factor_var=fv,
                    group_index=mapping.reshape(train[0].shape),mll_edges=MASS,zpt_edges=ZPT)
                rec[mode]=data
            summary[f'{ch}/{cat}']=rec
            draw(ROOT,dest/f'binning_comparison_{ch}',f'{ch}; {cat}; m_{{ll}}#geq400 GeV; independent validation',
                 {k:panel_record(d) for k,d in panels.items()},('target','before','coarse','fine'))
            # Fixed 50x50 GeV boxes, chosen before examining angular outcomes.
            for ml in (400,450,500,550):
                for zl in (50,100,150,200):
                    use=((MASS[:-1,None]>=ml)&(MASS[1:,None]<=ml+50)&(ZPT[None,:-1]>=zl)&(ZPT[None,1:]<=zl+50))
                    rows=[mom[ci,k,1][use].sum(axis=0) for k in (0,ki)]
                    r=dict(mll=[ml,ml+50],zpt=[zl,zl+50],features={},TV={},matched_features={},matched_TV={},
                           neff=[float(x[0,0]**2/x[0,1]) for x in rows])
                    mi=np.flatnonzero((MASS[:-1]>=ml)&(MASS[1:]<=ml+50))
                    zi=np.flatnonzero((ZPT[:-1]>=zl)&(ZPT[1:]<=zl+50))
                    def local(x): return x[mi][:,zi]
                    local_train=[local(x) for x in train]
                    local_groups=make_groups(*local_train,'mll_zpt',20.)
                    ss,sv,tt,tv=[aggregate(x,local_groups) for x in local_train]
                    lf=tt/ss; lfv=tv/ss**2+tt**2*sv/ss**4
                    r['local_train_min_neff']=20; r['local_groups']=len(local_groups)
                    local_mom=[aggregate(local(mom[ci,k,1]),local_groups) for k in (0,ki)]
                    pp={}
                    for i,key in enumerate(FEATURES):
                        es,et=[estimate(x[i]) for x in rows]
                        r['features'][key]=dict(source=es,target=et,
                            difference=float(es['value']-et['value']),error=float(np.hypot(es['error'],et['error'])))
                        ea=independent_feature(local_mom[0][:,i],lf,lfv)
                        r['matched_features'][key]=dict(source=ea,target=et,
                            difference=float(ea['value']-et['value']),error=float(np.hypot(ea['error'],et['error'])))
                    for key in EDGES:
                        arrays=[aggregate(local(x[key][ci,k,1]),local_groups) for k in (0,ki) for x in (h,v)]
                        d=compare_arrays(arrays,lf,lfv)
                        r['TV'][key]=d['tv_before']; pp[key]=panel_record({'fine':d})
                        r['matched_TV'][key]=d['tv_after']
                    name=f'{ch}_mll{ml}_{ml+50}_zpt{zl}_{zl+50}'
                    boxes[f'{ch}/{cat}/{name}']=r
                    draw(ROOT,dest/name,f'{ch}; {cat}; {ml}#leqm_{{ll}}<{ml+50}, {zl}#leqp_{{T}}^{{ll}}<{zl+50} GeV',
                        pp,('target','before','fine'))
            print('Finished',ch,cat,flush=True)
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (a.out_dir/'conditional_boxes.json').write_text(json.dumps(boxes,indent=2,allow_nan=False)+'\n')
    lines=['# Conditional angle and fine-binning check','',
        'DY OS MC, mll>=400, nominal DY corrections, no charge flip. No angular weight is fitted.',
        'Same random fold assignment as study 12: fold 0 trains transfer factors, fold 1 compares shapes.',
        'Coarse reproduces study 12 mll+Zpt matching; fine uses mll 25 GeV steps to 700, 50 to 1000, >=1000 overflow.',
        'Fine Zpt grid subdivides the previous grid with 10 GeV steps below 200 and 25 GeV steps to 500.',
        'Both merge adjacent Zpt bins to train Neff>=50 per population. Thus not every final bin is narrow.',
        'Fixed boxes are 50x50 GeV; show nominal source/target plus finer within-box matching from training half (min Neff=20).',
        'Even after local matching, within-bin and independent-test fluctuations can leave mll/Zpt differences; raw means are saved.',
        'Ratio points require raw source and target bin Neff>=20; all bins enter shapes, means and TV.',
        'Means, including mll/Zpt inside fixed boxes, use raw values; pT overflow is included in last plotted bin.',
        'Statistical errors only. Transfer error propagation is first-order. TV is a descriptive distance, not a significance.',
        '', '| channel/target | binning | observable | before -> after -> target (mean) | TV before -> after |',
        '|---|---|---|---|---|']
    for key,r in summary.items():
        for mode,c in r.items():
            for obs in EDGES:
                means=' -> '.join(f"{c['features'][obs][k]['value']:.4f} +/- {c['features'][obs][k]['error']:.4f}" for k in ('before','after','target'))
                lines.append(f"| {key} | {mode} ({c['groups']} cells) | {obs} | {means} | {c['TV'][obs]['before']:.4f} -> {c['TV'][obs]['after']:.4f} |")
    (a.out_dir/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    lines=['# Fixed-box conditional comparisons','',
        'All differences below are reweighted 1jet minus target, on independent test events.',
        'Within each 50x50 GeV box, transfer uses mll/Zpt only; fine cells merge to training Neff>=20.',
        'Nominal DY corrections remain on. No A_pT, delta-phi or charge-flip weights.',
        'Quoted errors are MC statistics and fitted transfer uncertainties, not systematic errors.',
        'The mean mll and Zpt differences diagnose imperfect within-cell matching / test fluctuations.',
        'Multiple boxes and observables are examined: individual deviations are not global significances.',
        '', '| channel/target | mll / Zpt box [GeV] | delta A_pT | delta dphi [rad] | delta pT2 [GeV] | delta mll [GeV] | delta Zpt [GeV] |',
        '|---|---|---|---|---|---|---|']
    for key,r in boxes.items():
        vals=[]
        for obs in ('asymmetry','dphi','pt2','mll','zpt'):
            x=r['matched_features'][obs]; vals.append(f"{x['difference']:+.4f} +/- {x['error']:.4f}")
        lines.append('| '+ '/'.join(key.split('/')[:2])+f" | {r['mll']} / {r['zpt']} | "+' | '.join(vals)+' |')
    (a.out_dir/'CONDITIONAL_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('Finished:',a.out_dir)


if __name__=='__main__': main()
