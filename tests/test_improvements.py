"""Independent numerical references and selected-portfolio consistency checks."""

import hashlib
from io import BytesIO
import json
import re
import unittest
import zipfile
import numpy as np
import pandas as pd
from scipy.stats import norm

from src.config import ROOT, TICKERS, NAV, TRAIN_END
from src.portfolio import metrics, path, capm
from src.risk import mc_losses, empirical, normal_log, contributions, filtered_forecast
from src.backtesting import summarize, traffic, coverage
from src.evt import uncertainty, estimate
from src.data import validate_prices
from src.interactive import Limits, analyze, recommendation, usd, allocation_id, optimize, allocation_checks, library_json, parse_library, what_if
from src.exports import provenance, export_package


class IndependentReferences(unittest.TestCase):
    def test_all_performance_ratios_against_scalar_reference(self):
        p=np.array([.012,-.006,.003,-.009,.017,.002,-.004,.008]*45)
        market=np.array([.01,-.013,.002,.006,.014,-.005,.004,.007]*45)
        benchmark=market*.55+.00003
        rf=np.full(len(p),.00008)
        actual=metrics(p,market,benchmark,rf)
        annual=252
        ex=p-rf
        mx=market-rf
        mean=lambda x:sum(float(v) for v in x)/len(x)
        variance=lambda x:sum((float(v)-mean(x))**2 for v in x)/(len(x)-1)
        vol=np.sqrt(variance(p)*annual)
        beta=sum((float(x)-mean(ex))*(float(y)-mean(mx)) for x,y in zip(ex,mx))/sum((float(y)-mean(mx))**2 for y in mx)
        wealth=1.0
        peak=1.0
        dd=0.0
        for value in p:
            wealth*=1+float(value)
            peak=max(peak,wealth)
            dd=max(dd,1-wealth/peak)
        cagr=wealth**(annual/len(p))-1
        downside=np.sqrt(mean([min(float(x),0)**2 for x in ex])*annual)
        expected={"CAGR":cagr,"arithmetic_return":mean(p)*annual,"volatility":vol,
            "Sharpe":mean(ex)*annual/vol,"Sortino":mean(ex)*annual/downside,
            "Treynor":mean(ex)*annual/beta,"Jensen_alpha":(mean(ex)-beta*mean(mx))*annual,
            "information_ratio":mean(p-benchmark)*annual/np.sqrt(variance(p-benchmark)*annual),
            "max_drawdown":dd,"Calmar":cagr/dd,"beta":beta,"cumulative_return":wealth-1}
        for key,value in expected.items():
            self.assertAlmostEqual(actual[key],value,places=11,msg=key)

    def test_capm_matches_independent_least_squares(self):
        rng=np.random.default_rng(193)
        market=rng.normal(.0003,.01,500)
        rf=pd.Series(np.full(500,.0001))
        frame=pd.DataFrame({ticker:(1+i/10)*market+rng.normal(0,.002,500) for i,ticker in enumerate(TICKERS)})
        frame.SPY=market
        got=capm(frame,rf)
        design=np.c_[np.ones(500),market-rf]
        for row in got.itertuples():
            alpha,beta=np.linalg.lstsq(design,frame[row.ticker]-rf,rcond=None)[0]
            self.assertAlmostEqual(row.beta,beta,places=11)
            self.assertAlmostEqual(row.annual_alpha,alpha*252,places=11)

    def test_monte_carlo_joint_moments_and_seed(self):
        rng=np.random.default_rng(812)
        cov=np.full((7,7),.00004)+np.eye(7)*.00006
        x=rng.multivariate_normal(np.full(7,.0002),cov,size=1800)
        weights=np.array([.1,.05,.05,.6,.15,.02,.03])
        loss=mc_losses(pd.DataFrame(x),weights,n=100000,seed=71)
        sample_cov=np.cov(x,rowvar=False)
        shrunk=.95*sample_cov+.05*np.diag(np.diag(sample_cov))
        mu=x.mean(axis=0)
        expmean=np.exp(mu+.5*np.diag(shrunk))
        expected_mean=-float(weights@(expmean-1))
        asset_cov=np.outer(expmean,expmean)*np.expm1(shrunk)
        expected_variance=float(weights@asset_cov@weights)
        self.assertLess(abs(loss.mean()-expected_mean),5*np.sqrt(expected_variance/len(loss)))
        self.assertLess(abs(loss.var(ddof=1)/expected_variance-1),.025)
        np.testing.assert_array_equal(loss[:2000],mc_losses(pd.DataFrame(x),weights,n=2000,seed=71))
        prefix=empirical(loss[:50000],.99)["ES"]
        full=empirical(loss,.99)["ES"]
        self.assertLess(abs(prefix-full),.001)

    def test_flat_distributions_are_defined(self):
        r=pd.DataFrame(np.zeros((200,7)),columns=TICKERS)
        weights=np.array([.2,0,0,.6,.2,0,0])
        self.assertEqual(normal_log(np.zeros(200),.99),dict(VaR=0.0,ES=0.0))
        np.testing.assert_array_equal(mc_losses(r,weights,n=200),np.zeros(200))
        self.assertEqual(filtered_forecast(np.zeros(200),.99)["volatility_ratio"],1)
        self.assertIsNone(metrics(np.zeros(200),np.zeros(200),np.zeros(200),np.zeros(200))["beta"])
        self.assertTrue(np.isfinite(contributions(r,weights).component_normal_VaR).all())

    def test_basel_boundaries_and_binary_input_validation(self):
        for hits,expected in [(0,"Green"),(4,"Green"),(5,"Amber"),(9,"Amber"),(10,"Red"),(250,"Red")]:
            self.assertEqual(traffic(np.r_[np.ones(hits),np.zeros(250-hits)],.99),expected)
        self.assertTrue(traffic(np.zeros(249),.99).startswith("N/A"))
        for value in [.9,.95]:
            self.assertTrue(traffic(np.zeros(250),value).startswith("N/A"))
        with self.assertRaises(ValueError):
            coverage(np.array([0,.5,1]),.99)

    def test_full_and_latest_250_windows_are_separate(self):
        n=300
        loss=np.zeros(n)
        loss[:10]=2
        loss[-3:]=2
        frame=pd.DataFrame(dict(model="Historical",confidence=.99,date=pd.bdate_range("2024-01-01",periods=n),VaR=1.0,ES=1.5,loss=loss))
        got=summarize(frame).iloc[0]
        self.assertEqual(got.exceptions,13)
        self.assertEqual(got.last250_exceptions,3)
        self.assertAlmostEqual(got.expected,3)
        self.assertAlmostEqual(got.last250_expected,2.5)
        self.assertEqual(got.traffic_last250,"Green")
        self.assertTrue(got.traffic_full.startswith("N/A"))
        duplicate=pd.concat([frame,frame.iloc[:1]])
        with self.assertRaises(ValueError):
            summarize(duplicate)

    def test_selected_confidence_evt_intervals_reproduce(self):
        x=np.random.default_rng(920).exponential(.01,1500)
        first=uncertainty(x,.85,.95,reps=30)
        second=uncertainty(x,.85,.95,reps=30)
        self.assertEqual(first,second)
        self.assertEqual(first["confidence"],.95)
        self.assertLess(first["VaR_CI"][0],first["VaR_CI"][1])
        self.assertLess(first["ES_CI"][0],first["ES_CI"][1])
        with self.assertRaises(ValueError):
            uncertainty(x,.95,.95,reps=30)
        self.assertIsNone(estimate(dict(shape=1.1,scale=.01,threshold=.02,p_exceed=.1),.99)["ES"])


class SelectedPortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prices=pd.read_csv(ROOT/"data/snapshots/adjusted_prices.csv",index_col=0,parse_dates=True)
        cls.r=cls.prices.pct_change(fill_method=None).dropna()
        cls.rf=pd.read_csv(ROOT/"outputs/tables/risk_free.csv",index_col=0,parse_dates=True).iloc[:,0]
        cls.alloc=pd.read_csv(ROOT/"outputs/tables/allocations.csv",index_col=0)
        cls.weights=cls.alloc.iloc[:,0].to_numpy()

    def test_currency_identity_for_all_risk_and_stress_rows(self):
        self.assertEqual(usd(-.1523),-1523000)
        self.assertEqual(usd(.01),100000)
        stress=pd.read_csv(ROOT/"outputs/tables/stress.csv")
        np.testing.assert_allclose(stress.return_pct.map(usd),stress.USD,atol=.001)
        risk=pd.read_csv(ROOT/"outputs/tables/risk_snapshot.csv")
        np.testing.assert_allclose(risk.VaR.map(usd),risk.VaR_USD,atol=.001)
        np.testing.assert_allclose(risk.ES.map(usd),risk.ES_USD,atol=.001)

    def test_selected_stress_and_metrics_change_together(self):
        first=analyze(self.r,self.rf,self.weights,"reference")
        other=np.array([.2,0,0,.6,.2,0,0])
        second=analyze(self.r,self.rf,other,"custom")
        self.assertNotEqual(first["allocation_id"],second["allocation_id"])
        self.assertNotEqual(first["kpi"]["CAGR"],second["kpi"]["CAGR"])
        self.assertFalse(first["stress"].USD.equals(second["stress"].USD))
        hyp=second["stress"].query("n == 1").iloc[0]
        np.testing.assert_allclose(hyp[TICKERS].astype(float).sum(),hyp.return_pct)
        self.assertAlmostEqual(hyp.USD,usd(hyp.return_pct))

    def test_reference_breach_cannot_approve(self):
        result=analyze(self.r,self.rf,self.weights,"reference")
        card=result["checks"].set_index("check")
        self.assertEqual(card.loc["Worst historical replay drawdown","status"],"FAIL")
        self.assertEqual(recommendation(result)["status"],"REVISE")
        self.assertIn("PENDING",recommendation(result)["human_approval"])

    def test_benchmark_asset_cap_failure_is_rejected(self):
        result=analyze(self.r,self.rf,self.alloc["60/40 benchmark"].to_numpy(),"benchmark")
        self.assertEqual(recommendation(result)["status"],"REJECT")

    def test_approval_requires_policy_and_selected_validation(self):
        # Deliberately relaxed research limits exercise the branch; they are not
        # a claim that the original mandate or any human committee approved it.
        result=analyze(self.r,self.rf,self.weights,"reference",limits=Limits(drawdown=.20,scenario_loss=.20))
        forecasts=pd.read_csv(ROOT/"outputs/tables/forecasts.csv",parse_dates=["date"])
        validation=summarize(forecasts[forecasts.date>=pd.Timestamp(result["test_start"])])
        decision=recommendation(result,validation)
        self.assertEqual(decision["status"],"APPROVE")
        self.assertIn("PENDING",decision["human_approval"])
        self.assertEqual(recommendation(result)["status"],"REVISE")
        failed=validation.copy()
        failed.loc[(failed.model=="Historical") & np.isclose(failed.confidence,.99),"conditional_p"]=.001
        self.assertEqual(recommendation(result,failed)["status"],"REVISE")

    def test_limits_propagate_without_rewriting_weights(self):
        base=analyze(self.r,self.rf,self.weights,"reference")
        revised=analyze(self.r,self.rf,self.weights,"reference",limits=Limits(drawdown=.20,scenario_loss=.20))
        self.assertGreater(base["checks"].status.eq("FAIL").sum(),revised["checks"].status.eq("FAIL").sum())
        self.assertEqual(base["allocation_id"],revised["allocation_id"])
        self.assertEqual(base["kpi"],revised["kpi"])

    def test_complete_price_validation_rejects_bad_inputs(self):
        validate_prices(self.prices)
        bad=self.prices.copy()
        bad.iloc[0,0]=np.inf
        with self.assertRaises(ValueError):
            validate_prices(bad)
        bad=self.prices.copy()
        bad.iloc[0,0]=np.nan
        with self.assertRaises(ValueError):
            validate_prices(bad)
        with self.assertRaises(ValueError):
            validate_prices(pd.concat([self.prices,self.prices.iloc[:1]]))
        with self.assertRaises(ValueError):
            validate_prices(self.prices.iloc[::-1])

    def test_library_roundtrip_and_input_rejection(self):
        library={"My allocation":self.weights.tolist()}
        before=self.weights.copy()
        raw=library_json(library,"verified-dataset")
        self.assertEqual(parse_library(raw),library)
        np.testing.assert_array_equal(before,self.weights)
        data=json.loads(raw)
        data["portfolios"]["My allocation"]["CASH"]=0
        with self.assertRaises(ValueError):
            parse_library(json.dumps(data))
        with self.assertRaises(ValueError):
            library_json({"":self.weights},"version")
        with self.assertRaises(ValueError):
            parse_library("x"*1000001)

    def test_optimizer_hard_limits_and_future_data_guard(self):
        train=pd.DataFrame(.0003,index=pd.bdate_range("2017-01-01",periods=150),columns=TICKERS)
        limits=Limits()
        w=optimize(train,limits)
        self.assertTrue(allocation_checks(w,limits).status.eq("PASS").all())
        from src.config import HYPOTHETICAL
        self.assertLessEqual(-w@np.array([HYPOTHETICAL[t] for t in TICKERS]),limits.scenario_loss+1e-7)
        with self.assertRaises(ValueError):
            optimize(self.r,limits)
        with self.assertRaises(ValueError):
            optimize(train,Limits(objective=.3))

    def test_what_if_rate_sign_units_and_additivity(self):
        got=what_if(self.weights,-.2,100,6,-.05)
        self.assertAlmostEqual(got.loc[got.ticker=="AGG","assumed_return"].iloc[0],-.06)
        self.assertAlmostEqual(got.contribution_USD.sum(),usd(got.contribution.sum()))
        opposite=what_if(self.weights,-.2,-100,6,-.05)
        self.assertGreater(opposite.contribution.sum(),got.contribution.sum())

    def test_selected_export_provenance_and_pdf_lengths(self):
        result=analyze(self.r,self.rf,self.weights,"Selected verification portfolio")
        decision=recommendation(result)
        risk=pd.read_csv(ROOT/"outputs/tables/risk_snapshot.csv").query("confidence == .99")
        meta=provenance(result,"dataset-verification",.99,"Historical")
        prefix,archive,entries=export_package(result,risk,decision,meta)
        self.assertIn(result["allocation_id"],prefix)
        with zipfile.ZipFile(BytesIO(archive)) as zipped:
            self.assertIsNone(zipped.testzip())
        for line in entries["SHA256SUMS.txt"].decode().splitlines():
            digest,name=line.split("  ",1)
            self.assertEqual(hashlib.sha256(entries[name]).hexdigest(),digest)
        for name,data in entries.items():
            if name.endswith(".csv"):
                frame=pd.read_csv(BytesIO(data))
                self.assertTrue(frame.capital_USD.eq(NAV).all())
                self.assertTrue(frame.allocation_id.eq(result["allocation_id"]).all())
        for name,low,high in [("technical.pdf",7,15),("tear_sheet.pdf",1,1),("memo.pdf",1,1)]:
            data=entries[name]
            pages=len(re.findall(rb"/Type\s*/Page\b",data))
            self.assertTrue(low<=pages<=high,(name,pages))


if __name__=="__main__":
    unittest.main()
