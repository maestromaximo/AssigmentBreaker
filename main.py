# Import required modules
import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw
import pytesseract
from pytesseract import image_to_string
from pdf2image import convert_from_path

# Set path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "C:/Users/aleja/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"

# Function to convert PDF pages to images
def extract_pages_as_images(pdf_path):
    return convert_from_path(pdf_path)

# Function to read the question number using OCR
def detect_question_number(image, debug=False):
    # Define the crop area (top-right corner of the page)
    left = image.width - 120
    top = 0
    right = image.width
    bottom = 120

    # Crop the image
    cropped = image.crop((left, top, right, bottom))

    # If debug mode is enabled, save the cropped image and the original image with a rectangle showing the cropped area
    if debug:
        draw = ImageDraw.Draw(image)
        draw.rectangle(((left, top), (right, bottom)), outline="red")
        image.save('debug.png')
        cropped.save('debug_cropped.png')
    
    # Attempt to recognize a number in the cropped image
    try:
        return int(image_to_string(cropped, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'))
    except ValueError:
        # If the OCR fails to recognize a number, print a debug message and return 0
        print("OCR didn't find a number on the page.")
        return 0

# Function to write a subset of pages to a new PDF
def create_pdf_from_pages(pdf_reader, pages, output_path):
    pdf_writer = PdfWriter()
    # Add the specified pages to the writer
    for page in pages:
        pdf_writer.add_page(pdf_reader.pages[page])
    # Write the pages to a new PDF
    with open(output_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

# Main function to control the program flow
def main():
    # Create a Tk root widget and hide it (we only use the file dialog)
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select the input PDF
    file_path = filedialog.askopenfilename()

    # Read the PDF and convert its pages to images
    pdf_reader = PdfReader(file_path)
    images = extract_pages_as_images(file_path)
    
    # Initialize variables to keep track of the current assignment, question, and pages
    last_question_number = 0
    assignment_number = 1
    pages = []
    
    # Process each image
    for i, image in enumerate(images):
        # Detect the question number using OCR
        question_number = detect_question_number(image, debug=True)
        # If the question number decreases, it means we have started a new assignment
        if question_number < last_question_number:
            # Write the previous assignment's pages to a new PDF
            output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            create_pdf_from_pages(pdf_reader, pages, output_path)
            # Start a new assignment
            assignment_number += 1
            pages = []
        # Update the last question number and add the current page to the list of pages
        last_question_number = question_number
        pages.append(i)

    # If there are any remaining pages, write them to a new PDF
    if pages:
        output_path = f'AssignmentsBreak{assignment_number}/Q{last_question_number}.pdf'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        create_pdf_from_pages(pdf_reader, pages, output_path)

    # Start the Tk event loop (even though we don't use any widgets)
    root.mainloop()

# Run the main function if the script is run directly
if __name__ == "__main__":
    main()
