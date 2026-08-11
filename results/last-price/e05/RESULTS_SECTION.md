# E05 results section

## Confirmatory results

E05 completed the preregistered 702-episode panel: 648 bargaining episodes and 54 posted-price controls across 27 buyer-model × product × tightness source cells. The technical gate passed. There were no duplicate episode IDs, infrastructure failures in episode rows, invalid finite-menu choices, menu-reconstruction mismatches, realized bargaining prices above buyer budget, or realized bargaining prices below seller cost. All 216 matched bargaining blocks contained the three preregistered buyer models, and posted-price controls satisfied the prespecified cross-model equality check.

Changing the buyer model had a large effect on trade formation. The preregistered Cochran Q test rejected equality of matched agreement outcomes across the three buyer models (Q = 118.768, df = 2, Holm-adjusted p = 1.62127 × 10^-26). Agreement occurred in 39 of 216 Qwen 3 1.7B bargaining episodes (18.06%), 33 of 216 Gemma 3 4B episodes (15.28%), and 122 of 216 Llama 3.2 3B episodes (56.48%). In the prespecified pairwise decompositions, Llama exceeded Gemma by 41.20 percentage points and Qwen by 38.43 percentage points after Holm correction, while the Qwen–Gemma difference of 2.78 percentage points was not statistically significant.

The buyer model also changed realized buyer welfare. The preregistered Friedman test rejected equality of unconditional normalized realized buyer surplus across the three models (χ²_F = 192.147, df = 2, Holm-adjusted p = 3.77508 × 10^-42). Mean normalized realized buyer surplus was 0.0125 for Qwen, 0.0000 for Gemma, and 0.1340 for Llama. All three prespecified pairwise welfare contrasts were significant after Holm correction.

These results show that, in the frozen finite-action bargaining environment, model identity is an economically consequential treatment: holding the buyer's economic primitives and the bargaining mechanism fixed, changing only the model representing the buyer changes both the probability of trade and the buyer's realized welfare. The experiment does not identify a universal notion of model capability and does not establish that the observed ranking generalizes beyond these models, products, or artificial bargaining agents.

## Secondary heterogeneity

The prespecified model × product interaction was significant for agreement (clustered Wald p = 1.12636 × 10^-5) and for realized buyer welfare (clustered Wald p = 0.02410). The largest agreement gap appeared for headphones, where Llama agreed in 80.56% of bargaining episodes, compared with 26.39% for Gemma and 16.67% for Qwen. Llama's mean normalized realized buyer surplus remained positive across all three products: 0.1092 for chairs, 0.1739 for headphones, and 0.1189 for suitcases.
