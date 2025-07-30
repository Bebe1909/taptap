#!/usr/bin/env python3
"""
Enhanced Data Extraction for TapTap
===================================

This module provides advanced OCR and image processing techniques
to extract accurate data from cropped game images.
"""

import cv2
import numpy as np
import pytesseract
import easyocr
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class EnhancedExtractor:
    def __init__(self):
        """Initialize the enhanced extractor with OCR engines"""
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
        
    def preprocess_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply multiple preprocessing techniques to improve OCR accuracy"""
        processed_images = []
        
        # Original image
        processed_images.append(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_images.append(gray)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(thresh)
        
        # Apply adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        processed_images.append(adaptive_thresh)
        
        # Apply morphological operations
        kernel = np.ones((1,1), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed_images.append(morph)
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        processed_images.append(denoised)
        
        # Apply contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        processed_images.append(enhanced)
        
        return processed_images
    
    def extract_with_tesseract(self, image: np.ndarray) -> List[str]:
        """Extract text using Tesseract OCR with multiple preprocessing"""
        results = []
        
        # Try different preprocessing techniques
        processed_images = self.preprocess_image(image)
        
        for i, processed_img in enumerate(processed_images):
            try:
                # Try different PSM modes
                for psm in [6, 7, 8, 13]:
                    config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789'
                    text = pytesseract.image_to_string(processed_img, config=config)
                    if text.strip():
                        results.append(text.strip())
                        
                # Try without whitelist
                text = pytesseract.image_to_string(processed_img, config='--oem 3 --psm 6')
                if text.strip():
                    results.append(text.strip())
                    
            except Exception as e:
                continue
                
        return results
    
    def extract_with_easyocr(self, image: np.ndarray) -> List[str]:
        """Extract text using EasyOCR"""
        try:
            results = self.easyocr_reader.readtext(image)
            texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Lower threshold for small text
                    texts.append(text.strip())
            return texts
        except Exception as e:
            return []
    
    def extract_numbers_from_text(self, texts: List[str]) -> List[int]:
        """Extract numbers from OCR results"""
        numbers = []
        for text in texts:
            # Find all numbers in the text
            number_matches = re.findall(r'\d+', text)
            for match in number_matches:
                try:
                    numbers.append(int(match))
                except ValueError:
                    continue
        return numbers
    
    def extract_data_from_image(self, image_path: str) -> Dict[str, any]:
        """Extract data from a single cropped image"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {}
        
        # Extract text with both OCR engines
        tesseract_results = self.extract_with_tesseract(image)
        easyocr_results = self.extract_with_easyocr(image)
        
        # Combine all results
        all_texts = tesseract_results + easyocr_results
        
        # Extract numbers
        numbers = self.extract_numbers_from_text(all_texts)
        
        # Debug: Print all extracted texts and numbers
        print(f"    📝 Extracted texts: {all_texts}")
        print(f"    🔢 Extracted numbers: {numbers}")
        
        # Try to map numbers to expected format
        # Expected format: [B, S, T, People, Dollar]
        if len(numbers) >= 5:
            return {
                "b_value": str(numbers[0]),
                "s_value": str(numbers[1]), 
                "t_value": str(numbers[2]),
                "people_count": str(numbers[3]),
                "dollar_amount": str(numbers[4])
            }
        elif len(numbers) >= 3:
            # Try to find patterns
            return {
                "b_value": str(numbers[0]) if len(numbers) > 0 else "0",
                "s_value": str(numbers[1]) if len(numbers) > 1 else "0",
                "t_value": str(numbers[2]) if len(numbers) > 2 else "0",
                "people_count": str(numbers[3]) if len(numbers) > 3 else "0",
                "dollar_amount": str(numbers[4]) if len(numbers) > 4 else "0"
            }
        else:
            return {
                "b_value": "0",
                "s_value": "0",
                "t_value": "0", 
                "people_count": "0",
                "dollar_amount": "0"
            }

def extract_all_data_enhanced():
    """Enhanced data extraction from all cropped images"""
    
    extractor = EnhancedExtractor()
    all_results = []
    
    # Get all cropped image files
    cropped_files = []
    for file in os.listdir("images"):
        if file.endswith("_cropped.png") and ("daroka" in file or "lexi" in file or "mafer" in file):
            cropped_files.append(file)
    
    print(f"  → Found {len(cropped_files)} cropped images to process")
    
    for cropped_file in cropped_files:
        print(f"\n    🔍 Processing: {cropped_file}")
        
        # Extract timestamp and region from filename
        parts = cropped_file.replace(".png", "").split("_")
        
        if len(parts) >= 4:
            timestamp = f"{parts[1]}_{parts[2]}"
            iteration = "01"
            region = parts[3]  # daroka, lexi, or mafer
            
            # Extract data using enhanced OCR
            image_path = f"images/{cropped_file}"
            extracted_data = extractor.extract_data_from_image(image_path)
            
            if extracted_data:
                # Add metadata
                data = {
                    "timestamp": timestamp,
                    "iteration": iteration,
                    "region": region,
                    "username": region.capitalize(),
                    "filename": cropped_file,
                    **extracted_data
                }
                all_results.append(data)
                print(f"    ✅ Extracted: {extracted_data}")
            else:
                print(f"    ❌ Failed to extract data from {cropped_file}")
    
    return all_results

if __name__ == "__main__":
    import os
    results = extract_all_data_enhanced()
    print(f"\n📊 Total results: {len(results)}")
    for result in results:
        print(f"  {result}") 