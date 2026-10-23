exec(open("flipsf.py").read().split("isdy=d")[0])
# per-electron P from pooled MC (universal), pT x |eta| bins
PT=np.array([53,70,100,150,200,300,400,600,4000.]); ETA=np.array([0,0.8,1.4442,1.566,2.0,2.5])
def ib(i):
    return (np.clip(np.searchsorted(PT,d[f"l{i}_pt"],"right")-1,0,len(PT)-2),
            np.clip(np.searchsorted(ETA,np.abs(d[f"l{i}_scEta"]),"right")-1,0,len(ETA)-2))
mc=~isdata; num=np.zeros((len(PT)-1,len(ETA)-1)); den=np.zeros_like(num); B={}
for i in (1,2):
    a,b=ib(i); B[i]=(a,b); ok=mc&cls[i]["prompt"]&(d[f"l{i}_genChargeIdx"]!=0)
    np.add.at(den,(a[ok],b[ok]),w[ok]); np.add.at(num,(a[ok&cls[i]["flip"]],b[ok&cls[i]["flip"]]),w[ok&cls[i]["flip"]])
P=np.divide(num,den,out=np.zeros_like(num),where=den>0)
def wts(which):
    r=np.ones(len(w))
    for i in (1,2):
        s=np.where(np.abs(d[f"l{i}_scEta"])<1.5,SFB,SFE); p=P[B[i]]
        ok=cls[i]["prompt"]&(d[f"l{i}_genChargeIdx"]!=0)&which
        r=np.where(ok&cls[i]["flip"],r*s,r)
        r=np.where(ok&~cls[i]["flip"],r*(1-s*p)/(1-p),r)
    return r
isdy=d["g"]=="DY"
r_dy=wts(isdy); r_all=wts(mc)
def row(lab,m,q):
    D=(m&isdata&q).sum(); M=m&mc&q
    v=[w[M].sum(),(w*r_dy)[M].sum(),(w*r_all)[M].sum()]
    print(f"| {lab} | {D} | "+" | ".join(f"{x:.1f} ({D/x:.4f})" for x in v)+" |")
hdr="| 선택 | data | MC 없음 (data/MC) | DY만 SF | 전 공정 SF |\n|---|---|---|---|---|"
cr=d["isDYCR"]>0; zw=(d["passResolved"]>0)&(d["m_l1l2"]>=60)&(d["m_l1l2"]<150)
for rn,rm in [("DY CR",cr),("Z window",zw)]:
    print(f"\n## {rn}\n"+hdr)
    row("OS",rm,~ss); row("SS",rm,ss)
    e1=np.abs(d["l1_scEta"])>1.5; e2=np.abs(d["l2_scEta"])>1.5; n=e1.astype(int)+e2.astype(int)
    for k,l in enumerate(["BB","BE","EE"]): row("OS "+l,rm&(n==k),~ss)
    # SS/OS double ratio
    for lab,r in [("없음",np.ones(len(w))),("DY만",r_dy),("전 공정",r_all)]:
        so=lambda q:(w*r)[rm&mc&q].sum()
        dr=((rm&isdata&ss).sum()/(rm&isdata&~ss).sum())/(so(ss)/so(~ss))
        print(f"  (SS/OS)_data/(SS/OS)_MC [{lab}] = {dr:.3f}")
sr=(d["passResolved"]>0)&(d["m_l1l2"]>200)&(d["m_lljj"]>800)&mc
print("\nSR-like MC OS:",*[f"{(w*r)[sr&~ss].sum():.1f}" for r in (np.ones(len(w)),r_dy,r_all)])
