#!/usr/bin/env python3
"""
Advanced Data Extraction for TapTap
==================================

This module uses multiple extraction methods (v2, v3, v4)
and combines results for better accuracy with optimized consensus analysis.
"""

import os
import cv2
import pytesseract
import re
import csv
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional


class TapTapDataExtractor:
    """
    Main class for extracting data from TapTap images using multiple OCR methods.
    """
    
    def __init__(self):
        """Initialize the data extractor with default settings."""
        self.regions = ['daroka', 'lexi', 'mafer']
        self.fields = ['b_value', 's_value', 't_value', 'people_count', 'dollar_amount']
        
    def extract_lisa_data_v2(self, image_path: str) -> Dict:
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

    def extract_game_stat_v3(self, image_path: str) -> Dict:
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

    def extract_stat_v4(self, image_path: str) -> Dict:
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

    def extract_stat_combined(self, image_path: str) -> Dict:
        """Combine results from v2, v3, and v4 methods"""
        result_v2 = self.extract_lisa_data_v2(image_path)
        result_v3 = self.extract_game_stat_v3(image_path)
        result_v4 = self.extract_stat_v4(image_path)

        merged = {}
        for key in self.fields:
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

    def batch_extract_advanced(self, folder_path: str) -> List[Dict]:
        """Extract data from all images in folder"""
        results = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".png"):
                full_path = os.path.join(folder_path, filename)
                result = self.extract_stat_combined(full_path)
                results.append(result)
        return results

    def extract_from_clahe_advanced(self) -> List[Dict]:
        """Extract data from CLAHE enhanced images using advanced methods"""
        results = []
        debug_folder = "../../images"

        if not os.path.exists(debug_folder):
            print("❌ Images folder not found. Please run the continuous monitoring first to generate images.")
            return results

        for region in self.regions:
            region_folder = os.path.join(debug_folder, region)
            if os.path.exists(region_folder):
                for filename in os.listdir(region_folder):
                    if "clahe_enhanced" in filename and filename.endswith(".png"):
                        full_path = os.path.join(region_folder, filename)
                        result = self.extract_stat_combined(full_path)
                        result["region"] = region
                        results.append(result)

        return results


class ConsensusAnalyzer:
    """
    Class for analyzing consensus across multiple debug images and processing methods.
    """
    
    def __init__(self, extractor: TapTapDataExtractor):
        """Initialize with a data extractor instance."""
        self.extractor = extractor
        self.regions = extractor.regions
        self.fields = extractor.fields
        
    def analyze_debug_images_consensus(self) -> Dict:
        """
        Analyze all debug images and find the most consistent results across different processing methods.
        Returns the best result for each region based on frequency analysis.
        """
        debug_folder = "../../images"
        results = {}
        
        if not os.path.exists(debug_folder):
            print("❌ Images folder not found. Please run the continuous monitoring first to generate images.")
            return results
        
        for region in self.regions:
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
                result_v2 = self.extractor.extract_lisa_data_v2(full_path)
                result_v3 = self.extractor.extract_game_stat_v3(full_path)
                result_v4 = self.extractor.extract_stat_v4(full_path)
                
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
            consensus_result = self._find_consensus(all_results)
            results[region] = consensus_result
            
            print(f"\n✅ {region.upper()} CONSENSUS RESULT:")
            print(f"   B: {consensus_result['b_value']:>3} | S: {consensus_result['s_value']:>3} | T: {consensus_result['t_value']:>2} | 👥: {consensus_result['people_count']:>3} | 💰: {consensus_result['dollar_amount']}")
            print(f"   Best method: {consensus_result['best_method']}")
            print(f"   Confidence: {consensus_result['confidence']:.1f}%")
        
        return results

    def _find_consensus(self, all_results: List[Dict]) -> Dict:
        """
        Find the most consistent values across all results using frequency analysis.
        """
        consensus = {}
        
        # Collect all values for each field and method
        field_values = defaultdict(lambda: defaultdict(list))
        
        for result in all_results:
            for method in ['v2', 'v3', 'v4']:
                for field in self.fields:
                    value = result[method].get(field, '')
                    if value:  # Only count non-empty values
                        field_values[field][method].append(value)
        
        # Find most common value for each field
        for field in self.fields:
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
            for field in self.fields:
                if field_values[field][method]:
                    method_score += len(field_values[field][method])
                    method_total += 1
            
            if method_total > 0:
                method_scores[method] = method_score / method_total
            else:
                method_scores[method] = 0
        
        best_method = max(method_scores, key=method_scores.get)
        overall_confidence = sum(consensus[f'{field}_confidence'] for field in self.fields) / len(self.fields)
        
        consensus['best_method'] = best_method
        consensus['confidence'] = overall_confidence
        
        return consensus

    def generate_consensus_report(self) -> None:
        """
        Generate a comprehensive report of consensus analysis from debug images.
        """
        print("🚀 DEBUG IMAGES CONSENSUS ANALYSIS")
        print("=" * 60)
        
        results = self.analyze_debug_images_consensus()
        
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
        self._save_consensus_to_csv(results)
        
        print("\n✅ Consensus analysis complete!")

    def _save_consensus_to_csv(self, results: Dict) -> None:
        """
        Save consensus results to CSV file.
        """
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

    def get_consensus_results(self) -> Dict:
        """
        Get consensus results in a simple format.
        Returns a dictionary with the best results for each region.
        """
        results = self.analyze_debug_images_consensus()
        
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

    def print_simple_consensus(self) -> None:
        """
        Print consensus results in a simple, clean format.
        """
        results = self.get_consensus_results()
        
        print("🎯 FINAL CONSENSUS RESULTS")
        print("=" * 50)
        
        for region, data in results.items():
            print(f"{region.upper()}: B: {data['b_value']:>3} | S: {data['s_value']:>3} | T: {data['t_value']:>2} | 👥: {data['people_count']:>3} | 💰: {data['dollar_amount']}")
            print(f"   Confidence: {data['confidence']:.1f}% | Best Method: {data['best_method']}")
            print()


