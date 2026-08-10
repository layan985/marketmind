import json, math, os
from datetime import datetime, timezone
from pathlib import Path
from experiments import last_price_e02a_scale as base

TIGHT = {"loose": 0.45, "medium": 0.65, "tight": 0.85}
STATES = (("baseline", 1.0), ("shock_10pct", 1.1))
ANCHORS = ("shown", "hidden")
ORDERS = ("buyer_first", "seller_first")
N = int(os.environ.get("N_SEEDS", "3"))
P = base.P

def seed_for(t, i):
    return 20260810 + int(base.sha(f"e02b|{base.PRODUCT_ID}|{t}|{i}")[:8], 16) % 10000000

def posted(t, ratio, state, mult, seed):
    cost = base.r2(P["buyer_value"] * ratio * mult); price = base.r2(cost * 1.04); events, infra = [], None
    try:
        prompt = f"Product: {P['name']}. Public posted price: ${price}. The price is non-negotiable. Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. The only legal actions are accept or walk_away. Choose one."
        c = base.model_call(base.BUYER_MODEL, base.BUYER_SYSTEM, prompt, seed); p = c["parsed"] or {}; a = p.get("action"); valid = a in ("accept", "walk_away")
        if not valid: a = "invalid"
        agree = valid and a == "accept"; events.append(base.event(base.BUYER_LABEL, a, None, p, c))
    except Exception as exc: agree, infra = None, str(exc)
    efficient = P["buyer_value"] > cost
    return {"episode_id": base.sha(f"e02b|{base.BUYER_LABEL}|{base.PRODUCT_ID}|posted|{t}|{state}")[:24], "buyer": base.BUYER_LABEL, "buyer_model": base.BUYER_MODEL, "seller": "posted", "seller_model": "posted_price_v1", "product_id": base.PRODUCT_ID, "tightness": t, "anchor": "posted_price", "order": "posted", "seed_index": 0, "seed": seed, "state": state, "seller_cost": cost, "agreement": agree, "final_price": price if agree else None, "normalized_price": base.r2(price / P["reference_price"]) if agree else None, "buyer_surplus": base.r2(P["buyer_value"] - price) if agree else 0, "seller_profit": base.r2(price - cost) if agree else 0, "trade_destroyed": None if agree is None else bool(efficient and not agree), "invalid_actions": sum(e["action"] == "invalid" for e in events), "infrastructure_failure": infra is not None, "error": infra, "turns": len(events), "events": events}

def bargain(t, ratio, anchor, order, state, mult, i, seed):
    cost = base.r2(P["buyer_value"] * ratio * mult); events, outstanding, agree, final, bad, infra = [], None, False, None, 0, None; turn = "buyer" if order == "buyer_first" else "seller"
    try:
        for step in range(6):
            is_buyer = turn == "buyer"; actor = base.BUYER_LABEL if is_buyer else base.SELLER_LABEL; model = base.BUYER_MODEL if is_buyer else base.SELLER_MODEL; system = base.BUYER_SYSTEM if is_buyer else base.SELLER_SYSTEM
            private = f"Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. You do not know seller cost." if is_buyer else f"Your private marginal cost is ${cost}. You do not know buyer value or budget."
            anchor_text = f"Public reference price: ${P['reference_price']}." if anchor == "shown" else "No public numerical reference price is provided."
            legal = "There is no outstanding offer. Legal actions now: offer or walk_away." if outstanding is None else f"Outstanding offer ${outstanding['price']} from {outstanding['actor']}. Legal actions now: accept, reject, offer a counteroffer, or walk_away."
            prompt = f"Product: {P['name']}. {anchor_text} {private}\nPublic history:\n{base.history(events)}\n{legal}\nChoose the next action."
            c = base.model_call(model, system, prompt, seed + step); p = c["parsed"] or {}; a, x = p.get("action"), p.get("price"); x = float(x) if isinstance(x, (int, float)) and math.isfinite(float(x)) else None; valid = a in ("offer", "accept", "reject", "walk_away")
            if outstanding is None and a in ("accept", "reject"): valid = False
            if a == "offer": valid = valid and x is not None and x > 0 and (not is_buyer or x <= P["budget"]) and (is_buyer or x >= cost)
            if a == "accept":
                valid = valid and outstanding is not None and outstanding["actor"] != actor
                if valid and is_buyer: valid = outstanding["price"] <= P["budget"]
                if valid and not is_buyer: valid = outstanding["price"] >= cost
            if not valid: bad += 1; a = "invalid"
            events.append(base.event(actor, a, x, p, c))
            if a == "offer": outstanding = {"actor": actor, "price": base.r2(x)}
            elif a == "accept": agree, final = True, outstanding["price"]; break
            elif a == "reject": outstanding = None
            elif a == "walk_away": break
            turn = "seller" if is_buyer else "buyer"
    except Exception as exc: infra = str(exc)
    efficient = P["buyer_value"] > cost
    return {"episode_id": base.sha(f"e02b|{base.BUYER_LABEL}|{base.PRODUCT_ID}|bargain|{t}|{anchor}|{order}|{state}|{i}")[:24], "buyer": base.BUYER_LABEL, "buyer_model": base.BUYER_MODEL, "seller": base.SELLER_LABEL, "seller_model": base.SELLER_MODEL, "product_id": base.PRODUCT_ID, "tightness": t, "anchor": anchor, "order": order, "seed_index": i, "seed": seed, "state": state, "seller_cost": cost, "agreement": None if infra else agree, "final_price": base.r2(final) if agree else None, "normalized_price": base.r2(final / P["reference_price"]) if agree else None, "buyer_surplus": base.r2(P["buyer_value"] - final) if agree else 0, "seller_profit": base.r2(final - cost) if agree else 0, "trade_destroyed": None if infra else bool(efficient and not agree), "invalid_actions": bad, "infrastructure_failure": infra is not None, "error": infra, "turns": len(events), "events": events}

def main():
    rows = []
    for t, ratio in TIGHT.items():
        for state, mult in STATES: rows.append(posted(t, ratio, state, mult, seed_for(t, 0)))
        for i in range(N):
            s = seed_for(t, i)
            for anchor in ANCHORS:
                for order in ORDERS:
                    for state, mult in STATES: rows.append(bargain(t, ratio, anchor, order, state, mult, i, s))
    expected = 6 + 3 * N * 2 * 2 * 2; assert len(rows) == expected
    summary = {"buyer": base.BUYER_LABEL, "buyer_model": base.BUYER_MODEL, "seller_model": base.SELLER_MODEL, "product_id": base.PRODUCT_ID, "n_seeds": N, "episodes": len(rows), "bargaining_episodes": sum(r["seller"] != "posted" for r in rows), "agreements": sum(r.get("agreement") is True for r in rows), "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows), "invalid_actions": sum(r.get("invalid_actions", 0) for r in rows)}
    out = {"experiment_id": "last-price-e02b-mechanism-test-20260810", "generated_at": datetime.now(timezone.utc).isoformat(), "buyer_model": base.BUYER_MODEL, "seller_model": base.SELLER_MODEL, "product": {"product_id": base.PRODUCT_ID, **P}, "summary": summary, "episodes": rows}
    target = Path("artifacts") / f"{base.BUYER_LABEL}-{base.PRODUCT_ID}"; target.mkdir(parents=True, exist_ok=True); (target / "episodes.json").write_text(json.dumps(out, indent=2)); (target / "summary.json").write_text(json.dumps(summary, indent=2)); print(json.dumps(summary, indent=2))

if __name__ == "__main__": main()
