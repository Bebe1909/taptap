# ocr_extract_values.py
# pip install opencv-python pytesseract

import cv2
import pytesseract

# ==== CONFIG ====
image_path = "out/output_otsu.png"  # đổi thành đường dẫn ảnh của bạn

# Toạ độ: (x1, y1, x2, y2)
coords = {
    "b_value": (321, 444, 404, 493),
    "p_value": (430, 444, 504, 498),
    "t_value": (547, 443, 650, 502),
    "participants": (762, 425, 917, 469),
    "total_bet": (762, 468, 918, 517),
}
# ===============

# Load ảnh
img = cv2.imread(image_path)
if img is None:
    raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

def ocr_region(image, region, digits_only=False):
    """Cắt ảnh theo region, tiền xử lý và OCR."""
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

# OCR cho từng giá trị
results = {
    "b_value": ocr_region(img, coords["b_value"], digits_only=True),
    "p_value": ocr_region(img, coords["p_value"], digits_only=True),
    "t_value": ocr_region(img, coords["t_value"], digits_only=True),
    "participants": ocr_region(img, coords["participants"], digits_only=True),
    "total_bet": ocr_region(img, coords["total_bet"]),
}

# In kết quả
for key, val in results.items():
    print(f"{key}: {val}")
