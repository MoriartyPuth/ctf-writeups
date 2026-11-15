import cv2
import numpy as np
import pytesseract

img = cv2.imread("flag.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
enhanced = clahe.apply(gray)

big = cv2.resize(enhanced, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

denoised = cv2.fastNlMeansDenoising(big, None, 10, 7, 21)

kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
sharpened = cv2.filter2D(denoised, -1, kernel)

_, thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh_inv = cv2.bitwise_not(thresh)

text = pytesseract.image_to_string(thresh_inv, config="--psm 6 --oem 3")
print("OCR Result:")
print(text)
