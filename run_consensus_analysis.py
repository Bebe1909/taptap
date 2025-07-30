#!/usr/bin/env python3
"""
TapTap Consensus Analysis Runner
===============================

This script provides easy access to run consensus analysis from the root directory.
It can run either the full analysis or the optimized version.
"""

import sys
import os
import subprocess

def run_full_consensus():
    """Run the full consensus analysis"""
    print("🔍 Running Full Consensus Analysis...")
    print("=" * 50)
    
    # Change to utils directory and run the script
    utils_dir = os.path.join(os.path.dirname(__file__), "src", "utils")
    script_path = os.path.join(utils_dir, "consensus_analyzer.py")
    
    # Use the virtual environment Python
    python_path = os.path.join(os.path.dirname(__file__), ".env", "bin", "python3")
    
    try:
        result = subprocess.run([python_path, script_path], 
                              cwd=utils_dir, 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running full consensus analysis: {e}")
        return False

def run_optimized_consensus():
    """Run the optimized consensus analysis"""
    print("⚡ Running Optimized Consensus Analysis...")
    print("=" * 50)
    
    # Change to utils directory and run the script
    utils_dir = os.path.join(os.path.dirname(__file__), "src", "utils")
    script_path = os.path.join(utils_dir, "optimized_consensus_analyzer.py")
    
    # Use the virtual environment Python
    python_path = os.path.join(os.path.dirname(__file__), ".env", "bin", "python3")
    
    try:
        result = subprocess.run([python_path, script_path], 
                              cwd=utils_dir, 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running optimized consensus analysis: {e}")
        return False

def main():
    """Main function to run consensus analysis"""
    print("🚀 TapTap Consensus Analysis Runner")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['full', 'complete', 'all']:
            success = run_full_consensus()
        elif mode in ['optimized', 'fast', 'quick']:
            success = run_optimized_consensus()
        else:
            print("❌ Invalid mode. Use 'full' or 'optimized'")
            print("   Usage: python3 run_consensus_analysis.py [full|optimized]")
            return
    else:
        # Default to optimized
        print("🎯 No mode specified, running optimized analysis (recommended)")
        print("   Use 'python3 run_consensus_analysis.py full' for complete analysis")
        print()
        success = run_optimized_consensus()
    
    if success:
        print("\n✅ Consensus analysis completed successfully!")
    else:
        print("\n❌ Consensus analysis failed!")

if __name__ == "__main__":
    main() 