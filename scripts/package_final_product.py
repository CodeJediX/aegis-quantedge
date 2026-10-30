"""Package the four requested submission items and the required AI disclosure."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.package_submission import main as package_source


def main():
    package_source()
    source=ROOT.parent/"QuantEdge_1.0_Final_Submission.zip"
    technical=ROOT/"reports/Current_Technical_Report.pdf"
    tear=ROOT/"reports/Current_Investment_Tear_Sheet.pdf"
    ai=ROOT/"reports/AI_Usage_Details.pdf"
    assert 7<=len(PdfReader(technical).pages)<=15
    assert len(PdfReader(tear).pages)==1
    assert len(PdfReader(ai).pages)==2
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    readme="""# QuantumX AEGIS - submission package

Product release: 30 October 2026. The four requested deliverables are mapped below.

1. SOURCE / GITHUB
   Source_Code.zip contains the clean, documented repository, authentic frozen
   inputs, numerical outputs, tests and reproduction scripts.
   Public source: https://github.com/CodeJediX/aegis-quantedge

2. STREAMLIT APPLICATION
   Live app: https://quantumx-aegis.streamlit.app/
   Extract Source_Code.zip, open its QuantEdge_1.0_Final_Submission directory
   and use Python 3.11. Install dependencies with:
       python -m pip install -r requirements.txt
   Launch the app with ONE command:
       streamlit run app.py
   Optional isolated-environment setup is in the repository README.
   No API key, paid service or market-data download is needed to launch.

3. TECHNICAL REPORT
   Technical_Report.pdf: 15 pages. Methodology, data/cleaning, results and explicit
   assumptions/limitations; original 13-page study plus two current product pages.

4. EXECUTIVE TEAR SHEET
   Executive_Tear_Sheet.pdf: one page. Reference allocation, performance, VaR/ES,
   failed-limit rationale, recommendation and required action before funding.

AI_Usage_Details.pdf is included to satisfy the brief's material AI disclosure.
The source also retains earlier Word/presentation/mobile materials as optional
supporting files; they are not prerequisites for running the Streamlit app.

NEW PRODUCT FEATURES
- Side-by-side 90/95/99 risk comparison and identified CSV export.
- Dashboard risk follows selected confidence/method; historical returns stay fixed.
- Proposed limits persist across workspaces and generated reports.
- Reference reset restores the original analysis while retaining saved profiles.
- Simplified downloads and grouped evidence; all mandatory methods remain.

IMPORTANT INTERPRETATION
Data are frozen through 2026-09-30. Default reference remains REVISE with three
original-limit failures. Independent human-team investment review is PENDING.
Automated tests do not replace that review or imply a capital guarantee.
No AI-detector/plagiarism-database clearance is claimed. The team must review,
substantiate and defend the work before submission under the brief's AI rules.
Free hosting uses real read-only SQLite; no external PostgreSQL provisioning is
claimed. No payment details or paid resources were used.

CHECKS
See documentation/Testing_and_Validation.md in the source for 53 numerical /
integration / database / state tests, 28 base and 129 expanded interface checks,
9 product-flow checks and 9 typed-guide checks. The source manifest inventories
files with SHA256 checksums. DELIVERY_MANIFEST.json verifies this outer package.
"""
    entries={"README.md":readme.encode(),"Source_Code.zip":source.read_bytes(),
             "Technical_Report.pdf":technical.read_bytes(),"Executive_Tear_Sheet.pdf":tear.read_bytes(),
             "AI_Usage_Details.pdf":ai.read_bytes(),
             "LINKS.txt":b"Website: https://quantumx-aegis.streamlit.app/\nGitHub: https://github.com/CodeJediX/aegis-quantedge\n"}
    manifest={"release_date":"2026-10-30","source_revision":revision,"human_approval":"PENDING",
              "files":[{"file":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()} for name,data in entries.items()]}
    entries["DELIVERY_MANIFEST.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
    target=ROOT.parent/"QuantumX_AEGIS_Submission_2026-10-30.zip"
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in entries.items():archive.writestr(name,data)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for row in manifest["files"]:
            data=archive.read(row["file"])
            assert len(data)==row["bytes"] and hashlib.sha256(data).hexdigest()==row["sha256"]
    print(json.dumps({"zip":str(target),"bytes":target.stat().st_size,"PDF_pages":[15,1,2],"files":len(entries)},indent=2))


if __name__=="__main__":main()
