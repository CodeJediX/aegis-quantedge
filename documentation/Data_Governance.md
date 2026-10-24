# Data governance

ETF source is Yahoo Finance accessed through yfinance. The seven permitted tickers are the only holdings. FRED DTB3 provides a risk-free diagnostic; no additional macro dataset is used. Requested price period is 2005-01-01 through 2026-09-30, with API end 2026-10-01 exclusive. Common actual prices begin 2005-01-03. Snapshot metadata records exact retrieval timestamps, checksums, dates, source and library versions.

The raw adjusted-price snapshot is compact and authentic. It is bundled so a judge can reproduce the submitted result offline rather than depend on mutable vendor adjustments. `python run.py --refresh-data` redownloads through approved sources; vendor revisions create a new research dataset. A failed request raises an actionable error. No substitute vendor, synthetic price or invented observation is used.

Dates are normalized, sorted, checked for duplicates and intersected before returns. No price forward-fill or outlier deletion is performed. Every cleaning step runs in src/data.py. Large log moves, flat prices and abrupt rolling-volatility changes are flagged and retained in data_flags.csv. A flag is a request for inspection, not proof of an error. Coverage and ADF results are exported. ADF unit-root rejection does not imply iid returns or constant volatility.

DTB3 is numeric, valid observed values are carried forward over the union of source/trading dates and shifted by one observation before trading-date alignment. There is no backfill or use of same-date rate closes. Current-vintage historical rates and Yahoo revisions remain point-in-time limitations. Price snapshot validation does not establish accuracy against an independent vendor or verify dates omitted by all assets.

Reproduction validates SHA-256 inputs. Downloaded data are supplied for this competition research, without a claim of unrestricted commercial redistribution rights. Do not publish private credentials. The mandatory code uses no secrets and the .env.example contains no live keys.
