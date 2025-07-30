#!/usr/bin/env python3
"""
Web Automation for TapTap
=========================

This module handles web automation using Playwright to navigate to TapTap
and take screenshots of the game interface.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

async def _run_web_automation_async():
    """Run web automation to navigate to TapTap and take screenshots"""
    
    # Create images directory if it doesn't exist
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("  → Navigating to TapTap...")
            await page.goto("https://taptap.asia")
            await page.wait_for_load_state("networkidle")
            
            # Wait a bit for page to fully load
            await page.wait_for_timeout(5000)
            
            print("  → Checking for overlays...")
            # Try to close any overlays or popups
            try:
                # Look for close buttons on overlays
                close_selectors = [
                    "[data-testid='close']",
                    ".close",
                    ".modal-close",
                    ".overlay-close",
                    "button[aria-label='Close']",
                    ".dialog-close"
                ]
                
                for selector in close_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=2000)
                        await page.click(selector)
                        print(f"    → Closed overlay with selector: {selector}")
                        await page.wait_for_timeout(1000)
                    except:
                        continue
                        
            except Exception as e:
                print(f"    → No overlays found or couldn't close: {e}")
            
            print("  → Selecting casino menu...")
            # Try different selectors for casino menu
            casino_selectors = [
                "text=Casino",
                "text=casino", 
                "a[href*='casino']",
                "[data-content-name*='Casino']",
                ".nav-item-name:has-text('casino')"
            ]
            
            casino_clicked = False
            for selector in casino_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector, timeout=10000)
                    print(f"    → Clicked casino with selector: {selector}")
                    casino_clicked = True
                    break
                except Exception as e:
                    print(f"    → Failed with selector {selector}: {e}")
                    continue
            
            if not casino_clicked:
                print("  → Could not click casino menu, taking screenshot anyway...")
            
            await page.wait_for_timeout(3000)
            
            print("  → Taking 1 screenshot...")
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = images_dir / f"screenshot_{timestamp}.png"
            
            await page.screenshot(path=str(screenshot_path))
            print(f"    📸 Screenshot: {screenshot_path}")
            
        except Exception as e:
            print(f"❌ Error during web automation: {e}")
            # Still try to take screenshot even if there's an error
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = images_dir / f"screenshot_{timestamp}.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"    📸 Screenshot taken despite error: {screenshot_path}")
            except:
                print("    ❌ Could not take screenshot")
        finally:
            await browser.close()

def run_web_automation():
    """Synchronous wrapper for async web automation"""
    asyncio.run(_run_web_automation_async())

if __name__ == "__main__":
    run_web_automation() 