# MarketMind 0.2.0 — Executable Study and Controlled Audit

MarketMind 0.2.0 turns the preregistered prospective design into an executable analysis
contract and adds a deterministic, reviewer-facing research audit. The estimators frozen
for the prospective holdout remain MarketMind 0.1.0; this release builds explicit study,
verification, and provenance layers around that frozen core.

## Executable prospective-study engine

- Constructs exactly three fixed signals per trend, breakout, and mean-reversion family.
- Applies the registered High MII → trend, Medium MII → breakout, Low MII → mean-reversion map.
- Executes candidate and comparator exposures with the same one-session lag and cost model.
- Implements paired synchronized moving-block Sharpe comparisons across markets for H1/H3.
- Implements the H2a–H2c mechanism contrasts with Holm family-wise correction.

## Controlled research audit

The command below writes a complete human- and machine-readable evidence pack and exits
nonzero if an acceptance rule fails:

```bash
marketmind audit --output artifacts/research-audit
```

The frozen v0.2.0 record passes 7/7 controlled checks: deterministic replay, recovery of
disclosed synthetic coherence, feature and threshold look-ahead perturbations, directional
information recovery, exact strategy selection and execution timing, and artifact integrity.

These checks validate controlled implementation behavior. They do not establish trading
profitability or reveal any interim result from the sealed 2026–2027 holdout.

## Provenance and quality

- Every MII result bundle now includes SHA-256 hashes and byte counts for its numerical files.
- Demo results are bound to the exact input fingerprint and data manifest.
- Package version metadata now has one source of truth.
- CI now runs tests, linting, strict type checking, static HTML validation, a controlled audit,
  strict documentation builds, and distribution validation.

## Public research surface

- New research dossier with the executable architecture, audit results, evidence boundaries,
  maturity matrix, and five-minute reviewer path.
- Prospective scoreboard updated to active / protocol frozen / outcomes sealed.
- Official CMT Association award record, OSF protocol, Zenodo DOI, source, and replication
  challenge are directly cross-linked.
