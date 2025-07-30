#!/usr/bin/env python3
"""
Image Cropping for TapTap
=========================

This module handles cropping specific regions from screenshots
to extract game data areas.
"""

import cv2
import os
from pathlib import Path
from datetime import datetime

def crop_all_regions():
    """Crop all regions from screenshots in the images directory"""
    
    images_dir = Path("images")
    if not images_dir.exists():
        print("❌ Images directory not found. Please run web automation first.")
        return
    
    # Find all screenshots
    screenshots = list(images_dir.glob("screenshot_*.png"))
    if not screenshots:
        print("❌ No screenshots found. Please run web automation first.")
        return
    
    print(f"  → Found {len(screenshots)} screenshots to crop")
    
    for screenshot_path in screenshots:
        print(f"    ✅ Cropped: {screenshot_path.name}")
        
        # Read the screenshot
        img = cv2.imread(str(screenshot_path))
        if img is None:
            print(f"    ❌ Could not read image: {screenshot_path}")
            continue
        
        # Get image dimensions
        height, width = img.shape[:2]
        
        # Define crop regions (these are example coordinates - adjust as needed)
        # You'll need to adjust these based on the actual UI layout
        
        # Lexi area (top left region)
        lexi_crop = img[100:400, 50:300]  # Adjust coordinates
        lexi_path = images_dir / f"{screenshot_path.stem}_lexi_cropped.png"
        cv2.imwrite(str(lexi_path), lexi_crop)
        
        # Mafer area (top right region)
        mafer_crop = img[100:400, 350:600]  # Adjust coordinates
        mafer_path = images_dir / f"{screenshot_path.stem}_mafer_cropped.png"
        cv2.imwrite(str(mafer_path), mafer_crop)
        
        # Daroka area (bottom region)
        daroka_crop = img[450:750, 200:500]  # Adjust coordinates
        daroka_path = images_dir / f"{screenshot_path.stem}_daroka_cropped.png"
        cv2.imwrite(str(daroka_path), daroka_crop)
        
        print(f"      → Saved: {lexi_path.name}")
        print(f"      → Saved: {mafer_path.name}")
        print(f"      → Saved: {daroka_path.name}")

if __name__ == "__main__":
    crop_all_regions() 