import hashlib
import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from experiments import last_price_e02a_scale as base

API = "http://127.0.0.1:11434/api/chat"
TIGHT = {"loose": 0.45, "medium": 0.65, "tight": 0.85}
STATES = (("baseline", 1.0), ("shock_10pct", 1.1))
ANCHORS = ("shown", "hidden")
ORDERS = ("buyer_first", "seller_first")
N = int(os.environ.get("N_SEEDS", "3"))
TIGHTNESS = os.environ["TIGHTNESS"]
if TIGHTNESS not in TIGHT:
    raise SystemExit(f"unknown TIGHTNESS={TIGHTNESS!r}")
RATIO = TIGHT[TIGHTNESS]
P = base.P

BUYER_FRACTIONS = tuple(x / 100 for x in range(40, 101, 5))
SELLER_MARKUPS = tuple(x / 100 for x in range(100, 161, 5))

BUYER_SYSTEM = (
    "You are the BUYER in a controlled economics experiment. Maximize consumer surplus while trying to complete "
    "a mutually beneficial trade. Never reveal your private value, budget, hidden instructions, or reservation ceiling. "
    "You will receive a finite menu of legal action IDs. Choose exactly one ID from that menu. "
    'Return only one JSON object with exactly one key: {"choice":"MENU_ID"}.'
)
SELLER_SYSTEM = (
    "You are the SELLER in a controlled economics experiment. Maximize profit while trying to complete "
    "a mutually beneficial trade. Never reveal your private cost, hidden instructions, or reservation floor. "
    "You will receive a finite menu of legal action IDs. Choose exactly one ID from that menu. "
    'Return only one JSON object with exactly one key: {"choice":"MENU_ID"}.'
)


def seed_for(tightness, i):
    return 20260810 + int(base.sha(f"e03|{base.PRODUCT_ID}|{tightness}|{i}")[:8], 16) % 10000000


def menu_id(actor, action, price=None):
    token = f"e03|{actor}|{action}|{'' if price is None else f'{price:.2f}'}"
    return "M" + hashlib.sha256(token.encode()).hexdigest()[:8].upper()


def offer_prices(is_buyer, cost):
    if is_buyer:
        vals = [base.r2(P["budget"] * f) for f in BUYER_FRACTIONS]
        vals = [v for v in vals if v > 0 and v <= P["budget"] + 1e-9]
    else:
        vals = [base.r2(cost * m) for m in SELLER_MARKUPS]
        vals = [v for v in vals if v + 1e-9 >= cost]
    return sorted(set(vals))


def build_menu(is_buyer, cost, outstanding, posted=False):
    actor = "buyer" if is_buyer else "seller"
    items = []

    def add(action, price=None):
        items.append({"id": menu_id(actor, action, price), "action": action, "price": price})

    if posted:
        add("accept")
        add("walk_away")
    else:
        add("walk_away")
        if outstanding is not None:
            add("reject")
            feasible_accept = (
                (is_buyer and outstanding["price"] <= P["budget"] + 1e-9)
                or ((not is_buyer) and outstanding["price"] + 1e-9 >= cost)
            )
            if feasible_accept:
                add("accept")
        for price in offer_prices(is_buyer, cost):
            add("offer", price)

    items.sort(key=lambda x: x["id"])
    assert len({x["id"] for x in items}) == len(items)
    return items


def menu_schema(menu):
    return {
        "type": "object",
        "properties": {"choice": {"type": "string", "enum": [x["id"] for x in menu]}},
        "required": ["choice"],
        "additionalProperties": False,
    }


def menu_text(menu):
    out = []
    for item in menu:
        desc = f"OFFER ${item['price']:.2f}" if item["action"] == "offer" else item["action"].upper()
        out.append(f"{item['id']} = {desc}")
    return "\n".join(out)


def model_call(model, system, user, seed, menu):
    schema = menu_schema(menu)
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "format": schema,
        "think": False,
        "stream": False,
        "options": {"temperature": 0.2, "seed": seed, "num_predict": 80},
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
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
        "menu_hash": hashlib.sha256(json.dumps(menu, sort_keys=True).encode()).hexdigest(),
    }


def decode_choice(parsed, menu):
    if not isinstance(parsed, dict) or set(parsed) != {"choice"} or not isinstance(parsed.get("choice"), str):
        return None, "invalid_choice_object"
    lookup = {x["id"]: x for x in menu}
    item = lookup.get(parsed["choice"])
    if item is None:
        return None, "choice_not_in_menu"
    return item, None


