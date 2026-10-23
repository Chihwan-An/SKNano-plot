# Charge-flip SF barrel-endcap closure systematic (2024, AN-style 2-region SF)

SF_B and SF_E are fitted from the pure BB / EE Z-peak categories (60-120 GeV); the mixed BE category is a prediction:
pred_SF(BE) = OS data x [SF_B P_B/(1-P_B) + SF_E P_E/(1-P_E)]. The deviation of obs(BE)/pred_SF(BE) from 1 is the systematic
(`FlipBEClosure_2024` lnN on the Flip process). N_Z estimators from `sf_roofit.json`; adopted: **roofit_full**.

| N_Z method | SF_B (BB) | SF_E (EE) | BE obs | BE pred (SF=1) | BE obs/pred (SF=1) | BE obs/pred_SF | lnN |
|---|---|---|---|---|---|---|---|
| count | 1.425 ± 0.042 | 1.450 ± 0.027 | 2623 ± 57 | 1806 | 1.453 ± 0.032 | **1.005 ± 0.022** | 1.005 |
| roofit_full (adopted) | 1.457 ± 0.038 | 1.468 ± 0.024 | 3071 ± 61 | 2051 | 1.497 ± 0.031 | **1.023 ± 0.021** | 1.023 |
| roofit_win | 1.454 ± 0.038 | 1.465 ± 0.024 | 2910 ± 58 | 1947 | 1.494 ± 0.031 | **1.023 ± 0.021** | 1.023 |

Adopted lnN = 1 + |obs/pred_SF - 1| = **1.023** (roofit_full); with the statistical error added in quadrature it would be 1.031.
The count method closes to 0.5 % (within its 2.2 % error); the RooFit N_Z gives 2.3 % (1.1 sigma). The larger RooFit value is taken as the systematic.
Applied in the cards as `--flip-lnn FlipBEClosure_2024=<lnN>` (scripts/cbv15_dc_cards.py), on the Flip process of rEESR_SS and rDYEECR_SS.
