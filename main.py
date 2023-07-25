import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw
import pytesseract
from pytesseract import image_to_string
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = "C:/Users/aleja/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"  # change this to your own location

def extract_pages_as_images(pdf_path):
    return convert_from_path(pdf_path)

def detect_question_number(image, debug=False):
    left = image.width - 120
    top = 0
    right = image.width
    bottom = 120

    cropped = image.crop((left, top, right, bottom))
    if debug:
        draw = ImageDraw.Draw(image)
        draw.rectangle(((left, top), (right, bottom)), outline="red")
        image.save('debug.png')
        cropped.save('debug_cropped.png')
        
    try:
        return int(image_to_string(cropped, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'))
    except ValueError:
        print("OCR didn't find a number on the page.")
        return 0

def create_pdf_from_pages(pdf_reader, pages, output_path):
    pdf_writer = PdfWriter()
    for page in pages:
        pdf_writer.add_page(pdf_reader.pages[page])
    with open(output_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    pdf_reader = PdfReader(file_path)
    images = extract_pages_as_images(file_path)
    
    last_question_number = 0
    assignment_number = 1
    pages = []
    
    for i, image in enumerate(images):
        question_number = detect_question_number(image, debug=True)
        if question_number < last_question_number:
            output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            create_pdf_from_pages(pdf_reader, pages, output_path)
            assignment_number += 1
            pages = []
        last_question_number = question_number
        pages.append(i)

    if pages:
        output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        create_pdf_from_pages(pdf_reader, pages, output_path)

    root.mainloop()

if __name__ == "__main__":
    main()
