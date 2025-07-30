# TapTap Debug Images Consensus Analysis

## Overview

This feature analyzes all debug images generated from different image processing methods and finds the most consistent OCR results across multiple extraction algorithms. It helps overcome OCR difficulties caused by text/number colors being blurry against backgrounds.

## How It Works

1. **Multiple Processing Methods**: Each debug image is processed using 3 different OCR extraction methods (V2, V3, V4)
2. **Frequency Analysis**: The system counts how often each value appears across all methods and processing techniques
3. **Consensus Finding**: The most frequently detected value for each field becomes the consensus result
4. **Confidence Scoring**: Each result includes a confidence percentage based on how consistent the detection was

## Usage

### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run consensus analysis
python consensus_analyzer.py
```

### Programmatic Usage

```python
from src.utils.advanced_data_extraction import get_consensus_results, print_simple_consensus

# Get results as dictionary
results = get_consensus_results()

# Print simple results
print_simple_consensus()
```

## Output Format

### Console Output
```
🎯 FINAL CONSENSUS RESULTS
==================================================
DAROKA: B:  49 | S:  33 | T: 46 | 👥: 315 | 💰: 33,945
   Confidence: 71.0% | Best Method: v2

LEXI: B:  49 | S:   2 | T:  2 | 👥: 697 | 💰: 17,803
   Confidence: 78.2% | Best Method: v3

MAFER: B:  45 | S:  22 | T:  4 | 👥: 319 | 💰: 1,503
   Confidence: 79.9% | Best Method: v3
```

### CSV Output
The results are also saved to `consensus_results.csv` with detailed confidence scores for each field.

### Dictionary Format
```python
{
    'daroka': {
        'b_value': '49',
        's_value': '33', 
        't_value': '46',
        'people_count': '315',
        'dollar_amount': '33,945',
        'confidence': 71.0,
        'best_method': 'v2'
    },
    'lexi': { ... },
    'mafer': { ... }
}
```

## File Structure Requirements

```
debug_images/
├── daroka/
│   ├── screenshot_20250730_173118_daroka_cropped_original.png
│   ├── screenshot_20250730_173118_daroka_cropped_clahe_enhanced.png
│   ├── screenshot_20250730_173118_daroka_cropped_otsu_binarized.png
│   └── ... (other processed images)
├── lexi/
│   └── ... (processed images)
└── mafer/
    └── ... (processed images)
```

## Processing Methods Analyzed

The system analyzes results from these image processing techniques:
- `original` - Original cropped image
- `clahe_enhanced` - CLAHE (Contrast Limited Adaptive Histogram Equalization)
- `otsu_binarized` - Otsu thresholding
- `adaptive_binarized` - Adaptive thresholding
- `histogram_equalized` - Histogram equalization
- `gamma_corrected` - Gamma correction
- `denoised` - Noise reduction
- `gaussian_blur` - Gaussian blur
- `median_blur` - Median blur
- `bilateral_filter` - Bilateral filtering
- `dilated` - Morphological dilation
- `eroded` - Morphological erosion
- `opening` - Morphological opening
- `closing` - Morphological closing
- `deskewed` - Image deskewing
- `bordered` - Border addition
- `rescaled` - Image rescaling
- `processed_17` - Custom processing method
- `adaptive2_binarized` - Alternative adaptive thresholding

## OCR Extraction Methods

### V2 Method
- Uses people count detection
- Position-based extraction
- Basic pattern matching

### V3 Method  
- Improved pattern matching
- Enhanced regex patterns
- Better field identification

### V4 Method
- Enhanced pattern recognition
- Position-based fallback
- Advanced number detection

## Confidence Scoring

- **100%**: All methods detected the same value
- **80-99%**: High consistency across methods
- **60-79%**: Moderate consistency
- **Below 60%**: Low consistency, may need manual verification

## Best Practices

1. **Run debug image processing first** to generate all the processed images
2. **Check confidence scores** - higher confidence means more reliable results
3. **Review the best method** - different regions may work better with different extraction methods
4. **Use CSV output** for detailed analysis and reporting
5. **Manual verification** for results with low confidence scores

## Troubleshooting

### No debug_images folder
```
❌ Debug folder not found. Please run debug_image_processing.py first.
```
**Solution**: Run the debug image processing script first to generate the processed images.

### Missing dependencies
```
ModuleNotFoundError: No module named 'pytesseract'
```
**Solution**: Install dependencies in the virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Low confidence scores
- Check if the original images have good quality
- Try different image processing methods
- Consider manual verification for critical data

## Example Results

Based on the analysis, here are typical results:

| Region | B Value | S Value | T Value | People Count | Dollar Amount | Confidence |
|--------|---------|---------|---------|--------------|---------------|------------|
| DAROKA | 49      | 33      | 46      | 315          | 33,945        | 71.0%      |
| LEXI   | 49      | 2       | 2       | 697          | 17,803        | 78.2%      |
| MAFER  | 45      | 22      | 4       | 319          | 1,503         | 79.9%      |

This consensus analysis provides much more reliable results than using any single processing method alone! 