import hashlib, json, math, os, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from experiments import last_price_e02a_scale as base

API = "http://127.0.0.1:11434/api/chat"
TIGHT = {"loose": 0.45, "medium": 0.65, "tight": 0.85}
STATES = (("baseline", 1.0), ("shock_10pct", 1.1))
ANCHORS = ("shown", "hidden")
ORDERS = ("buyer_first", "seller_first")
N = int(os.environ.get("N_SEEDS", "3"))
P = base.P


def seed_for(t, i):
    # Preserve E02-B/E02-C initial matched seeds exactly.
    return 20260810 + int(base.sha(f"e02b|{base.PRODUCT_ID}|{t}|{i}")[:8], 16) % 10000000


def action_object(action, price_schema):
    return {
        "type": "object",
        "properties": {
            "action": {"const": action},
            "price": price_schema,
            "message": {"type": "string"},
        },
        "required": ["action", "price", "message"],
        "additionalProperties": False,
    }


def schema_for(is_buyer, cost, outstanding, posted=False):
    null_price = {"type": "null"}
    if posted:
        return {"oneOf": [action_object("accept", null_price), action_object("walk_away", null_price)]}

    offer_price = {"type": "number", "exclusiveMinimum": 0}
    if is_buyer:
        offer_price["maximum"] = P["budget"]
    else:
        offer_price["minimum"] = cost

    choices = [action_object("offer", offer_price), action_object("walk_away", null_price)]
    if outstanding is not None:
        choices.append(action_object("reject", null_price))
        feasible_accept = (is_buyer and outstanding["price"] <= P["budget"]) or ((not is_buyer) and outstanding["price"] >= cost)
        if feasible_accept:
            choices.append(action_object("accept", null_price))
    return {"oneOf": choices}


def schema_call(model, system, user, seed, schema):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "format": schema,
        "think": False,
        "stream": False,
        "options": {"temperature": 0.2, "seed": seed, "num_predict": 160},
    }
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(req, timeout=240) as resp:
        data = json.loads(resp.read().decode())
    msg = data.get("message") or {}
    raw = msg.get("content", "")
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = None
    return {
        "parsed": parsed,
        "raw": raw,
        "thinking": msg.get("thinking", ""),
        "resolved_model": data.get("model"),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
        "latency_ms": round((time.time() - started) * 1000),
        "schema_hash": hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest(),
    }


def parse_price(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x)):
        return float(x)
    return None


def validate(parsed, is_buyer, cost, outstanding, posted=False):
    if not isinstance(parsed, dict):
        return False, "not_object", None, None
    if set(parsed) != {"action", "price", "message"}:
        return False, "wrong_fields", parsed.get("action"), parse_price(parsed.get("price"))
    action, raw_price = parsed.get("action"), parsed.get("price")
    price = parse_price(raw_price)
    if not isinstance(parsed.get("message"), str):
        return False, "message_not_string", action, price
    if posted:
        if action not in ("accept", "walk_away") or raw_price is not None:
            return False, "posted_illegal", action, price
        return True, None, action, None
    if action not in ("offer", "accept", "reject", "walk_away"):
        return False, "unknown_action", action, price
    if action != "offer" and raw_price is not None:
        return False, "nonoffer_price_not_null", action, price
    if outstanding is None and action in ("accept", "reject"):
        return False, "no_offer_to_answer", action, price
    if action == "offer":
        if price is None or price <= 0:
            return False, "invalid_offer_price", action, price
        if is_buyer and price > P["budget"]:
            return False, "buyer_offer_over_budget", action, price
        if (not is_buyer) and price < cost:
            return False, "seller_offer_below_cost", action, price
    if action == "accept":
        if outstanding is None:
            return False, "accept_without_offer", action, price
        if is_buyer and outstanding["price"] > P["budget"]:
            return False, "buyer_accept_over_budget", action, price
        if (not is_buyer) and outstanding["price"] < cost:
            return False, "seller_accept_below_cost", action, price
    return True, None, action, price


def make_event(actor, action, price, parsed, call):
    e = base.event(actor, action, price, parsed, call)
    e["schema_hash"] = call.get("schema_hash")
    return e


