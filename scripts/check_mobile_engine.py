"""Cross-check independently implemented native Java math against Python evidence."""
from pathlib import Path
import csv
import subprocess
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.config import ROOT,TEST_START
from src.interactive import analyze
from src.risk import empirical,normal_log
from src.backtesting import summarize
from build_mobile import BUILD,tools


def main():
    assets=BUILD/"assets";assets.mkdir(parents=True,exist_ok=True)
    import shutil
    for filename,original in [("adjusted_prices.csv","data/snapshots/adjusted_prices.csv"),("risk_free.csv","outputs/tables/risk_free.csv"),("allocations.csv","outputs/tables/allocations.csv")]:shutil.copyfile(ROOT/original,assets/filename)
    prices=pd.read_csv(assets/"adjusted_prices.csv",index_col=0,parse_dates=True);r=prices.pct_change(fill_method=None).dropna();rf=pd.read_csv(assets/"risk_free.csv",index_col=0,parse_dates=True).iloc[:,0]
    allocations=pd.read_csv(assets/"allocations.csv",index_col=0).to_dict("list");allocations["Custom 20-60-20"]=[.2,0,0,.6,.2,0,0]
    rows=[]
    for name,w in allocations.items():
        w=np.array(w);a=analyze(r,rf,w,name)
        values={**{k:a["kpi"][k] for k in ["CAGR","volatility","max_drawdown","Sharpe","Sortino","beta","Jensen_alpha","information_ratio","Calmar","Treynor","annual_turnover"]},"expected_return":a["expected_return"],"training_volatility":a["training_volatility"],"training_drawdown":a["checks"].set_index("check").loc["Training maximum net drawdown","value"],"ES99":a["ES99"],"failed_checks":int(a["checks"].status.eq("FAIL").sum())}
        for alpha in [.90,.95,.99]:
            simple=r.iloc[-756:].to_numpy()@w;hs=empirical(-simple,alpha);gauss=normal_log(simple,alpha)
            for model,v in [("HS",hs),("Gaussian",gauss)]:
                for key in ["VaR","ES"]:values[f"{model}_{key}_{alpha:.2f}"]=v[key]
        for i,row in enumerate(a["stress"].itertuples()):values[f"stress_{i}_return"]=row.return_pct;values[f"stress_{i}_drawdown"]=row.max_drawdown
        rows.extend((name+"::"+key,"NaN" if v is None else float(v)) for key,v in values.items())
    forecasts=pd.read_csv(ROOT/"outputs/tables/forecasts.csv",parse_dates=["date"]);card=summarize(forecasts[forecasts.date>=pd.Timestamp(TEST_START)]).query("model == 'Historical' and confidence == .99").iloc[0]
    rows.extend(("Backtest::"+key,float(card[source])) for key,source in [("n","n"),("hits","exceptions"),("last_hits","last250_exceptions"),("kupiec_p","kupiec_p"),("independence_p","independence_p"),("conditional_p","conditional_p")])
    with (assets/"python_reference.csv").open("w",newline="",encoding="utf-8") as f:writer=csv.writer(f);writer.writerow(["metric","expected"]);writer.writerows(rows)
    _,_,java,_,env=tools();out=BUILD/"jvm_checks";out.mkdir(exist_ok=True)
    subprocess.run([str(java/"javac.exe"),"-encoding","UTF-8","-d",str(out),str(ROOT/"mobile/app/src/main/java/com/quantumx/aegis/ResearchEngine.java"),str(ROOT/"mobile/tests/EngineReferenceTest.java")],check=True,env=env)
    completed=subprocess.run([str(java/"java.exe"),"-cp",str(out),"EngineReferenceTest",str(assets)],check=True,text=True,capture_output=True,env=env)
    print(completed.stdout)
    import json
    (ROOT/"outputs/results/mobile_engine_checks.json").write_text(json.dumps(dict(reference_checks=len(rows),result="PASS",output=completed.stdout.strip(),tolerance=2e-9,source="Python selected analysis and frozen reference backtests",synthetic_market_data=False),indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":main()
