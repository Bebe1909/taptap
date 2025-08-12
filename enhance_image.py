# enhance_for_tesseract_full.py
# pip install opencv-python pillow numpy scikit-image

import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from skimage.filters import threshold_sauvola

# ==== CONFIG ====
INPUT  = "images/screenshot_20250811_234232_cropped.png"
OUTPUT_BASE = "out/output"   # KHÔNG có đuôi; tool sẽ sinh _rescaled.png, _otsu.png...
TARGET_XHEIGHT = 26
MIN_SCALE, MAX_SCALE = 0.75, 3.0
SAVE_DPI = 300
# Binarisation knobs
ADAPTIVE_OTSU_BLOCK = 64      # 32/64/128
SAUVOLA_WINDOW = 25           # 15–51 (lẻ)
SAUVOLA_K = 0.2               # 0.2–0.5
# ================

def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def estimate_char_height(gray: np.ndarray) -> float | None:
    g = cv2.GaussianBlur(gray, (3,3), 0)
    _, bin_ = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if bin_.mean() > 127:
        bin_ = 255 - bin_
    bin_ = cv2.morphologyEx(bin_, cv2.MORPH_OPEN, np.ones((2,2), np.uint8))
    num, labels, stats, _ = cv2.connectedComponentsWithStats(255 - bin_, connectivity=8)
    heights = []
    for i in range(1, num):
        x, y, w, h, area = stats[i]
        if 2 <= h <= gray.shape[0]*0.25 and 2 <= w <= gray.shape[1]*0.25 and area >= 8:
            heights.append(h)
    return float(np.median(heights)) if heights else None

def rescale_for_ocr(img_bgr: np.ndarray, target_xheight: int = TARGET_XHEIGHT) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h_est = estimate_char_height(gray)
    if not h_est:
        s = 2.0 if max(img_bgr.shape[:2]) < 1200 else 1.0
    else:
        s = target_xheight / h_est
        s = max(MIN_SCALE, min(MAX_SCALE, s))
    if s > 1.0:
        out = cv2.resize(img_bgr, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
    elif s < 1.0:
        k = max(1, int(round(1.0/s)) // 2 * 2 + 1)  # kernel lẻ
        blurred = cv2.GaussianBlur(img_bgr, (k, k), 0)
        out = cv2.resize(blurred, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    else:
        out = img_bgr.copy()
    return out

def save_with_dpi(bgr: np.ndarray, path: Path, dpi: int = SAVE_DPI):
    ensure_parent(path)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    Image.fromarray(rgb).save(str(path), dpi=(dpi, dpi))

def binarize_for_tesseract(gray: np.ndarray, method: str = 'adaptive_otsu') -> np.ndarray:
    if method == 'otsu':
        _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == 'adaptive_otsu':
        h, w = gray.shape
        bin_img = np.zeros_like(gray)
        bs = ADAPTIVE_OTSU_BLOCK
        for y in range(0, h, bs):
            for x in range(0, w, bs):
                y1, x1 = min(y+bs, h), min(x+bs, w)
                block = gray[y:y1, x:x1]
                if block.size:
                    _, b = cv2.threshold(block, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    bin_img[y:y1, x:x1] = b
    elif method == 'sauvola':
        # skimage expects float/uint8 fine; window_size must be odd
        win = SAUVOLA_WINDOW if SAUVOLA_WINDOW % 2 == 1 else SAUVOLA_WINDOW + 1
        thresh_s = threshold_sauvola(gray, window_size=win, k=SAUVOLA_K)
        bin_img = (gray > thresh_s).astype(np.uint8) * 255
    else:
        raise ValueError(f"Unknown method: {method}")
    return bin_img

if __name__ == "__main__":
    in_path = Path(INPUT)
    img = cv2.imread(str(in_path))
    if img is None:
        raise SystemExit(f"Không đọc được ảnh: {in_path.resolve()}")

    out_base = Path(OUTPUT_BASE)
    # 1) Rescale
    rescaled = rescale_for_ocr(img, TARGET_XHEIGHT)
    save_with_dpi(rescaled, out_base.with_name(out_base.name + "_rescaled.png"))

    # 2) Binarise từ ảnh sau khi rescale
    gray_rescaled = cv2.cvtColor(rescaled, cv2.COLOR_BGR2GRAY)
    for m in ['otsu', 'adaptive_otsu', 'sauvola']:
        bin_img = binarize_for_tesseract(gray_rescaled, m)
        out_path = out_base.with_name(out_base.name + f"_{m}.png")
        ensure_parent(out_path)
        ok = cv2.imwrite(str(out_path), bin_img)
        if not ok:
            raise SystemExit(f"❌ Không ghi được file: {out_path}")
        print(f"✅ Saved: {out_path}")

    print("Hoàn tất.")
