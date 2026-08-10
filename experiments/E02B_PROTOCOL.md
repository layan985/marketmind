# Last Price E02-B Mechanism Test — Frozen Protocol

Freeze date: 2026-08-10

## Question

E02-A found a large transaction-price premium for Llama 3.2 3B relative to Qwen3 1.7B and Gemma 3 4B while all three buyers traded successfully. E02-B tests whether that result is explained by a supplied public reference-price anchor, move order, or bargaining tightness.

## Models

Buyer treatments:
- `qwen17` = `qwen3:1.7b`
- `gemma4` = `gemma3:4b`
- `llama3` = `llama3.2:3b`

Seller held fixed:
- `qwen3:4b`

All calls use Ollama local inference, JSON output, `think=false`, temperature `0.2`, max six agent turns, and deterministic numeric seeds.

## Economic primitives

Three product scales are retained from E02-A:

| product | reference price | buyer value | budget |
|---|---:|---:|---:|
| headphones | 200 | 250 | 250 |
| suitcase | 140 | 180 | 180 |
| chair | 320 | 400 | 400 |

The buyer value and budget are private. Seller cost is private.

## Mechanism factors

1. Public numerical anchor:
   - `shown`: the E02-A reference price is supplied to both agents.
   - `hidden`: no numerical reference price is supplied to either agent.

2. Move order:
   - `buyer_first`
   - `seller_first`

3. Surplus tightness:
   - `loose`: baseline seller cost = 0.45 × buyer value
   - `medium`: baseline seller cost = 0.65 × buyer value
   - `tight`: baseline seller cost = 0.85 × buyer value

4. Cost state:
   - `baseline`: multiplier 1.00
   - `shock_10pct`: multiplier 1.10

Even the tight shocked condition remains ex-ante efficient: seller cost = 0.935 × buyer value.

5. Replications:
   - 3 matched seed indices per bargaining cell.
   - Numeric seeds are matched across buyer model, anchor, move order, and cost state for the same product × tightness × seed index.

## Scale

Bargaining:
3 buyers × 3 products × 3 tightness levels × 2 anchor states × 2 move orders × 2 cost states × 3 seeds = 648 episodes.

Posted-price negative control:
3 buyers × 3 products × 3 tightness levels × 2 cost states × 1 seed = 54 episodes.

Total expected E02-B episodes = 702.

For the posted-price control, price is mechanically fixed at 1.04 × seller cost. This remains below buyer value even in the tight shocked condition. Buyer model can affect acceptance but cannot affect the posted transaction price.

## Frozen outcomes

Primary outcome: transaction price divided by public reference price, conditional on trade.

Co-primary outcome: agreement probability.

Secondary outcomes: buyer surplus, seller profit, rounds, invalid actions, trade destruction, cost pass-through / experienced inflation, and posted-price control behavior.

## Primary mechanism tests

P1 — Anchor-independent persistence:
Within `anchor=hidden` and `order=buyer_first`, compare Llama 3.2 3B with Qwen3 1.7B on matched common-trade normalized prices across product × tightness × cost-state × seed cells. Report mean paired difference, bootstrap 95% CI, sign counts, and two-sided paired Wilcoxon p-value.

P2 — Differential anchor susceptibility:
For each matched product × tightness × order × cost-state × seed cell, compute each model's shown-minus-hidden normalized-price effect. Compare the Llama anchor effect with the Qwen anchor effect using the paired difference-in-differences. Report mean DID, bootstrap 95% CI, and two-sided paired Wilcoxon p-value.

Holm correction is applied across P1 and P2.

## Secondary mechanism tests

- Repeat P1 and anchor DID for Gemma comparisons.
- Move-order DID: seller-first minus buyer-first, compared across models.
- Tightness gradient: mean normalized transaction price by buyer model and cost/value tier.
- Agreement and trade-destruction rates by model and mechanism.
- Matched +10% cost-shock experienced inflation by model.
- Model × tightness patterns in buyer surplus.

## Validity / release gates

- Exactly 702 episode rows.
- No duplicate episode IDs.
- Posted-price transaction price must be mechanically invariant across buyer models within identical posted cells.
- All final prices must satisfy buyer budget and seller cost constraints.
- Infrastructure failures and invalid actions are reported and never silently dropped.
- Any primary price test uses only cells where both compared models traded.
- The full row set, including failed/no-trade episodes, remains in the artifact.

## Interpretation boundary

E02-B is an open-weight mechanism test. It does not establish effects for commercial GPT, Claude, Gemini, or other provider-hosted models. The experiment is designed to discriminate anchoring, move-order, and tightness mechanisms before commercial-model replication.
