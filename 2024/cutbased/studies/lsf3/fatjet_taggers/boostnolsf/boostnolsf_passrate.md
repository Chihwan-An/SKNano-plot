# BoostNoLSF: tagger pass rate in the boosted SR

Signal and background, 2024. The away fatjet is the first with |dPhi(lead lepton, J)| > 2.0 taken from the FULL
fatjet collection -- no LSF3 cut -- so the tagger scan replaces LSF3 rather than sitting on top of it.

Background groups follow plot/cutbased/config.py. The analyzer histograms are already normalised to 109.8 fb^-1, so each group is the plain sum of its samples.

## SR_Boosted_EE (XWWqqev)

| sample | SR yield (no cut) | LSF3 > 0.75 | same-rate cut | > 0.01 | > 0.1 | > 0.5 |
|---|---|---|---|---|---|---|
| W_R 1 TeV | 39668.72 | 97.3% | 1.83e-03 | 92.5% | 67.7% | 6.1% |
| W_R 2 TeV | 5266.75 | 96.3% | 6.80e-03 | 95.5% | 80.3% | 11.8% |
| W_R 3 TeV | 509.67 | 95.9% | 6.36e-03 | 94.9% | 78.0% | 10.8% |
| W_R 4 TeV | 55.01 | 95.2% | 7.12e-03 | 94.2% | 72.1% | 10.5% |
| W_R 5 TeV | 8.86 | 94.5% | 7.53e-03 | 93.8% | 71.5% | 10.7% |
| W_R 6 TeV | 2.47 | 95.4% | 5.82e-03 | 93.6% | 72.8% | 10.5% |
| W_R 7 TeV | 0.98 | 95.8% | 5.21e-03 | 93.5% | 73.5% | 10.5% |
| Drell-Yan | 172.75 | 95.5% | 1.85e-04 | 74.4% | 37.0% | 0.6% |
| $t\bar{t}$ + tW | 435.20 | 95.0% | 1.41e-05 | 24.0% | 9.8% | 0.3% |
| Nonprompt | 96.76 | 67.1% | 8.96e-05 | 13.9% | 3.1% | 0.1% |
| Others | 42.77 | 91.7% | 8.17e-05 | 58.1% | 33.6% | 1.8% |

At each signal's LSF3-equivalent tagger cut (the cut keeping the same signal fraction as LSF3 > 0.75), against LSF3 > 0.75 itself, which keeps 682.61 background events. The last two columns scan for the best cut instead, over the range where at least 1 background event survives (score < 0.50); past that the background MC is exhausted and S/sqrt(B) diverges on nothing. That maximum is shallow -- 'best cut' is the range staying within 1 % of it, not a single recommended value.

| sample | tagger cut | background kept | vs LSF3 > 0.75 | S/sqrt(B) tagger | S/sqrt(B) LSF3 | best cut | S/sqrt(B) best |
|---|---|---|---|---|---|---|---|
| W_R 1 TeV | 1.83e-03 | 365.72 | 0.54x | 2021.90 | 1478.01 | 0.06-0.12 | 2423.67 |
| W_R 2 TeV | 6.80e-03 | 292.79 | 0.43x | 296.96 | 194.08 | 0.18-0.22 | 416.09 |
| W_R 3 TeV | 6.36e-03 | 292.79 | 0.43x | 28.57 | 18.71 | 0.15-0.20 | 37.22 |
| W_R 4 TeV | 7.12e-03 | 289.30 | 0.42x | 3.09 | 2.01 | 0.15-0.20 | 3.66 |
| W_R 5 TeV | 7.53e-03 | 285.26 | 0.42x | 0.50 | 0.32 | 0.18-0.20 | 0.59 |
| W_R 6 TeV | 5.82e-03 | 302.18 | 0.44x | 0.14 | 0.09 | 0.16-0.20 | 0.17 |
| W_R 7 TeV | 5.21e-03 | 306.37 | 0.45x | 0.05 | 0.04 | 0.18-0.22 | 0.07 |

## SR_Boosted_EE (lsf3)

