# mll-only OS -> SS reweighting: mlljj closure

Resolved DY MC only; nJet>=2, passResolved, mlljj>800. Raw charge, no tightCharge requirement.
Independent random half for training T(mll)=SS/OS, half for validation; no data used.
All shapes normalized to unit area in the displayed region. No extra mlljj reweighting.
Shape covariance includes training-factor correlations between mlljj bins and unit-area normalization.
Gaussian chi2 uses only bins with SS effective entries >=10; low-stat results are descriptive.
Last mlljj bin includes overflow >=8000 GeV. Nominal DY corrections are the primary result; noDY is a crosscheck.

| mode | target | channel | region | mll chi2/ndf (p) | mlljj before (p) | mlljj after (p) | predicted/SS yield |
|---|---|---|---|---|---|---|---|
| nominal | prompt_singleflip | EE | inclusive | 42.48/33 (0.125) | 156.35/8 (9.27e-30) | 151.84/8 (8.09e-29) | 0.974 +/- 0.021 |
| nominal | prompt_singleflip | EE | Zwindow | 16.87/14 (0.263) | 133.93/8 (4.34e-25) | 133.33/8 (5.76e-25) | 0.970 +/- 0.023 |
| nominal | prompt_singleflip | EE | sideband | 14.57/11 (0.203) | 25.40/7 (0.000644) | 25.33/7 (0.000664) | 1.047 +/- 0.056 |
| nominal | prompt_singleflip | EE | SR | 9.66/6 (0.14) | 13.10/7 (0.0698) | 10.91/7 (0.142) | 0.922 +/- 0.082 |

A successful mll check alone does not imply mlljj closure. A failure after successful mll validation rejects this mll-only OS kernel at the tested binning/statistics.
This tests the conditional mlljj shape of 2-jet OS vs SS. It does not construct a second jet from a 1-jet event or validate a 1j->2j transfer.
prompt_singleflip requires both leptons matched to prompt/tau-origin gen leptons with gen OS; OS has zero flips and SS exactly one flip.
reco_all uses the full reconstructed DY OS/SS populations, including unmatched or nonprompt leptons.
