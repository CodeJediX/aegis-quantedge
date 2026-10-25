"""Selected-portfolio PDF/CSV exports with explicit provenance and approval state."""

from datetime import datetime, timezone
from html import escape
from io import BytesIO
import hashlib
import importlib.metadata as md
import json
import re
import zipfile

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak

from .config import NAV, SEED, N_SIM, TICKERS, TRAIN_END, TEST_START, TC
from .interactive import usd


def provenance(result, dataset_version, alpha, method):
    return dict(portfolio=result["name"], allocation_id=result["allocation_id"],
                dataset_version=dataset_version, generated_utc=datetime.now(timezone.utc).isoformat(),
                data_through=result["latest_end"], capital_USD=NAV, training_end=TRAIN_END,
                test_start=result["test_start"], test_end=result["test_end"],
                lookback=result["lookback"], current_confidence=alpha, current_method=method,
                seed=SEED, snapshot_MC_draws=N_SIM, rolling_MC_draws=10000,
                transaction_cost_per_traded_dollar=TC,
                forecast_horizon="One trading day", limits=result["limits"],
                versions={package:md.version(package) for package in ["numpy", "pandas", "scipy", "statsmodels", "streamlit", "plotly", "reportlab"]},
                human_approval="PENDING - no independent human approval recorded")


def csv_bytes(frame, metadata):
    out = frame.copy()
    for key in ["portfolio", "allocation_id", "dataset_version", "generated_utc", "capital_USD"]:
        if key not in out:
            out[key] = metadata[key]
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(lambda v: "'" + v if isinstance(v, str) and v.startswith(("=", "+", "-", "@")) else v)
    return out.to_csv(index=False, float_format="%.12g").encode("utf-8-sig")