class OptimizedConsensusAnalyzer(ConsensusAnalyzer):
    """
    Optimized consensus analyzer with smart sampling and early termination.
    """
    
    def __init__(self, extractor: TapTapDataExtractor):
        """Initialize the optimized analyzer."""
        super().__init__(extractor)
        self.method_priority = {
            # 'otsu_binarized': 1,      # Usually very effective
            # 'clahe_enhanced': 2,      # Good for contrast issues
            # 'original': 3,            # Baseline
            # 'histogram_equalized': 4, # Good for brightness issues
            'adaptive_binarized': 5,  # Good for varying lighting
            # 'gamma_corrected': 6,     # Good for dark images
            # 'denoised': 7,           # Good for noisy images
            # 'median_blur': 8,        # Good for salt-and-pepper noise
            # 'bilateral_filter': 9,    # Good for edge preservation
            # 'opening': 10,           # Morphological operations
            # 'closing': 11,
            # 'dilated': 12,
            # 'eroded': 13,
            # 'deskewed': 14,          # Good for rotated text
            # 'bordered': 15,          # Good for edge text
            # 'rescaled': 16,          # Basic scaling
            'gaussian_blur': 17,     # May blur text too much
            # 'adaptive2_binarized': 18, # Alternative method
            'processed_17': 19       # Custom method (lowest priority)
        }
    
    def analyze_debug_images_consensus_optimized(self, sample_size: int = 5, confidence_threshold: float = 80.0) -> Dict:
        """
        Optimized consensus analysis using smart sampling and early termination.
        
        Args:
            sample_size: Number of most promising images to process (default: 5)
            confidence_threshold: Stop processing if confidence reaches this level (default: 80%)
        """
        debug_folder = "../../images"
        results = {}
        
        if not os.path.exists(debug_folder):
            print("❌ Images folder not found. Please run the continuous monitoring first to generate images.")
            return results
        
        for region in self.regions:
            print(f"\n🔍 Analyzing {region.upper()} region (optimized)...")
            print("-" * 50)
            
            region_folder = os.path.join(debug_folder, region)
            if not os.path.exists(region_folder):
                print(f"❌ Region folder {region} not found")
                continue
            
            # Get all PNG files and prioritize them
            image_files = [f for f in os.listdir(region_folder) if f.endswith('.png')]
            
            if not image_files:
                print(f"❌ No PNG files found in {region}")
                continue
            
            print(f"📁 Found {len(image_files)} debug images")
            
            # Prioritize images by processing method (most promising first)
            prioritized_files = self._prioritize_images_by_method(image_files)
            
            # Take only the top N most promising images
            selected_files = prioritized_files[:sample_size]
            print(f"🎯 Processing top {len(selected_files)} most promising images")
            
            # Process selected images with early termination
            consensus_result = self._process_images_with_early_termination(
                region_folder, selected_files, region, confidence_threshold
            )
            
            results[region] = consensus_result
            
            print(f"\n✅ {region.upper()} OPTIMIZED CONSENSUS RESULT:")
            print(f"   B: {consensus_result['b_value']:>3} | S: {consensus_result['s_value']:>3} | T: {consensus_result['t_value']:>2} | 👥: {consensus_result['people_count']:>3} | 💰: {consensus_result['dollar_amount']}")
            print(f"   Best method: {consensus_result['best_method']}")
            print(f"   Confidence: {consensus_result['confidence']:.1f}%")
            print(f"   Images processed: {consensus_result['images_processed']}/{len(image_files)}")
        
        return results

    def _prioritize_images_by_method(self, image_files: List[str]) -> List[str]:
        """
        Prioritize images based on processing method effectiveness.
        Returns sorted list of filenames with most promising methods first.
        """
        def get_priority(filename):
            # Extract method name from filename
            for method in self.method_priority:
                if method in filename:
                    return self.method_priority[method]
            return 999  # Unknown method gets lowest priority
        
        # Sort by priority (lower number = higher priority)
        return sorted(image_files, key=get_priority)

    def _process_images_with_early_termination(self, region_folder: str, image_files: List[str], region: str, confidence_threshold: float) -> Dict:
        """
        Process images with early termination when confidence threshold is reached.
        """
        field_values = defaultdict(list)
        images_processed = 0
        
        for filename in image_files:
            full_path = os.path.join(region_folder, filename)
            processing_method = filename.replace(f'screenshot_20250730_173118_{region}_cropped_', '').replace('.png', '')
            
            print(f"  Processing: {processing_method}")
            
            # Extract using all three methods
            result_v2 = self.extractor.extract_lisa_data_v2(full_path)
            result_v3 = self.extractor.extract_game_stat_v3(full_path)
            result_v4 = self.extractor.extract_stat_v4(full_path)
            
            # Collect all values
            for method_result in [result_v2, result_v3, result_v4]:
                mapped_result = method_result.get('mapped_result', {})
                for field in self.fields:
                    value = mapped_result.get(field, '')
                    if value:
                        field_values[field].append(value)
            
            images_processed += 1
            
            # Check if we have enough confidence to stop early
            current_confidence = self._calculate_current_confidence(field_values)
            print(f"    Current confidence: {current_confidence:.1f}%")
            
            if current_confidence >= confidence_threshold:
                print(f"    ✅ Early termination: confidence {current_confidence:.1f}% >= {confidence_threshold}%")
                break
        
        # Calculate final consensus
        consensus = self._calculate_consensus_from_values(field_values)
        consensus['images_processed'] = images_processed
        
        return consensus

    def _calculate_current_confidence(self, field_values: Dict) -> float:
        """
        Calculate current confidence based on collected values.
        """
        if not field_values:
            return 0.0
        
        total_confidence = 0
        for field in self.fields:
            values = field_values[field]
            if values:
                # Count most common value
                value_counts = Counter(values)
                most_common_count = value_counts.most_common(1)[0][1]
                field_confidence = (most_common_count / len(values)) * 100
                total_confidence += field_confidence
        
        return total_confidence / len(self.fields)

    def _calculate_consensus_from_values(self, field_values: Dict) -> Dict:
        """
        Calculate consensus from collected field values.
        """
        consensus = {}
        
        for field in self.fields:
            values = field_values[field]
            if values:
                value_counts = Counter(values)
                most_common_value, count = value_counts.most_common(1)[0]
                total_count = len(values)
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
        
        # Determine best method (simplified for optimization)
        consensus['best_method'] = 'v3'  # Default to v3 as it's usually most reliable
        overall_confidence = sum(consensus[f'{field}_confidence'] for field in self.fields) / len(self.fields)
        consensus['confidence'] = overall_confidence
        
        return consensus

    def get_consensus_results_optimized(self, sample_size: int = 5, confidence_threshold: float = 80.0) -> Dict:
        """
        Get consensus results using optimized approach.
        """
        results = self.analyze_debug_images_consensus_optimized(sample_size, confidence_threshold)
        
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
                'best_method': consensus['best_method'],
                'images_processed': consensus.get('images_processed', 0)
            }
        
        return formatted_results

    def print_optimized_consensus(self, sample_size: int = 5, confidence_threshold: float = 80.0) -> None:
        """
        Print consensus results using optimized approach.
        """
        results = self.get_consensus_results_optimized(sample_size, confidence_threshold)
        
        print("🎯 OPTIMIZED CONSENSUS RESULTS")
        print("=" * 50)
        print(f"📊 Sample size: {sample_size}, Confidence threshold: {confidence_threshold}%")
        print()
        
        for region, data in results.items():
            print(f"{region.upper()}: B: {data['b_value']:>3} | S: {data['s_value']:>3} | T: {data['t_value']:>2} | 👥: {data['people_count']:>3} | 💰: {data['dollar_amount']}")
            print(f"   Confidence: {data['confidence']:.1f}% | Best Method: {data['best_method']} | Images: {data['images_processed']}")
            print()


