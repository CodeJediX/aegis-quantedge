"""Streamlit route functions share deterministic, testable research modules."""

import json
import os
import hmac
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import genpareto
from .config import ROOT, TICKERS, NAV, TRAIN_END, TEST_START, TC, EQUITY
from .portfolio import path, metrics, solve, validate_weights, moments
from .risk import risk_table, empirical, filtered_forecast, contributions
from .evt import fit, estimate, bootstrap
from .backtesting import summarize
from .database import active_store, research_version, release_table, DatabaseUnavailable

COLORS = ["#55CCB0", "#D8B76E", "#91B8D3", "#CE846B", "#B4A4CE", "#6EABB4", "#B5C6A2"]
px.defaults.color_discrete_sequence = COLORS


def open_workspace(page):
    st.session_state["page"] = page


def read(name: str) -> pd.DataFrame:
    return release_table(name)


def saved_allocations_panel(w):
    store = active_store()
    if store is None:
        return
    with st.expander("Saved research allocations"):
        if os.environ.get("AEGIS_READONLY_DATABASE") == "1":
            st.info("Your allocation experiments stay in this session. Download a copy from Build a portfolio to keep your weights. Shared online saving is unavailable on this deployment.")
            return
        st.caption("Saved proposals are shared research records. They do not change the approved snapshot or the fixed backtest. Only the configured team administrator can save records.")
        version = research_version()
        records = store.list_allocations(version)
        if records:
            lookup = {row["id"]: row for row in records}
            selected = st.selectbox("Saved allocation", list(lookup), format_func=lambda key: lookup[key]["name"] + " · " + lookup[key]["created_at"][:10], key="saved_allocation")
            if st.button("Load saved allocation", key="load_saved"):
                values = json.loads(lookup[selected]["weights_json"])
                st.session_state["custom"] = validate_weights(np.array([values[t] for t in TICKERS])).tolist()
                st.success("Loaded. Select Custom allocation in the sidebar to inspect this proposal.")
        else:
            st.info("No research allocations have been saved for this release.")
        admin_key = os.environ.get("AEGIS_ADMIN_KEY", "")
        if admin_key:
            with st.form("persist_allocation"):
                label = st.text_input("Allocation name", max_chars=80, key="saved_name")
                token = st.text_input("Team administrator key", type="password", key="saved_admin_key")
                submitted = st.form_submit_button("Save current allocation to database")
            if submitted:
                if not hmac.compare_digest(token.encode(), admin_key.encode()):
                    st.error("The administrator key is not valid.")
                else:
                    identity = store.save_allocation(version, label, w)
                    st.success("Allocation saved to the database. Record " + identity[:8] + ".")
        else:
            st.caption("Saving is disabled until a team administrator key is configured.")


def pct(x):
    return "N/A" if x is None or not np.isfinite(float(x)) else f"{x:.2%}"


def chart(fig) -> None:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1C21",
        plot_bgcolor="#0E1C21",
        font=dict(family="Segoe UI", color="#DCE9EF", size=12),
        title=dict(font=dict(family="Georgia", size=20, color="#EDF3F1"), x=0.01),
        colorway=COLORS,
        margin=dict(l=18, r=24, t=58, b=30),
        legend=dict(orientation="h", y=-0.2),
        height=370,
        hoverlabel=dict(bgcolor="#162A30", font_color="#EDF3F1"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#243B42", zerolinecolor="#3A565E")
    st.plotly_chart(fig, use_container_width=True)


def lede(text):
    st.markdown(f'<div class="lede">{text}</div>', unsafe_allow_html=True)


def table(frame):
    st.dataframe(frame, width="stretch", hide_index=True)


@st.cache_data(show_spinner=False)
def current_risk(r: pd.DataFrame, weights: tuple, alpha: float) -> pd.DataFrame:
    w = np.array(weights)
    df = risk_table(r, w, [alpha])
    past = r.to_numpy() @ w
    try:
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [dict(model="EVT", confidence=alpha, **estimate(fit(-past), alpha))]
                ),
            ],
            ignore_index=True,
        )
    except ValueError:
        pass
    return pd.concat(
        [
            df,
            pd.DataFrame(
                [
                    dict(
                        model="Volatility state",
                        confidence=alpha,
                        **filtered_forecast(past, alpha),
                    )
                ]
            ),
        ],
        ignore_index=True,
    )


