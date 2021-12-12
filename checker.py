"""
    OMR (Optical Mark Recognition) Bubble Sheets Using OpenCV Python
    Authors:
        JUSTINE BALDOVINO
        JEFFERSON CLEMENTE
        EXEQUIEL LUSTAN
        JHOSUA MOSTAR
    A requirement for CS Elective Computer Vision BSCS-4C.
"""
import cv2 as cv
import numpy as np
import os
import detect_name
from datetime import datetime

original_answer_key_image = []
original_answer_sheet_image = []
totalScores = 0
passed = 0


def load_images(answer_sheet_path, answer_key_path):
    """
        @param answer_sheet_path - Answer Sheets Folder Path
        @param answer_key_path - Answer Key File Path

        This load_images function loads all necessary images needed for processing
        and all images loaded are resized to 1200 x 1500.

        Returns Answer Sheet Images (Array), Answer Key Image
    """
    global original_answer_key_image, original_answer_sheet_image
    collected_answer_sheets = []

    answer_key = cv.imread(answer_key_path)
    original_answer_key_image = cv.resize(
        answer_key, (1200, 1500), cv.INTER_AREA)

    for filename in os.listdir(answer_sheet_path):
        image = cv.imread(os.path.join(answer_sheet_path, filename))
        if image is not None:
            resizedimage = cv.resize(image, (1200, 1500), cv.INTER_AREA)
            collected_answer_sheets.append(resizedimage)

    original_answer_sheet_image = collected_answer_sheets
    return collected_answer_sheets, original_answer_key_image


