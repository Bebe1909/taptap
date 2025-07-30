#!/usr/bin/env python3
"""
Debug Image Processing for TapTap OCR
=====================================

This module saves all processed images to a debug folder
so you can visually inspect the image processing results.
"""

import cv2
import numpy as np
import pytesseract
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class DebugImageProcessor:
    def __init__(self):
        """Initialize the debug image processor"""
        self.tesseract_configs = [
            '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789'
        ]
        
        # Create debug folder
        self.debug_folder = Path("debug_images")
        self.debug_folder.mkdir(exist_ok=True)
        
    def rescale_image(self, image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """Rescale image to improve OCR accuracy"""
        height, width = image.shape[:2]
        scale_factor = target_dpi / 72.0
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        rescaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        return rescaled
    
    def remove_borders(self, image: np.ndarray, border_size: int = 10) -> np.ndarray:
        """Add white border to prevent edge issues"""
        bordered = cv2.copyMakeBorder(
            image, border_size, border_size, border_size, border_size,
            cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )
        return bordered
    
    def apply_binarization(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply multiple binarization techniques"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = []
        
        # 1. Otsu thresholding
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(otsu)
        
        # 2. Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        results.append(adaptive)
        
        # 3. Adaptive thresholding with different parameters
        adaptive2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 3)
        results.append(adaptive2)
        
        return results
    
    def remove_noise(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply noise removal techniques"""
        results = []
        
        # 1. Gaussian blur
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        results.append(blurred)
        
        # 2. Median blur
        median = cv2.medianBlur(image, 3)
        results.append(median)
        
        # 3. Bilateral filter
        bilateral = cv2.bilateralFilter(image, 9, 75, 75)
        results.append(bilateral)
        
        # 4. Non-local means denoising
        denoised = cv2.fastNlMeansDenoising(image)
        results.append(denoised)
        
        return results
    
    def apply_morphological_operations(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply dilation and erosion operations"""
        results = []
        kernel = np.ones((2, 2), np.uint8)
        
        # 1. Dilation
        dilated = cv2.dilate(image, kernel, iterations=1)
        results.append(dilated)
        
        # 2. Erosion
        eroded = cv2.erode(image, kernel, iterations=1)
        results.append(eroded)
        
        # 3. Opening
        opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        results.append(opening)
        
        # 4. Closing
        closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        results.append(closing)
        
        return results
    
    def enhance_contrast(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply contrast enhancement techniques"""
        results = []
        
        # 1. CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        results.append(enhanced)
        
        # 2. Histogram equalization
        equalized = cv2.equalizeHist(image)
        results.append(equalized)
        
        # 3. Gamma correction
        gamma = 1.2
        gamma_corrected = np.power(image / 255.0, gamma) * 255.0
        gamma_corrected = gamma_corrected.astype(np.uint8)
        results.append(gamma_corrected)
        
        return results
    
    def save_processed_images(self, original_image: np.ndarray, processed_images: List[np.ndarray], 
                            base_filename: str, region: str):
        """Save all processed images to debug folder"""
        
        # Create region-specific folder
        region_folder = self.debug_folder / region
        region_folder.mkdir(exist_ok=True)
        
        # Save original image
        original_path = region_folder / f"{base_filename}_original.png"
        cv2.imwrite(str(original_path), original_image)
        
        # Save processed images with descriptive names
        image_types = [
            "rescaled", "bordered", "deskewed",
            "otsu_binarized", "adaptive_binarized", "adaptive2_binarized",
            "gaussian_blur", "median_blur", "bilateral_filter", "denoised",
            "dilated", "eroded", "opening", "closing",
            "clahe_enhanced", "histogram_equalized", "gamma_corrected"
        ]
        
        for i, img in enumerate(processed_images):
            if i < len(image_types):
                img_name = f"{base_filename}_{image_types[i]}.png"
            else:
                img_name = f"{base_filename}_processed_{i}.png"
            
            img_path = region_folder / img_name
            cv2.imwrite(str(img_path), img)
        
        print(f"    💾 Saved {len(processed_images) + 1} images to {region_folder}")
    
    def process_image_comprehensive(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply comprehensive image processing pipeline"""
        processed_images = []
        
        # Original image
        processed_images.append(image)
        
        try:
            # 1. Rescale
            rescaled = self.rescale_image(image)
            processed_images.append(rescaled)
            
            # 2. Remove borders
            bordered = self.remove_borders(rescaled)
            processed_images.append(bordered)
            
            # 3. Deskew (skip for now to avoid errors)
            deskewed = bordered  # Skip deskewing for now
            processed_images.append(deskewed)
            
            # 4. Apply binarization
            binarized = self.apply_binarization(deskewed)
            processed_images.extend(binarized)
            
            # 5. Apply noise removal to first binarized image
            denoised = self.remove_noise(binarized[0])
            processed_images.extend(denoised)
            
            # 6. Apply morphological operations to first denoised image
            morph_ops = self.apply_morphological_operations(denoised[0])
            processed_images.extend(morph_ops)
            
            # 7. Apply contrast enhancement to first gray image
            gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
            enhanced = self.enhance_contrast(gray)
            processed_images.extend(enhanced)
                
        except Exception as e:
            print(f"    ⚠️ Image processing failed: {e}")
            # Fallback to basic processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(thresh)
        
        return processed_images
    
    def extract_text_from_processed_images(self, processed_images: List[np.ndarray]) -> List[str]:
        """Extract text from all processed images"""
        all_texts = []
        
        for i, img in enumerate(processed_images):
            for config in self.tesseract_configs:
                try:
                    text = pytesseract.image_to_string(img, config=config)
                    if text.strip():
                        all_texts.append(text.strip())
                except Exception as e:
                    continue
        
        return all_texts
    
    def debug_single_image(self, image_path: str):
        """Debug a single image and save all processed versions"""
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Error loading: {image_path}")
            return
        
        # Get image info
        height, width = image.shape[:2]
        filename = Path(image_path).stem
        region = filename.split('_')[-2] if '_' in filename else 'unknown'
        
        print(f"\n🔍 Debugging: {filename}")
        print(f"    📏 Image size: {width}x{height}")
        print(f"    🏷️ Region: {region}")
        
        # Apply comprehensive processing
        processed_images = self.process_image_comprehensive(image)
        print(f"    🔧 Generated {len(processed_images)} processed images")
        
        # Save all processed images
        self.save_processed_images(image, processed_images, filename, region)
        
        # Extract text from all processed images
        all_texts = self.extract_text_from_processed_images(processed_images)
        print(f"    📝 Extracted {len(all_texts)} text samples")
        
        # Show first few text samples
        for i, text in enumerate(all_texts[:5]):
            print(f"      Sample {i+1}: '{text}'")
        
        # Extract numbers
        numbers = []
        for text in all_texts:
            number_matches = re.findall(r'\d+', text)
            for match in number_matches:
                try:
                    numbers.append(int(match))
                except ValueError:
                    continue
        
        if numbers:
            from collections import Counter
            counter = Counter(numbers)
            common_numbers = [num for num, count in counter.most_common() if count >= 1]
            print(f"    🔢 Found numbers: {common_numbers[:10]}...")
        else:
            print("    ❌ No numbers found")

def debug_all_cropped_images():
    """Debug all cropped images in the images folder"""
    
    processor = DebugImageProcessor()
    
    # Get all cropped image files
    cropped_files = []
    for file in os.listdir("images"):
        if file.endswith("_cropped.png") and ("daroka" in file or "lexi" in file or "mafer" in file):
            cropped_files.append(file)
    
    print(f"🔍 Found {len(cropped_files)} cropped images to debug")
    
    for cropped_file in cropped_files:
        image_path = f"images/{cropped_file}"
        processor.debug_single_image(image_path)
    
    print(f"\n✅ Debug complete! Check the 'debug_images' folder to see all processed images.")

if __name__ == "__main__":
    debug_all_cropped_images() 