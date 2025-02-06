from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from PIL import Image
import pdf2image
import tempfile
import os


def get_table_dimensions(table):
    """Get the actual dimensions of the table including merged cells"""
    max_cols = 0
    for row in table.rows:
        col_count = 0
        for cell in row.cells:
            # Account for grid_span (horizontal merging)
            grid_span = cell._tc.grid_span
            col_count += grid_span if grid_span else 1
        max_cols = max(max_cols, col_count)
    return len(table.rows), max_cols


def extract_table_data(table):
    """Extract data from docx table handling merged cells"""
    data = []
    row_idx = 0
    while row_idx < len(table.rows):
        row = table.rows[row_idx]
        row_data = []
        col_idx = 0

        while col_idx < len(row.cells):
            cell = row.cells[col_idx]

            # Get cell content
            text = cell.text.strip()

            # Handle vertical merging
            v_merge = cell._tc.get_or_add_tcPr().get_or_add_vMerge()
            if v_merge.val == "continue":
                # Use value from cell above
                text = data[row_idx - 1][col_idx]

            # Handle horizontal merging
            grid_span = cell._tc.grid_span
            if grid_span > 1:
                # Add empty strings for merged columns
                row_data.append(text)
                row_data.extend([""] * (grid_span - 1))
                col_idx += grid_span
            else:
                row_data.append(text)
                col_idx += 1

        data.append(row_data)
        row_idx += 1

    return data


def table_to_image(table, output_path):
    """Convert a single table to an image"""
    # Get table data and dimensions
    table_data = extract_table_data(table)
    rows, cols = get_table_dimensions(table)

    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        doc = SimpleDocTemplate(
            tmp_pdf.name,
            pagesize=(
                letter[0],
                letter[1] * (rows / 40 + 1),
            ),  # Adjust page height based on rows
        )

        # Create ReportLab table
        rl_table = Table(table_data)

        # Add table style
        style = TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
        rl_table.setStyle(style)

        # Build PDF
        doc.build([rl_table])

        # Convert PDF to image
        images = pdf2image.convert_from_path(tmp_pdf.name)

        # Since we designed the PDF to fit the table on one page,
        # we should only have one image
        if images:
            images[0].save(output_path)

    # Clean up temporary PDF
    os.unlink(tmp_pdf.name)
    return output_path


def extract_tables_as_images(docx_path, output_dir="table_images"):
    """Extract all tables from a DOCX file as separate images"""
    os.makedirs(output_dir, exist_ok=True)
    doc = Document(docx_path)

    for i, table in enumerate(doc.tables):
        output_path = os.path.join(output_dir, f"table_{i}.png")
        table_to_image(table, output_path)
        print(f"Saved table {i} to {output_path}")


if __name__ == "__main__":
    docx_path = "p9467_doc0__4-1-16__Antigua_Barbuda_CD_9467_PIF.docx"
    extract_tables_as_images(docx_path)
