import glob, os, numpy as np
D="/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/data/chargeflip/dumps_v4/all"
def grp(b):
    b=b.replace("tree_Skim_HNWR_","")
    if b.startswith("DYto2L"): return "DY"
    if b.startswith(("EGamma","Muon")): return None
    if b.startswith("TTto2L2Nu"): return "TT2L"
    if b.startswith(("TWminusto2L2Nu","TbarWplusto2L2Nu")): return "tW2L"
    if b.startswith(("TTtoLNu2Q","TWminustoLNu2Q","TbarWplustoLNu2Q","TB","Tbar")): return "top1L"
    if b.startswith("WtoLNu"): return "WJets"
    if b.startswith("WZto"): return "WZ"
    if b.startswith("ZZto"): return "ZZ"
    if b.startswith("WWto"): return "WW"
    if b.startswith(("TTLL","TTLNu")): return "ttV"
    return "other:"+b
K=['channel','isDYCR','isSS','passResolved','m_l1l2','m_lljj','weight']+[f'l{i}_{v}' for i in (1,2) for v in ('charge','genChargeIdx','genPartFlav','tightCharge','pt','scEta')]
acc={}
for p in sorted(glob.glob(D+"/tree_*.npz")):
    g=grp(os.path.basename(p))
    if g is None: continue
    z=np.load(p); m=z["channel"]==11
    for k in K: acc.setdefault(k,[]).append(z[k][m])
    acc.setdefault("g",[]).append(np.full(m.sum(),g))
d={k:np.concatenate(v) for k,v in acc.items()}
w=d["weight"].astype(float); ss=d["isSS"]>0
cls={}
for i in (1,2):
    f=d[f"l{i}_genPartFlav"]; q=d[f"l{i}_charge"]; gq=d[f"l{i}_genChargeIdx"]
    prompt=(f==1)|(f==15)
    cls[i]=dict(prompt=prompt, flip=prompt&(gq!=0)&(q!=gq), pho=(f==22), np_=~prompt&(f!=22))
anyflip=cls[1]["flip"]|cls[2]["flip"]
anynp=cls[1]["np_"]|cls[2]["np_"]
anypho=(cls[1]["pho"]|cls[2]["pho"])&~anynp
bothprompt_noflip=cls[1]["prompt"]&cls[2]["prompt"]&~anyflip
cat=np.full(len(w),"other",dtype=object)
cat[bothprompt_noflip]="promptSS"; cat[anypho&~anyflip]="photon"; cat[anynp&~anyflip]="nonprompt"; cat[anyflip]="flip"
tc2=(d["l1_tightCharge"]==2)&(d["l2_tightCharge"]==2)
regs={"DY CR (60<mee<150, mlljj>800)":d["isDYCR"]>0,
      "Z window 60-150 (resolved, no mlljj)":(d["passResolved"]>0)&(d["m_l1l2"]>=60)&(d["m_l1l2"]<150),
      "SR-like (resolved, mee>200, mlljj>800)":(d["passResolved"]>0)&(d["m_l1l2"]>200)&(d["m_lljj"]>800)}
G=["DY","TT2L","tW2L","top1L","WJets","WZ","ZZ","WW","ttV"]+sorted({x for x in np.unique(d["g"]) if x.startswith("other")})
for tag,extra in [("raw charge",np.ones(len(w),bool)),("both tightCharge==2",tc2)]:
  for rn,rm in regs.items():
    print(f"\n### {rn} — SS ee, {tag}")
    print("| group | SS total | flip | prompt SS | photon | nonprompt | flip frac | OS total | SS/OS | per-e flip P (prompt e) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for g in G+["ALL non-DY"]:
        gm=(d["g"]==g) if g!="ALL non-DY" else (d["g"]!="DY")
        m=rm&extra&gm; s=m&ss; o=m&~ss
        if w[m].sum()==0: continue
        c={k:w[s&(cat==k)].sum() for k in ["flip","promptSS","photon","nonprompt","other"]}
        tot=w[s].sum(); os_=w[o].sum()
        # per-electron flip prob among prompt gen-matched electrons (all charges)
        num=sum(w[m&cls[i]["flip"]].sum() for i in (1,2)); den=sum(w[m&cls[i]["prompt"]&(d[f"l{i}_genChargeIdx"]!=0)].sum() for i in (1,2))
        print(f"| {g} | {tot:.2f} | {c['flip']:.2f} | {c['promptSS']:.2f} | {c['photon']:.2f} | {c['nonprompt']:.2f} | {c['flip']/tot if tot>0 else 0:.2f} | {os_:.1f} | {tot/os_ if os_>0 else 0:.4f} | {num/den if den>0 else 0:.2e} |")
