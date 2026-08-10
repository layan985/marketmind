import glob, json, random, statistics
from collections import Counter, defaultdict
from pathlib import Path
from scipy.stats import wilcoxon

BUYERS = ("qwen17", "gemma4", "llama3")
PRODUCTS = ("headphones", "suitcase", "chair")
EXPECTED = 702


def avg(x):
    return statistics.fmean(x) if x else None


def wp(x):
    if not x:
        return None
    if all(abs(v) < 1e-12 for v in x):
        return 1.0
    return float(wilcoxon(x, zero_method="wilcox", alternative="two-sided", method="auto").pvalue)


def ci(x, n=5000):
    if not x:
        return [None, None]
    if len(x) == 1:
        return [x[0], x[0]]
    rng = random.Random(20260810)
    boot = [statistics.fmean(x[rng.randrange(len(x))] for _ in x) for _ in range(n)]
    boot.sort()
    return [boot[int(0.025 * (n - 1))], boot[int(0.975 * (n - 1))]]


def rep_ratio(x):
    c = ci(x)
    return {
        "n": len(x),
        "mean_ratio": avg(x),
        "mean_pp": avg(x) * 100 if x else None,
        "ci95_pp": [v * 100 if v is not None else None for v in c],
        "negative": sum(v < 0 for v in x),
        "zero": sum(abs(v) < 1e-12 for v in x),
        "positive": sum(v > 0 for v in x),
        "p": wp(x),
    }


def rep_pct(x):
    c = ci(x)
    return {
        "n": len(x),
        "mean_pct": avg(x),
        "ci95_pct": c,
        "negative": sum(v < 0 for v in x),
        "zero": sum(abs(v) < 1e-12 for v in x),
        "positive": sum(v > 0 for v in x),
        "p": wp(x),
    }


def holm(pvals):
    valid = [(k, v) for k, v in pvals.items() if v is not None]
    valid.sort(key=lambda kv: kv[1])
    m = len(valid)
    adjusted = {}
    running = 0.0
    for i, (k, p) in enumerate(valid):
        raw = min(1.0, (m - i) * p)
        running = max(running, raw)
        adjusted[k] = running
    return {k: adjusted.get(k) for k in pvals}


def load():
    rows = []
    files = sorted(glob.glob("collected/**/episodes.json", recursive=True))
    for f in files:
        rows += json.load(open(f))["episodes"]
    return rows, files


def price_map(rows, buyer, pred=lambda r: True):
    return {
        (r["product_id"], r["tightness"], r["anchor"], r["order"], r["state"], r["seed_index"]): r["normalized_price"]
        for r in rows
        if r["seller"] != "posted"
        and r["buyer"] == buyer
        and pred(r)
        and r.get("agreement")
        and r.get("normalized_price") is not None
    }


def mdiff(rows, a, b, pred=lambda r: True):
    A = price_map(rows, a, pred)
    B = price_map(rows, b, pred)
    keys = sorted(set(A) & set(B))
    return [A[k] - B[k] for k in keys]


def effect(rows, buyer, kind, pred=lambda r: True):
    matched = defaultdict(dict)
    for r in rows:
        if r["seller"] == "posted" or r["buyer"] != buyer or not pred(r):
            continue
        if not r.get("agreement") or r.get("normalized_price") is None:
            continue
        if kind == "anchor":
            key = (r["product_id"], r["tightness"], r["order"], r["state"], r["seed_index"])
            matched[key][r["anchor"]] = r["normalized_price"]
        else:
            key = (r["product_id"], r["tightness"], r["anchor"], r["state"], r["seed_index"])
            matched[key][r["order"]] = r["normalized_price"]
    if kind == "anchor":
        return {k: d["shown"] - d["hidden"] for k, d in matched.items() if "shown" in d and "hidden" in d}
    return {k: d["seller_first"] - d["buyer_first"] for k, d in matched.items() if "seller_first" in d and "buyer_first" in d}


def did(A, B):
    keys = sorted(set(A) & set(B))
    return [A[k] - B[k] for k in keys]


def inflation(rows, buyer):
    matched = defaultdict(dict)
    for r in rows:
        if r["seller"] == "posted" or r["buyer"] != buyer:
            continue
        if not r.get("agreement") or r.get("final_price") is None:
            continue
        key = (r["product_id"], r["tightness"], r["anchor"], r["order"], r["seed_index"])
        matched[key][r["state"]] = r["final_price"]
    return {
        k: (d["shock_10pct"] / d["baseline"] - 1) * 100
        for k, d in matched.items()
        if "baseline" in d and "shock_10pct" in d and d["baseline"] > 0
    }


