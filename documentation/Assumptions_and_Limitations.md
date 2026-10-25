# Assumptions and limitations

## Proposed mandate assumptions

USD 10 million, 10+ year horizon and annual governance review. Proposed nominal total-return objective: 4% before endowment spending, motivated by an assumed 2.5% inflation rate and about 1.46% real growth. This inflation assumption is not a forecast or downloaded observation. A sustainable spending rate and income payout requirement must be agreed with the client; reinvested distributions are not separately spendable cash in the model.

Fully invested, long only, no leverage. AGG 35–70%, GLD 5–20%, combined equity 20–50%. Individual caps: SPY 25%, EFA 20%, EEM 15%, XLE 10%, XLK 20%. Constraints are proposed governance assumptions, not client-confirmed limits. SPY overlaps with XLK and XLE. Geographic diversification is available but not forced. AGG concentration is a duration, credit and mortgage exposure, not a cash guarantee.

## Portfolio and return accounting

Log returns are stored and used in ADF and Gaussian simulations. Portfolio wealth uses exact weighted simple returns. Daily rebalancing is an explicit, potentially impractical assumption; 10bp times the absolute traded weights is charged before each subsequent day's return. Initial establishment, taxes, custody and market impact are excluded. Published KPIs are net of these assumed rebalance costs. Risk forecasts and historical stress replays use hypothetical gross P&L at constant target weights, not actual net fund P&L. Dollar losses use constant reference NAV of USD 10 million.

252-day annualization; CAGR uses the number of observations/252, not elapsed calendar years. Sortino uses all-observation downside deviation relative to lagged daily risk-free return. Treynor can be unstable at small beta. Jensen alpha and CAPM use SPY as an imperfect market proxy and are not proof of skill. Information ratio uses the 60/40 SPY/AGG benchmark. No claim of return predictability follows from historical shrunk means.

## Data and temporal validity

Yahoo adjusted histories can be revised. The supplied hashes freeze the specific retrieved snapshot. All seven ETFs have common history from 2005; no missing returned trading-date cells were interpolated. Common omissions by every ticker are not detected by an exchange-calendar cross-check. Price flags identify potential anomalies and genuine crises together; flagged returns are retained. No independent second vendor validation was performed.

DTB3 is a bank-discount quote converted using a 91-day assumed bill maturity and 365/360 yield conversion, then to daily compounding over 252 days. Only strictly earlier observations are used. Current-vintage FRED data are not a perfect historical information set; release delays and revisions are not modelled. The risk-free proxy affects performance diagnostics, not the portfolio weights or risk forecasts.

Allocation training ends 2018-12-31. Development is 2019–2022; test is 2023–2026. No development- or test-based portfolio or hyperparameter selection is used. The allocation design was constructed after those historical dates, so this is a retrospective chronological experiment, not a preregistered or real-time track record. Crisis replays use the later selected weights and are explicitly hindsight exposure tests.

## Model limits

All VaR/ES forecasts are one-day. Do not multiply daily estimates by the square root of a long horizon and treat that as a tested capital bound. Historical quantiles cannot extrapolate beyond the training shocks. The parametric model fits a normal portfolio log return; Monte Carlo simulates normal asset log returns, then aggregates simple returns. Both omit heavy-tailed innovations; their agreement is not independent model validation. MC uses 5% diagonal covariance shrinkage, 50,000 snapshot draws and 10,000 rolling draws with a fixed seed/common random numbers.

EVT uses the upper loss tail above the 90th percentile, chosen before test evaluation to provide roughly 76 exceedances in 756 observations while isolating the loss tail. Threshold sensitivity at 85%, 87.5%, 90%, 92.5%, 95% exposes bias–variance trade-offs. No claim of an objectively optimal threshold is made. Fewer than 40 exceedances are rejected. ES is unavailable when fitted shape is at least one. Serial clustering, nonstationarity and small tail samples undermine asymptotic precision. The 20-day circular-block bootstrap refits thresholds and parameters but is not a full guarantee of confidence-interval coverage. No EVT estimate is reported at/below the fitting threshold.

Rolling risk estimates use exactly the 756 preceding returns and never the forecast-date return. Kupiec assumes Bernoulli coverage under its null; Christoffersen examines first-order exception clustering. Sparse exceptions make power weak; degenerate transition rows produce unavailable independence diagnostics. A non-rejection is not approval. Basel green/amber/red applies only to 250 one-day 99% forecasts (0–4 / 5–9 / 10+ exceptions). The dashboard explicitly distinguishes full range from last 250 observations and labels other settings N/A. This is a teaching application of legacy Basel backtesting, not an endowment capital regulation.

The volatility-state extension scales historical shocks by the 20-day/756-day volatility ratio, clipped at 0.5–3. It is statistical and interpretable, not machine learning. Its test results are retained even when unfavourable. Historical replay does not predict the next crisis; the hypothetical scenario carries no estimated probability and no invented recovery path. Recovery means regained pre-trough replay peak, not inflation-adjusted recovery.

## Decision and approval

The scorecard reports separate policy tests without a weighted composite. Proposed limits are 10% annual volatility, 15% drawdown/scenario loss and 2.5% daily ES99; nominal return objective 4%. A failure requires review; a pass does not imply safety. Limit sensitivity is shown at ±20%. The proposal is ADJUST: resolve stress-limit breaches and missing spending/income assumptions before funding. The human team must independently review the allocation, model logic and investment conclusion. The application cannot grant that approval.

The current interactive equivalent is **REVISE**, with three default failed checks:16.71% training net drawdown,15.23% worst terminal scenario loss and17.52% worst historical crisis drawdown against15% proposed limits. APPROVE/REVISE/REJECT is automated triage only; human approval remains pending. Editable limits are research assumptions, not client-authorized mandate amendments. Strict optimization failure is not proof of global infeasibility.

## Interactive research and storage

Custom allocations are retrospective experiments. Repeated viewing or optimizing after seeing test/crisis outcomes can overfit the displayed history, even though solver inputs stop in2018 and each rolling forecast uses only earlier returns. Custom validation is unavailable until explicitly run; fixed-reference outputs are not relabelled. Unrun validation prevents automated APPROVE.

The named allocation library is scoped to the current session. Download its JSON to retain it and import it after a reset. Free public hosting uses a real read-only SQLite store rebuilt from verified snapshots; local disk is temporary and shared public saves are disabled. Optional administrator-controlled SQL saving is a separate deployment mode. No external PostgreSQL service is claimed.

Rate shocks use a first-order assumed duration approximation, omitting convexity, spreads, coupons and timing. Volatility multipliers and equity/gold shocks are hypothetical sensitivities without assigned probabilities. Tail confidence intervals are conditional on the block-resampling design and can be unavailable. The80-exceedance caution is heuristic. Neither advanced features nor a numerical APPROVE provide a capital guarantee.
