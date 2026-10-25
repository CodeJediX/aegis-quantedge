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
    if path.suffix in {".pyc", ".log", ".db", ".sqlite", ".sqlite3"} or path.name in {".env", "secrets.toml"}:
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
        "AEGIS / Quantum-X | QuantEdge 1.0 Final Challenge | prepared 24 October 2026; release verified 25 October 2026",
        "",
        "Data cutoff: 2026-09-30. Technical report 13 pages plus editable Word companion; tear sheet 1; memo 1; pitch 12 slides and 660-second rehearsal target. All five technical layers and twelve workspaces are implemented.",
        "",
        "Live application: https://quantumx-aegis.streamlit.app/ (Streamlit Community Cloud; verified 25 October 2026). Public source: https://github.com/CodeJediX/aegis-quantedge. Hosting uses read-only SQLite rebuilt from verified research snapshots; shared saves are disabled. **Pending human actions:** independent team validation and the final investment decision. No human approval is claimed.",
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