| sample | SR yield (no cut) | LSF3 > 0.75 | same-rate cut | > 0.01 | > 0.1 | > 0.5 |
|---|---|---|---|---|---|---|
| W_R 1 TeV | 39668.72 | 97.3% | 7.36e-01 | 100.0% | 99.9% | 99.6% |
| W_R 2 TeV | 5266.75 | 96.3% | 7.35e-01 | 100.0% | 100.0% | 99.0% |
| W_R 3 TeV | 509.67 | 95.9% | 7.35e-01 | 100.0% | 100.0% | 98.1% |
| W_R 4 TeV | 55.01 | 95.2% | 7.37e-01 | 100.0% | 99.9% | 97.5% |
| W_R 5 TeV | 8.86 | 94.5% | 7.35e-01 | 100.0% | 99.8% | 97.2% |
| W_R 6 TeV | 2.47 | 95.4% | 7.35e-01 | 100.0% | 99.7% | 97.7% |
| W_R 7 TeV | 0.98 | 95.8% | 7.36e-01 | 100.0% | 99.8% | 98.4% |
| Drell-Yan | 172.75 | 95.5% | 7.34e-01 | 100.0% | 100.0% | 99.6% |
| $t\bar{t}$ + tW | 435.20 | 95.0% | 7.37e-01 | 100.0% | 100.0% | 99.4% |
| Nonprompt | 96.76 | 67.1% | 7.35e-01 | 100.0% | 99.6% | 95.5% |
| Others | 42.77 | 91.7% | 7.35e-01 | 100.0% | 100.0% | 99.3% |

At each signal's LSF3-equivalent tagger cut (the cut keeping the same signal fraction as LSF3 > 0.75), against LSF3 > 0.75 itself, which keeps 682.61 background events. The last two columns scan for the best cut instead, over the range where at least 1 background event survives (score < 0.99); past that the background MC is exhausted and S/sqrt(B) diverges on nothing. That maximum is shallow -- 'best cut' is the range staying within 1 % of it, not a single recommended value.

| sample | tagger cut | background kept | vs LSF3 > 0.75 | S/sqrt(B) tagger | S/sqrt(B) LSF3 | best cut | S/sqrt(B) best |
|---|---|---|---|---|---|---|---|
| W_R 1 TeV | 7.36e-01 | 684.95 | 1.00x | 1478.12 | 1478.01 | 0.76-0.90 | 1494.64 |
| W_R 2 TeV | 7.35e-01 | 684.95 | 1.00x | 194.04 | 194.08 | 0.65-0.93 | 194.65 |
| W_R 3 TeV | 7.35e-01 | 684.95 | 1.00x | 18.69 | 18.71 | 0.71-0.86 | 18.83 |
| W_R 4 TeV | 7.37e-01 | 684.95 | 1.00x | 2.00 | 2.01 | 0.72-0.86 | 2.02 |
| W_R 5 TeV | 7.35e-01 | 684.95 | 1.00x | 0.32 | 0.32 | 0.00-0.20 | 0.32 |
| W_R 6 TeV | 7.35e-01 | 684.95 | 1.00x | 0.09 | 0.09 | 0.71-0.88 | 0.09 |
| W_R 7 TeV | 7.36e-01 | 684.95 | 1.00x | 0.04 | 0.04 | 0.69-0.91 | 0.04 |

## SR_Boosted_MM (XWWqqmv)

| sample | SR yield (no cut) | LSF3 > 0.75 | same-rate cut | > 0.01 | > 0.1 | > 0.5 |
|---|---|---|---|---|---|---|
| W_R 1 TeV | 44073.55 | 91.4% | 1.68e-02 | 94.4% | 73.0% | 9.0% |
| W_R 2 TeV | 6518.45 | 88.8% | 6.94e-02 | 96.8% | 86.2% | 19.3% |
| W_R 3 TeV | 825.48 | 89.4% | 6.75e-02 | 97.2% | 86.2% | 19.7% |
| W_R 4 TeV | 121.87 | 88.7% | 5.43e-02 | 96.8% | 82.9% | 20.5% |
| W_R 5 TeV | 23.32 | 88.7% | 4.88e-02 | 96.9% | 81.6% | 21.7% |
| W_R 6 TeV | 6.73 | 88.1% | 4.38e-02 | 96.5% | 79.8% | 22.3% |
| W_R 7 TeV | 2.37 | 87.9% | 3.37e-02 | 95.6% | 77.1% | 20.9% |
| Drell-Yan | 186.16 | 83.8% | 2.84e-03 | 76.9% | 40.6% | 1.0% |
| $t\bar{t}$ + tW | 667.03 | 70.6% | 6.35e-05 | 20.6% | 9.0% | 0.5% |
| Nonprompt | 513.31 | 9.9% | 2.80e-03 | 5.8% | 2.0% | 0.1% |
| Others | 57.64 | 55.8% | 2.25e-03 | 47.9% | 30.7% | 2.2% |

At each signal's LSF3-equivalent tagger cut (the cut keeping the same signal fraction as LSF3 > 0.75), against LSF3 > 0.75 itself, which keeps 709.83 background events. The last two columns scan for the best cut instead, over the range where at least 1 background event survives (score < 0.54); past that the background MC is exhausted and S/sqrt(B) diverges on nothing. That maximum is shallow -- 'best cut' is the range staying within 1 % of it, not a single recommended value.