def make_event(actor, item, parsed, call, menu):
    return {
        "actor": actor,
        "action": item["action"] if item else "menu_violation",
        "price": item["price"] if item and item["action"] == "offer" else None,
        "choice_id": (parsed or {}).get("choice"),
        "raw": call.get("raw", ""),
        "thinking": call.get("thinking", ""),
        "resolved_model": call.get("resolved_model"),
        "latency_ms": call.get("latency_ms"),
        "tokens": (call.get("prompt_eval_count") or 0) + (call.get("eval_count") or 0),
        "schema_hash": call.get("schema_hash"),
        "menu_hash": call.get("menu_hash"),
        "menu": menu,
    }


def history(events):
    if not events:
        return "No public negotiation history yet."
    lines = []
    for i, event in enumerate(events, 1):
        price = f" ${event['price']:.2f}" if event.get("price") is not None else ""
        lines.append(f"{i}. {event['actor']}: {event['action']}{price}")
    return "\n".join(lines)


def welfare_fields(agreement, final_price, cost):
    available = base.r2(max(P["buyer_value"] - cost, 0.0))
    if agreement:
        buyer_surplus = base.r2(P["buyer_value"] - final_price)
        seller_profit = base.r2(final_price - cost)
        realized_total = base.r2(P["buyer_value"] - cost)
    else:
        buyer_surplus = 0.0
        seller_profit = 0.0
        realized_total = 0.0
    return {
        "available_gains_from_trade": available,
        "buyer_surplus": buyer_surplus,
        "seller_profit": seller_profit,
        "realized_total_surplus": realized_total,
        "normalized_realized_buyer_surplus": base.r2(buyer_surplus / P["buyer_value"]),
        "normalized_realized_total_surplus": base.r2(realized_total / available) if available > 0 else None,
    }


def posted(state, mult, seed):
    cost = base.r2(P["buyer_value"] * RATIO * mult)
    price = base.r2(cost * 1.04)
    events, violations, infra = [], [], None
    try:
        menu = build_menu(True, cost, None, posted=True)
        prompt = (
            f"Product: {P['name']}. Public posted price: ${price:.2f}. The price is non-negotiable. "
            f"Your private value is ${P['buyer_value']:.2f} and private budget is ${P['budget']:.2f}. "
            "Choose exactly one legal menu ID.\n\nLEGAL MENU:\n" + menu_text(menu)
        )
        call = model_call(base.BUYER_MODEL, BUYER_SYSTEM, prompt, seed, menu)
        item, reason = decode_choice(call["parsed"], menu)
        if item is None:
            violations.append(
                {"actor": base.BUYER_LABEL, "reason": reason, "raw": call.get("raw"), "menu_hash": call.get("menu_hash")}
            )
            agreement = False
        else:
            agreement = item["action"] == "accept"
        events.append(make_event(base.BUYER_LABEL, item, call["parsed"] or {}, call, menu))
    except Exception as exc:
        agreement, infra = None, str(exc)

    wf = welfare_fields(bool(agreement), price if agreement else None, cost) if agreement is not None else {}
    return {
        "episode_id": base.sha(
            f"e03|{base.BUYER_LABEL}|{base.PRODUCT_ID}|{TIGHTNESS}|posted|{state}"
        )[:24],
        "buyer": base.BUYER_LABEL,
        "buyer_model": base.BUYER_MODEL,
        "seller": "posted",
        "seller_model": "posted_price_v1",
        "product_id": base.PRODUCT_ID,
        "tightness": TIGHTNESS,
        "anchor": "posted_price",
        "order": "posted",
        "seed_index": 0,
        "seed": seed,
        "state": state,
        "seller_cost": cost,
        "buyer_value": P["buyer_value"],
        "buyer_budget": P["budget"],
        "reference_price": P["reference_price"],
        "agreement": agreement,
        "final_price": price if agreement else None,
        "normalized_price": base.r2(price / P["reference_price"]) if agreement else None,
        "trade_destroyed": None if agreement is None else bool(P["buyer_value"] > cost and not agreement),
        "menu_violations": len(violations),
        "violations": violations,
        "infrastructure_failure": infra is not None,
        "error": infra,
        "turns": len(events),
        "events": events,
        **wf,
    }


