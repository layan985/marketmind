# MarketMind replication program

The replication track is separate from the package's own empirical claims. Its purpose is to demonstrate that MarketMind can be used to independently reconstruct published computational results and to document where results are sensitive to implementation, sample, costs, or market regime.

## Candidate study families

Prefer papers with public or reconstructable data and a computational claim that maps cleanly to MarketMind:

1. financial-network topology from correlation matrices and minimum spanning trees;
2. Hurst/fractal persistence in market returns;
3. information-theoretic dependence or transfer entropy across financial assets;
4. technical-indicator performance under regime conditioning.

## Selection criteria

A replication target must satisfy all of the following:

- the original scientific claim is precise enough to test;
- the sample and transformations can be reconstructed lawfully;
- the primary result can be expressed as a table, statistic, or figure;
- an independent implementation is possible without copying the authors' code line-for-line;
- negative or discrepant findings can be reported without reframing them as success.

## Protocol

For each target:

1. freeze a citation and exact claim;
2. write a protocol before examining the final replicated outcome;
3. rebuild the data pipeline independently;
4. reproduce the original specification as closely as possible;
5. quantify numerical agreement/disagreement;
6. run predeclared sensitivity checks;
7. add realistic transaction costs only as a clearly separated extension when the original claim is trading-related;
8. archive code, configuration, data manifest and output hashes;
9. prepare a replication report suitable for an open computational-reproducibility venue.

## Report structure

- Original claim
- Reproduction environment
- Data reconstruction
- Independent implementation
- Primary replication result
- Discrepancies
- Sensitivity / robustness
- Limitations
- Reproducibility instructions

## Evidence policy

A failed replication is not a failed project. Do not tune the implementation until the published result appears. Preserve discrepancies and explain only those supported by evidence.
