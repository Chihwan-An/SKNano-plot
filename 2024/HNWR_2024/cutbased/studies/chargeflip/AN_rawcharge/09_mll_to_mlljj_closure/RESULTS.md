# mll-only OS -> SS reweighting: mlljj closure

Resolved DY MC only; nJet>=2, passResolved, mlljj>800. Raw charge, no tightCharge requirement.
Independent random half for training T(mll)=SS/OS, half for validation; no data used.
All shapes normalized to unit area in the displayed region. No extra mlljj reweighting.
Shape covariance includes training-factor correlations between mlljj bins and unit-area normalization.
Gaussian chi2 uses only bins with SS effective entries >=10; low-stat results are descriptive.
Last mlljj bin includes overflow >=8000 GeV. Nominal DY corrections are the primary result; noDY is a crosscheck.

| mode | target | channel | region | mll chi2/ndf (p) | mlljj before (p) | mlljj after (p) | predicted/SS yield |
|---|---|---|---|---|---|---|---|
| nominal | reco_all | EE | inclusive | 41.12/33 (0.157) | 163.44/8 (3.05e-31) | 153.24/8 (4.13e-29) | 1.023 +/- 0.021 |
| nominal | reco_all | EE | Zwindow | 16.70/15 (0.337) | 150.97/8 (1.23e-28) | 151.16/8 (1.12e-28) | 1.026 +/- 0.024 |
| nominal | reco_all | EE | sideband | 15.06/11 (0.18) | 6.19/8 (0.626) | 6.12/8 (0.634) | 0.943 +/- 0.053 |
| nominal | reco_all | EE | SR | 5.95/5 (0.311) | 5.59/7 (0.589) | 3.50/7 (0.835) | 1.144 +/- 0.103 |
| nominal | reco_all | MM | inclusive | 6.72/3 (0.0813) | 0.47/2 (0.791) | 0.83/2 (0.662) | 1.077 +/- 0.194 |
| nominal | reco_all | MM | Zwindow | 4.30/1 (0.038) | 0.09/1 (0.763) | 0.11/1 (0.743) | 0.912 +/- 0.279 |
| nominal | reco_all | MM | sideband | insufficient stats | 1.15/1 (0.284) | 1.15/1 (0.284) | 1.447 +/- 0.378 |
| nominal | reco_all | MM | SR | insufficient stats | insufficient stats | insufficient stats | 0.813 +/- 0.327 |
| nominal | prompt_singleflip | EE | inclusive | 44.38/35 (0.133) | 173.46/8 (2.43e-33) | 168.35/8 (2.85e-32) | 1.026 +/- 0.022 |
| nominal | prompt_singleflip | EE | Zwindow | 20.69/16 (0.191) | 157.13/8 (6.36e-30) | 157.30/8 (5.86e-30) | 1.030 +/- 0.024 |
| nominal | prompt_singleflip | EE | sideband | 14.59/11 (0.202) | 12.48/8 (0.131) | 12.41/8 (0.134) | 0.957 +/- 0.051 |
| nominal | prompt_singleflip | EE | SR | 7.44/6 (0.282) | 6.74/8 (0.565) | 4.50/8 (0.81) | 1.085 +/- 0.096 |
| nominal | prompt_singleflip | MM | inclusive | insufficient stats | insufficient stats | insufficient stats | 0.815 +/- 0.658 |
| nominal | prompt_singleflip | MM | Zwindow | insufficient stats | insufficient stats | insufficient stats | 0.817 +/- 0.667 |
| nominal | prompt_singleflip | MM | sideband | insufficient stats | insufficient stats | insufficient stats | empty validation target |
| nominal | prompt_singleflip | MM | SR | insufficient stats | insufficient stats | insufficient stats | 0.089 +/- 0.113 |
| noDY | reco_all | EE | inclusive | 44.26/35 (0.136) | 167.05/8 (5.35e-32) | 153.37/8 (3.88e-29) | 1.020 +/- 0.021 |
| noDY | reco_all | EE | Zwindow | 18.70/16 (0.284) | 154.03/8 (2.83e-29) | 154.06/8 (2.79e-29) | 1.022 +/- 0.023 |
| noDY | reco_all | EE | sideband | 14.04/11 (0.231) | 7.04/8 (0.533) | 6.91/8 (0.546) | 0.940 +/- 0.049 |
| noDY | reco_all | EE | SR | 8.22/6 (0.222) | 4.85/8 (0.773) | 3.04/8 (0.932) | 1.134 +/- 0.096 |
| noDY | reco_all | MM | inclusive | 6.43/3 (0.0924) | 0.36/3 (0.947) | 1.08/3 (0.782) | 1.069 +/- 0.183 |
| noDY | reco_all | MM | Zwindow | 4.35/1 (0.037) | 0.34/1 (0.561) | 0.41/1 (0.523) | 0.906 +/- 0.268 |
| noDY | reco_all | MM | sideband | insufficient stats | 1.19/1 (0.275) | 1.19/1 (0.275) | 1.389 +/- 0.343 |
| noDY | reco_all | MM | SR | insufficient stats | insufficient stats | insufficient stats | 0.858 +/- 0.316 |
| noDY | prompt_singleflip | EE | inclusive | 45.81/37 (0.152) | 177.15/8 (4.09e-34) | 170.71/8 (9.17e-33) | 1.022 +/- 0.021 |
| noDY | prompt_singleflip | EE | Zwindow | 21.40/16 (0.164) | 161.59/8 (7.44e-31) | 161.74/8 (6.93e-31) | 1.026 +/- 0.023 |
| noDY | prompt_singleflip | EE | sideband | 14.08/12 (0.296) | 13.46/8 (0.0969) | 13.34/8 (0.101) | 0.948 +/- 0.047 |
| noDY | prompt_singleflip | EE | SR | 8.19/7 (0.316) | 5.56/8 (0.696) | 3.46/8 (0.903) | 1.084 +/- 0.090 |
| noDY | prompt_singleflip | MM | inclusive | insufficient stats | insufficient stats | insufficient stats | 0.818 +/- 0.619 |
| noDY | prompt_singleflip | MM | Zwindow | insufficient stats | insufficient stats | insufficient stats | 0.821 +/- 0.634 |
| noDY | prompt_singleflip | MM | sideband | insufficient stats | insufficient stats | insufficient stats | empty validation target |
| noDY | prompt_singleflip | MM | SR | insufficient stats | insufficient stats | insufficient stats | 0.110 +/- 0.139 |

A successful mll check alone does not imply mlljj closure. A failure after successful mll validation rejects this mll-only OS kernel at the tested binning/statistics.
This tests the conditional mlljj shape of 2-jet OS vs SS. It does not construct a second jet from a 1-jet event or validate a 1j->2j transfer.
prompt_singleflip requires both leptons matched to prompt/tau-origin gen leptons with gen OS; OS has zero flips and SS exactly one flip.
reco_all uses the full reconstructed DY OS/SS populations, including unmatched or nonprompt leptons.
