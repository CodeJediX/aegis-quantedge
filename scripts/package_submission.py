"""Build one clean ZIP with a self-checking file inventory; excludes local-only state."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    # A locally extracted copy must never be repackaged inside itself.
    if rel.parts[0] == ROOT.name:
        return False
    if any(
        p in {"__pycache__", ".git", ".venv", "venv", ".deck_build"} for p in rel.parts
    ):
        return False
    if path.suffix in {".pyc", ".log", ".db", ".sqlite", ".sqlite3", ".jks", ".keystore", ".class", ".dex", ".idsig"} or path.name in {".env", "secrets.toml"}:
        return False
    if path.name.startswith(".env.") and path.name != ".env.example":
        return False
    if path.name.endswith((".db-wal", ".db-shm", ".sqlite3-wal", ".sqlite3-shm")):
        return False
    return path.is_file()


def main() -> None:
    files = sorted(
        p for p in ROOT.rglob("*") if include(p) and p.name != "SUBMISSION_MANIFEST.md"
    )
    lines = [
        "# Submission manifest",
        "",
        "AEGIS / Quantum-X | QuantEdge 1.0 Final Challenge | current release 26 October 2026",
        "",
        "Data cutoff: 2026-09-30. Current technical report 15 pages, investment tear sheet 1 page, AI usage details 2 pages and a signed native Android APK. Original 13-page report/Word companion, memo and 12-slide pitch are preserved. All five technical layers and twelve workspaces are implemented.",
        "Selected-portfolio exports are generated separately in the app: technical PDF 7 pages, tear sheet 1, committee memo 1, identified CSV/ZIP and provenance. The current default automated recommendation is REVISE with three failed proposed policy checks. Verification: 49 numerical/integration/database tests, 28 base and 129 expanded interface checks, 9 branding/chat checks, 222 Java/Python comparisons and 24 signed-APK emulator runtime checks. Native model scope is explicitly smaller than website scope; see mobile/README.md.",
        "",
        "Live application: https://quantumx-aegis.streamlit.app/ (free Streamlit Community Cloud). Public source: https://github.com/CodeJediX/aegis-quantedge. Hosting uses read-only SQLite rebuilt from verified research snapshots; shared saves are disabled. **Pending human actions:** independent team validation and the final investment decision. No human approval is claimed.",
        "",
        "The application runs locally with one command after dependency installation: `streamlit run app.py`. Numerical/PDF report reproduction: `python run.py --reproduce`. Optional pitch authoring uses a separate Node artifact-tool runtime; the provided PPTX/PDF is ready to open.",
        "",
        "All CSV/JSON outputs and figures are genuine executed results. Synthetic data appear only in numerical unit-test fixtures; the hypothetical scenario is explicitly an assumed shock. No model result is invented.",
        "",
        "Virtual environments, secrets, intermediate deck builds and external QA render directories are excluded. This inventory omits its own checksum to avoid self-reference.",
        "",
        "| File | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for p in files:
        lines.append(
            f"| {p.relative_to(ROOT).as_posix()} | {p.stat().st_size} | {hashlib.sha256(p.read_bytes()).hexdigest()} |"
        )
    (ROOT / "SUBMISSION_MANIFEST.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    target = ROOT.parent / "QuantEdge_1.0_Final_Submission.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for p in files + [ROOT / "SUBMISSION_MANIFEST.md"]:
            archive.write(p, Path(ROOT.name) / p.relative_to(ROOT))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive CRC failed")
        names = archive.namelist()
        required = [
            "README.md",
            "requirements.txt",
            "app.py",
            "run.py",
            "reports/Technical_Report.pdf",
            "reports/Technical_Report.docx",
            "reports/Current_Technical_Report.pdf",
            "reports/Current_Investment_Tear_Sheet.pdf",
            "reports/AI_Usage_Details.pdf",
            "assets/quantumx_logo.png",
            "mobile/README.md",
            "mobile/releases/QuantumX_AEGIS_1.0.0.apk",
            "mobile/releases/APK_MANIFEST.json",
            "reports/Executive_Tear_Sheet.pdf",
            "reports/Investment_Committee_Memo.pdf",
            "presentation/Final_Pitch.pptx",
            "presentation/Final_Pitch.pdf",
            "documentation/AI_Disclosure.md",
            "documentation/Requirements_Traceability.md",
        ]
        if not all(f"{ROOT.name}/{p}" in names for p in required):
            raise ValueError("Missing required deliverable")
    if target.stat().st_size > 25_000_000:
        raise ValueError("Archive unexpectedly exceeds25 MB internal target")
    print(
        json.dumps(
            dict(
                zip=str(target),
                files=len(names),
                bytes=target.stat().st_size,
                MB=target.stat().st_size / 1e6,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
