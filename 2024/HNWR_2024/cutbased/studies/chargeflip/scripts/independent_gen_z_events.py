"""Read raw NLO generator fields only; no HT, HLT, reco-lepton or SR selection."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

BASE=Path(__file__).resolve().parents[1]
COLS=('mass','pt','pz','eta','rapidity','source','njet25','njet50','boson_candidates')


def extract(a):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    header=Path(__file__).with_name('independent_gen_z.hxx')
    ROOT.gInterpreter.Declare(header.read_text())
    meta=json.loads(a.manifest.read_text())
    cap=min(meta['processed'],a.max_events) if a.max_events else meta['processed']
    out=a.out_dir/meta['sample']
    if out.with_suffix('.npz').exists():
        raise FileExistsError(out)
    df=ROOT.RDataFrame('Events',ROOT.std.vector('string')(meta['inputs'])).Range(cap)
    df=df.Define('ind_z','IndependentDY::direction(GenPart_pt,GenPart_eta,GenPart_phi,GenPart_mass,GenPart_pdgId,GenPart_status,GenPart_statusFlags,GenJet_pt,GenJet_eta,GenJet_phi)')
    for i,name in enumerate(COLS):
        df=df.Define('ind_'+name,f'ind_z[{i}]')
    # HT is read only as an audit observable. It never enters a Filter.
    arrays=df.AsNumpy(['ind_'+k for k in COLS]+['genWeight','LHE_HT'])
    d={k:arrays['ind_'+k] for k in COLS}
    d.update(genWeight=arrays['genWeight'],LHE_HT=arrays['LHE_HT'])
    assert len(d['mass'])==cap
    a.out_dir.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out.with_suffix('.npz'),**d)
    found=d['source']>0
    rec=dict(sample=meta['sample'],sample_info=meta['sample_info'],inputs=meta['inputs'],processed=cap,
        processed_sumw=float(d['genWeight'].astype(float).sum()),
        negative_events=int((d['genWeight']<0).sum()),
        sources={str(k):int((d['source']==k).sum()) for k in (0,1,2,3)},
        raw_ht_lt40=int((d['LHE_HT']<40).sum()),found_ht_lt40=int((found&(d['LHE_HT']<40)).sum()),
        root_version=ROOT.gROOT.GetVersion(),definition_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),
        definition='Hard-process last-copy gen Z (status62 preferred by identification); otherwise unique isHardProcess OSSF e/mu pair. Ambiguous/missing excluded and counted. Pre-FSR boson.',
        jets='GenJet pt>40, abs eta<2.5 (primary) or <5 (cross-check); dR>=0.4 from prompt status1 gen e/mu, no lepton kinematic cuts.',
        cuts='No HT, trigger, reconstructed object, lepton pt/eta, or SR cuts. All raw events retained in cache.',
        weights='Plot with full signed genWeight*xsec/processed_sumw, no PU/SF/DY/CF/transfer.')
    out.with_suffix('.json').write_text(json.dumps(rec,indent=2)+'\n')
    print('COMPLETE',meta['sample'],rec['sources'],'HT<40',rec['raw_ht_lt40'],flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--manifests',type=Path,default=BASE/'data/nlo_direction_v1')
    ap.add_argument('--out-dir',type=Path,default=BASE/'data/independent_gen_z_v1')
    ap.add_argument('--max-events',type=int)
    a=ap.parse_args()
    if a.manifest:
        extract(a); return
    files=sorted(p for p in a.manifests.glob('DYto2*_MLL*.json') if '.root.' not in p.name)
    if len(files)!=20: raise ValueError(f'Expected 20 sample manifests, found {len(files)}')
    a.out_dir.mkdir(parents=True,exist_ok=True)
    def run(f):
        if (a.out_dir/f.name).exists(): return
        cmd=[sys.executable,__file__,'--manifest',str(f),'--out-dir',str(a.out_dir)]
        if a.max_events: cmd+=['--max-events',str(a.max_events)]
        print('START',f.stem,flush=True)
        with (a.out_dir/(f.stem+'.log')).open('w') as log:
            p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
        if p.returncode: raise RuntimeError(f'{f.stem} failed; inspect its log')
        print('DONE',f.stem,flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run,files))


if __name__=='__main__': main()
