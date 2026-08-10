# Last Price E03 — Trade Formation and Realized Welfare

## Status
Preregistered before execution on 2026-08-10.

## Motivation
E02-E mechanically removed free-form numeric prices from the executable action space. In the complete Qwen/Llama panel, the earlier conditional-price hypotheses did not survive, while a large buyer-model difference in trade formation appeared. E03 is a new confirmatory experiment. It does not retroactively redefine E02-E.

E03 asks whether changing only the AI model representing an otherwise identical buyer changes:
1. whether mutually beneficial exchange occurs; and
2. the buyer's realized welfare once both agreement probability and transaction price are accounted for.

## Design invariants
E03 preserves E02-E's finite feasible action mechanism.

At every turn the harness constructs a finite menu of economically legal actions. The model returns only a menu ID. The harness maps that ID to an action and, where relevant, a price. A model-generated free-form number can never become an executable offer or transaction price.

### Buyer offer menu
The buyer may offer only:
40%, 45%, 50%, ..., 100% of its own private budget.

### Seller offer menu
The seller may offer only:
100%, 105%, 110%, ..., 160% of its own private marginal cost.

### Hidden-anchor protection
When the public reference price is hidden, neither actor's offer menu depends on that reference price.

### Non-price actions
- walk_away is always available.
- reject is available when an outstanding offer exists.
- accept is available only when the outstanding offer satisfies the actor's private feasibility constraint.
- posted-price episodes allow only accept or walk_away.

No silent repairs, substitutions, retries, or post-hoc reruns are allowed after execution begins.

## Models
Buyer models:
- qwen3:1.7b (`qwen17`)
- gemma3:4b (`gemma4`)
- llama3.2:3b (`llama3`)

Fixed seller model:
- qwen3:4b

Exact Ollama tags and modelfiles are captured in each cell artifact.

## Products
- wireless noise-cancelling headphones
- durable carry-on suitcase
- ergonomic desk chair

Buyer values, budgets, and reference prices are inherited unchanged from the E02 series.

## Experimental grid
For each buyer-model × product × tightness job:
- tightness: loose, medium, or tight
- cost states: baseline and +10% shock
- public reference price: shown or hidden
- move order: buyer first or seller first
- 3 matched seeds
- posted-price control for both cost states

Each job contains:
- 24 bargaining episodes
- 2 posted-price episodes
- 26 episodes total

There are 27 jobs:
3 buyer models × 3 products × 3 tightness regimes.

Total planned sample:
- 648 bargaining episodes
- 54 posted-price controls
- 702 episodes total

The 27-job execution split is an infrastructure change only. It replaces E02-E's 9 jobs of 78 episodes to reduce exposure to long-run GitHub runner shutdowns. The scientific grid is unchanged.

## Primary outcomes

### P1 — trade formation
Binary agreement in bargaining episodes.

The confirmatory null is that the three buyer models have equal agreement probabilities on matched bargaining blocks.

Matched block:
product × tightness × state × anchor × move order × seed.

Expected complete matched blocks: 216.

Primary test:
- Cochran's Q across the three related buyer-model outcomes.
- Two-sided.
- P1 is supported if Holm-adjusted p <= 0.05.

No directional ordering such as Llama > Qwen is preregistered as universal.

### P2 — realized buyer welfare
For every bargaining episode:

`normalized_realized_buyer_surplus = I(trade) * (buyer_value - final_price) / buyer_value`

No trade contributes zero. This is unconditional realized welfare: it combines the extensive margin of trade formation and the intensive margin of the price conditional on trade.

Primary test:
- Friedman repeated-measures test across the three buyer models on matched bargaining blocks.
- Two-sided.
- P2 is supported if Holm-adjusted p <= 0.05.

## Familywise error control
Holm correction is applied jointly across the two confirmatory omnibus p-values P1 and P2.

## Prespecified pairwise decompositions
Only after the omnibus tests are computed:
- Agreement: exact two-sided McNemar tests for Qwen–Gemma, Qwen–Llama, and Gemma–Llama.
- Buyer welfare: paired two-sided Wilcoxon signed-rank tests for the same three pairs.
- Holm correction is applied separately within each three-test pairwise family.
- Pairwise effect sizes are reported even if not significant.

These pairwise tests decompose the omnibus result; they are not substitutes for P1/P2.

## Prespecified model × product heterogeneity
The E02-E extensive-margin pattern reversed sign for chair, so product heterogeneity is prespecified rather than hidden.

E03 reports:
- agreement rate by buyer model × product;
- normalized realized buyer surplus by buyer model × product;
- pairwise matched agreement differences by product;
- pairwise matched welfare differences by product.

A secondary linear-probability model is estimated on bargaining rows:

`agreement ~ matched-block fixed effects + buyer-model main effects + buyer-model × product interactions`

with standard errors clustered by matched block.

An analogous OLS model is estimated for normalized realized buyer surplus.

The joint buyer-model × product interaction Wald tests are secondary. They are not part of the confirmatory P1/P2 gate.

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
- model token usage and latency.

Conditional-price results are secondary because E02-E falsified the earlier primary conditional-price claims under finite feasible actions.

## Technical gate
The confirmatory gate opens only if all are true:
- exactly 702 episodes are present;
- exactly 27 source cell files are present;
- exactly 648 bargaining episodes and 54 posted controls are present;
- zero duplicate episode IDs;
- zero infrastructure failures;
- zero invalid finite-menu choices;
- zero menu-reconstruction mismatches;
- zero realized bargaining prices above buyer budget;
- zero realized bargaining prices below seller cost;
- posted-price conditional transaction prices have zero cross-model range within product × tightness × state cells;
- all 216 bargaining matched blocks contain exactly the three preregistered buyer models.

If the technical gate fails, confirmatory P1/P2 are reported as not adjudicated. No failed or missing cell is silently rerun or imputed.

## Confirmatory substantive gate
Pass only if:
1. the technical gate passes; and
2. at least one of P1 or P2 has Holm-adjusted p <= 0.05.

The report must still show both outcomes, including nulls.

## Interpretation boundary
E03 is an open-weight local-inference experiment with artificial bargaining agents. A positive result supports the narrow claim that algorithmic representation can affect trade formation and/or realized buyer welfare in this controlled environment. It does not establish a universal model ranking, effects for proprietary commercial models, or effects for human consumers.
