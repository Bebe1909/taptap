#!/usr/bin/env python3
"""
Advanced Data Extraction for TapTap
==================================

This module uses multiple extraction methods (v2 and v3)
and combines results for better accuracy.
"""

import os
import cv2
import pytesseract
import re
from collections import Counter, defaultdict

def extract_lisa_data_v2(image_path: str):
    """Extract data using v2 method with people count detection"""
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"❌ Cannot read image: {image_path}"}

    image_resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config_all = r'--oem 3 --psm 6'
    text_all = pytesseract.image_to_string(thresh, config=config_all)

    def extract_numbers_with_commas(text):
        return re.findall(r'\d{1,3}(?:,\d{3})+', text)

    def extract_all_numbers(text):
        return re.findall(r'\d+', text)

    def extract_people_count(text):
        lines = text.split('\n')
        for line in lines:
            # Improved pattern to catch more variations
            match = re.search(r'[@#oO§© ]?(\d{3})\b', line)
            if match:
                return match.group(1)
        return ''

    numbers_with_commas = extract_numbers_with_commas(text_all)
    all_numbers = extract_all_numbers(text_all)
    people = extract_people_count(text_all)

    b_val = ''
    s_val = ''
    t_val = ''
    if len(all_numbers) >= 3:
        try:
            p_idx = next(i for i, v in enumerate(all_numbers) if len(v) == 3)
            b_val = all_numbers[p_idx - 2] if p_idx >= 2 else ''
            s_val = all_numbers[p_idx - 1] if p_idx >= 1 else ''
            t_val = all_numbers[p_idx + 1] if p_idx + 1 < len(all_numbers) else ''
        except StopIteration:
            b_val = all_numbers[0]
            s_val = all_numbers[1] if len(all_numbers) > 1 else ''
            t_val = all_numbers[2] if len(all_numbers) > 2 else ''

    mapped = {
        "b_value": b_val,
        "s_value": s_val,
        "t_value": t_val,
        "people_count": people,
        "dollar_amount": numbers_with_commas[0] if numbers_with_commas else ''
    }

    return {
        "raw_text": text_all.strip(),
        "mapped_result": mapped
    }

def extract_game_stat_v3(image_path: str):
    """Extract data using v3 method with improved pattern matching"""
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"❌ Cannot read image: {image_path}"}

    image_resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config_all = r'--oem 3 --psm 6'
    text_all = pytesseract.image_to_string(thresh, config=config_all).strip()

    # Improved regex patterns for better matching
    b_match = re.search(r'\bB\s?(\d{1,3})', text_all)
    s_match = re.search(r'\bS\s?(\d{1,3})', text_all)
    t_match = re.search(r'[\u25CB@\*oO\)§©]\s?(\d{1,3})', text_all)
    p_match = re.search(r'[👥#@§© ](\d{3})\b', text_all)
    dollar_match = re.search(r'\$\s?(\d{1,3}(?:,\d{3})+)', text_all)

    # Additional patterns for better extraction
    if not b_match:
        b_match = re.search(r'B(\d{1,3})', text_all)
    if not s_match:
        s_match = re.search(r'S(\d{1,3})', text_all)
    if not t_match:
        t_match = re.search(r'[T@](\d{1,3})', text_all)
    if not p_match:
        p_match = re.search(r'(\d{3})', text_all)  # Fallback for people count
    if not dollar_match:
        dollar_match = re.search(r'(\d{1,3}(?:,\d{3})+)', text_all)  # Fallback for dollar

    mapped = {
        "b_value": b_match.group(1) if b_match else '',
        "s_value": s_match.group(1) if s_match else '',
        "t_value": t_match.group(1) if t_match else '',
        "people_count": p_match.group(1) if p_match else '',
        "dollar_amount": dollar_match.group(1) if dollar_match else ''
    }

    return {
        "raw_text": text_all,
        "mapped_result": mapped
    }