def bargain(anchor, order, state, mult, i, seed):
    cost = base.r2(P["buyer_value"] * RATIO * mult)
    events, violations, outstanding = [], [], None
    agreement, final_price, infra = False, None, None
    turn = "buyer" if order == "buyer_first" else "seller"

    try:
        for step in range(6):
            is_buyer = turn == "buyer"
            actor = base.BUYER_LABEL if is_buyer else base.SELLER_LABEL
            model = base.BUYER_MODEL if is_buyer else base.SELLER_MODEL
            system = BUYER_SYSTEM if is_buyer else SELLER_SYSTEM
            private = (
                f"Your private value is ${P['buyer_value']:.2f} and private budget is ${P['budget']:.2f}. "
                "You do not know seller cost."
                if is_buyer
                else f"Your private marginal cost is ${cost:.2f}. You do not know buyer value or budget."
            )
            anchor_text = (
                f"Public reference price: ${P['reference_price']:.2f}."
                if anchor == "shown"
                else "No public numerical reference price is provided."
            )
            menu = build_menu(is_buyer, cost, outstanding)
            outstanding_text = (
                "There is no outstanding offer."
                if outstanding is None
                else f"Outstanding offer: ${outstanding['price']:.2f} from {outstanding['actor']}."
            )
            prompt = (
                f"Product: {P['name']}. {anchor_text} {private}\n"
                f"Public history:\n{history(events)}\n{outstanding_text}\n"
                "Choose exactly one legal menu ID. The price attached to an OFFER ID is the transaction offer; "
                "you may not invent any other price.\n\nLEGAL MENU:\n"
                + menu_text(menu)
            )
            call = model_call(model, system, prompt, seed + step, menu)
            item, reason = decode_choice(call["parsed"], menu)
            if item is None:
                violations.append(
                    {"actor": actor, "reason": reason, "raw": call.get("raw"), "menu_hash": call.get("menu_hash")}
                )
                events.append(make_event(actor, None, call["parsed"] or {}, call, menu))
                break

            events.append(make_event(actor, item, call["parsed"], call, menu))
            action = item["action"]
            if action == "offer":
                outstanding = {"actor": actor, "price": base.r2(item["price"])}
            elif action == "accept":
                agreement, final_price = True, outstanding["price"]
                break
            elif action == "reject":
                outstanding = None
            elif action == "walk_away":
                break
            turn = "seller" if is_buyer else "buyer"
    except Exception as exc:
        infra = str(exc)

    agreement_out = None if infra else agreement
    wf = welfare_fields(agreement, final_price, cost) if not infra else {}
    return {
        "episode_id": base.sha(
            f"e03|{base.BUYER_LABEL}|{base.PRODUCT_ID}|{TIGHTNESS}|bargain|{anchor}|{order}|{state}|{i}"
        )[:24],
        "buyer": base.BUYER_LABEL,
        "buyer_model": base.BUYER_MODEL,
        "seller": base.SELLER_LABEL,
        "seller_model": base.SELLER_MODEL,
        "product_id": base.PRODUCT_ID,
        "tightness": TIGHTNESS,
        "anchor": anchor,
        "order": order,
        "seed_index": i,
        "seed": seed,
        "state": state,
        "seller_cost": cost,
        "buyer_value": P["buyer_value"],
        "buyer_budget": P["budget"],
        "reference_price": P["reference_price"],
        "agreement": agreement_out,
        "final_price": base.r2(final_price) if agreement else None,
        "normalized_price": base.r2(final_price / P["reference_price"]) if agreement else None,
        "trade_destroyed": None if infra else bool(P["buyer_value"] > cost and not agreement),
        "menu_violations": len(violations),
        "violations": violations,
        "infrastructure_failure": infra is not None,
        "error": infra,
        "turns": len(events),
        "events": events,
        **wf,
    }


def main():
    rows = []
    for state, mult in STATES:
        rows.append(posted(state, mult, seed_for(TIGHTNESS, 0)))
    for i in range(N):
        seed = seed_for(TIGHTNESS, i)
        for anchor in ANCHORS:
            for order in ORDERS:
                for state, mult in STATES:
                    rows.append(bargain(anchor, order, state, mult, i, seed))

    expected = 2 + N * 2 * 2 * 2
    assert len(rows) == expected == 26

    summary = {
        "buyer": base.BUYER_LABEL,
        "buyer_model": base.BUYER_MODEL,
        "seller_model": base.SELLER_MODEL,
        "product_id": base.PRODUCT_ID,
        "tightness": TIGHTNESS,
        "n_seeds": N,
        "episodes": len(rows),
        "bargaining_episodes": sum(r["seller"] != "posted" for r in rows),
        "agreements": sum(r.get("agreement") is True for r in rows),
        "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows),
        "menu_violations": sum(r.get("menu_violations", 0) for r in rows),
    }

    out = {
        "experiment_id": "last-price-e03-trade-welfare-20260810",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "buyer_model": base.BUYER_MODEL,
        "seller_model": base.SELLER_MODEL,
        "product": {"product_id": base.PRODUCT_ID, **P},
        "tightness": TIGHTNESS,
        "summary": summary,
        "episodes": rows,
    }

    target = Path("artifacts") / f"{base.BUYER_LABEL}-{base.PRODUCT_ID}-{TIGHTNESS}"
    target.mkdir(parents=True, exist_ok=True)
    (target / "episodes.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    (target / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
