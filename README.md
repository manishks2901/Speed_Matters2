# Speed_Matters

A high-performance video processing application that applies 4 different visual effects to videos using parallel threading.

## Overview

Speed_Matters processes video files by:
1. **Demuxing** - Extracting frames from input video
2. **Processing** - Applying 4 different effects in parallel threads
3. **Muxing** - Combining processed videos with original audio
4. **Threading** - Managing parallel execution with exactly 4 threads

## Video Effects

The application creates 4 variants of your video with different effects:

- **Classic Film** (Variant 0) - Vintage sepia tone effect
- **Cyberpunk** (Variant 1) - Futuristic neon-enhanced visuals  
- **Nature** (Variant 2) - Enhanced natural colors and contrast
- **Fire** (Variant 3) - Warm, fire-inspired color grading

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Process a video
python variant.py test.mp4
```

## Testing

The project has comprehensive test coverage with **4 test categories**:

### 1. Effects Tests (`test_effects.py`)
- Tests all 4 effect variants (Classic Film, Cyberpunk, Nature, Fire)
- Validates image processing operations and edge cases

### 2. Demux Tests (`test_demux.py`) 
- Tests video file parsing and frame extraction
- Handles different file formats and error conditions

### 3. Mux Tests (`test_mux.py`)
- Tests audio/video combination with FFmpeg
- Validates subprocess operations and error handling

### 4. Threading Tests (`test_threading.py`)
- **Verifies exactly 4 threads are created** for parallel processing
- Tests thread synchronization and coordination
- Validates unique effect assignment to each thread

### Running Tests

```bash
# Run all tests
python run_tests.py --all

# Run specific test category
pytest tests/test_threading.py -v
pytest tests/test_effects.py -v
pytest tests/test_demux.py -v
pytest tests/test_mux.py -v
```

**Test Results**: 40/40 tests passing (100% success rate)

## Architecture

```
Input Video → Demux → 4 Parallel Threads → Mux → 4 Output Videos
                          ├─ Thread 1 (Classic Film)
                          ├─ Thread 2 (Cyberpunk)  
                          ├─ Thread 3 (Nature)
                          └─ Thread 4 (Fire)
```

## Technical Requirements

- **Python 3.7+**
- **PyAV** - Video processing and frame manipulation
- **NumPy** - Numerical operations for image effects
- **SciPy** - Advanced image processing functions  
- **FFmpeg** - Audio/video muxing (external dependency)

## Performance

- **Parallel Processing**: 4 simultaneous threads for maximum efficiency
- **Memory Optimized**: Efficient frame processing and memory management
- **Thread Verification**: Automated testing ensures exactly 4 threads are used

## Output

The application generates 4 output files:
- `output_variant_0.mp4` - Classic Film effect
- `output_variant_1.mp4` - Cyberpunk effect  
- `output_variant_2.mp4` - Nature effect
- `output_variant_3.mp4` - Fire effect

Each output video includes the original audio track combined with the processed video.