"""Regime-comparison tests used in the empirical design."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import f_oneway, kruskal, rankdata


def regime_tests(returns: pd.Series, regimes: pd.Series) -> pd.Series:
    """Run Kruskal-Wallis and one-way ANOVA on pooled ranks."""
    frame = pd.concat(
        [pd.to_numeric(returns, errors="coerce").rename("return"), regimes.rename("regime")], axis=1
    ).dropna()
    groups = [
        group["return"].to_numpy()
        for _, group in frame.groupby("regime", observed=True)
        if len(group) >= 2
    ]
    if len(groups) < 2:
        raise ValueError("at least two regimes with two observations each are required")
    kw = kruskal(*groups)
    ranked = rankdata(frame["return"])
    ranked_frame = frame.assign(rank=ranked)
    rank_groups = [
        group["rank"].to_numpy()
        for _, group in ranked_frame.groupby("regime", observed=True)
        if len(group) >= 2
    ]
    anova = f_oneway(*rank_groups)
    return pd.Series(
        {
            "kruskal_statistic": float(kw.statistic),
            "kruskal_pvalue": float(kw.pvalue),
            "rank_anova_statistic": float(anova.statistic),
            "rank_anova_pvalue": float(anova.pvalue),
            "observations": float(len(frame)),
        }
    )

