from fpdf import FPDF
import os

class ComprehensiveDemoPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'CONFIDENTIAL - LEGISLATIVE DRAFT', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def create_comprehensive_demo():
    pdf = ComprehensiveDemoPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title Page
    pdf.set_font('Arial', 'B', 24)
    pdf.ln(40)
    pdf.cell(0, 20, 'Digital Markets and Data', ln=True, align='C')
    pdf.cell(0, 20, 'Sovereignty Act of 2026', ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.ln(10)
    pdf.cell(0, 10, 'Draft Version 4.2.1-B', ln=True, align='C')
    pdf.cell(0, 10, 'Committee on Technology and Civil Liberties', ln=True, align='C')
    
    pdf.add_page()
    
    # Table of Contents Style
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Arrangement of Sections', ln=True)
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    sections = [
        "Section 1: Short Title and Commencement",
        "Section 2: Definitions and Interpretations",
        "Section 3: Data Localization Requirements",
        "Section 4: Interoperability Mandates for Key Platforms",
        "Section 5: Enforcement Mechanisms and Penalties",
        "Section 6: Force Majeure and Exceptional Circumstances",
        "Section 7: Indemnification of Cloud Service Providers"
    ]
    for section in sections:
        pdf.cell(0, 10, section, ln=True)
    
    pdf.ln(10)
    
    # Section 1
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, sections[0], ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, (
        "This Act shall be cited as the Digital Markets and Data Sovereignty Act (DMDSA) of 2026. "
        "It shall come into force on the first day of the fiscal year following its enactment, "
        "notwithstanding any prior regulations to the contrary. The provisions herein apply to all "
        "entities processing data of citizens within the territorial jurisdiction."
    ))
    
    # Section 2 - Terms for Glossary
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, sections[1], ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, (
        "In this Act, unless the context otherwise requires:\n"
        "1. 'Data Fiduciary' refers to any entity that determines the purpose and means of processing personal data.\n"
        "2. 'Interoperability' refers to the ability of different information systems and software applications to communicate and exchange data.\n"
        "3. 'Sovereign Data Cluster' refers to a distributed ledger or database infrastructure physically located within national borders."
    ))

    # Section 5 - Specific information for Q&A
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, sections[4], ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, (
        "Non-compliance with Data Localization requirements established in Section 3 shall result in "
        "administrative penalties. For a first-time violation, the entity shall be liable for a fine "
        "equivalent to 4% of its annual global turnover. Subsequent violations may lead to a permanent "
        "revocation of the operational license. Furthermore, individual directors of the Data Fiduciary "
        "may be held personally liable under the doctrine of 'piercing the corporate veil' for intentional negligence."
    ))

    # Section 6 - Legal Jargon
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, sections[5], ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, (
        "The requirements of this Act may be suspended in the event of Force Majeure, including but not "
        "limited to natural disasters, war, or catastrophic network failure beyond the reasonable control "
        "of the entity. However, 'Force Majeure' shall not include economic hardship or changes in market dynamics."
    ))

    output_path = "Comprehensive_Legal_Document_Demo.pdf"
    pdf.output(output_path)
    print(f"Professional Demo PDF created successfully: {output_path}")

if __name__ == "__main__":
    create_comprehensive_demo()
