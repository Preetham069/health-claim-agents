import io
from fpdf import FPDF
from datetime import datetime

class AdjudicationPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(24, 43, 73)
        self.cell(0, 10, "PRE-AUTHORIZATION DETERMINATION NOTICE", ln=True, align="C")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "CareShield Health Insurance Automated Adjudication Engine", ln=True, align="C")
        self.line(10, 28, 200, 28)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "CONFIDENTIAL & PRIVILEGED - CLINICAL DECISION SUPPORT SYSTEM", align="C")

def generate_pdf_letter(case_id: str, verdict: str, reviewer: str, comments: str, letter_body: str) -> bytes:
    pdf = AdjudicationPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Meta Details Box
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, 32, 190, 28, 'F')
    
    pdf.set_xy(14, 35)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(45, 6, "Case Reference ID:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 6, case_id, ln=False)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(35, 6, "Determination:", ln=False)
    pdf.set_font("Helvetica", "B", 10)
    if verdict == "Approve":
        pdf.set_text_color(0, 128, 0)
    elif verdict == "Reject":
        pdf.set_text_color(180, 0, 0)
    else:
        pdf.set_text_color(200, 120, 0)
    pdf.cell(40, 6, verdict.upper(), ln=True)
    
    pdf.set_xy(14, 43)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(45, 6, "Adjudicating Officer:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 6, reviewer, ln=False)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(35, 6, "Date Issued:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(40, 6, datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True)
    
    pdf.set_xy(14, 51)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 6, "Clinical Remarks:", ln=False)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(130, 6, comments[:75], ln=True)
    
    # Body Letter
    pdf.set_xy(10, 68)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(20, 20, 20)
    
    # Sanitize characters for standard Helvetica encoding
    clean_text = letter_body.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(190, 5, clean_text)
    
    return bytes(pdf.output())