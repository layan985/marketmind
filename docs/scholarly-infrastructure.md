# Scholarly infrastructure

This repository is part of a persistent scholarly identity and research-output system for **Layan Oraidi**.

## Canonical researcher identity

- **Name:** Layan Oraidi
- **ORCID:** https://orcid.org/0009-0005-0202-2582
- **GitHub:** https://github.com/layan985
- **Machine-readable graph:** `research-graph.json`

The canonical scholarly name is **Layan Oraidi**. External identifiers must only be added after they have actually been issued and verified. Do not publish placeholder DOI, RePEc, SSRN, OSF DOI, Google Scholar, or JOSS identifiers.

The identity graph is:

1. ORCID identifies the researcher.
2. DOIs identify immutable research outputs.
3. GitHub records the living development history.
4. PyPI distributes installable software.
5. Zenodo archives versioned software and datasets.
6. OSF records preregistrations and research protocols.
7. RePEc connects economics works to the author identity when indexed.
8. SSRN distributes economics/finance working papers where appropriate.
9. Google Scholar indexes publications and citations.
10. The personal website acts as the canonical human-readable index.

## Research-output graph

MarketMind is represented as separate but related research objects:

- **Paper:** *The Emergent Market Mind: Detecting Self-Organizing Intelligence in Financial Markets Through Multiscale Information Networks*.
- **Software:** *MarketMind: Multiscale Market Intelligence Research Software*.
- **Dataset:** *MarketMind Historical Market-Regime Dataset*.
- **Preregistration:** *Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis*.
- **Methods output:** a future citable methods paper/report describing the open framework and reproducibility protocol.

The paper DOI, software DOI, dataset DOI, preregistration DOI, and any future JOSS article DOI must remain distinct. Each object should cross-link to the others with related identifiers.

## Issued identifiers

### Researcher

- ORCID: **0009-0005-0202-2582**

### Software archive

- MarketMind archived release **v0.1.0**
- Zenodo record: https://zenodo.org/records/21844956
- Version DOI: **10.5281/zenodo.21844956**

This DOI identifies the archived v0.1.0 software release. It must not be reused for a dataset, paper, preregistration, or later software version.

### OSF

- Public registration URL: https://osf.io/nyseh/overview
- Associated project: https://osf.io/649gj
- Registration DOI: **not populated until publicly verified**

## Version discipline

The prospective 2026–2027 validation is scientifically frozen to **MarketMind 0.1.0** and the preregistration must continue to identify that version.

The repository source metadata currently identifies **0.1.1** as the current software-maintenance version and includes `RELEASE_NOTES_v0.1.1.md`. This does **not** alter the preregistered frozen implementation. A public v0.1.1 GitHub/Zenodo release should receive its own release tag and version DOI before it is treated as an archived release in the scholarly graph.

Accordingly:

- **0.1.0** = frozen preregistered implementation + archived Zenodo software release.
- **0.1.1** = later maintenance/open-science metadata state until separately released and archived.

## Metadata contract

Every DOI-bearing output should include, where applicable:

- Creator: Layan Oraidi
- ORCID: 0009-0005-0202-2582
- canonical title
- version
- release/publication date
- resource type
- abstract/description
- license
- repository URL
- DOI
- related paper/software/dataset/registration identifiers
- keywords
- citation text

## ORCID synchronization

The issued ORCID iD is **0009-0005-0202-2582** and is propagated to:

- `CITATION.cff`;
- `.zenodo.json` creator metadata;
- `codemeta.json`;
- `research-graph.json`.

As new DOI-bearing software, datasets, registrations, and publications are issued, add them to the ORCID record and cross-link them back to this repository and the canonical personal website. Prefer trusted DOI imports over duplicate manual records.

## Release chains

For stable software versions:

`GitHub tag -> GitHub Release -> Zenodo archive -> version DOI -> ORCID -> website`

The first completed software chain is:

`v0.1.0 -> Zenodo record 21844956 -> DOI 10.5281/zenodo.21844956`

For datasets:

`reproducible pipeline -> frozen dataset files -> codebook/data dictionary -> provenance -> changelog -> Zenodo dataset deposit -> dataset DOI -> ORCID -> website`

For preregistration:

`frozen protocol -> OSF public registration -> registration DOI when verified -> ORCID -> paper/software cross-links`

For discovery profiles:

`ORCID + DOI-bearing works -> RePEc / Google Scholar / SSRN -> verified profile URLs -> personal website + research-graph.json`

For a future JOSS submission:

`stable research software -> documentation -> tests -> external reproduction/audit -> archived software release -> JOSS submission -> JOSS article DOI -> ORCID + website`

## Tracking

- Issue #1: prospective validation and OSF DOI propagation.
- Issue #4: external reproduction/audit gate.
- Issue #8/#11: historical dataset DOI pipeline.
- Issue #10: Google Scholar and SSRN profiles.
- Issue #12: RePEc, personal site, broader research identity graph, and JOSS pipeline.

## No identifier fabrication

A DOI or profile identifier must never be guessed, pre-filled, or represented as real before issuance/verification. Metadata files should be updated immediately after the corresponding service returns the identifier.