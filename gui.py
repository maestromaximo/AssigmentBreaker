import os
import pickle
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.ttk import Style
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk
from PyPDF2 import PdfReader, PdfWriter
from PIL import ImageDraw
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

try:
    with open('saved_directory.pkl', 'rb') as f:
        saved_directory = pickle.load(f)
except FileNotFoundError:
    saved_directory = os.getcwd()

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.withdraw()
        self.title('Assignment Breaker')
        self.geometry('800x600')
        self.style = ThemedStyle(self)
        self.style.set_theme("arc")  # Set the theme
        self.create_loading_screen()
        self.create_main_menu()

    def create_loading_screen(self):
        loading_label = ttk.Label(self, text="Assignment Breaker", font=("Arial", 30))
        loading_label.pack(pady=250)
        self.after(2000, loading_label.destroy)  # The loading screen will show for 2 seconds

    def create_main_menu(self):
        self.deiconify()
        self.debug_button = ttk.Button(self, text="Debug", command=self.debug_screen)
        self.debug_button.pack(pady=20)

        self.start_button = ttk.Button(self, text="Start", command=self.start_program)
        self.start_button.pack(pady=20)

        self.directory_button = ttk.Button(self, text="Directory", command=self.choose_directory)
        self.directory_button.pack(pady=20)

        self.settings_button = ttk.Button(self, text="Settings", command=self.settings_screen)
        self.settings_button.pack(pady=20)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def debug_screen(self):
        self.clear_screen()
        self.hyper_debug_var = tk.BooleanVar()
        self.hyper_debug_var.set(HyperDebugMode)
        debug_checkbutton = ttk.Checkbutton(self, text="HyperDebug Mode", variable=self.hyper_debug_var, onvalue=True, offvalue=False)
        debug_checkbutton.pack(pady=20)
        back_button = ttk.Button(self, text="Back", command=self.back_to_main)
        back_button.pack(pady=20)

    def start_program(self):
         # start of the main function
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

    def choose_directory(self):
        global saved_directory
        saved_directory = filedialog.askdirectory()
        # Save the chosen directory for future use
        with open('saved_directory.pkl', 'wb') as f:
            pickle.dump(saved_directory, f)

    def settings_screen(self):
        self.clear_screen()
        self.clear_assignments_button = ttk.Button(self, text="Clear All Temp Assignments", command=self.clear_assignments)
        self.clear_assignments_button.pack(pady=20)
        back_button = ttk.Button(self, text="Back", command=self.back_to_main)
        back_button.pack(pady=20)

    def clear_assignments(self):
        current_directory = os.getcwd()
        for item in os.listdir(current_directory):
            if item.startswith("AssignmentsBreak") and os.path.isdir(item):
                shutil.rmtree(item)

    def back_to_main(self):
        self.clear_screen()
        self.create_main_menu()

if __name__ == "__main__":
    app = Application()
    app.mainloop()

# import json
# import os
# import tkinter as tk
# from tkinter import ttk, filedialog
# from ttkthemes import ThemedTk

# from main import main as process_pdf


# class Settings:
#     def __init__(self, settings_path):
#         self.settings_path = settings_path
#         self.settings = {
#             "output_dir": os.getcwd(),
#             "hyper_debug": False
#         }
#         self.load_settings()

#     def load_settings(self):
#         if os.path.exists(self.settings_path):
#             with open(self.settings_path, 'r') as f:
#                 self.settings = json.load(f)
#         else:
#             self.save_settings()

#     def save_settings(self):
#         with open(self.settings_path, 'w') as f:
#             json.dump(self.settings, f)

#     def get(self, key, default=None):
#         return self.settings.get(key, default)

#     def set(self, key, value):
#         self.settings[key] = value
#         self.save_settings()


# class App:
#     def __init__(self):
#         self.settings = Settings('settings.json')

#         self.root = ThemedTk(theme="equilux")
#         self.root.geometry('400x200')
#         self.root.title('Assignment Breaker')

#         self.show_main_menu()

#         self.root.mainloop()

#     def show_main_menu(self):
#         for widget in self.root.winfo_children():
#             widget.destroy()

#         start_button = ttk.Button(self.root, text='Start', command=self.start)
#         start_button.pack(fill='x')

#         debug_button = ttk.Button(self.root, text='Debug', command=self.debug)
#         debug_button.pack(fill='x')

#         dir_button = ttk.Button(self.root, text='Directory', command=self.set_directory)
#         dir_button.pack(fill='x')

#         settings_button = ttk.Button(self.root, text='Settings', command=self.settings_menu)
#         settings_button.pack(fill='x')

#     def start(self):
#         process_pdf(self.settings.get('output_dir'), self.settings.get('hyper_debug'))
#         self.root.destroy()

#     def debug(self):
#         for widget in self.root.winfo_children():
#             widget.destroy()

#         debug_state = tk.BooleanVar()
#         debug_state.set(self.settings.get('hyper_debug'))
#         debug_check = ttk.Checkbutton(self.root, text='Enable Hyper Debug', var=debug_state, command=lambda: self.settings.set('hyper_debug', debug_state.get()))
#         debug_check.pack()

#         back_button = ttk.Button(self.root, text='Back', command=self.show_main_menu)
#         back_button.pack(fill='x')

#     def set_directory(self):
#         directory = filedialog.askdirectory()
#         self.settings.set('output_dir', directory)

#     def settings_menu(self):
#         pass  # Here you can add code to handle other settings


# if __name__ == '__main__':
#     app = App()
