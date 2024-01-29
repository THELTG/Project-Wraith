#libraries needed for pdf formatting
from fpdf import FPDF
from datetime import datetime
import os
from PyPDF2 import PdfReader, PdfWriter


class PDF(FPDF):

    def header(self):
        self.image("./apps/static/assets/images/wraith3.png", w=50, h=35, x=150,y=0) 

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial","I",8)
        self.cell(0,10,"Page" + str(self.page_no())+ '/{nb}',0,0, "C")


def pdf_gen(data, hostname, pdfname, password=None):

    pdf = FPDF()
    pdf = PDF()
    pdf.alias_nb_pages()

    pdf.set_auto_page_break(auto=True, margin=40)
    pdf.set_top_margin(40)

    pdf.add_page()

    pdf.set_font('Times', 'B', 30)
    pdf.set_y(40)
    pdf.cell(40,15,'Penetration Test Report', ln=2)
    pdf.set_font('Times', '', 10)

    d_minute = datetime.utcnow().minute
    if d_minute<10:
        d_minute = f"0{d_minute}"

    #update the hour digits
    d_hour = datetime.utcnow().hour + 8
    if d_hour >= 24:
        d_hour -= 24
        date = f"{datetime.utcnow():%Y-%m-%d} 0{d_hour}:{d_minute}"
    else:
        date = f"{datetime.utcnow():%Y-%m-%d} {d_hour}:{d_minute}"

    pdf.cell(40,5,f"Scanned by: Project Wraith", ln=2)
    pdf.cell(40,5,f"Generated on: {date}", ln=2)
    pdf.multi_cell(1,18,f"")
    pdf.set_font('Times', 'B', 14)
    pdf.cell(40,5,f"Host Machine: {hostname[0]}", ln=2)
    pdf.multi_cell(40,5,f"")
    pdf.cell(40,5,f"Agent Identifier: {pdfname[0]}")


    #print(data) # testing


    # for reference : data array looks something like the following : [('Kernel Driver check', 'false', 'Generic Detail for Kernel Driver check', 'False Detail for Kernel Driver check')]
    # [0] - technique name, [1] - test result, [2] - basic info for technique, [3] - additional info (optional) , [4] - info about mitigation measures (optional), [5] - info based on whether the result is true or false

    for i in range(len(data)):
        pdf.add_page()
        pdf.set_y(40)
        pdf.set_font('Times', 'B', 28)

        pdf.cell(40,20,f"{data[i][0]}",ln=2)
        pdf.set_font('Times', 'B', 15)
        pdf.multi_cell(40,10,"")

        pdf.cell(40,10,f"Exploitation Technique - {data[i][0]}",ln=2) # exploitation technique name
        pdf.set_font('Times', '', 12)
        pdf.cell(40,2,f"",ln=2)
        pdf.multi_cell(185,5,f"{data[i][2]}") # basic info for exploitation, there regardless of whether a true or false result was received

        if data[i][1] == "True":
            success = "Successful"
        else:
            success = "Unsuccessful"

        pdf.set_font('Times', 'B', 15)
        pdf.multi_cell(1,8,f"") 
        pdf.cell(40,5,f"[ Operation {success} ]",ln=2)

        pdf.set_font('Times', '', 12)
        pdf.cell(40,5,f"",ln=2)
        pdf.multi_cell(185,5,f"{data[i][5]}") # info based on the result received
        
        if data[i][3] != '' : # if there is additional info (currently only for the rce/privesc check operation and kernel driver check)
            pdf.set_font('Times', 'B', 15)
            pdf.multi_cell(1,8,f"") 
            pdf.cell(40,5,f"[ Additional Info : Operation Output ]",ln=2)
            
            pdf.set_font('Courier', '', 8)
            pdf.cell(40,5,f"",ln=2)

            pdf.multi_cell(185,5,f"{data[i][3]}") 

        if data[i][4] != '' : # if there is info about mitigation measures
            pdf.set_font('Times', 'B', 15)
            pdf.multi_cell(1,8,f"") 
            pdf.cell(40,5,f"[ Preventive Measures ]",ln=2)

            pdf.set_font('Times', '', 12)
            pdf.cell(40,5,f"",ln=2)

            pdf.multi_cell(185,5,f"{data[i][4]}") 

    filepath = f'{pdfname[0]}_{pdfname[1]}_{pdfname[2]}_{datetime.utcnow():%Y-%m-%d}.pdf'
    pdf_path = os.path.join("./apps/reports", filepath)
    pdf.output(pdf_path)  



####password encryption
    
    if password:
        with open(f"./apps/reports/{filepath}", "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            with open(f"./apps/reports/{filepath}", "wb") as encrypted_pdf:
                writer.write(encrypted_pdf)


    return filepath






                 
