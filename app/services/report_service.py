import json
import re
import textwrap


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT_MARGIN = 48
RIGHT_MARGIN = 48
TOP_MARGIN = 785
BOTTOM_MARGIN = 56


def _normalize_text(text: str):
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.encode("latin-1", "replace").decode("latin-1")


def _escape_pdf_text(text: str):
    safe = _normalize_text(text)
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_text(text: str, font_size: int = 11, indent: int = 0):
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return [""]
    usable_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - indent
    approx_chars = max(24, int(usable_width / max(font_size * 0.53, 1)))
    return textwrap.wrap(
        cleaned,
        width=approx_chars,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [cleaned]


def _extract_summary_points(bundle):
    analysis = bundle.get("analysis") or {}
    summary = analysis.get("summary") or ""
    if summary:
        bullets = []
        for line in summary.splitlines():
            cleaned = line.strip().lstrip("*-• ").strip()
            if len(cleaned) >= 18:
                bullets.append(cleaned)
        if bullets:
            return bullets[:5]

    formatted_output = analysis.get("formatted_output") or ""
    if "RISK OVERVIEW:" in formatted_output:
        formatted_output = formatted_output.split("RISK OVERVIEW:", 1)[0]
    formatted_output = formatted_output.replace("📄 SUMMARY:", "").strip()
    parts = re.split(r"(?:\n|(?<=\.)\s+)[\*\u2022\-]?\s*", formatted_output)
    bullets = []
    for part in parts:
        cleaned = " ".join(part.split()).strip(" -*•")
        if len(cleaned) >= 18:
            bullets.append(cleaned)
    deduped = []
    seen = set()
    for bullet in bullets:
        key = bullet.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(bullet)
    return deduped[:5]


def _report_filename(bundle):
    document = bundle.get("document") or {}
    original_name = document.get("original_name") or "tnc_analysis"
    first_name = original_name.split(",")[0].strip()
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", first_name)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_") or "tnc_analysis"
    return f"{safe_stem}_report.pdf"


class SimplePdfBuilder:
    def __init__(self):
        self.pages = []
        self.page_commands = []
        self.cursor_y = TOP_MARGIN

    def _new_page(self):
        if self.page_commands:
            self.pages.append(self.page_commands)
        self.page_commands = []
        self.cursor_y = TOP_MARGIN

    def _ensure_space(self, needed_height: int):
        if not self.page_commands:
            return
        if self.cursor_y - needed_height < BOTTOM_MARGIN:
            self._new_page()

    def add_spacer(self, amount: int):
        self.cursor_y -= amount

    def add_line(self, text: str, *, font: str = "F1", size: int = 11, leading: int = 16, indent: int = 0, color=(0.11, 0.16, 0.23)):
        self._ensure_space(leading)
        escaped = _escape_pdf_text(text)
        x = LEFT_MARGIN + indent
        r, g, b = color
        self.page_commands.append(
            f"BT /{font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg {x} {self.cursor_y} Td ({escaped}) Tj ET"
        )
        self.cursor_y -= leading

    def add_paragraph(self, text: str, *, font: str = "F1", size: int = 11, leading: int = 16, indent: int = 0, color=(0.11, 0.16, 0.23)):
        for line in _wrap_text(text, font_size=size, indent=indent):
            self.add_line(line, font=font, size=size, leading=leading, indent=indent, color=color)

    def add_section(self, title: str):
        self.add_spacer(8)
        self.add_line(title, font="F2", size=18, leading=24, color=(0.06, 0.13, 0.24))

    def finalize(self):
        if self.page_commands:
            self.pages.append(self.page_commands)
        if not self.pages:
            self.pages = [[]]
        return _render_pdf(self.pages)


