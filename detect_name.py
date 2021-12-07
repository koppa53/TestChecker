#from tensorflow.keras.models import load_model
#from imutils.contours import sort_contours
import numpy as np
import argparse
import imutils
import cv2 as cv

import pytesseract as pyt


"""def tensorflow_handwritten_detection(image_path):

    model = load_model("handwriting.model")

    cover_image = cv.imread(image_path)
    x = 360
    y = 0
    h = 300
    w = 900 
    image = cover_image[y:y+h, x:x+w]
    scale_percent = 100  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv.resize(image, dim, interpolation=cv.INTER_AREA)

    gray = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    # perform edge detection, find contours in the edge map, and sort the
    # resulting contours from left-to-right
    edged = cv.Canny(blurred, 30, 150)
    cnts = cv.findContours(edged.copy(), cv.RETR_EXTERNAL,
        cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sort_contours(cnts, method="left-to-right")[0]

    chars = []

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv.boundingRect(c)
        # filter out bounding boxes, ensuring they are neither too small
        # nor too large
        if (w >= 5 and w <= 150) and (h >= 15 and h <= 120):
            # extract the character and threshold it to make the character
            # appear as *white* (foreground) on a *black* background, then
            # grab the width and height of the thresholded image
            roi = gray[y:y + h, x:x + w]
            thresh = cv.threshold(roi, 0, 255,
                cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
            (tH, tW) = thresh.shape
            # if the width is greater than the height, resize along the
            # width dimension
            if tW > tH:
                thresh = imutils.resize(thresh, width=32)
            # otherwise, resize along the height
            else:
                thresh = imutils.resize(thresh, height=32)
            
            # re-grab the image dimensions (now that its been resized)
            # and then determine how much we need to pad the width and
            # height such that our image will be 32x32
            (tH, tW) = thresh.shape
            dX = int(max(0, 32 - tW) / 2.0)
            dY = int(max(0, 32 - tH) / 2.0)
            # pad the image and force 32x32 dimensions
            padded = cv.copyMakeBorder(thresh, top=dY, bottom=dY,
                left=dX, right=dX, borderType=cv.BORDER_CONSTANT,
                value=(0, 0, 0))
            padded = cv.resize(padded, (32, 32))
            # prepare the padded image for classification via our
            # handwriting OCR model
            padded = padded.astype("float32") / 255.0
            padded = np.expand_dims(padded, axis=-1)
            # update our list of characters that will be OCR'd
            chars.append((padded, (x, y, w, h)))

    # extract the bounding box locations and padded characters
    boxes = [b[1] for b in chars]
    chars = np.array([c[0] for c in chars], dtype="float32")
    # OCR the characters using our handwriting recognition model
    preds = model.predict(chars)
    # define the list of label names
    labelNames = "0123456789"
    labelNames += "abcdefghijklmnopqrstuvwxyz"
    labelNames = [l for l in labelNames]

    # loop over the predictions and bounding box locations together
    for (pred, (x, y, w, h)) in zip(preds, boxes):
        # find the index of the label with the largest corresponding
        # probability, then extract the probability and label
        i = np.argmax(pred)
        prob = pred[i]
        label = labelNames[i]

        # draw the prediction on the image
        print("[INFO] {} - {:.2f}%".format(label, prob * 100))
        cv.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv.putText(resized, label, (x - 10, y - 10),
            cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv.imshow("result", resized)
    cv.waitKey(0)
"""
def name_detection(image_path):
    cover_image = cv.imread(image_path)
    x = 360
    y = 0
    h = 300
    w = 900 
    image = cover_image[y:y+h, x:x+w]
    scale_percent = 100  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv.resize(image, dim, interpolation=cv.INTER_AREA)


    pyt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    grayscale = cv.cvtColor(resized, cv.COLOR_BGR2GRAY)

    threshold = cv.threshold(grayscale, 0, 255, cv.THRESH_OTSU)[1]

    configure = r'-l eng --oem 3 --psm 12'

    content = pyt.image_to_data(
        threshold, output_type=pyt.Output.DICT, config=configure)
    total_length = len(content["text"])

    #cv.imshow("images", threshold)

    print(content)

    for i in range(total_length):
        if int(float(content["conf"][i])) > 30:
            x, y, w, h = (content["left"][i], content["top"]
                        [i], content["width"][i], content["height"][i])
            resized = cv.rectangle(resized, (x, y), ((x+w), (y+h)), (0, 255, 0), 2)

    for j in content["text"]:
        if(j != ""):
            print(j)

    cv.imshow("image", resized)
    cv.waitKey(0)


name_detection("Answer Sheets/james_harden.jpg")