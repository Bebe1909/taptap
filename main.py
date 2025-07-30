#!/usr/bin/env python3
"""
TapTap Web Automation - Main Entry Point
========================================

This is the main entry point for the TapTap web automation system.
It provides a command-line interface to run web automation and image cropping.

Usage:
    python main.py [command] [options]

Commands:
    web        - Run web automation and take screenshots
    crop       - Crop regions from screenshots
    fullflow   - Run complete workflow (web + crop + extract + CSV)
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(description="TapTap Web Automation System")
    parser.add_argument("command", choices=["web", "crop", "fullflow"], 
                       help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "web":
        print("🌐 Running web automation...")
        # Import and run web automation
        try:
            from src.utils.full_flow import run_web_automation_with_screenshots
            run_web_automation_with_screenshots()
        except ImportError:
            print("❌ Web automation module not found. Please create src/utils/full_flow.py")
        
    elif args.command == "crop":
        print("✂️ Cropping regions from screenshot...")
        # Import and run crop
        try:
            from src.utils.full_flow import crop_all_screenshots
            crop_all_screenshots()
        except ImportError:
            print("❌ Crop module not found. Please create src/utils/full_flow.py")
        
    elif args.command == "fullflow":
        print("🚀 Running full workflow...")
        # Import and run full flow
        try:
            from src.utils.full_flow import run_full_flow
            run_full_flow()
        except ImportError:
            print("❌ Full flow module not found. Please create src/utils/full_flow.py")
        
    print("✅ Command completed!")

if __name__ == "__main__":
    main()