# Convenience functions for backward compatibility
def extract_lisa_data_v2(image_path: str) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    return extractor.extract_lisa_data_v2(image_path)

def extract_game_stat_v3(image_path: str) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    return extractor.extract_game_stat_v3(image_path)

def extract_stat_v4(image_path: str) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    return extractor.extract_stat_v4(image_path)

def extract_stat_combined(image_path: str) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    return extractor.extract_stat_combined(image_path)

def batch_extract_advanced(folder_path: str) -> List[Dict]:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    return extractor.batch_extract_advanced(folder_path)

def extract_from_clahe_advanced() -> List[Dict]:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    return extractor.extract_from_clahe_advanced()

def analyze_debug_images_consensus() -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    return analyzer.analyze_debug_images_consensus()

def find_consensus(all_results: List[Dict]) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    return analyzer._find_consensus(all_results)

def generate_consensus_report() -> None:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    analyzer.generate_consensus_report()

def save_consensus_to_csv(results: Dict) -> None:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    analyzer._save_consensus_to_csv(results)

def get_consensus_results() -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    return analyzer.get_consensus_results()

def print_simple_consensus() -> None:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    analyzer.print_simple_consensus()

def analyze_debug_images_consensus_optimized(sample_size: int = 5, confidence_threshold: float = 80.0) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = OptimizedConsensusAnalyzer(extractor)
    return analyzer.analyze_debug_images_consensus_optimized(sample_size, confidence_threshold)

