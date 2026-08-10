import glob, json, random, statistics
from collections import defaultdict
from pathlib import Path
from scipy.stats import wilcoxon

BUYERS = ("qwen17", "gemma4", "llama3")
PRODUCTS = ("headphones", "suitcase", "chair")
EXPECTED = 702
BUDGETS = {"headphones": 250, "suitcase": 180, "chair": 400}


def avg(x): return statistics.fmean(x) if x else None

def wp(x):
    if not x: return None
    if all(abs(v) < 1e-12 for v in x): return 1.0
    return float(wilcoxon(x, zero_method="wilcox", alternative="two-sided", method="auto").pvalue)

def ci(x, n=5000):
    if not x: return [None, None]
    if len(x) == 1: return [x[0], x[0]]
    rng = random.Random(20260810)
    b = [statistics.fmean(x[rng.randrange(len(x))] for _ in x) for _ in range(n)]
    b.sort()
    return [b[int(.025 * (n - 1))], b[int(.975 * (n - 1))]]

def rep(x):
    c = ci(x)
    return {"n": len(x), "mean_ratio": avg(x), "mean_pp": avg(x) * 100 if x else None,
            "ci95_pp": [v * 100 if v is not None else None for v in c],
            "negative": sum(v < 0 for v in x), "zero": sum(abs(v) < 1e-12 for v in x),
            "positive": sum(v > 0 for v in x), "p": wp(x)}

def rep_pct(x):
    c = ci(x)
    return {"n": len(x), "mean_pct": avg(x), "ci95_pct": c,
            "negative": sum(v < 0 for v in x), "zero": sum(abs(v) < 1e-12 for v in x),
            "positive": sum(v > 0 for v in x), "p": wp(x)}

def holm(pdict):
    valid = [(k, v) for k, v in pdict.items() if v is not None]
    valid.sort(key=lambda kv: kv[1])
    out, running, m = {}, 0.0, len(valid)
    for i, (k, p) in enumerate(valid):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return {k: out.get(k) for k in pdict}

def load():
    rows, files = [], sorted(glob.glob("collected/**/episodes.json", recursive=True))
    for f in files: rows += json.load(open(f))["episodes"]
    return rows, files

def price_map(rows, buyer, pred=lambda r: True):
    return {(r["product_id"], r["tightness"], r["anchor"], r["order"], r["state"], r["seed_index"]): r["normalized_price"]
            for r in rows if r["seller"] != "posted" and r["buyer"] == buyer and pred(r)
            and r.get("agreement") and r.get("normalized_price") is not None}

def mdiff(rows, a, b, pred=lambda r: True):
    A, B = price_map(rows, a, pred), price_map(rows, b, pred)
    keys = sorted(set(A) & set(B))
    return [A[k] - B[k] for k in keys]

def effect(rows, buyer, kind):
    m = defaultdict(dict)
    for r in rows:
        if r["seller"] == "posted" or r["buyer"] != buyer or not r.get("agreement") or r.get("normalized_price") is None: continue
        if kind == "anchor":
            k = (r["product_id"], r["tightness"], r["order"], r["state"], r["seed_index"])
            m[k][r["anchor"]] = r["normalized_price"]
        else:
            k = (r["product_id"], r["tightness"], r["anchor"], r["state"], r["seed_index"])
            m[k][r["order"]] = r["normalized_price"]
    if kind == "anchor": return {k: d["shown"] - d["hidden"] for k, d in m.items() if "shown" in d and "hidden" in d}
    return {k: d["seller_first"] - d["buyer_first"] for k, d in m.items() if "seller_first" in d and "buyer_first" in d}

def did(A, B):
    keys = sorted(set(A) & set(B))
    return [A[k] - B[k] for k in keys]

def inflation(rows, buyer):
    m = defaultdict(dict)
    for r in rows:
        if r["seller"] == "posted" or r["buyer"] != buyer or not r.get("agreement") or r.get("final_price") is None: continue
        k = (r["product_id"], r["tightness"], r["anchor"], r["order"], r["seed_index"])
        m[k][r["state"]] = r["final_price"]
    return {k: (d["shock_10pct"] / d["baseline"] - 1) * 100 for k, d in m.items()
            if "baseline" in d and "shock_10pct" in d and d["baseline"] > 0}


