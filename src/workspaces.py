"""Interactive research views: one selected allocation, explicit reference results."""

from dataclasses import asdict
from html import escape
import hashlib
import json
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import genpareto

from .config import ROOT, TICKERS, NAV, TRAIN_END, TEST_START, WINDOW, SEED, N_SIM
from .portfolio import path, capm, moments, validate_weights
from .risk import contributions, empirical, mc_losses
from .evt import fit, estimate, sensitivity, uncertainty, reliability
from .backtesting import forecasts, summarize, paired_score_ci
from .database import research_version
from .interactive import Limits, analyze, recommendation, compare, optimize, allocation_id, usd, library_json, parse_library, what_if
from .exports import provenance, export_package, csv_bytes
from .product import POLICY_CONTROLS, policy_parameters, remember_policy, restore_policy, restore_reference
from .ui import chart, table, pct, lede, open_workspace, current_risk, read, saved_allocations_panel


def money_fraction(value):
    return "Unavailable" if value is None or not np.isfinite(value) else f"USD {usd(value):,.0f}"


def limits_from_state():
    return policy_parameters(st.session_state)


def remember_policy_control(key):
    remember_policy(st.session_state, key)


def reset_policy_controls():
    restore_policy(st.session_state)


def reset_reference_context():
    restore_reference(st.session_state)


@st.cache_data(show_spinner=False, max_entries=30)
def selected_analysis(r, rf, weights, name, lookback, proposed_limits):
    return analyze(r, rf, np.array(weights), name, lookback, Limits(**proposed_limits))


@st.cache_data(show_spinner=False, max_entries=12)
def comparison(r, rf, allocations, lookback, proposed_limits):
    return compare(r, rf, {k:np.array(v) for k,v in allocations.items()}, lookback, Limits(**proposed_limits))


@st.cache_data(show_spinner=False, max_entries=8)
def rolling_selected(r, weights, lookback):
    return forecasts(r, np.array(weights), start=TEST_START, window=lookback, n_mc=10000)


@st.cache_data(show_spinner=False, max_entries=16)
def run_optimizer(train, proposed_limits, priority):
    return optimize(train, Limits(**proposed_limits), priority)


@st.cache_data(show_spinner=False, max_entries=16)
def tail_interval(loss, threshold, alpha):
    return uncertainty(np.array(loss), threshold, alpha, reps=100, block=20)


def validation_key(result):
    return research_version()[:16]+"_"+result["allocation_id"]+"_"+str(result["lookback"])


def available_forecasts(result, alloc):
    if result["lookback"] == WINDOW and np.allclose(result["weights"], alloc.iloc[:,0].to_numpy(), atol=1e-11, rtol=0):
        frame = read("forecasts")
        frame.date = pd.to_datetime(frame.date)
        return frame[frame.date >= pd.Timestamp(TEST_START)].copy(), "Locked reference weights and 756-day window"
    frame = st.session_state.get("selected_backtests", {}).get(validation_key(result))
    return (frame, "Selected allocation / selected lookback") if frame is not None else (None, "Selected allocation has not yet been backtested")


def apply_custom(weights, label="Custom allocation"):
    st.session_state["custom"] = validate_weights(np.array(weights)).tolist()
    st.session_state["custom_label"] = label
    st.session_state["_use_custom"] = True
    st.rerun()


def formatted_checks(checks):
    frame = checks.copy()
    frame["Observed"] = frame.value.map(pct)
    frame["Proposed range / limit"] = frame.apply(lambda row:
        (pct(row.minimum)+" to "+pct(row.maximum)) if pd.notna(row.minimum) and pd.notna(row.maximum)
        else "At least "+pct(row.minimum) if pd.notna(row.minimum) else "At most "+pct(row.maximum),axis=1)
    return frame.rename(columns={"check":"Check","status":"Status"})[["Check","Observed","Proposed range / limit","Status"]]


def decision_banner(result, decision):
    code = decision["status"]
    tone = "green" if code == "APPROVE" else "red" if code == "REJECT" else "amber"
    st.markdown(f'<div class="decision-banner {tone}"><span class="decision-code">{code}</span>'
                f'<div><strong>{escape(result["name"])}</strong><p>{decision["failed_checks"]} failed policy checks · Human approval pending</p></div></div>',unsafe_allow_html=True)
    st.caption("Historical model assessment, not a funding authorization.")


def policy_details(result, decision):
    with st.expander("Failed constraints and required corrective actions", expanded=decision["status"] != "APPROVE"):
        failed = result["checks"].query("status == 'FAIL'")
        if len(failed):
            table(formatted_checks(failed))
        else:
            st.success("All displayed numerical policy checks pass. Validation and independent human approval still apply.")
        for action in decision["actions"]:
            st.write("• " + action)
    with st.expander("All policy and asset-constraint checks"):
        table(formatted_checks(result["checks"]))


def allocations_for_comparison(alloc, result):
    values = {key:alloc[key].tolist() for key in alloc.columns}
    values[result["name"]] = result["weights"].tolist()
    for name, weights in st.session_state.get("portfolio_library", {}).items():
        values["Saved: " + name] = weights
    return values