def make_report(result, risk, decision, metadata, validation=None, kind="technical"):
    if kind not in {"technical", "tear_sheet", "memo"}:
        raise ValueError("Unknown report type")
    output = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="AEGISBody", fontSize=9, leading=13, spaceAfter=8, textColor=colors.HexColor("#203840")))
    styles.add(ParagraphStyle(name="AEGISSmall", fontSize=8, leading=11, spaceAfter=5))
    styles.add(ParagraphStyle(name="AEGISHead", fontName="Times-Roman", fontSize=24, leading=29, spaceAfter=15, textColor=colors.HexColor("#123D3D")))
    story = []

    def p(text, small=False):
        story.append(Paragraph(escape(str(text)), styles["AEGISSmall" if small else "AEGISBody"]))

    def title(text):
        story.append(Paragraph(escape(text), styles["AEGISHead"]))

    def tab(headers, rows, widths=None):
        values = [[Paragraph(escape(str(v)), styles["AEGISSmall"]) for v in row] for row in [headers] + rows]
        table = Table(values, colWidths=widths or [475 / len(headers)] * len(headers), repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0),colors.HexColor("#DBEEEA")),
                                  ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F0F5F5")]),
                                  ("VALIGN",(0,0),(-1,-1),"TOP"), ("TOPPADDING",(0,0),(-1,-1),5),
                                  ("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        story.append(table)
        story.append(Spacer(1,10))

    def percent(v):
        return "Unavailable" if v is None or not np.isfinite(v) else f"{v:.2%}"

    def money(v):
        return "Unavailable" if v is None or not np.isfinite(v) else f"USD {usd(v):,.0f}"

    def base_header(label):
        title("AEGIS | " + label)
        p(f'{metadata.get("portfolio_label",result["name"])} | allocation {result["allocation_id"]} | USD {NAV:,.0f} reference capital')
        p(f'Dataset {metadata["dataset_version"][:16]} | data through {metadata["data_through"]} | analysis {metadata["generated_utc"]}', True)

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#536E74"))
        canvas.drawString(58,27,"AEGIS | Historical research | Human approval pending")
        canvas.drawRightString(537,27,str(doc.page))

    k = result["kpi"]
    failed = result["checks"].query("status == 'FAIL'")
    worst = float(result["stress"].query("n > 1").max_drawdown.max())

    def decision_content():
        p("AUTOMATED RECOMMENDATION: " + decision["status"] + ". Human approval: PENDING.")
        p("This assesses the selected allocation against proposed limits. It is not an authorization to invest. Return estimates use training data; reported test outcomes are retrospective.")
        tab(["Metric", "Result"], [["Training estimated annual arithmetic return",percent(result["expected_return"])],
            ["Held-out net CAGR",percent(k["CAGR"])], ["Held-out maximum drawdown",percent(k["max_drawdown"])],
            ["Current historical daily ES99",percent(result["ES99"]) + " / " + money(result["ES99"])],
            ["Worst historical crisis drawdown",percent(worst) + " / " + money(worst)]], [270,205])

    if kind in {"tear_sheet", "memo"}:
        base_header("Executive tear sheet" if kind == "tear_sheet" else "Investment committee memorandum")
        decision_content()
        if kind == "tear_sheet":
            tab(["Holding", "Weight"], [[t,percent(w)] for t,w in zip(TICKERS,result["weights"])], [270,205])
        else:
            p("Failed constraints: " + ("; ".join(failed.check.tolist()) if len(failed) else "No numerical policy failures; validation and human approval still apply."))
            p("Required action: " + " ".join(decision["actions"][:5]))
            p("The proposal must be revised or rejected if the client retains a limit that the observed results breach. Spending, inflation, liquidity needs and implementation feasibility require an explicit human mandate decision.")
        p("Limits and caveats: seven permitted ETFs; long only; daily rebalancing with 10bp L1 turnover cost for net KPIs. Crisis replays and one-day risk are gross. Hypothetical shocks are assumptions, not probabilities. Historical risk does not bound future loss. AI-assisted analysis; independent human review is pending.", True)
    else:
        base_header("Selected portfolio technical report")
        decision_content()
        p("Required corrective actions")
        for action in decision["actions"]:
            p(action, True)
        p("Research objective: a conservative USD10m endowment case with a 10+ year horizon, annual governance review and a proposed nominal return objective. Spending needs remain unconfirmed. This export follows the selected portfolio and does not replace the locked research package.")
        story.append(PageBreak())
        base_header("2 | Allocation, objectives and performance")
        tab(["ETF", "Selected weight"], [[t,percent(w)] for t,w in zip(TICKERS,result["weights"])], [180,295])
        names={"CAGR":"Net CAGR","arithmetic_return":"Annual arithmetic return","volatility":"Annual volatility","Sharpe":"Sharpe ratio","Sortino":"Sortino ratio","Treynor":"Treynor ratio","Jensen_alpha":"Annual Jensen alpha","information_ratio":"Information ratio","max_drawdown":"Maximum drawdown","Calmar":"Calmar ratio","beta":"Beta to SPY","cumulative_return":"Cumulative net return","annual_turnover":"Annual L1 turnover"}
        tab(["Performance diagnostic", "Held-out result"], [[label,percent(k[name]) if name in {"CAGR","arithmetic_return","volatility","max_drawdown","Jensen_alpha","cumulative_return","annual_turnover"} else "Unavailable" if k[name] is None else f"{k[name]:.4f}"] for name,label in names.items()], [270,205])
        p("CAGR compounds net simple returns over observations/252. Annual volatility uses sample standard deviation. Sharpe and Sortino use the lagged risk-free series; downside deviation includes all observations. CAPM uses SPY as an imperfect market proxy. No training return estimate is a guaranteed or live expected return.", True)
        story.append(PageBreak())
        base_header("3 | One-day downside risk")
        rows = [[row.model, percent(row.VaR),percent(row.ES), money(row.VaR),money(row.ES)] for row in risk.itertuples()]
        tab(["Model","VaR","ES","VaR amount","ES amount"],rows,[93,63,63,128,128])
        p(f'All models above use confidence {metadata["current_confidence"]:.0%} and the selected {result["lookback"]}-return window, {result["latest_start"]} to {result["latest_end"]}. Dollar values always multiply return fractions by USD10,000,000.')
        p("Historical VaR is an interpolated quantile. ES is q + mean[(loss-q)+]/(1-alpha). The parametric model integrates a Gaussian portfolio log-return tail. Monte Carlo uses correlated Gaussian asset log returns with 5% diagonal covariance shrinkage, then exact simple-return aggregation. EVT fits GPD excesses above a justified threshold; no extrapolation is reported at or below that threshold.")
        p("EVT uncertainty, threshold sensitivity and serial clustering are material. At least 40 exceedances are required to fit; fewer than 80 triggers a cautious application warning. ES is unavailable when fitted shape is at least 1. Intervals are conditional block-resampling diagnostics, not coverage guarantees.")
        story.append(PageBreak())
        base_header("4 | Historical and hypothetical stress")
        tab(["Scenario","Terminal return","Capital impact","Maximum drawdown"], [[row.scenario,percent(row.return_pct),money(row.return_pct),percent(row.max_drawdown)] for row in result["stress"].itertuples()],[135,95,135,110])
        p("The 2008, 2020 and2022 paths use actual adjusted-ETF observations and the currently selected constant target weights. They are retrospective exposure replays, not strategies held at those dates. Their P&L is gross of trading costs. Recovery dates follow the same hindsight weights through the remaining dataset.")
        p("The funding-squeeze event applies simultaneous assumed returns to the seven holdings. It has no estimated probability or invented recovery path. Asset contributions include changing NAV for historical daily replays and sum to total scenario return. Maximum drawdown is distinct from terminal loss.")
        p("A 15.23% loss on this reference capital is USD1,523,000. A15% maximum tolerated loss is USD1,500,000. Similar-looking percentages and dollar labels do not change these units.")
        story.append(PageBreak())
        base_header("5 | Validation and policy checks")
        if validation is not None and len(validation):
            v = validation[np.isclose(validation.confidence,metadata["current_confidence"])]
            tab(["Model","Full exceptions","Latest 250","Kupiec p","Independence p","Joint p"], [[row.model,f'{row.exceptions}/{row.n}',f'{row.last250_exceptions}/{row.last250_n} / {row.traffic_last250}',f'{row.kupiec_p:.3f}',"N/A" if pd.isna(row.independence_p) else f'{row.independence_p:.3f}',"N/A" if pd.isna(row.conditional_p) else f'{row.conditional_p:.3f}'] for row in v.itertuples()],[85,75,100,65,85,65])
        else:
            p("Selected-allocation rolling validation has not been run. Fixed-reference forecasts are not substituted or relabelled as custom-portfolio evidence.")
        tab(["Policy test","Observed","Status"], [[row.check,percent(row.value),row.status] for row in result["checks"].itertuples()],[300,95,80])
        p("Coverage, independence and conditional-coverage tests answer different questions. Basel-style traffic lights require250 one-day99% forecasts; full-sample counts and latest250 counts are reported separately. No statistical non-rejection is regulatory or investment approval.",True)
        story.append(PageBreak())
        base_header("6 | Data, model parameters and reproducibility")
        labels={"capital_USD":"Reference capital (USD)","training_end":"Training end","test_start":"Test start","test_end":"Test end","lookback":"Prior returns in risk window","seed":"Random seed","snapshot_MC_draws":"Snapshot MC draws","rolling_MC_draws":"Rolling MC draws","transaction_cost_per_traded_dollar":"Cost per traded dollar"}
        tab(["Parameter","Value"], [[label,f'{metadata[key]:,}' if key in {"capital_USD","snapshot_MC_draws","rolling_MC_draws","lookback"} else str(metadata[key])] for key,label in labels.items()],[210,265])
        p("Proposed limits: " + "; ".join(key.replace("_"," ")+" = "+percent(value) for key,value in result["limits"].items()) + ". Editing these assumptions does not record client approval.",True)
        p("Approved inputs: Yahoo Finance through yfinance adjusted close, and FRED DTB3 for the lagged risk-free proxy. The common-calendar snapshot is hash verified. No live download is required to launch the app; unavailable providers do not cause synthetic data substitution.")
        p("Processing: verify snapshot checksums and positive, finite, unique chronological prices; compute exact simple returns and statistical log returns; retain anomaly flags; inspect training-only ADF tests. FRED uses strictly earlier observations. Common missing exchange dates and current-vintage revisions remain disclosed limitations.")
        p("Installed versions: " + "; ".join(key+"="+value for key,value in metadata["versions"].items()),True)
        p("Reproduce: pip install -r requirements.txt; streamlit run hosted_app.py. Locked research pipeline: python run.py --reproduce. Tests: python -m unittest discover -s tests. The full dataset fingerprint is included in metadata.json alongside this export.")
        story.append(PageBreak())
        base_header("7 | Interpretation, limitations and responsibility")
        p("Training-only optimization enforces asset constraints, a return target, volatility, empirical ES99, training drawdown and the assumed funding shock. Preservation, balanced-growth and return priorities share the proposed hard limits. An optimizer that finds no feasible solution reports failure rather than relaxing constraints silently.")
        p("2020 and2022 crises and all held-out outcomes are assessment data, not optimization inputs. Nevertheless, the overall design was developed retrospectively; user-edited portfolios are not preregistered unseen strategies. Repeated custom exploration can overfit the historical test period.")
        p("Additional limits: daily constant-weight rebalancing may be impractical; initial establishment, taxes, spending, custody, market impact and liquidity stress are omitted. Bond duration/convexity, ETF tracking, cross-currency exposures and the overlap between SPY and sector ETFs matter. A first-order rate-shock what-if is an explicit assumption, not a bond-price forecast.")
        p("Research innovation consists of interpretable volatility scaling, tail-threshold sensitivity, conditional block intervals, exact empirical ES attribution and constrained downside-aware optimization. Negative or inconclusive results are retained. There is no unsupported predictive or capital-protection claim.")
        p("AI use: OpenAI Codex assisted implementation, tests, interpretation, interface and reports. Automated reference checks are not independent human validation. The team must review, revise, understand and defend all material conclusions. The deterministic Research guide does not call an external generative model.")
        p("FINAL HUMAN DECISION: PENDING. A named human investment committee must agree the mandate, risk limits, spending assumptions, allocation and final APPROVE/REVISE/REJECT decision. This document records an automated research assessment only.")
        p("Source references: Yahoo adjusted prices via yfinance; FRED DTB3 (fred.stlouisfed.org/series/DTB3); BIS backtesting framework (bis.org/publ/bcbsc223.pdf); SciPy generalized Pareto documentation (docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genpareto.html). Full methodology, references and AI disclosure are included in the fixed reference package and the website.", True)

    SimpleDocTemplate(output,pagesize=(595.28,841.89),leftMargin=60,rightMargin=60,
                      topMargin=45,bottomMargin=48,title="AEGIS - " + result["name"],author="Quantum-X; AI-assisted research").build(story,onFirstPage=footer,onLaterPages=footer)
    return output.getvalue()


def export_package(result, risk, decision, metadata, validation=None):
    slug = re.sub(r"[^a-zA-Z0-9_-]+","_",result["name"]).strip("_")[:45] or "portfolio"
    stamp = metadata["generated_utc"][:19].replace(":","").replace("-","")
    prefix = f'aegis_{slug}_{result["allocation_id"]}_{stamp}'
    entries = {"metadata.json":json.dumps(metadata,indent=2,allow_nan=False).encode(),
               "recommendation.json":json.dumps(decision,indent=2,allow_nan=False).encode()}
    for key, frame in {"weights":pd.DataFrame(dict(ticker=TICKERS,weight=result["weights"])),
                       "risk":risk, "stress":result["stress"], "policy_checks":result["checks"],
                       "performance":pd.DataFrame([result["kpi"]])}.items():
        entries[key+".csv"] = csv_bytes(frame,metadata)
    if validation is not None:
        entries["validation.csv"] = csv_bytes(validation,metadata)
    for kind in ["technical","tear_sheet","memo"]:
        entries[kind+".pdf"] = make_report(result,risk,decision,metadata,validation,kind)
    entries["SHA256SUMS.txt"] = "\n".join(hashlib.sha256(data).hexdigest()+"  "+name for name,data in entries.items()).encode()
    buffer = BytesIO()
    with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as archive:
        for name,data in entries.items():
            archive.writestr(prefix+"/"+name,data)
    return prefix, buffer.getvalue(), entries
