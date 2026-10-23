#!/usr/bin/env python3
"""Expected crossing (r = 1) in mWR, log-linear interpolation of r between the 1 TeV grid points (as tab:expected_crossings).
   python3 crossings.py limits.csv [...]   or   python3 crossings.py --workdir work_blind TAG ...  (reads limit.log)"""
import csv, math, re, sys, os, json
Q = ["m1", "med", "p1"]

def cross(pts):  # pts: sorted [(mWR, r)]
    for (m0, r0), (m1, r1) in zip(pts, pts[1:]):
        if r0 <= 1 < r1:
            a, b = math.log(r0), math.log(r1)
            return m0 + (m1 - m0) * (0 - a) / (b - a)
    return float("nan")

def table(rows):  # rows: {(mWR,mN): {q: r}}
    out = {}
    for lab, sel in (("N200", lambda m, n: n == 200), ("halfN", lambda m, n: 2 * n == m)):
        pts = sorted((m, v) for (m, n), v in rows.items() if sel(m, n))
        out[lab] = {q: cross([(m, v[q]) for m, v in pts]) for q in Q}
        out[lab]["npts"] = len(pts)
    return out

def from_csv(p):
    rows = {}
    for r in csv.DictReader(open(p)):
        rows[(int(float(r["mWR"])), int(float(r["mN"])))] = {"m1": float(r["r_exp_minus1sigma"]), "med": float(r["r_exp_median"]), "p1": float(r["r_exp_plus1sigma"])}
    return rows

def from_logs(wd, tag, ch):
    rows = {}
    for d in os.listdir(wd):
        m = re.fullmatch(re.escape(f"{tag}_{ch}_") + r"WR(\d+)_N(\d+)", d)
        if not m: continue
        try: txt = open(f"{wd}/{d}/limit.log").read()
        except OSError: continue
        g = {k: re.search(rf"Expected {k}%: r < ([0-9.eE+-]+)", txt) for k in ("16.0", "50.0", "84.0")}
        if not all(g.values()): continue
        rows[(int(m[1]), int(m[2]))] = {"m1": float(g["16.0"][1]), "med": float(g["50.0"][1]), "p1": float(g["84.0"][1])}
    return rows

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--workdir":
        res = {t: {ch: table(from_logs(a[1], t, ch)) for ch in ("EE", "MM")} for t in a[2:]}
    else:
        res = {p: table(from_csv(p)) for p in a}
    print(json.dumps(res, indent=1))
