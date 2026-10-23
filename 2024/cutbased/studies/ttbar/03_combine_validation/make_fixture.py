#!/usr/bin/env python3
"""Synthetic fixture for the shared-rateParam Top model (spec 10.2 / 10.3). No systematics, no MC-stat nuisances.
CR obs is the Asimov for beta = 1.2; the SR pseudo-observation is arbitrary (variant A / B) and must not matter
when the SR is masked.   python3 make_fixture.py OUTDIR"""
import sys, os, array, ROOT
ROOT.gROOT.SetBatch(True); ROOT.TH1.AddDirectory(False)
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
EDGES = array.array("d", [800, 1200, 2000, 8000])
CR = {"Top": [600, 300, 100], "Other": [60, 30, 10]}
SR = {"Signal": [1, 2, 3], "Top": [40, 20, 10], "Other": [5, 3, 2]}
BETA = 1.2
OBS_CR = [BETA * t + o for t, o in zip(CR["Top"], CR["Other"])]            # 780, 390, 130
OBS_SR = {"A": [50, 25, 14], "B": [500, 1, 300]}


def h(name, vals):
    x = ROOT.TH1D(name, "", 3, EDGES)
    for i, v in enumerate(vals): x.SetBinContent(i + 1, v); x.SetBinError(i + 1, 0.0)
    return x


for var, obs_sr in OBS_SR.items():
    f = ROOT.TFile.Open(f"{out}/shapes_{var}.root", "RECREATE")
    for ch, procs, obs in (("CR_EM", CR, OBS_CR), ("SR_EE", SR, obs_sr)):
        d = f.mkdir(ch); d.cd()
        for p, v in procs.items(): h(p, v).Write()
        h("data_obs", obs).Write()
    f.Close()
    with open(f"{out}/card_{var}.txt", "w") as c:
        c.write(f"""imax 2
jmax 2
kmax *
------------
shapes * * shapes_{var}.root $CHANNEL/$PROCESS $CHANNEL/$PROCESS_$SYSTEMATIC
------------
bin          CR_EM SR_EE
observation  -1    -1
------------
bin      CR_EM CR_EM SR_EE  SR_EE SR_EE
process  Top   Other Signal Top   Other
process  1     2     0      1     2
rate     -1    -1    -1     -1    -1
------------
dummy lnN - - 1.0001 - -
beta_top rateParam CR_EM Top 1 [0,5]
beta_top rateParam SR_EE Top 1 [0,5]
""")
print("fixture written to", out)
