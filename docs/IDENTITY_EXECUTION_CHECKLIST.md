# Scholarly Identity Execution Checklist

Canonical researcher: **Layan Oraidi**  
ORCID: **0009-0005-0202-2582**  
GitHub: **https://github.com/layan985**

This checklist is the operational path from a collection of projects to a persistent, machine-readable scholarly identity. Never invent an identifier. Only mark a step complete after the service has actually issued or verified the identifier.

## 1. ORCID — canonical researcher identity

Go to: https://orcid.org/my-orcid

### Record settings
- [ ] Published name: **Layan Oraidi**
- [ ] ORCID iD: **0009-0005-0202-2582**
- [ ] Add current education affiliation using the official institution entry.
- [ ] Add GitHub under Websites & social links: `https://github.com/layan985`
- [ ] Add the personal research website only after it is live and verified.
- [ ] Keep at least one backup email on the account.

### Add MarketMind software
In **Works → +Add → Add work with a DOI**, enter:

`10.5281/zenodo.21844956`

Verify before saving:
- Title: **MarketMind: Multiscale Market Intelligence Research Software**
- Type: software
- Creator/author: **Layan Oraidi**
- Version: **0.1.0**
- Year: **2026**
- Visibility: public

Do not manually create duplicate records if a trusted DOI import already exists.

### Later ORCID additions
- [ ] MarketMind v0.1.1 DOI once issued
- [ ] MarketMind dataset DOI once issued
- [ ] OSF registration DOI once verified
- [ ] *The Emergent Market Mind* publication DOI once issued
- [ ] JOSS paper DOI if/when accepted

## 2. GitHub → Zenodo release chain

Existing archived scientific release:
- **v0.1.0**
- DOI: **10.5281/zenodo.21844956**
- This is the version frozen in the prospective preregistration.

Current source metadata identifies a later **0.1.1** maintenance/open-science state. Do not change the preregistration to 0.1.1.

### Publish v0.1.1
- [ ] Open `https://github.com/layan985/marketmind/releases/new`
- [ ] Create tag: `v0.1.1`
- [ ] Target: `main`
- [ ] Release title: **MarketMind 0.1.1 — Preregistered Validation Infrastructure**
- [ ] Paste the body from `RELEASE_NOTES_v0.1.1.md`
- [ ] Mark as a normal release, not a prerelease
- [ ] Publish release

### Archive v0.1.1 in Zenodo
Go to: https://zenodo.org/account/settings/github/

- [ ] Confirm `layan985/marketmind` is enabled in the Zenodo GitHub integration.
- [ ] Wait until Zenodo processes the new GitHub release.
- [ ] Open the generated Zenodo record.
- [ ] Copy the **v0.1.1 version DOI** exactly as issued.
- [ ] Record the concept DOI too if Zenodo exposes it.
- [ ] Add the new DOI to Issue #13 and to the repository metadata.

Important: `.zenodo.json` is authoritative for GitHub-triggered Zenodo deposits when it is present. Keep it synchronized with the release metadata.

## 3. OSF preregistration DOI

Registration: **https://osf.io/nyseh/overview**  
Associated project: **https://osf.io/649gj**

The registration is a frozen scientific object. Do not edit its scientific plan to match later results.

- [ ] Open the registration while signed in.
- [ ] Open **Metadata**.
- [ ] Find the full DOI / registration number.
- [ ] Copy the DOI exactly as displayed.
- [ ] Confirm the registration is public.
- [ ] Add the DOI to GitHub Issue #1.
- [ ] Add the DOI to `CITATION.cff`, `.zenodo.json`, `research-graph.json`, README, ORCID and the personal site.

Do not infer a DOI from the OSF ID. Use only the DOI shown by OSF.

## 4. RePEc Author Service

Register at: https://authors.repec.org/script/new-user

The registration is six steps: introduction, name variations, affiliations, research works, confirmation email, ready.

### Step 1 fields
- First/given: **Layan**
- Last/family: **Oraidi**
- Do not use titles.
- Homepage: leave blank unless the personal research site is already live.
- Use an email you will retain long-term.

### Name variations
Only add forms actually used on real scholarly outputs. Examples may include:
- Layan Oraidi
- L. Oraidi

Do not create artificial variants to widen search matching.

### Affiliations
Use the real current university/institution and the real dates.

### Research works
Claim only genuine RePEc-indexed works authored by you. RePEc Author Service does not accept direct document uploads; works must already exist in the RePEc bibliographic database.

After confirmation:
- [ ] Copy the permanent **RePEc Short-ID**.
- [ ] Add it to Issue #12.
- [ ] Add the RePEc profile to the personal site and `research-graph.json`.

If a genuine economics working paper is not indexed by RePEc, use an appropriate RePEc-participating repository rather than inventing an entry.

## 5. Google Scholar profile

