#!/usr/bin/env python3
"""
Performance Comparison: Original vs Optimized Consensus Analysis
==============================================================

This script compares the performance and accuracy between the original
full analysis and the optimized smart sampling approach.
"""

import sys
import os
import time


from ..src.utils.advanced_data_extraction import TapTapDataExtractor, ConsensusAnalyzer, OptimizedConsensusAnalyzer

def compare_performance():
    """Compare performance between original and optimized approaches"""
    print("⚡ PERFORMANCE COMPARISON: ORIGINAL vs OPTIMIZED")
    print("=" * 60)
    
    # Create extractor and analyzer instances
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    optimized_analyzer = OptimizedConsensusAnalyzer(extractor)
    
    # Test original approach
    print("\n🔍 Testing ORIGINAL approach (full analysis)...")
    start_time = time.time()
    original_results = analyzer.get_consensus_results()
    original_time = time.time() - start_time
    
    print(f"⏱️  Original approach took: {original_time:.2f} seconds")
    
    # Test optimized approach
    print("\n🔍 Testing OPTIMIZED approach (smart sampling)...")
    start_time = time.time()
    optimized_results = optimized_analyzer.get_consensus_results_optimized(sample_size=5, confidence_threshold=80.0)
    optimized_time = time.time() - start_time
    
    print(f"⏱️  Optimized approach took: {optimized_time:.2f} seconds")
    
    # Calculate performance improvement
    speedup = original_time / optimized_time if optimized_time > 0 else float('inf')
    
    print(f"\n📊 PERFORMANCE SUMMARY:")
    print(f"   Original time: {original_time:.2f} seconds")
    print(f"   Optimized time: {optimized_time:.2f} seconds")
    print(f"   Speedup: {speedup:.1f}x faster")
    print(f"   Time saved: {original_time - optimized_time:.2f} seconds")
    
    return original_results, optimized_results, speedup

def compare_accuracy(original_results, optimized_results):
    """Compare accuracy between original and optimized approaches"""
    print("\n📊 ACCURACY COMPARISON:")
    print("=" * 60)
    
    regions = ['daroka', 'lexi', 'mafer']
    fields = ['b_value', 's_value', 't_value', 'people_count', 'dollar_amount']
    
    total_matches = 0
    total_fields = 0
    
    for region in regions:
        print(f"\n{region.upper()}:")
        original = original_results.get(region, {})
        optimized = optimized_results.get(region, {})
        
        region_matches = 0
        for field in fields:
            orig_val = original.get(field, '')
            opt_val = optimized.get(field, '')
            
            match = orig_val == opt_val
            status = "✅" if match else "❌"
            
            print(f"  {field:12}: {orig_val:>8} vs {opt_val:>8} {status}")
            
            if match:
                region_matches += 1
            total_fields += 1
        
        region_accuracy = (region_matches / len(fields)) * 100
        total_matches += region_matches
        print(f"  Accuracy: {region_accuracy:.1f}% ({region_matches}/{len(fields)} fields match)")
    
    overall_accuracy = (total_matches / total_fields) * 100
    print(f"\n🎯 OVERALL ACCURACY: {overall_accuracy:.1f}% ({total_matches}/{total_fields} fields match)")
    
    return overall_accuracy

def print_recommendations(speedup, accuracy):
    """Print recommendations based on performance comparison"""
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 60)
    
    if speedup >= 5 and accuracy >= 90:
        print("✅ EXCELLENT: Use optimized approach for production")
        print("   - Significant performance improvement")
        print("   - High accuracy maintained")
        print("   - Recommended for all use cases")
        
    elif speedup >= 3 and accuracy >= 80:
        print("✅ GOOD: Use optimized approach with monitoring")
        print("   - Good performance improvement")
        print("   - Acceptable accuracy")
        print("   - Monitor results for critical applications")
        
    elif speedup >= 2:
        print("⚠️  MODERATE: Consider optimized approach for non-critical use")
        print("   - Some performance improvement")
        print("   - May have accuracy trade-offs")
        print("   - Test thoroughly before production use")
        
    else:
        print("❌ POOR: Stick with original approach")
        print("   - Minimal performance improvement")
        print("   - Accuracy may be compromised")
        print("   - Not recommended for production")
    
    print(f"\n📈 SPECIFIC RECOMMENDATIONS:")
    print(f"   - Speedup achieved: {speedup:.1f}x")
    print(f"   - Accuracy maintained: {accuracy:.1f}%")
    
    if speedup >= 5:
        print("   - Consider reducing sample_size for even faster results")
        print("   - Increase confidence_threshold for higher accuracy")
    elif speedup < 3:
        print("   - Consider increasing sample_size for better accuracy")
        print("   - Decrease confidence_threshold for faster results")

def main():
    """Main function to run performance comparison"""
    print("🚀 TapTap Consensus Analysis Performance Comparison")
    print("=" * 60)
    
    # Check if debug_images folder exists
    if not os.path.exists("debug_images"):
        print("❌ Debug folder not found. Please run debug_image_processing.py first.")
        return
    
    # Compare performance
    original_results, optimized_results, speedup = compare_performance()
    
    # Compare accuracy
    accuracy = compare_accuracy(original_results, optimized_results)
    
    # Print recommendations
    print_recommendations(speedup, accuracy)
    
    # Show detailed results
    print("\n" + "=" * 60)
    print("📋 DETAILED RESULTS:")
    print("=" * 60)
    
    # Create analyzer instances for detailed results
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    optimized_analyzer = OptimizedConsensusAnalyzer(extractor)
    
    print("\n🔍 ORIGINAL APPROACH RESULTS:")
    analyzer.print_simple_consensus()
    
    print("\n⚡ OPTIMIZED APPROACH RESULTS:")
    optimized_analyzer.print_optimized_consensus()
    
    print("\n✅ Performance comparison complete!")

if __name__ == "__main__":
    main() 