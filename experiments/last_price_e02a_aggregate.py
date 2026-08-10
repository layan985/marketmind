import glob
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

BUYER_ORDER = ["qwen17", "gemma4", "llama3"]
BUYER_NAMES = {
    "qwen17": "Qwen3 1.7B",
    "gemma4": "Gemma 3 4B",
    "llama3": "Llama 3.2 3B",
}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return [round(max(0, center - half), 4), round(min(1, center + half), 4)]


def exact_mcnemar(a, b):
    keys = sorted(set(a) & set(b))
    n10 = sum(bool(a[k]) and not bool(b[k]) for k in keys)
    n01 = sum(not bool(a[k]) and bool(b[k]) for k in keys)
    n = n10 + n01
    if n == 0:
        p = 1.0
    else:
        lo = min(n10, n01)
        tail = sum(math.comb(n, i) for i in range(lo + 1)) / (2 ** n)
        p = min(1.0, 2 * tail)
    return {"common_cells": len(keys), "a_trade_b_no": n10, "a_no_b_trade": n01, "discordant": n, "p_exact": p}


def holm(results):
    ordered = sorted(results, key=lambda x: x[1]["p_exact"])
    running = 0.0
    m = len(ordered)
    for i, (name, r) in enumerate(ordered):
        adjusted = min(1.0, r["p_exact"] * (m - i))
        running = max(running, adjusted)
        r["p_holm"] = min(1.0, running)


def mean_or_none(xs):
    return round(statistics.mean(xs), 4) if xs else None


