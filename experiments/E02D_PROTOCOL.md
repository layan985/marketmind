# Last Price E02-D — Constrained-Action Validation

## Purpose

E02-B and E02-C found model-specific price-anchor effects, but E02-C still produced unresolved illegal actions after one retry. E02-D tests the same economic mechanism with illegal actions made unavailable at generation time through state-dependent JSON Schema structured outputs.

E02-D does not overwrite, clean, or reinterpret E02-B/E02-C.

## Frozen models

Buyer treatments:
- `qwen17` = `qwen3:1.7b`
- `gemma4` = `gemma3:4b`
- `llama3` = `llama3.2:3b`

Fixed seller:
- `qwen3:4b`

## Frozen economic design

Unchanged from E02-B/E02-C:
- products: headphones, suitcase, chair;
- seller-cost tightness: 0.45, 0.65, 0.85 times buyer value;
- states: baseline and +10% seller-cost shock;
- public reference-price anchor: shown or hidden;
- move order: buyer first or seller first;
- three matched seeds per bargaining cell;
- posted-price negative controls;
- maximum six economic turns.

The natural-language system prompts, economic turn prompts, initial RNG seeds, temperature, and maximum output budget are preserved from E02-B. The only intended intervention is replacing unconstrained JSON generation with a dynamically generated JSON Schema passed through Ollama's `format` field.

Expected episodes: **702** = 9 buyer×product jobs × 78 episodes per job.

## State-dependent constrained action space

There are no retries, correction messages, clipping rules, inferred actions, or discretionary repairs.

For each turn, the harness constructs a JSON Schema that contains only actions legal in the current public state.

### No outstanding offer

Permitted actions:
- `offer`
- `walk_away`

`accept` and `reject` are absent from the schema.

### Outstanding counterparty offer

Permitted actions:
- `offer`
- `reject`
- `walk_away`
- `accept` only when the outstanding price is feasible for the acting agent.

### Price constraints

For a buyer `offer`:
- price must be finite and strictly positive;
- price must be <= private buyer budget.

For a seller `offer`:
- price must be finite;
- price must be >= private marginal cost.

For `accept`, `reject`, and `walk_away`, price is structurally `null`.

Every schema requires exactly `action`, `price`, and `message` and forbids extra fields.

The schema is supplied only through the decoder/API `format` field. It is not copied into the natural-language prompt, so the natural-language bargaining prompt remains aligned with E02-B/E02-C.

## Mechanical post-generation audit

Every returned action is independently revalidated after decoding.

If a generated response violates the same published legality rules despite the schema, the episode terminates immediately and records one `schema_violation`. No retry is allowed.

Thus E02-D distinguishes:
- decoder-constrained legal negotiation; from
- any residual schema/implementation failure.

## Primary outcomes

P1 — hidden-anchor, buyer-first transaction-price difference:

`normalized_price(Llama 3.2 3B) - normalized_price(Qwen3 1.7B)`

computed only on matched cells in which both buyers trade.

P2 — differential anchor effect:

`(shown - hidden)_Llama - (shown - hidden)_Qwen`

computed on matched cells with all required successful trades.

Both use paired two-sided Wilcoxon tests and Holm correction across P1 and P2. Bootstrap confidence intervals use a fixed seed.

## Preregistered technical validation criteria

Technical gate passes only if:
- all 702 episodes are present;
- all nine buyer×product source cells are present;
- no duplicate episode IDs;
- zero infrastructure failures;
- zero schema violations under independent mechanical validation;
- zero realized transaction prices above buyer budget or below seller cost;
- posted-price negative-control range across buyer models is zero.

## Preregistered substantive replication criteria

The mechanism is substantively replicated only if the technical gate passes and:
- pooled P1 remains negative;
- pooled P2 remains positive;
- Holm-adjusted p <= 0.05 for both P1 and P2;
- P1 has the preregistered negative direction in at least two of three products;
- P2 has the preregistered positive direction in at least two of three products.

## Secondary outcomes

Report:
- agreement rates and destroyed efficient trades;
- anchor effects by model;
- move-order effects by model;
- tightness slices;
- product-specific P1/P2;
- matched +10% cost-shock experienced inflation.

Inflation remains secondary and must not be promoted to a confirmatory claim from E02-D.

## Interpretation boundary

E02-D is an open-weight constrained-decoding validation. Commercial-model generalization remains untested until a separately frozen multi-provider experiment.