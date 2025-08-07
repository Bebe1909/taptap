#!/usr/bin/env python3
"""
TapTap Main Entry Point
=======================

This is the main entry point for the TapTap analysis system.
It provides access to all the different analysis modes.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Main function to run TapTap analysis"""
    print("🚀 TapTap Analysis System")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['continuous', 'monitor', 'live']:
            from src.runners.consensus_analysis_runner import run_continuous_monitoring
            success = run_continuous_monitoring()
        elif mode in ['full', 'complete', 'all']:
            from src.runners.consensus_analysis_runner import run_full_consensus
            success = run_full_consensus()
        elif mode in ['optimized', 'fast', 'quick']:
            from src.runners.consensus_analysis_runner import run_optimized_consensus
            success = run_optimized_consensus()
        elif mode in ['test', 'test-monitor']:
            from src.test.continuous_monitoring_test import test_continuous_monitoring
            success = test_continuous_monitoring()
        else:
            print("❌ Invalid mode. Use 'continuous', 'full', 'optimized', or 'test'")
            print("   Usage: python main.py [continuous|full|optimized|test]")
            print("\n   Modes:")
            print("   - continuous: Run 60s monitoring with consensus analysis")
            print("   - full: Run full consensus analysis on existing images")
            print("   - optimized: Run optimized consensus analysis")
            print("   - test: Run 15s test monitoring")
            return
    else:
        # Default to continuous monitoring
        print("🎯 No mode specified, running continuous monitoring (recommended)")
        print("   Use 'python main.py test' for quick testing")
        print("   Use 'python main.py full' for existing image analysis")
        print()
        from src.runners.consensus_analysis_runner import run_continuous_monitoring
        success = run_continuous_monitoring()
    
    if success:
        print("\n✅ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")

if __name__ == "__main__":
    main()