def _render_pdf(page_commands):
    object_count = 4 + (len(page_commands) * 2)
    objects = {}

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{5 + (index * 2)} 0 R" for index in range(len(page_commands)))
    objects[2] = f"<< /Type /Pages /Count {len(page_commands)} /Kids [{kids}] >>".encode()
    objects[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    objects[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"

    for index, commands in enumerate(page_commands):
        page_object = 5 + (index * 2)
        content_object = page_object + 1
        stream = "\n".join(commands).encode("latin-1", "replace")
        objects[page_object] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_object} 0 R >>"
        ).encode()
        objects[content_object] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode()
            + stream
            + b"\nendstream"
        )

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (object_count + 1)

    for object_number in range(1, object_count + 1):
        offsets[object_number] = len(pdf)
        pdf.extend(f"{object_number} 0 obj\n".encode())
        pdf.extend(objects[object_number])
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {object_count + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for object_number in range(1, object_count + 1):
        pdf.extend(f"{offsets[object_number]:010} 00000 n \n".encode())

    pdf.extend(
        f"trailer\n<< /Size {object_count + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )
    return bytes(pdf)


def build_analysis_report_pdf(bundle):
    document = bundle.get("document") or {}
    analysis = bundle.get("analysis") or {}
    clauses = bundle.get("clauses") or []
    chats = bundle.get("chat_history") or []

    risk_overview = json.loads(analysis.get("risk_overview_json") or "{}")
    summary_points = _extract_summary_points(bundle)
    top_clauses = clauses[:5]
    recent_chats = chats[:3]

    builder = SimplePdfBuilder()
    builder.add_line("T&C Analyzer Report", font="F2", size=24, leading=30, color=(0.05, 0.12, 0.22))
    builder.add_line(document.get("original_name") or "Document analysis", font="F2", size=16, leading=22, color=(0.12, 0.24, 0.39))
    builder.add_line(
        f"Source: {(document.get('source_type') or 'unknown').upper()}   Pages: {document.get('page_count') or 0}   Created: {document.get('created_at') or 'N/A'}",
        size=10,
        leading=16,
        color=(0.42, 0.48, 0.56),
    )
    if document.get("source_url"):
        builder.add_paragraph(f"Source URL: {document['source_url']}", size=10, leading=14, color=(0.42, 0.48, 0.56))

    builder.add_section("Risk Overview")
    builder.add_line(
        f"High risk clauses: {risk_overview.get('high', 0)}    Medium risk clauses: {risk_overview.get('medium', 0)}    Low risk clauses: {risk_overview.get('low', 0)}",
        font="F2",
        size=13,
        leading=18,
        color=(0.10, 0.19, 0.31),
    )

    builder.add_section("Executive Summary")
    if summary_points:
        for point in summary_points:
            builder.add_paragraph(f"- {point}", size=11, leading=16)
    else:
        builder.add_paragraph(analysis.get("summary") or "No summary available for this analysis.")

    builder.add_section("Top Risk Signals")
    if top_clauses:
        for index, clause in enumerate(top_clauses, start=1):
            builder.add_line(
                f"{index}. {clause['risk']} risk | {clause['category'].replace('_', ' ').title()} | Score {clause['risk_score']}/10 | Page {clause['page_number']}",
                font="F2",
                size=12,
                leading=17,
                color=(0.10, 0.19, 0.31),
            )
            builder.add_paragraph(clause["reason"], size=11, leading=15)
            builder.add_paragraph(
                f"Clause excerpt: {clause['clause_text'][:420]}",
                size=10,
                leading=14,
                color=(0.35, 0.42, 0.50),
                indent=10,
            )
            builder.add_spacer(4)
    else:
        builder.add_paragraph("No risk clauses were stored for this document.")

    if recent_chats:
        builder.add_section("Recent Questions")
        for chat in recent_chats:
            builder.add_line(f"Question: {chat['question']}", font="F2", size=11, leading=16, color=(0.10, 0.19, 0.31))
            builder.add_paragraph(f"Answer: {chat['answer']}", size=11, leading=15)
            builder.add_line(
                f"Grounded: {'Yes' if chat['grounded'] else 'No'}   Confidence: {chat['confidence']}",
                size=10,
                leading=14,
                color=(0.42, 0.48, 0.56),
            )
            builder.add_spacer(4)

    builder.add_section("Generated By")
    builder.add_paragraph(
        "AI Terms & Conditions Analyzer. This report summarizes stored analysis results and cited clause signals for quicker review.",
        size=10,
        leading=14,
        color=(0.42, 0.48, 0.56),
    )

    return builder.finalize()


def build_report_filename(bundle):
    return _report_filename(bundle)