def preprocess_image(answer_sheets, answer_key):
    """
        @param answer_sheets - Collected Answer Sheets Images
        @param answer_key - Answer Key Image

        The preprocess_image function will make premilinary processes
        to the image for further image processing (contour detection).
        The premilinary processes are:
            GRAYSCALING , BLURING , CANNY EDGE DETECTION.

        Returns Preprocessed Answer Sheets (Array), Preprocessed Answer Key
    """
    processed_answer_sheets = []

    gray = cv.cvtColor(answer_key, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    processed_answer_key = cv.Canny(blurred, 75, 150)

    for img in answer_sheets:
        g = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        b = cv.GaussianBlur(g, (5, 5), 0)
        e = cv.Canny(b, 75, 150)
        processed_answer_sheets.append(e)

    return processed_answer_sheets, processed_answer_key


def test_checker(processed_answer_sheet, processed_answer_key):
    """
        @param processed_answer_sheet - Preprocessed answer sheet images.
        @param processed_answer_key - Preprocessed answer key.

        The function test_checker will now perform FUNCTION CALLS for the checking of
        preprocessed images of answer sheet and answer key. Both images are CROPPED
        based on THREE columns of the two image to find the bubbles and passed to
        get_answer_keys and check_answer_sheet functions.
    """
    global original_answer_key_image, original_answer_sheet_image

    correct_answers_list = get_answer_keys(
        processed_answer_key, original_answer_key_image)

    items = sum(len(i) for i in correct_answers_list)

    for i in range(len(processed_answer_sheet)):

        firstCol = crop_image(
            processed_answer_sheet[i], 80, 300, processed_answer_sheet[i].shape[1], 300)
        secCol = crop_image(
            processed_answer_sheet[i], 450, 300, processed_answer_sheet[i].shape[1], 300)
        thirdCol = crop_image(
            processed_answer_sheet[i], 820, 310, processed_answer_sheet[i].shape[1], 310)

        process_1, correct_answers = check_answer_sheet(
            firstCol, original_answer_sheet_image[i], correct_answers_list[0], 80, 300)
        process_2 = process_1
        process_2, correct_answers2 = check_answer_sheet(
            secCol, original_answer_sheet_image[i], correct_answers_list[1], 450, 300)
        final_process = process_2
        final_process, correct_answers3 = check_answer_sheet(
            thirdCol, original_answer_sheet_image[i], correct_answers_list[2], 820, 310)

        plot_score(
            cv.resize(final_process, (800, 900)), (correct_answers+correct_answers2+correct_answers3), items, i)


def get_answer_keys(answer_key, original_key):
    """
        @param answer_key - Preprocessed Answer Key Image.
        @param original_key - Original Answer Key Image.

        The get_answer_keys function performs:
            CROPPING - to remove uncessesary features in the image for contour detection,
            CONTOUR DETECTION
            FILTER CONTOURS - for finding bubbles in the image and shaded bubbles as correct answers.

        Returns Correct Answers List (Array)
    """

    firstCol = crop_image(answer_key, 80, 300, answer_key.shape[1], 300)
    secCol = crop_image(answer_key, 450, 300, answer_key.shape[1], 300)
    thirdCol = crop_image(answer_key, 820, 310, answer_key.shape[1], 310)

    answer_key_bubbles = get_bubbles(firstCol)
    answer_key_bubbles2 = get_bubbles(secCol)
    answer_key_bubbles3 = get_bubbles(thirdCol)

    process_1, correct_answers = get_shaded(
        answer_key_bubbles, original_key, 80, 300)
    process_2 = process_1
    process_2, correct_answers2 = get_shaded(
        answer_key_bubbles2, original_key, 450, 300)
    process_3 = process_2
    process_3, correct_answers3 = get_shaded(
        answer_key_bubbles3, original_key, 820, 310)

    # Resize image
    image = cv.resize(process_3, (800, 900))
    cv.imshow("Answer Key", image)

    correct_answers_list = np.array(
        (correct_answers, correct_answers2, correct_answers3
         ), dtype=object)
    return correct_answers_list


def crop_image(image, x_coord, y_coord, height, width):
    """
        @param image - Image Source/File
        @param x_coord - X coordinate in image Pixel
        @param y_coord - Y coordinate in image Pixel
        @param height - Height size of crop image
        @param width - Width size of crop image

        The crop_image function performs basic image CROPPING.

        Returns Cropped Image
    """
    return image[y_coord:y_coord+height, x_coord:x_coord+width]


def get_bubbles(image):
    """
        @param image - Image Source/File

        The get_bubbles functions performs THRESHOLDING and CONTOUR DETECTION.
        CONTOURS are sorted using the BOUNDING RECT of itself filtering based on
        WIDTH and HEIGHT.
        FILTERED CONTOURS are sorted using functions sort() and
        get_contour_precedence()

        Returns Sorted Bubbles (Array)
    """
    global n
    thresh = cv.threshold(image, 100, 255,
                          cv.THRESH_OTSU)[1]
    cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL,
                              cv.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for c in range(len(cnts)):
        x, y, w, h = cv.boundingRect(cnts[c])
        if w > 48 and w < 60 and h > 30:
            bubbles.append(cnts[c])

    bubbles.sort(
        key=lambda x: get_contour_precedence(x, thresh.shape[1]))

    return bubbles


def get_contour_precedence(contour, cols):
    """
        @param contour - Image contours
        @param cols - Image height

        The get_contour_precedence function is used to sorts the contours from left-to-right
        and top-to-bottom by calculating based on X and Y coordinates of contours with a
        tolerance factor.

        Returns (numeric value)
    """
    tolerance_factor = 65
    origin = cv.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def get_shaded(answer_key_contours, original_answer_key_image, x_coord, y_coord):
    """
        @param answer_key_contours - contours of bubble answer sheet image
        @param original_answer_key_image - answer key image
        @param x_coord - x coordinate in image pixel
        @param y_coord - y coordinate in image pixel

        The get_shaded function performs filtering of shaded bubbles by using
        boundingRect(), cv.mean() to get average color value in an certain are of image using
        the return values of bounding rect and filtered according to its values, adding a
        rectangle marker to the image.

        Returns marked original image, corrects answers index list (Array)
    """
    correct_answers = []

    for i in range(len(answer_key_contours)):
        x, y, w, h = cv.boundingRect(answer_key_contours[i])
        x = x + x_coord
        y = y + y_coord
        # cv.putText(original_answer_key_image, str(i), (x, y),
        #           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        BGRs = np.array(
            cv.mean(original_answer_key_image[y:y+h, x:x+w])).astype(np.uint8)
        if BGRs[0] < 210:
            cv.rectangle(original_answer_key_image,
                         (x, y), (x+w, y+h), (0, 255, 0), 2)
            correct_answers.append(i)

    return original_answer_key_image, correct_answers


