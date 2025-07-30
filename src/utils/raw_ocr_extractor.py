#!/usr/bin/env python3
"""
Raw OCR Extractor for TapTap Images
===================================

This module extracts raw OCR text from all images
without any processing or mapping.
"""

import os
import cv2
import pytesseract

def extract_raw_ocr(image_path: str):
    """Extract raw OCR text from image"""
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"❌ Cannot read image: {image_path}"}

    # Simple preprocessing for better OCR
    image_resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Extract raw OCR
    config = r'--oem 3 --psm 6'
    raw_text = pytesseract.image_to_string(thresh, config=config)

    return {
        "file": os.path.basename(image_path),
        "raw_ocr": raw_text.strip(),
        "image_size": f"{image.shape[1]}x{image.shape[0]}"
    }

def extract_from_original_images():
    """Extract raw OCR from original cropped images"""
    results = []
    
    if not os.path.exists("images"):
        print("❌ Images folder not found")
        return results
    
    for filename in os.listdir("images"):
        if filename.lower().endswith(".png") and ("cropped" in filename or "screenshot" in filename):
            full_path = os.path.join("images", filename)
            result = extract_raw_ocr(full_path)
            results.append(result)
    
    return results

def extract_from_clahe_images():
    """Extract raw OCR from CLAHE enhanced images"""
    results = []
    debug_folder = "./debug_images"

    if not os.path.exists(debug_folder):
        print("❌ Debug folder not found")
        return results

    regions = ['daroka', 'lexi', 'mafer']

    for region in regions:
        region_folder = os.path.join(debug_folder, region)
        if os.path.exists(region_folder):
            for filename in os.listdir(region_folder):
                if "clahe_enhanced" in filename and filename.endswith(".png"):
                    full_path = os.path.join(region_folder, filename)
                    result = extract_raw_ocr(full_path)
                    result["region"] = region
                    results.append(result)

    return results

def main():
    """Main function to extract raw OCR"""
    print("🔍 Raw OCR Extraction from TapTap Images")
    print("=" * 60)
    
    # Extract from original images
    print("\n📁 Raw OCR from Original Images:")
    print("-" * 50)
    
    original_results = extract_from_original_images()
    if original_results:
        print(f"Found {len(original_results)} original images")
        for result in original_results:
            print(f"\n📄 {result['file']} ({result['image_size']})")
            print("Raw OCR:")
            print(f"'{result['raw_ocr']}'")
            print("-" * 40)
    else:
        print("❌ No original images found")
    
    # Extract from CLAHE enhanced images
    print("\n📁 Raw OCR from CLAHE Enhanced Images:")
    print("-" * 50)
    
    clahe_results = extract_from_clahe_images()
    if clahe_results:
        print(f"Found {len(clahe_results)} CLAHE enhanced images")
        for result in clahe_results:
            region = result.get('region', '').upper()
            print(f"\n📄 [{region}] {result['file']} ({result['image_size']})")
            print("Raw OCR:")
            print(f"'{result['raw_ocr']}'")
            print("-" * 40)
    else:
        print("❌ No CLAHE enhanced images found")
    
    print("\n✅ Raw OCR extraction complete!")

if __name__ == "__main__":
    main() 