# MM-BENCH-008 — The Simplest Model That Wins

## Question

What is the simplest model that reproduces MarketMind classifications closely enough that the extra machinery no longer earns its complexity?

## Candidate simplifications

- realized volatility alone;
- average absolute correlation alone;
- first-principal-component concentration;
- trend × volatility rules;
- two-feature threshold rules;
- a distilled multinomial logistic model fit only on training data.

## Evaluation

Out-of-sample state agreement, transition-date agreement, persistence, perturbation stability, future-volatility separation, cross-market consistency, calibration where applicable and computational cost.

## Complexity rule

Prefer the simpler model if it matches the full system within prespecified tolerances on the scientifically relevant outcomes. MarketMind is not required to win this benchmark; a successful distillation is a legitimate research result and may justify simplifying the software.