def main():
    rows, files = load()
    barg = [r for r in rows if r["seller"] != "posted"]
    duplicate_count = len(rows) - len({r["episode_id"] for r in rows})
    infra = sum(r.get("infrastructure_failure") is True for r in rows)
    schema_violations = sum(r.get("schema_violations", 0) for r in rows)

    bounds = 0
    for r in rows:
        if r.get("agreement") and r.get("final_price") is not None:
            if r["final_price"] > BUDGETS[r["product_id"]] + 1e-9: bounds += 1
            if r["seller"] != "posted" and r["final_price"] + 1e-9 < r["seller_cost"]: bounds += 1

    posted = defaultdict(list)
    for r in rows:
        if r["seller"] == "posted":
            posted[(r["product_id"], r["tightness"], r["state"])].append(r)
    posted_failures, posted_max_price_range = 0, 0.0
    for key, group in posted.items():
        if len(group) != 3 or len({r.get("agreement") for r in group}) != 1:
            posted_failures += 1
            continue
        prices = [r["final_price"] for r in group if r.get("agreement") and r.get("final_price") is not None]
        if prices:
            posted_max_price_range = max(posted_max_price_range, max(prices) - min(prices))

    audit = {
        "rows": len(rows), "expected": EXPECTED, "source_files": len(files), "duplicates": duplicate_count,
        "infrastructure_failures": infra, "schema_violations": schema_violations,
        "price_constraint_failures": bounds, "posted_control_failures": posted_failures,
        "posted_price_max_model_range": posted_max_price_range,
    }
    audit["technical_gate_pass"] = (len(rows) == EXPECTED and len(files) == 9 and duplicate_count == 0 and infra == 0
                                    and schema_violations == 0 and bounds == 0 and posted_failures == 0
                                    and posted_max_price_range <= 1e-9)

    agreement = {}
    for b in BUYERS:
        rr = [r for r in barg if r["buyer"] == b]
        tr = [r for r in rr if r.get("agreement")]
        agreement[b] = {"trades": len(tr), "episodes": len(rr), "rate": len(tr) / len(rr) if rr else None,
                        "mean_price_reference_pct": avg([r["normalized_price"] * 100 for r in tr if r.get("normalized_price") is not None]),
                        "destroyed": sum(r.get("trade_destroyed") is True for r in rr)}

    p1_values = mdiff(rows, "llama3", "qwen17", lambda r: r["anchor"] == "hidden" and r["order"] == "buyer_first")
    p1 = rep(p1_values)
    ae = {b: effect(rows, b, "anchor") for b in BUYERS}
    oe = {b: effect(rows, b, "order") for b in BUYERS}
    p2_values = did(ae["llama3"], ae["qwen17"])
    p2 = rep(p2_values)
    adj = holm({"P1": p1["p"], "P2": p2["p"]})
    p1["holm_p"], p2["holm_p"] = adj["P1"], adj["P2"]

    product_primary = {}
    p1_negative_products = p2_positive_products = 0
    for product in PRODUCTS:
        pv1 = mdiff(rows, "llama3", "qwen17", lambda r, p=product: r["product_id"] == p and r["anchor"] == "hidden" and r["order"] == "buyer_first")
        aL = {k: v for k, v in ae["llama3"].items() if k[0] == product}
        aQ = {k: v for k, v in ae["qwen17"].items() if k[0] == product}
        pv2 = did(aL, aQ)
        r1, r2 = rep(pv1), rep(pv2)
        product_primary[product] = {"P1": r1, "P2": r2}
        if r1["mean_pp"] is not None and r1["mean_pp"] < 0: p1_negative_products += 1
        if r2["mean_pp"] is not None and r2["mean_pp"] > 0: p2_positive_products += 1

    substantive_stats_pass = (p1["mean_pp"] is not None and p1["mean_pp"] < 0 and p2["mean_pp"] is not None and p2["mean_pp"] > 0
                              and p1.get("holm_p") is not None and p1["holm_p"] <= .05
                              and p2.get("holm_p") is not None and p2["holm_p"] <= .05
                              and p1_negative_products >= 2 and p2_positive_products >= 2)
    audit["substantive_stats_pass"] = substantive_stats_pass
    audit["substantive_replication_pass"] = bool(audit["technical_gate_pass"] and substantive_stats_pass)

    anchor = {b: rep(list(ae[b].values())) for b in BUYERS}
    order = {b: rep(list(oe[b].values())) for b in BUYERS}
    tight = {}
    for b in BUYERS:
        tight[b] = {}
        for t in ("loose", "medium", "tight"):
            vals = [r["normalized_price"] * 100 for r in barg if r["buyer"] == b and r["tightness"] == t and r.get("agreement") and r.get("normalized_price") is not None]
            tight[b][t] = {"n": len(vals), "mean_price_reference_pct": avg(vals)}

    im = {b: inflation(rows, b) for b in BUYERS}
    inf = {b: rep_pct(list(im[b].values())) for b in BUYERS}
    infdiff = {}
    for a, b in (("qwen17", "gemma4"), ("qwen17", "llama3"), ("gemma4", "llama3")):
        infdiff[f"{a}_minus_{b}"] = rep_pct(did(im[a], im[b]))

    out = {
        "experiment_id": "last-price-e02d-constrained-schema-20260810",
        "audit": audit,
        "primary": {"P1_hidden_buyer_first_llama_minus_qwen": p1, "P2_anchor_DID_llama_minus_qwen": p2},
        "product_primary": product_primary,
        "agreement": agreement,
        "anchor_effect_by_model": anchor,
        "order_effect_by_model": order,
        "tightness": tight,
        "experienced_inflation": inf,
        "inflation_differences": infdiff,
    }
    Path("aggregate").mkdir(exist_ok=True)
    Path("aggregate/E02D_RESULTS.json").write_text(json.dumps(out, indent=2))
    Path("aggregate/E02D_AUDIT.json").write_text(json.dumps(audit, indent=2))
    lines = [
        "# Last Price E02-D — Constrained-Action Validation", "",
        f"Rows: **{len(rows)} / {EXPECTED}**", f"Technical gate: **{'PASS' if audit['technical_gate_pass'] else 'FAIL'}**",
        f"Substantive stats: **{'PASS' if substantive_stats_pass else 'FAIL'}**",
        f"Substantive replication: **{'PASS' if audit['substantive_replication_pass'] else 'FAIL'}**",
        f"Infrastructure failures: **{infra}**", f"Schema violations: **{schema_violations}**",
        f"Posted control failures: **{posted_failures}**", "", "## Primary", "",
        f"P1 hidden-anchor buyer-first Llama−Qwen: **{p1['mean_pp']} pp**, 95% CI {p1['ci95_pp']}, p={p1['p']}, Holm p={p1['holm_p']}.",
        f"P2 anchor DID Llama−Qwen: **{p2['mean_pp']} pp**, 95% CI {p2['ci95_pp']}, p={p2['p']}, Holm p={p2['holm_p']}.",
        f"P1 negative direction products: **{p1_negative_products}/3**; P2 positive direction products: **{p2_positive_products}/3**.",
        "", "## Product primary",
    ]
    for p in PRODUCTS:
        lines.append(f"- {p}: P1 {product_primary[p]['P1']['mean_pp']} pp; P2 {product_primary[p]['P2']['mean_pp']} pp")
    lines += ["", "## Agreement"]
    for b in BUYERS:
        lines.append(f"- {b}: {agreement[b]['trades']}/{agreement[b]['episodes']} trades; mean price/reference {agreement[b]['mean_price_reference_pct']}%")
    lines += ["", "## Interpretation boundary", "Open-weight structured-decoding validation only; commercial-model generalization remains untested."]
    Path("aggregate/E02D_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
