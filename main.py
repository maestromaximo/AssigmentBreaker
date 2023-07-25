import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
from PIL import Image
import pytesseract
from pytesseract import image_to_string
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

# Add this line after the import statements
pytesseract.pytesseract.tesseract_cmd = "C:/Users/aleja/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"  # change this to your own location

def extract_pages_as_images(pdf_path):
    return convert_from_path(pdf_path)

def detect_question_number(image):
    # Crop the top right corner and use OCR to extract the number
    # You may need to adjust the crop area depending on your PDFs
    cropped = image.crop((image.width-100, 0, image.width, 100))
    return int(image_to_string(cropped))

def create_pdf_from_pages(pages, output_path):
    merger = PyPDF2.PdfFileMerger()
    for page in pages:
        merger.append(page)
    merger.write(output_path)

def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    images = extract_pages_as_images(file_path)
    pages = []
    last_question_number = 0
    assignment_number = 1
    for i, image in enumerate(images):
        question_number = detect_question_number(image)
        if question_number < last_question_number:
            # New assignment
            output_path = f'AssignmentsBreak{assignment_number}/Q{question_number}.pdf'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            create_pdf_from_pages(pages, output_path)
            assignment_number += 1
            pages = []
        last_question_number = question_number
        pages.append(i)

    if pages:
        output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        create_pdf_from_pages(pages, output_path)

    root.mainloop()

if __name__ == "__main__":
    main()
