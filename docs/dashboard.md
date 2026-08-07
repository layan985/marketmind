# Interactive dashboard

Install and launch:

```bash
pip install "marketmind[dashboard]"
marketmind-dashboard
```

The dashboard can use deterministic synthetic data or a user-supplied wide CSV. It exposes:

- MII and its three component paths;
- the latest causal regime;
- rolling parameter and cost controls;
- all nine regime-conditional indicator reports;
- downloadable MII, thresholds, and regime labels.

Uploaded data remains in the running Streamlit process. Deployments should add the
organization's own access controls and data-retention policy before accepting licensed or
confidential histories.

