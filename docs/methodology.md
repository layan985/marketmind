# Methodology

## Memory

The package estimates the DFA Hurst exponent from the integrated, demeaned return
profile. Linear trends are removed in forward and reverse non-overlapping segments over
log-spaced scales. \(H>0.5\) indicates persistence and \(H<0.5\) antipersistence.

Higuchi dimension is estimated on the reconstructed log-price path using
\(k=1,\ldots,20\). The paper's self-affine mapping \(H_D=2-D\) turns lower geometric
complexity into higher memory. Absolute-return autocorrelation is fit with an exponential
decay; slow decay implies persistent volatility memory.

## Information flow

Shannon entropy uses 20 equal-width bins within each trailing window. The MII uses
`1 - normalized_entropy`, so structural order points upward.

Mutual information uses the Kraskov nearest-neighbor estimator with a Chebyshev metric.
Transfer entropy is implemented as conditional mutual information:

\[
TE_{X\rightarrow Y}=I(X_{t-1};Y_t\mid Y_{t-1}).
\]

The baseline is \(k=3\); sensitivity checks should repeat at \(k=4\) and \(k=5\).
Estimator outputs are in nats. Deterministic micro-jitter resolves exact distance ties.

## Connectivity

For each trailing return panel, MarketMind computes:

1. mean absolute pairwise correlation;
2. Onnela-style weighted clustering after thresholding edge strengths;
3. a minimum spanning tree on \(d_{ij}=\sqrt{2(1-\rho_{ij})}\).

The MST is built with Prim's algorithm. Coherence is one minus mean tree-edge distance
scaled by the maximum correlation distance of two.

The API accepts a four-market primary panel for memory/information and an optional
broader `network_data` panel for sector and volatility connectivity. If the second panel
is omitted, the primary panel is reused.

## Normalization and weights

Raw measures are transformed so higher always means more coherent information structure.
They are then min-max normalized and averaged inside each component. MII weights are
fixed at 0.35 memory, 0.40 information, and 0.25 connectivity.

The paper does not publish the scaler bounds. MarketMind therefore exposes two policies:

- `expanding`: update causal bounds with data available at the current date;
- `development`: fit bounds through a declared development end and freeze them.

The second policy is appropriate for the manuscript's 2003–2014 development and
2015–2024 validation split.

## Regimes

At the first trading observation of each month, lower and upper MII terciles are estimated
from up to 756 preceding sessions. They remain fixed through that month. The current MII
observation is never included in the threshold sample used to classify itself.

The printed 0.33 and 0.67 values are descriptive approximations, not fixed ex-post cutoffs.
