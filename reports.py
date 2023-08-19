from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

import os

default_receipts_path = os.path.sep.join(
    [os.path.expanduser("~"), "Documents", "TheosWaters Receipts"]
)

if not os.path.exists(default_receipts_path):
    os.mkdir(default_receipts_path)

if not os.path.exists("./receipts"):
    os.mkdir("./receipts")


def generate_receipt(
    receiptpath, customer_name, date, time, water_amount, cost, service_provider
):
    pdf_file = canvas.Canvas(receiptpath, pagesize=landscape(letter))
    content = [
        ["Customer", customer_name],
        ["Date", date],
        ["Time", time],
        ["Water Amount", water_amount],
        ["Cost", cost],
        ["Served By", service_provider],
    ]
    table_x = 50
    table_y = 400
    font_size = 35
    table = Table(content)
    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightblue,
                ),  # Header row background color
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),  # Header row text color
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # Header row alignment
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Header row font
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.beige,
                ),  # Content row background color
                ("FONTSIZE", (0, 0), (-1, 0), font_size),  # Header row font size
                ("BOTTOMPADDING", (0, 0), (-1, 0), 40),  # Header row bottom padding
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightblue,
                ),  # Header row stripe color
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    1,
                    colors.black,
                ),  # Header row bottom border
                (
                    "LINEBELOW",
                    (0, -1),
                    (-1, -1),
                    1,
                    colors.black,
                ),  # Content row bottom border
            ]
        )
    )
    table.wrapOn(pdf_file, 800, 600)
    table.drawOn(pdf_file, table_x, table_y)
    content_width = table._width
    content_height = table._height
    border_x = table_x - 5
    border_y = table_y - 5
    border_width = content_width + 10
    border_height = content_height + 10
    pdf_file.rect(border_x, border_y, border_width, border_height, stroke=1, fill=0)
    company_name = "TheosWaters Limited"
    company_name_x = 50
    company_name_y = 350
    pdf_file.setFont(
        "Helvetica-Bold", 30
    )  # Increase the font size for the company name
    pdf_file.drawString(company_name_x, company_name_y, company_name)
    pdf_file.line(50, 330, 50, 330)
    line_x = 50
    line_y = 330
    line_width = border_width + 300  # Increase the width by 50 units
    pdf_file.setLineWidth(5)
    pdf_file.line(line_x, line_y, line_x + line_width, line_y)
    pdf_file.save()


if __name__ == "__main__":
    path = "receipt.pdf"
    customer_name = "John Doe"
    date = "2023-06-10"
    time = "15:30"
    water_amount = "500 ml"
    cost = "$2.50"
    serviceman = "Abigail Thompson"
    generate_receipt(path, customer_name, date, time, water_amount, cost, serviceman)