def posted(t, ratio, state, mult, seed):
    cost = base.r2(P["buyer_value"] * ratio * mult)
    price = base.r2(cost * 1.04)
    events, violations, infra = [], [], None
    try:
        prompt = f"Product: {P['name']}. Public posted price: ${price}. The price is non-negotiable. Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. The only legal actions are accept or walk_away. Choose one."
        schema = schema_for(True, cost, None, posted=True)
        c = schema_call(base.BUYER_MODEL, base.BUYER_SYSTEM, prompt, seed, schema)
        ok, reason, action, x = validate(c["parsed"], True, cost, None, posted=True)
        if not ok:
            violations.append({"actor": base.BUYER_LABEL, "reason": reason, "raw": c.get("raw"), "schema_hash": c.get("schema_hash")})
            agree = False
            events.append(make_event(base.BUYER_LABEL, "schema_violation", None, c["parsed"] or {}, c))
        else:
            agree = action == "accept"
            events.append(make_event(base.BUYER_LABEL, action, None, c["parsed"], c))
    except Exception as exc:
        agree, infra = None, str(exc)
    efficient = P["buyer_value"] > cost
    return {
        "episode_id": base.sha(f"e02d|{base.BUYER_LABEL}|{base.PRODUCT_ID}|posted|{t}|{state}")[:24],
        "buyer": base.BUYER_LABEL, "buyer_model": base.BUYER_MODEL,
        "seller": "posted", "seller_model": "posted_price_v1",
        "product_id": base.PRODUCT_ID, "tightness": t, "anchor": "posted_price", "order": "posted",
        "seed_index": 0, "seed": seed, "state": state, "seller_cost": cost,
        "agreement": agree, "final_price": price if agree else None,
        "normalized_price": base.r2(price / P["reference_price"]) if agree else None,
        "buyer_surplus": base.r2(P["buyer_value"] - price) if agree else 0,
        "seller_profit": base.r2(price - cost) if agree else 0,
        "trade_destroyed": None if agree is None else bool(efficient and not agree),
        "schema_violations": len(violations), "violations": violations,
        "infrastructure_failure": infra is not None, "error": infra, "turns": len(events), "events": events,
    }


def bargain(t, ratio, anchor, order, state, mult, i, seed):
    cost = base.r2(P["buyer_value"] * ratio * mult)
    events, violations, outstanding, agree, final, infra = [], [], None, False, None, None
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
            schema = schema_for(is_buyer, cost, outstanding)
            c = schema_call(model, system, prompt, seed + step, schema)
            ok, reason, action, x = validate(c["parsed"], is_buyer, cost, outstanding)
            if not ok:
                violations.append({"actor": actor, "reason": reason, "raw": c.get("raw"), "schema_hash": c.get("schema_hash")})
                events.append(make_event(actor, "schema_violation", None, c["parsed"] or {}, c))
                break
            events.append(make_event(actor, action, x, c["parsed"], c))
            if action == "offer":
                outstanding = {"actor": actor, "price": base.r2(x)}
            elif action == "accept":
                agree, final = True, outstanding["price"]
                break
            elif action == "reject":
                outstanding = None
            elif action == "walk_away":
                break
            turn = "seller" if is_buyer else "buyer"
    except Exception as exc:
        infra = str(exc)
    efficient = P["buyer_value"] > cost
    return {
        "episode_id": base.sha(f"e02d|{base.BUYER_LABEL}|{base.PRODUCT_ID}|bargain|{t}|{anchor}|{order}|{state}|{i}")[:24],
        "buyer": base.BUYER_LABEL, "buyer_model": base.BUYER_MODEL,
        "seller": base.SELLER_LABEL, "seller_model": base.SELLER_MODEL,
        "product_id": base.PRODUCT_ID, "tightness": t, "anchor": anchor, "order": order,
        "seed_index": i, "seed": seed, "state": state, "seller_cost": cost,
        "agreement": None if infra else agree, "final_price": base.r2(final) if agree else None,
        "normalized_price": base.r2(final / P["reference_price"]) if agree else None,
        "buyer_surplus": base.r2(P["buyer_value"] - final) if agree else 0,
        "seller_profit": base.r2(final - cost) if agree else 0,
        "trade_destroyed": None if infra else bool(efficient and not agree),
        "schema_violations": len(violations), "violations": violations,
        "infrastructure_failure": infra is not None, "error": infra, "turns": len(events), "events": events,
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
    assert len(rows) == expected == 78
    summary = {
        "buyer": base.BUYER_LABEL, "buyer_model": base.BUYER_MODEL, "seller_model": base.SELLER_MODEL,
        "product_id": base.PRODUCT_ID, "n_seeds": N, "episodes": len(rows),
        "bargaining_episodes": sum(r["seller"] != "posted" for r in rows),
        "agreements": sum(r.get("agreement") is True for r in rows),
        "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows),
        "schema_violations": sum(r.get("schema_violations", 0) for r in rows),
    }
    out = {
        "experiment_id": "last-price-e02d-constrained-schema-20260810",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "buyer_model": base.BUYER_MODEL, "seller_model": base.SELLER_MODEL,
        "product": {"product_id": base.PRODUCT_ID, **P}, "summary": summary, "episodes": rows,
    }
    target = Path("artifacts") / f"{base.BUYER_LABEL}-{base.PRODUCT_ID}"
    target.mkdir(parents=True, exist_ok=True)
    (target / "episodes.json").write_text(json.dumps(out, indent=2))
    (target / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
