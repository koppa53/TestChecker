import cv2 as cv
import numpy as np
import os

original_answer_key_image = []
original_answer_sheet_image = []


def load_images(answer_sheet_path, answer_key_path):
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
            processed_answer_sheet[i], 820, 300, processed_answer_sheet[i].shape[1], 300)

        process_1, correct_answers = check_answer_sheet(
            firstCol, original_answer_sheet_image[i], correct_answers_list[0], 80, 300)
        process_2 = process_1
        process_2, correct_answers2 = check_answer_sheet(
            secCol, original_answer_sheet_image[i], correct_answers_list[1], 450, 300)
        final_process = process_2
        final_process, correct_answers3 = check_answer_sheet(
            thirdCol, original_answer_sheet_image[i], correct_answers_list[2], 820, 300)

        plot_score(
            cv.resize(final_process, (800, 900)), (correct_answers+correct_answers2+correct_answers3), items, i)


def get_answer_keys(answer_key, original_key):

    firstCol = crop_image(answer_key, 80, 300, answer_key.shape[1], 300)
    secCol = crop_image(answer_key, 450, 300, answer_key.shape[1], 300)
    thirdCol = crop_image(answer_key, 820, 300, answer_key.shape[1], 300)

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
        answer_key_bubbles3, original_key, 820, 300)

    # Resize image
    image = cv.resize(process_3, (800, 900))
    cv.imshow("Answer Key", image)

    correct_answers_list = np.array(
        (correct_answers, correct_answers2, correct_answers3
         ), dtype=object)
    return correct_answers_list


def crop_image(image, x_coord, y_coord, height, width):

    return image[y_coord:y_coord+height, x_coord:x_coord+width]


def get_bubbles(image):
    thresh = cv.threshold(image, 100, 255,
                          cv.THRESH_OTSU)[1]
    cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL,
                              cv.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for c in cnts:
        x, y, w, h = cv.boundingRect(c)
        if w > 40 and h > 30:
            bubbles.append(c)

    bubbles.sort(
        key=lambda x: get_contour_precedence(x, thresh.shape[1]))

    return bubbles


def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def get_shaded(answer_key_contours, original_answer_key_image, x_coord, y_coord):
    correct_answers = []

    for i in range(len(answer_key_contours)):
        x, y, w, h = cv.boundingRect(answer_key_contours[i])
        x = x + x_coord
        y = y + y_coord
        cv.putText(original_answer_key_image, str(i), (x, y),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        BGRs = np.array(
            cv.mean(original_answer_key_image[y:y+h, x:x+w])).astype(np.uint8)
        if BGRs[0] < 210:
            cv.rectangle(original_answer_key_image,
                         (x, y), (x+w, y+h), (0, 255, 0), 2)
            correct_answers.append(i)

    return original_answer_key_image, correct_answers


def check_answer_sheet(croppped_image, original_answer_sheet_image, correct_answers, x_coord, y_coord):

    answer_sheet_bubbles = get_bubbles(croppped_image)

    processed_image, correct_answers = check_shaded(
        answer_sheet_bubbles, original_answer_sheet_image, correct_answers, x_coord, y_coord)

    return processed_image, correct_answers


def check_shaded(contours, original_image, correct_answers, x_coord, y_coord):
    correct = 0
    for i in range(len(contours)):
        x, y, w, h = cv.boundingRect(contours[i])
        x = x + x_coord
        y = y + y_coord
        checked_image = original_image
        cv.putText(checked_image, str(i), (x, y),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
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
    average = int(items*0.75)
    if correct < average:
        cv.putText(imS, str(correct), (600, 140),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv.putText(imS, str(correct), (600, 140),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv.putText(imS, "__", (600, 145),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv.putText(imS, str(items), (600, 175),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv.imshow("outsput" + str(n), imS)


answer_sheets, answer_key = load_images(
    "D:/Documents/Python Projects/TestChecker/Answer Sheets", "D:/Documents/Python Projects/TestChecker/Answer Key/1.png")
processed_answer_sheets, processed_answer_key = preprocess_image(
    answer_sheets, answer_key)
test_checker(processed_answer_sheets, processed_answer_key)
cv.waitKey(0)
