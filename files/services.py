"""
Fayllarni qayta ishlash logikasi. Celery task'lar shu funksiyalarni chaqiradi.
Har bir funksiya: input fayl yo'lini oladi, natija faylini diskka yozadi va
natija faylining yo'lini qaytaradi (relative path, MEDIA_ROOT ichida).
"""

import os
import uuid

import pandas as pd
import pdfplumber
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from django.conf import settings


def _output_path(job_id, filename):
    folder = os.path.join(settings.MEDIA_ROOT, "outputs", str(job_id))
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, filename)


def _relative_to_media(abs_path):
    return os.path.relpath(abs_path, settings.MEDIA_ROOT)


def process_excel_clean(job):
    """
    Excel faylni o'qiydi: bo'sh qatorlarni va to'liq takrorlangan qatorlarni
    o'chiradi, natijani yangi xlsx sifatida saqlaydi.
    options: {"dedup_columns": ["col1", "col2"]} -- ixtiyoriy, berilmasa barcha
    ustunlar bo'yicha dedup qilinadi.
    """
    df = pd.read_excel(job.input_file.path)

    df = df.dropna(how="all")

    dedup_cols = job.options.get("dedup_columns") if job.options else None
    if dedup_cols:
        df = df.drop_duplicates(subset=dedup_cols)
    else:
        df = df.drop_duplicates()

    out_path = _output_path(job.id, "cleaned.xlsx")
    df.to_excel(out_path, index=False)
    return _relative_to_media(out_path)


def process_excel_to_pdf(job):
    """
    Excel faylni o'qiydi va oddiy jadval ko'rinishidagi PDF hisobot yaratadi.
    """
    df = pd.read_excel(job.input_file.path)

    out_path = _output_path(job.id, "report.pdf")

    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("FileFlow hisobot", styles["Title"]), Spacer(1, 12)]

    data = [list(df.columns)] + df.astype(str).values.tolist()

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    elements.append(table)

    doc.build(elements)
    return _relative_to_media(out_path)


def process_pdf_table_extract(job):
    """
    PDF ichidagi jadval(lar)ni topib, har birini bitta Excel faylga
    alohida sheet sifatida yozadi.
    """
    out_path = _output_path(job.id, "extracted_tables.xlsx")
    wb = Workbook()
    wb.remove(wb.active)  # default bo'sh sheet'ni o'chiramiz

    sheet_count = 0
    with pdfplumber.open(job.input_file.path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables, start=1):
                sheet_count += 1
                ws = wb.create_sheet(title=f"p{page_num}_t{t_idx}"[:31])
                for row in table:
                    ws.append([cell if cell is not None else "" for cell in row])

    if sheet_count == 0:
        ws = wb.create_sheet(title="empty")
        ws.append(["PDF ichida jadval topilmadi"])

    wb.save(out_path)
    return _relative_to_media(out_path)


PROCESSORS = {
    "excel_clean": process_excel_clean,
    "excel_to_pdf": process_excel_to_pdf,
    "pdf_table_extract": process_pdf_table_extract,
}