def main():
    rows, files = load()
    bargaining = [r for r in rows if r["seller"] != "posted"]
    duplicates = len(rows) - len({r["episode_id"] for r in rows})
    infra = sum(r.get("infrastructure_failure") is True for r in rows)
    first_invalid = sum(r.get("first_invalid_attempts", 0) for r in rows)
    retries = sum(r.get("retries_used", 0) for r in rows)
    retry_successes = sum(r.get("retry_successes", 0) for r in rows)
    unresolved = sum(r.get("unresolved_protocol_failures", 0) for r in rows)

    posted = defaultdict(list)
    for r in rows:
        if r["seller"] == "posted" and r.get("agreement") and r.get("final_price") is not None:
            posted[(r["product_id"], r["tightness"], r["state"])].append(r["final_price"])
    posted_max_range = max((max(v) - min(v) for v in posted.values()), default=None)

    bounds = 0
    budgets = {"headphones": 250, "suitcase": 180, "chair": 400}
    for r in rows:
        if r.get("agreement") and r.get("final_price") is not None:
            if r["final_price"] > budgets[r["product_id"]] + 1e-9:
                bounds += 1
            if r["seller"] != "posted" and r["final_price"] + 1e-9 < r["seller_cost"]:
                bounds += 1

    audit = {
        "rows": len(rows),
        "expected": EXPECTED,
        "source_files": len(files),
        "duplicates": duplicates,
        "infrastructure_failures": infra,
        "first_invalid_attempts": first_invalid,
        "retries_used": retries,
        "retry_successes": retry_successes,
        "retry_success_rate": retry_successes / retries if retries else None,
        "unresolved_protocol_failures": unresolved,
        "price_constraint_failures": bounds,
        "posted_price_max_model_range": posted_max_range,
    }
    audit["technical_release_gate_pass"] = (
        len(rows) == EXPECTED
        and len(files) == 9
        and duplicates == 0
        and infra == 0
        and unresolved == 0
        and bounds == 0
        and posted_max_range is not None
        and posted_max_range <= 1e-9
    )

    agreement = {}
    for b in BUYERS:
        rr = [r for r in bargaining if r["buyer"] == b]
        tr = [r for r in rr if r.get("agreement")]
        agreement[b] = {
            "trades": len(tr),
            "episodes": len(rr),
            "rate": len(tr) / len(rr) if rr else None,
            "mean_price_reference_pct": avg([r["normalized_price"] * 100 for r in tr if r.get("normalized_price") is not None]),
            "destroyed": sum(r.get("trade_destroyed") is True for r in rr),
        }

    p1 = rep_ratio(mdiff(rows, "llama3", "qwen17", lambda r: r["anchor"] == "hidden" and r["order"] == "buyer_first"))
    anchor_effect = {b: effect(rows, b, "anchor") for b in BUYERS}
    order_effect = {b: effect(rows, b, "order") for b in BUYERS}
    p2 = rep_ratio(did(anchor_effect["llama3"], anchor_effect["qwen17"]))
    adjusted = holm({"P1": p1["p"], "P2": p2["p"]})
    p1["holm_p"] = adjusted["P1"]
    p2["holm_p"] = adjusted["P2"]

    product_primary = {}
    p1_direction_products = 0
    p2_direction_products = 0
    for product in PRODUCTS:
        pp1 = rep_ratio(mdiff(rows, "llama3", "qwen17", lambda r, p=product: r["product_id"] == p and r["anchor"] == "hidden" and r["order"] == "buyer_first"))
        l_ae = effect(rows, "llama3", "anchor", lambda r, p=product: r["product_id"] == p)
        q_ae = effect(rows, "qwen17", "anchor", lambda r, p=product: r["product_id"] == p)
        pp2 = rep_ratio(did(l_ae, q_ae))
        product_primary[product] = {"P1": pp1, "P2": pp2}
        p1_direction_products += int(pp1["mean_pp"] is not None and pp1["mean_pp"] < 0)
        p2_direction_products += int(pp2["mean_pp"] is not None and pp2["mean_pp"] > 0)

    substantive_pass = bool(
        audit["technical_release_gate_pass"]
        and p1["mean_pp"] is not None and p1["mean_pp"] < 0
        and p2["mean_pp"] is not None and p2["mean_pp"] > 0
        and p1["holm_p"] is not None and p1["holm_p"] <= 0.05
        and p2["holm_p"] is not None and p2["holm_p"] <= 0.05
        and p1_direction_products >= 2
        and p2_direction_products >= 2
    )

    first_invalid_by_actor = Counter()
    first_invalid_by_reason = Counter()
    first_invalid_by_tightness = Counter()
    first_invalid_by_buyer = Counter()
    for r in rows:
        for a in r.get("rejected_attempts", []):
            if a.get("attempt") != 1:
                continue
            actor_type = "buyer" if a.get("actor") == r.get("buyer") else "seller"
            first_invalid_by_actor[actor_type] += 1
            first_invalid_by_reason[a.get("reason") or "unknown"] += 1
            first_invalid_by_tightness[r.get("tightness") or "posted"] += 1
            first_invalid_by_buyer[r.get("buyer") or "unknown"] += 1

    anchor = {b: rep_ratio(list(anchor_effect[b].values())) for b in BUYERS}
    order = {b: rep_ratio(list(order_effect[b].values())) for b in BUYERS}
    inflation_maps = {b: inflation(rows, b) for b in BUYERS}
    experienced_inflation = {b: rep_pct(list(inflation_maps[b].values())) for b in BUYERS}
    inflation_differences = {}
    for a, b in (("qwen17", "gemma4"), ("qwen17", "llama3"), ("gemma4", "llama3")):
        inflation_differences[f"{a}_minus_{b}"] = rep_pct(did(inflation_maps[a], inflation_maps[b]))

    out = {
        "experiment_id": "last-price-e02c-protocol-robustness-20260810",
        "audit": audit,
        "validation": {
            "substantive_replication_pass": substantive_pass,
            "P1_direction_products": p1_direction_products,
            "P2_direction_products": p2_direction_products,
        },
        "primary": {
            "P1_hidden_buyer_first_llama_minus_qwen": p1,
            "P2_anchor_DID_llama_minus_qwen": p2,
            "by_product": product_primary,
        },
        "agreement": agreement,
        "protocol": {
            "first_invalid_by_actor": dict(first_invalid_by_actor),
            "first_invalid_by_reason": dict(first_invalid_by_reason),
            "first_invalid_by_tightness": dict(first_invalid_by_tightness),
            "first_invalid_by_buyer_condition": dict(first_invalid_by_buyer),
        },
        "anchor_effect_by_model": anchor,
        "order_effect_by_model": order,
        "experienced_inflation": experienced_inflation,
        "inflation_differences": inflation_differences,
    }

    Path("aggregate").mkdir(exist_ok=True)
    Path("aggregate/E02C_RESULTS.json").write_text(json.dumps(out, indent=2))
    Path("aggregate/E02C_AUDIT.json").write_text(json.dumps(audit, indent=2))
    lines = [
        "# Last Price E02-C — Protocol-Compliance Robustness",
        "",
        f"Rows: **{len(rows)} / {EXPECTED}**",
        f"Technical release gate: **{'PASS' if audit['technical_release_gate_pass'] else 'FAIL'}**",
        f"Substantive replication: **{'PASS' if substantive_pass else 'FAIL'}**",
        f"Infrastructure failures: **{infra}**",
        f"First-attempt illegal actions: **{first_invalid}**",
        f"Retry successes: **{retry_successes}/{retries}**",
        f"Unresolved protocol failures: **{unresolved}**",
        f"Posted-price max model range: **{posted_max_range}**",
        "",
        "## Primary",
        "",
        f"P1 hidden-anchor buyer-first Llama−Qwen: **{p1['mean_pp']} pp**, 95% CI {p1['ci95_pp']}, p={p1['p']}, Holm p={p1['holm_p']}.",
        f"P2 anchor DID (Llama−Qwen): **{p2['mean_pp']} pp**, 95% CI {p2['ci95_pp']}, p={p2['p']}, Holm p={p2['holm_p']}.",
        f"Directional consistency: P1 {p1_direction_products}/3 products; P2 {p2_direction_products}/3 products.",
        "",
        "## Interpretation boundary",
        "Open-weight protocol-robustness test only; commercial-model generalization remains untested.",
    ]
    Path("aggregate/E02C_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
