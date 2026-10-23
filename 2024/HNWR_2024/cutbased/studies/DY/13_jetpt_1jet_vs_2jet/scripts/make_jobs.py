#!/usr/bin/env python3
"""Quick local JetXcheck run (2026-09-25): a few files per sample, job macros cloned from the FlipSF production.
Scale per sample = total files / used files (MC); data is used for shapes only."""
import glob, os, re
R = "/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_205901_HNWR_RFlav_DYCRCharge_SRChargeSplit_ZptNJet_FlipSF/2024"
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/gv0/Users/achihwan/SKNanoOutput_jetxcheck"
PLAN = {}
for d in sorted(glob.glob(f"{R}/Skim_HNWR_DYto2L-4Jets_*")): PLAN[os.path.basename(d)] = 4
PLAN.update({"Skim_HNWR_TTto2L2Nu_TuneCP5": 8, "Skim_HNWR_TWminusto2L2Nu": 2, "Skim_HNWR_TbarWplusto2L2Nu": 2})
for s in ["Muon0", "Muon1", "EGamma0", "EGamma1"]: PLAN[f"Skim_HNWR_{s}_G"] = 10
FLAGS = '\t"RFlav",\n\t"ZptNJet",\n\t"JetXcheck",\n\t"WeightSystOnly",\n'
lines = []
for s, n in PLAN.items():
    js = sorted(glob.glob(f"{R}/{s}/job_*.cc"), key=lambda p: int(re.findall(r"job_(\d+)", p)[0]))
    tot = len(js); os.makedirs(f"{OUT}/{s}", exist_ok=True)
    for p in js[:n]:
        k = re.findall(r"job_(\d+)", p)[0]; t = open(p).read()
        t = re.sub(r"module\.Userflags = \{.*?\};", "module.Userflags = {\n" + FLAGS + "    };", t, flags=re.S)
        t = re.sub(r'SetOutfilePath\(".*?"\)', f'SetOutfilePath("{OUT}/{s}/hists_{k}.root")', t)
        t = t.replace(f"void job_{k}()", f"void jx_{s.replace('-', '_')}_{k}()")
        name = f"jx_{s.replace('-', '_')}_{k}"
        open(f"{W}/jobs/{name}.cc", "w").write(t)
        lines.append(name)
    open(f"{OUT}/{s}/scale.txt", "w").write(f"{tot} {min(n, tot)}\n")
open(f"{W}/jobs/list.txt", "w").write("\n".join(lines) + "\n")
print(len(lines), "macros")
