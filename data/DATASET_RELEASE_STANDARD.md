# Dataset release standard

## Dataset title

**MarketMind Historical Market-Regime Dataset**

This dataset must be deposited and cited as an independent research object, separate from the MarketMind software release and separate from the associated paper.

## Required release contents

Each public dataset release should contain:

- frozen data files for the release;
- `DATA_DICTIONARY.csv`;
- a human-readable codebook;
- provenance metadata;
- exact pipeline/configuration used to construct the release;
- checksums for distributed files;
- changelog/version notes;
- license and citation metadata;
- known limitations and source restrictions;
- related identifiers for the paper, software, and preregistration once those identifiers exist.

## Versioning

Use semantic versioning for material dataset changes:

- patch: documentation or metadata correction that does not change observations;
- minor: backward-compatible addition of observations, markets, or variables;
- major: methodological or schema change that can alter interpretation or break downstream use.

Never silently overwrite a previously cited release. A changed research object receives a new version.

## Provenance

For each source series record, where legally possible:

- provider;
- requested ticker/series identifier;
- requested start/end dates;
- field used;
- adjustment convention;
- trading-calendar handling;
- forward-fill or imputation rule;
- data retrieval date;
- content checksum;
- transformation history.

Licensed Bloomberg/Refinitiv observations used in the original paper must not be redistributed when the license prohibits redistribution. Public proxy releases must be labelled as methodological replications rather than bit-for-bit reproductions.

## Citation target

Once Zenodo issues the first dataset DOI, replace this section with the exact version-specific citation and preserve the concept DOI separately.

Do not reuse the software DOI as the dataset DOI.

## Update schedule

The intended maintenance policy is versioned rather than silent continuous editing. Historical releases remain immutable after DOI issuance; new observations or methodological changes are published as new releases with changelog entries.
