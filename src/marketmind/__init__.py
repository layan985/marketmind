"""MarketMind: multiscale market-regime research tools."""

from marketmind.backtest import EvaluationResult, WalkForwardEvaluator
from marketmind.fractal import dfa_hurst, higuchi_fractal_dimension
from marketmind.information import mutual_information, shannon_entropy, transfer_entropy
from marketmind.mii import MarketMind, MarketMindConfig, MIIResult
from marketmind.networks import DynamicNetwork, correlation_distance, minimum_spanning_tree
from marketmind.regimes import classify_regimes

__all__ = [
    "DynamicNetwork",
    "EvaluationResult",
    "MIIResult",
    "MarketMind",
    "MarketMindConfig",
    "WalkForwardEvaluator",
    "classify_regimes",
    "correlation_distance",
    "dfa_hurst",
    "higuchi_fractal_dimension",
    "minimum_spanning_tree",
    "mutual_information",
    "shannon_entropy",
    "transfer_entropy",
]

__version__ = "0.1.0"

