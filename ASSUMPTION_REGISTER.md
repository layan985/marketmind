# Assumption Register

| ID | Assumption | Why it exists | Required sensitivity | Failure mode | Status |
| --- | --- | --- | --- | --- | --- |
| A-001 | MII component weights 0.35 / 0.40 / 0.25 | Frozen theoretical synthesis used by the originating framework | weight grid and component ablations | conclusion depends narrowly on one arbitrary weighting | active; sensitivity required |
| A-002 | 252-session estimation window | one-trading-year structural window | 126 / 252 / 504 where study permits | excessive turnover or estimator instability | active |
| A-003 | preceding-window regime thresholds | prevents future observations from defining past states | alternate trailing horizons and refresh frequencies | state labels unstable to modest threshold choices | active |
| A-004 | monthly threshold refresh | limits threshold churn while remaining causal | weekly / monthly / quarterly in exploratory work | conclusions depend on refresh timing | active |
| A-005 | Kraskov `k=3` | frozen information-estimator setting | `k=4`, `k=5`; known-answer synthetic systems | direction or magnitude unstable across defensible k | active |
| A-006 | correlation-derived network structure | interpretable dependence baseline | eigenvalue and alternative network summaries | network metrics are redundant or unstable | active |
| A-007 | public proxy panel represents a reproducible research panel | licensed paper histories cannot be redistributed | source-vintage and proxy sensitivity | public result is mistaken for exact paper reproduction | active; explicit limitation |
| A-008 | one-session execution lag | information available at t cannot earn same-session return | timing red-team tests | same-session exposure appears | frozen for prospective study |
| A-009 | 5 bps primary turnover cost | prespecified friction assumption | 0 / 5 / 10 / 25 bps | result exists only at implausibly favorable cost | frozen for prospective study |
| A-010 | one-year prospective horizon | feasible future sample without optional stopping | report realized observation count and power limitations | too few state observations for precise inference | frozen endpoint |

The register is not a defense of these assumptions. It is a map of where conclusions are allowed to fail.
