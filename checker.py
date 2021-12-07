import cv2 as cv
import numpy as np
import os

original_answer_key_image = []
original_answer_sheet_image = []


def test_checker(answer, processed_answer_key):
    global original_answer_key_image, original_answer_sheet_image
    answer_key_contours = get_answer_key_contours(
        processed_answer_key, original_answer_key_image)
    get_answer_sheet_scores(
        answer, original_answer_sheet_image, answer_key_contours)


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


def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def get_answer_sheet_scores(answer_sheet, original_sheet_image, correct_answers):
    answer_sheet_contours = []
    all_contours = []
    n = 0
    a = 0
    items = len(correct_answers)
    for img in answer_sheet:
        correct = 0
        answer_sheet_contours = []
        thresh = cv.threshold(img, 100, 255,
                              cv.THRESH_OTSU)[1]
        cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL,
                                  cv.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv.boundingRect(c)
            if w > 40 and w < 100 and h > 30 and h < 43:
                # cv.putText(original_sheet_image[n], str(a), (x, y),
                #           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                # BGR = np.array(
                #    cv.mean(original_sheet_image[n][y:y+h, x:x+w])).astype(np.uint8)
                # if BGR[0] < 210:
                # cv.rectangle(original_sheet_image[n],
                #            (x, y), (x+w, y+h), (0, 255, 0), 2)
                answer_sheet_contours.append(c)
                #a += 1
        answer_sheet_contours.sort(
            key=lambda x: get_contour_precedence(x, thresh.shape[1]))
        for i in range(len(answer_sheet_contours)):
            x, y, w, h = cv.boundingRect(answer_sheet_contours[i])
            imS = cv.putText(original_sheet_image[n], str(i), (x, y),
                             cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            BGR = np.array(
                cv.mean(original_sheet_image[n][y:y+h, x:x+w])).astype(np.uint8)
            if BGR[0] < 210:
                if i in correct_answers:
                    cv.rectangle(original_sheet_image[n],
                                 (x, y), (x+w, y+h), (0, 255, 0), 2)
                    correct += 1
                else:
                    cv.rectangle(original_sheet_image[n],
                                 (x, y), (x+w, y+h), (0, 0, 255), 2)
        # Resize image
        imS = cv.resize(original_sheet_image[n], (800, 940))
        plot_score(imS, correct, items, n)
        #cv.imshow("outputs"+str(n), imS)
        cv.imshow("outputs"+str(n),
                  cv.resize(thresh, (800, 940)))
        all_contours.append(answer_sheet_contours)
        n = n+1

    return all_contours


def get_answer_key_contours(answer_key, original_key):
    answer_key_contours = []
    correct_answers = []

    thresh = cv.threshold(answer_key, 100, 255,
                          cv.THRESH_OTSU)[1]
    cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL,
                              cv.CHAIN_APPROX_SIMPLE)
    n = 0
    for c in cnts:
        x, y, w, h = cv.boundingRect(c)
        if w > 40 and w < 100 and h > 30 and h < 43:
            BGR = np.array(
                cv.mean(original_key[y:y+h, x:x+w])).astype(np.uint8)
            if BGR[0] < 210:
                cv.rectangle(original_key,
                             (x, y), (x+w, y+h), (0, 255, 0), 2)
            answer_key_contours.append(c)
        n += 1
    answer_key_contours.sort(
        key=lambda x: get_contour_precedence(x, thresh.shape[1]))
    imS = cv.resize(original_key, (800, 940))
    for i in range(len(answer_key_contours)):
        x, y, w, h = cv.boundingRect(answer_key_contours[i])
        # imS = cv.putText(original_key, str(i), (x, y),
        #                 cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        BGRs = np.array(
            cv.mean(original_key[y:y+h, x:x+w])).astype(np.uint8)
        if BGRs[0] < 210:
            # cv.putText(original_key, str(n), (x, y),
            #           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            correct_answers.append(i)
    # Resize image
    imS = cv.resize(imS, (800, 940))
    cv.imshow("output", imS)

    return correct_answers


def preprocess_image(answer_sheets, answer_key):

    processed_answer_sheets = []

    gray = cv.cvtColor(answer_key, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    processed_answer_key = cv.Canny(blurred, 75, 200)

    for img in answer_sheets:
        g = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        b = cv.GaussianBlur(g, (5, 5), 0)
        e = cv.Canny(b, 75, 150)
        processed_answer_sheets.append(e)

    return processed_answer_sheets, processed_answer_key


def load_images(answer_sheet_path, answer_key_path):
    global original_answer_key_image, original_answer_sheet_image
    collected_answer_sheets = []

    answer_key = cv.imread(answer_key_path)
    original_answer_key_image = answer_key

    for filename in os.listdir(answer_sheet_path):
        image = cv.imread(os.path.join(answer_sheet_path, filename))
        if image is not None:
            resizedimage = cv.resize(image, (1200, 1500), cv.INTER_AREA)
            collected_answer_sheets.append(resizedimage)

    original_answer_sheet_image = collected_answer_sheets
    return collected_answer_sheets, answer_key


answer_sheets, answer_key = load_images(
    "D:/Documents/Python Projects/TestChecker/Answer Sheets", "D:/Documents/Python Projects/TestChecker/Answer Key/1.png")
processed_answer_sheets, processed_answer_key = preprocess_image(
    answer_sheets, answer_key)
test_checker(processed_answer_sheets, processed_answer_key)
cv.waitKey(0)
