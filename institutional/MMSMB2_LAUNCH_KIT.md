# MMSMB-2 / Market Twins — Launch Kit

## The line

**Same market. Different machine.**

I built a synthetic financial benchmark where the temporal propagation mechanism changes while the stationary contemporaneous covariance is held fixed. Volatility, average correlation and PC1 concentration sit at chance; a simple temporal mechanism score detects the switch. Then I reverse the experiment: volatility changes while the mechanism does not.

The point is not to announce another regime detector. The point is to ask whether a financial model can distinguish **what changed**, and whether it can admit when the answer is not identifiable.

## Public launch post

MMSMB-1 gave me an annoying result: simple volatility recovered the synthetic regime better than MarketMind, and average correlation reproduced almost all of the connectivity states.

So instead of hiding that, I built the next benchmark around it.

In MMSMB-2 I generate two 9-variable markets with different temporal propagation mechanisms but the same stationary contemporaneous covariance. Across 200 replications, volatility, average correlation and PC1 concentration are basically chance at detecting the switch: 0.505, 0.497 and 0.497 AUC. A very simple VAR-coefficient shift gets 0.797.

Then I invert the experiment. I keep the propagation mechanism fixed and increase the covariance scale 2.25x. Volatility goes to 1.000 AUC; the temporal mechanism scores go back to chance.

There is a third track where two causal orientations imply exactly the same observational Gaussian law. The correct answer there is not a confident arrow. It is “you cannot identify this without another assumption or intervention.”

I’m calling the benchmark **Market Twins: Same Market, Different Machine**. Code, seeds and results are public. I would genuinely like other methods to beat it.

## Academic outreach

Priority people are authors whose work is directly adjacent to the benchmark question rather than generic finance celebrities:

- Sarah Mameche, Lénaïg Cornanguer, Urmi Ninad and Jilles Vreeken — SPACETIME / non-stationary temporal causal discovery.
- Muhammad Hasan Ferdous, Emam Hossain and Md Osman Gani — TimeGraph benchmark.
- Dennis Thumm, Billy Tim Anthony and Ying Chen — DoTime interventional/counterfactual time-series benchmark generator.

Message:

> I built a finance-specific falsification benchmark that separates temporal mechanism shifts from state/nuisance shifts. One track holds stationary covariance fixed while changing the VAR propagation graph; another holds propagation fixed while volatility changes; a third rewards abstention on an observationally equivalent orientation case. I thought it might be adjacent to your work on [SPACETIME / TimeGraph / DoTime]. The code and frozen results are public. If you think the construction is flawed, I would particularly value the failure case; if it is useful, I’d love an outside baseline or reproduction.

## Commercial outreach

### Lane 1 — synthetic financial-data vendors

Best first targets are teams already selling synthetic time-series or financial synthetic-data tooling, because validation is part of the product promise. Examples to investigate first: Gretel, MOSTLY AI/Syntho, Synthesized and adjacent enterprise synthetic-data vendors.

Hook:

> Your QA can show that synthetic data matches distributions. Market Twins asks a different question: does it preserve or invent the temporal mechanism a downstream model would act on? I built an open benchmark for that distinction and offer a private adversarial validation using the same protocol.

### Lane 2 — specialist financial time-series AI

The buyer is any team claiming a specialized temporal model is structurally better than generic baselines: forecasting, hedging, liquidity, risk or regime systems.

Hook:

> I’m not offering another forecasting model. I test whether a financial time-series model reacts to genuine mechanism changes or merely volatility/correlation proxies, using controlled worlds where the answer is known.

### Lane 3 — financial model governance / regulators / research groups

Synthetic-data governance is already an active financial-services problem. The offer fits teams that need evidence about model utility, structural fidelity and failure boundaries rather than data generation itself.

Hook:

> I have an open falsification benchmark plus a fixed-scope private validation service. The output is a reproducible dossier: structural sensitivity, nuisance invariance, proxy collapse, difficulty frontier, identifiability failures and claim boundaries.

## Offer

- Open benchmark: free.
- Structural Validation Snapshot: from EUR 2,500 for one model/claim.
- Private Adversarial Validation: from EUR 7,500 for custom stress worlds and confidential readout.
- Sponsored/custom benchmark: scoped separately.

Do not sell this as guaranteed alpha, certification or causal truth in live markets. Sell it as an independent way to test whether a model's stated structural claim survives adversarial evidence.

## Fame loop

1. Publish the benchmark result and the MarketMind loss that motivated it in the same post.
2. Tag/cite adjacent causal-time-series benchmark authors only where genuinely relevant.
3. Invite one external reproduction and one competing baseline, not generic applause.
4. Publish the first discrepancy or failure publicly.
5. Turn each outside submission into a benchmark-board update with a permanent result record.
6. Submit the benchmark generator/research note to a reproducible-software or benchmark venue once an independent reproduction exists.

The reputational asset is not “MarketMind always wins.” It is that MarketMind publishes tests strong enough to make its own claims fail.
