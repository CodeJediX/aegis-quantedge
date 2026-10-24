"""Exercise authorized saves and cross-session loads using a real isolated SQL DB."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from src.database import ResearchStore, active_store, research_version


def main():
    previous = {key: os.environ.get(key) for key in ("AEGIS_DATABASE_URL", "AEGIS_ADMIN_KEY", "AEGIS_REQUIRE_DATABASE")}
    try:
        with tempfile.TemporaryDirectory() as temporary:
            url = "sqlite:///" + (Path(temporary) / "research.sqlite3").as_posix()
            os.environ.update(AEGIS_DATABASE_URL=url, AEGIS_ADMIN_KEY="isolated-test-key", AEGIS_REQUIRE_DATABASE="1")
            active_store.cache_clear()
            store = active_store()
            version = store.seed()
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
            app.selectbox(key="page").set_value("Portfolio Decision Lab").run()
            assert not app.exception
            app.text_input(key="saved_name").set_value("SQL persistence verification")
            app.text_input(key="saved_admin_key").set_value("wrong-key")
            app.button(key="FormSubmitter:persist_allocation-Save current allocation to database").click().run()
            assert len(app.error) > 0
            assert store.status(version)["saved_allocations"] == 0
            app.text_input(key="saved_admin_key").set_value("isolated-test-key")
            app.button(key="FormSubmitter:persist_allocation-Save current allocation to database").click().run()
            assert not app.exception
            assert store.status(version)["saved_allocations"] == 1
            second = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
            second.selectbox(key="page").set_value("Portfolio Decision Lab").run()
            assert not second.exception
            second.button(key="load_saved").click().run()
            assert not second.exception
            assert abs(sum(second.session_state["custom"]) - 1) < 1e-10
            assert second.selectbox(key="saved_allocation").value == store.list_allocations(version)[0]["id"]
            store.engine.dispose()
            active_store.cache_clear()
            print("SQL UI checks passed: unauthorized write rejected, authorized write persisted, fresh session loaded allocation")
    finally:
        active_store.cache_clear()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    main()
