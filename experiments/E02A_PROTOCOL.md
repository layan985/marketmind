# Last Price E02-A — Open-Model Validation Protocol

Frozen before execution on 2026-08-10.

## Question
Holding the consumer, product, seller, information set, bargaining rules, and random seed fixed, does changing only the buyer model change (1) whether an efficient trade completes and (2) the transaction price conditional on trade?

## Treatments
Buyer models:
- `qwen3:1.7b`
- `gemma3:4b`
- `llama3.2:3b`

Seller model: `qwen3:4b` in every bargaining cell.

The workflow records Ollama's resolved local model IDs in every artifact. No model substitution is allowed after results are observed.

## Products
Three goods with fixed economic primitives:

| product | reference price | buyer value/budget | baseline seller cost |
|---|---:|---:|---:|
| headphones | 200 | 250 | 120 |
| carry-on suitcase | 140 | 180 | 85 |
| ergonomic desk chair | 320 | 400 | 195 |

The shock state raises seller cost by exactly 10% and changes no buyer primitive.

## Randomization / matching
For each buyer × product combination, five seeds are run. The same seed is used for the baseline and +10% cost-shock member of a matched pair. Buyer moves first. Maximum negotiation length is six actions.

Full E02-A grid:

`3 buyer models × 3 products × 5 seeds × 2 cost states × 2 market mechanisms = 180 episodes`

The two mechanisms are bilateral bargaining and a posted-price negative control.

## Primary outcomes
1. Agreement probability / efficient-trade completion.
2. Transaction price conditional on agreement.

Agreement and price must always be reported together. A lower observed price is not treated as an improvement if it is purchased through trade destruction.

## Secondary outcomes
- buyer surplus
- seller profit
- invalid structured actions
- negotiation length
- matched +10% cost-shock pass-through / experienced inflation where both members of the pair trade

Malformed or invalid actions remain in the data as model behavior. Infrastructure failures are recorded separately and are not converted into negotiation failures.

## Negative control
In posted-price cells the transaction price is mechanically fixed at `1.2 × seller cost`. Conditional on agreement, price dispersion across buyer models must therefore be zero within each product × cost state. A non-zero range is a release blocker.

## Analysis committed before execution
- Report raw counts and rates by buyer model.
- Pairwise buyer-model agreement comparisons use matched cells and an exact McNemar/binomial test on discordant pairs; Holm correction across the three pairwise comparisons.
- Conditional-price comparisons use only cells where both compared models trade; report matched mean price difference and the number of common-trade cells. Do not infer a price advantage from selection into trade.
- Cost-shock pass-through is computed only for buyer × product × seed pairs that trade in both baseline and shock states.
- Report invalid-action rate separately; do not silently repair malformed behavior.
- Do not describe this 180-episode validation as the preregistered 72,000-episode confirmatory benchmark.

## Falsification / failure conditions
E02-A does not support a buyer-model price effect if prices are indistinguishable conditional on common trades. It does not support an experienced-inflation comparison for a model without matched baseline/shock trades. If posted-price conditional price dispersion is non-zero, the run fails audit.
