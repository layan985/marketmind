# MarketMind External Replication Challenge

MarketMind should not be considered reproducible because its author says so. This challenge invites independent researchers, students, and developers to try to reproduce a public result and report what happens — including discrepancies.

## Challenge 01 — deterministic demo

Target release: **MarketMind v0.1.0**  
Archived release: **https://doi.org/10.5281/zenodo.21844956**

Install the public package and run the offline deterministic demonstration:

```bash
python -m pip install marketmind
marketmind demo --output artifacts/demo
```

The command writes the synthetic input, provenance manifest, raw and normalized metrics, MII states, and exact run configuration. Record the package version, Python version, platform, commands, generated hashes, and any numerical differences.

## Challenge 02 — clean repository run

```bash
git clone https://github.com/layan985/marketmind.git
cd marketmind
python -m pip install -e ".[all]"
pytest
marketmind demo --output artifacts/demo
```

If you reproduce the run successfully, report the success. If you do not, report the discrepancy. Both outcomes are useful evidence.

## How to report

Open a GitHub issue using the **External replication report** template. State exactly what you attempted, the release or commit, environment, commands, outcome, hashes/numerical comparisons, and the smallest reproducible discrepancy if one exists.

Replication reports will be treated as evidence, not testimonials. A successful independent report should be linkable from the public research portfolio. A failed report should remain public until the discrepancy is understood and documented.

## Scope

The deterministic demo and synthetic/public-data workflows are reproducible without proprietary data. The award paper used licensed Bloomberg and Refinitiv histories that cannot be redistributed; public proxy pipelines therefore test the method, not byte-for-byte equality with those licensed inputs.
