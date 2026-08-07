# Walk-forward evaluation

## Pre-specified signal family

| Category | Signals |
| --- | --- |
| Trend | 50/200 SMA, 100-day MA slope, close above EMA(100) |
| Mean reversion | RSI(14) entry/exit, lower Bollinger reversal, three-down-close reversal |
| Breakout | 20-day high, 20-day Donchian, ATR(14) expansion |

All systems are unlevered and long-only. Parameters are fixed rather than selected on
performance.

## Timing

An indicator calculated with date-\(t\) close data becomes a position at \(t+1\) by default.
Regime labels are shifted by the same execution lag. Turnover is the absolute position
change; costs and slippage are charged per unit turnover.

## Metrics and tests

Evaluation reports average and median return, hit rate, annualized Sharpe, maximum
drawdown, profit factor, total and annualized return, volatility, exposure, and trades.
`regime_tests` supplies Kruskal–Wallis and ANOVA-on-ranks comparisons.

## Robustness

- `naive_baselines` creates buy-and-hold, cash, lag-sign, and exposure-matched shuffle.
- `transaction_cost_sweep` repeats every test under several basis-point assumptions.
- `block_bootstrap_interval` preserves short-run dependence in uncertainty intervals.
- `white_reality_check` bootstraps the best result after centering all tried strategies.
- `deflated_sharpe_probability` penalizes multiple trials and non-normal return moments.

These checks reduce overstatement; none turns an observational backtest into a live-trading guarantee.

