"""Real app checks for confidence feedback, durable limits and matching exports."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.config import ROOT,TICKERS


def main():
    app=AppTest.from_file(str(ROOT/"hosted_app.py"),default_timeout=120).run()
    results=[]
    def check(name):
        assert not app.exception,[e.message for e in app.exception]
        results.append({"check":name,"passed":True})
    check("product launch")
    value99=app.metric[3].value
    stable=[m.value for m in app.metric[:3]]
    app.selectbox(key="confidence").set_value(.95).run()
    assert app.metric[3].label=="Historical ES 95%" and app.metric[3].value!=value99
    assert stable==[m.value for m in app.metric[:3]]
    assert any("3 failed policy checks" in item.value for item in app.markdown)
    check("confidence changes visible risk while returns and policy stay fixed")
    app.selectbox(key="page").set_value("Risk Analytics").run()
    levels=next(frame.value for frame in app.dataframe if "Expected exceedance frequency" in frame.value.columns)
    assert levels.Confidence.tolist()==["90%","95%","99%"]
    values=np.array([float(v.strip('%')) for v in levels.VaR])
    prices=pd.read_csv(ROOT/"data/snapshots/adjusted_prices.csv",index_col=0,parse_dates=True)[TICKERS]
    weights=pd.read_csv(ROOT/"outputs/tables/allocations.csv",index_col=0).iloc[:,0].to_numpy()
    losses=-(prices.pct_change(fill_method=None).dropna().iloc[-756:].to_numpy()@weights)
    np.testing.assert_allclose(values,np.quantile(losses,[.90,.95,.99])*100,atol=.0051)
    assert np.all(np.diff(values)>=0)
    check("all confidence levels match independent quantiles of real selected returns")
    app.selectbox(key="method").set_value("EVT").run()
    levels=next(frame.value for frame in app.dataframe if "Expected exceedance frequency" in frame.value.columns)
    assert levels.iloc[0].VaR=="Unavailable"
    assert levels.iloc[1].VaR!="Unavailable"
    check("confidence comparison keeps EVT90 unavailable")
    app.selectbox(key="page").set_value("Portfolio Decision Lab").run()
    app.number_input(key="limit_dd").set_value(20.0).run()
    app.number_input(key="limit_scenario").set_value(18.0).run()
    check("risk limits can be edited")
    app.selectbox(key="page").set_value("Executive Command Center").run()
    app.selectbox(key="page").set_value("Investment Committee Reports").run()
    assert any("Edited research limits" in x.value for x in app.warning)
    app.button(key="prepare_reports").click().run()
    _,(_,_,entries)=app.session_state["report_export"]
    meta=json.loads(entries["metadata.json"])
    assert meta["limits"]["drawdown"]==.20 and meta["limits"]["scenario_loss"]==.18
    assert meta["current_confidence"]==.95 and meta["current_method"]=="EVT"
    check("limits and confidence persist through navigation into actual report metadata")
    app.selectbox(key="page").set_value("Portfolio Decision Lab").run()
    assert app.number_input(key="limit_dd").value==20.0
    assert app.number_input(key="limit_scenario").value==18.0
    app.button(key="restore_limits").click().run()
    assert app.number_input(key="limit_dd").value==15.0 and app.number_input(key="limit_scenario").value==15.0
    check("returning editor and original-limit restoration are consistent")
    app.selectbox(key="page").set_value("Portfolio Construction").run()
    app.selectbox(key="portfolio").set_value("60/40 benchmark").run()
    app.selectbox(key="lookback").set_value(252).run()
    import datetime
    app.date_input(key="dates").set_value((datetime.date(2025,1,2),datetime.date(2025,12,31))).run()
    app.button(key="restore_reference").click().run()
    assert app.selectbox(key="portfolio").value=="AEGIS minimum variance"
    assert app.selectbox(key="confidence").value==.99 and app.selectbox(key="method").value=="Historical"
    assert app.selectbox(key="lookback").value==756
    assert tuple(app.date_input(key="dates").value)==tuple(app.session_state["_reference_dates"])
    assert not any("widget with key" in item.value.lower() for item in app.warning)
    check("reference reset restores allocation and analysis controls")
    app.selectbox(key="page").set_value("Investment Committee Reports").run()
    assert "report_export" in app.session_state
    assert not any(item.proto.label=="Download selected analysis package · ZIP" for item in app.get("download_button"))
    check("changed settings do not expose stale selected report downloads")
    (ROOT/"outputs/results/product_release_checks.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(f"{len(results)} product release checks passed")


if __name__=="__main__":main()
