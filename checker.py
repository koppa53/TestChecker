import cv2 as cv
import numpy as np
import os

original_answer_key_image = []
original_answer_sheet_image = []


def test_checker(answer, answer_key):
    global original_answer_key_image
    answer_key_contours = get_answer_key_contours(
        answer_key, original_answer_key_image)
    n = 0
    for img in answer:
        correct, items = 0, 0
        for c in answer_key_contours:
            x, y, w, h = cv.boundingRect(c)
            BGR = np.array(
                cv.mean(img[y:y+h, x:x+w])).astype(np.uint8)
            if BGR[0] < 150:
                cv.rectangle(img,
                             (x, y), (x+w, y+h), (0, 255, 0), 2)
                correct += 1
            else:
                cv.rectangle(img,
                             (x, y), (x+w, y+h), (0, 0, 255), 2)
            items += 1
        # Resize image
        imS = cv.resize(img, (800, 940))
        plot_score(imS, correct, items, n)
        n = n + 1

    cv.waitKey(0)


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


def get_answer_key_contours(answer_key, original_key):
    answer_key_contours = []

    thresh = cv.threshold(answer_key, 100, 255,
                          cv.THRESH_OTSU)[1]
    cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL,
                              cv.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        x, y, w, h = cv.boundingRect(c)
        if w > 40 and h > 30:
            BGR = np.array(
                cv.mean(original_key[y:y+h, x:x+w])).astype(np.uint8)
            if BGR[0] < 150:
                cv.rectangle(original_key,
                             (x, y), (x+w, y+h), (0, 255, 0), 2)
                answer_key_contours.append(c)
    # Resize image
    imS = cv.resize(original_key, (800, 940))
    cv.imshow("output", imS)

    return answer_key_contours


def preprocess_image(answer_sheets, answer_key):

    processed_answer_sheets = []

    gray = cv.cvtColor(answer_key, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    processed_answer_key = cv.Canny(blurred, 75, 200)

    for img in answer_sheets:
        g = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        b = cv.GaussianBlur(g, (5, 5), 0)
        e = cv.Canny(b, 75, 200)
        processed_answer_sheets.append(e)

    return processed_answer_sheets, processed_answer_key


def load_images(answer_sheet_path, answer_key_path):
    global original_answer_key_image, original_answer_sheet_image
    collected_answer_sheets = []

    answer_key = cv.imread(answer_key_path)
    original_answer_key_image = answer_key

    for filename in os.listdir(answer_sheet_path):
        image = cv.imread(os.path.join(answer_sheet_path, filename))
        resizedimage = cv.resize(image, (1200, 1500))
        if image is not None:
            collected_answer_sheets.append(resizedimage)

    original_answer_sheet_image = collected_answer_sheets
    return collected_answer_sheets, answer_key


"""answer_sheets, answer_key = load_images()
answer_key = preprocess_image(answer_key)
test_checker(answer_sheets, answer_key)"""