def extract_stat_v4(image_path: str):
    """New v4 method with enhanced pattern recognition"""
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"❌ Cannot read image: {image_path}"}

    image_resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config_all = r'--oem 3 --psm 6'
    text_all = pytesseract.image_to_string(thresh, config=config_all).strip()

    # Extract all numbers first
    all_numbers = re.findall(r'\d+', text_all)
    numbers_with_commas = re.findall(r'\d{1,3}(?:,\d{3})+', text_all)
    
    # Find people count (3-digit numbers)
    people_count = ''
    for num in all_numbers:
        if len(num) == 3 and 100 <= int(num) <= 999:
            people_count = num
            break
    
    # Find dollar amount
    dollar_amount = numbers_with_commas[0] if numbers_with_commas else ''
    
    # Find B, S, T values by looking for patterns
    b_value = ''
    s_value = ''
    t_value = ''
    
    # Look for B/S/T patterns in text
    lines = text_all.split('\n')
    for line in lines:
        # B value patterns
        b_patterns = [r'B(\d{1,3})', r'\b(\d{1,3})\s*B', r'B\s*(\d{1,3})']
        for pattern in b_patterns:
            match = re.search(pattern, line)
            if match and not b_value:
                b_value = match.group(1)
                break
        
        # S value patterns
        s_patterns = [r'S(\d{1,3})', r'\b(\d{1,3})\s*S', r'S\s*(\d{1,3})']
        for pattern in s_patterns:
            match = re.search(pattern, line)
            if match and not s_value:
                s_value = match.group(1)
                break
        
        # T value patterns
        t_patterns = [r'[T@§©](\d{1,3})', r'\b(\d{1,3})\s*[T@§©]', r'[T@§©]\s*(\d{1,3})']
        for pattern in t_patterns:
            match = re.search(pattern, line)
            if match and not t_value:
                t_value = match.group(1)
                break
    
    # If not found by patterns, try position-based extraction
    if not b_value and len(all_numbers) >= 3:
        # Find the position of people count
        try:
            p_idx = next(i for i, v in enumerate(all_numbers) if v == people_count)
            if p_idx >= 2:
                b_value = all_numbers[p_idx - 2]
            if p_idx >= 1:
                s_value = all_numbers[p_idx - 1]
            if p_idx + 1 < len(all_numbers):
                t_value = all_numbers[p_idx + 1]
        except StopIteration:
            pass

    mapped = {
        "b_value": b_value,
        "s_value": s_value,
        "t_value": t_value,
        "people_count": people_count,
        "dollar_amount": dollar_amount
    }

    return {
        "raw_text": text_all,
        "mapped_result": mapped
    }

def extract_stat_combined(image_path: str):
    """Combine results from v2, v3, and v4 methods"""
    result_v2 = extract_lisa_data_v2(image_path)
    result_v3 = extract_game_stat_v3(image_path)
    result_v4 = extract_stat_v4(image_path)

    merged = {}
    for key in ['b_value', 's_value', 't_value', 'people_count', 'dollar_amount']:
        # Priority: v4 > v3 > v2
        val_v4 = result_v4["mapped_result"].get(key, '')
        val_v3 = result_v3["mapped_result"].get(key, '')
        val_v2 = result_v2["mapped_result"].get(key, '')
        
        merged[key] = val_v4 if val_v4 else (val_v3 if val_v3 else val_v2)

    return {
        "file": os.path.basename(image_path),
        "final_result": merged,
        "v2_result": result_v2["mapped_result"],
        "v3_result": result_v3["mapped_result"],
        "v4_result": result_v4["mapped_result"],
        "raw_text_v2": result_v2.get("raw_text", ""),
        "raw_text_v3": result_v3.get("raw_text", ""),
        "raw_text_v4": result_v4.get("raw_text", "")
    }

def batch_extract_advanced(folder_path: str):
    """Extract data from all images in folder"""
    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):
            full_path = os.path.join(folder_path, filename)
            result = extract_stat_combined(full_path)
            results.append(result)
    return results

def extract_from_clahe_advanced():
    """Extract data from CLAHE enhanced images using advanced methods"""
    results = []
    debug_folder = "./debug_images"

    if not os.path.exists(debug_folder):
        print("❌ Debug folder not found. Please run debug_image_processing.py first.")
        return results

    regions = ['daroka', 'lexi', 'mafer']

    for region in regions:
        region_folder = os.path.join(debug_folder, region)
        if os.path.exists(region_folder):
            for filename in os.listdir(region_folder):
                if "clahe_enhanced" in filename and filename.endswith(".png"):
                    full_path = os.path.join(region_folder, filename)
                    result = extract_stat_combined(full_path)
                    result["region"] = region
                    results.append(result)

    return results

