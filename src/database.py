"""Versioned SQL persistence for approved research inputs and saved scenarios.

PostgreSQL is used in hosting; SQLite is supported for isolated local tests.
Database configuration never changes the fixed research design or recalculates it.
"""

import hashlib
import io
import json
import os
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sqlalchemy import (
    Column, Date, Float, ForeignKeyConstraint, Integer, MetaData, String, Table,
    Text, Index, create_engine, func, insert, select, text,
)
from sqlalchemy.exc import SQLAlchemyError

from .config import ROOT, TICKERS
from .portfolio import validate_weights


class DatabaseUnavailable(RuntimeError):
    """Safe application error that never contains a connection string."""


def configured_url():
    return os.environ.get("AEGIS_DATABASE_URL") or os.environ.get("DATABASE_URL")


def evidence_files(root=ROOT):
    return [
        root / "data/snapshots/adjusted_prices.csv",
        root / "data/snapshots/DTB3.csv",
        *sorted((root / "data/metadata").glob("*.json")),
        *sorted((root / "outputs/tables").glob("*.csv")),
        root / "outputs/results/summary.json",
    ]


def research_version(root=ROOT):
    digest = hashlib.sha256()
    for path in evidence_files(root):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


class ResearchStore:
    def __init__(self, url):
        if url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        self.postgres = url.startswith("postgresql+psycopg://")
        if not (self.postgres or url.startswith("sqlite:///")):
            raise ValueError("Use a PostgreSQL connection URL or a local SQLite file.")
        options = dict(pool_pre_ping=True, hide_parameters=True)
        if self.postgres:
            options.update(pool_size=2, max_overflow=0, pool_recycle=300,
                           connect_args={"sslmode": "require", "connect_timeout": 15,
                                         "prepare_threshold": None})
        try:
            self.engine = create_engine(url, **options)
        except (SQLAlchemyError, ValueError):
            raise DatabaseUnavailable("The database connection configuration is invalid.") from None
        schema = "aegis" if self.postgres else None
        self.meta = MetaData(schema=schema)
        self.datasets = Table(
            "research_datasets", self.meta,
            Column("version", String(64), primary_key=True),
            Column("created_at", String(40), nullable=False),
            Column("source", String(120), nullable=False),
            Column("price_count", Integer, nullable=False),
            Column("start_date", Date, nullable=False),
            Column("end_date", Date, nullable=False),
        )
        reference = f"{schema}.research_datasets.version" if schema else "research_datasets.version"
        self.prices = Table(
            "adjusted_prices", self.meta,
            Column("version", String(64), primary_key=True),
            Column("date", Date, primary_key=True),
            Column("ticker", String(8), primary_key=True),
            Column("adjusted_close", Float, nullable=False),
            ForeignKeyConstraint(["version"], [reference]),
        )
        self.artifacts = Table(
            "research_artifacts", self.meta,
            Column("version", String(64), primary_key=True),
            Column("name", String(160), primary_key=True),
            Column("sha256", String(64), nullable=False),
            Column("content", Text, nullable=False),
            ForeignKeyConstraint(["version"], [reference]),
        )
        self.scenarios = Table(
            "saved_allocations", self.meta,
            Column("id", String(36), primary_key=True),
            Column("version", String(64), nullable=False),
            Column("name", String(80), nullable=False),
            Column("weights_json", Text, nullable=False),
            Column("created_at", String(40), nullable=False),
            ForeignKeyConstraint(["version"], [reference]),
        )
        Index("ix_saved_allocations_version_created", self.scenarios.c.version, self.scenarios.c.created_at)

    def seed(self, root=ROOT):
        """Atomic, idempotent import; a new input/output hash creates a new version."""
        version = research_version(root)
        prices = pd.read_csv(root / "data/snapshots/adjusted_prices.csv", index_col=0, parse_dates=True)[TICKERS]
        if prices.isna().any().any() or (prices <= 0).any().any():
            raise ValueError("Database import requires complete positive adjusted prices.")
        for filename, metadata in [("adjusted_prices.csv", "prices.json"), ("DTB3.csv", "fred.json")]:
            expected = json.loads((root / "data/metadata" / metadata).read_text(encoding="utf-8-sig"))["sha256"]
            if hashlib.sha256((root / "data/snapshots" / filename).read_bytes()).hexdigest() != expected:
                raise ValueError("Snapshot checksum mismatch; database import refused.")
        try:
            with self.engine.begin() as connection:
                if self.postgres:
                    # Serialize competing starts, including schema creation and seed.
                    connection.execute(text("SELECT pg_advisory_xact_lock(17423001)"))
                    connection.execute(text("CREATE SCHEMA IF NOT EXISTS aegis"))
                self.meta.create_all(connection)
                if self.postgres:
                    connection.execute(text("REVOKE ALL ON SCHEMA aegis FROM PUBLIC"))
                    for table_name in ("research_datasets", "adjusted_prices", "research_artifacts", "saved_allocations"):
                        connection.execute(text(f"ALTER TABLE aegis.{table_name} ENABLE ROW LEVEL SECURITY"))
                if connection.execute(select(self.datasets.c.version).where(self.datasets.c.version == version)).first():
                    return version
                connection.execute(insert(self.datasets), dict(
                    version=version, created_at=datetime.now(timezone.utc).isoformat(),
                    source="Yahoo Finance via yfinance; FRED DTB3", price_count=len(prices) * len(TICKERS),
                    start_date=prices.index.min().date(), end_date=prices.index.max().date(),
                ))
                records = [dict(version=version, date=date.date(), ticker=ticker, adjusted_close=float(row[ticker]))
                           for date, row in prices.iterrows() for ticker in TICKERS]
                for start in range(0, len(records), 1000):
                    connection.execute(insert(self.prices), records[start:start + 1000])
                for path in evidence_files(root):
                    raw = path.read_bytes()
                    connection.execute(insert(self.artifacts), dict(
                        version=version, name=path.relative_to(root).as_posix(),
                        sha256=hashlib.sha256(raw).hexdigest(), content=raw.decode("utf-8"),
                    ))
                return version
        except SQLAlchemyError:
            raise DatabaseUnavailable("Persistent database initialization failed. Check the server-side database configuration.") from None

    def content(self, version, name):
        try:
            with self.engine.connect() as connection:
                row = connection.execute(select(self.artifacts.c.content, self.artifacts.c.sha256).where(
                    self.artifacts.c.version == version, self.artifacts.c.name == name)).first()
            if row is None:
                raise DatabaseUnavailable("The deployed research version is missing. Run the database bootstrap for this release.")
            if hashlib.sha256(row.content.encode("utf-8")).hexdigest() != row.sha256:
                raise DatabaseUnavailable("Database evidence checksum mismatch. Restore the verified research version.")
            return row.content
        except SQLAlchemyError:
            raise DatabaseUnavailable("Persistent database is unavailable. Check the server-side connection and database status.") from None

    def table(self, version, name):
        return pd.read_csv(io.StringIO(self.content(version, "outputs/tables/" + name + ".csv")))

    def load_prices(self, version):
        try:
            with self.engine.connect() as connection:
                rows = connection.execute(select(self.prices.c.date, self.prices.c.ticker, self.prices.c.adjusted_close).where(
                    self.prices.c.version == version).order_by(self.prices.c.date, self.prices.c.ticker)).all()
            if not rows:
                raise DatabaseUnavailable("No adjusted prices exist for this research version.")
            frame = pd.DataFrame(rows, columns=["date", "ticker", "adjusted_close"]).pivot(index="date", columns="ticker", values="adjusted_close")
            frame.index = pd.to_datetime(frame.index)
            frame.columns.name = None
            frame = frame[TICKERS]
            expected = pd.read_csv(io.StringIO(self.content(version, "data/snapshots/adjusted_prices.csv")), index_col=0, parse_dates=True)[TICKERS]
            try:
                pd.testing.assert_frame_equal(frame, expected, check_names=False, check_exact=True)
            except AssertionError:
                raise DatabaseUnavailable("Database prices differ from the verified source snapshot.") from None
            return frame
        except SQLAlchemyError:
            raise DatabaseUnavailable("Persistent price database is unavailable.") from None

    def status(self, version):
        try:
            with self.engine.connect() as connection:
                count = connection.scalar(select(func.count()).select_from(self.prices).where(self.prices.c.version == version))
                scenarios = connection.scalar(select(func.count()).select_from(self.scenarios).where(self.scenarios.c.version == version))
            return dict(backend="PostgreSQL" if self.postgres else "SQLite", price_rows=count, saved_allocations=scenarios, version=version)
        except SQLAlchemyError:
            raise DatabaseUnavailable("Persistent database status is unavailable.") from None

    def save_allocation(self, version, name, weights):
        weights = validate_weights(weights)
        name = str(name).strip()
        if not name or len(name) > 80:
            raise ValueError("Use an allocation name between 1 and 80 characters.")
        row = dict(id=str(uuid.uuid4()), version=version, name=name,
                   weights_json=json.dumps(dict(zip(TICKERS, weights.tolist())), allow_nan=False),
                   created_at=datetime.now(timezone.utc).isoformat())
        try:
            with self.engine.begin() as connection:
                connection.execute(insert(self.scenarios), row)
            return row["id"]
        except SQLAlchemyError:
            raise DatabaseUnavailable("The allocation could not be saved to the database.") from None

    def list_allocations(self, version):
        try:
            with self.engine.connect() as connection:
                rows = connection.execute(select(self.scenarios).where(self.scenarios.c.version == version).order_by(self.scenarios.c.created_at.desc()).limit(100)).mappings().all()
            return [dict(row) for row in rows]
        except SQLAlchemyError:
            raise DatabaseUnavailable("Saved allocations could not be read from the database.") from None


@lru_cache(maxsize=1)
def active_store():
    url = configured_url()
    return ResearchStore(url) if url else None


def release_table(name):
    store = active_store()
    if store is None:
        return pd.read_csv(ROOT / f"outputs/tables/{name}.csv")
    return store.table(research_version(), name)
