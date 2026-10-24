# Timed rehearsal draft

Target: 11 minutes across 12 slides. Read at a measured pace, pause at charts, and rehearse aloud. These are suggested words, not a claim that a live pitch has occurred. The team must revise the judgment into its own independently substantiated argument.

## 1. AEGIS | 0:00–0:35

Good morning. We are Quantum-X, and AEGIS is our research platform for the Serendib University Endowment. Our starting question is how to preserve the fund’s ability to support its mission when markets are adverse. We study the prescribed seven-ETF universe and a ten-million-dollar mandate. We will show both the candidate allocation and the evidence that prevents us from recommending unconditional funding. This is an AI-assisted research proposal, and its investment judgment remains subject to independent team review.

## 2. The investment decision | 0:35–1:25

Our proposed decision is to adjust the mandate before committing capital. The analysis does not stop at a favourable Sharpe ratio or an attractive return. We compare the candidate with an explicit risk tolerance, then ask whether it survives the historical and assumed stresses we can examine. That comparison exposes a conflict: our provisional crisis tolerance is fifteen percent, while some losses are larger. The committee must resolve the limit, or require a different eligible allocation. A daily risk model cannot make that governance decision for it.

## 3. A conservative policy framework | 1:25–2:20

The horizon is at least ten years, but the immediate risk engine forecasts one-day losses. Those horizons serve different purposes. We use a provisional four-percent nominal total-return objective and a two-and-a-half-percent inflation assumption, leaving about one-point-four-six percent real growth before spending. A payout requirement has not been provided, so sustainable income adequacy is not established. Bonds have a floor and cap, gold has its own range, and aggregate equities are capped. These are proposed limits for committee review, rather than a claim that the client already approved them.

## 4. Data before decisions | 2:20–3:15

The prices come from Yahoo through yfinance, with adjusted closes for the seven eligible ETFs. FRED supplies the risk-free diagnostic. We align dates before returns, retain flagged large moves and record hashes so the judge can reproduce the actual dataset. Portfolio weights use data through twenty-eighteen. We report twenty-nineteen through twenty-twenty-two separately, followed by the later held-out sample. This is retrospective chronological testing, not a preregistered live track record. FRED data are strictly lagged but current vintage, which remains a point-in-time limitation.

## 5. The proposed allocation | 3:15–4:15

The main portfolio minimizes training variance using a covariance estimate with ten-percent diagonal shrinkage. The bond cap binds. The result holds seventy percent AGG, ten percent gold, and the remaining twenty percent in SPY and XLK. The other eligible weights are zero because diversification by ticker count is not the objective, and we did not force geographic exposures. There are costs to that choice: AGG concentrates duration and credit risk, while SPY overlaps technology. Those exposures must be weighed against the estimated reduction in ordinary portfolio volatility.

## 6. Return is one part of suitability | 4:15–5:15

In the held-out period, the candidate produces net CAGR of 9.99%, volatility of 6.64%, and drawdown of 6.12%. The comparison table also shows alternatives with higher later returns. We do not switch to them because they performed well in the test sample. Equal weights and sixty-forty also exceed the proposed equity ceiling. Net performance charges ten basis points per dollar of daily rebalance turnover. Initial purchase, taxes, spending and market impact remain outside the calculation. Historical returns therefore inform suitability but cannot promise the endowment a spendable yield.

## 7. Risk estimates depend on assumptions | 5:15–6:15

The risk comparison holds portfolio, horizon and confidence constant. Historical VaR samples observed portfolio losses. The parametric model assumes normal portfolio log returns. Monte Carlo simulates correlated normal asset log returns and aggregates their simple returns, using a different covariance correction. Their disagreement therefore reflects both assumptions and aggregation. More importantly, the two Gaussian estimates are not independent confirmation of tail safety. Expected Shortfall complements VaR by estimating loss severity beyond the cutoff. All dollar amounts scale one-day fractional losses to the ten-million-dollar reference capital.

## 8. EVT makes uncertainty visible | 6:15–7:15

EVT focuses on the tail rather than fitting the whole loss distribution. We fit threshold excesses with a generalized Pareto model. The ninety-percent threshold was frozen to retain about seventy-six exceedances in the rolling window, while sensitivity reveals what happens when that choice changes. The latest fitted shape is negative, but its uncertainty spans zero. We therefore do not present the fitted endpoint as a dependable maximum loss. The laboratory rejects insufficient samples and unsupported confidence levels, and it suppresses an ES when the fitted tail mean is not finite.

## 9. Forecasts precede observed losses | 7:15–8:15

For validation, each threshold uses exactly the seven-hundred-and-fifty-six returns preceding its forecast date. Kupiec checks the exception frequency. Christoffersen asks whether exceptions cluster in a first-order pattern, and the combined test checks both. Small p-values challenge the stated model assumptions; large p-values do not certify safety. The full test is longer than two-hundred-and-fifty observations. Its traffic light is therefore not applicable. The separately labelled last-two-hundred-and-fifty classification uses one-day ninety-nine-percent forecasts and the legacy Basel cutoffs, as a teaching diagnostic rather than regulation of this fund.

## 10. Crisis losses challenge the risk budget | 8:15–9:15

The stress evidence changes the decision. We replay genuine daily ETF paths for the financial crisis, COVID and the rate-hiking year. The replay is deliberately labelled hindsight exposure, because these weights were not a policy available in two-thousand-and-eight. Terminal return can conceal a deeper interim drawdown. We also assume a simultaneous funding squeeze where equities, bonds and gold all lose value. That shock has no assigned probability or invented recovery. The observed seventeen-and-a-half-percent drawdown and roughly fifteen-point-two-percent hypothetical loss challenge the provisional fifteen-percent tolerance.

## 11. Useful innovation includes rejection | 9:15–10:10

Our regime extension is intentionally simple: short-window volatility scales historical shocks relative to the longer window. It makes forecasts adaptive without an opaque classifier. But the evidence does not show a reliable improvement. The score difference interval crosses zero and exception clustering worsens. We keep that negative finding instead of promoting complexity. The useful innovations are also operational: a threshold stability laboratory, crisis playback, a ledger of assumptions and validation, and separate policy checks without arbitrary composite weights. The research assistant merely guides reviewers to computed evidence and requires no external AI service.

## 12. Conditions for a fundable mandate | 10:10–11:00

The closing action is to agree the acceptable crisis exposure, define the spending requirement and approve a feasible rebalancing process. If the fifteen-percent tolerance is binding, a revised allocation must be substantiated before funding; otherwise the current proposal should be rejected. Historical losses can still be exceeded, even after the mandate is revised. The package provides the working application, reproducible calculations, reports and defence material. The human team must independently examine, revise and defend the allocation and final recommendation. With those conditions stated, we welcome questions on both what the models measure and what they leave unresolved.