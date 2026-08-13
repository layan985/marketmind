"""MarketMind: multiscale market-regime research tools."""

from marketmind._version import __version__
from marketmind.backtest import EvaluationResult, WalkForwardEvaluator
from marketmind.fractal import dfa_hurst, higuchi_fractal_dimension
from marketmind.information import mutual_information, shannon_entropy, transfer_entropy
from marketmind.mii import MarketMind, MarketMindConfig, MIIResult
from marketmind.networks import DynamicNetwork, correlation_distance, minimum_spanning_tree
from marketmind.regimes import classify_regimes
from marketmind.study import (
    ConfirmatoryMarketResult,
    confirmatory_market_returns,
    family_exposures,
    mechanism_block_bootstrap,
    paired_sharpe_block_bootstrap,
    strategy_exposures,
)

__all__ = [
    "ConfirmatoryMarketResult",
    "DynamicNetwork",
    "EvaluationResult",
    "MIIResult",
    "MarketMind",
    "MarketMindConfig",
    "WalkForwardEvaluator",
    "__version__",
    "classify_regimes",
    "confirmatory_market_returns",
    "correlation_distance",
    "dfa_hurst",
    "family_exposures",
    "higuchi_fractal_dimension",
    "minimum_spanning_tree",
    "mechanism_block_bootstrap",
    "mutual_information",
    "paired_sharpe_block_bootstrap",
    "shannon_entropy",
    "strategy_exposures",
    "transfer_entropy",
]
