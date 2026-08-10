# Last Price E02-C — Protocol-Compliance Robustness

## Purpose

E02-B found large model-specific price-anchor and move-order effects, but its release audit failed because model outputs contained illegal actions. E02-C tests whether the two preregistered E02-B mechanisms survive a deterministic legal-action enforcement layer.

E02-C is a robustness experiment. It does not overwrite, clean, or reinterpret E02-B.

## Frozen models

Buyer treatments:
- `qwen17` = `qwen3:1.7b`
- `gemma4` = `gemma3:4b`
- `llama3` = `llama3.2:3b`

Fixed seller:
- `qwen3:4b`

## Frozen economic design

The economic design is unchanged from E02-B:
- products: headphones, suitcase, chair;
- seller-cost tightness: 0.45, 0.65, 0.85 times buyer value;
- states: baseline and +10% seller-cost shock;
- public reference-price anchor: shown or hidden;
- move order: buyer first or seller first;
- three matched seeds per bargaining cell;
- posted-price negative controls;
- maximum six economic turns.

The initial E02-B prompts and initial RNG seeds are preserved exactly. This is deliberate: before enforcement is invoked, E02-C should reproduce the same first attempted action as E02-B for a given cell.

Expected episodes: **702** = 9 buyer×product jobs × 78 episodes per job.

## Deterministic enforcement treatment

Each economic turn receives at most two model attempts.

1. Generate the first action using the exact E02-B turn prompt and seed.
2. Validate it mechanically against the published protocol.
3. If legal, accept it into public history.
4. If illegal, reject it. The illegal attempt is logged but is **not** added to public negotiation history and does not consume an economic turn.
5. Give exactly one retry using the same turn prompt plus this identical correction string for every model and every illegality:

> `PROTOCOL CORRECTION: Your previous action was illegal under the published protocol. Return exactly one legal JSON action now. Do not explain the error.`

6. The retry seed is the original turn seed plus 100000.
7. If the retry is legal, accept it into history.
8. If the retry is also illegal, terminate the episode without agreement and record one unresolved protocol failure. No discretionary repair, clipping, coerced acceptance, inferred action, or third attempt is allowed.

## Mechanical legality rules

Allowed actions are `offer`, `accept`, `reject`, `walk_away`.

- With no outstanding offer, `accept` and `reject` are illegal.
- `offer` requires a finite positive numeric price.
- A buyer offer above its private budget is illegal.
- A seller offer below its private marginal cost is illegal.
- `accept` requires an outstanding offer made by the counterparty.
- A buyer may not accept a price above its budget.
- A seller may not accept a price below its cost.
- Non-offer actions must have a null price; a stray numeric price is ignored for legality but recorded in the raw model output.

Posted-price control allows only `accept` or `walk_away`; one identical retry is permitted after an illegal first attempt.

## Primary outcomes

P1 — hidden-anchor, buyer-first transaction-price difference:

`normalized_price(Llama 3.2 3B) - normalized_price(Qwen3 1.7B)`

computed only on matched cells in which both buyers trade.

P2 — differential anchor effect:

`(shown - hidden)_Llama - (shown - hidden)_Qwen`

computed on matched cells with the required successful trades.

Both use paired two-sided Wilcoxon tests and Holm correction across P1 and P2. Bootstrap confidence intervals use a fixed seed.

## Preregistered validation criteria

The mechanism is considered technically clean only if:
- all 702 episodes are present;
- all nine source cells are present;
- no duplicate episode IDs;
- zero infrastructure failures;
- zero unresolved protocol failures after the single retry;
- zero realized transaction prices outside buyer-budget or seller-cost bounds;
- posted-price negative-control range across buyer models is zero.

The mechanism is considered substantively replicated if, in addition:
- pooled P1 remains negative;
- pooled P2 remains positive;
- Holm-adjusted p <= 0.05 for both P1 and P2;
- each effect has the preregistered direction in at least two of the three products.

First-attempt illegality and retry use are descriptive outcomes and are not themselves release blockers if the retry resolves them legally.

## Secondary outcomes

Report:
- agreement rates and destroyed efficient trades;
- first-attempt illegal actions by actor/model/tightness;
- retry success rates;
- unresolved failures, if any;
- anchor effects by model;
- move-order effects by model;
- product-specific P1 and P2;
- experienced inflation under the matched +10% cost shock.

Inflation is secondary and must not be promoted to a confirmatory claim from E02-C.

## Interpretation boundary

E02-C is an open-weight robustness experiment. Commercial-model generalization remains untested until a separately frozen multi-provider replication.