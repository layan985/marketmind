# Corrections and Retractions

A correction is issued when a public result remains interpretable but a material error, metadata defect, or provenance problem must be fixed. The original record remains traceable and the correction describes impact.

A result is retracted when the evidence artifact, computation, data rights, or methodological defect makes the original claim unreliable. Retraction status propagates to the machine-readable registry rather than leaving a stale headline claim live.

## Correction record: MM-RN-003 / LAB-002 — 18 August 2026

**Affected artifact:** `experiments/records/LAB-002_summary.csv` as first published in commit `d5066c58f584ec53912e054fe369de503afbb8dc`.

**Issue:** the five reported arm means reproduce exactly from the disclosed LAB-002 generator, but several medians, percentiles, extrema and exceedance fractions in the first summary file do not.

**Resolution:** MM-RN-003 v1.0 recomputes all secondary distribution statistics from the disclosed generator, publishes `LAB-002_runs.csv` for seeds 1000–1099, replaces the summary with reproducible values, and archives the publication snapshot under release reference `MM-RN-003-v1.0`.

**Impact on headline claim:** none. Mean annualized Sharpe remains 0.019143 for the causal control, 2.796394 for the centered-window arm and 21.016873 for same-session execution. The central inference is unchanged.

**Historical record:** the superseded file remains available through Git history and is not silently erased.
