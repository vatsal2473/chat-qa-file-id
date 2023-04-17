import docx2txt
import PyPDF2
import re


def docx_to_text(book_name):

    doc_text = docx2txt.process("data/all_files/"+book_name)

    doc_text = doc_text.replace("\n", " ")
    doc_text = " ".join(doc_text.split())

    paragraphs = doc_text.split(".")

    with open(f'data/txt_files/{book_name[:-5]}.txt', "w") as txt_file:
        for paragraph in paragraphs:
            words = paragraph.split()
            lines = []
            line = ""
            for word in words:
                if len(line + " " + word) <= 16:
                    line += " " + word
                else:
                    lines.append(line.strip())
                    line = word
            lines.append(line.strip())
            txt_file.write(" ".join(lines) + "\n\n")

def pdf_to_text(book_name):

    pdf_file = open('data/all_files/'+book_name, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    pdf_text = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        pdf_text += page_text

    pdf_file.close()

    pdf_text = re.sub(r'\s+', ' ', pdf_text)
    pdf_text = re.sub(r'\n', ' ', pdf_text)

    paragraphs = re.findall(r'.+?\.', pdf_text)

    # remove .pdf from book_name and add .txt at the end
    
    with open(f'data/txt_files/{book_name[:-4]}.txt', 'w') as txt_file:
        for paragraph in paragraphs:
            words = paragraph.split()
            lines = []
            line = ""
            for word in words:
                if len(line + " " + word) <= 16:
                    line += " " + word
                else:
                    lines.append(line.strip())
                    line = word
            lines.append(line.strip())
            txt_file.write(" ".join(lines) + "\n\n")