Start at: https://scholar.google.com/citations

- [ ] Create/confirm profile under **Layan Oraidi**.
- [ ] Use the real affiliation.
- [ ] Add genuine scholarly works only.
- [ ] Merge duplicate versions of the same work.
- [ ] Set article updates to require review until the profile is stable.
- [ ] Make the profile public.
- [ ] Add the personal research website once live.
- [ ] Copy the final public profile URL into Issue #10 and `research-graph.json`.

Do not add award pages, GitHub repos, or non-scholarly web pages as fake publications.

## 6. SSRN

Start at: https://papers.ssrn.com/

- [ ] Create/confirm author account under **Layan Oraidi**.
- [ ] Submit only complete working papers/preprints you have the right to post.
- [ ] Keep paper titles identical across SSRN, ORCID, website and CV.
- [ ] Use the canonical ORCID where SSRN permits it.
- [ ] When a paper receives a journal DOI, cross-link the published version rather than creating misleading duplicate titles.
- [ ] Record the verified SSRN author URL in Issue #10 and `research-graph.json`.

## 7. Personal research website

Target canonical domain: **layanoraidi.com** only after live verification.

Required sections:
- [ ] Research bio
- [ ] Papers / working papers
- [ ] Software
- [ ] Datasets
- [ ] Preregistrations
- [ ] Awards
- [ ] Talks
- [ ] CV
- [ ] Contact
- [ ] ORCID / GitHub / Scholar / RePEc / SSRN links

Machine-readable layer:
- [ ] schema.org `Person` JSON-LD
- [ ] `sameAs` entries only for verified profiles
- [ ] `ScholarlyArticle` metadata for papers
- [ ] `SoftwareSourceCode` metadata for software
- [ ] `Dataset` metadata for datasets
- [ ] public `research-graph.json`
- [ ] BibTeX export

## 8. MarketMind dataset DOI

Tracked in Issues #8 and #11.

Do not mint a dataset DOI until real derived dataset files, provenance, codebook, data dictionary, configuration and checksums are frozen.

Target title: **MarketMind Historical Market-Regime Dataset**  
Target version: **1.0.0**

- [ ] Generate derived files from the reproducible public proxy pipeline.
- [ ] Freeze checksums and metadata.
- [ ] Deposit as a Zenodo **Dataset**, not as software.
- [ ] Copy the issued dataset DOI.
- [ ] Cross-link software DOI, preregistration and associated paper.
- [ ] Import dataset DOI into ORCID.

## 9. JOSS — later, not immediately

JOSS is a peer-reviewed journal for research software. MarketMind is conceptually in-scope, but JOSS currently expects a meaningful public development history and feature-complete research software.

Do not rush a submission merely for another line on the CV.

Before submission:
- [ ] Public development history is mature enough for JOSS eligibility.
- [ ] External reproduction/audit in Issue #4 is completed.
- [ ] Documentation is complete.
- [ ] Automated tests pass.
- [ ] Installation works in a clean environment.
- [ ] Contribution and governance paths are clear.
- [ ] Software has an OSI-approved license.
- [ ] A concise JOSS paper exists in the required format.
- [ ] Any required AI-use disclosure is accurate.

If accepted, record the JOSS Crossref DOI as a separate scholarly object. Never replace the Zenodo software DOI with the JOSS article DOI.

## 10. Canonical identity graph

The target relationship is:

`ORCID → personal site → papers → software → datasets → Zenodo DOIs → OSF preregistration → RePEc → Google Scholar → SSRN → citations/talks/CV`

For MarketMind specifically:

`Layan Oraidi (ORCID)`
`  → The Emergent Market Mind (paper)`
`  → MarketMind (software)`
`      → GitHub`
`      → PyPI`
`      → Zenodo v0.1.0 DOI`
`      → later software-version DOIs`
`      → OSF prospective preregistration`
`      → MarketMind dataset DOI`
`      → eventual JOSS article`

## Immediate order of operations

Do these account-side actions in this exact order:

1. [ ] Add MarketMind DOI `10.5281/zenodo.21844956` to ORCID.
2. [ ] Check OSF Metadata and copy the real registration DOI.
3. [ ] Publish GitHub release `v0.1.1`.
4. [ ] Capture the new Zenodo v0.1.1 DOI.
5. [ ] Register RePEc and capture the Short-ID.
6. [ ] Create/clean Google Scholar and capture the public profile URL.
7. [ ] Create/clean SSRN and capture the author URL.
8. [ ] Finish and verify the canonical personal site.
9. [ ] Generate and publish the historical dataset only when real files are frozen.
10. [ ] Build external users/contributors and accumulate public development history before JOSS submission.

When a new identifier is issued, immediately propagate it to:

`ORCID + README + CITATION.cff + .zenodo.json + codemeta.json + research-graph.json + personal site + CV`
