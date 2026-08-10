# Last Price E04 — Independent Trade-Formation and Welfare Replication

## Status
Preregistered before execution on 2026-08-10.

## Relationship to E03
E03 was designed as the first confirmatory trade-formation/welfare experiment, but its preregistered technical gate did not open: two Gemma × suitcase jobs failed before bargaining because the Ollama model registry returned HTTP 503 during model download. The E03 frozen aggregate therefore did not adjudicate P1 or P2.

E04 is **not** a completion of those two missing E03 cells. It is a new independent replication that reruns the complete 702-episode scientific grid from scratch using fresh matched seeds.

No E03 partial-panel outcome statistic is used to tune E04. E04 keeps the same scientific design, action menus, primary outcomes, hypothesis tests, and technical gate as E03.

## Infrastructure changes fixed before execution
Only execution reliability changes:
- fresh E04 seeds for every bargaining block;
- 27 buyer × product × tightness jobs, 26 episodes each;
- maximum 6 jobs in parallel rather than 9;
- model downloads may be retried up to 5 times with deterministic increasing sleeps before inference begins;
- setup status is written to the cell artifact directory before model pulls, so a setup failure remains auditable.

Model-download retries are infrastructure retries only. Once episode generation begins, there are no episode retries, substitutions, repairs, or reruns.

## Models
Buyer models:
- qwen3:1.7b (`qwen17`)
- gemma3:4b (`gemma4`)
- llama3.2:3b (`llama3`)

Fixed seller model:
- qwen3:4b

Exact Ollama tags and modelfiles are captured in each successful cell artifact.

## Products
- wireless noise-cancelling headphones
- durable carry-on suitcase
- ergonomic desk chair

Buyer values, budgets, and reference prices are inherited unchanged from the E02/E03 series.

## Finite feasible action mechanism
E04 uses the identical E03 finite-action mechanism.

At every turn the harness constructs a finite menu of economically legal actions. The model returns only a menu ID. A free-form model-generated number can never become an executable offer or transaction price.

Buyer offers:
- 40%, 45%, 50%, ..., 100% of the buyer's private budget.

Seller offers:
- 100%, 105%, 110%, ..., 160% of the seller's private marginal cost.

When the public reference price is hidden, neither actor's offer menu depends on the reference price.

Non-price actions:
- walk_away always available;
- reject available when an outstanding offer exists;
- accept available only when the outstanding offer satisfies the actor's private feasibility constraint;
- posted-price episodes allow only accept or walk_away.

## Experimental grid
For each buyer-model × product × tightness job:
- tightness: loose, medium, tight;
- seller cost: baseline and +10% shock;
- public reference price: shown or hidden;
- move order: buyer first or seller first;
- 3 fresh matched E04 seeds;
- posted-price control under both cost states.

Each of 27 jobs contains:
- 24 bargaining episodes;
- 2 posted-price episodes;
- 26 episodes total.

Planned sample:
- 648 bargaining episodes;
- 54 posted-price controls;
- 702 total episodes.

## Primary outcome P1 — trade formation
Binary agreement in bargaining episodes.

Matched block:
product × tightness × state × anchor × move order × seed index.

Expected complete matched blocks: 216.

Confirmatory test:
- two-sided Cochran's Q across the three related buyer-model outcomes.

No universal directional ordering is preregistered.

## Primary outcome P2 — realized buyer welfare
For every bargaining episode:

`normalized_realized_buyer_surplus = I(trade) * (buyer_value - final_price) / buyer_value`

No trade contributes zero.

Confirmatory test:
- two-sided Friedman repeated-measures test across the three buyer models on the 216 matched bargaining blocks.

## Familywise error control
Holm correction is applied jointly across P1 and P2.

## Prespecified pairwise decompositions
Only after omnibus tests:
- agreement: exact two-sided McNemar tests for Qwen–Gemma, Qwen–Llama, Gemma–Llama;
- welfare: paired two-sided Wilcoxon signed-rank tests for the same three pairs;
- Holm correction separately within each three-test family.

Pairwise tests decompose the omnibus tests and do not replace P1/P2.

## Prespecified model × product heterogeneity
Report:
- agreement rate by buyer model × product;
- normalized realized buyer surplus by buyer model × product;
- matched pairwise agreement differences by product;
- matched pairwise welfare differences by product.

Secondary fixed-block regressions estimate buyer-model main effects plus buyer-model × product interactions for agreement and normalized realized buyer welfare, with standard errors clustered by matched block.

These interaction tests are secondary, not part of the P1/P2 confirmatory gate.

## Secondary outcomes
- conditional normalized transaction price;
- buyer surplus;
- seller profit;
- total realized surplus;
- trade destruction;
- move-order effects;
- public-reference effects;
- shock effects;
- tightness effects;
- turns;
- token usage and latency.

Conditional price remains secondary because E02-E falsified the earlier primary conditional-price claims under finite feasible actions.

## Technical gate
The confirmatory gate opens only if all are true:
- exactly 27 source cell files;
- exactly 702 episodes;
- exactly 648 bargaining episodes and 54 posted controls;
- zero duplicate episode IDs;
- zero infrastructure failures in episode rows;
- zero invalid finite-menu choices;
- zero menu-reconstruction mismatches;
- zero realized bargaining prices above buyer budget;
- zero realized bargaining prices below seller cost;
- posted-price conditional transaction prices have zero cross-model range within product × tightness × state cells;
- all 216 matched bargaining blocks contain exactly the three preregistered buyer models.

If the technical gate fails, P1/P2 are reported as not adjudicated. Missing cells are not imputed and failed inference cells are not rerun.

## Confirmatory substantive gate
Pass only if:
1. the technical gate passes; and
2. at least one of P1 or P2 has Holm-adjusted p <= 0.05.

Both outcomes are reported regardless of significance.

## Interpretation boundary
E04 is an open-weight local-inference experiment with artificial bargaining agents. A positive result supports only the narrow claim that algorithmic representation can affect trade formation and/or realized buyer welfare in this controlled environment. It does not establish a universal model ranking, effects for proprietary commercial models, or effects for human consumers.