def check_answer_sheet(croppped_image, original_answer_sheet_image, correct_answers, x_coord, y_coord):
    """
        @param cropped_image - cropped image source/file
        @param original_answer_sheet_image - original answer sheet image/file
        @param correct_answers - correct answers index list

        The function check_answer_sheet performs function calls to get_bubbles() and
        check_shaded().

        Returns Marked Answer Sheet, Correct Answers (Numeric Value)
    """
    answer_sheet_bubbles = get_bubbles(croppped_image)

    processed_image, correct_answers = check_shaded(
        answer_sheet_bubbles, original_answer_sheet_image, correct_answers, x_coord, y_coord)

    return processed_image, correct_answers


def check_shaded(contours, original_image, correct_answers, x_coord, y_coord):
    """
        @param contours - image contours
        @param original_image - original image
        @param correct_answers - correct answers list
        @param x_coord - x coordinate in image pixel
        @param y_coord - y coordinate in image pixel

        The check_shaded function uses boundingRect() and cv.mean() function for checking
        the answer sheets to find and check color average color values within the region in the image.
        Using B values in (BGR) it determines if the region is shaded or not. If shaded it matches to
        the correct answers list if it has same index.

        Returns checked answer sheet image, correct answers (Numeric)
    """
    correct = 0
    for i in range(len(contours)):
        x, y, w, h = cv.boundingRect(contours[i])
        x = x + x_coord
        y = y + y_coord
        checked_image = original_image
        # cv.putText(checked_image, str(i), (x, y),
        #           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        BGR = np.array(
            cv.mean(checked_image[y:y+h, x:x+w])).astype(np.uint8)
        if BGR[0] < 210:
            if i in correct_answers:
                cv.rectangle(checked_image,
                             (x, y), (x+w, y+h), (0, 255, 0), 2)
                correct += 1
            else:
                cv.rectangle(checked_image,
                             (x, y), (x+w, y+h), (0, 0, 255), 2)
    return checked_image, correct


def plot_score(imS, correct, items, n):
    """
        @param imS - image source/file
        @param correct - total correct score
        @param items - total items in answer sheet
        @param n - counter

        The plot_score function writes total score in the answer sheet image.
        Using putText() function.
    """
    global passed
    current_directory = os.getcwd()
    now = datetime.now()

    average = int(items*0.75)
    if correct < average:
        cv.putText(imS, str(correct), (600, 140),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        passed += 1
        cv.putText(imS, str(correct), (600, 140),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv.putText(imS, "__", (600, 145),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv.putText(imS, str(items), (600, 175),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    fullName = detect_name.name_detection(imS)
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
    #cv.putText(imS,fullName, (200, 120),cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    with open('ScoreSheet.txt', 'a') as the_file:
        the_file.write(str(n+1)+". "+fullName + " - " + str(correct) +
                       ", " + dt_string + "\n")

    save_path = current_directory + r"\Results"
    cv.imwrite(os.path.join(
        save_path, f'{fullName}_CHKD_{dt_string}.jpg'), imS)
    cv.imshow("outsput" + str(n), imS)


def getPassing():
    global original_answer_sheet_image, passed
    number_of_students = len(original_answer_sheet_image)
    passed_students = passed
    passing = round((passed_students / number_of_students) * 100, 2)
    return passing


# answer_sheets, answer_key = load_images(
#     "C:/Users/tlust/Desktop/TestChecker_2/TestChecker/Answer Sheets", "C:/Users/tlust/Desktop/TestChecker_2/TestChecker/Answer Key/1.png")
# processed_answer_sheets, processed_answer_key = preprocess_image(
#     answer_sheets, answer_key)
# test_checker(processed_answer_sheets, processed_answer_key)
cv.waitKey(0)
