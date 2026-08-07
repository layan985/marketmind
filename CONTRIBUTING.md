# Contributing

Contributions are welcome when they preserve causal timing, expose assumptions, and add
tests for numerical behavior.

1. Open an issue describing the estimator, bug, or research extension.
2. Create a focused branch and install `pip install -e ".[all]"`.
3. Add tests, documentation, and a changelog entry.
4. Run `ruff check .`, `pytest`, and `mkdocs build --strict`.
5. Open a pull request. Explain data provenance and any divergence from the paper defaults.

New estimators should document units, bias, sample-size requirements, randomness, and
the information set available at time `t`. Empirical claims need a reproducible data
manifest; licensed data must not be committed.
