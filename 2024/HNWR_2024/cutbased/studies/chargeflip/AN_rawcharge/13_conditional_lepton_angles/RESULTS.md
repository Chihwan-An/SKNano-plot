# Conditional angle and fine-binning check

DY OS MC, mll>=400, nominal DY corrections, no charge flip. No angular weight is fitted.
Same random fold assignment as study 12: fold 0 trains transfer factors, fold 1 compares shapes.
Coarse reproduces study 12 mll+Zpt matching; fine uses mll 25 GeV steps to 700, 50 to 1000, >=1000 overflow.
Fine Zpt grid subdivides the previous grid with 10 GeV steps below 200 and 25 GeV steps to 500.
Both merge adjacent Zpt bins to train Neff>=50 per population. Thus not every final bin is narrow.
Fixed boxes are 50x50 GeV; show nominal source/target plus finer within-box matching from training half (min Neff=20).
Even after local matching, within-bin and independent-test fluctuations can leave mll/Zpt differences; raw means are saved.
Ratio points require raw source and target bin Neff>=20; all bins enter shapes, means and TV.
Means, including mll/Zpt inside fixed boxes, use raw values; pT overflow is included in last plotted bin.
Statistical errors only. Transfer error propagation is first-order. TV is a descriptive distance, not a significance.

