"""Import hashed genuine research evidence into the configured SQL database."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.database import active_store, DatabaseUnavailable


def main():
    store = active_store()
    if store is None:
        raise SystemExit("Set AEGIS_DATABASE_URL in the hosting secret settings before database bootstrap.")
    try:
        version = store.seed()
        print(json.dumps(store.status(version), indent=2))
    except DatabaseUnavailable as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
