"""NLO POWHEG reco Z direction: signed MC weights, exclusive 0/1/2 jets.

Plot from portable event NPZs; no access to original ROOT inputs is needed.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from jetbin_z_direction import COLS, EDGES, FEATURES, REGIONS, reconstruct, draw
from jetbin_lepton_shapes import BASE, CHANNELS, estimate

SLICES = {'all_zpt':(0,np.inf), 'zpt_50to100':(50,100), 'zpt_100to150':(100,150)}


def moments(x, w):
    ok = np.isfinite(x)
    x, w = x[ok], w[ok]
    return np.array([w.sum(), (w*w).sum(), (w*x).sum(), (w*w*x).sum(), (w*w*x*x).sum()])


def accumulate(d):
    q,y,eta = reconstruct(d)
    valid = np.isfinite(eta)
    obs = dict(eta=eta, rapidity=y, abs_eta=np.abs(eta), abs_y=np.abs(y))
    feats = (np.abs(eta),np.abs(y),np.where(valid,np.abs(eta)<1,np.nan),np.abs(y)<1,
             q,d['m_l1l2'],np.where(valid,np.abs(eta)>=6,np.nan),y<0)
    result = {}
    for ch, chid in zip(CHANNELS, (11,13)):
        for region,(lo,hi) in REGIONS.items():
            for slice_name,(ql,qh) in SLICES.items():
                use = (d['channel']==chid)&(d['m_l1l2']>=lo)&(d['m_l1l2']<hi)&(q>=ql)&(q<qh)
                h = {k:np.zeros((3,len(e)-1)) for k,e in EDGES.items()}
                v = {k:np.zeros_like(a) for k,a in h.items()}
                records = {}
                for nj in range(3):
                    pick = use&(d['nJet']==nj)
                    w = d['weight'][pick].astype(float)
                    for key,e in EDGES.items():
                        x=obs[key][pick]; ok=np.isfinite(x)
                        x=np.clip(x[ok],e[0],np.nextafter(e[-1],e[0]))
                        h[key][nj] = np.histogram(x,bins=e,weights=w[ok])[0]
                        v[key][nj] = np.histogram(x,bins=e,weights=w[ok]**2)[0]
                        np.testing.assert_allclose(h[key][nj].sum(),w[ok].sum(),rtol=1e-10,atol=1e-7)
                        np.testing.assert_allclose(v[key][nj].sum(),(w[ok]**2).sum(),rtol=1e-10,atol=1e-7)
                    mm=[moments(np.asarray(x[pick],dtype=float),w) for x in feats]
                    records[f'{nj}j']=dict(mc_entries=int(pick.sum()),negative_entries=int((w<0).sum()),
                        sumw=float(w.sum()),neff=float(w.sum()**2/(w*w).sum()) if len(w) else 0,
                        zero_qt=int((~valid[pick]).sum()),
                        **{f:estimate(m) if m[0]!=0 else dict(value=None,error=None)
                           for f,m in zip(FEATURES,mm)})
                result[f'{ch}/{region}/{slice_name}']=(h,v,records)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dumps',type=Path,default=BASE/'data/nlo_direction_v1')
    ap.add_argument('--out-dir',type=Path,default=BASE/'AN_rawcharge/15_nlo_jetbin_z_direction')
    a=ap.parse_args()
    files=sorted(a.dumps.glob('DYto2*_MLL*.npz'))
    if len(files)!=20:
        raise ValueError(f'Expected 20 completed ee/mumu mass samples; found {len(files)}')
    parts=[]; sources=[]
    for f in files:
        meta=json.loads(f.with_suffix('.json').read_text())
        with np.load(f) as z:
            take=(z['hasPair']>0)&(z['isSS']==0)&(z['m_l1l2']>=60)
            d={k:z[k][take] for k in COLS}
        if any(not np.all(np.isfinite(x)) for x in d.values()):
            raise ValueError(f'Nonfinite inputs: {f}')
        np.testing.assert_array_equal(d['w_dy'],np.ones_like(d['w_dy']))
        parts.append(d); sources.append(meta)
    data={k:np.concatenate([p[k] for p in parts]) for k in COLS}
    result=accumulate(data)
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary={}
    for key,(h,v,records) in result.items():
        ch,region,slice_name=key.split('/')
        if any(h['rapidity'][k].sum()<=0 for k in range(3)):
            continue
        dest=a.out_dir/region/slice_name; dest.mkdir(parents=True,exist_ok=True)
        draw(ROOT,dest,ch,'NLO POWHEG (subsample)',region,slice_name,h,v,
             subtitle='2024; no gen HT cut; lepton p_{T}>60/53 GeV; no DY/CF/transfer weight; MC stat. only')
        np.savez_compressed(dest/f'distributions_{ch}.npz',
            **{f'h_{k}':x for k,x in h.items()},**{f'v_{k}':x for k,x in v.items()},
            **{f'edges_{k}':e for k,e in EDGES.items()})
        summary[key]=records
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (a.out_dir/'provenance.json').write_text(json.dumps(dict(samples=sources,
        selection='Existing HNWR_ChargeFlip: hasPair, OS, mll>=60; exactly 0/1/2 cleaned jets, pt>40, abs eta<2.5; no SR topology cut',
        weights='Signed genWeight normalization x luminosity x PU x lepton SF. MCweight uses sign; xsec/processed sumSign per mass sample. w_dy verified ==1. No charge-flip or transfer weights.',
        statistics='Bounded prefixes, not full production. Errors include weighted counting and shape normalization, not systematic variations.',
        eta='Reconstructed dilepton momentum eta; qT=0 excluded from eta only; abs eta>=6 folded to edge display bins; raw moments unclipped.',
        portability='Input paths are provenance only; replot from NPZs with --dumps.'),indent=2)+'\n')
    lines=['# NLO POWHEG: reco dilepton direction by jet count','',
           '2024 ee/mumu mass-binned samples (10 GeV to infinity), bounded event subsets, no generator HT cut.',
           'Exclusive 0/1/2 cleaned jets; same CF analyzer selections as the LO study; no passResolved/mlljj cut.',
           'Signed MC weights retained; no DY, charge-flip, or transfer reweighting. PU and lepton SF retained.',
           'Each category is normalized to area one. Errors are MC statistical only.',
           '', '| channel / mass | jets | mean abs eta | mean abs y | abs eta<1 [%] | mean qT [GeV] | entries | Neff |',
           '|---|---|---|---|---|---|---|---|']
    for key,record in summary.items():
        if not key.endswith('/all_zpt'): continue
        for cat,r in record.items():
            def fmt(name,scale=1):
                t=r[name]; return f'{scale*t["value"]:.4f} +- {scale*t["error"]:.4f}'
            lines.append(f'| {key} | {cat} | {fmt("mean_abs_eta")} | {fmt("mean_abs_y")} | {fmt("fraction_abs_eta_lt1",100)} | {fmt("mean_zpt")} | {r["mc_entries"]} | {r["neff"]:.1f} |')
    (a.out_dir/'RESULTS.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    main()
