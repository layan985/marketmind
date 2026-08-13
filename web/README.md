# MarketMind public web surface

This directory contains the static MarketMind website. It is separate from the Streamlit dashboard and from the code used for the prospective test.

## Vercel deployment settings

Import `layan985/marketmind` into a dedicated Vercel project with:

- **Root Directory:** `web`
- **Framework Preset:** Other
- **Build Command:** leave empty
- **Output Directory:** leave empty / repository root for this static directory
- **Install Command:** leave empty

The directory contains the public homepage (`index.html`), research dossier
(`research.html`), validation ledger (`validation.html`), shared stylesheet, and Vercel
configuration. Clean URLs expose the two detail pages as `/research` and `/validation`.
No secrets or environment variables are required.

## Deployment boundary

Do not point the existing `marketpulse-live` production alias at this repository. MarketPulse and MarketMind are distinct products. MarketMind should have its own Vercel project and production alias so public citations cannot resolve to the wrong interface.

## Verification before outreach

Before sharing the production URL externally:

1. confirm the page title is `MarketMind — Multiscale Market Intelligence`;
2. confirm `/research` and `/validation` load and their GitHub, DOI, OSF, PyPI, audit,
   reproducibility, and replication-challenge links resolve correctly;
3. verify desktop and mobile layouts;
4. confirm no prospective performance result is claimed;
5. confirm the page says research software / not investment advice;
6. record the production URL in the root README only after verification.
