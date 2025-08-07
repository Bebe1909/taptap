#!/usr/bin/env python3
"""
Enhanced Image Processing for TapTap OCR
========================================

This module applies advanced image processing techniques
based on Tesseract documentation to improve OCR accuracy.
"""

import cv2
import numpy as np
import pytesseract
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

class EnhancedImageProcessor:
    def __init__(self):
        """Initialize the enhanced image processor"""
        self.tesseract_configs = [
            '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            '--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789'
        ]
        
    def rescale_image(self, image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """Rescale image to improve OCR accuracy (Tesseract works best at 300+ DPI)"""
        height, width = image.shape[:2]
        
        # Calculate scale factor to achieve target DPI
        # Assuming original image is around 72 DPI
        scale_factor = target_dpi / 72.0
        
        # Resize image
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        rescaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        return rescaled
    
    def remove_borders(self, image: np.ndarray, border_size: int = 10) -> np.ndarray:
        """Remove borders that can interfere with OCR"""
        height, width = image.shape[:2]
        
        # Add white border to prevent edge issues
        bordered = cv2.copyMakeBorder(
            image, border_size, border_size, border_size, border_size,
            cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )
        return bordered
    
    def apply_binarization(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply multiple binarization techniques"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = []
        
        # 1. Otsu thresholding (default Tesseract method)
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
        
        # 1. Gaussian blur for noise reduction
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        results.append(blurred)
        
        # 2. Median blur for salt-and-pepper noise
        median = cv2.medianBlur(image, 3)
        results.append(median)
        
        # 3. Bilateral filter for edge-preserving smoothing
        bilateral = cv2.bilateralFilter(image, 9, 75, 75)
        results.append(bilateral)
        
        # 4. Non-local means denoising
        denoised = cv2.fastNlMeansDenoising(image)
        results.append(denoised)
        
        return results
    
    def apply_morphological_operations(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply dilation and erosion operations"""
        results = []
        
        # Create kernel
        kernel = np.ones((2, 2), np.uint8)
        
        # 1. Dilation (for thin characters)
        dilated = cv2.dilate(image, kernel, iterations=1)
        results.append(dilated)
        
        # 2. Erosion (for bold characters)
        eroded = cv2.erode(image, kernel, iterations=1)
        results.append(eroded)
        
        # 3. Opening (erosion followed by dilation)
        opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        results.append(opening)
        
        # 4. Closing (dilation followed by erosion)
        closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        results.append(closing)
        
        return results
    
    def enhance_contrast(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply contrast enhancement techniques"""
        results = []
        
        # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
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
    
    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Deskew image to make text horizontal"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find lines using Hough transform
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None and len(lines) > 0:
                # Calculate average angle
                angles = []
                for line in lines[:10]:  # Use first 10 lines
                    rho, theta = line[0]  # Fix unpacking
                    angle = theta * 180 / np.pi
                    if angle < 45 or angle > 135:
                        angles.append(angle)
                
                if angles:
                    avg_angle = np.mean(angles)
                    # Rotate image
                    height, width = image.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                    rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
                    return rotated
        except Exception as e:
            print(f"    ⚠️ Deskew failed: {e}")
        
        return image
    
    def process_image_comprehensive(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply comprehensive image processing pipeline"""
        processed_images = []
        
        # Original image
        processed_images.append(image)
        
        try:
            # 1. Rescale for better OCR
            rescaled = self.rescale_image(image)
            processed_images.append(rescaled)
            
            # 2. Remove borders
            bordered = self.remove_borders(rescaled)
            processed_images.append(bordered)
            
            # 3. Deskew (optional, skip if fails)
            deskewed = self.deskew_image(bordered)
            processed_images.append(deskewed)
            
            # 4. Apply different binarization techniques
            binarized = self.apply_binarization(deskewed)
            processed_images.extend(binarized)
            
            # 5. Apply noise removal to each binarized image
            for binarized_img in binarized:
                denoised = self.remove_noise(binarized_img)
                processed_images.extend(denoised)
            
            # 6. Apply morphological operations (limit to avoid too many images)
            for denoised_img in processed_images[-len(binarized)*2:]:  # Last 2*len(binarized) images
                morph_ops = self.apply_morphological_operations(denoised_img)
                processed_images.extend(morph_ops)
            
            # 7. Apply contrast enhancement (limit to avoid too many images)
            gray_images = [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img 
                          for img in processed_images[-10:]]  # Last 10 images
            
            for gray_img in gray_images:
                enhanced = self.enhance_contrast(gray_img)
                processed_images.extend(enhanced)
                
        except Exception as e:
            print(f"    ⚠️ Image processing failed: {e}")
            # Fallback to basic processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(thresh)
        
        return processed_images
    
    def process_image_optimized(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Optimized image processing that only generates the 3 best methods:
        - processed_17 (custom method)
        - gaussian_blur (noise reduction)
        - adaptive_binarized (adaptive thresholding)
        """
        processed_images = {}
        
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Method 1: processed_17 (custom method - enhanced with CLAHE + adaptive threshold)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            clahe_enhanced = clahe.apply(gray)
            processed_17 = cv2.adaptiveThreshold(
                clahe_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            processed_images['processed_17'] = processed_17
            
            # Method 2: gaussian_blur (noise reduction)
            gaussian_blur = cv2.GaussianBlur(gray, (3, 3), 0)
            processed_images['gaussian_blur'] = gaussian_blur
            
            # Method 3: adaptive_binarized (adaptive thresholding)
            adaptive_binarized = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            processed_images['adaptive_binarized'] = adaptive_binarized
            
        except Exception as e:
            print(f"    ⚠️ Optimized image processing failed: {e}")
            # Fallback to basic processing
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images['fallback'] = thresh
        
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
    
    def extract_data_from_image(self, image_path: str) -> Dict[str, any]:
        """Extract data using enhanced image processing"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {}
        
        # Get image dimensions
        height, width = image.shape[:2]
        print(f"    📏 Original image size: {width}x{height}")
        
        # Apply comprehensive image processing
        processed_images = self.process_image_comprehensive(image)
        print(f"    🔧 Generated {len(processed_images)} processed images")
        
        # Extract text from all processed images
        all_texts = self.extract_text_from_processed_images(processed_images)
        print(f"    📝 Extracted {len(all_texts)} text samples")
        
        # Extract numbers from all texts
        numbers = []
        for text in all_texts:
            number_matches = re.findall(r'\d+', text)
            for match in number_matches:
                try:
                    numbers.append(int(match))
                except ValueError:
                    continue
        
        # Find most common numbers
        from collections import Counter
        if numbers:
            counter = Counter(numbers)
            common_numbers = [num for num, count in counter.most_common() if count >= 1]
            print(f"    🔢 Found numbers: {common_numbers}")
            
            # Map numbers to fields
            if len(common_numbers) >= 5:
                return {
                    "b_value": str(common_numbers[0]),
                    "s_value": str(common_numbers[1]),
                    "t_value": str(common_numbers[2]),
                    "people_count": str(common_numbers[3]),
                    "dollar_amount": str(common_numbers[4])
                }
            elif len(common_numbers) >= 3:
                return {
                    "b_value": str(common_numbers[0]) if len(common_numbers) > 0 else "0",
                    "s_value": str(common_numbers[1]) if len(common_numbers) > 1 else "0",
                    "t_value": str(common_numbers[2]) if len(common_numbers) > 2 else "0",
                    "people_count": str(common_numbers[3]) if len(common_numbers) > 3 else "0",
                    "dollar_amount": str(common_numbers[4]) if len(common_numbers) > 4 else "0"
                }
        
        return {
            "b_value": "0",
            "s_value": "0",
            "t_value": "0",
            "people_count": "0",
            "dollar_amount": "0"
        }

    def extract_data_from_image_optimized(self, image_path: str) -> Dict[str, any]:
        """Extract data using optimized image processing (only 3 best methods)"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {}
        
        # Get image dimensions
        height, width = image.shape[:2]
        print(f"    📏 Original image size: {width}x{height}")
        
        # Apply optimized image processing (only 3 methods)
        processed_images = self.process_image_optimized(image)
        print(f"    🔧 Generated {len(processed_images)} optimized processed images")
        
        # Extract text from optimized processed images
        all_texts = []
        for method_name, processed_img in processed_images.items():
            for config in self.tesseract_configs:
                try:
                    text = pytesseract.image_to_string(processed_img, config=config)
                    if text.strip():
                        all_texts.append(text.strip())
                except Exception as e:
                    continue
        
        print(f"    📝 Extracted {len(all_texts)} text samples")
        
        # Extract numbers from all texts
        numbers = []
        for text in all_texts:
            number_matches = re.findall(r'\d+', text)
            for match in number_matches:
                try:
                    numbers.append(int(match))
                except ValueError:
                    continue
        
        # Find most common numbers
        from collections import Counter
        if numbers:
            counter = Counter(numbers)
            common_numbers = [num for num, count in counter.most_common() if count >= 1]
            print(f"    🔢 Found numbers: {common_numbers[:20]}...")  # Show first 20
            
            # Extract data using the same logic as the original
            if len(common_numbers) >= 5:
                b_value = str(common_numbers[0])
                s_value = str(common_numbers[1])
                t_value = str(common_numbers[2])
                people_count = str(common_numbers[3])
                dollar_amount = str(common_numbers[4])
            else:
                # Fallback if not enough numbers
                b_value = str(common_numbers[0]) if common_numbers else '0'
                s_value = str(common_numbers[1]) if len(common_numbers) > 1 else '0'
                t_value = str(common_numbers[2]) if len(common_numbers) > 2 else '0'
                people_count = str(common_numbers[3]) if len(common_numbers) > 3 else '0'
                dollar_amount = str(common_numbers[4]) if len(common_numbers) > 4 else '0'
        else:
            b_value = s_value = t_value = people_count = dollar_amount = '0'
        
        # Extract region and timestamp from filename
        filename = os.path.basename(image_path)
        region = 'cropped'  # Default
        timestamp = filename.replace('.png', '')
        
        if '_cropped.png' in filename:
            region = filename.split('_cropped.png')[0].split('_')[-1]
            timestamp = '_'.join(filename.split('_')[:-2])
        
        result = {
            'b_value': b_value,
            's_value': s_value,
            't_value': t_value,
            'people_count': people_count,
            'dollar_amount': dollar_amount,
            'region': region,
            'filename': filename,
            'timestamp': timestamp,
            'processing_methods': list(processed_images.keys())
        }
        
        print(f"    ✅ Extracted data: {result}")
        return result

def extract_all_data_enhanced():
    """Enhanced data extraction using comprehensive image processing"""
    
    processor = EnhancedImageProcessor()
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
            
            # Extract data using enhanced processing
            image_path = f"images/{cropped_file}"
            extracted_data = processor.extract_data_from_image(image_path)
            
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
    results = extract_all_data_enhanced()
    print(f"\n📊 Total results: {len(results)}")
    for result in results:
        print(f"  {result}") 