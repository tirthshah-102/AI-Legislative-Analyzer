from fpdf import FPDF
import os

class ReportGenerator:
    def generate_summary_pdf(self, summary_text, language, filename="legislative_summary.pdf"):
        """
        Generates a PDF with Unicode support for English, Hindi, and Gujarati.
        """
        os.makedirs("tmp", exist_ok=True)
        output_path = os.path.join("tmp", filename)

        # Initialize FPDF
        pdf = FPDF()
        pdf.add_page()
        
        # Determine font path - try standard Windows paths for Nirmala UI (best for Hindi/Gujarati)
        font_path = None
        common_paths = [
            r"C:\Windows\Fonts\Nirmala.ttc",
            r"C:\Windows\Fonts\nirmala.ttf",
            r"C:\Windows\Fonts\Nirmala.ttf",
            r"C:\Windows\Fonts\shruti.ttf",
            r"C:\Windows\Fonts\mangal.ttf",
            r"C:\Windows\Fonts\arial.ttf"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        # Load fonts
        if font_path:
            pdf.add_font("UnicodeFont", "", font_path)
            pdf.add_font("UnicodeFont", "B", font_path) # Simplified, usually different files needed for Bold
            font_name = "UnicodeFont"
        else:
            # Fallback to built-in Helvetica if no external font found (won't support Indic well but prevents crash)
            font_name = "helvetica"

        # Content
        pdf.set_font(font_name, 'B', 18)
        pdf.cell(0, 14, text="Legislative Analysis Report", ln=True, align='C')
        pdf.ln(4)

        pdf.set_font(font_name, '', 12)
        pdf.set_draw_color(92, 141, 137)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        pdf.set_font(font_name, 'B', 11)
        pdf.cell(0, 10, text=f"Language: {language}", ln=True, align='L')
        pdf.ln(4)

        pdf.set_font(font_name, '', 11)
        pdf.set_fill_color(247, 250, 250)
        
        # For fpdf2, we don't need to normalize to latin-1 like the original code did
        # It handles UTF-8 if a Unicode font is added
        pdf.multi_cell(0, 8, text=summary_text)

        pdf.output(output_path)
        return output_path
