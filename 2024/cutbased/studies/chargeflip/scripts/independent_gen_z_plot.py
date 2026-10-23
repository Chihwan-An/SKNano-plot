"""Unit-area NLO gen Z eta/y, independent of reconstructed analysis selections."""
import argparse
import json
from pathlib import Path
import numpy as np
from jetbin_lepton_shapes import BASE, norm, estimate
from nlo_jetbin_z_direction import moments

EDGES={'eta':np.linspace(-10,10,81),'rapidity':np.linspace(-6,6,61)}
REGIONS={'all_mass':(0,np.inf),'Zpeak':(80,100),'highmass':(400,np.inf)}
SLICES={'all_pt':(0,np.inf),'pt_100to150':(100,150)}
FEATURES=('mean_abs_eta','mean_abs_y','mean_pt','fraction_abs_eta_lt1',
          'fraction_abs_y_lt1','fraction_ht_lt40','fraction_abs_eta_ge10')


def build(folder):
    files=sorted(folder.glob('DYto2*_MLL*.npz'))
    if len(files)!=20: raise ValueError(f'Expected 20 samples, found {len(files)}')
    accum={}; sources=[]
    for f in files:
        meta=json.loads(f.with_suffix('.json').read_text()); sources.append(meta)
        with np.load(f) as z: d={k:z[k] for k in z.files}
        assert len(d['mass'])==meta['processed']
        sw=d['genWeight'].astype(float).sum()
        np.testing.assert_allclose(sw,meta['processed_sumw'])
        w=d['genWeight'].astype(float)*meta['sample_info']['xsec']/sw
        found=d['source']>0
        if not all(np.all(np.isfinite(d[k][found])) for k in ('mass','pt','rapidity','pz')):
            raise ValueError(f'Nonfinite Z kinematics: {f}')
        valideta=np.isfinite(d['eta'])
        assert np.all(valideta[found&(d['pt']>0)])
        ch='EE' if f.name.startswith('DYto2E_') else 'MM'
        features=(np.abs(d['eta']),np.abs(d['rapidity']),d['pt'],
                  np.where(valideta,np.abs(d['eta'])<1,np.nan),np.abs(d['rapidity'])<1,
                  d['LHE_HT']<40,np.where(valideta,np.abs(d['eta'])>=10,np.nan))
        for jetkey in ('njet25','njet50'):
            for region,(lo,hi) in REGIONS.items():
                for sl,(ql,qh) in SLICES.items():
                    key=f'{ch}/{jetkey}/{region}/{sl}'
                    if key not in accum:
                        accum[key]=dict(h={k:np.zeros((3,len(e)-1)) for k,e in EDGES.items()},
                            v={k:np.zeros((3,len(e)-1)) for k,e in EDGES.items()},
                            mom=np.zeros((3,len(FEATURES),5)),counts=np.zeros((3,4),dtype=np.int64))
                    a=accum[key]
                    use=found&(d['mass']>=lo)&(d['mass']<hi)&(d['pt']>=ql)&(d['pt']<qh)
                    for nj in range(3):
                        pick=use&(d[jetkey]==nj); ww=w[pick]
                        a['counts'][nj]+=[int(pick.sum()),int((ww<0).sum()),
                            int((pick&(d['LHE_HT']<40)).sum()),int((pick&~valideta).sum())]
                        for k,e in EDGES.items():
                            x=d[k][pick]; ok=np.isfinite(x)
                            x=np.clip(x[ok],e[0],np.nextafter(e[-1],e[0]))
                            h=np.histogram(x,bins=e,weights=ww[ok])[0]
                            v=np.histogram(x,bins=e,weights=ww[ok]**2)[0]
                            np.testing.assert_allclose(h.sum(),ww[ok].sum(),rtol=1e-9,atol=1e-9)
                            np.testing.assert_allclose(v.sum(),(ww[ok]**2).sum(),rtol=1e-9,atol=1e-9)
                            a['h'][k][nj]+=h; a['v'][k][nj]+=v
                        for i,x in enumerate(features): a['mom'][nj,i]+=moments(x[pick],ww)
        print('HIST',f.stem,flush=True)
    return accum,sources


