#!/usr/bin/env python3
"""
Consensus Analyzer for TapTap Debug Images
==========================================

This script analyzes all debug images and finds the most consistent results
across different processing methods and image enhancements.
"""

import sys
import os
from advanced_data_extraction import TapTapDataExtractor, ConsensusAnalyzer

def main():
    
    """Main function to run consensus analysis"""
    print("🔍 TapTap Debug Images Consensus Analyzer")
    print("=" * 50)
    
    # Check if debug_images folder exists (look in parent directory)
    debug_folder = "../../debug_images"
    if not os.path.exists(debug_folder):
        print("❌ Debug folder not found. Please run debug_image_processing.py first.")
        print("   Make sure you have debug_images/ folder with subfolders for each region.")
        return
    
    # Create extractor and analyzer instances
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    
    # Run the full consensus analysis
    analyzer.generate_consensus_report()
    
    print("\n🎯 SUMMARY:")
    print("=" * 50)
    print("The consensus analysis has:")
    print("✅ Processed all debug images in each region")
    print("✅ Applied V2, V3, and V4 extraction methods")
    print("✅ Found the most consistent values across all methods")
    print("✅ Generated confidence scores for each field")
    print("✅ Saved results to consensus_results.csv")
    print("\n📊 Check consensus_results.csv for the final results!")

if __name__ == "__main__":
    main() 