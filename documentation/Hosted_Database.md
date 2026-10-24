# Hosted application and SQL database

The application retains Python and Streamlit. The no-payment Render configuration uses a real SQLite research database, initialized from the verified release snapshots on every new container. Shared allocation saving is disabled with `AEGIS_READONLY_DATABASE=1` because free container storage is temporary. All required research pages and current-session allocation experiments work in this mode. A separate Supabase PostgreSQL database is supported as an optional durable store; its provisioning is not claimed. No live deployment is claimed until verified against the actual provider.

## Data stored

- `aegis.research_datasets`: immutable release fingerprint, source, date coverage and record count.
- `aegis.adjusted_prices`: 38,290 genuine adjusted-price records, keyed by release, date and approved ticker.
- `aegis.research_artifacts`: hashed source snapshots, provenance, calculated CSV tables and summary JSON for that release.
- `aegis.saved_allocations`: named proposals and their weights, linked to the exact research release. These are shared research records, not personal accounts, actual positions or human approvals.

When SQL is configured, the app reads prices and research tables from the database. It checks artifact hashes and verifies normalized prices against the hashed source snapshot. It does not silently substitute local files on a database outage. Offline use without a configured URL remains available for reproducibility.

## Hosting configuration

Set these in Render's server-side environment settings:

| Variable | Purpose |
|---|---|
| `AEGIS_DATABASE_URL` | Supabase PostgreSQL connection URL. Copy the actual session-pooler host from the project's Connect dialog for IPv4 access. Do not infer the host. |
| `AEGIS_ADMIN_KEY` | Long random administrator key. Render Blueprint generates it. Required only to save shared allocation records. |
| `AEGIS_REQUIRE_DATABASE` | `1` on the hosted service, so missing configuration blocks startup. |
| `AEGIS_READONLY_DATABASE` | `1` for free SQLite hosting. Blocks shared saves and explains temporary storage in the app. |

For the no-payment deployment, `AEGIS_DATABASE_URL=sqlite:////tmp/aegis-research.sqlite3` is a nonsecret local SQL URL, not a PostgreSQL credential. Leave `AEGIS_ADMIN_KEY` unset. Select Render's manual **Web Service** setup and the **Free / $0 per month** compute plan. Render's Blueprint creation requested payment information on this account and was cancelled; no card was entered. The manual configuration uses the build/start commands and environment settings in `render.yaml`. PostgreSQL-specific instructions below apply only when an external database is configured.

PostgreSQL connections use TLS, a small connection pool, finite connection timeout and no prepared statements. Credentials stay server-side, outside the Git repository and ZIP. The `aegis` schema is separate from the default public Data API schema. Bootstrap revokes schema access from PUBLIC and enables row-level security as defense in depth. The bootstrap database role must own this schema; no anonymous browser role receives database access. Use a dedicated database project for this application.

Startup runs `python scripts/bootstrap_database.py` before Streamlit starts. Import is transactional, uses a PostgreSQL advisory lock, and is idempotent for the same release. A changed source/output fingerprint creates a separate research version. Existing releases and saved proposals are retained. Bootstrap does not redownload or invent market data. Streamlit binds to `0.0.0.0` and Render's assigned `$PORT`. The health endpoint is `/_stcore/health`.

## Saved proposals

Open Portfolio Decision Lab, expand Saved research allocations, enter a name and the team administrator key, and save the current allocation. Only someone with that server-configured key can write. Viewers can load the most recent100 shared proposals for the current release into the Custom allocation view. This never rewrites saved validation forecasts. Do not store confidential holdings or personal information in shared research labels.

## Deployment verification

Before handing off a live URL, confirm the provider deployment is live, the HTTPS health endpoint succeeds, the browser renders the application, the database contains the genuine research records, and a saved test proposal survives a new database connection. A localhost address or a deployment-configuration link is not a hosted app URL.

Free hosting can sleep when idle, and database providers impose free-tier quotas. Do not enable paid upgrades without the team's decision. Render's free local filesystem is ephemeral; it is unsuitable for the production SQL store. Provider plan details should be rechecked when deploying.

References: [Render free services](https://render.com/docs/free), [Render Blueprint specification](https://render.com/docs/blueprint-spec), [Supabase PostgreSQL connections](https://supabase.com/docs/guides/database/connecting-to-postgres), [SQLAlchemy psycopg dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg).