def analyze_debug_images_consensus():
    """
    Analyze all debug images and find the most consistent results across different processing methods.
    Returns the best result for each region based on frequency analysis.
    """
    debug_folder = "./debug_images"
    results = {}
    
    if not os.path.exists(debug_folder):
        print("❌ Debug folder not found. Please run debug_image_processing.py first.")
        return results
    
    regions = ['daroka', 'lexi', 'mafer']
    
    for region in regions:
        print(f"\n🔍 Analyzing {region.upper()} region...")
        print("-" * 50)
        
        region_folder = os.path.join(debug_folder, region)
        if not os.path.exists(region_folder):
            print(f"❌ Region folder {region} not found")
            continue
        
        # Get all PNG files in the region folder
        image_files = [f for f in os.listdir(region_folder) if f.endswith('.png')]
        
        if not image_files:
            print(f"❌ No PNG files found in {region}")
            continue
        
        print(f"📁 Found {len(image_files)} debug images")
        
        # Extract data from all images using all methods
        all_results = []
        for filename in image_files:
            full_path = os.path.join(region_folder, filename)
            # Extract processing method from filename (remove common prefix and suffix)
            processing_method = filename.replace(f'screenshot_20250730_173118_{region}_cropped_', '').replace('.png', '')
            
            # Extract using all three methods
            result_v2 = extract_lisa_data_v2(full_path)
            result_v3 = extract_game_stat_v3(full_path)
            result_v4 = extract_stat_v4(full_path)
            
            result_entry = {
                'file': filename,
                'processing_method': processing_method,
                'v2': result_v2.get('mapped_result', {}),
                'v3': result_v3.get('mapped_result', {}),
                'v4': result_v4.get('mapped_result', {}),
                'raw_v2': result_v2.get('raw_text', ''),
                'raw_v3': result_v3.get('raw_text', ''),
                'raw_v4': result_v4.get('raw_text', '')
            }
            
            all_results.append(result_entry)
            
            # Print individual results
            print(f"  {processing_method:25} | V2: B:{result_entry['v2'].get('b_value', ''):>3} S:{result_entry['v2'].get('s_value', ''):>3} T:{result_entry['v2'].get('t_value', ''):>2} 👥:{result_entry['v2'].get('people_count', ''):>3} 💰:{result_entry['v2'].get('dollar_amount', '')}")
            print(f"  {'':25} | V3: B:{result_entry['v3'].get('b_value', ''):>3} S:{result_entry['v3'].get('s_value', ''):>3} T:{result_entry['v3'].get('t_value', ''):>2} 👥:{result_entry['v3'].get('people_count', ''):>3} 💰:{result_entry['v3'].get('dollar_amount', '')}")
            print(f"  {'':25} | V4: B:{result_entry['v4'].get('b_value', ''):>3} S:{result_entry['v4'].get('s_value', ''):>3} T:{result_entry['v4'].get('t_value', ''):>2} 👥:{result_entry['v4'].get('people_count', ''):>3} 💰:{result_entry['v4'].get('dollar_amount', '')}")
        
        # Find consensus for each field
        consensus_result = find_consensus(all_results)
        results[region] = consensus_result
        
        print(f"\n✅ {region.upper()} CONSENSUS RESULT:")
        print(f"   B: {consensus_result['b_value']:>3} | S: {consensus_result['s_value']:>3} | T: {consensus_result['t_value']:>2} | 👥: {consensus_result['people_count']:>3} | 💰: {consensus_result['dollar_amount']}")
        print(f"   Best method: {consensus_result['best_method']}")
        print(f"   Confidence: {consensus_result['confidence']:.1f}%")
    
    return results

