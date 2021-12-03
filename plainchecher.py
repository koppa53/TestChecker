import cv2 as cv
import numpy as np
import os
# changes
# qweeqweqeqw


def test_checker(answer, answer_key):
    answer_key_contours = get_answer_key_contours(answer_key)
    correct, items = 0, 0
    for img in answer:
        for c in answer_key_contours:
            x, y, w, h = cv.boundingRect(c)
            BGR = np.array(
                cv.mean(img[y:y+h, x:x+w])).astype(np.uint8)
            if BGR[0] < 100:
                cv.rectangle(img,
                             (x, y), (x+w, y+h), (0, 255, 0), 2)
                correct += 1
            else:
                cv.rectangle(img,
                             (x, y), (x+w, y+h), (0, 0, 255), 2)
            items += 1
        print(f"Total Score: {correct}, out of {items}")
        # Resize image
        imS = cv.resize(img, (800, 940))
        cv.imshow("outsput", imS)

    cv.waitKey(0)


def get_answer_key_contours(answer_key):
    global original_key
    answer_key_contours = []
    for img in answer_key:
        thresh = cv.threshold(img, 100, 255,
                              cv.THRESH_OTSU)[1]
        cnts, _ = cv.findContours(thresh, cv.RETR_EXTERNAL,
                                  cv.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            x, y, w, h = cv.boundingRect(c)
            if w > 40 and h > 30:
                BGR = np.array(
                    cv.mean(original_key[0][y:y+h, x:x+w])).astype(np.uint8)
                if BGR[0] < 100:
                    cv.rectangle(original_key[0],
                                 (x, y), (x+w, y+h), (0, 255, 0), 2)
                    answer_key_contours.append(c)
        # Resize image
        imS = cv.resize(original_key[0], (800, 940))
        cv.imshow("output", imS)

    return answer_key_contours


def preprocess_image(answer_key):
    preprocessed_answer_key = []

    for img in answer_key:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (5, 5), 0)
        edged = cv.Canny(blurred, 75, 200)
        preprocessed_answer_key.append(edged)

    return preprocessed_answer_key


def load_images():
    collected_answer_sheets = []
    collected_answer_key = []
    for filename in os.listdir("Answer Key"):
        image = cv.imread(os.path.join("Answer Key", filename))
        if image is not None:
            collected_answer_key.append(image)

    for filename in os.listdir("Answer Sheets"):
        image = cv.imread(os.path.join("Answer Sheets", filename))
        if image is not None:
            collected_answer_sheets.append(image)

    return collected_answer_sheets, collected_answer_key


answer_sheets, answer_key = load_images()
original_key = answer_key
answer_key = preprocess_image(answer_key)
test_checker(answer_sheets, answer_key)
