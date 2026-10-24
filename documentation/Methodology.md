# Methodology

The locked design uses 2005–2018 returns to fit portfolio weights, 2019–2022 as a development reporting period and 2023–2026 as a chronological test. These are retrospective design choices, not a preregistered live strategy. No held-out performance selects a portfolio or tunes its settings.

## Portfolio construction and KPIs

Markowitz variance minimization uses 90% sample covariance plus 10% diagonal covariance, annualized by 252. A mean-variance alternative uses 50% sample means plus 50% the cross-asset mean and risk aversion 6. A constrained equal-risk-contribution objective is labelled constrained risk parity, since limits prevent exactly equal budgets. Equal weighting and 60/40 SPY/AGG are transparent comparisons and need not satisfy the proposed conservative limits. AGG concentration and SPY/XLK overlap are explicit trade-offs.

Exact gross portfolio return is w'R with simple asset returns. Daily rebalance cost is 0.001 times the absolute deviation of the prior day's drifted weights from target. Net return is (1-cost)(1+gross)-1. NAV compounds net simple returns. The initial purchase is excluded. Benchmark uses identical accounting. KPIs use daily lagged risk-free returns, SPY market proxy and the 60/40 benchmark. Full definitions and limits are in Assumptions_and_Limitations.md.

## Loss models

Loss L = -w'R. Historical VaR is the linearly interpolated empirical alpha quantile q. ES = q + mean[(L-q)+]/(1-alpha). This finite-sample excess form is used consistently. Parametric risk fits a Gaussian to log(1+portfolio gross return) and uses exact lognormal tail integration. Monte Carlo simulates joint Gaussian asset log returns, uses 95% sample covariance plus 5% diagonal and transforms each asset back to simple return before aggregation. Both Gaussian approaches can underestimate heavy tails.

EVT fits a generalized Pareto distribution to positive excesses above the 90th loss percentile, with zero excess location. VaR = u + beta/xi [(p_u/(1-alpha))^xi - 1], using the logarithmic limit when xi approaches zero. ES = (VaR + beta - xi*u)/(1-xi), available only for xi<1. Requested confidence must exceed the fitted threshold quantile and tail probability. At least 40 exceedances are required. The frozen 90% rule provides about 76 exceedances in a 756-day window; sensitivity and block-resampled intervals expose uncertainty instead of selecting a threshold on test performance.

## Validation and decision support

One-step forecasts use only the preceding 756 observations. Main test includes historical, parametric, Monte Carlo, EVT at 95/99% and an interpretable volatility-state extension at all three confidence levels. The extension scales demeaned historical shocks by clipped 20-day/long-window volatility. No classifier training or external LLM is required.

Kupiec evaluates unconditional hit coverage, Christoffersen first-order independence and their sum conditional coverage. Degenerate transitions produce N/A. Basel traffic lights require precisely 250 one-day 99% forecasts. FZ0 joint score is excess/(p*ES) + VaR/ES + log(ES) - 1 for positive ES. Lower is better; paired 20-day block intervals compare extension and historical forecasts. Results of failed tests are retained.

Historical risk contributions differentiate the empirical ES estimator including quantile interpolation. They sum to total ES by Euler homogeneity; a finite-difference test verifies the derivative. Gaussian simple-return VaR marginal contributions use -mu + z_alpha*Sigma*w/sigma and are explicitly labelled as a separate approximation. Crisis P&L contributions include changing NAV and sum to terminal return. Historical stress is hindsight replay; hypothetical shocks are assumptions, not observations.

The policy scorecard uses separate limit checks and no composite weighting. This avoids inventing a standard capital-preservation score. Limits are sensitivity-tested at 80%, 100%, 120% and require committee approval. Risk-budget sizing is diagnostic only: cash is not an eligible holding, so a fundable change must use the approved universe or a revised mandate.
