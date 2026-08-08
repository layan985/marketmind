# Scholarly infrastructure

This repository is part of a persistent scholarly identity and research-output system for **Layan Oraidi**.

## Canonical researcher identity

- **Name:** Layan Oraidi
- **ORCID:** https://orcid.org/0009-0005-0202-2582
- **GitHub:** https://github.com/layan985

The canonical scholarly name is **Layan Oraidi**. External identifiers must only be added after they have actually been issued. Do not publish placeholder DOI, SSRN, OSF, or Google Scholar identifiers.

The identity graph is:

1. ORCID identifies the researcher.
2. DOIs identify immutable research outputs.
3. GitHub records the living development history.
4. PyPI distributes installable software.
5. Zenodo archives versioned software and datasets.
6. OSF records preregistrations and research protocols.
7. SSRN distributes economics/finance working papers where appropriate.
8. Google Scholar indexes publications and citations.
9. The personal website acts as the canonical human-readable index.

## Research-output graph

MarketMind should be represented as separate but related research objects:

- **Paper:** *The Emergent Market Mind: Detecting Self-Organizing Intelligence in Financial Markets Through Multiscale Information Networks*.
- **Software:** *MarketMind: Multiscale Market Intelligence Research Software*.
- **Dataset:** *MarketMind Historical Market-Regime Dataset*.
- **Preregistration:** prospective out-of-sample MarketMind validation.
- **Methods output:** a citable methods paper/report describing the open framework and reproducibility protocol.

The paper DOI, software DOI, dataset DOI, and preregistration DOI must remain distinct. Each object should cross-link to the others with related identifiers.

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
- `codemeta.json`.

As new DOI-bearing software, dataset, preregistration, and publications are issued, add them to the ORCID record and cross-link them back to this repository and the canonical personal website. Prefer trusted DOI imports over duplicate manual records.

## Release chain

For stable software versions:

`GitHub tag -> GitHub Release -> Zenodo archive -> version DOI -> ORCID -> website`

For datasets:

`reproducible pipeline -> frozen dataset files -> codebook/data dictionary -> provenance -> changelog -> Zenodo dataset deposit -> dataset DOI -> ORCID -> website`

For preregistration:

`frozen protocol -> OSF public registration -> registration DOI -> ORCID -> paper/software cross-links`

## No identifier fabrication

A DOI must never be guessed, pre-filled, or represented as real before issuance. Metadata files should be updated immediately after the corresponding service returns the identifier.
