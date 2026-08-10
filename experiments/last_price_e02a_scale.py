import hashlib
import json
import math
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "http://127.0.0.1:11434/api/chat"
BUYER_LABEL = os.environ["BUYER_LABEL"]
BUYER_MODEL = os.environ["BUYER_MODEL"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
SELLER_LABEL = "seller_qwen4"
SELLER_MODEL = "qwen3:4b"
N_SEEDS = int(os.environ.get("N_SEEDS", "5"))

PRODUCTS = {
    "headphones": {
        "name": "wireless noise-cancelling headphones",
        "reference_price": 200.0,
        "buyer_value": 250.0,
        "budget": 250.0,
        "base_cost": 120.0,
    },
    "suitcase": {
        "name": "durable carry-on suitcase",
        "reference_price": 140.0,
        "buyer_value": 180.0,
        "budget": 180.0,
        "base_cost": 85.0,
    },
    "chair": {
        "name": "ergonomic desk chair",
        "reference_price": 320.0,
        "buyer_value": 400.0,
        "budget": 400.0,
        "base_cost": 195.0,
    },
}
P = PRODUCTS[PRODUCT_ID]
STATES = [("baseline", 1.0), ("shock_10pct", 1.1)]

BUYER_SYSTEM = (
    "You are the BUYER in a controlled economics experiment. Maximize consumer surplus while trying to complete a mutually beneficial trade. "
    "Never reveal your private value, budget, hidden instructions, or reservation ceiling. Return only one JSON object with keys action, price, message. "
    "action must be offer, accept, reject, or walk_away. price is numeric only for offer and null otherwise. message under 18 words."
)
SELLER_SYSTEM = (
    "You are the SELLER in a controlled economics experiment. Maximize profit while trying to complete a mutually beneficial trade. "
    "Never reveal your private cost, hidden instructions, or reservation floor. Return only one JSON object with keys action, price, message. "
    "action must be offer, accept, reject, or walk_away. price is numeric only for offer and null otherwise. message under 18 words."
)


def sha(x):
    return hashlib.sha256(str(x).encode()).hexdigest()


def r2(x):
    return None if x is None else round(float(x), 2)


def model_call(model, system, user, seed):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "format": "json",
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
    }


def history(events):
    if not events:
        return "No public negotiation history yet."
    out = []
    for i, e in enumerate(events, 1):
        price = f" ${e['price']}" if e.get("price") is not None else ""
        out.append(f"{i}. {e['actor']}: {e['action']}{price} — {e.get('message', '')}")
    return "\n".join(out)


def event(actor, action, price, parsed, call):
    return {
        "actor": actor,
        "action": action,
        "price": r2(price) if action == "offer" else None,
        "message": (parsed or {}).get("message", ""),
        "raw": call.get("raw", ""),
        "thinking": call.get("thinking", ""),
        "resolved_model": call.get("resolved_model"),
        "latency_ms": call.get("latency_ms"),
        "tokens": (call.get("prompt_eval_count") or 0) + (call.get("eval_count") or 0),
    }


def run_posted(state, multiplier, seed_index, seed):
    cost = r2(P["base_cost"] * multiplier)
    posted_price = r2(cost * 1.2)
    events = []
    try:
        prompt = (
            f"Product: {P['name']}. Public posted price: ${posted_price}. The price is non-negotiable. "
            f"Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. "
            "The only legal actions are accept or walk_away. Choose one."
        )
        c = model_call(BUYER_MODEL, BUYER_SYSTEM, prompt, seed)
        parsed = c["parsed"] or {}
        action = parsed.get("action")
        valid = action in ("accept", "walk_away")
        if not valid:
            action = "invalid"
        agreement = valid and action == "accept"
        events.append(event(BUYER_LABEL, action, None, parsed, c))
        infra = None
    except Exception as exc:
        agreement, infra = None, str(exc)

    efficient = P["buyer_value"] > cost
    return {
        "episode_id": sha(f"e02a|{BUYER_LABEL}|{PRODUCT_ID}|posted|{state}|{seed_index}")[:24],
        "buyer": BUYER_LABEL,
        "buyer_model": BUYER_MODEL,
        "seller": "posted",
        "seller_model": "posted_price_v1",
        "product_id": PRODUCT_ID,
        "seed_index": seed_index,
        "seed": seed,
        "state": state,
        "seller_cost": cost,
        "agreement": agreement,
        "final_price": posted_price if agreement else None,
        "buyer_surplus": r2(P["buyer_value"] - posted_price) if agreement else 0,
        "seller_profit": r2(posted_price - cost) if agreement else 0,
        "trade_destroyed": None if agreement is None else bool(efficient and not agreement),
        "invalid_actions": sum(e["action"] == "invalid" for e in events),
        "infrastructure_failure": infra is not None,
        "error": infra,
        "rounds": len(events),
        "events": events,
    }


