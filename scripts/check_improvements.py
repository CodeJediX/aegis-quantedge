"""End-to-end checks for selected-portfolio consistency and the improvement request.

Runs against real snapshots, including one selected-allocation rolling backtest.
"""

from io import BytesIO
import json
import sys
from pathlib import Path
import re
import numpy as np
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.config import TICKERS


def main():
    results=[]
    app=AppTest.from_file(str(ROOT/"hosted_app.py"),default_timeout=240).run()

    def check(label):
        errors=[error.message for error in app.exception]
        results.append(dict(check=label,passed=not errors,exceptions=errors))
        assert not errors,(label,errors)

    def page(name):
        app.selectbox(key="page").set_value(name).run()
        check("route "+name)

    check("startup")
    assert any("REVISE" in item.value for item in app.markdown)
    page("Risk Analytics")
    portfolios=app.selectbox(key="portfolio").options
    for portfolio in portfolios:
        app.selectbox(key="portfolio").set_value(portfolio).run()
        for confidence in [.90,.95,.99]:
            for method in ["Historical","Parametric","Monte Carlo","EVT","Volatility state"]:
                app.selectbox(key="confidence").set_value(confidence)
                app.selectbox(key="method").set_value(method).run()
                check(f"risk matrix {portfolio} / {confidence} / {method}")
    app.radio(key="risk_units").set_value("USD").run()
    check("USD display")
    page("Portfolio Construction")
    app.selectbox(key="portfolio").set_value("60/40 benchmark").run()
    assert app.number_input(key="weight_SPY").value==60.0
    app.selectbox(key="portfolio").set_value("AEGIS minimum variance").run()
    assert abs(app.number_input(key="weight_SPY").value-11.73300527)<1e-6
    check("allocation editor follows selected weights")
    for ticker,value in zip(TICKERS,[20,0,0,60,20,0,0]):
        app.number_input(key="weight_"+ticker).set_value(float(value))
    app.button(key="FormSubmitter:allocation_form-Apply allocation to portfolio and risk views").click().run()
    assert app.selectbox(key="portfolio").value=="Custom allocation"
    check("custom allocation applies")
    app.text_input(key="library_name").set_value("Verification allocation")
    app.button(key="library_save").click().run()
    assert "Verification allocation" in app.session_state["portfolio_library"]
    app.selectbox(key="portfolio").set_value("60/40 benchmark").run()
    app.button(key="library_load").click().run()
    assert app.selectbox(key="portfolio").value=="Custom allocation"
    np.testing.assert_allclose(app.session_state["custom"],[.2,0,0,.6,.2,0,0])
    check("named session allocation reload")
    for measures in ["Performance","Downside risk","All calculations"]:
        app.radio(key="comparison_measures").set_value(measures).run()
        check("portfolio comparison "+measures)

    page("Crisis Simulation Studio")
    for scenario in ["2008 GFC","2020 COVID","2022 rates","Hypothetical funding squeeze"]:
        app.selectbox(key="stress_scenario").set_value(scenario).run()
        check("stress "+scenario)
        assert any("USD" in metric.label for metric in app.metric)
    app.radio(key="scenario_tool").set_value("What-if assumptions").run()
    for bps in [-100,200]:
        app.slider(key="whatif_rate").set_value(bps).run()
        app.slider(key="whatif_vol").set_value(1.5).run()
        check("what-if rate/volatility "+str(bps))

    page("EVT & Tail-Risk Laboratory")
    app.selectbox(key="confidence").set_value(.95).run()
    app.slider(key="threshold").set_value(.85).run()
    app.button(key="tail_ci").click().run()
    assert app.session_state["tail_interval"][3]==.95
    check("selected-confidence EVT uncertainty")
    app.slider(key="threshold").set_value(.95).run()
    app.selectbox(key="lookback").set_value(252).run()
    check("insufficient EVT exceedances handled")
    assert len(app.warning)>0
    app.selectbox(key="lookback").set_value(756).run()
    app.selectbox(key="confidence").set_value(.99).run()

    page("Backtesting & Validation")
    try:
        cached=app.session_state["selected_backtests"]
    except KeyError:
        cached={}
    assert not cached
    assert any("not substituted" in warning.value for warning in app.warning)
    app.button(key="run_selected_backtest").click().run(timeout=240)
    check("full selected-allocation chronological backtest")
    stored=list(app.session_state["selected_backtests"].values())[0]
    assert (stored.estimate_end<stored.date).all()
    assert (stored.estimate_start<stored.estimate_end).all()
    for detail in ["Coverage tests","Exception windows","All numerical diagnostics"]:
        app.radio(key="validation_detail").set_value(detail).run()
        check("validation detail "+detail)
    app.radio(key="validation_source").set_value("Fixed research reference").run()
    check("explicit fixed reference source")

    page("Portfolio Decision Lab")
    app.number_input(key="limit_dd").set_value(20.0).run()
    app.number_input(key="limit_scenario").set_value(20.0).run()
    app.button(key="compare_priorities").click().run()
    check("training-only objective comparison")
    rows=app.session_state["priority_comparison"][1]
    assert len(rows)==3
    assert len(app.session_state["priority_comparison"][2])==3,rows
    app.button(key="optimize_selected").click().run()
    check("optimizer applies feasible training allocation")
    for ticker in TICKERS:
        assert len(app.session_state["custom"])==7

    page("Investment Committee Reports")
    app.button(key="prepare_reports").click().run()
    check("selected PDF/CSV package generation")
    _,(_,archive,entries)=app.session_state["report_export"]
    for name,low,high in [("technical.pdf",7,15),("tear_sheet.pdf",1,1),("memo.pdf",1,1)]:
        pages=len(re.findall(rb"/Type\s*/Page\b",entries[name]))
        assert low<=pages<=high,(name,pages)
    page("AI Research Assistant")
    for question in app.selectbox(key="guide_question").options:
        app.selectbox(key="guide_question").set_value(question).run()
        check("guide "+question)
    page("Assumptions & Limitations")
    page("Methodology, Sources & AI Disclosure")
    (ROOT/"outputs/results/improvement_checks.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(str(len(results))+" improvement interface checks passed")


if __name__=="__main__":
    main()
