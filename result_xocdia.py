# ocr_extract_points.py
# pip install opencv-python pytesseract

import cv2
import pytesseract

# ===== CONFIG =====
image_path = "out/output_otsu.png"

# Toạ độ: (x1, y1, x2, y2)
coords = {
    "e_value": (320, 440, 400, 495),
    "o_value": (431, 441, 553, 504),
    "participants": (765, 425, 912, 467),
    "total_bet": (762, 469, 915, 517),
}
# ==================

# Đọc ảnh gốc
img = cv2.imread(image_path)
if img is None:
    raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

def ocr_region(image, region, digits_only=False):
    """Cắt theo region, tiền xử lý và OCR"""
    x1, y1, x2, y2 = region
    roi = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = '--oem 3 --psm 6'
    if digits_only:
        config += ' digits'
    text = pytesseract.image_to_string(thresh, config=config)
    return text.strip()

# Extract từng giá trị
results = {
    "e_value": ocr_region(img, coords["e_value"], digits_only=True),
    "o_value": ocr_region(img, coords["o_value"], digits_only=True),
    "participants": ocr_region(img, coords["participants"], digits_only=True),
    "total_bet": ocr_region(img, coords["total_bet"]),
}

# In kết quả
for k, v in results.items():
    print(f"{k}: {v}")
