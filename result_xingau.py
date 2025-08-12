# ocr_extract_bstp.py
# pip install opencv-python pytesseract

import cv2
import pytesseract

# ==== CONFIG ====
image_path = "out/output_otsu.png"  # Đường dẫn ảnh mới
coords = {
    "b_value": (322, 448, 403, 503),
    "s_value": (429, 446, 502, 501),
    "t_value": (547, 445, 651, 503),
    "participants": (784, 425, 918, 465),
    "total_bet": (781, 470, 918, 513),
}
# ===============

def ocr_region(image, region, digits_only=False):
    """Cắt ảnh theo tọa độ, tiền xử lý và OCR."""
    x1, y1, x2, y2 = region
    roi = image[y1:y2, x1:x2]

    # Tiền xử lý: grayscale + blur + otsu threshold
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR config
    config = '--oem 3 --psm 6'
    if digits_only:
        config += ' digits'

    text = pytesseract.image_to_string(th, config=config)
    return text.strip()

if __name__ == "__main__":
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

    results = {}
    for key, box in coords.items():
        results[key] = ocr_region(img, box, digits_only=(key != "total_bet"))

    for key, val in results.items():
        print(f"{key}: {val}")
