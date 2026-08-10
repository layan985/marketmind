import json
from datetime import datetime, timezone
from pathlib import Path

from experiments import last_price_e03_driver as e03

N = e03.N


def seed_for(tightness, i):
    return 20260811 + int(
        e03.base.sha(f"e05|{e03.base.PRODUCT_ID}|{tightness}|{i}")[:8], 16
    ) % 10000000


def retag(row):
    row = dict(row)
    row["episode_id"] = e03.base.sha(
        "|".join(
            [
                "e05",
                str(row.get("buyer")),
                str(row.get("product_id")),
                str(row.get("tightness")),
                str(row.get("seller")),
                str(row.get("anchor")),
                str(row.get("order")),
                str(row.get("state")),
                str(row.get("seed_index")),
            ]
        )
    )[:24]
    return row


def main():
    rows = []
    for state, mult in e03.STATES:
        rows.append(retag(e03.posted(state, mult, seed_for(e03.TIGHTNESS, 0))))

    for i in range(N):
        seed = seed_for(e03.TIGHTNESS, i)
        for anchor in e03.ANCHORS:
            for order in e03.ORDERS:
                for state, mult in e03.STATES:
                    rows.append(retag(e03.bargain(anchor, order, state, mult, i, seed)))

    expected = 2 + N * 2 * 2 * 2
    assert len(rows) == expected == 26

    summary = {
        "buyer": e03.base.BUYER_LABEL,
        "buyer_model": e03.base.BUYER_MODEL,
        "seller_model": e03.base.SELLER_MODEL,
        "product_id": e03.base.PRODUCT_ID,
        "tightness": e03.TIGHTNESS,
        "n_seeds": N,
        "episodes": len(rows),
        "bargaining_episodes": sum(r["seller"] != "posted" for r in rows),
        "agreements": sum(r.get("agreement") is True for r in rows),
        "infrastructure_failures": sum(r.get("infrastructure_failure") is True for r in rows),
        "menu_violations": sum(r.get("menu_violations", 0) for r in rows),
        "seed_namespace": "e05-20260811",
    }

    out = {
        "experiment_id": "last-price-e05-trade-welfare-replication-20260811",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "buyer_model": e03.base.BUYER_MODEL,
        "seller_model": e03.base.SELLER_MODEL,
        "product": {"product_id": e03.base.PRODUCT_ID, **e03.P},
        "tightness": e03.TIGHTNESS,
        "summary": summary,
        "episodes": rows,
    }

    target = Path("artifacts") / f"{e03.base.BUYER_LABEL}-{e03.base.PRODUCT_ID}-{e03.TIGHTNESS}"
    target.mkdir(parents=True, exist_ok=True)
    (target / "episodes.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    (target / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
