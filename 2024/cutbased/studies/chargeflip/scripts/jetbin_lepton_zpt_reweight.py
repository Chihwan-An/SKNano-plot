#!/usr/bin/env python3
"""DY OS 1j -> >=2j using reco dilepton pT, with independent-half validation.

Build once with --dumps; thereafter only the portable cache is required.
Factors are estimated separately per channel, target and displayed mll region.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from jetbin_lepton_shapes import BASE, PT, ETA, CATS, CHANNELS, REGIONS, FEATURES, TERMS, COLS, estimate
from jetbin_lepton_mll_reweight import comparison, normalized, weighted_feature, draw

MASS=np.array([60,80,90,100,120,150,200,300,400,500,700,1000,np.inf])
ZPT=np.array([0,20,40,60,80,100,125,150,175,200,250,300,400,500,700,1000,1500,np.inf])
SEED=20260919


def build(dumps,cache):
    files=sorted(dumps.glob('tree_Skim_HNWR_DYto2L*.npz'))
    if not files: raise ValueError(f'No DY inputs in {dumps}')
    # channel, category, leg, random half, mll, Zpt, lepton pt, abs eta
    shape=(2,3,2,2,len(MASS)-1,len(ZPT)-1,len(PT)-1,len(ETA)-1)
    hist=np.zeros(shape); var=np.zeros(shape); counts=np.zeros(shape,dtype=np.int64)
    moments=np.zeros(shape[:6]+(len(FEATURES),len(TERMS)))
    sources=[]
    bins_shape=shape[3:]
    for file_index,path in enumerate(files):
        with np.load(path) as z:
            use=(z['hasPair']>0)&(z['isSS']==0)&(z['m_l1l2']>=60)&(z['nJet']>=1)
            d={k:z[k][use] for k in COLS+('pt_l1l2',)}
            fold=np.random.default_rng(SEED+file_index).integers(0,2,size=len(use),dtype=np.int8)[use]
        if any(not np.all(np.isfinite(a)) for a in d.values()): raise ValueError('Nonfinite inputs')
        if np.any(d['weight']<0) or np.any(d['pt_l1l2']<0): raise ValueError('Invalid weight or Zpt')
        masks=(d['nJet']==1,d['nJet']>=2,(d['nJet']>=2)&(d['passResolved']>0)&(d['m_lljj']>800))
        for ci,chid in enumerate((11,13)):
            for ki,cut in enumerate(masks):
                take=cut&(d['channel']==chid)
                mb=np.searchsorted(MASS,d['m_l1l2'][take],side='right')-1
                zb=np.searchsorted(ZPT,d['pt_l1l2'][take],side='right')-1
                ff=fold[take]; w=d['weight'][take].astype(float); w2=w*w
                moment_idx=np.ravel_multi_index((ff,mb,zb),bins_shape[:3])
                for li in range(2):
                    pt=d[f'l{li+1}_pt'][take].astype(float); eta=np.abs(d[f'l{li+1}_scEta'][take].astype(float))
                    if np.any(pt<PT[0]) or np.any(eta>ETA[-1]): raise ValueError('Lepton outside acceptance')
                    pb=np.clip(np.searchsorted(PT,pt,side='right')-1,0,len(PT)-2)
                    eb=np.clip(np.searchsorted(ETA,eta,side='right')-1,0,len(ETA)-2)
                    idx=np.ravel_multi_index((ff,mb,zb,pb,eb),bins_shape)
                    for dest,weight in ((hist,w),(var,w2),(counts,None)):
                        add=np.bincount(idx,weights=weight,minlength=int(np.prod(bins_shape))).reshape(bins_shape)
                        dest[ci,ki,li]+=add
                    for fi,x in enumerate((pt,eta,pt>=150,pt>=400,eta>=1.566,(pt>=150)&(eta>=1.566))):
                        x=np.asarray(x,dtype=float)
                        for ti,weight in enumerate((w,w2,w*x,w2*x,w2*x*x)):
                            moments[ci,ki,li,:,:,:,fi,ti]+=np.bincount(moment_idx,weights=weight,
                                minlength=int(np.prod(bins_shape[:3]))).reshape(bins_shape[:3])
        sources.append(dict(file=path.name,bytes=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns,selected=int(use.sum())))
        print(f'{path.name}: {use.sum():,} selected',flush=True)
    np.testing.assert_allclose(hist.sum(axis=(-2,-1)),moments[...,0,0],rtol=1e-12)
    np.testing.assert_allclose(var.sum(axis=(-2,-1)),moments[...,0,1],rtol=1e-12)
    np.testing.assert_array_equal(counts[:,:,0].sum(axis=(-2,-1)),counts[:,:,1].sum(axis=(-2,-1)))
    cache.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(cache,hist=hist,var=var,counts=counts,moments=moments,
                        mll_edges=MASS,zpt_edges=ZPT,pt_edges=PT,eta_edges=ETA)
    cache.with_suffix('.json').write_text(json.dumps(dict(channels=CHANNELS,categories=CATS,
        axes='channel,category,leg,fold,mll,zpt,pt,eta',features=FEATURES,moment_terms=TERMS,
        seed=SEED,split='numpy default_rng(seed+sorted_file_index), random original row assignment; fold0 train, fold1 test',
        zpt='reconstructed dilepton pt_l1l2, not generator Z pT',weight='stored nominal DY corrections and lepton SF; no charge flip',
        selection='hasPair, isSS==0, mll>=60, nJet>=1; categories identical to study 10',
        source_directory=str(dumps.resolve()),source_path_is_provenance_only=True,samples=sources),indent=2)+'\n')
    return hist,var,moments


def neff(h,v):
    return h*h/v if v>0 else 0.


def make_groups(s,vs,t,vt,mode,minimum):
    """Merge adjacent Zpt bins using TRAIN statistics only; never discard yield."""
    nm,nz=s.shape
    rows=[list(range(nm))] if mode=='zpt' else [[i] for i in range(nm)]
    groups=[]
    for row in rows:
        hs=s[row].sum(axis=0); hv=vs[row].sum(axis=0)
        ht=t[row].sum(axis=0); tv=vt[row].sum(axis=0)
        def enough(a,b):
            return min(neff(hs[a:b].sum(),hv[a:b].sum()),neff(ht[a:b].sum(),tv[a:b].sum()))>=minimum
        if not enough(0,nz): raise ValueError('Insufficient mass-bin statistics: use coarser MASS bins')
        ranges=[]; start=0
        if mode=='mll': ranges=[(0,nz)]
        else:
            for end in range(1,nz+1):
                if enough(start,end): ranges.append((start,end)); start=end
            if start<nz:
                if ranges: ranges[-1]=(ranges[-1][0],nz)
                else: ranges=[(0,nz)]
        for start,end in ranges:
            groups.append(np.array([m*nz+z for m in row for z in range(start,end)],dtype=int))
    np.testing.assert_array_equal(np.sort(np.concatenate(groups)),np.arange(nm*nz))
    return groups


def aggregate(a,groups):
    flat=a.reshape((-1,)+a.shape[2:])
    return np.array([flat[g].sum(axis=0) for g in groups])


def independent_comparison(s,vs,t,vt,f,fv):
    """Test histograms independent of training factors; delta-method covariance."""
    pred=(s*f[:,None]).sum(axis=0)
    cp=np.diag((vs*f[:,None]**2).sum(axis=0))+np.einsum('g,gi,gj->ij',fv,s,s)
    before,cb,_=normalized(s.sum(axis=0),np.diag(vs.sum(axis=0)))
    after,ca,_=normalized(pred,cp)
    target,ct,_=normalized(t.sum(axis=0),np.diag(vt.sum(axis=0)))
    ratios=[]; errors=[]; ok=target>0
    for p,c in ((before,cb),(after,ca)):
        r=np.full_like(p,np.nan); e=r.copy(); r[ok]=p[ok]/target[ok]
        e[ok]=np.sqrt(np.maximum(0,np.diag(c)[ok]/target[ok]**2+p[ok]**2*np.diag(ct)[ok]/target[ok]**4))
        ratios.append(r); errors.append(e)
    return dict(before=before,after=after,target=target,cov_before=cb,cov_after=ca,cov_target=ct,
                cov_after_target=np.zeros_like(ct),ratios=np.array(ratios),errors=np.array(errors),
                tv_before=float(.5*np.abs(before-target).sum()),tv_after=float(.5*np.abs(after-target).sum()))


def independent_feature(m,f,fv):
    sw,v,x,vx,vxx=m.T
    n=np.dot(f,sw); mean=np.dot(f,x)/n
    variance=(np.sum(f*f*(vxx-2*mean*vx+mean*mean*v))+np.sum(fv*(x-mean*sw)**2))/n**2
    return dict(value=float(mean),error=float(np.sqrt(max(variance,0))))


def plot_factors(ROOT,dest,ch,cat,region,records):
    canvas=ROOT.TCanvas('zpt_factors','',1050,650); canvas.SetLogy(); canvas.SetBottomMargin(.14)
    rows=records['zpt']; edges=np.array([r['zpt_low'] for r in rows]+[2000.])
    h=ROOT.TH1D('factor',';reco p_{T}(ll) [GeV];N_{2j} / N_{1j}',len(edges)-1,edges)
    for i,r in enumerate(rows): h.SetBinContent(i+1,r['factor']); h.SetBinError(i+1,r['error'])
    h.SetMinimum(min(r['factor'] for r in rows)*.4); h.SetMaximum(max(r['factor'] for r in rows)*8)
    h.SetMarkerStyle(20); h.Draw('E1')
    label=ROOT.TLatex(); label.SetNDC(); label.SetTextFont(42); label.SetTextSize(.035)
    label.DrawLatex(.13,.92,f'{ch} OS; {cat}; {region}; training-half factors')
    label.SetTextSize(.027); label.DrawLatex(.13,.85,'Nominal DY; no charge flip; last displayed bin extends to infinity')
    for ext in ('png','pdf'): canvas.SaveAs(str(dest/f'zpt_factors_{ch}.{ext}'))
    canvas.Close()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dumps',type=Path)
    ap.add_argument('--cache',type=Path,default=BASE/'data/jetbin_lepton_zpt_histograms.npz')
    ap.add_argument('--out-dir',type=Path,default=BASE/'AN_rawcharge/12_1jet_2jet_zpt_reweighted')
    ap.add_argument('--min-train-neff',type=float,default=50.)
    a=ap.parse_args()
    if a.dumps: h,v,mom=build(a.dumps,a.cache)
    else:
        with np.load(a.cache) as z:
            for k,edges in (('mll_edges',MASS),('zpt_edges',ZPT),('pt_edges',PT),('eta_edges',ETA)):
                np.testing.assert_array_equal(z[k],edges)
            h,v,mom=z['hist'],z['var'],z['moments']
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary={}; all_factors={}
    for ci,ch in enumerate(CHANNELS):
        for ki,cat in enumerate(CATS[1:],1):
            for region,(lo,hi) in REGIONS.items():
                select=(MASS[:-1]>=lo)&(MASS[1:]<=hi)
                mass_ids=np.flatnonzero(select)
                # Sum lepton bins for factor estimation; leg 1 and leg 2 carry identical yields.
                train=[x[ci,k,0,0,select].sum(axis=(-2,-1)) for k in (0,ki) for x in (h,v)]
                dest=a.out_dir/cat/region; dest.mkdir(parents=True,exist_ok=True)
                factor_records={}
                for mode in ('mll','zpt','mll_zpt'):
                    groups=make_groups(*train,mode,a.min_train_neff)
                    ts,tv,tt,ttv=[aggregate(x,groups) for x in train]
                    f=tt/ts; fv=ttv/ts**2+tt**2*tv/ts**4
                    records=[]
                    for gi,g in enumerate(groups):
                        mi,zi=np.unravel_index(g,train[0].shape)
                        ml,mh=MASS[mass_ids[mi.min()]],MASS[mass_ids[mi.max()]+1]
                        zl,zh=ZPT[zi.min()],ZPT[zi.max()+1]
                        records.append(dict(mll_low=float(ml),mll_high=float(mh) if np.isfinite(mh) else None,
                            zpt_low=float(zl),zpt_high=float(zh) if np.isfinite(zh) else None,
                            factor=float(f[gi]),error=float(np.sqrt(fv[gi])),source_neff=float(neff(ts[gi],tv[gi])),
                            target_neff=float(neff(tt[gi],ttv[gi]))))
                    factor_records[mode]=records
                    for evaluation in ('same_sample','validation'):
                        rd=dest/mode/evaluation; rd.mkdir(parents=True,exist_ok=True)
                        panels={}; record={}
                        for leg in range(2):
                            inputs=[]; mm=[]
                            for k in (0,ki):
                                for x in (h,v):
                                    hh=x[ci,k,leg].sum(axis=0)[select] if evaluation=='same_sample' else x[ci,k,leg,1,select]
                                    inputs.append(aggregate(hh,groups))
                                m=mom[ci,k,leg].sum(axis=0)[select] if evaluation=='same_sample' else mom[ci,k,leg,1,select]
                                mm.append(aggregate(m,groups))
                            s,sv,t,tvtest=inputs
                            rec={}
                            for obs in ('pt','eta','joint'):
                                arrays=[x.reshape(len(x),-1) if obs=='joint' else x.sum(axis=2 if obs=='pt' else 1) for x in inputs]
                                d=comparison(*arrays) if evaluation=='same_sample' else independent_comparison(*arrays,f,fv)
                                panels[f'l{leg+1}_{obs}']=d
                                rec[f'{obs}_TV']={k:d[f'tv_{k}'] for k in ('before','after')}
                                np.savez_compressed(rd/f'comparison_{ch}_l{leg+1}_{obs}.npz',**d,pt_edges=PT,eta_edges=ETA)
                            for fi,feat in enumerate(FEATURES):
                                ms,mt=[x[:,fi] for x in mm]
                                after=weighted_feature(ms,mt) if evaluation=='same_sample' else independent_feature(ms,f,fv)
                                rec[feat]=dict(before=estimate(ms.sum(axis=0)),after=after,target=estimate(mt.sum(axis=0)))
                            record[f'l{leg+1}']=rec
                            if leg==0:
                                ss=s.sum(axis=(1,2)); st=t.sum(axis=(1,2))
                                used_f=st/ss if evaluation=='same_sample' else f
                                record['yields']=dict(before=float(ss.sum()),after=float(np.dot(used_f,ss)),target=float(st.sum()))
                                record['matched_variable_TV']=float(.5*np.abs(used_f*ss/np.dot(used_f,ss)-st/st.sum()).sum())
                                np.savez_compressed(rd/f'applied_factors_{ch}.npz',factor=used_f,
                                    factor_var=(tvtest.sum(axis=(1,2))/ss**2+st**2*sv.sum(axis=(1,2))/ss**4) if evaluation=='same_sample' else fv,
                                    source=ss,target=st,after=used_f*ss)
                        summary[f'{ch}/{cat}/{region}/{mode}/{evaluation}']=record
                        draw(ROOT,rd,ch,region,cat,panels,
                             matching={'mll':'m_{ll}','zpt':'p_{T}(ll)','mll_zpt':'m_{ll},p_{T}(ll)'}[mode],
                             independent=evaluation=='validation')
                all_factors[f'{ch}/{cat}/{region}']=factor_records
                plot_factors(ROOT,dest,ch,cat,region,factor_records)
                print(f'Finished {ch}/{cat}/{region}',flush=True)
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (a.out_dir/'training_factors.json').write_text(json.dumps(all_factors,indent=2,allow_nan=False)+'\n')
    lines=['# DY OS: 1j -> >=2j recoil transfer','',
        'Zpt means reco pt_l1l2. Nominal DY corrections on; no charge flip; DY MC only.',
        'ge2j = nJet>=2; SRtopology additionally requires passResolved and mlljj>800.',
        'Factors are separately estimated per channel, target AND mll region. Inclusive factors are not reused in highmass.',
        'mll mode: match mass only. zpt mode: match recoil only within this mll region. mll_zpt: match the joint distribution.',
        'Same_sample: full-sample factors and full-sample comparison, fitted-factor correlations included.',
        'Validation: factors from random fold 0, applied to independent fold 1; factor errors propagated. No systematic errors.',
        f'Base mll edges: {MASS.tolist()}. Base Zpt edges: {ZPT.tolist()}.',
        f'Adjacent Zpt bins merged using training sample only until both populations have Neff>={a.min_train_neff:g}.',
        'Mass bins are not merged. Low-stat Zpt tail merged backward. Factors are absolute yield ratios, not unit-area ratios.',
        'All plotted lepton shapes have unit area; last pT bin includes >=2000. Moments use raw pT.',
        'TV=0.5 sum absolute normalized-bin differences; 0 identical. Finite statistics and binning affect TV.',
        '', '| channel/target/mll region/method/evaluation | leg | mean pT: before -> after -> target [GeV] | pT TV: before -> after |',
        '|---|---|---|---|']
    for key,r in summary.items():
        for leg in ('l1','l2'):
            c=r[leg]; mean=' -> '.join(f"{c['mean_pt'][k]['value']:.2f} +/- {c['mean_pt'][k]['error']:.2f}" for k in ('before','after','target'))
            lines.append(f"| {key} | {leg} | {mean} | {c['pt_TV']['before']:.4f} -> {c['pt_TV']['after']:.4f} |")
    (a.out_dir/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('Finished:',a.out_dir,flush=True)


if __name__=='__main__': main()
