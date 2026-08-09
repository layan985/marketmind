# MarketMind adoption roadmap

MarketMind's next development phase is **adoption over feature accumulation**.

The project already has an installable package, CI, documentation, a DOI-backed archived release, a public replication challenge, and a preregistered prospective validation. The next publication-quality evidence must therefore come from people other than the primary author.

## Six-month scorecard

Target window: **9 August 2026 through 9 February 2027**.

| Target | Goal | Counting rule |
| --- | ---: | --- |
| External researchers who install/use MarketMind | **5** | Distinct non-author users with a public issue, research repository, notebook, report, citation, or other verifiable research-use record. |
| Non-author GitHub issues | **3+** | Issues opened by accounts other than `layan985`; author-created tracking issues do not count. |
| External PR/contributor | **1+** | A substantive PR from a non-author account that is reviewed and merged. |
| Independent technical reproduction | **1** | Fresh-environment reproduction with release/commit, environment, commands, and outcome publicly recorded. |
| Paper/preprint/research object using MarketMind | **1+** | A public research object that actually uses MarketMind and identifies the software version/DOI. |
| Conference/demo presentation | **1** | Public event record plus slides, notebook, video, or other durable evidence. |
| Public releases | **v0.2 -> v0.3** | Releases should respond to research-use evidence, audit findings, or API maturation; do not release merely to inflate version count. |
| JOSS | **2027 target** | Submit only after the public-history, research-impact, documentation, testing, and open-development gates are genuinely satisfied. |

## Evidence policy

Do not count private praise, package-page views, GitHub stars, self-opened issues, self-authored test repositories, or unverified statements as external adoption.

Prefer evidence that an editor or reviewer could independently inspect:

- a non-author issue or pull request;
- a public reproduction report;
- a repository or notebook importing MarketMind;
- a paper/preprint citing the software DOI or release;
- archived slides or a recorded research demo;
- a public integration into another research workflow.

Null findings, failed installations, numerical discrepancies, API confusion, and critical feedback are valid adoption evidence. They should remain visible and be resolved transparently.

## What not to optimize for

Until this scorecard has real external movement, do **not** prioritize additional estimators simply because they are interesting. New scientific functionality should require at least one of:

1. an external user need;
2. a reproduction/audit finding;
3. a clearly documented methodological gap that blocks a research use case;
4. a preregistered scientific requirement.

The default answer to an unrequested feature should be: document it in the backlog, then keep working on adoption.

## Phase 1 — make first use trivial

**9 August–7 September 2026**

Deliverables:

- keep `pip install marketmind` and `marketmind demo --output artifacts/demo` as the canonical first-use path;
- route independent attempts through `REPLICATION_CHALLENGE.md` and the external-replication issue template;
- add a research-use report template so external researchers can document real use without pretending it is a bug;
- maintain a small set of contribution-sized tasks that can be completed without understanding the entire package;
- personally recruit a first cohort of researchers/students to attempt installation and report what happened.

Success gate: at least **2 external install/use attempts** and **1 non-author issue**.

## Phase 2 — independent reproduction before more claims

**8 September–7 October 2026**

Goal: close publication gate #4 with an actual outside attempt.

Required record:

- MarketMind release or commit;
- Python/platform environment;
- exact commands;
- output hashes or numerical comparison where applicable;
- every ambiguity or failure encountered;
- linked fixes, if fixes are needed.

Success gate: **1 independent technical reproduction report**.

## Phase 3 — v0.2 is a user-driven release

**8 October–7 November 2026**

`v0.2.0` should be the first release whose notes can truthfully say it incorporates findings from external use or independent reproduction.

Preferred changes:

- installation/documentation fixes surfaced by outsiders;
- API clarification;
- stronger reference tests;
- reproducible research examples;
- error messages and diagnostics;
- provenance improvements.

Avoid unrelated feature expansion.

Success gate: **v0.2.0 released**, with release notes linking the public evidence that motivated material changes.

## Phase 4 — earn an external contributor

**8 November–7 December 2026**

Create contribution opportunities that are scientifically meaningful but bounded:

- add one independent estimator reference fixture;
- improve one documented research example;
- add one data/provenance edge-case test;
- improve one API/documentation path discovered during external use;
- reproduce one expected behavior with an independent implementation.

Review external work seriously: request tests and evidence where needed, credit the contributor, and keep the discussion public.

Success gate: **1 merged non-author PR**.

## Phase 5 — research use, not just software use

**8 December 2026–7 January 2027**

At least one external user should move beyond `pip install` into a research object:

- methods notebook;
- replication repository;
- working paper or preprint;
- teaching/research exercise;
- dataset analysis;
- conference demonstration.

The object should record the MarketMind release/commit and cite the software DOI where appropriate.

Success gate: **1 public research object using MarketMind** and **5 cumulative external users**.

## Phase 6 — v0.3 and JOSS readiness audit

**8 January–9 February 2027**

`v0.3.0` should consolidate the public development period and external feedback.

Before any JOSS submission, audit the repository against current JOSS requirements and review criteria. At minimum verify:

- more than six months of public development history;
- development activity distributed across that period rather than concentrated in an initial repository dump;
- public releases/version tags;
- public issues and pull requests;
- ideally, visible external engagement;
- demonstrated research use/impact rather than hypothetical future usefulness;
- complete installation and functionality documentation;
- automated tests and CI;
- clear statement of need, limitations, license, contribution process, and citation metadata;
- software-paper draft that describes evidence actually present in the repository.

If those gates are not met, delay submission. A later strong JOSS paper is more valuable than an early desk rejection.

## Public adoption ledger

Record only evidence that already exists.

| Date | Person/project | Evidence type | Public link | MarketMind version | Result | Counts toward |
| --- | --- | --- | --- | --- | --- | --- |
| _none yet_ |  |  |  |  |  |  |

When an entry becomes real, replace the placeholder row and link the underlying public record.

## Release doctrine

### v0.2.0 — reproducible research release
Release after the first meaningful external install/reproduction feedback has been incorporated.

### v0.3.0 — externally exercised release
Release after the package has accumulated visible third-party use, at least one external contribution or audit-driven change, and a stronger research-use example set.

### JOSS — publication, not validation theater
A JOSS submission should summarize a development and adoption record that already happened. It must never be used to create the appearance of research impact that the repository does not yet contain.
