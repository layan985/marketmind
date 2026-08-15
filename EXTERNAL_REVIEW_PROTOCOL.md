# MarketMind External Review Protocol

## Scope

External review is a bounded technical critique of a defined release, method, benchmark, experiment, data treatment or research claim. It is not an honorary advisory title and it is not equivalent to independent reproduction.

## Review request

The request must identify the exact object under review, the questions the reviewer is being asked to attack, the relevant version/commit, and any conflicts or prior collaboration.

## Preferred review modes

- methodological review of one estimator, diagnostic or validation decision;
- code review of a defined implementation surface;
- benchmark design review;
- data/proxy and measurement review;
- prospective-governance review;
- falsification/red-team review.

## Review record

A publishable review record contains:

`review_id` · `reviewer` · `date` · `object` · `version/commit` · `scope` · `conflicts` · `questions` · `findings` · `severity` · `author_response` · `changes` · `unresolved_items` · `publication_permission`

Reviewer identity is published only with permission. A private review may still be recorded as completed if the existence and scope can legitimately be disclosed, but anonymous praise is never converted into a named endorsement.

## Severity

Use: `INFORMATIONAL`, `MINOR`, `MATERIAL`, `CRITICAL`.

Material and critical findings must link to an issue, correction, release note, methodology change or explicit decision not to change with rationale.

## Evidence label

Only a completed outside review record meeting this protocol may carry `EXTERNAL REVIEW`. Review does not imply that results reproduced independently.
