# Last Price E05 — Frozen Aggregate Report

Technical gate: **PASS**
- source files: 27 / 27
- episodes: 702 / 702
- bargaining: 648 / 648
- posted controls: 54 / 54
- infrastructure failures: 0
- menu violations: 0
- menu reconstruction mismatches: 0
- over-budget agreements: 0
- below-cost agreements: 0
- matched bargaining blocks: 216 / 216

## Confirmatory outcomes

Confirmatory gate: **PASS**

### P1 — trade formation
- Cochran Q: 118.768
- raw p: 1.62127e-26
- Holm p: 1.62127e-26

### P2 — realized buyer welfare
- Friedman statistic: 192.147
- raw p: 1.88754e-42
- Holm p: 3.77508e-42

### By model

| buyer | agreements | n | agreement rate | mean normalized realized buyer surplus |
|---|---:|---:|---:|---:|
| qwen17 | 39 | 216 | 0.1806 | 0.0125 |
| gemma4 | 33 | 216 | 0.1528 | 0.0000 |
| llama3 | 122 | 216 | 0.5648 | 0.1340 |

## Interpretation boundary

Conditional price is secondary in E03. The primary question is whether changing the buyer model changes trade formation and/or unconditional realized buyer welfare under a mechanically finite feasible action space.
