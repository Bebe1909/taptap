# TapTap Continuous Monitoring with Consensus Analysis

## Overview

This enhanced system provides continuous monitoring of TapTap game data with advanced consensus analysis to ensure the highest accuracy in text extraction. The system runs for 60 seconds with captures every 5 seconds, applying consensus analysis to each iteration.

## Key Features

### 🔄 Continuous Monitoring
- **Duration**: 60 seconds total runtime
- **Capture Interval**: Every 5 seconds (12 iterations total)
- **Real-time Processing**: Each iteration includes screenshot, cropping, extraction, and consensus analysis

### 🔍 Consensus Analysis Integration
- **Multi-Method Extraction**: Uses V2, V3, and V4 extraction methods
- **Confidence Scoring**: Calculates confidence levels for each extracted value
- **Optimized Processing**: Smart sampling and early termination for performance
- **Best Result Selection**: Automatically selects the most consistent results

### 📊 Performance Tracking
- **Detailed Metrics**: Tracks timing for each step (screenshot, crop, extract, consensus)
- **Performance Analysis**: Identifies bottlenecks and provides optimization recommendations
- **Confidence Trends**: Monitors confidence levels across iterations
- **Error Tracking**: Logs and reports any errors during processing

## Usage

### Quick Start (Recommended)
```bash
# Run continuous monitoring (60 seconds, 5-second intervals)
python3 run_consensus_analysis.py continuous
```

### Test Mode (15 seconds)
```bash
# Test the functionality first (15 seconds, 3 iterations)
python3 test_continuous_monitoring.py
```

### Legacy Modes
```bash
# Run full consensus analysis on existing images
python3 run_consensus_analysis.py full

# Run optimized consensus analysis on existing images
python3 run_consensus_analysis.py optimized
```

## Output Structure

### Continuous Results Directory
```
continuous_results/
├── performance_report.json      # Comprehensive performance analysis
├── iteration_1.csv             # Detailed results for each iteration
├── iteration_2.csv
├── ...
└── iteration_12.csv
```

### Performance Report Contents
```json
{
  "summary": {
    "total_iterations": 12,
    "total_duration": 58.5,
    "average_iteration_time": 4.87,
    "average_confidence": 85.2,
    "errors_count": 0
  },
  "timing_breakdown": {
    "average_screenshot_time": 2.1,
    "average_crop_time": 0.3,
    "average_extract_time": 1.2,
    "average_consensus_time": 1.3
  },
  "performance_analysis": {
    "fastest_iteration": 5,
    "fastest_time": 3.8,
    "slowest_iteration": 2,
    "slowest_time": 6.2,
    "recommendations": [
      "Consider reducing capture frequency (currently 5s)"
    ]
  },
  "consensus_analysis": {
    "average_confidence": 85.2,
    "confidence_trend": [82, 85, 87, 86, 88, 85, 84, 86, 87, 85, 86, 87]
  }
}
```

## Workflow Process

### Each Iteration (5 seconds):
1. **📸 Screenshot Capture**
   - Navigate to TapTap website
   - Login and access game page
   - Take full-page screenshot
   - **Timing**: ~2-3 seconds

2. **✂️ Region Cropping**
   - Crop three regions: daroka, lexi, mafer
   - Save cropped images for processing
   - **Timing**: ~0.3 seconds

3. **📝 Data Extraction**
   - Apply enhanced image processing
   - Extract text using multiple OCR methods
   - **Timing**: ~1-2 seconds

4. **🔍 Consensus Analysis**
   - Run V2, V3, V4 extraction methods
   - Calculate confidence scores
   - Select best results
   - **Timing**: ~1-2 seconds

5. **📊 Results Storage**
   - Save iteration results to CSV
   - Update performance metrics
   - **Timing**: ~0.1 seconds

## Performance Optimization

### Current Performance Targets
- **Total Iteration Time**: < 5 seconds
- **Screenshot Time**: < 3 seconds
- **Consensus Analysis Time**: < 2 seconds
- **Confidence Level**: > 80%

