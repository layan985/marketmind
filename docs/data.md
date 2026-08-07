# Data and reproducibility

## Public proxy pipeline

Install the optional adapter and execute the versioned YAML request:

```bash
pip install "marketmind[data]"
marketmind fetch --config config/paper-public.yml --output data/raw/paper-public
```

The pipeline records the requested ticker map, provider, dates, price field, bounded
forward-fill rule, coverage, missingness, and a stable SHA-256 content fingerprint.

## Licensed paper data

The original paper used Bloomberg and Refinitiv for several primary histories. Those
observations cannot be placed in an open repository. Export them to the documented wide
CSV schema and run the same local pipeline.

!!! important
    Public Yahoo histories can differ because of adjustments, revisions, market calendars,
    and futures rolls. They reproduce the method, not necessarily each paper number.

## Missing data

Prices may be forward-filled for a bounded number of sessions, configured by
`forward_fill_limit`. The package refuses non-positive prices and duplicate timestamps.
Return panels are aligned inside each estimator window, and the usable cross-section is
recorded by the run's data artifact.

See the repository's `REPRODUCIBILITY.md` for the complete protocol.