def find_consensus(all_results):
    """
    Find the most consistent values across all results using frequency analysis.
    """
    fields = ['b_value', 's_value', 't_value', 'people_count', 'dollar_amount']
    consensus = {}
    
    # Collect all values for each field and method
    field_values = defaultdict(lambda: defaultdict(list))
    
    for result in all_results:
        for method in ['v2', 'v3', 'v4']:
            for field in fields:
                value = result[method].get(field, '')
                if value:  # Only count non-empty values
                    field_values[field][method].append(value)
    
    # Find most common value for each field
    for field in fields:
        all_values = []
        for method in ['v2', 'v3', 'v4']:
            all_values.extend(field_values[field][method])
        
        if all_values:
            # Count frequency of each value
            value_counts = Counter(all_values)
            most_common_value, count = value_counts.most_common(1)[0]
            total_count = len(all_values)
            confidence = (count / total_count) * 100
            
            consensus[field] = most_common_value
            consensus[f'{field}_confidence'] = confidence
            consensus[f'{field}_count'] = count
            consensus[f'{field}_total'] = total_count
        else:
            consensus[field] = ''
            consensus[f'{field}_confidence'] = 0
            consensus[f'{field}_count'] = 0
            consensus[f'{field}_total'] = 0
    
    # Determine best method based on overall confidence
    method_scores = {}
    for method in ['v2', 'v3', 'v4']:
        method_score = 0
        method_total = 0
        for field in fields:
            if field_values[field][method]:
                method_score += len(field_values[field][method])
                method_total += 1
        
        if method_total > 0:
            method_scores[method] = method_score / method_total
        else:
            method_scores[method] = 0
    
    best_method = max(method_scores, key=method_scores.get)
    overall_confidence = sum(consensus[f'{field}_confidence'] for field in fields) / len(fields)
    
    consensus['best_method'] = best_method
    consensus['confidence'] = overall_confidence
    
    return consensus

def generate_consensus_report():
    """
    Generate a comprehensive report of consensus analysis from debug images.
    """
    print("🚀 DEBUG IMAGES CONSENSUS ANALYSIS")
    print("=" * 60)
    
    results = analyze_debug_images_consensus()
    
    if not results:
        print("❌ No results to report")
        return
    
    print("\n📊 FINAL CONSENSUS REPORT")
    print("=" * 60)
    
    for region, consensus in results.items():
        print(f"\n{region.upper()}:")
        print(f"  B: {consensus['b_value']:>3} (confidence: {consensus['b_value_confidence']:.1f}%, {consensus['b_value_count']}/{consensus['b_value_total']})")
        print(f"  S: {consensus['s_value']:>3} (confidence: {consensus['s_value_confidence']:.1f}%, {consensus['s_value_count']}/{consensus['s_value_total']})")
        print(f"  T: {consensus['t_value']:>2} (confidence: {consensus['t_value_confidence']:.1f}%, {consensus['t_value_count']}/{consensus['t_value_total']})")
        print(f"  👥: {consensus['people_count']:>3} (confidence: {consensus['people_count_confidence']:.1f}%, {consensus['people_count_count']}/{consensus['people_count_total']})")
        print(f"  💰: {consensus['dollar_amount']} (confidence: {consensus['dollar_amount_confidence']:.1f}%, {consensus['dollar_amount_count']}/{consensus['dollar_amount_total']})")
        print(f"  Best method: {consensus['best_method']}")
        print(f"  Overall confidence: {consensus['confidence']:.1f}%")
    
    # Save results to CSV
    save_consensus_to_csv(results)
    
    print("\n✅ Consensus analysis complete!")

def save_consensus_to_csv(results):
    """
    Save consensus results to CSV file.
    """
    import csv
    
    csv_filename = "consensus_results.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['region', 'b_value', 'b_confidence', 's_value', 's_confidence', 
                     't_value', 't_confidence', 'people_count', 'people_confidence',
                     'dollar_amount', 'dollar_confidence', 'best_method', 'overall_confidence']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for region, consensus in results.items():
            row = {
                'region': region,
                'b_value': consensus['b_value'],
                'b_confidence': f"{consensus['b_value_confidence']:.1f}%",
                's_value': consensus['s_value'],
                's_confidence': f"{consensus['s_value_confidence']:.1f}%",
                't_value': consensus['t_value'],
                't_confidence': f"{consensus['t_value_confidence']:.1f}%",
                'people_count': consensus['people_count'],
                'people_confidence': f"{consensus['people_count_confidence']:.1f}%",
                'dollar_amount': consensus['dollar_amount'],
                'dollar_confidence': f"{consensus['dollar_amount_confidence']:.1f}%",
                'best_method': consensus['best_method'],
                'overall_confidence': f"{consensus['confidence']:.1f}%"
            }
            writer.writerow(row)
    
    print(f"💾 Results saved to {csv_filename}")

def get_consensus_results():
    """
    Get consensus results in a simple format.
    Returns a dictionary with the best results for each region.
    """
    results = analyze_debug_images_consensus()
    
    # Format results in a clean way
    formatted_results = {}
    for region, consensus in results.items():
        formatted_results[region] = {
            'b_value': consensus['b_value'],
            's_value': consensus['s_value'], 
            't_value': consensus['t_value'],
            'people_count': consensus['people_count'],
            'dollar_amount': consensus['dollar_amount'],
            'confidence': consensus['confidence'],
            'best_method': consensus['best_method']
        }
    
    return formatted_results