def portfolio_library(weights):
    library = st.session_state.setdefault("portfolio_library", {})
    with st.expander("My saved allocations", expanded=False):
        st.caption("Saved names belong to this session. Export the JSON library to keep it after the session ends, then import it to restore. The fixed research reference is never overwritten.")
        label = st.text_input("Allocation name",max_chars=80,key="library_name")
        if st.button("Save selected allocation",key="library_save"):
            try:
                if label.strip() in library:
                    raise ValueError("That name already exists. Use a new name to keep both versions.")
                candidate = {**library,label.strip():list(weights)}
                library_json(candidate,research_version())
                st.session_state["portfolio_library"] = candidate
                st.success("Saved in this session. Export the library to preserve it.")
                library = candidate
            except ValueError as exc:
                st.error(str(exc))
        if library:
            saved = st.selectbox("Saved allocation",list(library),key="library_selected")
            if st.button("Load saved allocation",key="library_load"):
                apply_custom(library[saved], saved)
            st.download_button("Export my allocation library · JSON",library_json(library,research_version()),file_name="aegis_allocation_library.json",mime="application/json")
        upload = st.file_uploader("Import allocation library",type=["json"],key="library_upload")
        if st.button("Import uploaded library",key="library_import"):
            try:
                if upload is None:
                    raise ValueError("Choose an exported AEGIS JSON library first.")
                imported = parse_library(upload.getvalue())
                if set(imported) & set(library):
                    raise ValueError("Some names already exist. Rename those allocations in the imported file to preserve both versions.")
                combined = {**library,**imported}
                library_json(combined,research_version())
                st.session_state["portfolio_library"] = combined
                st.success("Library imported. Reload this section to select a saved allocation.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


def comparison_view(r, rf, alloc, result):
    rows = comparison(r,rf,allocations_for_comparison(alloc,result),result["lookback"],result["limits"])
    st.subheader("Compare allocations on the same evidence")
    mode = st.radio("Comparison measures",["Performance","Downside risk","All calculations"],horizontal=True,key="comparison_measures")
    if mode == "Performance":
        out = rows[["portfolio","CAGR","volatility","Sharpe"]].copy()
        out.CAGR = out.CAGR.map(pct)
        out.volatility = out.volatility.map(pct)
        out.Sharpe = out.Sharpe.map(lambda v:f"{v:.3f}" if pd.notna(v) else "N/A")
        table(out.rename(columns={"portfolio":"Portfolio","CAGR":"Test net CAGR","volatility":"Test volatility"}))
    elif mode == "Downside risk":
        out = rows[["portfolio","ES99","worst_scenario_loss","worst_replay_drawdown"]].copy()
        for column in out.columns[1:]:
            out[column] = out[column].map(pct)
        table(out.rename(columns={"portfolio":"Portfolio","ES99":"Daily ES99","worst_scenario_loss":"Scenario loss","worst_replay_drawdown":"Crisis drawdown"}))
    else:
        for selected in rows.portfolio:
            with st.expander(selected):
                row = rows[rows.portfolio == selected].iloc[0]
                percentages={"expected_return","CAGR","arithmetic_return","volatility","Jensen_alpha","max_drawdown","cumulative_return","annual_turnover","ES99","worst_scenario_loss","worst_replay_drawdown"}
                values=[]
                for col in rows.columns[2:]:
                    value=row[col]
                    values.append("Unavailable" if pd.isna(value) else pct(value) if col in percentages else f"USD {value:,.0f}" if col.endswith("_USD") else str(int(value)) if col=="failed_checks" else f"{value:.4f}")
                table(pd.DataFrame({"Metric":[col.replace("_"," ") for col in rows.columns[2:]],"Value":values}))
    st.caption("Training estimated returns are not forecasts. Net performance uses identical dates, costs and benchmark. Daily ES99 uses the same recent window; crisis comparisons use identical events. Benchmarks may fail the case's asset caps.")


def overview(result, risk, decision, a, method):
    decision_banner(result, decision)
    selected=risk[risk.model==method]
    selected_es=selected.iloc[0].ES if len(selected) else None
    columns = st.columns(4)
    for col,label,value,help_text in zip(columns,["Training estimated return","Held-out net CAGR","Worst crisis drawdown",f"{method} ES {a:.0%}"],
        [pct(result["expected_return"]),pct(result["kpi"]["CAGR"]),pct(result["stress"].query("n > 1").max_drawdown.max()),money_fraction(selected_es)],
        ["Shrunk annual arithmetic return estimated through2018; not a forecast.","Net compound return over the retrospective held-out period.","Largest drawdown across2008,2020 and2022 hindsight replays.","Expected one-day shortfall at your selected confidence and method. The separate mandate check always uses historical ES99."]):
        col.metric(label,value,help=help_text)
    st.caption(" · ".join(t+" "+pct(value) for t,value in zip(TICKERS,result["weights"]) if value>1e-10))
    policy_details(result,decision)
    with st.expander("All selected portfolio weights"):
        table(pd.DataFrame({"ETF":TICKERS,"Weight":[pct(v) for v in result["weights"]]}))
    row = risk[risk.model == method]
    if len(row):
        st.caption(f'Selected risk view: {method} at {a:.0%} · VaR {money_fraction(row.iloc[0].VaR)} · ES {money_fraction(row.iloc[0].ES)} · as of {result["latest_end"]}')
    else:
        st.info("The selected method is unavailable at this confidence/window. Open Risk comparison for the reason.")
    left,right = st.columns([1.4,1])
    test_path = result["path"].loc[TEST_START:]
    with left:
        chart(px.line(x=test_path.index,y=np.cumprod(1+test_path.net)*NAV,title="Held-out capital after modeled costs",labels={"x":"Date","y":"Portfolio value (USD)"}))
    with right:
        chart(px.bar(x=TICKERS,y=result["weights"],title="Selected allocation",labels={"x":"ETF","y":"Weight"}).update_yaxes(tickformat=".0%"))
    actions=st.columns(3)
    for col,label,target in zip(actions,["Build a portfolio →","Compare downside risk →","Replay a market crisis →"],["Portfolio Construction","Risk Analytics","Crisis Simulation Studio"]):
        col.button(label,on_click=open_workspace,args=(target,),use_container_width=True)


def market_view(s, prices, r, lookback):
    lede("Adjusted prices, a common observed trading calendar and retained data-quality flags. No live price feed is implied.")
    tick=st.multiselect("Price series",TICKERS,default=["SPY","AGG","GLD"])
    if tick:
        chart(px.line(prices[tick]/prices[tick].iloc[0],title="Adjusted prices · first observation = 1",labels={"value":"Growth multiple","index":"Date"}))
    chart(px.imshow(r.iloc[-lookback:].corr(),zmin=-1,zmax=1,color_continuous_scale="RdBu",text_auto=".2f",title="Selected-window return correlations"))
    c=st.columns(3)
    c[0].metric("Aligned price dates",f'{len(prices):,}')
    c[1].metric("Missing price cells",int(prices.isna().sum().sum()))
    c[2].metric("Retained flags",int(s["data"]["flags"]))
    with st.expander("Coverage and provenance"):
        table(read("coverage"))
        meta=json.loads((ROOT/"data/metadata/prices.json").read_text(encoding="utf-8-sig"))
        table(pd.DataFrame({"Field":["Source","Retrieved UTC","Dataset fingerprint","Common calendar","Risk-free rate"],"Value":[meta["source"],meta["retrieved_utc"],research_version(),s["data"]["common_calendar_note"],s["data"]["fred_note"]]}))
    with st.expander("ADF checks and retained anomaly flags"):
        table(read("adf"))
        table(read("data_flags"))
        st.caption("ADF tests training log returns for a unit root. Rejection does not prove independence, stable volatility or normality. Flags are retained rather than silently removed.")


def construction(r,rf,alloc,result):
    lede("Choose your weights. Compare the outcome. Keep the allocations you want to revisit.")
    for ticker,weight in zip(TICKERS,result["weights"]):
        st.session_state.setdefault("weight_"+ticker,float(weight*100))
    with st.form("allocation_form"):
        cols=st.columns(4)
        values=[cols[i%4].number_input(t+" weight (%)",0.0,100.0,value=None,step=0.5,key="weight_"+t) for i,t in enumerate(TICKERS)]
        apply=st.form_submit_button("Apply allocation to portfolio and risk views")
    if apply:
        try:
            if any(value is None for value in values):
                raise ValueError("Enter a weight for every ETF; use 0% for assets you do not want to hold")
            apply_custom(np.asarray(values, dtype=float)/100)
        except ValueError as exc:
            st.error(str(exc)+". Weights must total 100%; no partial allocation was applied.")
    st.button("Restore reference portfolio and settings",key="restore_reference",on_click=reset_reference_context,
              help="Restore the original allocation, 99% Historical risk, 756-day window and original proposed limits. Saved allocation names are kept.")
    st.caption(f'Selected: {result["name"]} · ID {result["allocation_id"]}. Custom choices are retrospective research experiments, not a new independent out-of-sample strategy.')
    metadata=provenance(result,research_version(),st.session_state.get("confidence",.99),st.session_state.get("method","Historical"))
    weights_csv=csv_bytes(pd.DataFrame({"ticker":TICKERS,"weight":result["weights"]}),metadata)
    st.download_button("Download selected allocation · CSV",weights_csv,file_name="aegis_allocation_"+result["allocation_id"]+"_"+metadata["generated_utc"][:10]+".csv",mime="text/csv")
    portfolio_library(result["weights"])
    comparison_view(r,rf,alloc,result)
    chart(px.line(read("frontier"),x="volatility",y="expected_return",markers=True,title="Fixed reference training frontier").update_xaxes(tickformat=".0%").update_yaxes(tickformat=".0%"))
    st.caption("The frontier is a locked training diagnostic; selected portfolio comparisons above recalculate. It is not silently relabelled as a custom frontier.")
    train=r.loc[:TRAIN_END]
    with st.expander("Selected portfolio CAPM and diversification"):
        k=result["kpi"]
        mu,cov=moments(train)
        weights=result["weights"]
        vals={"Selected test beta to SPY":k["beta"],"Selected test Jensen alpha":k["Jensen_alpha"],"Weight concentration HHI":float(weights@weights),"Effective holdings":1/float(weights@weights),"Training diversification ratio":float(weights@np.sqrt(np.diag(cov))/np.sqrt(weights@cov@weights))}
        table(pd.DataFrame({"Metric":vals.keys(),"Value":["N/A" if v is None else f"{v:.4f}" for v in vals.values()]}))
        table(capm(train,rf.loc[train.index]))
    test=result["path"].loc[TEST_START:]
    wealth=np.cumprod(1+test.net)
    draw=wealth/np.maximum.accumulate(np.r_[1,wealth])[1:]-1
    chart(px.line(x=test.index,y=draw,title="Selected held-out drawdown",labels={"x":"Date","y":"Drawdown"}).update_yaxes(tickformat=".0%"))


def risk_view(r,result,risk,a,method):
    lede("Compare one-day loss estimates on the same portfolio and historical window.")
    units=st.radio("Risk display units",["Percent of capital","USD"],horizontal=True,key="risk_units")
    fmt=pct if units=="Percent of capital" else money_fraction
    table(pd.DataFrame({"Model":risk.model,"VaR":[fmt(v) for v in risk.VaR],"Expected shortfall":[fmt(v) for v in risk.ES]}))
    st.caption(f'{result["name"]} · {a:.0%} confidence · {result["lookback"]} prior returns · {result["latest_start"]} to {result["latest_end"]}')
    chart(px.bar(risk.melt(id_vars="model",value_vars=["VaR","ES"]),x="model",y="value",color="variable",barmode="group",title=f"Matched {a:.0%} one-day risk",labels={"value":"Fraction of capital","model":"Model"}).update_yaxes(tickformat=".1%"))
    if not risk.model.eq("EVT").any():
        st.info("EVT unavailable at 90% because the requested quantile is at or below the 90% fitting threshold. Use 95% or 99%." if a<=0.90 else "EVT could not be fitted reliably for this window. Increase the lookback or inspect Tail-risk lab; no replacement estimate is invented.")
    with st.expander("Compare confidence levels · 90% / 95% / 99%"):
        st.caption("Higher confidence examines rarer losses. This changes VaR and ES, not historical returns or the mandate's fixed ES99 check. Confidence is not model accuracy.")
        rows=[]
        for alpha in [.90,.95,.99]:
            estimates=current_risk(r.iloc[-result["lookback"]:],tuple(result["weights"]),alpha)
            chosen=estimates[estimates.model==method]
            rows.append({"Confidence":f"{alpha:.0%}","VaR":float(chosen.iloc[0].VaR) if len(chosen) else np.nan,
                         "ES":float(chosen.iloc[0].ES) if len(chosen) else np.nan,
                         "Expected exceedance frequency":{.90:"About 1 in 10 trading days",.95:"About 1 in 20 trading days",.99:"About 1 in 100 trading days"}[alpha]})
        levels=pd.DataFrame(rows)
        display=levels.rename(columns={"ES":"Expected shortfall"}).copy()
        for column in ["VaR","Expected shortfall"]:
            display[column]=display[column].map(lambda value:fmt(value) if pd.notna(value) else "Unavailable")
        st.caption(method+" · "+result["name"]+" · same "+str(result["lookback"])+"-return window")
        table(display)
        st.caption("Exceedance frequencies are model expectations, not guarantees. EVT90 is unavailable at the default 90% fitting threshold. VaR is not a maximum loss.")
        metadata=provenance(result,research_version(),a,method)
        st.download_button("Download confidence comparison · CSV",csv_bytes(levels,metadata),
                           file_name="aegis_confidence_"+result["allocation_id"]+".csv",mime="text/csv",key="confidence_csv")
    with st.expander("How to interpret the models"):
        st.write("Historical simulation keeps observed shocks. Parametric and Monte Carlo use Gaussian log-return assumptions, so their agreement is not independent confirmation. EVT extrapolates tail exceedances and adds threshold and parameter uncertainty. Volatility state rescales historical shocks; it is not a trained predictor.")
    with st.expander("Selected portfolio Monte Carlo convergence"):
        sim=mc_losses(np.log1p(r.iloc[-result["lookback"]:]),result["weights"])
        rows=[dict(Draws=n,**empirical(sim[:n],a)) for n in [5000,10000,25000,N_SIM]]
        out=pd.DataFrame(rows)
        out.VaR=out.VaR.map(pct)
        out.ES=out.ES.map(pct)
        table(out)
        se=float(np.std([empirical(batch,a)["ES"] for batch in np.array_split(sim,10)],ddof=1)/np.sqrt(10))
        st.caption(f'Seed {SEED}; 5% diagonal covariance shrinkage; 50,000 correlated Gaussian log-return draws. Batch ES standard error: {pct(se)}. Reproducible simulation does not establish model adequacy.')


def tail_view(r,result,a):
    lede("Read the tail estimates and reliability warning first. Threshold sensitivity and conditional intervals expose uncertainty rather than establish a capital guarantee.")
    tq=st.slider("POT threshold quantile",0.85,0.95,0.90,0.005,key="threshold")
    loss=-(r.iloc[-result["lookback"]:].to_numpy()@result["weights"])
    try:
        model=fit(loss,tq)
    except ValueError as exc:
        st.warning(str(exc)+". Reduce the threshold or use more observations; no EVT estimate is available.")
        return
    flags=reliability(model,loss)
    st.warning(flags["status"]+": "+flags["message"])
    if not model["finite_ES"]:
        st.error("The fitted tail shape is at least1, so finite expected shortfall does not exist under this GPD. ES is unavailable.")
    if a>tq:
        est=estimate(model,a)
        cols=st.columns(2)
        cols[0].metric(f"EVT VaR {a:.0%}",pct(est["VaR"]))
        cols[1].metric(f"EVT ES {a:.0%}",pct(est["ES"]))
        st.caption(f'VaR {money_fraction(est["VaR"])} · ES {money_fraction(est["ES"])} · selected allocation {result["allocation_id"]}')
        if st.button("Estimate selected-confidence uncertainty · 100 block resamples",key="tail_ci"):
            try:
                with st.spinner("Refitting threshold and GPD in 100 circular block samples…"):
                    interval=tail_interval(tuple(loss),tq,a)
                st.session_state["tail_interval"]=(result["allocation_id"],result["lookback"],tq,a,interval)
            except ValueError as exc:
                st.warning(str(exc))
        saved=st.session_state.get("tail_interval")
        if saved is not None and saved[:4]==(result["allocation_id"],result["lookback"],tq,a):
            ci=saved[4]
            table(pd.DataFrame({"95% conditional interval":["VaR","Expected shortfall","GPD shape"],
                "Low":[pct(ci["VaR_CI"][0]),pct(ci["ES_CI"][0]),f'{ci["shape_CI"][0]:.3f}'],
                "High":[pct(ci["VaR_CI"][1]),pct(ci["ES_CI"][1]),f'{ci["shape_CI"][1]:.3f}']}))
            st.caption(f'{ci["valid"]}/{ci["repetitions"]} valid fits; 20-day circular blocks. These are conditional diagnostics, not guaranteed confidence coverage.')
    else:
        st.info("Requested confidence must exceed the tail threshold. No EVT extrapolation is reported here.")
    c=st.columns(4)
    for col,label,value in zip(c,["Threshold loss","Exceedances","GPD shape","GPD scale"],[pct(model["threshold"]),model["exceedances"],f'{model["shape"]:.3f}',pct(model["scale"])]):
        col.metric(label,value)
    with st.expander("Selected allocation threshold sensitivity",expanded=True):
        sens=sensitivity(loss)
        compact=sens[["threshold_q","status"]].copy()
        compact["Exceedances"]=sens.get("exceedances")
        compact["Shape"]=sens.get("shape").map(lambda x:f"{x:.3f}" if pd.notna(x) else "N/A")
        compact["ES99"]=sens.get("ES").map(pct)
        compact.threshold_q=compact.threshold_q.map(pct)
        table(compact.rename(columns={"threshold_q":"Threshold","status":"Fit status"}))
        st.caption("Sensitivity always includes ES99 for the selected allocation; it is labelled independently of the sidebar confidence. The frozen reference uses a90% threshold; changing this interactive diagnostic does not tune the locked backtest.")
    with st.expander("Advanced tail diagnostics"):
        exc=np.sort(loss[loss>model["threshold"]]-model["threshold"])
        theory=genpareto.ppf((np.arange(len(exc))+.5)/len(exc),model["shape"],scale=model["scale"])
        fig=px.scatter(x=theory,y=exc,title="GPD tail Q-Q diagnostic",labels={"x":"Theoretical excess return","y":"Observed excess return"})
        fig.add_scatter(x=[0,max(theory)],y=[0,max(theory)],mode="lines",name="Equality")
        chart(fig.update_xaxes(tickformat=".1%").update_yaxes(tickformat=".1%"))
        st.caption(f'Adjacent exceedance pairs: {flags["adjacent_exceedance_pairs"]}. Serial clustering reduces independent information. At least40 exceedances are required; the80-observation caution threshold is an application heuristic.')


def validation_view(r,alloc,result,a,method):
    lede("Each forecast uses only earlier returns. Full-sample calibration and the latest250 traffic-light window are separate measurements.")
    source=st.radio("Validation portfolio",["Selected allocation","Fixed research reference"],horizontal=True,key="validation_source")
    if source=="Fixed research reference":
        raw=read("forecasts")
        raw.date=pd.to_datetime(raw.date)
        raw=raw[raw.date>=pd.Timestamp(TEST_START)]
        label="Fixed AEGIS reference · 756 prior returns"
        st.info("Reference evidence is fixed. It is not evidence for the selected custom portfolio or a changed lookback.")
    else:
        raw,label=available_forecasts(result,alloc)
        if raw is None:
            st.warning("No rolling validation is cached for this allocation and lookback. Run it before relying on an automated approval; reference statistics are not substituted.")
            if st.button("Run selected portfolio backtest",key="run_selected_backtest"):
                with st.status("Computing chronological one-step forecasts…",expanded=True) as status:
                    st.write("Fixed selected weights; each date uses only its preceding window. All three confidence levels and five supported methods are calculated. Monte Carlo uses10,000 draws per window.")
                    raw=rolling_selected(r,tuple(result["weights"]),result["lookback"])
                    cache=st.session_state.setdefault("selected_backtests",{})
                    cache[validation_key(result)]=raw
                    status.update(label="Selected-allocation forecasts complete",state="complete")
                st.rerun()
            return
    st.caption(label+" · retrospective test; not an independently preregistered live strategy")
    dates=st.session_state.get("dates",(pd.Timestamp(result["test_start"]).date(),pd.Timestamp(result["test_end"]).date()))
    if not isinstance(dates,(tuple,list)) or len(dates)!=2:
        st.info("Select both a start and end date in Analysis settings.")
        return
    filtered=raw[(pd.to_datetime(raw.date)>=pd.Timestamp(dates[0]))&(pd.to_datetime(raw.date)<=pd.Timestamp(dates[1]))&np.isclose(raw.confidence,a)].copy()
    if filtered.date.nunique()<2:
        st.warning("At least two forecast dates are required. Expand the date range.")
        return
    validation=summarize(filtered)
    picked=validation[validation.model==method]
    if picked.empty:
        st.info("This method is unavailable at the selected confidence. EVT requires confidence above its tail threshold.")
    else:
        row=picked.iloc[0]
        color=row.traffic_last250.lower() if row.traffic_last250 in {"Green","Amber","Red"} else "neutral"
        st.markdown(f'<div class="traffic-line {color}"><span class="traffic-light"></span><strong>{escape(method)} · {escape(str(row.traffic_last250))}</strong></div>',unsafe_allow_html=True)
        cols=st.columns(4)
        cols[0].metric("Full-window exceptions",f'{int(row.exceptions)} / {int(row.n)}')
        cols[1].metric("Full-window expected",f'{row.expected:.2f}')
        cols[2].metric("Latest-window exceptions",f'{int(row.last250_exceptions)} / {int(row.last250_n)}')
        cols[3].metric("Latest-window expected",f'{row.last250_expected:.2f}')
        st.caption(f'Full window {row.full_start} to {row.full_end}; latest window starts {row.last250_start}. Basel-style lights require exactly250 one-day99% forecasts and are not regulatory approval.')
    display=st.radio("Validation detail",["Coverage tests","Exception windows","All numerical diagnostics"],horizontal=True,key="validation_detail")
    if display=="Coverage tests":
        columns=["model","kupiec_p","independence_p","conditional_p"]
        out=validation[columns].copy()
        for col in columns[1:]:
            out[col]=out[col].map(lambda v:"UNAVAILABLE" if pd.isna(v) else f'{v:.3f} · '+("REVIEW" if v<.05 else "No rejection"))
        table(out.rename(columns={"model":"Model","kupiec_p":"Kupiec p","independence_p":"Christoffersen p","conditional_p":"Joint coverage p"}))
    elif display=="Exception windows":
        table(validation[["model","n","exceptions","expected","last250_n","last250_exceptions","last250_expected","traffic_last250"]])
    else:
        selected=st.selectbox("Diagnostic model",list(validation.model),key="diagnostic_model")
        row=validation[validation.model==selected].iloc[0]
        table(pd.DataFrame({"Diagnostic":row.index,"Value":[str(v) for v in row.values]}))
    series=filtered[filtered.model==method]
    if len(series):
        fig=go.Figure()
        fig.add_scatter(x=series.date,y=series.loss*NAV,mode="lines",name="Realized gross loss")
        fig.add_scatter(x=series.date,y=series.VaR*NAV,mode="lines",name="Prior-window VaR")
        hit=series.loss>series.VaR
        fig.add_scatter(x=series.loc[hit,"date"],y=series.loc[hit,"loss"]*NAV,mode="markers",name="Exceptions")
        chart(fig.update_layout(title="One-day loss versus prior forecast",yaxis_title="USD on10 million reference",xaxis_title="Forecast date"))
    with st.expander("Volatility-state innovation and paired uncertainty"):
        if a!=.99:
            st.caption("The paired model comparison below is explicitly at99% using the full test window, independent of the displayed date filter.")
        try:
            interval=paired_score_ci(raw)
            table(pd.DataFrame({"Measure":["Mean FZ0 difference","95% interval low","95% interval high"],"Value":[interval["mean_difference"],*interval["CI"]]}))
            st.write("Negative favours volatility state. An interval crossing zero does not establish improvement; a positive interval favours the historical baseline.")
        except (ValueError,KeyError):
            st.info("The paired99% comparison is unavailable for this forecast set.")


def stress_view(r,rf,alloc,result):
    lede("Historical paths use observed ETF returns. The selected weights are replayed retrospectively; the hypothetical event is an assumption with no assigned probability.")
    view=st.radio("Scenario tool",["Historical and design scenarios","What-if assumptions"],horizontal=True,key="scenario_tool")
    if view=="What-if assumptions":
        c=st.columns(2)
        eq=c[0].slider("Equity return shock (%)",-50.0,50.0,-20.0,1.0,key="whatif_equity")/100
        gold=c[1].slider("Gold return shock (%)",-50.0,50.0,-5.0,1.0,key="whatif_gold")/100
        rate=c[0].slider("Interest-rate shift (basis points)",-500,500,100,25,key="whatif_rate")
        duration=c[1].slider("Assumed AGG modified duration (years)",0.0,15.0,6.0,0.5,key="whatif_duration")
        shocks=what_if(result["weights"],eq,rate,duration,gold)
        pnl=float(shocks.contribution.sum())
        c=st.columns(2)
        c[0].metric("Assumed portfolio event return",pct(pnl))
        c[1].metric("Capital impact on USD10m",money_fraction(pnl))
        table(pd.DataFrame({"ETF":shocks.ticker,"Assumed return":shocks.assumed_return.map(pct),"Contribution (USD)":shocks.contribution.map(money_fraction)}))
        chart(px.bar(shocks,x="ticker",y="contribution_USD",title="Assumed event P&L contribution",labels={"contribution_USD":"USD","ticker":"ETF"}))
        st.caption("Assumptions only: equity ETFs share the equity shock; AGG return ≈ -duration × yield change; gold uses its own shock. Convexity, spreads, coupons, timing and recovery are omitted. No probability or forecast is claimed.")
        multiplier=st.slider("Volatility multiplier",0.5,2.5,1.0,0.1,key="whatif_vol")
        recent=r.iloc[-result["lookback"]:]
        scaled=recent.mean()+(recent-recent.mean())*multiplier
        if (scaled<=-1).any().any():
            st.warning("Scaled simple returns reached -100%; this model configuration is unavailable. Reduce the multiplier.")
        else:
            out=current_risk(scaled,tuple(result["weights"]),st.session_state.get("confidence",.99))
            table(pd.DataFrame({"Model":out.model,"Scaled VaR":out.VaR.map(pct),"Scaled ES":out.ES.map(pct)}))
            st.caption("This sensitivity scales observed deviations around the sample mean. It is a separate assumed distribution, not a new historical dataset or validated forecast.")
        return
    choices=allocations_for_comparison(alloc,result)
    comparisons=st.multiselect("Compare allocations",list(choices),default=list(dict.fromkeys([result["name"],"60/40 benchmark"])),key="stress_comparisons")
    # Always retain the selected allocation in its own capital-impact panel.
    full={**{name:np.array(choices[name]) for name in comparisons},result["name"]:result["weights"]}
    from .stress import historical
    stress,paths=historical(r,full)
    scenario=st.selectbox("Stress scenario",list(result["stress"].scenario),key="stress_scenario")
    sel=stress[stress.scenario==scenario]
    selected=sel[sel.portfolio==result["name"]].iloc[0]
    cols=st.columns(3)
    cols[0].metric("Selected terminal return",pct(selected.return_pct))
    cols[1].metric("Capital impact (USD10m)",money_fraction(selected.return_pct))
    cols[2].metric("Maximum drawdown",pct(selected.max_drawdown))
    st.caption("Historical observed-return hindsight replay, gross of costs." if selected.n>1 else "Assumed simultaneous shock; no event probability or recovery path.")
    table(pd.DataFrame({"Portfolio":sel.portfolio,"Event return":sel.return_pct.map(pct),"Capital impact":sel.return_pct.map(money_fraction),"Drawdown":sel.max_drawdown.map(pct)}))
    data=paths[paths.scenario==scenario]
    if len(data):
        replay=st.slider("Replay trading day",1,int(data.groupby("portfolio").size().max()),int(data.groupby("portfolio").size().max()),key="replay_day_"+scenario)
        chart(px.line(data.groupby("portfolio",group_keys=False).head(replay),x="date",y="wealth",color="portfolio",title="Observed crisis paths · selected weights",labels={"wealth":"Growth of one dollar","date":"Date"}))
        st.caption(f'Observed interval {selected.start} to {selected.end}. Recovery: {selected.recovery_date}. Recovery uses the same hindsight allocation through the remaining sample.')
    else:
        from .config import HYPOTHETICAL
        table(pd.DataFrame({"ETF":TICKERS,"Assumed shock":[pct(HYPOTHETICAL[t]) for t in TICKERS]}))
    attribution=pd.DataFrame({"ETF":TICKERS,"Contribution":[selected[t] for t in TICKERS]})
    attribution["P&L (USD)"]=attribution.Contribution.map(money_fraction)
    attribution.Contribution=attribution.Contribution.map(pct)
    table(attribution)
    st.caption("Asset contributions sum to terminal return. Historical contributions include changing portfolio NAV. Drawdown is a peak-relative ratio, distinct from terminal loss; dollar drawdown equivalents use fixed reference capital.")


def policy_editor():
    st.subheader("Proposed mandate and risk limits")
    st.caption("These controls change the research assessment. They do not record client approval or retrospectively alter the locked reference package.")
    saved=st.session_state.get("_policy_settings",{})
    for key,(_,default,_) in POLICY_CONTROLS.items():
        st.session_state.setdefault(key,saved.get(key,default))
    c=st.columns(2)
    fields=[(0,"Annual volatility limit (%)",1.0,50.0,0.5,"limit_vol"),
            (1,"Maximum drawdown limit (%)",1.0,60.0,0.5,"limit_dd"),
            (0,"Daily historical ES99 limit (%)",0.1,20.0,0.1,"limit_es"),
            (1,"Scenario terminal-loss limit (%)",1.0,60.0,0.5,"limit_scenario"),
            (0,"Training estimated return target (%)",0.0,30.0,0.5,"limit_return")]
    for column,label,lo,hi,step,key in fields:
        c[column].number_input(label,lo,hi,value=None,step=step,key=key,on_change=remember_policy_control,args=(key,))
    c[0].slider("Proposed AGG floor",0.35,0.70,value=None,step=0.05,key="limit_bond",on_change=remember_policy_control,args=("limit_bond",))
    c[1].slider("Proposed aggregate equity cap",0.20,0.50,value=None,step=0.05,key="limit_equity",on_change=remember_policy_control,args=("limit_equity",))
    st.button("Restore original risk limits",key="restore_limits",on_click=reset_policy_controls)
    st.caption("Edited limits stay active across workspaces and exports until restored. They are research assumptions, not client approval.")


def budgets(r,rf,alloc,result,decision,a):
    decision_banner(result,decision)
    policy_editor()
    priority=st.selectbox("Investment priority",["Capital preservation","Balanced growth","Improved returns"],key="investment_priority")
    st.caption("All priorities use the same hard limits. Optimization uses data through2018 only, with training drawdown/ES/volatility, a training return target and the assumed funding shock. Later crises are assessed after selection. Solver failure never relaxes a limit silently.")
    if st.button("Re-optimise using training data only",key="optimize_selected"):
        try:
            with st.spinner("Solving the proposed training constraints…"):
                weights=run_optimizer(r.loc[:TRAIN_END],result["limits"],priority)
            apply_custom(weights,priority+" candidate")
        except ValueError as exc:
            st.error(str(exc))
    if st.button("Compare investment priorities",key="compare_priorities"):
        rows=[]
        weights_by_priority={}
        with st.spinner("Solving and assessing all three priorities…"):
            for mode in ["Capital preservation","Balanced growth","Improved returns"]:
                try:
                    weights=run_optimizer(r.loc[:TRAIN_END],result["limits"],mode)
                    evaluated=analyze(r,rf,weights,mode,result["lookback"],Limits(**result["limits"]))
                    rec=recommendation(evaluated)
                    rows.append(dict(Priority=mode,Status=rec["status"],Estimated_return=pct(evaluated["expected_return"]),Worst_crisis_drawdown=pct(evaluated["stress"].query("n > 1").max_drawdown.max()),Failed_checks=rec["failed_checks"]))
                    weights_by_priority[mode]=weights.tolist()
                except ValueError:
                    rows.append(dict(Priority=mode,Status="NO FEASIBLE SOLUTION FOUND"))
        st.session_state["priority_comparison"]=(json.dumps(result["limits"],sort_keys=True),rows,weights_by_priority)
    saved=st.session_state.get("priority_comparison")
    if saved and saved[0]==json.dumps(result["limits"],sort_keys=True):
        table(pd.DataFrame(saved[1]))
        if saved[2]:
            chosen=st.selectbox("Priority candidate to inspect",list(saved[2]),key="priority_candidate")
            if st.button("Use priority candidate",key="use_priority"):
                apply_custom(saved[2][chosen],chosen+" candidate")
        st.caption("A training-feasible allocation can still fail a later crisis or validation. Those failures are retained; no historical test outcome selected the weights.")
    policy_details(result,decision)
    st.subheader("Selected allocation risk attribution")
    rc=contributions(r.iloc[-result["lookback"]:],result["weights"],a)
    table(pd.DataFrame({"ETF":rc.ticker,"Weight":rc.weight.map(pct),"ES contribution":rc.component_ES.map(money_fraction),"Normal VaR contribution":rc.component_normal_VaR.map(money_fraction)}))
    chart(px.bar(rc,x="ticker",y="component_ES",title=f"Historical ES contribution · {a:.0%}",labels={"component_ES":"Fraction of capital","ticker":"ETF"}).update_yaxes(tickformat=".1%"))
    with st.expander("Marginal contributions and allocation sensitivity"):
        table(rc)
        st.write("Component ES sums to empirical ES. Normal simple-return VaR attribution is a separate Gaussian approximation. For a small fully invested shift from asset j to i, approximate ES change is (marginal ES_i - marginal ES_j) × shifted weight.")
        source=st.selectbox("Transfer from",TICKERS,key="attribution_from")
        target=st.selectbox("Transfer to",TICKERS,index=4,key="attribution_to")
        shift=st.slider("Weight transfer (%)",0.0,10.0,1.0,0.5,key="attribution_shift")/100
        changed=result["weights"].copy()
        if source==target:
            st.info("Choose different source and destination assets.")
        elif shift>changed[TICKERS.index(source)]:
            st.info("The transfer exceeds the selected source holding. Reduce the shift.")
        else:
            changed[TICKERS.index(source)]-=shift
            changed[TICKERS.index(target)]+=shift
            recent=r.iloc[-result["lookback"]:]
            before=empirical(-(recent.to_numpy()@result["weights"]),a)["ES"]
            after=empirical(-(recent.to_numpy()@changed),a)["ES"]
            st.metric("Recomputed daily ES after hypothetical transfer",money_fraction(after),delta=money_fraction(after-before),delta_color="inverse")
            st.caption("This diagnostic does not apply the transfer or establish policy compliance. Use Build a portfolio to apply and check all limits.")
    budget=st.number_input("Daily ES risk budget (USD)",1000.0,float(NAV),250000.0,10000.0,key="sizing_budget")
    es=empirical(-(r.iloc[-result["lookback"]:].to_numpy()@result["weights"]),a)["ES"]
    st.metric("Indicative proportional exposure cap",pct(min(1,budget/(es*NAV))) if es>0 else "Unavailable")
    st.caption("Diagnostic sizing only. Cash is outside the permitted universe; any implementable reduction needs eligible-asset reallocation or a revised mandate.")
    with st.expander("Proposed risk-limit sensitivity"):
        subset=result["checks"][(result["checks"].category=="Risk / objective") & result["checks"].maximum.notna()]
        table(pd.DataFrame([{"Limit multiplier":f"{mult:.0%}","Within limits":int((subset.value<=subset.maximum*mult+1e-8).sum()),"Risk checks":len(subset)} for mult in [.8,1,1.2]]))
        st.caption("This diagnostic scales maximum risk limits by ±20%. It does not alter the proposed limits or imply client approval, and uses no arbitrary composite score.")
    portfolio_library(result["weights"])
    with st.expander("Optional team database saving"):
        saved_allocations_panel(result["weights"])


def guide(result,decision,validation):
    lede("A deterministic research guide linked to the selected allocation and actual calculations. It does not call a live generative AI model.")
    question=st.selectbox("Research question",["What is the proposed portfolio?","What does the backtest say?","Why do risk models disagree?","Can we claim capital is protected?","What requires human approval?"],key="guide_question")
    if question=="What is the proposed portfolio?":
        st.write(f'Selected: {result["name"]}. Automated recommendation: {decision["status"]}; {decision["failed_checks"]} policy checks fail. Human approval is pending.')
        table(pd.DataFrame({"ETF":TICKERS,"Weight":[pct(v) for v in result["weights"]]}))
        target="Portfolio Construction"
    elif question=="What does the backtest say?":
        if validation is None:
            st.info("This allocation/window has not been backtested. Run selected-allocation validation; reference results are not substituted.")
        else:
            row=validation[(validation.model=="Historical")&np.isclose(validation.confidence,.99)].iloc[0]
            st.write(f'Historical99% VaR had {int(row.exceptions)} exceptions in {int(row.n)} forecasts. The latest{int(row.last250_n)} window had {int(row.last250_exceptions)} exceptions: {row.traffic_last250}. Non-rejection does not prove a model is correct.')
        target="Backtesting & Validation"
    elif question=="Why do risk models disagree?":
        st.write("Historical simulation samples observed shocks. Parametric and Monte Carlo use Gaussian assumptions with different aggregation. EVT extrapolates tail exceedances and is sensitive to threshold and sample size. Compare them at the same confidence and horizon.")
        target="Risk Analytics"
    elif question=="Can we claim capital is protected?":
        worst=float(result["stress"].query("n > 1").max_drawdown.max())
        st.write(f'No. The selected allocation experienced a worst historical crisis replay drawdown of {pct(worst)}. VaR is not maximum loss, and hypothetical scenarios do not bound future losses.')
        target="Crisis Simulation Studio"
    else:
        st.write("Independent reviewers must check the code, allocation, risk limits, spending assumptions, crisis interpretation and final investment decision. Automated tests and this recommendation do not record human approval.")
        target="Investment Committee Reports"
    st.button("Open supporting calculations",on_click=open_workspace,args=(target,),key="guide_evidence")
    with st.expander("Full evidence ledger"):
        table(read("evidence_ledger"))


def reports(result,risk,decision,validation,a,method):
    lede("Take the decision, calculations and assumptions with you.")
    source_label=st.session_state.get("custom_label",result["name"]) if result["name"]=="Custom allocation" else result["name"]
    key=hashlib.sha256((research_version()+result["allocation_id"]+source_label+json.dumps(result["limits"],sort_keys=True)+str(result["lookback"])+str(a)+method+str(validation is not None)).encode()).hexdigest()
    st.subheader("Selected portfolio")
    st.caption("Create PDFs and data for the allocation and settings shown above. Human investment approval remains pending.")
    if st.button("Prepare selected portfolio reports",key="prepare_reports",type="primary"):
        with st.spinner("Preparing reports and calculations…"):
            meta=provenance(result,research_version(),a,method)
            meta["portfolio_label"]=source_label
            st.session_state["report_export"]=(key,export_package(result,risk,decision,meta,validation))
    prepared=st.session_state.get("report_export")
    if prepared is not None and prepared[0]==key:
        prefix,archive,entries=prepared[1]
        st.download_button("Download selected analysis package · ZIP",archive,file_name=prefix+".zip",mime="application/zip",type="primary")
        columns=st.columns(2)
        for col,kind,label in [(columns[0],"technical","Selected technical report"),(columns[1],"tear_sheet","Selected executive tear sheet")]:
            col.download_button(label+" · PDF",entries[kind+".pdf"],file_name=prefix+"_"+kind+".pdf",mime="application/pdf",key="selected_pdf_"+kind)
        with st.expander("Committee memorandum and calculation files"):
            st.download_button("Selected investment memorandum · PDF",entries["memo.pdf"],file_name=prefix+"_memo.pdf",mime="application/pdf",key="selected_pdf_memo")
            st.caption("The ZIP includes weights, risk, stress, policy checks, performance, available validation, analysis metadata and SHA256 checksums.")
    else:
        st.caption("Generate again after changing the allocation or settings. Earlier exports are not presented as current.")
    with st.expander("Download individual calculations · CSV"):
        meta=provenance(result,research_version(),a,method)
        slug=result["allocation_id"]+"_"+meta["generated_utc"][:10]
        for frame,label in [(risk,"risk"),(result["stress"],"stress"),(result["checks"],"policy_checks"),(pd.DataFrame([result["kpi"]]),"performance")]:
            st.download_button("Selected "+label.replace("_"," ")+" · CSV",csv_bytes(frame,meta),file_name="aegis_"+slug+"_"+label+".csv",mime="text/csv",key="selected_csv_"+label)
    st.divider()
    st.subheader("Reference study")
    st.caption("The original portfolio, original proposed limits and frozen dataset. These documents remain separate from your selected analysis.")
    current_files={"Current_Technical_Report.pdf":"Technical study · 15 pages", "Current_Investment_Tear_Sheet.pdf":"Investment tear sheet · 1 page", "AI_Usage_Details.pdf":"AI usage disclosure · 2 pages"}
    for file,label in current_files.items():
        document=ROOT/"reports"/file
        if document.is_file():
            st.download_button(label+" · PDF",document.read_bytes(),file_name=file,mime="application/pdf",key="release_"+file)
    st.link_button("View documented source on GitHub","https://github.com/CodeJediX/aegis-quantedge")
    with st.expander("Android companion and original presentation files"):
        apk=ROOT/"mobile/releases/QuantumX_AEGIS_1.0.0.apk"
        if apk.is_file():
            st.download_button("Native Android app · APK",apk.read_bytes(),file_name=apk.name,mime="application/vnd.android.package-archive",key="release_apk")
            st.caption("26 October native release. Offline Android8+ interface with historical/Gaussian risk and bundled26October documents. Advanced web models and later website changes remain on this website.")
        originals=[("reports/Technical_Report.docx","Original study · editable Word"),("reports/Investment_Committee_Memo.pdf","Original committee memo"),("presentation/Final_Pitch.pptx","Presentation · editable PowerPoint"),("presentation/Final_Pitch.pdf","Presentation · PDF")]
        for relative,label in originals:
            document=ROOT/relative
            if document.is_file():
                st.download_button(label,document.read_bytes(),file_name=document.name,key="fixed_download_"+document.name)
    with st.expander("Independent human review record"):
        st.markdown((ROOT/"documentation/Team_Approval_Checklist.md").read_text(encoding="utf-8-sig"))


def assumptions():
    st.info("Historical research is not a capital guarantee. The proposed mandate, spending needs and final decision require independent human review.")
    st.write("The reference case uses USD10 million, seven permitted ETFs, long-only fully invested weights and a10+ year horizon. Risk estimates are one-day; crisis replays are retrospective. Fees, liquidity, taxes and spending are only partly or not modeled.")
    text=(ROOT/"documentation/Assumptions_and_Limitations.md").read_text(encoding="utf-8-sig")
    sections=re.split(r"(?m)^## ",text)
    for section in sections[1:]:
        title,_,body=section.partition("\n")
        with st.expander(title.strip()):
            st.markdown(body)
    if len(sections)==1:
        with st.expander("Full assumptions and limitations"):
            st.markdown(text)
    with st.expander("Evidence ledger and model caveats"):
        table(read("evidence_ledger"))


def methods(result,a,method):
    lede("Understand the inputs, methods and responsibilities behind every result.")
    meta=provenance(result,research_version(),a,method)
    table(pd.DataFrame({"Parameter":["Dataset version","Data through","Training end","Test interval","Selected allocation ID","Lookback","Random seed","Snapshot MC draws","Rolling MC draws"],"Value":[meta["dataset_version"],meta["data_through"],TRAIN_END,meta["test_start"]+" to "+meta["test_end"],meta["allocation_id"],str(result["lookback"]),str(SEED),str(N_SIM),"10000"]}))
    for file in ["Methodology.md","Data_Governance.md","AI_Disclosure.md","Sources.md"]:
        with st.expander(file.replace("_"," ").replace(".md",""),expanded=False):
            st.markdown((ROOT/"documentation"/file).read_text(encoding="utf-8-sig"))
    with st.expander("Installed dependency versions and processing steps"):
        table(pd.DataFrame({"Dependency":meta["versions"].keys(),"Version":meta["versions"].values()}))
        st.write("Hash checks → complete adjusted-price validation → chronological simple/log returns → strictly lagged risk-free proxy → training-only optimization → fixed-weight walk-forward forecasts → explicit policy assessment. No synthetic provider fallback.")
    st.code("pip install -r requirements.txt\nstreamlit run hosted_app.py\npython -m unittest discover -s tests\npython scripts/check_app.py hosted_app.py\npython run.py --reproduce",language="bash")


def render(page,s,prices,r,rf,alloc,w,name,a,method,lookback,dates):
    limits=limits_from_state()
    result=selected_analysis(r,rf,tuple(w),name,lookback,asdict(limits))
    risk=current_risk(r.iloc[-lookback:],tuple(w),a)
    forecasts_,validation_label=available_forecasts(result,alloc)
    validation=summarize(forecasts_) if forecasts_ is not None else None
    decision=recommendation(result,validation)
    st.markdown('<div class="analysis-strip"><span>'+escape(name)+'</span><span>USD 10m</span><span>'+f'{a:.0%} · '+escape(method)+'</span><span>'+str(lookback)+' prior returns</span></div>',unsafe_allow_html=True)
    if name=="Custom allocation":
        st.caption("Custom: "+st.session_state.get("custom_label","User weights")+" · retrospective research")
    if result["limits"]!=asdict(Limits()):
        st.warning("Edited research limits are active across workspaces and exports. No client approval is recorded. Restore the original limits in Risk budgets.")
    if page=="Executive Command Center":
        overview(result,risk,decision,a,method)
    elif page=="Market Intelligence":
        market_view(s,prices,r,lookback)
    elif page=="Portfolio Construction":
        construction(r,rf,alloc,result)
    elif page=="Risk Analytics":
        risk_view(r,result,risk,a,method)
    elif page=="EVT & Tail-Risk Laboratory":
        tail_view(r,result,a)
    elif page=="Backtesting & Validation":
        validation_view(r,alloc,result,a,method)
    elif page=="Crisis Simulation Studio":
        stress_view(r,rf,alloc,result)
    elif page=="Portfolio Decision Lab":
        budgets(r,rf,alloc,result,decision,a)
    elif page=="AI Research Assistant":
        guide(result,decision,validation)
    elif page=="Investment Committee Reports":
        reports(result,risk,decision,validation,a,method)
    elif page=="Assumptions & Limitations":
        assumptions()
    elif page=="Methodology, Sources & AI Disclosure":
        methods(result,a,method)
    with st.expander("Analysis details"):
        st.caption(f'Allocation ID {result["allocation_id"]} · dataset {research_version()} · data through {result["latest_end"]}')
        st.caption(f'Test: {result["test_start"]} to {result["test_end"]}. Risk window: {result["latest_start"]} to {result["latest_end"]}. One-day risk horizon.')
        st.caption("Confidence changes VaR, ES and validation; historical performance and the fixed policy ES99 check stay unchanged.")
    from .chat_guide import chat_widget
    chat_widget(result,decision,validation is not None)
