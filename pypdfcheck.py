from PyPDF2 import PdfReader

# Opening the file using pypdf
file = PdfReader("test.pdf")
# Setting number of pages
no_of_pages = len(file.pages)
page=file.pages[0]
text=page.extractText()
