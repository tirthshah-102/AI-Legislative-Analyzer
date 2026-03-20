from fpdf import FPDF

def create_demo_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="The Green Energy Transition Act of 2026", ln=True, align='C')
    pdf.ln(10)
    
    # Section 1: Purpose
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Section 1: Objective and Scope", ln=True, align='L')
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, txt=(
        "This Act aims to accelerate the adoption of renewable energy sources across the country. "
        "The goal is to reduce carbon emissions by 50% by the year 2030 through a combination of "
        "subsidies, tax breaks, and mandatory green infrastructure projects."
    ))
    pdf.ln(5)
    
    # Section 2: Residential Subsidies
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Section 2: Incentives for Citizens", ln=True, align='L')
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, txt=(
        "1. Solar Panel Rebate: Every household that installs a certified solar power system will "
        "be eligible for a 30% direct cash rebate from the government.\n"
        "2. EV Charging Ports: The government will fund 50% of the cost for installing electric "
        "vehicle charging ports in residential apartment complexes.\n"
        "3. Energy Efficiency Bonus: Households that reduce their annual energy consumption by 15% "
        "will receive a 5000 rupee tax deduction."
    ))
    pdf.ln(5)
    
    # Section 3: Penalties
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Section 3: Compliance and Penalties", ln=True, align='L')
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, txt=(
        "Industrial plants that exceed the newly established carbon emission limits will face a "
        "daily fine of 1,00,000 rupees. Repeat offenders may have their operating licenses suspended "
        "for up to six months."
    ))
    
    pdf.output("Green_Energy_Act_Demo.pdf")
    print("Demo PDF created successfully: Green_Energy_Act_Demo.pdf")

if __name__ == "__main__":
    create_demo_pdf()
