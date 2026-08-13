# Proof Ledger

MarketMind separates award/publication records, implementation evidence, controlled tests, public-data substitutions, prospective evidence, and outside reproduction. The prospective holdout remains sealed until its registered end.

## Evidence badges

`REAL PUBLIC DATA` — externally published public data or public record.  
`CLIENT DATA` — real client data, if a future diagnostic is approved for disclosure.  
`PROVIDER TEST` — not currently a core MarketMind evidence class.  
`SYNTHETIC` — generated market data or known-structure simulations.  
`RANDOMIZED SYNTHETIC` — randomized synthetic experiment when used.  
`EXTERNALLY VERIFIED` — an external record or independent rerun.  
`FOUNDER PRODUCED` — implementation, analysis, tests, or artifacts produced in this repository.  
`PENDING VALIDATION` — outcome not yet observed, independently rerun, or externally used.

## Ledger

| Claim | Number | Evidence type | Source | Date | Code | Reproducible? | Limitation | Status |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| Frozen preregistration release | v0.1.0 | `FOUNDER PRODUCED` | `README.md`; Zenodo DOI 10.5281/zenodo.21844956 | frozen before holdout | tagged release / package | Yes | Later software releases do not alter the registered freeze | Frozen |
| Current controlled research implementation | v0.2.0 | `FOUNDER PRODUCED` | `README.md`; `RELEASE_NOTES_v0.2.0.md` | 2026-08-13 status | package source | Yes | Not the frozen preregistration release | Current implementation |
| CI source tests | 29 passing | `FOUNDER PRODUCED` | `README.md`; CI workflow | 2026-08-13 | test suite | Yes | Test coverage is not economic validation | Passing |
| Branch-aware coverage | 83.06% | `FOUNDER PRODUCED` | `README.md`; test environment | 2026-08-13 | test suite | Yes in matching environment | Coverage does not imply model truth | Passing |
| Controlled research audit | 7 / 7 checks | `FOUNDER PRODUCED` | `validation/audit-v0.2.0/AUDIT.md`; `README.md` | 2026-08-13 | `marketmind audit` | Yes | Controlled implementation evidence, not profitability evidence | Passing |
| Connectivity metrics vs disclosed trailing latent coherence | 0.879–0.901 correlation | `SYNTHETIC` `FOUNDER PRODUCED` | audit report / verification snapshot | 2026-08-13 | audit code | Yes | Known-structure validation only | Passing |
| Earlier raw metric change after future-only perturbation | 0.0 max absolute difference | `SYNTHETIC` `FOUNDER PRODUCED` | audit report / verification snapshot | 2026-08-13 | audit code | Yes | Tests leakage resistance for this perturbation design | Passing |
| Earlier regime rows changed after future-only perturbation | 0 / 350 | `SYNTHETIC` `FOUNDER PRODUCED` | audit report / verification snapshot | 2026-08-13 | audit code | Yes | Does not exhaust all possible leakage mechanisms | Passing |
| Known source→target minus reverse transfer entropy | +1.218 nats | `SYNTHETIC` `FOUNDER PRODUCED` | audit report / verification snapshot | 2026-08-13 | audit code | Yes | Known-structure directional-information test | Passing |
| Same-session confirmatory position | 0.0 | `FOUNDER PRODUCED` | audit report / executable study contract | 2026-08-13 | study engine | Yes | Verifies execution timing, not performance | Passing |
| Hash-verified result files | 4 / 4 | `FOUNDER PRODUCED` | audit report | 2026-08-13 | artifact integrity checks | Yes | Integrity does not establish external validity | Passing |
| Prospective holdout start | 10 Aug 2026 | `EXTERNALLY VERIFIED` `FOUNDER PRODUCED` | OSF registration + repository preregistration | 2026-08-10 | registered config | Yes | Outcome remains sealed | Active |
| Prospective holdout end | 6 Aug 2027 | `EXTERNALLY VERIFIED` `FOUNDER PRODUCED` | OSF registration + repository preregistration | registered before holdout | registered config | Yes | Future end date | Active |
| Prospective holdout result | 0 results available | `PENDING VALIDATION` | `RESULTS.md`; `README.md` | 2026-08-13 | registered study engine | Not yet | Interim outcome must not be exposed | Sealed |
| Independent reproductions | 0 | `PENDING VALIDATION` | `README.md`; `REPLICATION_CHALLENGE.md` | 2026-08-13 | N/A | N/A | Outside rerun required | Open zero |
| Outside research uses | 0 recorded | `PENDING VALIDATION` | `README.md` | 2026-08-13 | N/A | N/A | GitHub traffic/stars do not count | Open zero |
| Exact numerical reproduction of paper with redistributable data | 0 | `PENDING VALIDATION` | `README.md`; `REPRODUCIBILITY.md` | 2026-08-13 | public-data config | Partly | Bloomberg/Refinitiv histories cannot be redistributed | Not claimed |
| Public-data substitute pipeline | available | `REAL PUBLIC DATA` `FOUNDER PRODUCED` | `config/paper-public.yml`; data adapter | 2026-08-13 | package adapters | Yes subject to source availability | Public proxies differ from paper inputs | Available |
| Award record for underlying paper | 2026 Charles H. Dow Award | `EXTERNALLY VERIFIED` | CMT Association award record linked in README | 2026 | N/A | External record | Award validates recognition, not prospective performance | Verified |

## Public terminal rule

A research-terminal interface should expose the analytical path:

**choose market → choose window → memory → information flow → connectivity → regime → uncertainty → diagnostics → export report**

It must never collapse those measurements into an unexplained trading signal. Every visual should expose:

**SOURCE / N / WINDOW / FILTER / STATUS / LIMITATION / DOWNLOAD DATA**

The landing surface should make the sealed status impossible to miss:

**AWARD-WINNING THEORY. OPEN IMPLEMENTATION. FROZEN PROSPECTIVE TEST.**
