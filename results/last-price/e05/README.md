# Last Price E05 — archived frozen result

E05 is an independent replication of the frozen E04 trade-formation and buyer-welfare design. The experiment ran 27 buyer × product × tightness jobs, 26 episodes per job, for 702 episodes in total.

## Result

The technical gate passed with no blockers. All 27 source cells were present, all 702 episodes were recovered, all 216 matched bargaining blocks were complete, and the finite-action feasibility checks passed.

The two preregistered confirmatory outcomes were both significant after Holm correction:

- **Trade formation (P1):** Cochran Q = 118.768, df = 2, Holm p = 1.62127e-26.
- **Realized buyer welfare (P2):** Friedman statistic = 192.147, df = 2, Holm p = 3.77508e-42.

Agreement rates were 18.06% for Qwen 3 1.7B, 15.28% for Gemma 3 4B, and 56.48% for Llama 3.2 3B. Mean unconditional normalized realized buyer surplus was 0.0125, 0.0000, and 0.1340 respectively.

The result supports the narrow experimental claim that **changing the model representing an otherwise fixed buyer can materially change both whether trade occurs and the buyer's realized welfare in this finite-action bargaining environment**. It does not establish a universal ranking of models or effects for human consumers.

## Frozen identity

- Experiment: `last-price-e05-trade-welfare-replication-20260811`
- Original run: `31439894595`
- Trigger commit: `8a0da87fb8a6799af7a96bd866750b9aefc023fa`
- Frozen parent commit: `842245fd31f0d44214826ac6d1279b69d86b5af1`
- Original aggregate artifact SHA-256: `4e74a748a8046ea64ac9ed205b002b0828a5a271727f416c610b0b5641a26491`

## Files

- `E05_REPORT.md` — frozen aggregate report produced by the preregistered analysis.
- `audit_summary.json` — compact audit and confirmatory statistics.
- `data/episodes.csv.gz.b64.part01` through `part05` — the complete 702-row aggregate episode CSV, gzip-compressed, Base64-encoded, and split into five ordered text chunks for a compact repository archive.
- `PROVENANCE.md` — run identity, the post-analysis workflow error, and why it does not alter the result.
- `RESULTS_SECTION.md` — paper-ready results text.
- `figures/agreement_rate.svg` — agreement-rate figure.
- `figures/buyer_welfare.svg` — realized-welfare figure.
- `MANIFEST.sha256` — integrity hashes for the archived data and original artifact.

Reconstruct the complete CSV from a checkout of this archive with:

```bash
cat data/episodes.csv.gz.b64.part* | tr -d '\n' | base64 -d | gunzip > episodes.csv
```

Integrity targets:

- decoded gzip SHA-256: `7c47f8fd8baccc0de1dcaeeb53c823816db23df1a83f1169a1fec668d241d8c5`
- reconstructed `episodes.csv` SHA-256: `1efa9666846f4e58318ce56fa145f01daad652549f220ddd9a9c93b7c1dfa1fd`

The five GitHub data blobs were checked against the Git object hashes calculated directly from the source chunks before this archive was pinned.

The original E05 run is not rerun or repaired. This directory is a post-run archive of the outputs produced by that run.
