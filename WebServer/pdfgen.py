#libraries needed for pdf formatting
from fpdf import FPDF
from datetime import datetime
import os


class PDF(FPDF):

    def header(self):
        self.image("./apps/static/assets/images/wraith3.png", w=50, h=35, x=150,y=0) 

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial","I",8)
        self.cell(0,10,"Page" + str(self.page_no())+ '/{nb}',0,0, "C")

def pdf_gen(data, hostname, pdfname):

    pdf = FPDF()
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Times', 'B', 30)
    pdf.set_y(40)
    pdf.cell(40,15,'Penetration Test Report', ln=2)
    pdf.set_font('Times', '', 10)

    d_minute = datetime.utcnow().minute
    if d_minute<10:
        d_minute = f"0{d_minute}"
    date = f"{datetime.utcnow():%Y-%m-%d} {datetime.utcnow().hour + 8}:{d_minute}"
    pdf.cell(40,5,f"Scanned by: Project Wraith", ln=2)
    pdf.cell(40,5,f"Generated on: {date}", ln=2)
    pdf.cell(40,5,f"", ln=2)
    pdf.set_font('Times', 'B', 18)
    pdf.cell(40,5,f"Host Machine: {hostname}")



    for i in range(len(data)):
        pdf.add_page()
        pdf.set_y(40)
        pdf.set_font('Times', 'B', 28)

        pdf.cell(40,20,f"{data[i][2]}",ln=2)
        pdf.set_font('Times', 'B', 15)




        templst = data[i][4].split(" - ")


        pdf.cell(40,10,f"Exploitation Technique - {templst[0]}",ln=2)
        pdf.set_font('Times', '', 12)
        pdf.multi_cell(185,5,f"{templst[1]}")

        if data[i][3] == "True":
            success = "Successful"
        else:
            success = "Unsuccessful"

        pdf.set_font('Times', 'B', 15)
        pdf.cell(40,25,f"Penetration {success}")

        





    pdf.set_auto_page_break(auto=bool, margin=0.0)
    filepath = f'{pdfname[0]}_{pdfname[1]}_{pdfname[2]}_{datetime.utcnow():%Y-%m-%d}.pdf'
    pdf_path = os.path.join("./apps/reports", filepath)
    pdf.output(pdf_path)  

    return filepath






                 
