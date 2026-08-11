# E05 provenance note

E05 ran from GitHub Actions run `31439894595` on branch `last-price-e05-trade-welfare-replication-20260811`.

The trigger commit was:

`8a0da87fb8a6799af7a96bd866750b9aefc023fa`

GitHub records its parent as:

`842245fd31f0d44214826ac6d1279b69d86b5af1`

That parent matches `frozen_commit` in `experiments/E05_FREEZE.json`.

All 27 matrix jobs completed successfully. The preregistered aggregate analysis also completed successfully and printed:

`{"blockers": [], "rows": 702, "technical_gate_pass": true}`

The workflow was nevertheless marked failed because the later **Add freeze evidence** step executed `git rev-parse HEAD^` after the aggregate job had checked out the repository with the default shallow depth of 1. The parent object was therefore absent from that runner's local checkout. The aggregate report had already been produced, and the aggregate artifact was subsequently uploaded successfully.

This is an archival workflow defect, not an inference failure. E05 is not rerun. The workflow definition is corrected after the experiment so future archival steps fetch the parent commit, while the original run and frozen outputs remain unchanged.
