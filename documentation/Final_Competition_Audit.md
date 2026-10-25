# Critical review against the final rubric

Agent-performed audit, 24 October 2026. This is a critical review against the supplied rubric, not an independent human opinion or a predicted judge score.

| Rubric | Evidence | Remaining weakness / action |
|---|---|---|
| Investment decision-making — 30% | Training-constrained candidate, comparisons, explicit objective/horizon/limits, asset ES contributions, three crisis paths and a joint-loss scenario, one-page ADJUST memo | Spending/income requirement absent. Candidate breaches proposed crisis tolerance. Human committee/team must resolve this before accepting a funded mandate. The draft does not disguise a breach as conservative suitability. |
| Technical rigor — 25% | Exact simple-return accounting, log-model distinctions, full KPI set/CAPM, three VaR approaches at95/99, ES, justified POT/GPD with uncertainty, strictly prior-window forecasts and reference tests | Daily unconditional/rolling models omit long-horizon funding shortfall, current-vintage data are not a full point-in-time database, EVT has a small clustered tail sample, and Gaussian agreement is not independent evidence. ADF is not proof of stationarity of all moments. |
| Software/interface — 15% | Twelve working Streamlit workspaces, functional risk/allocation/date controls, offline snapshots, testable modules, error handling and responsive UI | The fixed validation record does not instantly recompute for arbitrary custom portfolios; this is clearly labelled. Desktop/mobile preview checked, but no broad browser/device compatibility certification. Public GitHub source and live Streamlit deployment verified 25 October 2026. |
| Innovation/ambition — 15% | EVT threshold lab, crisis replay controls, risk contributions, evidence ledger, separate policy scorecard/limit sensitivity and a walk-forward volatility-state comparison | The adaptive extension worsens conditional coverage and has no clear score improvement. It is not adopted as default. No gratuitous classifier or LLM feature is presented as validated research. |
| Communication/defence — 15% | 13-page report, one-page tear sheet, one-page memo, native 12-slide deck, 11-minute rehearsal draft, 30 Q&A items, clear disclosure | Live delivery has not been rehearsed or judged by the team. Independent human review and ability to defend every material choice remain essential. |

## Requirements with external completion steps

1. Public source: https://github.com/CodeJediX/aegis-quantedge. Live app: https://quantumx-aegis.streamlit.app/ (verified 25 October 2026). Free hosting uses read-only SQLite; external PostgreSQL support is optional and no Supabase database is claimed.
2. Complete independent human review under section 8.7. Record actual checks, changes, reviewers and approval; do not manufacture a signature or treat agent tests as human judgment.

The local application, data, reports and pitch files are completed. Deployment is optional because the brief permits a one-command local application. No source outside the approved Yahoo/FRED list is used for financial observations. No optional external LLM is needed. No claim of a winning score or unconditional submission eligibility is made.

## Interpretation that must survive the defence

A portfolio can have low ordinary volatility yet fail a crisis-loss tolerance. The chosen candidate is retained as a pre-specified conservative starting point, not selected for the best later return. Its stress-limit conflict drives ADJUST. A non-rejected statistical null and a green legacy traffic light cannot resolve that investment-policy conflict. This is the decision evidence the team must independently evaluate.
