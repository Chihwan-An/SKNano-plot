exec(open("flipcomp.py").read().split("tc2=")[0].replace("if g is None: continue","if g is None: g='DATA'"))
SFB,SFE=1.426,1.451
isdata=d["g"]=="DATA"; w=np.where(isdata,1.0,w)
sf=np.ones(len(w))
for i in (1,2):
    s=np.where(np.abs(d[f"l{i}_scEta"])<1.5,SFB,SFE)
    sf=np.where(cls[i]["flip"],sf*s,sf)
isdy=d["g"]=="DY"; mc=~isdata
def row(lab,m):
    D=m&isdata&ss
    base=w[m&mc&ss].sum()
    dyf=w[m&mc&ss&isdy]*(sf[m&mc&ss&isdy]-1); dyonly=base+dyf.sum()
    allf=(w[m&mc&ss]*sf[m&mc&ss]).sum()
    nd=D.sum()
    fdy=w[m&mc&ss&isdy&anyflip].sum(); fnd=w[m&mc&ss&~isdy&anyflip].sum()
    e=lambda p: f"{nd/p:.3f}±{np.sqrt(nd)/p:.3f}"
    print(f"| {lab} | {nd} | {base:.1f} | {e(base)} | {dyonly:.1f} | {e(dyonly)} | {allf:.1f} | {e(allf)} | {fdy:.1f} / {fnd:.1f} |")
hdr="| 선택 | data SS | MC (SF 없음) | data/MC | MC (DY만 SF) | data/MC | MC (전 공정 SF) | data/MC | MC flip DY / non-DY |\n|---|---|---|---|---|---|---|---|---|"
cr=d["isDYCR"]>0
print("## DY CR SS ee (raw charge)\n"+hdr); row("전체",cr)
for lo,hi in [(800,1200),(1200,1600),(1600,2400),(2400,8000)]:
    row(f"m_lljj {lo}-{hi}",cr&(d["m_lljj"]>=lo)&(d["m_lljj"]<hi))
for lab,(a,b) in {"BB":(0,0),"BE":(0,1),"EE":(1,1)}.items():
    e1=np.abs(d["l1_scEta"])>1.5; e2=np.abs(d["l2_scEta"])>1.5
    n=e1.astype(int)+e2.astype(int); row(lab,cr&(n==a+b))
zw=(d["passResolved"]>0)&(d["m_l1l2"]>=60)&(d["m_l1l2"]<150)
print("\n## Z window 60-150 resolved SS ee\n"+hdr); row("전체",zw)
sr=(d["passResolved"]>0)&(d["m_l1l2"]>200)&(d["m_lljj"]>800)&mc&ss
b=w[sr].sum(); dy=b+(w[sr&isdy]*(sf[sr&isdy]-1)).sum(); al=(w[sr]*sf[sr]).sum()
print(f"\nSR-like MC SS: 없음 {b:.1f} / DY만 {dy:.1f} / 전 공정 {al:.1f}")
