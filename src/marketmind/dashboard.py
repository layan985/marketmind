"""Interactive Streamlit research terminal for MarketMind."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def launch() -> int:
    """Launch this module with Streamlit."""
    try:
        import streamlit  # noqa: F401
    except ImportError as error:
        raise ImportError(
            "Install the dashboard extra: pip install 'marketmind[dashboard]'"
        ) from error
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve())]
    )


def _evidence_footer(st: Any, text: str) -> None:
    st.caption(text)


def app() -> None:
    """Render the research terminal without exposing sealed holdout outcomes."""
    import pandas as pd
    import plotly.express as px
    import streamlit as st

    from marketmind.backtest import WalkForwardEvaluator
    from marketmind.data import validate_prices
    from marketmind.indicators import all_signals
    from marketmind.mii import MarketMind, MarketMindConfig
    from marketmind.synthetic import synthetic_market

    st.set_page_config(page_title="MarketMind Research Terminal", page_icon="◫", layout="wide")

    st.markdown("### MARKETMIND / RESEARCH TERMINAL")
    st.title("Award-winning theory. Open implementation. Frozen prospective test.")
    st.caption(
        "Research software for inspecting memory, information flow, connectivity, regimes, uncertainty and walk-forward diagnostics."
    )

    status = st.columns(5)
    status[0].metric("Frozen release", "v0.1.0")
    status[1].metric("Controlled implementation", "v0.2.0")
    status[2].metric("Holdout start", "10 AUG 2026")
    status[3].metric("Holdout end", "06 AUG 2027")
    status[4].metric("Independent reproductions", "0")
    st.warning("HOLDOUT RESULT: NOT YET AVAILABLE. Confirmatory performance remains sealed.")
    st.caption(
        "EVIDENCE / preregistration + public repository · STATUS / PENDING VALIDATION · LIMITATION / no holdout result exists yet"
    )

    with st.sidebar:
        st.header("Research controls")
        source = st.radio("Market data", ["Deterministic demo", "Upload wide CSV"])
        window = st.number_input("Estimation window", 64, 756, 252, 21)
        step = st.number_input("Estimation step", 1, 63, 21)
        cost = st.number_input("Transaction cost (bps)", 0.0, 100.0, 5.0)
        run = st.button("Run diagnostics", type="primary")
        st.divider()
        st.caption("FLOW")
        st.caption("market → window → memory → information flow → connectivity → regime → diagnostics → export")

    uploaded: Any | None = None
    if source == "Upload wide CSV":
        uploaded = st.file_uploader(
            "CSV: date column followed by positive price columns", type="csv"
        )

    if not run:
        st.info("Choose a market source and run diagnostics. The deterministic demo requires no external API.")
        st.stop()

    if source == "Upload wide CSV":
        if uploaded is None:
            st.error("Upload a CSV first.")
            st.stop()
        assert uploaded is not None
        frame = pd.read_csv(uploaded)
        if "date" not in frame:
            st.error("The CSV needs a date column.")
            st.stop()
        frame["date"] = pd.to_datetime(frame["date"])
        prices = validate_prices(frame.set_index("date"))
        evidence_class = "USER-SUPPLIED DATA"
    else:
        prices = synthetic_market(periods=1800)
        evidence_class = "SYNTHETIC"

    with st.spinner("Estimating rolling memory, information and network states…"):
        result = MarketMind(MarketMindConfig(window=int(window), step=int(step))).fit_transform(prices)

    result_frame = result.to_frame()
    latest = result_frame.dropna(subset=["mii"]).iloc[-1]

    st.subheader("Current diagnostic state")
    columns = st.columns(5)
    columns[0].metric("MII", f"{latest['mii']:.3f}")
    columns[1].metric("Regime", str(latest["regime"]).upper())
    columns[2].metric("Memory", f"{latest['memory']:.3f}")
    columns[3].metric("Information flow", f"{latest['information']:.3f}")
    columns[4].metric("Connectivity", f"{latest['connectivity']:.3f}")
    _evidence_footer(
        st,
        f"SOURCE / selected input · N / {len(prices):,} rows · WINDOW / {int(window)} · STEP / {int(step)} · STATUS / {evidence_class} · LIMITATION / diagnostic state, not a trading recommendation",
    )

    chart = result_frame.reset_index(names="date")
    st.subheader("Market-memory and system-state history")
    st.plotly_chart(
        px.line(chart, x="date", y=["mii", "memory", "information", "connectivity"]),
        use_container_width=True,
    )
    _evidence_footer(
        st,
        f"SOURCE / selected input · WINDOW / rolling {int(window)} · FILTER / estimation step {int(step)} · STATUS / {evidence_class} · LIMITATION / composite and component diagnostics share the same input history",
    )

    st.subheader("Regime timeline")
    regime_chart = chart.dropna(subset=["regime"]).copy()
    regime_chart["regime"] = regime_chart["regime"].astype(str)
    st.plotly_chart(px.scatter(regime_chart, x="date", y="mii", color="regime"), use_container_width=True)
    _evidence_footer(
        st,
        "SOURCE / MarketMind regime classifier · STATUS / PENDING VALIDATION · LIMITATION / thresholds are historical classifications, not future-return guarantees",
    )

    st.subheader("Walk-forward diagnostics")
    asset = st.selectbox("Research asset", list(prices.columns))
    returns = prices[asset].pct_change()
    signals = all_signals(prices[asset])
    evaluation = WalkForwardEvaluator(cost_bps=float(cost)).evaluate(
        returns, signals, regimes=result.regimes["regime"]
    )
    table = evaluation.summary.reset_index()
    display_columns = [
        "signal",
        "category",
        "regime",
        "sharpe",
        "total_return",
        "max_drawdown",
        "trades",
    ]
    st.dataframe(table[display_columns], use_container_width=True, hide_index=True)
    _evidence_footer(
        st,
        f"SOURCE / WalkForwardEvaluator · COST / {float(cost):.1f} bps · STATUS / diagnostic evaluation · LIMITATION / development or user-supplied sample; prospective holdout remains sealed",
    )

    st.subheader("Proof ledger")
    proof = pd.DataFrame(
        [
            ["Frozen preregistration release", "v0.1.0", "OFFICIAL SOURCE", "Frozen"],
            ["Controlled implementation", "v0.2.0", "PENDING VALIDATION", "Current"],
            ["Controlled audit", "7 / 7 checks", "PENDING VALIDATION", "Passing"],
            ["Holdout result", "Not yet available", "PENDING VALIDATION", "Sealed"],
            ["Independent reproductions", "0", "PENDING VALIDATION", "Open zero"],
        ],
        columns=["Claim", "Number", "Evidence type", "Status"],
    )
    st.dataframe(proof, use_container_width=True, hide_index=True)

    export = result_frame.to_csv().encode()
    st.download_button(
        "Export diagnostic report data",
        export,
        file_name="marketmind_research_terminal.csv",
        mime="text/csv",
        type="primary",
    )
    st.caption("MarketMind is research software, not an execution engine or investment recommendation.")


if __name__ == "__main__":  # pragma: no cover
    app()
