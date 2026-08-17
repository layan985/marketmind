from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'records'
OUT.mkdir(parents=True, exist_ok=True)

def annualized_sharpe(x: np.ndarray) -> float:
    sd = np.std(x, ddof=1)
    return float(np.sqrt(252) * np.mean(x) / sd) if sd else float('nan')

def leakage_trial(n: int, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0, 0.01, n)
    s = pd.Series(returns)
    control_signal = np.sign(s.shift(1).rolling(20, min_periods=20).mean()).fillna(0).to_numpy()
    centered_signal = np.sign(s.rolling(21, center=True, min_periods=21).mean()).fillna(0).to_numpy()
    same_session_signal = np.sign(returns)
    score = s.shift(1).rolling(20, min_periods=20).mean().fillna(0).to_numpy()
    thresholds = np.quantile(np.abs(score[20:]), np.linspace(0.1, 0.9, 17))
    retrospective = []
    for threshold in thresholds:
        signal = np.where(score > threshold, 1, np.where(score < -threshold, -1, 0))
        retrospective.append((annualized_sharpe(signal * returns), signal))
    retrospective_signal = max(retrospective, key=lambda item: item[0])[1]
    candidates = []
    for _ in range(50):
        noise_score = rng.normal(size=n)
        signal = np.sign(pd.Series(noise_score).shift(1).rolling(5, min_periods=5).mean()).fillna(0).to_numpy()
        candidate_returns = signal * returns
        candidates.append((annualized_sharpe(candidate_returns), candidate_returns))
    selected_returns = max(candidates, key=lambda item:item[0])[1]
    return {
        'control': annualized_sharpe(control_signal * returns),
        'centered_window': annualized_sharpe(centered_signal * returns),
        'same_session': annualized_sharpe(same_session_signal * returns),
        'retrospective_threshold': annualized_sharpe(retrospective_signal * returns),
        'survivorship_selection_50': annualized_sharpe(selected_returns),
    }

def main() -> None:
    runs = pd.DataFrame([{'seed':1000+i, **leakage_trial(4000,1000+i)} for i in range(100)])
    runs.to_csv(OUT/'LAB-002_runs.csv', index=False, float_format='%.10f')
    rows=[]
    for c in [x for x in runs.columns if x != 'seed']:
        x=runs[c]
        rows.append({'arm':c,'mean':x.mean(),'median':x.median(),'p05':x.quantile(.05),'p95':x.quantile(.95),'max':x.max(),'min':x.min(),'fraction_gt_1':(x>1).mean(),'fraction_gt_2':(x>2).mean()})
    pd.DataFrame(rows).to_csv(OUT/'LAB-002_summary.csv', index=False, float_format='%.10f')

if __name__ == '__main__':
    main()
