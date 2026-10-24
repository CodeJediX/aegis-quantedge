"""Computed-output PDF reports and presentation evidence; no hardcoded market results."""

import json
import re
import pandas as pd
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from .config import ROOT, TICKERS, NAV

P = lambda v: f"{float(v):.2%}"
D = lambda v: f"${float(v):,.0f}"


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / f"outputs/tables/{name}.csv")


def build_reports(s: dict) -> None:
    risk = read("risk_snapshot")
    bt = read("backtesting_test")
    stress = read("stress")
    kpis = read("kpis")
    rc = read("risk_contributions")
    select = s["candidate"]
    k = s["out_of_sample"]
    ss = stress[stress.portfolio == select]
    b99 = bt[bt.confidence == 0.99]
    h = risk[(risk.model == "Historical") & (risk.confidence == 0.99)].iloc[0]
    ev = risk[(risk.model == "EVT") & (risk.confidence == 0.99)].iloc[0]
    hist = b99[b99.model == "Historical"].iloc[0]
    state = b99[b99.model == "Volatility state"].iloc[0]
    worst = float(ss[ss.n > 1].max_drawdown.max())
    hyp = float(ss[ss.n == 1].return_pct.iloc[0])
    styles = getSampleStyleSheet()
    for name, size, leading, col in [
        ("Body", 10, 14.3, "#18334B"),
        ("Small", 8.3, 11, "#18334B"),
        ("Caption", 8.3, 11, "#007E86"),
        ("H1", 21, 25, "#18334B"),
        ("H2", 11.5, 15, "#007E86"),
        ("Cover", 38, 43, "#18334B"),
    ]:
        styles.add(
            ParagraphStyle(
                name=name,
                fontName=(
                    "Helvetica-Bold" if name in ["H1", "H2", "Cover"] else "Helvetica"
                ),
                fontSize=size,
                leading=leading,
                textColor=colors.HexColor(col),
                spaceAfter=9,
                spaceBefore=5 if name == "H2" else 0,
            )
        )
    record = []

    def para(text, style="Body"):
        record.append(text)
        return Paragraph(text, styles[style])

    def tab(headers, rows, widths):
        vals = [
            [Paragraph(str(c), styles["Small"]) for c in row]
            for row in [headers] + rows
        ]
        table = Table(vals, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5F1F1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#F4F7F9")],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        record.extend([" | ".join(map(str, row)) for row in [headers] + rows])
        return table

    def fig(name, width=475):
        p = ROOT / f"outputs/figures/{name}.png"
        iw, ih = ImageReader(str(p)).getSize()
        return Image(str(p), width=width, height=width * ih / iw)

    def footer(c, doc):
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#667F8D"))
        c.drawString(52, 28, "QUANTUM-X / AEGIS   |   PROPOSAL PENDING TEAM REVIEW")
        c.drawRightString(543, 28, str(doc.page))

    def write(filename, story):
        SimpleDocTemplate(
            str(ROOT / "reports" / filename),
            pagesize=(595.28, 841.89),
            leftMargin=60,
            rightMargin=60,
            topMargin=50,
            bottomMargin=52,
            title="AEGIS | Serendib University Endowment",
            author="Quantum-X; AI-assisted proposal",
        ).build(story, onFirstPage=footer, onLaterPages=footer)

    story = []

    def p(text, style="Body"):
        story.append(para(text, style))

    def page(title):
        story.append(PageBreak())
        p(title, "H1")

    def t(headers, rows, widths):
        story.append(tab(headers, rows, widths))
        story.append(Spacer(1, 9))

    story.append(Spacer(1, 65))
    p("QUANTEDGE 1.0 / FINAL CHALLENGE", "H2")
    story.append(Spacer(1, 42))
    p("AEGIS", "Cover")
    p("Capital preservation research<br/>for the Serendib University Endowment", "H1")
    p("Quantum-X | USD 10 million proposed mandate", "H2")
    story.append(Spacer(1, 34))
    p("Decision proposal: ADJUST", "H1")
    p(
        f"The constrained allocation limits ordinary volatility, but a {P(worst)} historical drawdown and {P(-hyp)} assumed scenario loss require a clear committee decision on risk tolerance."
    )
    p(
        f'Data: {s["data"]["start"]} to {s["data"]["end"]}. Prepared 24 October 2026.',
        "Small",
    )
    p(
        "All findings are calculated by the accompanying code. The allocation and recommendation require independent human-team validation under the competition AI policy.",
        "Small",
    )
    page("01 / Executive decision")
    p(
        "A conservative mandate needs a loss budget that the committee can defend during a crisis. The research therefore chooses minimum training variance under explicit asset limits, rather than selecting the portfolio with the highest later return. The proposed mandate is fully invested and restricted to the seven ETFs in the official brief."
    )
    p(
        "The candidate holds "
        + ", ".join(
            f"{ticker} {P(weight)}"
            for ticker, weight in s["weights"].items()
            if weight > 1e-6
        )
        + ". Zero weights remain eligible for later committee-approved allocation changes."
    )
    t(
        ["Held-out result", "AEGIS", "60/40 benchmark"],
        [
            [
                label,
                P(k[key]),
                P(
                    kpis[
                        (kpis.period == "Test") & (kpis.portfolio == "60/40 benchmark")
                    ].iloc[0][key]
                ),
            ]
            for label, key in [
                ("Net CAGR", "CAGR"),
                ("Annual volatility", "volatility"),
                ("Maximum drawdown", "max_drawdown"),
            ]
        ],
        [205, 135, 135],
    )
    p(
        f'The candidate delivers {P(k["CAGR"])} net annualised compound return in the held-out sample, with {P(k["volatility"])} volatility. These are retrospective results, not a promised yield. Historical daily ES99 on the latest window is {P(h.ES)} or {D(h.ES*NAV)} of the reference capital.'
    )
    p(
        f"The central conflict is stress tolerance. The worst historical replay drawdown is {P(worst)}, above the proposed 15% limit. The hypothetical funding squeeze loses {P(-hyp)}. The draft decision is ADJUST: resolve that conflict and agree spending requirements before committing capital. If the committee will not revise limits and no compliant alternative is substantiated, do not fund the mandate as proposed."
    )
    p(
        "No human-team approval has been recorded. Automated checks support the calculations; they do not establish that the team has independently accepted the investment judgment.",
        "Small",
    )
    page("02 / Mandate and data discipline")
    p(
        "The proposed horizon is at least ten years with annual governance review. A provisional 4% nominal total-return objective is assessed against assumed 2.5% inflation, implying about 1.46% real growth before spending. The brief gives no payout rate; the team must agree one with the client. Distributions are reinvested in the return data, so the report cannot infer a sustainable cash income budget."
    )
    p(
        f'The approved sources are Yahoo Finance through yfinance and FRED DTB3. All seven ETFs have {s["data"]["n_prices"]:,} common adjusted prices from {s["data"]["start"]} through {s["data"]["end"]}. Missing aligned cells: {sum(s["data"]["missing"].values())}; dropped incomplete rows: {s["data"]["dropped_rows"]}. Adjusted closes account for vendor splits and distributions, but can be revised [2,3].'
    )
    t(
        ["ETF", "Role and material exposure"],
        [
            ["SPY", "US large-cap equities; broad market proxy"],
            ["EFA", "Developed-market equities outside the US; currency exposure"],
            ["EEM", "Emerging-market equities; currency and political risk"],
            [
                "AGG",
                "Investment-grade aggregate bonds; duration, credit and mortgage risk",
            ],
            ["GLD", "Gold; no contractual income"],
            ["XLE", "Energy equities; not direct commodity futures"],
            ["XLK", "Technology equities; overlap with SPY"],
        ],
        [55, 420],
    )
    p(
        "Simple returns are R = P/P_previous - 1. Log returns are log(P/P_previous). Dates are intersected before portfolio calculation; no price forward-fill or outlier removal is used. Large moves, flat prices and volatility breaks are flagged and retained. Snapshots are hashed and accompanied by retrieval timestamps."
    )
    adf = read("adf")
    p(
        f"Training-return ADF p-values range from {adf.p_value.min():.3g} to {adf.p_value.max():.3g}. These checks test a unit root, not normality or stable volatility [11]. FRED quotes are strictly lagged; the bank-discount rate is converted using an assumed 91-day bill. Current-vintage rates remain a historical-information limitation.",
        "Small",
    )
    page("03 / Portfolio construction")
    p(
        f'Weights are fitted on {s["n_train"]:,} daily returns ending {s["train_end"]}. The 2019-2022 development period is reported separately. The test contains {s["n_test"]} returns from {s["test_start"]} through {s["test_end"]}. No test outcome selects weights or model settings. This is a retrospective chronological exercise, not a preregistered track record.'
    )
    p(
        "The main objective is min w'Sigma w subject to full investment, nonnegative weights, 35-70% AGG, 5-20% GLD and 20-50% aggregate equity. Equity holdings have individual caps. Covariance is 90% training sample covariance plus 10% its diagonal. These limits are proposed governance assumptions rather than client-confirmed instructions [4]."
    )
    story.append(fig("allocation"))
    p(
        "Figure 1. Training-only target weights. The 70% AGG upper bound binds, leaving material duration and credit concentration despite low estimated variance.",
        "Caption",
    )
    p(
        "Alternatives are constrained mean variance (risk aversion 6), constrained risk parity, equal weights and 60/40 SPY/AGG. Historical means in the mean-variance model are shrunk halfway toward their cross-asset average. Equal weights and 60/40 are comparators and exceed the proposed aggregate equity ceiling."
    )
    p(
        "Daily rebalancing charges 10bp per dollar of absolute traded weights before the next day's return. Initial purchase and taxes are excluded. Net wealth compounds (1-cost)(1+w'R). Risk forecasts and crisis replays use gross hypothetical P&L; that distinction prevents treating their loss forecasts as exact net fund accounting.",
        "Small",
    )
    page("04 / Returns and investment trade-offs")
    rows = []
    for z in kpis[kpis.period == "Test"].itertuples():
        rows.append(
            [
                z.portfolio,
                P(z.CAGR),
                P(z.volatility),
                P(z.max_drawdown),
                f"{z.Sharpe:.2f}",
            ]
        )
    t(
        ["Held-out portfolio", "Net CAGR", "Volatility", "Drawdown", "Sharpe"],
        rows,
        [170, 80, 80, 80, 65],
    )
    story.append(fig("performance"))
    p(
        "Figure 2. Gross held-out paths illustrate allocation exposure; the table above charges the daily rebalance cost assumption. Higher-return alternatives also carry higher risk, and were not selected on this test sample.",
        "Caption",
    )
    t(
        ["AEGIS metric", "Value", "Interpretation"],
        [
            [
                "Sortino",
                f'{k["Sortino"]:.3f}',
                "Excess return / all-day downside deviation",
            ],
            ["Treynor", f'{k["Treynor"]:.3f}', "Annual excess return / beta"],
            [
                "Jensen alpha",
                P(k["Jensen_alpha"]),
                "Diagnostic alpha versus SPY, not proven skill",
            ],
            [
                "Information ratio",
                f'{k["information_ratio"]:.3f}',
                "Active return versus 60/40 / tracking error",
            ],
            ["Calmar", f'{k["Calmar"]:.3f}', "Net CAGR / maximum drawdown"],
            ["Beta", f'{k["beta"]:.3f}', "Sensitivity to SPY excess returns"],
        ],
        [125, 75, 275],
    )
    p(
        "CAPM asset betas and implied returns use training data and lagged DTB3 [5]. KPI definitions, annualization and cost treatment are specified in Methodology.md. A low-volatility result cannot establish income adequacy, crisis protection or a reliable expected alpha.",
        "Small",
    )
    page("05 / Daily VaR and Expected Shortfall")
    p(
        f'All models use the same target weights and latest {756}-return window, {s["latest_window_start"]} to {s["latest_window_end"]}. Loss is -w\'R, reported as a positive loss of NAV. VaR is a quantile. ES = q + mean[(L-q)+]/(1-alpha) measures average severe tail loss and handles finite samples consistently.'
    )
    rows = [
        [z.model, f"{z.confidence:.0%}", P(z.VaR), P(z.ES), D(z.ES * NAV)]
        for z in risk.itertuples()
        if z.confidence in [0.95, 0.99]
    ]
    t(["Model", "Level", "VaR", "ES", "ES on $10m"], rows, [125, 50, 85, 85, 130])
    story.append(fig("risk"))
    p(
        "Figure 3. Matching horizon and confidence makes model disagreement interpretable. Dollar amounts scale the one-day fractional loss by constant reference NAV.",
        "Caption",
    )
    p(
        "Historical simulation retains observed tails. Parametric risk fits a normal portfolio log return and integrates its lognormal tail exactly. Monte Carlo fits a multivariate normal to asset log returns, uses 5% diagonal covariance shrinkage, and aggregates simulated simple returns. Both Gaussian approaches can understate heavy tails. Their difference also reflects covariance treatment and nonlinear aggregation, not independent confirmation."
    )
    p(
        f'Snapshot simulation uses {s["seed"]} as seed and 50,000 draws; rolling forecasts use 10,000. The ES99 Monte Carlo batch standard error is {P(s["MC_ES99_standard_error"])} of NAV. The exported convergence table separates simulation stability from data/model uncertainty.',
        "Small",
    )
    page("06 / EVT and tail stability")
    m = s["evt_fit"]
    ci = s["evt_bootstrap"]
    p(
        f'Peaks over threshold fits a GPD to losses above the 90th percentile: {P(m["threshold"])}. The latest window gives {m["exceedances"]} exceedances. The rule is fixed before test evaluation to balance tail focus against small-sample estimation; it is not claimed to be optimal. The laboratory exposes thresholds from 85% to 95% [9,10].'
    )
    p(
        "For p = 1-alpha, VaR = u + beta/xi[(p_u/p)^xi - 1], with a logarithmic limit at xi = 0. ES = (VaR + beta - xi*u)/(1-xi), available only when xi &lt; 1. Estimates require at least 40 exceedances and confidence above the fitting threshold. At 90% confidence the app therefore reports EVT as unavailable."
    )
    story.append(fig("evt"))
    p(
        "Figure 4. Threshold changes alter both the tail sample and the fitted shape. A stable-looking line is not a formal proof that GPD asymptotics apply.",
        "Caption",
    )
    p(
        f'The fitted shape is {m["shape"]:.3f}. Its 95% block-bootstrap interval is [{ci["shape_CI"][0]:.3f}, {ci["shape_CI"][1]:.3f}], spanning zero. EVT ES99 is {P(ev.ES)}; the interval is [{P(ci["ES99_CI"][0])}, {P(ci["ES99_CI"][1])}]. The negative point estimate must not be interpreted as a dependable maximum possible market loss.'
    )
    p(
        f'{ci["valid"]} of {ci["repetitions"]} circular 20-day block resamples produced valid finite-ES fits. Each refits the threshold and parameters. Serial clustering, model misspecification and a limited tail sample remain; these intervals do not guarantee their nominal coverage. Sensitivity tables and interactive Q-Q diagnostics are supplied.',
        "Small",
    )
    page("07 / Rolling out-of-sample validation")
    p(
        "Each forecast date uses exactly the preceding 756 returns, ending strictly before that date. Portfolio weights remain fixed from the allocation training period. This is genuine one-step historical forecasting within a retrospective study. Kupiec tests hit frequency; Christoffersen tests first-order hit independence; their likelihood ratios combine into conditional coverage [6,7]."
    )
    t(
        ["99% model", "Hits / expected", "Kupiec p", "Indep. p", "CC p", "Last 250"],
        [
            [
                z.model,
                f"{int(z.exceptions)} / {z.expected:.2f}",
                f"{z.kupiec_p:.3f}",
                f"{z.independence_p:.3f}",
                f"{z.conditional_p:.3f}",
                z.traffic_last250,
            ]
            for z in b99.itertuples()
        ],
        [110, 85, 70, 70, 65, 75],
    )
    story.append(fig("backtest"))
    p(
        "Figure 5. Historical VaR99 forecasts and realized losses. Exceptions are retained as evidence rather than removed as bad data.",
        "Caption",
    )
    p(
        f"Historical simulation has {int(hist.exceptions)} exceptions against {hist.expected:.2f} expected. Its conditional-coverage p-value is {hist.conditional_p:.3f}; this is a non-rejection of that null, not proof of a correct tail model. The volatility-state extension has {int(state.exceptions)} exceptions and conditional-coverage p = {state.conditional_p:.3f}, illustrating why an adaptive feature should not be promoted merely for being more complex."
    )
    p(
        "The full test exceeds 250 observations, so its regulatory-style traffic classification is N/A. Last-250 status is separately labelled and uses precisely 250 one-day 99% forecasts: green 0-4, amber 5-9, red 10+. Other confidence levels and short selected ranges show N/A [8]. Sparse exceptions and nonstationarity limit test power.",
        "Small",
    )
    page("08 / Crisis exposure and recovery")
    p(
        "The three historical scenarios replay actual adjusted ETF returns at fixed target weights, gross of costs. They describe what this allocation would have experienced; weights estimated through 2018 were not a policy available in 2008. Recovery is measured against the replay peak before its worst drawdown, using the later observed path."
    )
    t(
        ["Scenario", "Return", "USD impact", "Peak drawdown", "Peak recovery"],
        [
            [z.scenario, P(z.return_pct), D(z.USD), P(z.max_drawdown), z.recovery_date]
            for z in ss.itertuples()
        ],
        [110, 65, 85, 85, 130],
    )
    story.append(fig("stress"))
    p(
        "Figure 6. Terminal crisis return can conceal a much larger interim drawdown. The orange bar is a hypothetical simultaneous shock, not an observed event.",
        "Caption",
    )
    p(
        "The funding squeeze assumes SPY -25%, EFA -30%, EEM -35%, AGG -12%, GLD -10%, XLE -25% and XLK -35%. It deliberately removes the assumption that bonds or gold must offset equities. No scenario probability is assigned; no synthetic recovery date is invented."
    )
    p(
        f"The largest historical drawdown is {P(worst)}, and the synthetic loss is {P(-hyp)} ({D(-hyp*NAV)}). Thus a bond-heavy allocation can be modestly volatile in ordinary conditions yet breach the proposed 15% crisis tolerance. Asset-level P&L contributions and comparisons with all alternatives are exported and available in the crisis studio.",
        "Small",
    )
    page("09 / Risk budgeting and analytical value")
    p(
        "Risk budgeting identifies where position changes matter. Historical ES contributions are derivatives of the finite-sample estimator, including interpolated quantile terms. Euler homogeneity makes their weighted sum equal portfolio ES; a numerical derivative test checks this identity. Gaussian simple-return VaR contributions are labelled separately rather than being attributed to the empirical or Monte Carlo model."
    )
    t(
        ["Holding", "Weight", "ES contribution", "ES share"],
        [
            [z.ticker, P(z.weight), P(z.component_ES), P(z.ES_share)]
            for z in rc.itertuples()
        ],
        [115, 95, 140, 125],
    )
    p(
        "The decision lab lets reviewers change target weights, the AGG floor, equity cap and a dollar risk budget. Re-optimization uses only the original allocation training slice. Current-risk experiments are kept separate from saved validation forecasts. A proportional exposure cap is diagnostic; cash is not an approved holding, so any funded change must use the seven eligible assets or an approved mandate revision."
    )
    rg = s["regime_comparison"]
    p(
        f'The interpretable volatility-state extension scales historical shocks by the short/long volatility ratio. Its mean joint FZ0 score minus historical is {rg["mean_difference"]:+.3f}; the paired 95% block interval is [{rg["CI"][0]:+.3f}, {rg["CI"][1]:+.3f}]. Lower is better. The interval crosses zero, and coverage worsens, so the extension is retained as research evidence rather than adopted as the default [12].'
    )
    p(
        "The scorecard avoids arbitrary composite weights: it shows each proposed policy check independently, with ±20% limit sensitivity. The evidence ledger ties metrics to their data window, formula, assumptions and validation. The optional assistant is a deterministic guide to that ledger; no external LLM controls a calculation or supplies a financial fact."
    )
    page("10 / Proposed committee action")
    p(
        "<b>Draft decision: ADJUST the mandate before funding.</b> The training minimum-variance candidate is suitable for discussion because its equity risk is capped and its construction does not depend on optimistic expected-return estimates. It is not ready for unconditional approval under a 15% crisis-loss/drawdown tolerance."
    )
    p(
        f"Ask the committee whether it can accept at least the observed {P(worst)} replay drawdown and assumed {P(-hyp)} funding-squeeze loss, while recognizing that future losses can exceed both. If not, require a new eligible-asset allocation that meets agreed stress constraints, or reject the current proposal. A favourable daily VaR backtest does not override the stress-limit breach."
    )
    story.append(
        tab(
            ["Evidence", "Implication"],
            [
                [
                    "70% AGG cap binds",
                    "Lower estimated variance comes with bond concentration and rate risk",
                ],
                [
                    f'Net held-out CAGR {P(k["CAGR"])}',
                    "Useful outcome, but not a promised sustainable return",
                ],
                [
                    f"Historical ES99 {P(h.ES)}",
                    "Use as one monitored estimate; compare Gaussian and EVT results",
                ],
                [
                    f"Worst replay drawdown {P(worst)}",
                    "The proposed 15% tolerance needs explicit resolution",
                ],
                [
                    "Spending requirement unspecified",
                    "Approve a payout/real-growth budget before implementation",
                ],
                [
                    "Human-team approval absent",
                    "The team must evaluate and defend the recommendation",
                ],
            ],
            [230, 245],
        )
    )
    p(
        "A proposed operating process is daily risk/exception review, monthly exposure and turnover review, and annual mandate/assumption review. These frequencies are governance suggestions, not statistically optimized thresholds. Trading requires a committee-approved risk appetite, feasible rebalance policy and independent sign-off."
    )
    p(
        "Equal weighting and 60/40 are rejected as immediate conservative candidates because their equity allocations exceed the proposed ceiling. Mean variance relies more heavily on estimated returns. Constrained risk parity remains a credible alternative for human discussion; its better later performance is not used retrospectively to replace the pre-specified candidate.",
        "Small",
    )
    page("11 / Limitations, reproducibility and AI")
    p(
        "Daily risk does not measure a ten-year endowment shortfall. The models omit spending, liquidity needs, custody, tax, trade impact, and detailed income accounting. Reinvestment assumptions can overstate spendable growth. All current risk estimates are conditional on a finite historical sample; neither VaR nor EVT is a worst-loss guarantee."
    )
    p(
        "Gaussian models miss heavy tails. EVT depends on threshold validity, finite tail means and serial-dependence assumptions. Current-vintage rates and adjusted prices are not a perfect point-in-time database. ADF rejection does not establish independence. Historical stress replays and post-2018 portfolio design cannot be portrayed as a strategy operating before that date."
    )
    p(
        "The project supplies a hashed data snapshot, approved-source downloader, cleaned returns, flags, fitted EVT parameters, forecasts with estimation dates, machine-readable risk tables, figures and a manifest. Run the numerical and report pipeline, then launch the interface:"
    )
    p(
        '<font name="Courier">pip install -r requirements.txt<br/>python run.py --reproduce<br/>streamlit run app.py</font>',
        "Small",
    )
    p(
        "No API key is required for mandatory operation. The data snapshot supports offline analysis. Live source failures produce errors rather than invented observations. Refreshing data can change results; a new hash means a new dataset. Exact runtime and QA evidence are documented in Testing_and_Validation.md."
    )
    p(
        "OpenAI Codex assisted with implementation, proposed modelling decisions, execution, tests, interpretation, interface and report/pitch drafting. Independent human validation is pending. The team must substantiate its portfolio choices, stress interpretation and final decision under section 8.7 of the official brief; agent checks do not satisfy that requirement."
    )
    p(
        "Repository publication and team approval are external actions. The package contains deployment instructions and a pending approval record; it does not invent a GitHub URL, deployed app or completed human signature. The full policy assumptions and sources are available in the app and documentation."
    )
    page("References")
    sources = (ROOT / "documentation/Sources.md").read_text(encoding="utf-8-sig")
    sources = sources.translate(
        str.maketrans(
            {
                "\u2013": "-",
                "\u2014": "-",
                "\u2019": "'",
                "\u2018": "'",
                "\u201c": '"',
                "\u201d": '"',
            }
        )
    )
    for line in sources.splitlines():
        if re.match(r"^\d+\.", line):
            p(line, "Small")
    write("Technical_Report.pdf", story)
    (ROOT / "reports/Technical_Report_Source.md").write_text(
        "# AEGIS technical report generated text\n\n" + "\n\n".join(record),
        encoding="utf-8",
    )
    # One-page committee documents contain only figures derived above.
    sheet = [
        para("AEGIS / Executive tear sheet", "H1"),
        para("Quantum-X | Serendib University Endowment | USD 10 million", "H2"),
        para(
            f'Data as of {s["data"]["end"]}. Proposal: ADJUST, pending independent team approval.',
            "Caption",
        ),
        para(
            "Horizon: 10+ years. Provisional objective: 4% nominal total return before spending; assumed inflation 2.5%. A payout/income budget remains to be agreed."
        ),
        tab(
            ["Proposed holding", "Weight", "Dollar allocation"],
            [[t, P(v), D(v * NAV)] for t, v in s["weights"].items() if v > 1e-6],
            [190, 100, 185],
        ),
        Spacer(1, 10),
        tab(
            ["Held-out net KPI", "Value", "Latest daily risk99", "% NAV / USD"],
            [
                [
                    "CAGR",
                    P(k["CAGR"]),
                    "Historical VaR",
                    f"{P(h.VaR)} / {D(h.VaR*NAV)}",
                ],
                [
                    "Volatility",
                    P(k["volatility"]),
                    "Historical ES",
                    f"{P(h.ES)} / {D(h.ES*NAV)}",
                ],
                [
                    "Maximum drawdown",
                    P(k["max_drawdown"]),
                    "EVT ES",
                    f"{P(ev.ES)} / {D(ev.ES*NAV)}",
                ],
            ],
            [135, 70, 110, 160],
        ),
        Spacer(1, 10),
        para(
            f"Capital at risk: worst historical replay drawdown {P(worst)}; hypothetical squeeze loss {P(-hyp)} ({D(-hyp*NAV)}). These exceed the proposed 15% tolerance and are not bounds on future loss."
        ),
        para(
            f"Validation: historical VaR99 has {int(hist.exceptions)}/{int(hist.n)} exceptions; Kupiec p={hist.kupiec_p:.3f}, independence p={hist.independence_p:.3f}. The last 250 forecasts are {hist.traffic_last250.lower()}; non-rejection is not a guarantee."
        ),
        para(
            "Committee action: resolve the crisis-risk limit and spending assumptions before funding. Retain the minimum-variance candidate for review; require a revised eligible allocation or reject if the agreed tolerance cannot be met."
        ),
        para(
            "Assumptions: daily target rebalancing, 10bp per dollar traded for net KPIs; gross one-day risk and stress P&L; finite historical sample; Gaussian and EVT model uncertainty. Gold generates no contractual income. All recommendations remain AI-assisted proposals.",
            "Small",
        ),
    ]
    write("Executive_Tear_Sheet.pdf", sheet)
    memo = [
        para("Investment committee memorandum", "H1"),
        para("To the Serendib University Endowment Investment Committee", "H2"),
        para(
            "From Quantum-X | 24 October 2026 | Draft for independent human-team review",
            "Caption",
        ),
        para(
            "<b>Proposed decision: ADJUST the mandate before committing capital.</b> A low-volatility portfolio is a useful starting point, but its crisis exposure exceeds the proposed tolerance."
        ),
        para(
            "The candidate holds "
            + ", ".join(f"{P(v)} {t}" for t, v in s["weights"].items() if v > 1e-6)
            + ". It was selected by constrained variance minimization on pre-2019 returns, not by selecting the strongest later performer."
        ),
        para(
            f'In the {s["n_test"]}-day held-out period it earned {P(k["CAGR"])} net CAGR with {P(k["volatility"])} volatility and {P(k["max_drawdown"])} maximum drawdown. Its latest historical daily ES99 is {D(h.ES*NAV)}; EVT gives {D(ev.ES*NAV)}. These estimates are model-dependent, not maximum losses.'
        ),
        para(
            f"The decisive concern is resilience. Historical replay reaches a {P(worst)} drawdown; the assumed funding squeeze loses {D(-hyp*NAV)}. Both exceed a 15% tolerance. A green last-250 VaR traffic light does not settle that mismatch."
        ),
        para(
            "<b>Requested action.</b> Confirm the acceptable crisis drawdown and loss budget, agree a sustainable payout/income requirement, and approve an executable rebalancing policy. If the committee retains the proposed 15% limit, require a substantiated reallocation within the seven eligible ETFs before funding; reject the current allocation if that cannot be achieved."
        ),
        para(
            "A bond floor reduces ordinary equity exposure but introduces rate and credit risk; SPY and XLK overlap. Gold diversifies drivers without contractual yield. The 60/40 and equal-weight comparisons exceed the proposed equity cap, while expected-return optimization is estimation-sensitive. Constrained risk parity should remain in the discussion."
        ),
        para(
            "Review daily risk and exceptions, exposures monthly, and mandate assumptions annually. These are proposed governance frequencies. The study excludes endowment spending, taxes and market impact and does not prove that historical or hypothetical losses bound the future."
        ),
        para(
            "OpenAI Codex assisted with this draft and its analysis. No independent team approval is recorded. The human team must review, revise and defend the investment judgment before it is submitted as its own recommendation.",
            "Small",
        ),
    ]
    write("Investment_Committee_Memo.pdf", memo)
    build_pitch_data(s, risk, b99, ss, kpis)


def build_pitch_data(s, risk, bt, stress, kpis) -> None:
    """Data-only slide plan for native editable chart/table generation in JS."""
    k = s["out_of_sample"]
    ev = s["evt_fit"]
    rg = s["regime_comparison"]
    selected = s["candidate"]
    slides = []

    def add(title, body, note, seconds=55, chart=None, table=None):
        slides.append(
            dict(
                title=title,
                body=body,
                notes=note,
                seconds=seconds,
                chart=chart,
                table=table,
            )
        )

    add(
        "AEGIS",
        "Capital preservation research\nQuantum-X · Serendib University Endowment\nUSD 10 million proposed mandate",
        "Introduce the mandate and identify this as an AI-assisted proposal pending independent team review. The objective is a defensible loss budget, not the highest backtested return.",
        35,
    )
    add(
        "The investment decision",
        "ADJUST the mandate before funding\nResolve stress tolerance and the spending objective",
        "The final brief asks for a decision. Explain that low daily volatility alone does not justify accepting the mandate. A 15% proposed drawdown limit conflicts with the replay evidence.",
        50,
    )
    add(
        "A conservative policy framework",
        "10+ year horizon · provisional 4% nominal objective\nAGG 35–70% · gold 5–20% · equities 20–50%\nNo leverage; daily rebalancing is a research assumption",
        "The 4% objective assumes 2.5% inflation, about 1.46% real growth before spending. No client payout rate was supplied. Constraints are our proposed assumptions for human review, not confirmed instructions.",
        55,
    )
    add(
        "Data before decisions",
        f'{s["data"]["n_prices"]:,} aligned adjusted closes · seven eligible ETFs\nTraining through 2018 · development 2019–2022\nTest {s["test_start"]} to {s["test_end"]}',
        "Sources: approved Yahoo through yfinance and FRED DTB3. No missing returned aligned cells. Flags are retained. Rates are strictly lagged but current vintage. This is a retrospective chronological experiment, not a preregistered live record. See documentation/Sources.md.",
        55,
    )
    add(
        "The proposed allocation",
        "Training variance minimization\nThe AGG cap binds; bond concentration remains a risk",
        "Explain sample covariance with 10% diagonal shrinkage, the constraints, and why zero international/energy weights are allowed. Geographic diversification was not forced. These weights need team review.",
        60,
        chart=dict(
            categories=TICKERS,
            series=[
                dict(name="Weight (%)", values=[100 * s["weights"][t] for t in TICKERS])
            ],
        ),
    )
    kk = kpis[kpis.period == "Test"]
    add(
        "Return is one part of suitability",
        f'AEGIS net held-out CAGR {P(k["CAGR"])}\nAnnual volatility {P(k["volatility"])} · drawdown {P(k["max_drawdown"])}',
        "Compare all alternatives without choosing the best test outcome. Costs are 10bp per dollar of absolute daily turnover. Benchmark uses the same net accounting. Income adequacy remains untested.",
        60,
        table=[["Portfolio", "Net CAGR", "Volatility", "Max DD"]]
        + [
            [z.portfolio, P(z.CAGR), P(z.volatility), P(z.max_drawdown)]
            for z in kk.itertuples()
        ],
    )
    rr = risk[risk.confidence == 0.99]
    add(
        "Risk estimates depend on assumptions",
        "One-day 99% losses on the same portfolio\nGaussian agreement does not establish tail adequacy",
        "Historical quantiles retain observed extremes. Parametric normal portfolio log returns and Monte Carlo normal asset log returns aggregate differently; both omit heavy tails. Dollar amounts use constant $10m NAV.",
        60,
        chart=dict(
            categories=rr.model.tolist(),
            series=[
                dict(name="VaR99 (% NAV)", values=(rr.VaR * 100).tolist()),
                dict(name="ES99 (% NAV)", values=(rr.ES * 100).tolist()),
            ],
        ),
    )
    add(
        "EVT makes uncertainty visible",
        f'90% threshold · {ev["exceedances"]} exceedances\nShape {ev["shape"]:.3f}; uncertainty spans zero\nTail laboratory exposes threshold sensitivity',
        "Threshold was fixed before the test to provide around 76 exceedances in 756 observations. Explain the GPD excess model, minimum 40 count, ES unavailable for shape at least one, and why a negative point estimate is not a safe loss bound. Source: McNeil/Frey context and SciPy, documentation/Sources.md.",
        60,
    )
    add(
        "Forecasts precede observed losses",
        "756 prior observations for every date\nLegacy Basel traffic lights use exactly 250 days at 99%",
        "Kupiec tests frequency and Christoffersen tests first-order clustering. Non-rejection is not proof. Last 250 is explicitly separate from the full test. Sources: Kupiec 1995, Christoffersen 1998 and BIS 1996, documentation/Sources.md.",
        60,
        table=[["99% model", "Exceptions", "Kupiec p", "CC p", "Last250"]]
        + [
            [
                z.model,
                str(int(z.exceptions)),
                f"{z.kupiec_p:.3f}",
                f"{z.conditional_p:.3f}",
                z.traffic_last250,
            ]
            for z in bt.itertuples()
        ],
    )
    add(
        "Crisis losses challenge the risk budget",
        "Terminal return can conceal a deeper interim drawdown\nHistorical replay is hindsight exposure, not a live track record",
        "Replay actual returns through 2008, COVID and 2022. Contrast terminal return with peak drawdown. The simultaneous funding squeeze is explicitly assumed, with no probability or invented recovery.",
        60,
        chart=dict(
            categories=stress.scenario.tolist(),
            series=[
                dict(
                    name="Terminal loss (%)", values=(-stress.return_pct * 100).tolist()
                ),
                dict(
                    name="Peak drawdown (%)",
                    values=(stress.max_drawdown * 100).tolist(),
                ),
            ],
        ),
    )
    add(
        "Useful innovation includes rejection",
        f'Volatility-state score difference {rg["mean_difference"]:+.3f}\n95% interval [{rg["CI"][0]:+.3f}, {rg["CI"][1]:+.3f}]\nNo reliable improvement; retain historical baseline',
        "Negative FZ0 difference would favour the extension. Its confidence interval crosses zero and its exception clustering is rejected. Demonstrate the evidence ledger, threshold lab, crisis controls and separate policy checks. The deterministic assistant uses no external LLM.",
        55,
    )
    add(
        "Conditions for a fundable mandate",
        "Agree crisis tolerance and payout requirement\nValidate an eligible allocation and feasible rebalancing\nHuman team reviews, revises and signs the decision",
        "Conclude with ADJUST. If 15% remains binding, require substantiated reallocation or reject this candidate. Limits can be exceeded in the future. No approval, GitHub publication or deployment is fabricated. The team must own and defend the final judgment under brief section 8.7.",
        50,
    )
    (ROOT / "presentation/pitch_data.json").write_text(json.dumps(slides, indent=2))
    total = sum(x["seconds"] for x in slides)
    (ROOT / "presentation/Speaker_Notes.md").write_text(
        "# Pitch rehearsal script\n\n"
        + f"Target duration: {total//60} minutes {total%60} seconds. Timings are rehearsal estimates, not a recorded performance.\n\n"
        + "\n\n".join(
            f'## {i}. {x["title"]} — {x["seconds"]} seconds\n\n{x["notes"]}'
            for i, x in enumerate(slides, 1)
        ),
        encoding="utf-8",
    )