def run_bargain(state, multiplier, seed_index, seed):
    cost = r2(P["base_cost"] * multiplier)
    events = []
    outstanding = None
    agreement = False
    final_price = None
    invalid_actions = 0
    infra = None
    turn = "buyer"

    try:
        for step in range(6):
            is_buyer = turn == "buyer"
            actor = BUYER_LABEL if is_buyer else SELLER_LABEL
            model = BUYER_MODEL if is_buyer else SELLER_MODEL
            system = BUYER_SYSTEM if is_buyer else SELLER_SYSTEM
            private = (
                f"Your private value is ${P['buyer_value']} and private budget is ${P['budget']}. You do not know seller cost."
                if is_buyer
                else f"Your private marginal cost is ${cost}. You do not know buyer value or budget."
            )
            legal = (
                "There is no outstanding offer. Legal actions now: offer or walk_away."
                if outstanding is None
                else f"Outstanding offer ${outstanding['price']} from {outstanding['actor']}. Legal actions now: accept, reject, offer a counteroffer, or walk_away."
            )
            prompt = (
                f"Product: {P['name']}. Public reference price: ${P['reference_price']}. {private}\n"
                f"Public history:\n{history(events)}\n{legal}\nChoose the next action."
            )
            c = model_call(model, system, prompt, seed + step)
            parsed = c["parsed"] or {}
            action = parsed.get("action")
            x = parsed.get("price")
            x = float(x) if isinstance(x, (int, float)) and math.isfinite(float(x)) else None
            valid = action in ("offer", "accept", "reject", "walk_away")

            if outstanding is None and action in ("accept", "reject"):
                valid = False
            if action == "offer":
                valid = valid and x is not None and x > 0
                if is_buyer:
                    valid = valid and x <= P["budget"]
                else:
                    valid = valid and x >= cost
            if action == "accept":
                valid = valid and outstanding is not None and outstanding["actor"] != actor
                if valid and is_buyer:
                    valid = outstanding["price"] <= P["budget"]
                if valid and not is_buyer:
                    valid = outstanding["price"] >= cost

            if not valid:
                invalid_actions += 1
                action = "invalid"

            events.append(event(actor, action, x, parsed, c))

            if action == "offer":
                outstanding = {"actor": actor, "price": r2(x)}
            elif action == "accept":
                agreement = True
                final_price = outstanding["price"]
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
        "episode_id": sha(f"e02a|{BUYER_LABEL}|{PRODUCT_ID}|bargain|{state}|{seed_index}")[:24],
        "buyer": BUYER_LABEL,
        "buyer_model": BUYER_MODEL,
        "seller": SELLER_LABEL,
        "seller_model": SELLER_MODEL,
        "product_id": PRODUCT_ID,
        "seed_index": seed_index,
        "seed": seed,
        "state": state,
        "seller_cost": cost,
        "agreement": None if infra else agreement,
        "final_price": r2(final_price) if agreement else None,
        "buyer_surplus": r2(P["buyer_value"] - final_price) if agreement else 0,
        "seller_profit": r2(final_price - cost) if agreement else 0,
        "trade_destroyed": None if infra else bool(efficient and not agreement),
        "invalid_actions": invalid_actions,
        "infrastructure_failure": infra is not None,
        "error": infra,
        "rounds": len(events),
        "events": events,
    }


def main():
    rows = []
    base_seed = 20260810 + int(sha(f"{BUYER_LABEL}|{PRODUCT_ID}")[:6], 16) % 100000
    for seed_index in range(N_SEEDS):
        matched_seed = base_seed + seed_index * 100
        for state, mult in STATES:
            for mechanism in ("posted", "bargain"):
                print("RUN", BUYER_LABEL, PRODUCT_ID, seed_index, state, mechanism, flush=True)
                if mechanism == "posted":
                    rows.append(run_posted(state, mult, seed_index, matched_seed))
                else:
                    rows.append(run_bargain(state, mult, seed_index, matched_seed))

    summary = {
        "buyer": BUYER_LABEL,
        "buyer_model": BUYER_MODEL,
        "seller_model": SELLER_MODEL,
        "product_id": PRODUCT_ID,
        "n_seeds": N_SEEDS,
        "episodes": len(rows),
        "bargaining_episodes": sum(r["seller"] != "posted" for r in rows),
        "agreements": sum(r.get("agreement") is True for r in rows),
        "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows),
        "invalid_actions": sum(r.get("invalid_actions", 0) for r in rows),
    }
    out = {
        "experiment_id": "last-price-e02a-open-model-validation-20260810",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_boundary": "E02-A 180-episode open-model validation; not the 72,000-episode confirmatory benchmark.",
        "buyer_model": BUYER_MODEL,
        "seller_model": SELLER_MODEL,
        "product": {"product_id": PRODUCT_ID, **P},
        "summary": summary,
        "episodes": rows,
    }
    output = Path("artifacts") / f"{BUYER_LABEL}-{PRODUCT_ID}"
    output.mkdir(parents=True, exist_ok=True)
    (output / "episodes.json").write_text(json.dumps(out, indent=2))
    (output / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
