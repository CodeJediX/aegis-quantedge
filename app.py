"""Launch: streamlit run app.py. All mandatory functions run without an API key."""

import json
import hashlib
import io
import os
import numpy as np
import pandas as pd
import streamlit as st
from src.config import ROOT, TICKERS
from src.ui import render
from src.database import active_store, research_version, DatabaseUnavailable

st.set_page_config(
    page_title="AEGIS | Quantum-X",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    "<style>"
    + (ROOT / "assets/style.css").read_text(encoding="utf-8-sig")
    + "</style>",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def inputs() -> tuple:
    store = active_store()
    if os.environ.get("AEGIS_REQUIRE_DATABASE") == "1" and store is None:
        raise DatabaseUnavailable("Hosted database configuration is required for this deployment.")
    for filename, metadata in [
        ("adjusted_prices.csv", "prices.json"),
        ("DTB3.csv", "fred.json"),
    ]:
        record = json.loads(
            (ROOT / "data/metadata" / metadata).read_text(encoding="utf-8-sig")
        )
        if (
            hashlib.sha256(
                (ROOT / "data/snapshots" / filename).read_bytes()
            ).hexdigest()
            != record["sha256"]
        ):
            raise ValueError("Snapshot checksum mismatch: " + filename)
    if store is not None:
        version = research_version()
        summary = json.loads(store.content(version, "outputs/results/summary.json"))
        prices = store.load_prices(version)
        r = prices.pct_change(fill_method=None).dropna()
        rf = pd.read_csv(io.StringIO(store.content(version, "outputs/tables/risk_free.csv")), index_col=0, parse_dates=True).iloc[:, 0]
        alloc = pd.read_csv(io.StringIO(store.content(version, "outputs/tables/allocations.csv")), index_col=0)
        return summary, prices, r, rf, alloc
    summary = json.loads(
        (ROOT / "outputs/results/summary.json").read_text(encoding="utf-8-sig")
    )
    prices = pd.read_csv(
        ROOT / "data/snapshots/adjusted_prices.csv", index_col=0, parse_dates=True
    )[TICKERS].dropna()
    r = prices.pct_change(fill_method=None).dropna()
    rf = pd.read_csv(
        ROOT / "outputs/tables/risk_free.csv", index_col=0, parse_dates=True
    ).iloc[:, 0]
    alloc = pd.read_csv(ROOT / "outputs/tables/allocations.csv", index_col=0)
    return summary, prices, r, rf, alloc


try:
    s, prices, r, rf, alloc = inputs()
except (FileNotFoundError, ValueError, KeyError, DatabaseUnavailable) as exc:
    st.error(
        "Research outputs are unavailable. Run python run.py --reproduce, then restart the app. "
        + str(exc)
    )
    st.stop()

PAGES = [
    "Executive Command Center",
    "Market Intelligence",
    "Portfolio Construction",
    "Risk Analytics",
    "EVT & Tail-Risk Laboratory",
    "Backtesting & Validation",
    "Crisis Simulation Studio",
    "Portfolio Decision Lab",
    "AI Research Assistant",
    "Investment Committee Reports",
    "Assumptions & Limitations",
    "Methodology, Sources & AI Disclosure",
]
with st.sidebar:
    st.markdown(
        '<div class="brand">AEGIS</div><div class="micro">QUANTUM-X · CAPITAL PRESERVATION RESEARCH</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.selectbox("Research workspace", PAGES, key="page")
    candidate = st.selectbox(
        "Portfolio", list(alloc.columns) + ["Custom allocation"], key="portfolio"
    )
    alpha = st.selectbox(
        "Confidence level",
        [0.90, 0.95, 0.99],
        index=2,
        format_func=lambda x: f"{x:.0%}",
        key="confidence",
    )
    method = st.selectbox(
        "VaR methodology",
        ["Historical", "Parametric", "Monte Carlo", "EVT", "Volatility state"],
        key="method",
    )
    lookback = st.selectbox(
        "Historical lookback (trading days)",
        [252, 504, 756, 1260],
        index=2,
        key="lookback",
    )
    dates = st.date_input(
        "Backtesting date range",
        value=(
            pd.Timestamp(s["test_start"]).date(),
            pd.Timestamp(s["test_end"]).date(),
        ),
        min_value=pd.Timestamp(s["test_start"]).date(),
        max_value=pd.Timestamp(s["test_end"]).date(),
        key="dates",
    )
    st.caption(
        "Backtest weights are the fixed AEGIS candidate; allocation experiments do not rewrite validated forecasts."
    )
    if active_store() is not None:
        backend = "PostgreSQL" if active_store().postgres else "SQLite"
        mode = " · read-only" if os.environ.get("AEGIS_READONLY_DATABASE") == "1" else ""
        st.caption("Research storage: " + backend + mode + " · version " + research_version()[:12])
    else:
        st.caption("Research storage: verified offline files")
    st.markdown(
        f'<div class="micro">DATA THROUGH {s["data"]["end"]}<br/>USD 10,000,000 mandate<br/>One-day risk horizon · {s["seed"]} seed</div>',
        unsafe_allow_html=True,
    )

w = np.asarray(
    st.session_state.get("custom", alloc.iloc[:, 0].tolist())
    if candidate == "Custom allocation"
    else alloc[candidate].to_numpy()
)
st.markdown(
    '<div class="eyebrow">SERENDIB UNIVERSITY ENDOWMENT FUND / RESEARCH PROPOSAL</div>',
    unsafe_allow_html=True,
)
st.title(page)
st.markdown(
    '<div class="status-line">PENDING TEAM REVIEW · Proposal and risk appetite require independent human approval</div>',
    unsafe_allow_html=True,
)
try:
    with st.spinner("Calculating from the approved historical snapshot…"):
        render(
            page,
            s,
            prices,
            r,
            rf,
            alloc,
            w,
            candidate,
            alpha,
            method,
            int(lookback),
            dates,
        )
except DatabaseUnavailable as exc:
    st.error(str(exc))
except (ValueError, KeyError, np.linalg.LinAlgError) as exc:
    st.error("This configuration could not be estimated: " + str(exc))
    st.info(
        "Try a longer lookback or less extreme threshold. Unsupported estimates are shown as unavailable rather than replaced with invented values."
    )
