# MarketMind Independent Replication Protocol

## Purpose

An independent reproduction tests whether an outside researcher can rebuild a frozen MarketMind result without relying on the original author's working environment or undocumented intervention. Internal reruns never satisfy this protocol.

## Eligible reproducer

The reproducer must be outside the author/maintainer role for the target release. Prior discussion is permitted, but all assistance that could affect the result should be logged.

## Frozen target

Before the rerun begins, record the target release/tag or commit, target result/artifact, data version or generator, configuration, expected hash where applicable, documented environment and the exact success criterion.

## Clean-environment procedure

1. Begin from a clean environment or container/VM.
2. Follow only the public installation and reproduction instructions initially.
3. Record every failure, ambiguity, dependency mismatch and undocumented assumption.
4. If maintainer help is required, timestamp the question and answer.
5. Re-run from a clean state after any material documentation or code correction.

## Report

The reproduction record must contain:

`reproduction_id` · `reproducer` · `date` · `target_version` · `target_commit` · `environment` · `data/artifact_hashes` · `commands` · `deviations` · `observed_outputs` · `comparison` · `failures` · `maintainer_assistance` · `conclusion`

## Conclusions

Use one of: `REPRODUCED`, `REPRODUCED_WITH_DOCUMENTED_DEVIATION`, `PARTIALLY_REPRODUCED`, `NOT_REPRODUCED`, `BLOCKED`.

A failed independent reproduction is not removed. It triggers a correction, issue, documentation change or release note as appropriate and remains part of the validation history.

## Evidence label

Only a completed outside record meeting this protocol may carry `INDEPENDENT REPRODUCTION`.