| channel/target | binning | observable | before -> after -> target (mean) | TV before -> after |
|---|---|---|---|---|
| EE/ge2j | coarse (50 cells) | asymmetry | 0.1476 +/- 0.0006 -> 0.2006 +/- 0.0015 -> 0.2003 +/- 0.0017 | 0.1582 -> 0.0124 |
| EE/ge2j | coarse (50 cells) | dphi | 2.7991 +/- 0.0016 -> 2.6377 +/- 0.0047 -> 2.6100 +/- 0.0044 | 0.2054 -> 0.0371 |
| EE/ge2j | coarse (50 cells) | pt1 | 266.4337 +/- 0.4609 -> 301.2956 +/- 1.2365 -> 299.6114 +/- 1.1114 | 0.1295 -> 0.0116 |
| EE/ge2j | coarse (50 cells) | pt2 | 200.4977 +/- 0.4131 -> 202.2608 +/- 0.9807 -> 200.9858 +/- 0.9364 | 0.0552 -> 0.0167 |
| EE/ge2j | fine (187 cells) | asymmetry | 0.1476 +/- 0.0006 -> 0.2011 +/- 0.0015 -> 0.2003 +/- 0.0017 | 0.1582 -> 0.0133 |
| EE/ge2j | fine (187 cells) | dphi | 2.7991 +/- 0.0016 -> 2.6375 +/- 0.0047 -> 2.6100 +/- 0.0044 | 0.2054 -> 0.0377 |
| EE/ge2j | fine (187 cells) | pt1 | 266.4337 +/- 0.4609 -> 301.8624 +/- 1.2684 -> 299.6114 +/- 1.1114 | 0.1295 -> 0.0136 |
| EE/ge2j | fine (187 cells) | pt2 | 200.4977 +/- 0.4131 -> 202.5773 +/- 1.0075 -> 200.9858 +/- 0.9364 | 0.0552 -> 0.0194 |
| EE/SRtopology | coarse (48 cells) | asymmetry | 0.1476 +/- 0.0006 -> 0.2170 +/- 0.0019 -> 0.2182 +/- 0.0023 | 0.1925 -> 0.0169 |
| EE/SRtopology | coarse (48 cells) | dphi | 2.7991 +/- 0.0016 -> 2.5775 +/- 0.0062 -> 2.5538 +/- 0.0060 | 0.2419 -> 0.0311 |
| EE/SRtopology | coarse (48 cells) | pt1 | 266.4337 +/- 0.4609 -> 335.5039 +/- 1.6050 -> 337.9513 +/- 1.4799 | 0.2920 -> 0.0204 |
| EE/SRtopology | coarse (48 cells) | pt2 | 200.4977 +/- 0.4131 -> 219.4846 +/- 1.3699 -> 220.6019 +/- 1.3519 | 0.1285 -> 0.0244 |
| EE/SRtopology | fine (142 cells) | asymmetry | 0.1476 +/- 0.0006 -> 0.2164 +/- 0.0019 -> 0.2182 +/- 0.0023 | 0.1925 -> 0.0171 |
| EE/SRtopology | fine (142 cells) | dphi | 2.7991 +/- 0.0016 -> 2.5805 +/- 0.0063 -> 2.5538 +/- 0.0060 | 0.2419 -> 0.0376 |
| EE/SRtopology | fine (142 cells) | pt1 | 266.4337 +/- 0.4609 -> 337.8792 +/- 1.6310 -> 337.9513 +/- 1.4799 | 0.2920 -> 0.0104 |
| EE/SRtopology | fine (142 cells) | pt2 | 200.4977 +/- 0.4131 -> 221.7345 +/- 1.4002 -> 220.6019 +/- 1.3519 | 0.1285 -> 0.0202 |
| MM/ge2j | coarse (55 cells) | asymmetry | 0.1514 +/- 0.0005 -> 0.2067 +/- 0.0013 -> 0.2025 +/- 0.0011 | 0.1540 -> 0.0145 |
| MM/ge2j | coarse (55 cells) | dphi | 2.7942 +/- 0.0014 -> 2.6362 +/- 0.0041 -> 2.6218 +/- 0.0034 | 0.1875 -> 0.0245 |
| MM/ge2j | coarse (55 cells) | pt1 | 266.6339 +/- 0.4028 -> 302.0721 +/- 1.0763 -> 299.2349 +/- 0.8537 | 0.1267 -> 0.0132 |
| MM/ge2j | coarse (55 cells) | pt2 | 198.8840 +/- 0.3524 -> 199.7094 +/- 0.8156 -> 199.5505 +/- 0.7081 | 0.0422 -> 0.0096 |
| MM/ge2j | fine (234 cells) | asymmetry | 0.1514 +/- 0.0005 -> 0.2071 +/- 0.0013 -> 0.2025 +/- 0.0011 | 0.1540 -> 0.0150 |
| MM/ge2j | fine (234 cells) | dphi | 2.7942 +/- 0.0014 -> 2.6355 +/- 0.0042 -> 2.6218 +/- 0.0034 | 0.1875 -> 0.0228 |
| MM/ge2j | fine (234 cells) | pt1 | 266.6339 +/- 0.4028 -> 301.5753 +/- 1.0801 -> 299.2349 +/- 0.8537 | 0.1267 -> 0.0133 |
| MM/ge2j | fine (234 cells) | pt2 | 198.8840 +/- 0.3524 -> 199.4040 +/- 0.8286 -> 199.5505 +/- 0.7081 | 0.0422 -> 0.0092 |
| MM/SRtopology | coarse (53 cells) | asymmetry | 0.1514 +/- 0.0005 -> 0.2245 +/- 0.0017 -> 0.2173 +/- 0.0014 | 0.1850 -> 0.0194 |
| MM/SRtopology | coarse (53 cells) | dphi | 2.7942 +/- 0.0014 -> 2.5792 +/- 0.0054 -> 2.5690 +/- 0.0045 | 0.2225 -> 0.0239 |
| MM/SRtopology | coarse (53 cells) | pt1 | 266.6339 +/- 0.4028 -> 336.8141 +/- 1.3579 -> 335.6778 +/- 1.1112 | 0.2787 -> 0.0251 |
| MM/SRtopology | coarse (53 cells) | pt2 | 198.8840 +/- 0.3524 -> 216.3628 +/- 1.1292 -> 218.6880 +/- 0.9619 | 0.1073 -> 0.0230 |
| MM/SRtopology | fine (187 cells) | asymmetry | 0.1514 +/- 0.0005 -> 0.2235 +/- 0.0017 -> 0.2173 +/- 0.0014 | 0.1850 -> 0.0186 |
| MM/SRtopology | fine (187 cells) | dphi | 2.7942 +/- 0.0014 -> 2.5821 +/- 0.0055 -> 2.5690 +/- 0.0045 | 0.2225 -> 0.0278 |
| MM/SRtopology | fine (187 cells) | pt1 | 266.6339 +/- 0.4028 -> 337.6088 +/- 1.3531 -> 335.6778 +/- 1.1112 | 0.2787 -> 0.0216 |
| MM/SRtopology | fine (187 cells) | pt2 | 198.8840 +/- 0.3524 -> 217.6088 +/- 1.1425 -> 218.6880 +/- 0.9619 | 0.1073 -> 0.0167 |
