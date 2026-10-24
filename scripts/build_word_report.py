"""Optional editable Word companion from the exact report flowables.

Requires python-docx in addition to the mandatory application dependencies.
No calculations or report content are rewritten by this format conversion.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.platypus import Paragraph, Table, Image, PageBreak, Spacer
from src import reporting


def clean(value):
    value = re.sub(r"<br\s*/?>", "\n", str(value), flags=re.I)
    return html.unescape(re.sub(r"<[^>]+>", "", value))


def main():
    captured = {}
    original = reporting.SimpleDocTemplate.build

    def capture(template, story, **kwargs):
        captured[Path(template.filename).name] = list(story)

    reporting.SimpleDocTemplate.build = capture
    try:
        reporting.build_reports(json.loads((ROOT / "outputs/results/summary.json").read_text(encoding="utf-8")))
    finally:
        reporting.SimpleDocTemplate.build = original

    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Pt(595.28), Pt(841.89)
    section.left_margin = section.right_margin = Pt(60)
    section.top_margin, section.bottom_margin = Pt(50), Pt(52)
    normal = document.styles["Normal"]
    normal.font.name, normal.font.size = "Arial", Pt(10)
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(8)
    for name, size in [("Title", 32), ("Heading 1", 21), ("Heading 2", 11.5)]:
        style = document.styles[name]
        style.font.name, style.font.size = "Arial", Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_after = Pt(9)
        for border in list(style.element.iter(qn("w:pBdr"))):
            border.getparent().remove(border)
    document.core_properties.title = "AEGIS capital preservation research"
    document.core_properties.author = "Quantum-X; AI-assisted proposal"
    footer = section.footer.paragraphs[0]
    footer.text = "QUANTUM-X / AEGIS    PROPOSAL PENDING TEAM REVIEW    "
    footer.runs[0].font.size = Pt(8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)

    for flow in captured["Technical_Report.pdf"]:
        if isinstance(flow, PageBreak):
            document.add_page_break()
        elif isinstance(flow, Paragraph):
            name = flow.style.name
            style = {"Cover": "Title", "H1": "Heading 1", "H2": "Heading 2"}.get(name, "Normal")
            text = clean(flow.text)
            if style in ("Heading 1", "Heading 2", "Title"):
                text = re.sub(r"[^\w\s]", " ", text.replace("Quantum-X", "QUANTUMXBRAND"))
                text = re.sub(r"[ \t]+", " ", text).strip()
                text = text.replace("QUANTUMXBRAND", "Quantum-X")
            p = document.add_paragraph(text, style)
            if name in ("Small", "Caption"):
                for run in p.runs:
                    run.font.size = Pt(8.3)
            p.paragraph_format.keep_together = True
        elif isinstance(flow, Table):
            table = document.add_table(rows=len(flow._cellvalues), cols=len(flow._cellvalues[0]))
            table.alignment = WD_TABLE_ALIGNMENT.LEFT
            table.autofit = False
            for j, width in enumerate(flow._colWidths):
                table.columns[j].width = Pt(width)
            borders = OxmlElement("w:tblBorders")
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
                tag = OxmlElement("w:" + edge)
                for key, val in {"val": "single", "sz": "4", "color": "D9D9D9"}.items():
                    tag.set(qn("w:" + key), val)
                borders.append(tag)
            table._tbl.tblPr.append(borders)
            for i, values in enumerate(flow._cellvalues):
                row = table.rows[i]
                if i == 0:
                    row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
                for j, value in enumerate(values):
                    cell = row.cells[j]
                    cell.width = Pt(flow._colWidths[j])
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    cell.text = clean(value.text if hasattr(value, "text") else value)
                    tcpr = cell._tc.get_or_add_tcPr()
                    shade = OxmlElement("w:shd")
                    shade.set(qn("w:fill"), "E5F1F1" if i == 0 else ("F4F7F9" if i % 2 == 0 else "FFFFFF"))
                    tcpr.append(shade)
                    margins = OxmlElement("w:tcMar")
                    for side, val in [("top", "70"), ("bottom", "70"), ("left", "100"), ("right", "100")]:
                        tag = OxmlElement("w:" + side)
                        tag.set(qn("w:w"), val)
                        tag.set(qn("w:type"), "dxa")
                        margins.append(tag)
                    tcpr.append(margins)
                    for p in cell.paragraphs:
                        p.paragraph_format.space_after = Pt(0)
                        p.paragraph_format.line_spacing = 1.05
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 or len(cell.text) > 40 else WD_ALIGN_PARAGRAPH.CENTER
                        for run in p.runs:
                            run.font.size = Pt(8.3)
                            run.bold = i == 0
        elif isinstance(flow, Image):
            p = document.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(str(flow.filename), width=Pt(flow.drawWidth), height=Pt(flow.drawHeight))
        elif isinstance(flow, Spacer):
            p = document.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = Pt(flow.height)
            p.add_run(" ").font.size = Pt(1)

    target = ROOT / "reports/Technical_Report.docx"
    document.save(target)
    print(target)


if __name__ == "__main__":
    main()