def draw(ROOT,dest,key,a):
    ch,jets,region,sl=key.split('/')
    c=ROOT.TCanvas('ind_gen','',1250,600); keep=[]
    colors=(ROOT.kBlack,ROOT.kAzure+2,ROOT.kRed+1)
    for p,(k,e) in enumerate(EDGES.items()):
        c.cd(); pad=ROOT.TPad(f'pad{p}','',.5*p,0,.5*(p+1),.86)
        pad.SetLeftMargin(.13); pad.SetBottomMargin(.13); pad.SetTopMargin(.15)
        pad.Draw(); pad.cd(); keep.append(pad)
        shapes=[norm(a['h'][k][j],a['v'][k][j]) for j in range(3)]
        ymax=max(float((x+np.sqrt(v)).max()) for x,v in shapes)*1.15
        ymin=min(0.,min(float(x.min()) for x,v in shapes)*1.15)
        legend=ROOT.TLegend(.53,.84,.91,.99); legend.SetBorderSize(0); legend.SetTextSize(.034)
        xlabel='#eta_{Z}^{gen}' if k=='eta' else 'y_{Z}^{gen}'
        for j,(x,v) in enumerate(shapes):
            h=ROOT.TH1D(f'h_{p}_{j}',f';{xlabel};fraction / bin',len(e)-1,e)
            for i in range(len(x)):
                h.SetBinContent(i+1,float(x[i])); h.SetBinError(i+1,float(np.sqrt(v[i])))
            h.SetLineColor(colors[j]); h.SetMarkerColor(colors[j]); h.SetLineWidth(2)
            h.SetMinimum(ymin); h.SetMaximum(ymax)
            h.GetXaxis().SetTitleSize(.047); h.GetYaxis().SetTitleSize(.045)
            h.Draw('hist e'+(' same' if j else '')); keep.append(h)
            legend.AddEntry(h,f'exactly {j} gen jet'+('s' if j!=1 else ''),'l')
        legend.Draw(); keep.append(legend)
    c.cd(); t=ROOT.TLatex(); t.SetNDC(); t.SetTextFont(42); t.SetTextSize(.029)
    mass={'all_mass':'all generated masses','Zpeak':'80<m_{Z}<100 GeV','highmass':'m_{Z}>400 GeV'}[region]
    t.DrawLatex(.035,.953,f'2024 NLO POWHEG, Z#rightarrow{ch}; {mass}; {sl}; unit area')
    t.SetTextSize(.024)
    t.DrawLatex(.035,.903,f'NO HT / trigger / lepton cuts or SF; gen jets p_{{T}}>40 GeV, |#eta|<{"2.5" if jets=="njet25" else "5"}; tails folded')
    dest.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'): c.SaveAs(str(dest/f'z_direction_{ch}.{ext}'))
    c.Close()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dumps',type=Path,default=BASE/'data/independent_gen_z_v1')
    ap.add_argument('--out-dir',type=Path,default=BASE/'AN_rawcharge/16_independent_gen_z')
    a=ap.parse_args(); accum,sources=build(a.dumps)
    import ROOT
    ROOT.gROOT.SetBatch(True); ROOT.gStyle.SetOptStat(0); ROOT.TH1.AddDirectory(False)
    summary={}
    for key,r in accum.items():
        records={}
        for j in range(3):
            mm=r['mom'][j]; sw,sw2=mm[1,:2]
            records[f'{j}j']=dict(entries=int(r['counts'][j,0]),negative=int(r['counts'][j,1]),
                ht_lt40_entries=int(r['counts'][j,2]),eta_undefined=int(r['counts'][j,3]),
                sumw=float(sw),neff=float(sw*sw/sw2) if sw2>0 else 0,
                **{f:estimate(m) if m[0]!=0 else dict(value=None,error=None) for f,m in zip(FEATURES,mm)})
        summary[key]=records
        ch,jets,region,sl=key.split('/'); dest=a.out_dir/jets/region/sl
        if all(x.sum()>0 for x in r['h']['eta']): draw(ROOT,dest,key,r)
        dest.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(dest/f'distributions_{ch}.npz',moments=r['mom'],counts=r['counts'],
            **{f'h_{k}':h for k,h in r['h'].items()},**{f'v_{k}':v for k,v in r['v'].items()},
            **{f'edges_{k}':e for k,e in EDGES.items()})
    (a.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (a.out_dir/'provenance.json').write_text(json.dumps(dict(samples=sources,
        independent='Direct raw GenPart and GenJet only; not HNWR_ChargeFlip or its selected events.',
        weight='Full signed genWeight*xsec/processed_sumw, no SF or reweight. Normalize each jet category to area one.',
        selections='No HT, trigger, reco object or lepton kinematic selection. Defined mass windows are gen boson mass.',
        overflow='Eta outside [-10,10] and y outside [-6,6] folded to edge display bins. Moments unclipped.',
        uncertainty='MC statistical only; partial raw-event prefixes, not full production.'),indent=2)+'\n')
    lines=['# Independent generator-level NLO Z direction','',
        'No HT, trigger, lepton pt/eta, reco selection or SF. Full signed genWeight; each category normalized to unit area.',
        'Primary: GenJet pt>40 GeV, abs eta<2.5, dR>=0.4 from prompt status1 gen e/mu; exact 0/1/2 jets.',
        'Companion njet50 uses abs eta<5. Mass windows refer to gen boson mass, not reco mll.',
        '', '| selection | jet | mean abs eta | mean abs y | mean pt | HT<40 [%] | entries |',
        '|---|---|---|---|---|---|---|']
    for key,r in summary.items():
        for nj,v in r.items():
            def fmt(k,scale=1):
                z=v[k]
                return 'empty' if z['value'] is None else f'{z["value"]*scale:.4f} +- {z["error"]*scale:.4f}'
            lines.append(f'|{key}|{nj}|{fmt("mean_abs_eta")}|{fmt("mean_abs_y")}|{fmt("mean_pt")}|{fmt("fraction_ht_lt40",100)}|{v["entries"]}|')
    (a.out_dir/'RESULTS.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__': main()
