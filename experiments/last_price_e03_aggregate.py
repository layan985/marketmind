import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

EXPECTED_BUYERS = ("qwen17", "gemma4", "llama3")
EXPECTED_PRODUCTS = ("headphones", "suitcase", "chair")
EXPECTED_TIGHTNESS = ("loose", "medium", "tight")
EXPECTED_ROWS = 702
EXPECTED_BARGAINING = 648
EXPECTED_POSTED = 54
EXPECTED_FILES = 27
EXPECTED_BLOCKS = 216

COLLECTED = Path("collected")
OUT = Path("aggregate")
OUT.mkdir(parents=True, exist_ok=True)


def holm(pvals):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted = {}
    running = 0.0
    for rank, (name, p) in enumerate(items, start=1):
        value = min(1.0, (m - rank + 1) * float(p))
        running = max(running, value)
        adjusted[name] = running
    return adjusted


def cochran_q(matrix):
    x = np.asarray(matrix, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3:
        raise ValueError("Cochran Q requires n x 3 matrix")
    k = x.shape[1]
    col = x.sum(axis=0)
    row = x.sum(axis=1)
    total = x.sum()
    denom = k * total - np.square(row).sum()
    if denom <= 0:
        return 0.0, 1.0
    q = (k - 1) * (k * np.square(col).sum() - total**2) / denom
    p = float(stats.chi2.sf(q, k - 1))
    return float(q), p


def exact_mcnemar(a, b):
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    a_yes_b_no = int(np.sum((a == 1) & (b == 0)))
    a_no_b_yes = int(np.sum((a == 0) & (b == 1)))
    discordant = a_yes_b_no + a_no_b_yes
    p = 1.0 if discordant == 0 else float(
        stats.binomtest(a_yes_b_no, discordant, p=0.5, alternative="two-sided").pvalue
    )
    return {
        "a_yes_b_no": a_yes_b_no,
        "a_no_b_yes": a_no_b_yes,
        "discordant": discordant,
        "p": p,
    }


def paired_wilcoxon(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diff = a - b
    if np.allclose(diff, 0.0):
        return {"statistic": 0.0, "p": 1.0}
    result = stats.wilcoxon(
        a,
        b,
        alternative="two-sided",
        zero_method="pratt",
        method="approx",
    )
    return {"statistic": float(result.statistic), "p": float(result.pvalue)}


def block_key(row):
    return (
        row["product_id"],
        row["tightness"],
        row["state"],
        row["anchor"],
        row["order"],
        int(row["seed_index"]),
    )


def verify_event(event):
    menu = event.get("menu")
    choice = event.get("choice_id")
    if not isinstance(menu, list) or choice is None:
        return False
    lookup = {item.get("id"): item for item in menu if isinstance(item, dict)}
    item = lookup.get(choice)
    if item is None:
        return False
    if event.get("action") != item.get("action"):
        return False
    expected_price = item.get("price") if item.get("action") == "offer" else None
    actual_price = event.get("price")
    if expected_price is None:
        return actual_price is None
    return actual_price is not None and abs(float(actual_price) - float(expected_price)) <= 1e-9


def safe_mean(values):
    vals = [float(x) for x in values if x is not None]
    return None if not vals else float(np.mean(vals))


def model_product_interaction(rows, outcome):
    try:
        import pandas as pd
        import statsmodels.api as sm
    except Exception as exc:
        return {"available": False, "error": str(exc)}

    data = []
    for row in rows:
        if row.get(outcome) is None:
            continue
        data.append(
            {
                "block": "|".join(map(str, block_key(row))),
                "buyer": row["buyer"],
                "product": row["product_id"],
                "y": float(row[outcome]),
            }
        )
    df = pd.DataFrame(data)
    if df.empty or df["block"].nunique() != EXPECTED_BLOCKS:
        return {
            "available": False,
            "error": f"requires {EXPECTED_BLOCKS} complete blocks; found {df['block'].nunique() if not df.empty else 0}",
        }

    df["gemma"] = (df["buyer"] == "gemma4").astype(float)
    df["llama"] = (df["buyer"] == "llama3").astype(float)
    df["gemma_chair"] = ((df["buyer"] == "gemma4") & (df["product"] == "chair")).astype(float)
    df["gemma_suitcase"] = ((df["buyer"] == "gemma4") & (df["product"] == "suitcase")).astype(float)
    df["llama_chair"] = ((df["buyer"] == "llama3") & (df["product"] == "chair")).astype(float)
    df["llama_suitcase"] = ((df["buyer"] == "llama3") & (df["product"] == "suitcase")).astype(float)

    xcols = [
        "gemma",
        "llama",
        "gemma_chair",
        "gemma_suitcase",
        "llama_chair",
        "llama_suitcase",
    ]
    grouped = df.groupby("block")
    ydm = df["y"] - grouped["y"].transform("mean")
    xdm = df[xcols].copy()
    for col in xcols:
        xdm[col] = df[col] - grouped[col].transform("mean")

    fit = sm.OLS(ydm.to_numpy(), xdm.to_numpy()).fit(
        cov_type="cluster", cov_kwds={"groups": df["block"].to_numpy()}
    )
    r = np.zeros((4, len(xcols)))
    for i, idx in enumerate((2, 3, 4, 5)):
        r[i, idx] = 1.0
    wald = fit.wald_test(r, scalar=True)
    return {
        "available": True,
        "coefficients": {name: float(value) for name, value in zip(xcols, fit.params)},
        "clustered_se": {name: float(value) for name, value in zip(xcols, fit.bse)},
        "interaction_wald_statistic": float(wald.statistic),
        "interaction_wald_p": float(wald.pvalue),
        "n_rows": int(len(df)),
        "n_blocks": int(df["block"].nunique()),
        "reference_buyer": "qwen17",
        "reference_product": "headphones",
    }


def main():
    files = sorted(COLLECTED.rglob("episodes.json"))
    rows = []
    source_summaries = []
    for path in files:
        payload = json.loads(path.read_text())
        source_summaries.append(
            {
                "path": str(path),
                "experiment_id": payload.get("experiment_id"),
                "buyer_model": payload.get("buyer_model"),
                "product_id": (payload.get("product") or {}).get("product_id"),
                "tightness": payload.get("tightness"),
                "episodes": len(payload.get("episodes") or []),
            }
        )
        for row in payload.get("episodes") or []:
            item = dict(row)
            item["_source_file"] = str(path)
            rows.append(item)

    counts = Counter(row.get("episode_id") for row in rows)
    duplicates = sorted(k for k, v in counts.items() if k is not None and v > 1)
    bargaining = [row for row in rows if row.get("seller") != "posted"]
    posted = [row for row in rows if row.get("seller") == "posted"]

    menu_violations = sum(int(row.get("menu_violations") or 0) for row in rows)
    reconstruction_mismatches = 0
    for row in rows:
        for event in row.get("events") or []:
            if not verify_event(event):
                reconstruction_mismatches += 1

    infra = [row for row in rows if row.get("infrastructure_failure") is True]
    over_budget = [
        row["episode_id"]
        for row in bargaining
        if row.get("agreement") is True
        and row.get("final_price") is not None
        and float(row["final_price"]) > float(row["buyer_budget"]) + 1e-9
    ]
    below_cost = [
        row["episode_id"]
        for row in bargaining
        if row.get("agreement") is True
        and row.get("final_price") is not None
        and float(row["final_price"]) + 1e-9 < float(row["seller_cost"])
    ]

    posted_groups = defaultdict(list)
    for row in posted:
        if row.get("agreement") is True and row.get("final_price") is not None:
            key = (row["product_id"], row["tightness"], row["state"])
            posted_groups[key].append(float(row["final_price"]))
    posted_ranges = {
        "|".join(key): (max(vals) - min(vals) if vals else None)
        for key, vals in sorted(posted_groups.items())
    }
    posted_price_failures = {
        key: value for key, value in posted_ranges.items() if value is not None and abs(value) > 1e-9
    }

    blocks = defaultdict(list)
    for row in bargaining:
        blocks[block_key(row)].append(row)
    bad_blocks = {}
    for key, items in blocks.items():
        buyers = sorted(row.get("buyer") for row in items)
        if len(items) != 3 or buyers != sorted(EXPECTED_BUYERS):
            bad_blocks["|".join(map(str, key))] = {"n": len(items), "buyers": buyers}

    experiment_ids = sorted({s["experiment_id"] for s in source_summaries})
    wrong_experiment = [x for x in experiment_ids if x != "last-price-e03-trade-welfare-20260810"]

    checks = {
        "source_files_27": len(files) == EXPECTED_FILES,
        "rows_702": len(rows) == EXPECTED_ROWS,
        "bargaining_648": len(bargaining) == EXPECTED_BARGAINING,
        "posted_54": len(posted) == EXPECTED_POSTED,
        "duplicates_zero": not duplicates,
        "infrastructure_failures_zero": not infra,
        "menu_violations_zero": menu_violations == 0,
        "menu_reconstruction_mismatches_zero": reconstruction_mismatches == 0,
        "over_budget_zero": not over_budget,
        "below_cost_zero": not below_cost,
        "posted_price_range_zero": not posted_price_failures,
        "matched_blocks_216": len(blocks) == EXPECTED_BLOCKS and not bad_blocks,
        "experiment_id_exact": not wrong_experiment and len(experiment_ids) == 1,
    }
    blockers = [name for name, ok in checks.items() if not ok]
    technical_pass = not blockers

    result = {
        "experiment_id": "last-price-e03-trade-welfare-20260810",
        "audit": {
            "technical_gate_pass": technical_pass,
            "checks": checks,
            "blockers": blockers,
            "source_files": len(files),
            "episodes": len(rows),
            "bargaining_episodes": len(bargaining),
            "posted_episodes": len(posted),
            "duplicate_episode_ids": duplicates,
            "infrastructure_failures": len(infra),
            "menu_violations": menu_violations,
            "menu_reconstruction_mismatches": reconstruction_mismatches,
            "over_budget_agreements": len(over_budget),
            "below_cost_agreements": len(below_cost),
            "posted_price_range_failures": posted_price_failures,
            "matched_blocks": len(blocks),
            "bad_blocks": bad_blocks,
            "source_summaries": source_summaries,
        },
        "confirmatory": {"status": "not_adjudicated" if not technical_pass else "pending"},
    }

    if technical_pass:
        ordered_blocks = sorted(blocks)
        agreement_matrix = []
        welfare_matrix = []
        for key in ordered_blocks:
            by_buyer = {row["buyer"]: row for row in blocks[key]}
            agreement_matrix.append(
                [1 if by_buyer[b]["agreement"] is True else 0 for b in EXPECTED_BUYERS]
            )
            welfare_matrix.append(
                [float(by_buyer[b]["normalized_realized_buyer_surplus"]) for b in EXPECTED_BUYERS]
            )

        q_stat, p1 = cochran_q(agreement_matrix)
        welfare_cols = np.asarray(welfare_matrix, dtype=float).T
        try:
            friedman = stats.friedmanchisquare(*welfare_cols)
            p2_stat = float(friedman.statistic)
            p2 = float(friedman.pvalue)
            if not math.isfinite(p2):
                p2_stat, p2 = 0.0, 1.0
        except Exception:
            p2_stat, p2 = 0.0, 1.0

        omnibus_adj = holm({"P1_trade_formation": p1, "P2_buyer_welfare": p2})

        pair_labels = (
            ("qwen17", "gemma4"),
            ("qwen17", "llama3"),
            ("gemma4", "llama3"),
        )
        pair_agreement = {}
        pair_welfare = {}
        agreement_raw_p = {}
        welfare_raw_p = {}
        matrix_a = np.asarray(agreement_matrix, dtype=int)
        matrix_w = np.asarray(welfare_matrix, dtype=float)
        buyer_idx = {buyer: i for i, buyer in enumerate(EXPECTED_BUYERS)}

        for a, b in pair_labels:
            ia, ib = buyer_idx[a], buyer_idx[b]
            key = f"{a}_minus_{b}"
            mc = exact_mcnemar(matrix_a[:, ia], matrix_a[:, ib])
            mc["agreement_difference_pp"] = float(
                100.0 * np.mean(matrix_a[:, ia] - matrix_a[:, ib])
            )
            pair_agreement[key] = mc
            agreement_raw_p[key] = mc["p"]

            wx = paired_wilcoxon(matrix_w[:, ia], matrix_w[:, ib])
            wx["mean_welfare_difference"] = float(np.mean(matrix_w[:, ia] - matrix_w[:, ib]))
            pair_welfare[key] = wx
            welfare_raw_p[key] = wx["p"]

        agreement_pair_adj = holm(agreement_raw_p)
        welfare_pair_adj = holm(welfare_raw_p)
        for key in pair_agreement:
            pair_agreement[key]["holm_p"] = agreement_pair_adj[key]
            pair_welfare[key]["holm_p"] = welfare_pair_adj[key]

        by_model = {}
        for buyer in EXPECTED_BUYERS:
            subset = [row for row in bargaining if row["buyer"] == buyer]
            by_model[buyer] = {
                "n": len(subset),
                "agreements": sum(row.get("agreement") is True for row in subset),
                "agreement_rate": safe_mean([1 if row.get("agreement") is True else 0 for row in subset]),
                "mean_normalized_realized_buyer_surplus": safe_mean(
                    [row.get("normalized_realized_buyer_surplus") for row in subset]
                ),
                "mean_conditional_normalized_price": safe_mean(
                    [row.get("normalized_price") for row in subset if row.get("agreement") is True]
                ),
            }

        by_model_product = {}
        for buyer in EXPECTED_BUYERS:
            for product in EXPECTED_PRODUCTS:
                subset = [
                    row for row in bargaining
                    if row["buyer"] == buyer and row["product_id"] == product
                ]
                by_model_product[f"{buyer}|{product}"] = {
                    "n": len(subset),
                    "agreements": sum(row.get("agreement") is True for row in subset),
                    "agreement_rate": safe_mean(
                        [1 if row.get("agreement") is True else 0 for row in subset]
                    ),
                    "mean_normalized_realized_buyer_surplus": safe_mean(
                        [row.get("normalized_realized_buyer_surplus") for row in subset]
                    ),
                }

        pairwise_by_product = {}
        for product in EXPECTED_PRODUCTS:
            pblocks = [key for key in ordered_blocks if key[0] == product]
            for a, b in pair_labels:
                av, bv, aw, bw = [], [], [], []
                for key in pblocks:
                    by_buyer = {row["buyer"]: row for row in blocks[key]}
                    av.append(1 if by_buyer[a]["agreement"] is True else 0)
                    bv.append(1 if by_buyer[b]["agreement"] is True else 0)
                    aw.append(float(by_buyer[a]["normalized_realized_buyer_surplus"]))
                    bw.append(float(by_buyer[b]["normalized_realized_buyer_surplus"]))
                pairwise_by_product[f"{product}|{a}_minus_{b}"] = {
                    "n_blocks": len(pblocks),
                    "agreement_difference_pp": float(100.0 * np.mean(np.asarray(av) - np.asarray(bv))),
                    "welfare_difference": float(np.mean(np.asarray(aw) - np.asarray(bw))),
                }

        interaction_agreement = model_product_interaction(
            [
                {**row, "agreement_num": 1.0 if row.get("agreement") is True else 0.0}
                for row in bargaining
            ],
            "agreement_num",
        )
        interaction_welfare = model_product_interaction(
            bargaining, "normalized_realized_buyer_surplus"
        )

        confirmatory_pass = (
            omnibus_adj["P1_trade_formation"] <= 0.05
            or omnibus_adj["P2_buyer_welfare"] <= 0.05
        )

        result["confirmatory"] = {
            "status": "pass" if confirmatory_pass else "fail",
            "P1_trade_formation": {
                "test": "Cochran Q",
                "statistic": q_stat,
                "df": 2,
                "raw_p": p1,
                "holm_p": omnibus_adj["P1_trade_formation"],
                "n_matched_blocks": len(ordered_blocks),
            },
            "P2_buyer_welfare": {
                "test": "Friedman",
                "statistic": p2_stat,
                "df": 2,
                "raw_p": p2,
                "holm_p": omnibus_adj["P2_buyer_welfare"],
                "n_matched_blocks": len(ordered_blocks),
                "outcome": "I(trade)*(buyer_value-final_price)/buyer_value",
            },
            "by_model": by_model,
            "pairwise_agreement": pair_agreement,
            "pairwise_welfare": pair_welfare,
            "by_model_product": by_model_product,
            "pairwise_by_product": pairwise_by_product,
            "secondary_interaction_agreement": interaction_agreement,
            "secondary_interaction_welfare": interaction_welfare,
        }

    (OUT / "e03_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    fieldnames = sorted({key for row in rows for key in row if key not in {"events", "violations"}})
    with (OUT / "episodes.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})

    lines = [
        "# Last Price E03 — Frozen Aggregate Report",
        "",
        f"Technical gate: **{'PASS' if technical_pass else 'FAIL'}**",
        f"- source files: {len(files)} / {EXPECTED_FILES}",
        f"- episodes: {len(rows)} / {EXPECTED_ROWS}",
        f"- bargaining: {len(bargaining)} / {EXPECTED_BARGAINING}",
        f"- posted controls: {len(posted)} / {EXPECTED_POSTED}",
        f"- infrastructure failures: {len(infra)}",
        f"- menu violations: {menu_violations}",
        f"- menu reconstruction mismatches: {reconstruction_mismatches}",
        f"- over-budget agreements: {len(over_budget)}",
        f"- below-cost agreements: {len(below_cost)}",
        f"- matched bargaining blocks: {len(blocks)} / {EXPECTED_BLOCKS}",
        "",
    ]
    if blockers:
        lines += ["## Technical blockers", ""] + [f"- {b}" for b in blockers] + [""]
    if technical_pass:
        c = result["confirmatory"]
        lines += [
            "## Confirmatory outcomes",
            "",
            f"Confirmatory gate: **{c['status'].upper()}**",
            "",
            "### P1 — trade formation",
            f"- Cochran Q: {c['P1_trade_formation']['statistic']:.6g}",
            f"- raw p: {c['P1_trade_formation']['raw_p']:.6g}",
            f"- Holm p: {c['P1_trade_formation']['holm_p']:.6g}",
            "",
            "### P2 — realized buyer welfare",
            f"- Friedman statistic: {c['P2_buyer_welfare']['statistic']:.6g}",
            f"- raw p: {c['P2_buyer_welfare']['raw_p']:.6g}",
            f"- Holm p: {c['P2_buyer_welfare']['holm_p']:.6g}",
            "",
            "### By model",
            "",
            "| buyer | agreements | n | agreement rate | mean normalized realized buyer surplus |",
            "|---|---:|---:|---:|---:|",
        ]
        for buyer in EXPECTED_BUYERS:
            item = c["by_model"][buyer]
            lines.append(
                f"| {buyer} | {item['agreements']} | {item['n']} | "
                f"{item['agreement_rate']:.4f} | {item['mean_normalized_realized_buyer_surplus']:.4f} |"
            )
        lines += [
            "",
            "## Interpretation boundary",
            "",
            "Conditional price is secondary in E03. The primary question is whether changing the buyer model changes trade formation and/or unconditional realized buyer welfare under a mechanically finite feasible action space.",
            "",
        ]
    else:
        lines += [
            "## Confirmatory status",
            "",
            "P1 and P2 are **not adjudicated** because the preregistered technical gate failed. No missing or failed cell is imputed.",
            "",
        ]

    (OUT / "E03_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"technical_gate_pass": technical_pass, "blockers": blockers, "rows": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