def get_consensus_results_optimized(sample_size: int = 5, confidence_threshold: float = 80.0) -> Dict:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = OptimizedConsensusAnalyzer(extractor)
    return analyzer.get_consensus_results_optimized(sample_size, confidence_threshold)

def print_optimized_consensus(sample_size: int = 5, confidence_threshold: float = 80.0) -> None:
    """Convenience function for backward compatibility."""
    extractor = TapTapDataExtractor()
    analyzer = OptimizedConsensusAnalyzer(extractor)
    analyzer.print_optimized_consensus(sample_size, confidence_threshold)


def main():
    """Main function to run advanced data extraction"""
    print("🚀 Advanced Data Extraction from TapTap Images")
    print("=" * 60)
    
    # Create extractor and analyzer instances
    extractor = TapTapDataExtractor()
    analyzer = ConsensusAnalyzer(extractor)
    optimized_analyzer = OptimizedConsensusAnalyzer(extractor)
    
    # Extract from original cropped images
    print("\n📁 Extracting from original cropped images...")
    print("-" * 50)
    
    if os.path.exists("images"):
        original_results = extractor.batch_extract_advanced("images")
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
    
    clahe_results = extractor.extract_from_clahe_advanced()
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
    analyzer.generate_consensus_report()
    
    print("✅ Advanced data extraction complete!")


if __name__ == "__main__":
    main() 