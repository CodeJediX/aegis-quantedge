"""Meaningful SQL persistence checks against the actual versioned research inputs."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError

from src.config import ROOT, TICKERS
from src.database import ResearchStore, DatabaseUnavailable


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.url = "sqlite:///" + (Path(self.temporary.name) / "research.sqlite3").as_posix()
        self.store = ResearchStore(self.url)
        self.version = self.store.seed()

    def tearDown(self):
        self.store.engine.dispose()
        self.temporary.cleanup()

    def test_idempotent_seed_and_genuine_price_roundtrip(self):
        self.assertEqual(self.version, self.store.seed())
        expected = pd.read_csv(ROOT / "data/snapshots/adjusted_prices.csv", index_col=0, parse_dates=True)[TICKERS]
        pd.testing.assert_frame_equal(self.store.load_prices(self.version), expected, check_names=False, check_exact=True)
        self.assertEqual(self.store.status(self.version)["price_rows"], len(expected) * 7)
        with self.store.engine.connect() as connection:
            self.assertEqual(connection.scalar(select(func.count()).select_from(self.store.datasets)), 1)

    def test_evidence_roundtrip(self):
        raw = (ROOT / "outputs/results/summary.json").read_bytes().decode("utf-8")
        self.assertEqual(self.store.content(self.version, "outputs/results/summary.json"), raw)
        pd.testing.assert_frame_equal(self.store.table(self.version, "kpis"), pd.read_csv(ROOT / "outputs/tables/kpis.csv"))

    def test_saved_allocation_survives_new_connection(self):
        weights = np.array([.12, 0, 0, .70, .10, 0, .08])
        label = "Committee's proposal '; DROP TABLE adjusted_prices; --"
        identity = self.store.save_allocation(self.version, label, weights)
        reopened = ResearchStore(self.url)
        try:
            records = reopened.list_allocations(self.version)
            self.assertEqual(records[0]["id"], identity)
            self.assertEqual(records[0]["name"], label)
            self.assertEqual(json.loads(records[0]["weights_json"])["AGG"], .70)
            self.assertEqual(reopened.status(self.version)["price_rows"], 38290)
        finally:
            reopened.engine.dispose()

    def test_invalid_allocations_do_not_persist(self):
        with self.assertRaises(ValueError):
            self.store.save_allocation(self.version, "bad", np.ones(7))
        with self.assertRaises(ValueError):
            self.store.save_allocation(self.version, " ", np.ones(7) / 7)
        self.assertEqual(self.store.list_allocations(self.version), [])

    def test_readonly_deployment_cannot_save(self):
        with patch.dict(os.environ, {"AEGIS_READONLY_DATABASE": "1"}):
            with self.assertRaisesRegex(ValueError, "read-only"):
                self.store.save_allocation(self.version, "Not allowed", np.ones(7) / 7)
        self.assertEqual(self.store.list_allocations(self.version), [])

    def test_corrupt_evidence_is_rejected(self):
        with self.store.engine.begin() as connection:
            connection.execute(update(self.store.artifacts).where(self.store.artifacts.c.name == "outputs/results/summary.json").values(content="{}"))
        with self.assertRaisesRegex(DatabaseUnavailable, "checksum"):
            self.store.content(self.version, "outputs/results/summary.json")

    def test_corrupt_price_rows_are_rejected(self):
        with self.store.engine.begin() as connection:
            connection.execute(update(self.store.prices).where(self.store.prices.c.ticker == "AGG").values(adjusted_close=1.0))
        with self.assertRaisesRegex(DatabaseUnavailable, "differ"):
            self.store.load_prices(self.version)

    def test_connection_failure_does_not_disclose_secrets(self):
        with patch.object(self.store.engine, "connect", side_effect=SQLAlchemyError("postgresql://secret-password@private-host")):
            with self.assertRaises(DatabaseUnavailable) as caught:
                self.store.status(self.version)
        self.assertNotIn("secret-password", str(caught.exception))
        self.assertNotIn("private-host", str(caught.exception))

    def test_unknown_version_does_not_fallback(self):
        with self.assertRaisesRegex(DatabaseUnavailable, "missing"):
            self.store.content("0" * 64, "outputs/results/summary.json")


if __name__ == "__main__":
    unittest.main()
