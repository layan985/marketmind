"""Interactive Streamlit dashboard for MII exploration."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


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


def app() -> None:
    """Render the interactive application."""
    import pandas as pd
    import plotly.express as px
    import streamlit as st

    from marketmind.backtest import WalkForwardEvaluator
    from marketmind.data import validate_prices
    from marketmind.indicators import all_signals
    from marketmind.mii import MarketMind, MarketMindConfig
    from marketmind.synthetic import synthetic_market

    st.set_page_config(page_title="MarketMind", page_icon="🧠", layout="wide")
    st.title("MarketMind")
    st.caption("Multiscale market intelligence: memory · information flow · connectivity")
    with st.sidebar:
        source = st.radio("Data source", ["Deterministic demo", "Upload wide CSV"])
        window = st.number_input("Rolling window", 64, 756, 252, 21)
        step = st.number_input("Estimation step", 1, 63, 21)
        cost = st.number_input("Cost per unit turnover (bps)", 0.0, 100.0, 5.0)
        run = st.button("Estimate market intelligence", type="primary")
    uploaded = None
    if source == "Upload wide CSV":
        uploaded = st.file_uploader(
            "CSV: date column followed by positive price columns", type="csv"
        )
    if not run:
        st.info("Choose data and estimate. The demo is deterministic and needs no external API.")
        return
    if source == "Upload wide CSV":
        if uploaded is None:
            st.error("Upload a CSV first.")
            return
        frame = pd.read_csv(uploaded)
        if "date" not in frame:
            st.error("The CSV needs a date column.")
            return
        frame["date"] = pd.to_datetime(frame["date"])
        prices = validate_prices(frame.set_index("date"))
    else:
        prices = synthetic_market(periods=1800)
    with st.spinner("Estimating rolling fractal, entropy, and network states…"):
        result = MarketMind(MarketMindConfig(window=int(window), step=int(step))).fit_transform(
            prices
        )
    latest = result.to_frame().dropna(subset=["mii"]).iloc[-1]
    columns = st.columns(4)
    columns[0].metric("MII", f"{latest['mii']:.3f}")
    columns[1].metric("Regime", str(latest["regime"]).upper())
    columns[2].metric("Memory", f"{latest['memory']:.3f}")
    columns[3].metric("Information flow", f"{latest['information']:.3f}")
    chart = result.to_frame().reset_index(names="date")
    st.plotly_chart(
        px.line(chart, x="date", y=["mii", "memory", "information", "connectivity"]),
        use_container_width=True,
    )
    st.subheader("Regime-conditional indicator evaluation")
    asset = st.selectbox("Asset", list(prices.columns))
    returns = prices[asset].pct_change()
    signals = all_signals(prices[asset])
    evaluation = WalkForwardEvaluator(cost_bps=float(cost)).evaluate(
        returns, signals, regimes=result.regimes["regime"]
    )
    table = evaluation.summary.reset_index()
    st.dataframe(
        table[["signal", "category", "regime", "sharpe", "total_return", "max_drawdown", "trades"]],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download MII and regimes",
        result.to_frame().to_csv().encode(),
        file_name="marketmind_mii.csv",
        mime="text/csv",
    )


if __name__ == "__main__":  # pragma: no cover
    app()
