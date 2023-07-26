import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw
import pytesseract
from pytesseract import image_to_string
from pdf2image import convert_from_path
import re

# Set path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "C:/Users/aleja/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"

# Set this to True to enable hyper debug mode
HyperDebugMode = False

def extract_pages_as_images(pdf_path):
    return convert_from_path(pdf_path)

def detect_question_number(image, i, debug=False):
    left = image.width - 120
    top = 0
    right = image.width
    bottom = 120

    cropped = image.crop((left, top, right, bottom))
    if debug:
        draw = ImageDraw.Draw(image)
        draw.rectangle(((left, top), (right, bottom)), outline="red")
        image.save(f'debug_{i}.png')
        cropped.save(f'debug_cropped_{i}.png')
        
    recognized_text = image_to_string(cropped, config='--psm 6 --oem 1').strip()
    print(f"OCR recognized text on page {i}: {recognized_text}")
    match = re.search(r'[1-9]|i', recognized_text)  # Search for the first digit between 1 and 9 or 'i'
    if match:
        recognized_digit = match.group()
        if recognized_digit == 'i':
            print(f"OCR recognized 'i' as '1' on page {i}.")
            return 1
        else:
            return int(recognized_digit)
    else:
        print(f"OCR didn't find a number between 1 and 9 or 'i' on page {i}.")
        return None


def detect_question_numberOld(image, i, debug=False):
    left = image.width - 120
    top = 0
    right = image.width
    bottom = 120

    cropped = image.crop((left, top, right, bottom))
    if debug:
        draw = ImageDraw.Draw(image)
        draw.rectangle(((left, top), (right, bottom)), outline="red")
        image.save(f'debug_{i}.png')
        cropped.save(f'debug_cropped_{i}.png')
        
    try:
        recognized_number = int(image_to_string(cropped, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'))
        print(f"OCR recognized number on page {i}: {recognized_number}")
        return recognized_number
    except ValueError:
        print(f"OCR didn't find a number on page {i}.")
        return None

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
    
    last_question_number = 1  # Start with question number 1
    assignment_number = 1
    pages = []
    
    for i, image in enumerate(images):
        question_number = detect_question_number(image, i, debug=HyperDebugMode)
        
        if question_number is not None and question_number < last_question_number:
            # Start of a new assignment detected
            output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            create_pdf_from_pages(pdf_reader, pages, output_path)
            assignment_number += 1
            pages = [i]  # Start the pages for the new assignment with the current page
            last_question_number = question_number
        elif question_number is not None:
            # Start of a new question detected
            output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            create_pdf_from_pages(pdf_reader, pages, output_path)
            pages = [i]  # Start the pages for the new question with the current page
            last_question_number = question_number
        else:
            # If no new question number is detected, continue appending the pages to the current question
            pages.append(i)

    # If there are any remaining pages, write them to a new PDF
    if pages:
        output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        create_pdf_from_pages(pdf_reader, pages, output_path)

    root.mainloop()


if __name__ == "__main__":
    main()
