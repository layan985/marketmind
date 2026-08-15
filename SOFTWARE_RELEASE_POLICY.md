# MarketMind Software Release Policy

## Release object

Every public release must identify version/tag, commit, release date, environment contract, test state, benchmark state, data/proxy changes, methodology changes, assumption-register changes, known failures, compatibility notes and artifact hashes where applicable.

## Evidence boundary

A software release may establish implementation state. It does not by itself establish external validity, independent reproduction, research use, profitability or prospective performance.

## Required checks

Before release:

1. run the documented source test suite;
2. run the controlled leakage/perturbation checks required by the release scope;
3. regenerate frozen benchmark artifacts affected by code changes;
4. compare material result hashes or documented expected outputs;
5. update the assumption and negative-results registers when relevant;
6. update changelog and migration notes;
7. verify that sealed prospective results remain sealed.

## Versioning

Breaking methodological or API changes require a version change that makes the change discoverable. Corrections that materially alter a published result must not silently overwrite the prior research record.

## Failed release check

A failed required check blocks release unless the failure is explicitly scoped, documented and the release is clearly marked as non-confirmatory/development. Known failures are published rather than removed from the record.
