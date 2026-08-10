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
CORRECTION = "PROTOCOL CORRECTION: Your previous action was illegal under the published protocol. Return exactly one legal JSON action now. Do not explain the error."


def seed_for(t, i):
    # Deliberately preserve E02-B initial seeds for paired enforcement robustness.
    return 20260810 + int(base.sha(f"e02b|{base.PRODUCT_ID}|{t}|{i}")[:8], 16) % 10000000


def parse_action(call):
    p = call.get("parsed") or {}
    a = p.get("action")
    raw_x = p.get("price")
    x = float(raw_x) if isinstance(raw_x, (int, float)) and math.isfinite(float(raw_x)) else None
    return p, a, x


def legality(action, price, is_buyer, actor, cost, outstanding, posted=False):
    if posted:
        if action not in ("accept", "walk_away"):
            return False, "posted_action"
        return True, None
    if action not in ("offer", "accept", "reject", "walk_away"):
        return False, "unknown_action"
    if outstanding is None and action in ("accept", "reject"):
        return False, "no_outstanding_offer"
    if action == "offer":
        if price is None or not math.isfinite(price) or price <= 0:
            return False, "invalid_offer_price"
        if is_buyer and price > P["budget"]:
            return False, "buyer_offer_above_budget"
        if (not is_buyer) and price < cost:
            return False, "seller_offer_below_cost"
    if action == "accept":
        if outstanding is None or outstanding["actor"] == actor:
            return False, "invalid_accept_target"
        if is_buyer and outstanding["price"] > P["budget"]:
            return False, "buyer_accept_above_budget"
        if (not is_buyer) and outstanding["price"] < cost:
            return False, "seller_accept_below_cost"
    return True, None


def rejected_attempt(actor, parsed, action, price, call, reason, attempt):
    return {
        "actor": actor,
        "attempt": attempt,
        "proposed_action": action,
        "proposed_price": base.r2(price),
        "reason": reason,
        "message": (parsed or {}).get("message", ""),
        "raw": call.get("raw", ""),
        "thinking": call.get("thinking", ""),
        "resolved_model": call.get("resolved_model"),
        "latency_ms": call.get("latency_ms"),
        "tokens": (call.get("prompt_eval_count") or 0) + (call.get("eval_count") or 0),
    }


def validated_call(model, system, prompt, turn_seed, is_buyer, actor, cost, outstanding, posted=False):
    rejected = []
    first = base.model_call(model, system, prompt, turn_seed)
    p, a, x = parse_action(first)
    valid, reason = legality(a, x, is_buyer, actor, cost, outstanding, posted=posted)
    if valid:
        e = base.event(actor, a, x, p, first)
        e.update({"retry_used": False, "attempt": 1})
        return {"event": e, "rejected": rejected, "first_invalid": False, "retry_success": False, "unresolved": False}

    rejected.append(rejected_attempt(actor, p, a, x, first, reason, 1))
    retry_prompt = prompt + "\n\n" + CORRECTION
    second = base.model_call(model, system, retry_prompt, turn_seed + 100000)
    p2, a2, x2 = parse_action(second)
    valid2, reason2 = legality(a2, x2, is_buyer, actor, cost, outstanding, posted=posted)
    if valid2:
        e = base.event(actor, a2, x2, p2, second)
        e.update({"retry_used": True, "attempt": 2})
        return {"event": e, "rejected": rejected, "first_invalid": True, "retry_success": True, "unresolved": False}

    rejected.append(rejected_attempt(actor, p2, a2, x2, second, reason2, 2))
    return {"event": None, "rejected": rejected, "first_invalid": True, "retry_success": False, "unresolved": True}


def posted(t, ratio, state, mult, seed):
    cost = base.r2(P["buyer_value"] * ratio * mult)
    price = base.r2(cost * 1.04)
    events, rejected, infra = [], [], None
    first_invalid = retries = retry_successes = unresolved = 0
    try:
        prompt = f"Product: {P['name']}. Public posted price: ${price}. The price is non-negotiable. Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. The only legal actions are accept or walk_away. Choose one."
        out = validated_call(base.BUYER_MODEL, base.BUYER_SYSTEM, prompt, seed, True, base.BUYER_LABEL, cost, None, posted=True)
        rejected.extend(out["rejected"])
        first_invalid += int(out["first_invalid"])
        retries += int(out["first_invalid"])
        retry_successes += int(out["retry_success"])
        unresolved += int(out["unresolved"])
        if out["event"] is None:
            agree = False
        else:
            events.append(out["event"])
            agree = out["event"]["action"] == "accept"
    except Exception as exc:
        agree, infra = None, str(exc)
    efficient = P["buyer_value"] > cost
    return {
        "episode_id": base.sha(f"e02c|{base.BUYER_LABEL}|{base.PRODUCT_ID}|posted|{t}|{state}")[:24],
        "buyer": base.BUYER_LABEL,
        "buyer_model": base.BUYER_MODEL,
        "seller": "posted",
        "seller_model": "posted_price_v1",
        "product_id": base.PRODUCT_ID,
        "tightness": t,
        "anchor": "posted_price",
        "order": "posted",
        "seed_index": 0,
        "seed": seed,
        "state": state,
        "seller_cost": cost,
        "agreement": agree,
        "final_price": price if agree else None,
        "normalized_price": base.r2(price / P["reference_price"]) if agree else None,
        "buyer_surplus": base.r2(P["buyer_value"] - price) if agree else 0,
        "seller_profit": base.r2(price - cost) if agree else 0,
        "trade_destroyed": None if agree is None else bool(efficient and not agree),
        "first_invalid_attempts": first_invalid,
        "retries_used": retries,
        "retry_successes": retry_successes,
        "unresolved_protocol_failures": unresolved,
        "infrastructure_failure": infra is not None,
        "error": infra,
        "turns": len(events),
        "events": events,
        "rejected_attempts": rejected,
    }


