# Research data

`snapshots/adjusted_prices.csv` is the authentic yfinance adjusted-close input for the seven eligible ETFs. `snapshots/DTB3.csv` is the authentic FRED risk-free quote input. Metadata records retrieval UTC timestamps, URLs/source, fixed dates and checksums. Reproduction validates hashes, aligns dates and regenerates cleaned outputs; no hand-edited prices are required.

Run `python run.py --refresh-data` from the project root to fetch a new snapshot. Vendor revisions can change results; an input checksum change is a new dataset. Approved-source failures are reported; prices are never fabricated. The compact snapshots are intentionally bundled for reproducibility. See documentation/Data_Governance.md for limitations and data-use notes.
