import numpy as np
import pytest

from marketmind.fractal import (
    absolute_return_acf_decay,
    dfa_hurst,
    higuchi_fractal_dimension,
    hurst_from_fractal_dimension,
)
from marketmind.information import (
    conditional_mutual_information,
    mutual_information,
    shannon_entropy,
    transfer_entropy,
)


def test_dfa_white_noise_is_near_half() -> None:
    values = np.random.default_rng(1).normal(size=4096)
    assert 0.40 < dfa_hurst(values, n_scales=16) < 0.62


def test_higuchi_brownian_path_has_plausible_dimension() -> None:
    path = np.cumsum(np.random.default_rng(2).normal(size=4096))
    dimension = higuchi_fractal_dimension(path, k_max=20)
    assert 1.3 < dimension < 1.7
    assert hurst_from_fractal_dimension(dimension) == pytest.approx(2 - dimension)


def test_acf_decay_and_validation() -> None:
    rng = np.random.default_rng(3)
    values = rng.normal(size=500)
    assert absolute_return_acf_decay(values, max_lag=10) >= 0
    with pytest.raises(ValueError):
        dfa_hurst(np.ones(100))
    with pytest.raises(ValueError):
        higuchi_fractal_dimension(values[:20], k_max=20)


def test_shannon_entropy_normalized_and_constant() -> None:
    values = np.linspace(-1, 1, 1000)
    assert shannon_entropy(values, bins=20, normalize=True) == pytest.approx(1.0, abs=0.01)
    assert shannon_entropy(np.ones(20)) == 0.0
    with pytest.raises(ValueError):
        shannon_entropy([[1, 2], [3, 4]])


def test_mutual_information_detects_dependence() -> None:
    rng = np.random.default_rng(4)
    x = rng.normal(size=800)
    dependent = x + rng.normal(scale=0.15, size=800)
    independent = rng.normal(size=800)
    assert mutual_information(x, dependent, k=3) > mutual_information(x, independent, k=3) + 0.5


def test_transfer_entropy_detects_direction() -> None:
    rng = np.random.default_rng(5)
    x = rng.normal(size=1200)
    y = np.zeros(1200)
    for index in range(1, len(y)):
        y[index] = 0.85 * x[index - 1] + 0.15 * y[index - 1] + rng.normal(scale=0.25)
    assert transfer_entropy(x, y, k=3) > transfer_entropy(y, x, k=3) + 0.15
    assert conditional_mutual_information(x[:-1], y[1:], y[:-1], k=3) >= 0


def test_information_validation() -> None:
    with pytest.raises(ValueError):
        mutual_information(np.arange(5), np.arange(4))
    with pytest.raises(ValueError):
        transfer_entropy(np.arange(10), np.arange(10), source_history=0)

