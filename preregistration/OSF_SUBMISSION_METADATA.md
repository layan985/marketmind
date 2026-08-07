# OSF Submission Metadata — MarketMind Prospective Validation

Use this page when creating the public OSF registration. The canonical scientific content is `OSF_MARKETMIND_PROSPECTIVE_2026.md`.

## Registry/template

- Registry: OSF Registries
- Template: **OSF Preregistration** (standard comprehensive template)
- Visibility: **Make registration public immediately**
- Intended submission date: 7–9 August 2026, before the prospective window begins
- Prospective window begins: 10 August 2026

## Title

**Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis**

## Contributor

**Layan Oraidi**

Link the author's ORCID in OSF metadata if available at submission time. Do not invent an ORCID identifier.

## Description

This prospective study evaluates whether the Market Intelligence Index (MII), an information-theoretic regime measure combining market memory, information flow, and network connectivity, predicts which broad class of technical signal performs best out of sample. The preregistered mapping is High MII → trend-following, Medium MII → breakout/volatility expansion, and Low MII → mean reversion. The confirmatory sample is restricted to future observations from 10 August 2026 through 6 August 2027. The analysis uses frozen MarketMind 0.1.0 software, fixed signal definitions, causal regime classification, one-session execution lag, explicit transaction costs, prespecified bootstrap inference, and a public deviation log. Results will be reported regardless of whether the hypotheses are supported.

## Suggested subjects

Select the closest OSF subject terms available to:

- Economics
- Finance
- Econometrics
- Quantitative Methods
- Data Science / Computational Research

Exact OSF vocabulary may differ; choose the closest official terms rather than inventing categories.

## Tags

`market-regimes`, `technical-analysis`, `information-theory`, `financial-markets`, `marketmind`, `preregistration`, `out-of-sample`, `reproducibility`, `open-science`, `computational-finance`

## Related resources

- GitHub repository: `https://github.com/layan985/marketmind`
- Frozen software release: `marketmind==0.1.0`
- Frozen source commit: `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`
- Preregistration file: `preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md`
- Acquisition configuration: `config/preregistered-validation-2026.yml`
- Deviation log: `preregistration/DEVIATIONS.csv`
- Tracking issue: GitHub issue #1

## Registration answers

Copy the corresponding sections from `OSF_MARKETMIND_PROSPECTIVE_2026.md` into the standard OSF Preregistration fields. Preserve wording of the confirmatory hypotheses, sample dates, exclusions, cost assumptions, statistical tests, and robustness designation.

## Final submission checks

Before pressing Submit:

- [ ] Confirm the date is before 10 August 2026.
- [ ] Confirm the standard **OSF Preregistration** template is selected.
- [ ] Confirm the prospective evaluation dates are 2026-08-10 through 2027-08-06.
- [ ] Confirm MarketMind version is 0.1.0.
- [ ] Confirm frozen commit is `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`.
- [ ] Confirm H1 names the unconditional nine-signal ensemble as the primary comparator.
- [ ] Confirm primary transaction costs are 5 bps per unit turnover.
- [ ] Confirm the four primary markets are SPX, NDX, SX5E, and ES.
- [ ] Confirm the primary bootstrap block length is 20 and replications are 10,000.
- [ ] Confirm the seed is 20260807.
- [ ] Confirm H2a–H2c use Holm correction.
- [ ] Confirm null/adverse results will be reported.
- [ ] Select **Make registration public immediately** if the goal is an immediate public DOI.
- [ ] Submit/approve the registration.

## Immediately after OSF assigns the DOI

Record the following in the repository without altering the frozen scientific plan:

- OSF registration URL
- OSF DOI
- OSF registration date

Add those identifiers to the README, `CITATION.cff`, and GitHub issue #1. The DOI is metadata linking to the frozen registration; it must not be fabricated in advance.
