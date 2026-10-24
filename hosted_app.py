"""Free Streamlit Community Cloud entry point with a genuine read-only SQL store."""
import os
import runpy
import tempfile
from pathlib import Path

if not (os.environ.get("AEGIS_DATABASE_URL") or os.environ.get("DATABASE_URL")):
    database_file = Path(tempfile.gettempdir()) / "aegis-research.sqlite3"
    os.environ["AEGIS_DATABASE_URL"] = "sqlite:///" + database_file.as_posix()
os.environ.setdefault("AEGIS_REQUIRE_DATABASE", "1")
os.environ.setdefault("AEGIS_READONLY_DATABASE", "1")

runpy.run_path(str(Path(__file__).resolve().with_name("app.py")), run_name="__main__")
