"""Approved Yahoo/yfinance and FRED ingestion, immutable replay and explicit flags."""

from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
import requests
from statsmodels.tsa.stattools import adfuller
from .config import ROOT, TICKERS, START, END, TRAIN_END

LOG = logging.getLogger(__name__)


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(refresh: bool = False) -> None:
    target = ROOT / "data/snapshots/adjusted_prices.csv"
    if refresh or not target.exists():
        LOG.info("Downloading approved ETF universe through yfinance")
        frame = yf.download(
            TICKERS,
            start=START,
            end=END,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if frame.empty or "Adj Close" not in frame:
            raise RuntimeError(
                "Yahoo returned no adjusted prices. Use the supplied snapshot or retry; no substituted source."
            )
        prices = frame["Adj Close"].reindex(columns=TICKERS)
        if prices.isna().all().any():
            raise RuntimeError("Incomplete ticker download; snapshot not overwritten.")
        prices.index = pd.to_datetime(prices.index).tz_localize(None)
        prices.to_csv(target, float_format="%.12g")
        meta = dict(
            source="Yahoo Finance through yfinance.download, Adj Close",
            retrieved_utc=datetime.now(timezone.utc).isoformat(),
            tickers=TICKERS,
            start=START,
            end_exclusive=END,
            sha256=checksum(target),
            yfinance_version=yf.__version__,
        )
        (ROOT / "data/metadata/prices.json").write_text(json.dumps(meta, indent=2))
    fred = ROOT / "data/snapshots/DTB3.csv"
    if refresh or not fred.exists():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3&cosd=2004-12-01&coed=2026-09-30"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        from io import StringIO

        rates = pd.read_csv(StringIO(response.text))
        rates.to_csv(fred, index=False)
        (ROOT / "data/metadata/fred.json").write_text(
            json.dumps(
                dict(
                    source="FRED DTB3",
                    url=url,
                    retrieved_utc=datetime.now(timezone.utc).isoformat(),
                    sha256=checksum(fred),
                    basis="bank discount yield",
                ),
                indent=2,
            )
        )


def load() -> tuple:
    p = ROOT / "data/snapshots/adjusted_prices.csv"
    f = ROOT / "data/snapshots/DTB3.csv"
    for file, meta in [(p, "prices"), (f, "fred")]:
        record = json.loads((ROOT / f"data/metadata/{meta}.json").read_text(encoding='utf-8-sig'))
        if checksum(file) != record["sha256"]:
            raise ValueError(f"{meta} checksum mismatch")
    raw = pd.read_csv(p, index_col=0, parse_dates=True)[TICKERS].loc[
        START : pd.Timestamp(END) - pd.Timedelta(days=1)
    ]
    if (
        raw.index.has_duplicates
        or not raw.index.is_monotonic_increasing
        or (raw <= 0).any().any()
    ):
        raise ValueError("Invalid price index or nonpositive prices")
    prices = raw.dropna(how="any")
    simple = prices.pct_change(fill_method=None).dropna()
    logs = np.log(prices / prices.shift()).dropna()
    rfraw = pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
    rfraw = pd.to_numeric(rfraw, errors="coerce").dropna()
    # Only strictly earlier rate observations, no same-date close or backfill.
    daily = rfraw.reindex(rfraw.index.union(simple.index)).sort_index().ffill()
    lag = daily.shift(1).reindex(simple.index)
    if lag.isna().any():
        raise ValueError("No strictly prior FRED rate for first return")
    # Convert assumed 91-day bank-discount bill to annual simple investment yield.
    investment = (365 / 360) * (lag / 100) / (1 - (lag / 100) * 91 / 360)
    rf = (1 + investment) ** (1 / 252) - 1
    rf.name = "daily_rf"
    flags = []
    train = logs.loc[:TRAIN_END]
    for ticker in TICKERS:
        x = logs[ticker]
        sd = train[ticker].std()
        for date, value in x.items():
            if abs(value) > 0.10 or abs(value) > 8 * sd:
                flags.append(
                    dict(
                        date=str(date.date()),
                        ticker=ticker,
                        type="large move retained",
                        value=value,
                    )
                )
            if value == 0:
                flags.append(
                    dict(
                        date=str(date.date()),
                        ticker=ticker,
                        type="flat price retained",
                        value=value,
                    )
                )
        rolling = x.rolling(63).std()
        baseline = rolling.shift(63)
        structural = (rolling / baseline > 2.5) & (
            rolling.shift() / baseline.shift() <= 2.5
        )
        for date in x.index[structural.fillna(False)]:
            flags.append(
                dict(
                    date=str(date.date()),
                    ticker=ticker,
                    type="volatility break flag retained",
                    value=float(rolling[date] / baseline[date]),
                )
            )
    adf = []
    for ticker in TICKERS:
        a = adfuller(
            train[ticker], maxlag=20, regression="c", autolag="AIC", result_object=False
        )
        adf.append(
            dict(
                ticker=ticker,
                statistic=a[0],
                p_value=a[1],
                lags=a[2],
                n=a[3],
                sample="training log returns",
            )
        )
    audit = dict(
        n_prices=len(prices),
        n_returns=len(simple),
        start=str(prices.index[0].date()),
        end=str(prices.index[-1].date()),
        missing=raw.isna().sum().to_dict(),
        dropped_rows=int(raw.isna().any(axis=1).sum()),
        max_abs_log_return=logs.abs().max().to_dict(),
        flags=len(flags),
        training_end=TRAIN_END,
        common_calendar_note="Intersection of valid Yahoo dates; no independent exchange-calendar verification",
        fred_note="Strictly lagged current-vintage DTB3, not a vintage-correct forecast dataset",
    )
    pd.DataFrame(flags, columns=["date", "ticker", "type", "value"]).to_csv(
        ROOT / "outputs/tables/data_flags.csv", index=False
    )
    pd.DataFrame(adf).to_csv(ROOT / "outputs/tables/adf.csv", index=False)
    pd.DataFrame(
        [
            dict(
                ticker=t,
                first_valid=str(raw[t].first_valid_index().date()),
                last_valid=str(raw[t].last_valid_index().date()),
                n_valid=int(raw[t].notna().sum()),
                missing=int(raw[t].isna().sum()),
            )
            for t in TICKERS
        ]
    ).to_csv(ROOT / "outputs/tables/coverage.csv", index=False)
    (ROOT / "outputs/results/data_audit.json").write_text(json.dumps(audit, indent=2))
    simple.to_csv(ROOT / "outputs/tables/simple_returns.csv")
    logs.to_csv(ROOT / "outputs/tables/log_returns.csv")
    rf.to_csv(ROOT / "outputs/tables/risk_free.csv")
    return prices, simple, logs, rf, audit
