# Last Price E02-E — Finite Feasible Action Validation

## Status
Preregistered before execution on 2026-08-10.

## Purpose
E02-E is a falsification test for the Last Price buyer-model and public-anchor effects after E02-D showed that Ollama's JSON-Schema decoder did not reliably enforce numeric minimum constraints. E02-E removes model-generated numeric prices entirely from the executable action space.

## Core intervention
At every turn the harness constructs a finite menu of economically legal actions. The model returns only a menu ID. The harness, not the model, maps that ID to the corresponding action and price.

No free-form numeric price emitted by a model can become an offer or transaction price.

### Buyer offer menu
The buyer may offer only:
40%, 45%, 50%, ..., 100% of its own private budget.

These menu values depend only on the buyer's private budget, which is already available to the buyer.

### Seller offer menu
The seller may offer only:
100%, 105%, 110%, ..., 160% of its own private marginal cost.

These menu values depend only on the seller's private cost, which is already available to the seller.

### Hidden-anchor protection
The hidden-anchor condition does not use the product reference price to build either actor's offer menu. Therefore the finite menu does not leak the withheld public reference price.

### Non-price actions
- walk_away is always available.
- reject is available when an outstanding offer exists.
- accept is available only when the outstanding offer satisfies the actor's private feasibility constraint.
- posted-price episodes allow only accept or walk_away.

## Models
Buyer models:
- qwen3:1.7b
- gemma3:4b
- llama3.2:3b

Fixed seller model:
- qwen3:4b

The exact Ollama tags and modelfiles are captured in each cell artifact.

## Products
- wireless noise-cancelling headphones
- durable carry-on suitcase
- ergonomic desk chair

Product values, budgets, and reference prices are inherited unchanged from the prior E02 series.

## Experimental grid
For each buyer-model × product cell:
- 3 tightness regimes: loose, medium, tight
- 2 cost states: baseline, +10% shock
- 2 public-anchor states: shown, hidden
- 2 move orders: buyer first, seller first
- 3 matched seeds
- posted-price controls for every tightness × cost-state pair

Each cell contains 78 episodes.
Nine cells yield 702 episodes total.

Seeds preserve the E02-B/C/D matched seed function.

## Primary hypotheses

### P1: buyer-representation price effect
Among successful hidden-anchor, buyer-first negotiations matched on product, tightness, state, and seed:

Llama3.2 3B normalized transaction price minus Qwen3 1.7B normalized transaction price is negative.

### P2: differential public-anchor transmission
Let A_b be the within-model shown-minus-hidden normalized price effect among matched successful trades.

Primary contrast:

A_Llama - A_Qwen > 0.

## Primary statistical rule
- Wilcoxon signed-rank tests on matched contrasts.
- 5,000-draw deterministic bootstrap confidence intervals.
- Holm correction across P1 and P2.
- Statistical significance threshold: adjusted p <= 0.05.
- Directional robustness requires P1 negative in at least 2/3 products and P2 positive in at least 2/3 products.

## Technical gate
The technical gate passes only if all are true:
- 702 rows are present from exactly nine source files.
- zero duplicate episode IDs.
- zero infrastructure failures.
- zero invalid finite-menu choices.
- zero menu reconstruction mismatches.
- zero realized bargaining prices above buyer budget.
- zero realized bargaining prices below seller cost.
- posted-price conditional transaction prices have zero cross-model range.

Buyer-model disagreement about whether to accept a posted price is reported as a behavioral outcome and is not a technical failure, because the posted-price control identifies price formation, not preference/participation invariance.

## Substantive replication gate
Pass only if:
1. technical gate passes;
2. P1 is negative with Holm-adjusted p <= 0.05;
3. P2 is positive with Holm-adjusted p <= 0.05;
4. P1 has the predicted sign in at least 2/3 products;
5. P2 has the predicted sign in at least 2/3 products.

## Interpretation boundary
This is an open-weight local-inference validation. It can establish whether the E02-B/C/D pattern survives a mechanically finite feasible action space. It does not establish generalization to proprietary commercial models or real consumers.
