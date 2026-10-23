# JES_2024 likelihood scans (combine), v2 card

data-only = JES prior removed (JES as POI); with prior = data-only + theta^2. Width = half of the q-1 interval.
A 'with prior' width below 1 means the data constrains JES beyond its prior. '(edge)' = interval hits the scan range [-1, 9].

## EE card

| scan | data-only best | -err | +err | with prior best | -err | +err | q_prior(0) - min |
|---|---|---|---|---|---|---|---|
| full card (baseline) | **+5.55** | 0.95 | 0.95 | **+2.82** | 0.60 | 0.77 | 18.4 |
| - rDYMuMuCR_OS | **+5.83** | 1.10 | 1.11 | **+2.63** | 0.73 | 0.73 | 12.9 |
| - rDYEECR_OS | **+5.05** | 1.04 | 1.05 | **+2.43** | 0.73 | 0.69 | 11.4 |
| - rFlvCR | **+4.93** | 1.07 | 1.08 | **+2.43** | 0.82 | 0.62 | 10.6 |
| only rFlvCR + rDYEECR_OS + rDYMuMuCR_OS | **+6.53** | 1.09 | 1.10 | **+3.02** | 0.78 | 0.68 | 16.5 |
| only rDYMuMuCR_OS | **+5.66** | 1.55 | 1.32 | **+1.65** | 0.82 | 0.84 | 3.8 |
| only rDYEECR_OS | **+7.36** | 1.68 | 1.54 (edge) | **+1.84** | 0.79 | 0.93 | 4.9 |
| only rFlvCR | **+7.24** | 2.14 | 1.67 (edge) | **+1.25** | 1.00 | 0.85 | 1.6 |
| only SR channels (Asimov) | **-0.00** | 0.90 | 3.62 (edge) | **-0.00** | 0.90 | 0.95 | -0.0 |
| full, DY R bins 1-6 + MuonTrig frozen | **+6.53** | 0.83 | 0.84 | **+3.80** | 0.56 | 0.70 | 38.3 |
| full, every constrained nuisance frozen except JES | **+5.87** | 0.73 | 0.73 | **+3.80** | 0.58 | 0.61 | 42.4 |
| full + MassSlopeDY/TT | **+2.13** | 1.25 | 1.27 | **+0.86** | 0.80 | 0.74 | 1.1 |
| 3 resolved CRs + MassSlopeDY/TT | **+2.46** | 1.57 | 1.62 | **+0.67** | 0.89 | 0.89 | 0.7 |

## MM card

| scan | data-only best | -err | +err | with prior best | -err | +err | q_prior(0) - min |
|---|---|---|---|---|---|---|---|
| full card (baseline) | **+5.14** | 0.92 | 0.93 | **+2.82** | 0.75 | 0.60 | 16.7 |
| full + MassSlopeDY/TT | **+1.88** | 1.21 | 1.24 | **+0.86** | 0.90 | 0.66 | 0.9 |

## FitDiagnostics (b-only, CR data + SR Asimov): baseline vs + MassSlopeDY/TT

| param | EE base | EE +slope | MM base | MM +slope |
|---|---|---|---|---|
| JES_2024 | +2.91 ± nan | +0.84 ± nan | +2.75 ± nan | +0.78 ± nan |
| MassSlopeDY | - | +1.52 ± nan | - | +1.44 ± nan |
| MassSlopeTT | - | +1.61 ± nan | - | +1.39 ± nan |
| ResolvedDYReshapeBin2 | -1.25 ± nan | -0.24 ± nan | -1.28 ± nan | -0.29 ± nan |
| ResolvedDYReshapeBin4 | +2.41 ± nan | +0.53 ± nan | +2.41 ± nan | +0.58 ± nan |
| ResolvedDYReshapeBin5 | +1.13 ± nan | -0.19 ± nan | +1.06 ± nan | -0.22 ± nan |
| MuonTrig_2024 | +1.37 ± nan | +0.80 ± nan | +1.36 ± nan | +0.75 ± nan |
| OthersNorm_2024 | +0.72 ± nan | +1.02 ± nan | +0.16 ± nan | +0.30 ± nan |
| R_DY_Resolved_2024 | - | - | - | - |
| R_TT_Resolved_2024 | - | - | - | - |
| R_DY_Boosted_2024 | - | - | - | - |
| fit_status | 0 | 0 | 0 | 0 |
