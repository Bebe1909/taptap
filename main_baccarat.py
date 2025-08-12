#!/usr/bin/env python3
"""
TapTap Main2 - Playwright Runner
================================

This is a simplified Playwright runner for TapTap.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def run_playwright_simple():
    """Run simple Playwright automation"""
    print("🚀 TapTap Playwright Runner")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Launch browser
            print("🌐 Launching browser...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # Go to page
            print("  → Navigating to TapTap...")
            page.goto("https://www.taptap.asia/vi-vn")

            # Click button in popup (if needed)
            time.sleep(5)
            dialog_button = page.locator("xpath=//div[contains(@class,'!absolute')]/button")
            if dialog_button.is_visible():
                dialog_button.click()

            # Select menu item: Casino trực tuyến
            print("  → Selecting casino menu...")
            item_menu = page.locator(
                "xpath=//nav[contains(@class,'responsive-menu')]//li[a[text()='casino trực tuyến']]")
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

            # click on point (122, 203)
            print("  → Clicking on Traditional Category...")
            try:
                page.mouse.click(122, 251)
                print("    ✅ Clicked on Traditional Category")
                time.sleep(2)  # Wait a bit after click
            except Exception as e:
                print(f"    ❌ Click failed: {e}")

            time.sleep(5)
                
            # Continue anyway to take screenshot
            print("  → Taking screenshot...")
            try:
                Path("images").mkdir(exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"images/screenshot_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"    📸 Screenshot saved: {screenshot_path}")
                
                # Crop the screenshot
                print("  → Cropping screenshot...")
                try:
                    import cv2
                    import numpy as np
                    
                    # Read the screenshot
                    img = cv2.imread(screenshot_path)
                    if img is not None:
                        # Crop with coordinates (x1, y1, x2, y2)
                        x1, y1, x2, y2 = 273, 367, 581, 541
                        cropped = img[y1:y2, x1:x2]
                        
                        # Save cropped image
                        cropped_path = screenshot_path.replace('.png', '_cropped.png')
                        cv2.imwrite(cropped_path, cropped)
                        print(f"    ✂️ Cropped image saved: {cropped_path}")
                        print(f"    📐 Crop area: ({x1}, {y1}) to ({x2}, {y2})")
                    else:
                        print("    ❌ Failed to read screenshot for cropping")
                        
                except ImportError:
                    print("    ⚠️ OpenCV not available, skipping crop")
                except Exception as e:
                    print(f"    ❌ Crop failed: {e}")
                    
            except Exception as e:
                print(f"    ❌ Screenshot failed: {e}")

            print("  ✅ Browser initialized and game page loaded")

            # Close browser
            browser.close()
            print("✅ Browser closed successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    run_playwright_simple()

if __name__ == "__main__":
    main()