def render(page, s, prices, r, rf, alloc, w, name, a, method, lookback, dates) -> None:
    recent = r.iloc[-lookback:]
    risk = current_risk(recent, tuple(w), a)
    test = r.loc[TEST_START:]
    pp = path(r, w)
    idx = test.index
    benchmark = path(r, alloc["60/40 benchmark"].to_numpy()).net
    k = metrics(pp.loc[idx, "net"], r.loc[idx, "SPY"], benchmark.loc[idx], rf.loc[idx])
    chosen = risk[risk.model == method]
    if page == "Executive Command Center":
        lede(
            "Explore a diversified seven-ETF portfolio through performance, downside risk, model validation and real crisis replays. Every figure comes from a fixed historical dataset."
        )
        row = chosen.iloc[0] if len(chosen) else None
        cols = st.columns(4)
        for c, label, value, explanation in zip(
            cols,
            [
                "Held-out net CAGR",
                "Held-out drawdown",
                f"{a:.0%} daily VaR",
                f"{a:.0%} daily ES",
            ],
            [
                pct(k["CAGR"]),
                pct(k["max_drawdown"]),
                pct(row.VaR) if row is not None else "N/A",
                pct(row.ES) if row is not None else "N/A",
            ],
            [
                "Compound annual growth after modeled costs over the held-out test period. Past performance does not predict future returns.",
                "Largest peak-to-trough loss within the held-out test period, starting from its initial portfolio value.",
                "One-day loss cutoff at the selected confidence level. Losses can exceed this estimate.",
                "Expected shortfall: estimated average one-day loss in the worst tail at the selected confidence level.",
            ],
        ):
            c.metric(label, value, help=explanation)
        if row is not None:
            st.caption(
                f'{name} · {method} · {lookback} prior returns · USD 10m reference value · VaR USD {row.VaR*NAV:,.0f} · ES USD {row.ES*NAV:,.0f}'
            )
        left, right = st.columns([1.6, 1])
        with left:
            ww = np.cumprod(1 + pp.loc[idx, "net"])
            chart(
                px.line(
                    x=idx,
                    y=ww * NAV,
                    labels={"x": "Held-out date", "y": "Portfolio NAV (USD)"},
                    title="Capital through the held-out period",
                )
            )
        with right:
            chart(
                px.bar(
                    x=TICKERS,
                    y=w * 100,
                    labels={"x": "Holding", "y": "Weight (%)"},
                    title="Target allocation",
                )
            )
        st.markdown('<div class="section-label">CHOOSE YOUR NEXT STEP</div>', unsafe_allow_html=True)
        actions = st.columns(3)
        for col, label, target in zip(actions,
            ["Build a portfolio →", "Compare downside risk →", "Replay a market crisis →"],
            ["Portfolio Construction", "Risk Analytics", "Crisis Simulation Studio"]):
            col.button(label, on_click=open_workspace, args=(target,), use_container_width=True)
        st.markdown(
            '<div class="review-note"><strong>Portfolio status · review before adoption</strong>'
            '<p>The minimum-variance allocation is a research starting point. Historical crisis loss exceeds the proposed 15% tolerance, so risk limits, spending needs and implementation must be approved before funding.</p></div>',
            unsafe_allow_html=True,
        )
        with st.expander("See the full decision scorecard"):
            table(read("scorecard"))
    elif page == "Market Intelligence":
        lede(
            "One approved universe, one common calendar. Large market moves remain in the research sample and are flagged for inspection."
        )
        tick = st.multiselect("Price series", TICKERS, default=["SPY", "AGG", "GLD"])
        if tick:
            chart(
                px.line(
                    prices[tick] / prices[tick].iloc[0],
                    labels={"value": "Normalized adjusted close", "index": "Date"},
                    title="Adjusted price histories",
                )
            )
        chart(
            px.imshow(
                recent.corr(),
                zmin=-1,
                zmax=1,
                color_continuous_scale="RdBu",
                text_auto=".2f",
                title=f"Return correlations · latest {lookback} observations",
            )
        )
        with st.expander("Coverage and provenance"):
            table(read("coverage"))
            st.json(s["data"])
            st.json(
                json.loads(
                    (ROOT / "data/metadata/prices.json").read_text(encoding="utf-8-sig")
                )
            )
        with st.expander("ADF checks and retained anomaly flags"):
            table(read("adf"))
            table(read("data_flags"))
            st.caption(
                "ADF rejects a unit root when p is small; this does not establish constant volatility, independence or normality."
            )
    elif page == "Portfolio Construction":
        lede(
            "The proposal minimises training variance under a bond floor, gold allocation and explicit equity caps. Alternative allocations show the cost of pursuing more return."
        )
        st.caption(
            "All candidate weights use observations through 2018-12-31; later outcomes do not select the candidate."
        )
        with st.form("allocation_form"):
            cols = st.columns(4)
            values = []
            for i, t in enumerate(TICKERS):
                values.append(
                    cols[i % 4].number_input(
                        t + " weight (%)",
                        0.0,
                        100.0,
                        float(w[i] * 100),
                        step=1.0,
                        key="weight_" + t,
                    )
                )
            apply = st.form_submit_button(
                "Apply allocation to portfolio and risk views"
            )
        if apply:
            try:
                st.session_state["custom"] = validate_weights(
                    np.array(values) / 100
                ).tolist()
                st.session_state["_use_custom"] = True
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        st.download_button("Download selected allocation · CSV", pd.DataFrame({"ticker": TICKERS, "weight": w}).to_csv(index=False), file_name="aegis_allocation.csv", mime="text/csv")
        chart(
            px.line(
                read("frontier"),
                x="volatility",
                y="expected_return",
                markers=True,
                title="Constrained frontier from shrunk training moments",
            )
        )
        table(read("kpis").query("period == 'Test'"))
        table(read("capm_training"))
        table(read("diversification"))
        chart(
            px.line(
                x=idx,
                y=pp.loc[idx, "drawdown"] * 100,
                labels={"x": "Date", "y": "Drawdown (%)"},
                title="Drawdown from the full-history running peak",
            )
        )
        st.caption(
            "For test-period standalone drawdown, see the KPI table, which resets initial NAV at the start of that period. CAPM uses SPY, not a global market portfolio."
        )
    elif page == "Risk Analytics":
        lede(
            "Compare a common one-day loss horizon. VaR marks a cutoff; ES estimates the mean loss in the worst tail beyond it."
        )
        display = risk.copy()
        display["VaR USD"] = display.VaR * NAV
        display["ES USD"] = display.ES * NAV
        display["VaR %"] = display.VaR * 100
        display["ES %"] = display.ES * 100
        compact = display[["model", "confidence", "VaR %", "ES %", "VaR USD", "ES USD"]].copy()
        compact.columns = ["Model", "Confidence", "VaR (%)", "Expected shortfall (%)", "VaR (USD)", "Expected shortfall (USD)"]
        compact["Confidence"] = compact["Confidence"].map(lambda x: f"{x:.0%}")
        compact[["VaR (%)", "Expected shortfall (%)"]] = compact[["VaR (%)", "Expected shortfall (%)"]].round(3)
        compact[["VaR (USD)", "Expected shortfall (USD)"]] = compact[["VaR (USD)", "Expected shortfall (USD)"]].round(0)
        table(compact)
        chart(
            px.bar(
                display.melt(id_vars="model", value_vars=["VaR %", "ES %"]),
                x="model",
                y="value",
                color="variable",
                barmode="group",
                labels={"value": "Loss (% NAV)"},
                title=f"Matched {a:.0%} risk estimates",
            )
        )
        if method == "EVT" and chosen.empty:
            st.info(
                "EVT unavailable at 90% because the requested quantile is at or below the 90% fitting threshold. Use 95% or 99%."
            )
        with st.expander("How to interpret the models"):
            st.write("Historical risk retains observed tails. Parametric risk assumes a normal portfolio log return. Monte Carlo assumes correlated normal asset log returns with covariance shrinkage. Agreement between the two Gaussian approaches is not independent confirmation. EVT extrapolates the observed loss tail and adds threshold and parameter uncertainty.")
        with st.expander("Monte Carlo convergence detail"):
            table(read("mc_convergence"))
            st.caption("This diagnostic belongs to the locked 756-day AEGIS reference, not the current allocation experiment.")
    elif page == "EVT & Tail-Risk Laboratory":
        lede(
            "A severe-loss estimate is only as credible as its tail sample. Move the threshold to see the loss of observations and the change in fitted shape."
        )
        tq = st.slider(
            "POT threshold quantile", 0.85, 0.95, 0.90, 0.005, key="threshold"
        )
        loss = -(recent.to_numpy() @ w)
        model = fit(loss, tq)
        c = st.columns(4)
        c[0].metric("Tail threshold", pct(model["threshold"]))
        c[1].metric("Tail observations", f'{model["exceedances"]:,}')
        c[2].metric("GPD shape", f'{model["shape"]:.3f}')
        c[3].metric("GPD scale", pct(model["scale"]))
        if a > tq:
            est = estimate(model, a)
            c = st.columns(2)
            c[0].metric(f"EVT VaR {a:.0%}", pct(est["VaR"]))
            c[1].metric(f"EVT ES {a:.0%}", pct(est["ES"]))
        else:
            st.info(
                "Requested confidence must exceed the tail threshold. No EVT extrapolation is reported here."
            )
        exc = np.sort(loss[loss > model["threshold"]] - model["threshold"])
        theory = genpareto.ppf(
            (np.arange(len(exc)) + 0.5) / len(exc), model["shape"], scale=model["scale"]
        )
        fig = px.scatter(
            x=theory * 100,
            y=exc * 100,
            labels={"x": "GPD theoretical excess (%)", "y": "Observed excess (%)"},
            title="Tail Q-Q diagnostic",
        )
        fig.add_scatter(
            x=[0, max(theory) * 100],
            y=[0, max(theory) * 100],
            mode="lines",
            name="Equality",
        )
        chart(fig)
        if st.button("Estimate 99% uncertainty with 100 block resamples"):
            with st.spinner("Refitting threshold and GPD across blocks…"):
                st.json(bootstrap(loss, tq, reps=100))
        if model["exceedances"] < 80:
            st.warning(
                "Fewer than 80 exceedances: tail precision is limited. Serial clustering further reduces independent information."
            )
        with st.expander("Threshold sensitivity and model detail"):
            table(read("evt_sensitivity"))
            st.caption("The saved sensitivity table uses the fixed 756-day reference allocation. The interactive fit above uses the current controls.")
    elif page == "Backtesting & Validation":
        lede(
            "Forecast first, observe second. Every threshold uses only the 756 trading days before the date being evaluated."
        )
        f = read("forecasts")
        f.date = pd.to_datetime(f.date)
        f = f[f.date >= pd.Timestamp(TEST_START)]
        if len(dates) != 2:
            st.info("Select both a start and an end date.")
            return
        f = f[
            (f.date >= pd.Timestamp(dates[0]))
            & (f.date <= pd.Timestamp(dates[1]))
            & (f.confidence == a)
        ]
        if len(f) == 0:
            st.warning("No forecasts in this date range.")
            return
        validation = summarize(f)
        g = f[f.model == method]
        selected = validation[validation.model == method]
        if len(selected):
            result = selected.iloc[0]
            traffic = str(result.traffic_last250)
            css = traffic.lower() if traffic in {"Green", "Amber", "Red"} else "neutral"
            st.markdown(
                f'<div class="traffic-line {css}"><span class="traffic-light"></span>'
                f'<strong>{method}</strong> · last-250 traffic light: {traffic} · '
                f'{int(result.exceptions)} exceptions across {int(result.n)} forecasts</div>',
                unsafe_allow_html=True,
            )
        st.dataframe(
            validation[["model", "confidence", "n", "exceptions", "expected", "exception_rate", "kupiec_p", "independence_p", "conditional_p", "traffic_last250"]],
            hide_index=True, width="stretch",
            column_config={
                "model": "Model", "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
                "n": "Forecasts", "exceptions": "Exceptions", "expected": st.column_config.NumberColumn("Expected", format="%.2f"),
                "exception_rate": st.column_config.NumberColumn("Exception rate", format="%.4f"),
                "kupiec_p": st.column_config.NumberColumn("Kupiec p-value", format="%.3f"),
                "independence_p": st.column_config.NumberColumn("Christoffersen independence p", format="%.3f"),
                "conditional_p": st.column_config.NumberColumn("Conditional coverage p", format="%.3f"),
                "traffic_last250": "Last-250 traffic light",
            },
        )
        if len(g):
            fig = go.Figure()
            fig.add_scatter(
                x=g.date, y=g.loss * NAV, mode="lines", name="Realized loss"
            )
            fig.add_scatter(x=g.date, y=g.VaR * NAV, mode="lines", name="Forecast VaR")
            hit = g.loss > g.VaR
            fig.add_scatter(
                x=g.loc[hit, "date"],
                y=g.loc[hit, "loss"] * NAV,
                mode="markers",
                name="Exceptions",
            )
            fig.update_layout(title="One-day USD risk exceptions · fixed AEGIS weights")
            chart(fig)
        st.caption(
            "Full-window traffic light applies only when exactly 250 forecasts at 99% are selected. Last-250 status uses a separate explicit 250-day window. It is a pedagogical Basel classification, not regulatory approval."
        )
        st.subheader("Did the volatility-state extension improve the model?")
        regime = s["regime_comparison"]
        rc = st.columns(3)
        rc[0].metric("Mean score difference", f'{regime["mean_difference"]:.3f}')
        rc[1].metric("95% interval · low", f'{regime["CI"][0]:.3f}')
        rc[2].metric("95% interval · high", f'{regime["CI"][1]:.3f}')
        st.write("No clear improvement. Negative values would favour the volatility-state model, but the interval crosses zero. The result is retained as an honest negative finding.")
        st.caption(
            "Lookback and portfolio sidebar controls affect current-risk experiments. The saved backtest uses the locked 756-day AEGIS design; it is never silently relabelled as a custom allocation backtest."
        )
    elif page == "Crisis Simulation Studio":
        lede(
            "Replay actual ETF paths before considering a synthetic shock. A current allocation replay describes exposure; it is not a strategy that existed during the crisis."
        )
        stress = read("stress")
        scenario = st.selectbox("Stress scenario", stress.scenario.unique())
        compare = st.multiselect(
            "Compare allocations",
            list(alloc.columns),
            default=["AEGIS minimum variance", "60/40 benchmark"],
        )
        sel = stress[(stress.scenario == scenario) & stress.portfolio.isin(compare)]
        table(
            sel[
                [
                    "portfolio",
                    "start",
                    "end",
                    "return_pct",
                    "USD",
                    "max_drawdown",
                    "recovery_date",
                ]
            ]
        )
        paths = read("crisis_paths")
        data = paths[(paths.scenario == scenario) & paths.portfolio.isin(compare)]
        if len(data):
            n = st.slider(
                "Replay trading day",
                1,
                int(data.groupby("portfolio").size().max()),
                int(data.groupby("portfolio").size().max()),
            )
            shown = data.groupby("portfolio", group_keys=False).head(n)
            chart(
                px.line(
                    shown,
                    x="date",
                    y="wealth",
                    color="portfolio",
                    title=f"Crisis replay through trading day {n}",
                    labels={"wealth": "Growth of $1"},
                )
            )
        else:
            from .config import HYPOTHETICAL

            table(
                pd.DataFrame(
                    {
                        "ticker": TICKERS,
                        "assumed_shock": [HYPOTHETICAL[t] for t in TICKERS],
                    }
                )
            )
            st.caption(
                "Simultaneous assumed return shocks, no probability or recovery path. Equity correlation rises implicitly through the common shock; no new covariance matrix is inferred."
            )
        if len(sel):
            table(sel[["portfolio"] + TICKERS])
            st.caption(
                "Asset P&L contributions sum to scenario return. Historical contributions incorporate changing portfolio NAV; the scenario is gross of costs."
            )
    elif page == "Portfolio Decision Lab":
        lede(
            "Risk budgets expose which holdings consume the loss allowance. Allocation experiments are proposals; they do not alter the pre-specified validation record."
        )
        saved_allocations_panel(w)
        rc = contributions(recent, w, alpha=a)
        table(rc)
        chart(
            px.bar(
                rc,
                x="ticker",
                y="component_ES",
                title=f"Euler contribution to historical daily ES {a:.0%}",
                labels={"component_ES": "Fraction of NAV"},
            )
        )
        st.caption(
            "ES contributions are derivatives of the finite-sample excess-loss ES estimator at the target weights. Gaussian simple-return VaR contributions are shown separately, not mislabelled as Monte Carlo or historical VaR contributions."
        )
        es = empirical(-(recent.to_numpy() @ w), a)["ES"]
        budget = st.number_input(
            "Daily ES risk budget (USD)",
            min_value=1000.0,
            max_value=float(NAV),
            value=250000.0,
            step=10000.0,
        )
        st.metric(
            "Indicative proportional exposure cap", pct(min(1, budget / (es * NAV)))
        )
        st.caption(
            "Diagnostic sizing only. Cash is outside this prescribed holding universe; implement any reduction through an approved eligible-asset reallocation or a revised mandate, not an assumed cash holding."
        )
        bond_min = st.slider("Proposed AGG floor", 0.35, 0.70, 0.35, 0.05)
        eq_cap = st.slider("Proposed aggregate equity cap", 0.20, 0.50, 0.50, 0.05)
        if st.button("Re-optimise using training data only"):
            new = solve(r.loc[:TRAIN_END], bond_min=bond_min, equity_cap=eq_cap)
            st.session_state["custom"] = new.tolist()
            table(pd.DataFrame({"ticker": TICKERS, "proposed_weight": new}))
            st.success(
                "Saved as Custom allocation; use the sidebar to inspect risk and performance."
            )
        table(read("scorecard"))
        table(read("policy_sensitivity"))
        st.caption(
            "Policy components have no arbitrary weighted total. Sensitivity changes proposed maximum limits by ±20%; these are client-approval assumptions."
        )
    elif page == "AI Research Assistant":
        lede(
            "Plain-language answers grounded in the published calculations. Choose a question to find the relevant evidence and caveats."
        )
        question = st.selectbox(
            "Research question",
            [
                "What is the proposed portfolio?",
                "What does the backtest say?",
                "Why do risk models disagree?",
                "Can we claim capital is protected?",
                "What requires human approval?",
            ],
        )
        answers = {
            "What is the proposed portfolio?": f'The training-constrained minimum-variance weights are {s["weights"]}. Inspect allocation constraints, held-out performance and stress results before accepting it.',
            "What does the backtest say?": "See the computed test table below. Small p-values are evidence against a specific calibration assumption; a non-rejection does not prove a model is correct.",
            "Why do risk models disagree?": "Historical risk samples observed shocks. Parametric and Monte Carlo models use Gaussian innovations with different aggregation. EVT fits only exceedances and is sensitive to threshold and sample size.",
            "Can we claim capital is protected?": "No. Daily VaR is not a maximum loss, and the historical sample does not contain every possible crisis. The synthetic scenario is an assumption, not a bound.",
            "What requires human approval?": "The human team must independently review the code, allocation, risk limits, stress interpretation and investment conclusion. No completed approval is recorded.",
        }
        st.write(answers[question])
        table(
            read("backtesting_test")
            if question == "What does the backtest say?"
            else read("evidence_ledger")
        )
        st.caption("Answers are deterministic and run without an external AI service, API key or transfer of confidential data.")
    elif page == "Investment Committee Reports":
        lede(
            "Committee documents use the locked research candidate. Downloaded reference reports do not change when you explore a custom allocation."
        )
        for folder in ["reports", "presentation"]:
            for file in sorted((ROOT / folder).glob("*")):
                if file.suffix in [".pdf", ".docx", ".pptx", ".md"]:
                    st.download_button(
                        file.stem.replace("_", " ") + " · " + file.suffix[1:].upper(),
                        data=file.read_bytes(),
                        file_name=file.name,
                        key="download_" + file.name,
                    )
        with st.expander("Research review and approval record"):
            st.markdown((ROOT / "documentation/Team_Approval_Checklist.md").read_text(encoding="utf-8-sig"))
    elif page == "Assumptions & Limitations":
        st.markdown(
            (ROOT / "documentation/Assumptions_and_Limitations.md").read_text(
                encoding="utf-8-sig"
            )
        )
        table(read("evidence_ledger"))
    elif page == "Methodology, Sources & AI Disclosure":
        for file in [
            "Methodology.md",
            "Data_Governance.md",
            "AI_Disclosure.md",
            "Sources.md",
        ]:
            with st.expander(
                file.replace("_", " ").replace(".md", ""),
                expanded=file == "Methodology.md",
            ):
                st.markdown(
                    (ROOT / "documentation" / file).read_text(encoding="utf-8-sig")
                )
        st.code(
            "pip install -r requirements.txt\npython run.py --reproduce\nstreamlit run app.py",
            language="bash",
        )
