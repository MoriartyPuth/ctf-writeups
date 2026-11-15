import cv2

img = cv2.imread("flag.png")
blur = cv2.Laplacian(img, cv2.CV_64F).var()
print(f"Laplacian variance: {blur:.2f}")
if blur > 100:
    print("Image is sharp — blur is purely CSS")
else:
    print("Image is actually blurry in the pixel data")
