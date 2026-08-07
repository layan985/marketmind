# MarketMind Historical Market-Regime Dataset — Codebook

## Purpose

The **MarketMind Historical Market-Regime Dataset** is designed as a citable empirical research output derived from the MarketMind methodology. It should be published independently from the software package and associated paper.

## Unit of observation

The canonical observation is a **market-date** pair at the release frequency produced by the configured pipeline. Exact frequency, sample dates, market universe, and parameter choices must be frozen in each release's provenance/configuration files.

## Core variables

### `date`
Observation date in ISO `YYYY-MM-DD` format. Dates follow the market-calendar and alignment conventions recorded in the release provenance.

### `market`
Canonical identifier for the market or asset represented by the row.

### `hurst`
Detrended-fluctuation-analysis Hurst estimate. Values are calculated only from information available within the configured estimation window.

### `fractal_dimension`
Higuchi fractal-dimension estimate for the configured price/return series and window.

### `entropy`
Shannon entropy measure calculated using the release's configured binning convention.

### `mutual_information`
Kraskov k-nearest-neighbor mutual-information estimate for the configured paired series.

### `transfer_entropy`
Directed information-flow estimate using causal inputs. The exact lag structure and estimator settings must be preserved in the release configuration.

### `network_connectivity`
Aggregate measure derived from the dynamic financial network constructed for the release's cross-section.

### `mii`
Market Intelligence Index composite combining memory, information-flow, and connectivity components under the release's frozen weighting and normalization choices.

### `regime`
Causal regime label (`low`, `medium`, or `high`) determined using thresholds learned exclusively from information available at the classification date.

## Missing values

Missing values are not to be replaced silently. They may arise from insufficient lookback history, inadequate aligned observations, insufficient network cross-section, or source-data gaps. Any forward filling or other bounded handling of source prices must occur upstream according to the documented release configuration.

## Provenance and licensed data

The original paper used licensed Bloomberg and Refinitiv histories for parts of the empirical sample. Those observations must not be redistributed where licensing prohibits it. Public proxy releases must explicitly state that they reproduce the method and research pipeline, not necessarily every numerical result from the licensed-data paper.

## Versioning

A DOI-bearing dataset release is immutable. Corrections or extensions are published as a new version and described in the changelog. Methodological/schema-breaking changes require a major version increment.

## Citation

The exact citation will be inserted after Zenodo issues the dataset DOI. Until then, cite the associated paper and software separately and identify the dataset version used without inventing an identifier.
