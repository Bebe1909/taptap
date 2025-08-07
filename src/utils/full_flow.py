#!/usr/bin/env python3
"""
Full Flow for TapTap
====================

This module orchestrates the complete workflow:
1. Web automation to take screenshots
2. Crop regions from screenshots
"""

import time
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import cv2
import csv

# Import enhanced image processing
from src.utils.enhanced_image_processing import extract_all_data_enhanced


def run_full_flow():
    """Run complete workflow: web automation -> screenshots -> crop -> extract -> CSV"""

    print("🚀 Starting Full Flow...")
    print("=" * 50)

    # Step 1: Web Automation
    print("🌐 Step 1: Running web automation...")
    run_web_automation_with_screenshots()

    # Step 2: Crop all screenshots
    print("\n✂️ Step 2: Cropping regions from all screenshots...")
    crop_all_screenshots()

    # Step 3: Extract data from all cropped images
    print("\n📝 Step 3: Extracting data from all images...")
    all_results = extract_all_data_enhanced()

    # Step 4: Save to CSV
    print("\n💾 Step 4: Saving results to CSV...")
    save_to_csv(all_results)

    print("\n✅ Full Flow completed successfully!")
    print(f"📊 Results saved to: output.csv")
    print(f"📁 Screenshots saved to: images/")
    print(f"📁 Cropped images saved to: images/")


def run_web_automation_with_screenshots():
    """Run web automation and take screenshots every 5 seconds for 10 iterations"""

    # Create images directory if it doesn't exist
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Go to page
        print("  → Navigating to TapTap...")
        page.goto("https://www.taptap.asia/vi-vn")

        # Click button in popup (if needed)
        dialog_button = page.locator("xpath=//div[contains(@class,'priority-dialog-content')]/div[1]/button")
        if dialog_button.is_visible():
            dialog_button.click()

        # Select menu item: Casino trực tuyến
        print("  → Selecting casino menu...")
        item_menu = page.locator("xpath=//nav[contains(@class,'responsive-menu')]//li[a[text()='casino trực tuyến']]")
        if item_menu.is_visible():
            item_menu.click()

        # Scroll to: Trending Game
        trending_game = page.locator("xpath=//div[text()='Xu Hướng Nổi Bật']")
        trending_game.scroll_into_view_if_needed()

        # Select game to monitor: Bacarat
        print("  → Selecting game...")
        taixiu_game = page.locator(
            "xpath=//div[contains(@class,'trending-games')]//div[contains(@class,'s-slide-catalog')]//div[contains(@class,'swiper-slide')][1]")
        taixiu_game.click()

        # Login
        print("  → Logging in...")
        page.fill("//input[@aria-label='Tên truy cập / Email']", "killer_hitman2308@yahoo.com")
        page.fill("//input[@aria-label='Mật Khẩu']", "Tester123456")
        page.locator("xpath=//button[@data-content-name='Log In - Options - (MK-CTA)']").click()

        # Wait and close
        time.sleep(20)

        # Click agree to accept currency (with error handling)
        try:
            dialog_button = page.locator("xpath=//div[contains(@class,'s-dialog-content')]//button")
            if dialog_button.is_visible(timeout=5000):
                dialog_button.click()
        except:
            print("  → No dialog found, continuing...")

        time.sleep(10)
        
        # Navigate to game page with error handling
        try:
            page.goto("https://bpcdf.vesnamex777.com/player/webMain.jsp?dm=1&title=1", timeout=30000)
            page.wait_for_timeout(10000)
        except Exception as e:
            print(f"  → Navigation error: {e}")
            # Continue anyway to take screenshot

        # Take 1 screenshot
        print("  → Taking 1 screenshot...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"images/screenshot_{timestamp}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"    📸 Screenshot: {screenshot_path}")

        browser.close()


def crop_all_screenshots():
    """Crop all screenshots in the images folder"""

    # Get all screenshot files
    screenshot_files = []
    for file in os.listdir("images"):
        if file.startswith("screenshot_") and file.endswith(".png"):
            screenshot_files.append(file)

    print(f"  → Found {len(screenshot_files)} screenshots to crop")

    for screenshot_file in screenshot_files:
        screenshot_path = f"images/{screenshot_file}"
        base_name = screenshot_file.replace(".png", "")

        # Load the screenshot
        img = cv2.imread(screenshot_path)
        if img is None:
            print(f"    ❌ Error loading: {screenshot_file}")
            continue

        # Define crop coordinates for all three regions
        regions = [
            ("lexi", 271, 508, 583, 539),
            ("mafer", 604, 509, 915, 541),
            ("daroka", 931, 509, 1244, 541)
        ]

        # Crop each region
        for name, x1, y1, x2, y2 in regions:
            # Check bounds to prevent OpenCV errors
            height, width = img.shape[:2]
            x1 = max(0, min(x1, width))
            y1 = max(0, min(y1, height))
            x2 = max(0, min(x2, width))
            y2 = max(0, min(y2, height))
            
            # Ensure valid crop region
            if x1 < x2 and y1 < y2:
                cropped = img[y1:y2, x1:x2]
                if cropped.size > 0:  # Check if cropped image is not empty
                    cropped_filename = f"images/{base_name}_{name}_cropped.png"
                    cv2.imwrite(cropped_filename, cropped)
                else:
                    print(f"    ⚠️ Empty crop for {name} in {screenshot_file}")
            else:
                print(f"    ⚠️ Invalid crop coordinates for {name} in {screenshot_file}")

        print(f"    ✅ Cropped: {screenshot_file}")


def save_to_csv(all_results):
    """Save all results to CSV file"""

    if not all_results:
        print("  ⚠️ No results to save")
        return

    # Define column order
    columns_order = ["timestamp", "iteration", "region", "username", "b_value", "s_value", "t_value", "people_count",
                     "dollar_amount", "filename"]

    # Save to CSV
    csv_file = "output.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns_order)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"  ✅ Saved {len(all_results)} records to {csv_file}")


if __name__ == "__main__":
    run_full_flow() 