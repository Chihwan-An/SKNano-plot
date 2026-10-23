exec(open("flipcomp.py").read().split("tc2=")[0])
PT=[53,100,200,400,4000]; ETA=[(0,0.8),(0.8,1.4442),(1.566,2.0),(2.0,2.5)]
res=d["passResolved"]>0
for gs in [["DY"],["TT2L","tW2L"],["WZ","ZZ","WW"]]:
  print("\n##", "+".join(gs), "(resolved, all mee, raw charge)  P_flip [n_eff flipped]")
  print("| eta \\ pT | "+" | ".join(f"{a}-{b}" for a,b in zip(PT[:-1],PT[1:]))+" |"); print("|---"*(len(PT))+"|")
  gm=np.isin(d["g"],gs)&res
  for lo,hi in ETA:
    row=[]
    for a,b in zip(PT[:-1],PT[1:]):
      num=den=n=0
      for i in (1,2):
        ae=np.abs(d[f"l{i}_scEta"]); pt=d[f"l{i}_pt"]
        m=gm&(ae>=lo)&(ae<hi)&(pt>=a)&(pt<b)&cls[i]["prompt"]&(d[f"l{i}_genChargeIdx"]!=0)
        num+=w[m&cls[i]["flip"]].sum(); den+=w[m].sum(); n+=(m&cls[i]["flip"]).sum()
      row.append(f"{num/den:.1e} [{n}]" if den>0 else "-")
    print(f"| {lo}-{hi} | "+" | ".join(row)+" |")