### Optimization Recommendations
The system automatically provides recommendations based on performance analysis:

- **High Iteration Time**: Consider reducing capture frequency
- **Slow Screenshots**: Check web automation and network speed
- **Slow Consensus**: Reduce sample size or increase confidence threshold
- **Low Confidence**: Check image quality and OCR settings

## Consensus Analysis Details

### Extraction Methods
1. **V2 Method**: Enhanced pattern matching with people count detection
2. **V3 Method**: Improved regex patterns for better accuracy
3. **V4 Method**: Advanced number extraction with validation

### Confidence Calculation
- **Field Agreement**: Percentage of methods agreeing on each field
- **Pattern Validation**: Confidence in regex pattern matches
- **Number Validation**: Confidence in numeric value extraction
- **Overall Confidence**: Weighted average across all fields

### Best Result Selection
- **Majority Voting**: Select most common value across methods
- **Confidence Weighting**: Prioritize results with higher confidence
- **Pattern Validation**: Validate against expected formats
- **Fallback Logic**: Use best available result if consensus fails

## Error Handling

### Graceful Error Recovery
- **Network Issues**: Retry with exponential backoff
- **OCR Failures**: Fall back to alternative methods
- **Image Processing Errors**: Skip iteration and continue
- **Consensus Failures**: Use best available result

### Error Logging
- **Detailed Error Messages**: Full error context and stack traces
- **Error Categorization**: Network, OCR, processing, consensus errors
- **Performance Impact**: Track how errors affect timing
- **Recovery Success**: Monitor successful error recovery

## Configuration Options

### Timing Configuration
```python
# In run_consensus_analysis.py
TOTAL_DURATION = 60  # seconds
CAPTURE_INTERVAL = 5  # seconds
```

### Consensus Configuration
```python
# In consensus analysis
SAMPLE_SIZE = 1  # images per region
CONFIDENCE_THRESHOLD = 70.0  # minimum confidence percentage
```

### Performance Thresholds
```python
# Performance targets
MAX_ITERATION_TIME = 5.0  # seconds
MAX_SCREENSHOT_TIME = 3.0  # seconds
MAX_CONSENSUS_TIME = 2.0  # seconds
MIN_CONFIDENCE = 80.0  # percentage
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ❌ Import error: No module named 'src.utils.full_flow'
   ```
   **Solution**: Ensure all required modules are in `src/utils/`

2. **Web Automation Failures**
   ```
   ❌ Error in iteration X: Navigation timeout
   ```
   **Solution**: Check internet connection and website availability

3. **OCR Failures**
   ```
   ⚠️ Consensus analysis error: OCR processing failed
   ```
   **Solution**: Verify Tesseract installation and image quality

4. **Performance Issues**
   ```
   ⚠️ Iteration took longer than 5s (6.2s)
   ```
   **Solution**: Check system resources and network speed

### Debug Mode
Run with verbose logging to identify issues:
```bash
# Add debug logging to see detailed output
python3 -u run_consensus_analysis.py continuous 2>&1 | tee monitoring.log
```

## Future Enhancements

### Planned Features
- **Adaptive Timing**: Automatically adjust capture frequency based on performance
- **Real-time Dashboard**: Web-based monitoring interface
- **Alert System**: Notifications for low confidence or errors
- **Machine Learning**: Improve OCR accuracy with training data
- **Multi-threading**: Parallel processing for faster iterations

### Performance Improvements
- **Caching**: Cache web automation state between iterations
- **Optimized OCR**: Use GPU acceleration for faster processing
- **Smart Sampling**: Intelligent image selection for consensus
- **Predictive Analysis**: Forecast optimal capture timing

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the performance report for insights
3. Run the test script to verify functionality
4. Check system logs for detailed error information

---

**Note**: This system is designed for performance monitoring and optimization. The 60-second duration provides sufficient data for analysis while the 5-second intervals ensure timely capture of game state changes.
