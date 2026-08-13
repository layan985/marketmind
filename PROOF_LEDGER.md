# MarketMind Proof Ledger

MarketMind separates controlled implementation evidence, known-structure synthetic tests, public-source substitutions, external records, independent reproduction and prospective evidence. The prospective holdout remains sealed until its registered end.

## Canonical evidence labels

`OFFICIAL SOURCE` · `REAL PUBLIC DATA` · `PROVIDER TEST` · `SYNTHETIC` · `RANDOMIZED SYNTHETIC` · `PRODUCTION CLIENT DATA` · `EXTERNAL REVIEW` · `INDEPENDENT REPRODUCTION` · `PENDING VALIDATION`

No alternative public badge vocabulary is used. Internal implementation evidence is described in the source/code/status columns rather than promoted into a separate evidence class.

## Ledger

| Claim | Number | Evidence label | Source | Date | Code / record | Reproducible? | Limitation | Status |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| Frozen preregistration release | v0.1.0 | `OFFICIAL SOURCE` | Zenodo DOI `10.5281/zenodo.21844956`; repository release | frozen before holdout | tagged release / package | Yes | Later software releases do not alter the registered freeze | Frozen |
| Current controlled implementation | v0.2.0 | `PENDING VALIDATION` | `README.md`; `RELEASE_NOTES_v0.2.0.md` | 2026-08-13 | package source | Yes | Current implementation is not itself external validation | Current implementation |
| CI source tests | 29 passing | `PENDING VALIDATION` | CI workflow / repository test suite | 2026-08-13 | tests | Yes | Test passing is implementation evidence, not economic validation | Passing |
| Branch-aware coverage | 83.06% | `PENDING VALIDATION` | test environment / coverage output | 2026-08-13 | tests | Yes in matching environment | Coverage does not establish model truth or profitability | Passing |
| Controlled research audit | 7 / 7 checks | `PENDING VALIDATION` | `validation/audit-v0.2.0/AUDIT.md`; `docs/research-audit.md` | 2026-08-13 | `marketmind audit` | Yes | Controlled implementation evidence; not independent reproduction | Passing |
| Connectivity metrics vs disclosed trailing latent coherence | 0.879–0.901 correlation | `SYNTHETIC` | controlled audit / verification snapshot | 2026-08-13 | audit code | Yes | Known-structure validation only | Passing |
| Earlier raw metric change after future-only perturbation | 0.0 max absolute difference | `SYNTHETIC` | controlled audit / verification snapshot | 2026-08-13 | audit code | Yes | Tests this perturbation design, not every possible leakage mechanism | Passing |
| Earlier regime rows changed after future-only perturbation | 0 / 350 | `SYNTHETIC` | controlled audit / verification snapshot | 2026-08-13 | audit code | Yes | Does not exhaust all possible leakage mechanisms | Passing |
| Known source→target minus reverse transfer entropy | +1.218 nats | `SYNTHETIC` | controlled audit / verification snapshot | 2026-08-13 | audit code | Yes | Known-structure directional-information test, not real-market performance | Passing |
| Same-session confirmatory position | 0.0 | `PENDING VALIDATION` | audit report / executable study contract | 2026-08-13 | study engine | Yes | Verifies execution timing contract, not performance | Passing |
| Hash-verified result files | 4 / 4 | `PENDING VALIDATION` | controlled audit | 2026-08-13 | artifact integrity checks | Yes | Integrity does not establish external validity | Passing |
| Prospective holdout start | 10 Aug 2026 | `OFFICIAL SOURCE` | OSF registration + repository preregistration | 2026-08-10 | registered config | Yes | Registration verifies the study record, not its future result | Active |
| Prospective holdout end | 6 Aug 2027 | `OFFICIAL SOURCE` | OSF registration + repository preregistration | registered before holdout | registered config | Yes | Future end date | Active |
| Prospective holdout result | SEALED / 0 public results | `PENDING VALIDATION` | `RESULTS.md`; preregistration | 2026-08-13 | registered study engine | Not yet | Interim outcome must not be exposed | Sealed |
| Independent reproductions | 0 recorded | `PENDING VALIDATION` | `REPLICATION_CHALLENGE.md`; repository registry | 2026-08-13 | N/A | N/A | Outside rerun required; internal reruns do not count | Open zero |
| External methodological/code reviews | 0 recorded as completed reviews | `PENDING VALIDATION` | public validation registry | 2026-08-13 | N/A | N/A | Informal discussion is not a completed review | Open zero |
| Outside research uses | 0 recorded | `PENDING VALIDATION` | research-use registry | 2026-08-13 | N/A | N/A | Traffic, stars and clones do not count | Open zero |
| Exact numerical reproduction of paper with redistributable data | 0 | `PENDING VALIDATION` | `REPRODUCIBILITY.md` | 2026-08-13 | public-data config | Partly | Bloomberg/Refinitiv histories cannot be redistributed | Not claimed |
| Public-data substitute pipeline | available | `REAL PUBLIC DATA` | `config/paper-public.yml`; public adapters | 2026-08-13 | package adapters | Yes, subject to public-source availability | Public proxies differ from paper inputs | Available |
| Charles H. Dow Award record for underlying paper | 2026 winner | `OFFICIAL SOURCE` | CMT Association award record linked in README | 2026 | external award record | Independently checkable | Award is recognition, not validation of prospective performance | Verified record |
| Production client market dataset | 0 disclosed | `PENDING VALIDATION` | repository claim boundary | 2026-08-13 | N/A | N/A | No production client data is claimed | Open zero |

## Public terminal rule

The analytical path is:

**choose market → choose window → memory → information flow → connectivity → network structure → regime → uncertainty → diagnostics → validation → export report**

The terminal must never collapse those measurements into an unexplained trading signal. Every visual exposes:

**SOURCE / N / WINDOW / FILTER / STATUS / LIMITATION / DOWNLOAD DATA**

The landing surface must make the sealed status impossible to miss:

**AWARD-WINNING THEORY. OPEN IMPLEMENTATION. FROZEN PROSPECTIVE TEST.**

## What would falsify or materially weaken a claim?

- A clean rerun fails to reproduce a frozen controlled result under the documented environment/configuration.
- Future-only perturbation changes earlier outputs contrary to the study contract.
- A known-direction synthetic test fails under its pre-specified conditions.
- A reported artifact hash does not match the frozen result.
- A benchmark/cost comparison overturns a claimed incremental result under the exact comparison contract.
- The prospective study fails its registered criteria once the sealed holdout is legitimately opened.
- An `INDEPENDENT REPRODUCTION` or `EXTERNAL REVIEW` documents a material methodological or implementation error.

Failed tests are release evidence, not marketing defects to hide.
