"""
    OMR (Optical Mark Recognition) Bubble Sheets Checker Using OpenCV Python
    Name Detection Module
    Authors:
        JUSTINE BALDOVINO
        JEFFERSON CLEMENTE
        EXEQUIEL LUSTAN
        JHOSUA MOSTAR
    A requirement for CS Elective Computer Vision BSCS-4C.
"""
import numpy as np
import cv2 as cv

import pytesseract as pyt


def name_detection(cover_image):
    x = 110
    y = 0
    h = 115
    w = 300
    image = cover_image[y:y+h, x:x+w]

    """scale_percent = 100  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)"""

    pyt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(grayscale, (3, 3), 0)
    threshold = cv.threshold(blurred, 0, 255, cv.THRESH_OTSU)[1]

    configure = r'-l eng --oem 3 --psm 12'

    content = pyt.image_to_data(
        threshold, output_type=pyt.Output.DICT, config=configure)
    total_length = len(content["text"])

    for i in range(total_length):
        if int(float(content["conf"][i])) > 30:
            x, y, w, h = (content["left"][i], content["top"]
                          [i], content["width"][i], content["height"][i])
            #image = cv.rectangle(image, (x, y), ((x+w), (y+h)), (0, 255, 0), 2)

    fullName = ""
    for j in content["text"]:
        if(j != ""):
            fullName = fullName + " " + j

    return fullName
