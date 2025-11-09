from fpdf import FPDF
import pandas as pd

def export_pdf_report(df, correlation_df=None, regression_info=None, plots=None, filename="report.pdf"):
    """
    Export a PDF report of the dataset, correlation, regression, and plots.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Data Analysis Report", ln=True, align="C")
    pdf.ln(10)

    # Dataset head
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Dataset Preview:", ln=True)
    pdf.set_font("Arial", "", 10)
    preview = df.head().to_string()
    pdf.multi_cell(0, 6, preview)
    pdf.ln(5)

    # Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary Statistics:", ln=True)
    pdf.set_font("Arial", "", 10)
    summary = df.describe().to_string()
    pdf.multi_cell(0, 6, summary)
    pdf.ln(5)

    # Correlation
    if correlation_df is not None:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Correlation Matrix:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, correlation_df.to_string())
        pdf.ln(5)

    # Regression
    if regression_info is not None:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Regression Results:", ln=True)
        pdf.set_font("Arial", "", 10)
        for key, val in regression_info.items():
            pdf.cell(0, 6, f"{key}: {val}", ln=True)
        pdf.ln(5)

    # Plots
    if plots is not None:
        for plot_path in plots:
            pdf.add_page()
            pdf.image(plot_path, x=15, y=25, w=180)

    # Save PDF
    pdf.output(filename)
    return filename