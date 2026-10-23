"""Run the existing CF analyzer on a reproducible bounded NLO subsample.

Use run_nlo_direction.sh inside cutbased/condor/in_container.sh.
The sample normalization is irrelevant within a single sample; different mass
samples must be combined using the *processed* sum of generator signs.
"""
import argparse
import json
import os
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sample', required=True)
    ap.add_argument('--max-events', type=int, default=20000)
    ap.add_argument('--raw-base', type=Path, default=Path('/gv0/DATA/SKNano/NanoAODv15_RNTuple/2024'))
    ap.add_argument('--out-dir', type=Path, default=Path(__file__).resolve().parents[1]/'data/nlo_direction_events')
    a = ap.parse_args()
    import ROOT
    import numpy as np
    ROOT.gROOT.SetBatch(True)
    if ROOT.gSystem.Load('libHNWR.so') < 0:
        raise RuntimeError('Cannot load libHNWR.so')
    info = json.loads((Path(os.environ['SKNANO_DATA'])/'2024/Sample/CommonSampleInfo.json').read_text())[a.sample]
    files = sorted((a.raw_base/info['PD']).glob('*/*/*/tree_*.root'))
    if not files:
        raise RuntimeError(f'No input for {a.sample}: {info}')
    # Use only enough complete files to reach the requested cap.
    chosen = []; n = 0
    for f in files:
        chosen.append(str(f))
        n += int(ROOT.RDataFrame('Events', str(f)).Count().GetValue())
        if n >= a.max_events:
            break
    print('INPUT', a.sample, len(chosen), 'files, cap', a.max_events, flush=True)
    raw = ROOT.RDataFrame('Events', ROOT.std.vector('string')(chosen)).Range(a.max_events)
    signs = raw.Define('gen_sign', '(genWeight>0)-(genWeight<0)')
    sum_sign = signs.Sum('gen_sign'); count = raw.Count(); sum_w = raw.Sum('genWeight')
    processed = int(count.GetValue()); norm = float(sum_sign.GetValue())
    if norm <= 0:
        raise RuntimeError('Nonpositive processed normalization')
    a.out_dir.mkdir(parents=True, exist_ok=True)
    output = a.out_dir/(a.sample+'.root')
    if output.exists():
        raise FileExistsError(output)
    module = ROOT.HNWR_ChargeFlip()
    module.SetRNTupleName('Events'); module.SetAnalyzerName('HNWR_ChargeFlip')
    module.SetOutputThreads(1); module.LogEvery = 10000
    module.IsDATA = False; module.MCSample = a.sample
    module.xsec = info['xsec']; module.sumSign = norm; module.sumW = float(sum_w.GetValue())
    module.SetEra('2024'); module.SetPeriod('')
    for f in chosen:
        module.AddFile(f)
    module.MaxEvent = processed
    module.SetOutfilePath(str(output))
    module.SetFailurePolicy('fail-fast'); module.SetMaxEventErrors(1)
    module.Init(); module.initializeAnalyzer(); module.Loop(); module.WriteHist()
    from jetbin_z_direction import COLS
    # Empty selected samples publish no RNTuple (e.g. low-mass ee after 60/53).
    with ROOT.TFile.Open(str(output)) as f:
        present = bool(f.Get('Central_CF_Tree'))
    if present:
        df = ROOT.RDataFrame('Central_CF_Tree', str(output))
        arrays = df.AsNumpy(list(COLS))
    else:
        arrays = {k:np.empty(0,dtype=np.float32) for k in COLS}
    np.savez_compressed(output.with_suffix('.npz'), **arrays)
    output.with_suffix('.json').write_text(json.dumps(dict(sample=a.sample, sample_info=info,
        inputs=chosen, processed=processed, processed_sum_sign=norm, processed_sumw=float(sum_w.GetValue()),
        selected_rows=len(arrays['weight']), negative_rows=int((arrays['weight']<0).sum()),
        note='Bounded prefix of sorted raw files, not full production; no generator HT cut.'), indent=2)+'\n')
    print('COMPLETE', a.sample, processed, len(arrays['weight']), flush=True)


if __name__ == '__main__':
    main()