def bargain(t, ratio, anchor, order, state, mult, i, seed):
    cost = base.r2(P["buyer_value"] * ratio * mult)
    events, rejected, outstanding = [], [], None
    agree, final, infra = False, None, None
    first_invalid = retries = retry_successes = unresolved = 0
    turn = "buyer" if order == "buyer_first" else "seller"
    try:
        for step in range(6):
            is_buyer = turn == "buyer"
            actor = base.BUYER_LABEL if is_buyer else base.SELLER_LABEL
            model = base.BUYER_MODEL if is_buyer else base.SELLER_MODEL
            system = base.BUYER_SYSTEM if is_buyer else base.SELLER_SYSTEM
            private = f"Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. You do not know seller cost." if is_buyer else f"Your private marginal cost is ${cost}. You do not know buyer value or budget."
            anchor_text = f"Public reference price: ${P['reference_price']}." if anchor == "shown" else "No public numerical reference price is provided."
            legal = "There is no outstanding offer. Legal actions now: offer or walk_away." if outstanding is None else f"Outstanding offer ${outstanding['price']} from {outstanding['actor']}. Legal actions now: accept, reject, offer a counteroffer, or walk_away."
            prompt = f"Product: {P['name']}. {anchor_text} {private}\nPublic history:\n{base.history(events)}\n{legal}\nChoose the next action."
            out = validated_call(model, system, prompt, seed + step, is_buyer, actor, cost, outstanding, posted=False)
            rejected.extend(out["rejected"])
            first_invalid += int(out["first_invalid"])
            retries += int(out["first_invalid"])
            retry_successes += int(out["retry_success"])
            unresolved += int(out["unresolved"])
            if out["event"] is None:
                break
            e = out["event"]
            events.append(e)
            a, x = e["action"], e.get("price")
            if a == "offer":
                outstanding = {"actor": actor, "price": base.r2(x)}
            elif a == "accept":
                agree, final = True, outstanding["price"]
                break
            elif a == "reject":
                outstanding = None
            elif a == "walk_away":
                break
            turn = "seller" if is_buyer else "buyer"
    except Exception as exc:
        infra = str(exc)
    efficient = P["buyer_value"] > cost
    return {
        "episode_id": base.sha(f"e02c|{base.BUYER_LABEL}|{base.PRODUCT_ID}|bargain|{t}|{anchor}|{order}|{state}|{i}")[:24],
        "buyer": base.BUYER_LABEL,
        "buyer_model": base.BUYER_MODEL,
        "seller": base.SELLER_LABEL,
        "seller_model": base.SELLER_MODEL,
        "product_id": base.PRODUCT_ID,
        "tightness": t,
        "anchor": anchor,
        "order": order,
        "seed_index": i,
        "seed": seed,
        "state": state,
        "seller_cost": cost,
        "agreement": None if infra else agree,
        "final_price": base.r2(final) if agree else None,
        "normalized_price": base.r2(final / P["reference_price"]) if agree else None,
        "buyer_surplus": base.r2(P["buyer_value"] - final) if agree else 0,
        "seller_profit": base.r2(final - cost) if agree else 0,
        "trade_destroyed": None if infra else bool(efficient and not agree),
        "first_invalid_attempts": first_invalid,
        "retries_used": retries,
        "retry_successes": retry_successes,
        "unresolved_protocol_failures": unresolved,
        "infrastructure_failure": infra is not None,
        "error": infra,
        "turns": len(events),
        "events": events,
        "rejected_attempts": rejected,
    }


def main():
    rows = []
    for t, ratio in TIGHT.items():
        for state, mult in STATES:
            rows.append(posted(t, ratio, state, mult, seed_for(t, 0)))
        for i in range(N):
            s = seed_for(t, i)
            for anchor in ANCHORS:
                for order in ORDERS:
                    for state, mult in STATES:
                        rows.append(bargain(t, ratio, anchor, order, state, mult, i, s))
    expected = 6 + 3 * N * 2 * 2 * 2
    assert len(rows) == expected
    summary = {
        "buyer": base.BUYER_LABEL,
        "buyer_model": base.BUYER_MODEL,
        "seller_model": base.SELLER_MODEL,
        "product_id": base.PRODUCT_ID,
        "n_seeds": N,
        "episodes": len(rows),
        "bargaining_episodes": sum(r["seller"] != "posted" for r in rows),
        "agreements": sum(r.get("agreement") is True for r in rows),
        "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows),
        "first_invalid_attempts": sum(r.get("first_invalid_attempts", 0) for r in rows),
        "retries_used": sum(r.get("retries_used", 0) for r in rows),
        "retry_successes": sum(r.get("retry_successes", 0) for r in rows),
        "unresolved_protocol_failures": sum(r.get("unresolved_protocol_failures", 0) for r in rows),
    }
    out = {
        "experiment_id": "last-price-e02c-protocol-robustness-20260810",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "buyer_model": base.BUYER_MODEL,
        "seller_model": base.SELLER_MODEL,
        "correction": CORRECTION,
        "product": {"product_id": base.PRODUCT_ID, **P},
        "summary": summary,
        "episodes": rows,
    }
    target = Path("artifacts") / f"{base.BUYER_LABEL}-{base.PRODUCT_ID}"
    target.mkdir(parents=True, exist_ok=True)
    (target / "episodes.json").write_text(json.dumps(out, indent=2))
    (target / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