def main():
    rows = []
    manifests = []
    for path in sorted(glob.glob("collected/*/episodes.json")):
        data = json.load(open(path))
        rows.extend(data["episodes"])
        manifests.append({"path": path, "buyer_model": data["buyer_model"], "seller_model": data["seller_model"], "product": data["product"]["product_id"]})

    expected = 180
    audit = {
        "episodes": len(rows),
        "expected_episodes": expected,
        "episode_count_pass": len(rows) == expected,
        "duplicate_episode_ids": len(rows) - len({r["episode_id"] for r in rows}),
        "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows),
        "invalid_actions": sum(r.get("invalid_actions", 0) for r in rows),
    }

    bargaining = [r for r in rows if r["seller"] != "posted"]
    posted = [r for r in rows if r["seller"] == "posted"]

    posted_ranges = {}
    for product in sorted({r["product_id"] for r in posted}):
        for state in ("baseline", "shock_10pct"):
            vals = [r["final_price"] for r in posted if r["product_id"] == product and r["state"] == state and r.get("agreement") and r.get("final_price") is not None]
            posted_ranges[f"{product}|{state}"] = round(max(vals) - min(vals), 8) if vals else None
    audit["posted_price_ranges"] = posted_ranges
    audit["posted_price_control_pass"] = all(v in (None, 0, 0.0) for v in posted_ranges.values())

    by_buyer = {}
    cell_maps = {}
    price_maps = {}
    for buyer in BUYER_ORDER:
        br = [r for r in bargaining if r["buyer"] == buyer and not r.get("infrastructure_failure")]
        trades = [r for r in br if r.get("agreement") is True]
        k, n = len(trades), len(br)
        state_rates = {}
        for state in ("baseline", "shock_10pct"):
            sr = [r for r in br if r["state"] == state]
            sk = sum(r.get("agreement") is True for r in sr)
            state_rates[state] = {"trades": sk, "n": len(sr), "rate": round(sk / len(sr), 4) if sr else None, "ci95_wilson": wilson(sk, len(sr))}

        norm_prices = []
        raw_prices_by_product = defaultdict(list)
        product_refs = {"headphones": 200.0, "suitcase": 140.0, "chair": 320.0}
        for r in trades:
            norm_prices.append(r["final_price"] / product_refs[r["product_id"]])
            raw_prices_by_product[r["product_id"]].append(r["final_price"])

        shock_pass = []
        for product in ("headphones", "suitcase", "chair"):
            for seed_idx in range(5):
                base = next((r for r in br if r["product_id"] == product and r["seed_index"] == seed_idx and r["state"] == "baseline"), None)
                shock = next((r for r in br if r["product_id"] == product and r["seed_index"] == seed_idx and r["state"] == "shock_10pct"), None)
                if base and shock and base.get("agreement") and shock.get("agreement") and base.get("final_price") and shock.get("final_price"):
                    shock_pass.append((shock["final_price"] / base["final_price"] - 1) * 100)

        by_buyer[buyer] = {
            "model": BUYER_NAMES[buyer],
            "trades": k,
            "n": n,
            "agreement_rate": round(k / n, 4) if n else None,
            "agreement_ci95_wilson": wilson(k, n),
            "state_rates": state_rates,
            "trade_destroyed": sum(r.get("trade_destroyed") is True for r in br),
            "invalid_actions": sum(r.get("invalid_actions", 0) for r in br),
            "conditional_price_ratio_to_reference_mean": mean_or_none(norm_prices),
            "conditional_price_by_product_mean": {p: mean_or_none(v) for p, v in raw_prices_by_product.items()},
            "matched_shock_pairs_with_trade": len(shock_pass),
            "experienced_inflation_pct_mean": mean_or_none(shock_pass),
        }
        cell_maps[buyer] = {(r["product_id"], r["state"], r["seed_index"]): bool(r.get("agreement")) for r in br}
        price_maps[buyer] = {(r["product_id"], r["state"], r["seed_index"]): r.get("final_price") for r in br if r.get("agreement") and r.get("final_price") is not None}

    pairwise = {}
    pairs = [("qwen17", "gemma4"), ("qwen17", "llama3"), ("gemma4", "llama3")]
    holder = []
    for a, b in pairs:
        key = f"{a}_vs_{b}"
        r = exact_mcnemar(cell_maps[a], cell_maps[b])
        common_price_keys = sorted(set(price_maps[a]) & set(price_maps[b]))
        diffs = [price_maps[a][k] - price_maps[b][k] for k in common_price_keys]
        r["common_trade_price_cells"] = len(common_price_keys)
        r["matched_price_diff_a_minus_b_mean"] = mean_or_none(diffs)
        pairwise[key] = r
        holder.append((key, r))
    holm(holder)

    release_blockers = []
    if not audit["episode_count_pass"]:
        release_blockers.append("episode_count")
    if audit["duplicate_episode_ids"]:
        release_blockers.append("duplicate_episode_ids")
    if audit["infrastructure_failures"]:
        release_blockers.append("infrastructure_failures")
    if not audit["posted_price_control_pass"]:
        release_blockers.append("posted_price_control")
    audit["release_blockers"] = release_blockers
    audit["audit_pass"] = not release_blockers

    summary = {
        "experiment_id": "last-price-e02a-open-model-validation-20260810",
        "evidence_boundary": "180-episode open-model validation; not the 72,000-episode confirmatory benchmark.",
        "audit": audit,
        "by_buyer": by_buyer,
        "pairwise_matched_agreement_and_price": pairwise,
        "manifests": manifests,
    }

    out = Path("aggregate")
    out.mkdir(exist_ok=True)
    (out / "e02a_summary.json").write_text(json.dumps(summary, indent=2))

    lines = [
        "# Last Price E02-A — Execution Report",
        "",
        f"Episodes: **{audit['episodes']} / {expected}**",
        f"Infrastructure failures: **{audit['infrastructure_failures']}**",
        f"Invalid actions: **{audit['invalid_actions']}**",
        f"Posted-price control: **{'PASS' if audit['posted_price_control_pass'] else 'FAIL'}**",
        f"Release audit: **{'PASS' if audit['audit_pass'] else 'FAIL'}**",
        "",
        "## Bargaining outcomes",
        "",
        "| Buyer | Trades | Agreement rate | 95% Wilson CI | Destroyed trades | Mean price/reference | Matched shock pairs | Mean experienced inflation |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for b in BUYER_ORDER:
        x = by_buyer[b]
        ci = x["agreement_ci95_wilson"]
        lines.append(f"| {x['model']} | {x['trades']}/{x['n']} | {x['agreement_rate']:.3f} | [{ci[0]:.3f}, {ci[1]:.3f}] | {x['trade_destroyed']} | {x['conditional_price_ratio_to_reference_mean']} | {x['matched_shock_pairs_with_trade']} | {x['experienced_inflation_pct_mean']} |")
    lines += ["", "## Matched pairwise tests", "", "| Comparison | Discordant | Exact p | Holm p | Common-trade price cells | Mean matched price difference (A-B) |", "|---|---:|---:|---:|---:|---:|"]
    for key, r in pairwise.items():
        lines.append(f"| {key} | {r['discordant']} | {r['p_exact']:.6f} | {r['p_holm']:.6f} | {r['common_trade_price_cells']} | {r['matched_price_diff_a_minus_b_mean']} |")
    lines += ["", "## Interpretation boundary", "", "Agreement and conditional price are co-primary outcomes. Price differences are reported only on common-trade cells. Missing matched baseline/shock trades are not imputed. This run is validation evidence, not the 72,000-episode confirmatory benchmark."]
    (out / "E02A_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