def print_simple_consensus():
    """
    Print consensus results in a simple, clean format.
    """
    results = get_consensus_results()
    
    print("🎯 FINAL CONSENSUS RESULTS")
    print("=" * 50)
    
    for region, data in results.items():
        print(f"{region.upper()}: B: {data['b_value']:>3} | S: {data['s_value']:>3} | T: {data['t_value']:>2} | 👥: {data['people_count']:>3} | 💰: {data['dollar_amount']}")
        print(f"   Confidence: {data['confidence']:.1f}% | Best Method: {data['best_method']}")
        print()

def main():
    """Main function to run advanced data extraction"""
    print("🚀 Advanced Data Extraction from TapTap Images")
    print("=" * 60)
    
    # Extract from original cropped images
    print("\n📁 Extracting from original cropped images...")
    print("-" * 50)
    
    if os.path.exists("images"):
        original_results = batch_extract_advanced("images")
        if original_results:
            print(f"Found {len(original_results)} cropped images")
            for result in original_results:
                m = result['final_result']
                print(f"{result['file']:45} | B:{m['b_value']:>3} | S:{m['s_value']:>3} | T:{m['t_value']:>2} | 👥:{m['people_count']:>3} | 💰:{m['dollar_amount']}")
                print(f"   V2: B:{m['b_value']:>3} S:{m['s_value']:>3} T:{m['t_value']:>2} 👥:{m['people_count']:>3} 💰:{m['dollar_amount']}")
                print(f"   V3: B:{m['b_value']:>3} S:{m['s_value']:>3} T:{m['t_value']:>2} 👥:{m['people_count']:>3} 💰:{m['dollar_amount']}")
                print(f"   V4: B:{m['b_value']:>3} S:{m['s_value']:>3} T:{m['t_value']:>2} 👥:{m['people_count']:>3} 💰:{m['dollar_amount']}")
                print(f"   Raw V2: '{result.get('raw_text_v2', '')[:50]}...'")
                print(f"   Raw V3: '{result.get('raw_text_v3', '')[:50]}...'")
                print(f"   Raw V4: '{result.get('raw_text_v4', '')[:50]}...'")
                print()
    
    # Extract from CLAHE enhanced images
    print("\n📁 Extracting from CLAHE enhanced images...")
    print("-" * 50)
    
    clahe_results = extract_from_clahe_advanced()
    if clahe_results:
        print(f"Found {len(clahe_results)} CLAHE enhanced images")
        for result in clahe_results:
            region = result.get('region', '').upper()
            m = result['final_result']
            print(f"[{region}] {result['file']:45} | B:{m['b_value']:>3} | S:{m['s_value']:>3} | T:{m['t_value']:>2} | 👥:{m['people_count']:>3} | 💰:{m['dollar_amount']}")
            print(f"   V2: B:{result['v2_result']['b_value']:>3} S:{result['v2_result']['s_value']:>3} T:{result['v2_result']['t_value']:>2} 👥:{result['v2_result']['people_count']:>3} 💰:{result['v2_result']['dollar_amount']}")
            print(f"   V3: B:{result['v3_result']['b_value']:>3} S:{result['v3_result']['s_value']:>3} T:{result['v3_result']['t_value']:>2} 👥:{result['v3_result']['people_count']:>3} 💰:{result['v3_result']['dollar_amount']}")
            print(f"   V4: B:{result['v4_result']['b_value']:>3} S:{result['v4_result']['s_value']:>3} T:{result['v4_result']['t_value']:>2} 👥:{result['v4_result']['people_count']:>3} 💰:{result['v4_result']['dollar_amount']}")
            print(f"   Raw V2: '{result.get('raw_text_v2', '')[:50]}...'")
            print(f"   Raw V3: '{result.get('raw_text_v3', '')[:50]}...'")
            print(f"   Raw V4: '{result.get('raw_text_v4', '')[:50]}...'")
            print()
    
    # Run consensus analysis
    print("\n🔍 Running consensus analysis on debug images...")
    print("-" * 50)
    generate_consensus_report()
    
    print("✅ Advanced data extraction complete!")

if __name__ == "__main__":
    main() 