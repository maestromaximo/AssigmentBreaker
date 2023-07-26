import pytest
from PIL import Image
from main import detect_question_number  # Assuming the name of your main script is main.py

# List of tuples for test data - format (image_path, expected_result)
testdata = [
    ("test_image_1.png", 1),  # An image with a visible '1' at the top right
    ("test_image_2.png", 2),  # An image with a visible '2' at the top right
    ("test_image_3.png", 3),  # An image with a visible '3' at the top right
    ("test_image_i.png", 1),  # An image with a visible 'i' at the top right
    ("test_image_blank.png", None),  # An image with no number at the top right
    ("test_image_no_number.png", None),  # An image with text but no number at the top right
]

@pytest.mark.parametrize("image_path,expected_result", testdata)
def test_detect_question_number(image_path, expected_result):
    image = Image.open(image_path)
    result = detect_question_number(image, 1, debug=False)
    assert result == expected_result

#C:\Python311\python.exe -m pytest test_main.py
