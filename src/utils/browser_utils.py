#!/usr/bin/env python3
"""
Browser Utilities for TapTap
============================

This module contains shared browser initialization and navigation logic
used across different parts of the TapTap analysis system.
"""

import time
from playwright.sync_api import sync_playwright


def initialize_browser_and_navigate():
    """
    Initialize browser and navigate to the TapTap game page.
    
    Returns:
        tuple: (browser, page) or (None, None) if initialization fails
    """
    try:
        p = sync_playwright().start()
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

        print("  ✅ Browser initialized and game page loaded")
        return browser, page
        
    except Exception as e:
        print(f"  ❌ Browser initialization error: {e}")
        return None, None


def take_screenshot(page, images_dir="images"):
    """
    Take a screenshot using the provided page object.
    
    Args:
        page: Playwright page object
        images_dir: Directory to save screenshots (default: "images")
    
    Returns:
        str: Path to the saved screenshot
    """
    from datetime import datetime
    from pathlib import Path
    
    # Ensure images directory exists
    Path(images_dir).mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"{images_dir}/screenshot_{timestamp}.png"
    page.screenshot(path=screenshot_path, full_page=True)
    return screenshot_path