| sample | tagger cut | background kept | vs LSF3 > 0.75 | S/sqrt(B) tagger | S/sqrt(B) LSF3 | best cut | S/sqrt(B) best |
|---|---|---|---|---|---|---|---|
| W_R 1 TeV | 1.68e-02 | 299.87 | 0.42x | 2335.29 | 1511.30 | 0.09-0.16 | 2526.24 |
| W_R 2 TeV | 6.94e-02 | 188.79 | 0.27x | 421.93 | 217.22 | 0.54-0.54 | 533.45 |
| W_R 3 TeV | 6.75e-02 | 194.42 | 0.27x | 53.26 | 27.69 | 0.54-0.54 | 72.50 |
| W_R 4 TeV | 5.43e-02 | 206.00 | 0.29x | 7.54 | 4.06 | 0.54-0.54 | 10.61 |
| W_R 5 TeV | 4.88e-02 | 217.06 | 0.31x | 1.41 | 0.78 | 0.54-0.54 | 2.14 |
| W_R 6 TeV | 4.38e-02 | 223.51 | 0.31x | 0.40 | 0.22 | 0.54-0.54 | 0.65 |
| W_R 7 TeV | 3.37e-02 | 248.35 | 0.35x | 0.13 | 0.08 | 0.54-0.54 | 0.23 |

## SR_Boosted_MM (lsf3)

| sample | SR yield (no cut) | LSF3 > 0.75 | same-rate cut | > 0.01 | > 0.1 | > 0.5 |
|---|---|---|---|---|---|---|
| W_R 1 TeV | 44073.55 | 91.4% | 7.34e-01 | 100.0% | 98.9% | 95.0% |
| W_R 2 TeV | 6518.45 | 88.8% | 7.35e-01 | 100.0% | 98.3% | 93.7% |
| W_R 3 TeV | 825.48 | 89.4% | 7.35e-01 | 100.0% | 98.6% | 94.2% |
| W_R 4 TeV | 121.87 | 88.7% | 7.36e-01 | 100.0% | 98.9% | 93.9% |
| W_R 5 TeV | 23.32 | 88.7% | 7.35e-01 | 100.0% | 98.9% | 93.4% |
| W_R 6 TeV | 6.73 | 88.1% | 7.36e-01 | 100.0% | 98.8% | 93.0% |
| W_R 7 TeV | 2.37 | 87.9% | 7.35e-01 | 100.0% | 98.9% | 92.9% |
| Drell-Yan | 186.16 | 83.8% | 7.34e-01 | 100.0% | 99.0% | 88.8% |
| $t\bar{t}$ + tW | 667.03 | 70.6% | 7.35e-01 | 100.0% | 98.2% | 81.0% |
| Nonprompt | 513.31 | 9.9% | 7.36e-01 | 100.0% | 97.7% | 36.5% |
| Others | 57.64 | 55.8% | 7.37e-01 | 100.0% | 98.4% | 69.4% |

At each signal's LSF3-equivalent tagger cut (the cut keeping the same signal fraction as LSF3 > 0.75), against LSF3 > 0.75 itself, which keeps 709.83 background events. The last two columns scan for the best cut instead, over the range where at least 1 background event survives (score < 0.99); past that the background MC is exhausted and S/sqrt(B) diverges on nothing. That maximum is shallow -- 'best cut' is the range staying within 1 % of it, not a single recommended value.

| sample | tagger cut | background kept | vs LSF3 > 0.75 | S/sqrt(B) tagger | S/sqrt(B) LSF3 | best cut | S/sqrt(B) best |
|---|---|---|---|---|---|---|---|
| W_R 1 TeV | 7.34e-01 | 713.67 | 1.01x | 1509.45 | 1511.30 | 0.78-0.90 | 1534.09 |
| W_R 2 TeV | 7.35e-01 | 713.67 | 1.01x | 217.09 | 217.22 | 0.68-0.86 | 217.51 |
| W_R 3 TeV | 7.35e-01 | 713.67 | 1.01x | 27.66 | 27.69 | 0.70-0.88 | 27.80 |
| W_R 4 TeV | 7.36e-01 | 713.67 | 1.01x | 4.06 | 4.06 | 0.68-0.88 | 4.07 |
| W_R 5 TeV | 7.35e-01 | 713.67 | 1.01x | 0.78 | 0.78 | 0.69-0.88 | 0.78 |
| W_R 6 TeV | 7.36e-01 | 713.67 | 1.01x | 0.22 | 0.22 | 0.69-0.89 | 0.22 |
| W_R 7 TeV | 7.35e-01 | 713.67 | 1.01x | 0.08 | 0.08 | 0.70-0.88 | 0.08 |

