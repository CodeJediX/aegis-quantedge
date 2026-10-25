"""Launch: streamlit run app.py. All mandatory functions run without an API key."""

import json
import hashlib
import io
import os
from html import escape
import numpy as np
import pandas as pd
import streamlit as st
from src.config import ROOT, TICKERS
from src.ui import render
from src.database import active_store, research_version, DatabaseUnavailable
from src.data import validate_prices
from src.interactive import allocation_id

st.set_page_config(
    page_title="AEGIS · Portfolio Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="auto",
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
    if store is not None and not store.postgres and os.environ.get("AEGIS_READONLY_DATABASE") == "1":
        store.seed()
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
        prices = validate_prices(store.load_prices(version))
        r = prices.pct_change(fill_method=None).dropna()
        rf = pd.read_csv(io.StringIO(store.content(version, "outputs/tables/risk_free.csv")), index_col=0, parse_dates=True).iloc[:, 0]
        alloc = pd.read_csv(io.StringIO(store.content(version, "outputs/tables/allocations.csv")), index_col=0)
        return summary, prices, r, rf, alloc
    summary = json.loads(
        (ROOT / "outputs/results/summary.json").read_text(encoding="utf-8-sig")
    )
    prices = pd.read_csv(
        ROOT / "data/snapshots/adjusted_prices.csv", index_col=0, parse_dates=True
    )[TICKERS]
    validate_prices(prices)
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
PAGE_LABELS = dict(zip(PAGES, [
    "Overview", "Markets", "Build a portfolio", "Risk comparison", "Tail-risk lab",
    "Model validation", "Stress testing", "Risk budgets", "Research guide",
    "Reports & downloads", "Assumptions & Limitations", "Methods & disclosures",
]))
PAGE_TITLES = {**PAGE_LABELS, "Executive Command Center": "Investment decision"}
if st.session_state.pop("_use_custom", False):
    st.session_state["portfolio"] = "Custom allocation"
with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><span class="brand-mark" aria-hidden="true">◈</span>'
        '<div><div class="brand">AEGIS</div><div class="brand-sub">PORTFOLIO INTELLIGENCE</div></div></div>',
        unsafe_allow_html=True,
    )
    page = st.selectbox("Workspace", PAGES, format_func=PAGE_LABELS.get, key="page")
    st.markdown('<div class="sidebar-label">EXPLORE AN ALLOCATION</div>', unsafe_allow_html=True)
    candidate = st.selectbox(
        "Portfolio", list(alloc.columns) + ["Custom allocation"], key="portfolio",
        help="Choose a reference portfolio, or build your own in Build a portfolio. All allocations use the same seven ETFs.",
    )
    alpha = st.selectbox(
        "Confidence level",
        [0.90, 0.95, 0.99],
        index=2,
        format_func=lambda x: f"{x:.0%}",
        key="confidence",
        help="A 99% VaR is a loss cutoff expected to be exceeded on about 1 in 100 days under the model. It is not a maximum loss.",
    )
    method = st.selectbox(
        "VaR methodology",
        ["Historical", "Parametric", "Monte Carlo", "EVT", "Volatility state"],
        key="method",
        help="Compare all methods in Risk comparison. Each estimates the same one-day loss horizon.",
    )
    with st.expander("Analysis settings", expanded=page == "Backtesting & Validation"):
        lookback = st.selectbox("Historical lookback (trading days)", [252, 504, 756, 1260], index=2, key="lookback")
        dates = st.date_input(
            "Backtesting date range",
            value=(pd.Timestamp(s["test_start"]).date(), pd.Timestamp(s["test_end"]).date()),
            min_value=pd.Timestamp(s["test_start"]).date(),
            max_value=pd.Timestamp(s["test_end"]).date(), key="dates",
        )
        st.caption("Date filters apply to Model validation. Selected-allocation forecasts use the selected lookback; the fixed research reference retains its756-day window.")
    with st.expander("About this research"):
        st.write("Seven ETFs across equities, bonds and gold. All dollar estimates use a USD 10 million reference portfolio; results are historical, not live prices.")
        st.caption("Reference case: Serendib University Endowment Fund · Quantum-X · QuantEdge 1.0. The case constraints remain in force. Independent human review of the investment proposal is pending.")
        if active_store() is not None:
            backend = "PostgreSQL" if active_store().postgres else "SQLite"
            mode = " · read-only" if os.environ.get("AEGIS_READONLY_DATABASE") == "1" else ""
            st.caption("Research storage: " + backend + mode + " · version " + research_version()[:12])
        else:
            st.caption("Research storage: verified offline files")
        st.caption(f'Reproducibility seed: {s["seed"]}')
    st.markdown(f'<div class="sidebar-footer"><span class="status-dot"></span> Historical dataset<br/><strong>Through {s["data"]["end"]}</strong></div>', unsafe_allow_html=True)

w = np.asarray(
    st.session_state.get("custom", alloc.iloc[:, 0].tolist())
    if candidate == "Custom allocation"
    else alloc[candidate].to_numpy()
)
signature = allocation_id(w)
if st.session_state.get("_editor_signature") != signature:
    for ticker, weight in zip(TICKERS, w):
        st.session_state["weight_" + ticker] = float(weight * 100)
    st.session_state["_editor_signature"] = signature
st.markdown(
    '<div class="app-topline"><span>RESEARCH / ' + escape(PAGE_LABELS[page].upper()) + '</span>'
    '<span class="snapshot-badge">HISTORICAL · ' + s["data"]["end"] + '</span></div>',
    unsafe_allow_html=True,
)
st.title(PAGE_TITLES[page])
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
st.markdown('<footer class="app-footer"><strong>AEGIS</strong><span>Historical research · No capital guarantee · Not personal investment advice</span></footer>', unsafe_allow_html=True)
