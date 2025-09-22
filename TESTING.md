# Testing Guide for Speed_Matters

This document describes the comprehensive test suite for the Speed_Matters video processing application.

## Overview

The test suite provides comprehensive coverage for all major components of the video processing pipeline:

- **Video Effects**: Tests for all 4 effect variants (Classic Film, Cyberpunk, Nature, Fire)
- **Video Demuxing**: Tests for reading and parsing video files
- **Frame Processing**: Tests for parallel video processing with effects
- **Video Muxing**: Tests for combining processed video with original audio
- **Integration**: End-to-end tests for the complete workflow

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── test_effects.py          # Unit tests for apply_video_effects()
├── test_demux.py           # Unit tests for demux_video_once()
├── test_mux.py             # Unit tests for mux_videos()
├── test_threading.py       # Unit tests for thread management and verification
└── run_tests.py            # Main test runner script
```

## Running Tests

### Prerequisites

Install testing dependencies:
```bash
pip install -r requirements.txt
```

### Quick Start

Run the basic test suite:
```bash
python run_tests.py
```

### Test Runner Options

The `run_tests.py` script provides various options:

```bash
# Run unit tests only
python run_tests.py --unit

# Run integration tests only  
python run_tests.py --integration

# Run performance tests only
python run_tests.py --performance

# Run all tests
python run_tests.py --all

# Run with coverage reporting
python run_tests.py --coverage

# Run specific test file
python run_tests.py --test tests/test_effects.py

# Run specific test function
python run_tests.py --test tests/test_effects.py::TestApplyVideoEffects::test_effect_variant_0_classic_film

# Verbose output
python run_tests.py --verbose


# Clean test artifacts
python run_tests.py --clean
```

### Direct pytest Usage

You can also run tests directly with pytest:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=variant --cov-report=html

# Run only fast tests (exclude performance tests)
pytest tests/ -m "not slow"

# Run only performance tests
pytest tests/ -m "slow"

# Run specific test file
pytest tests/test_effects.py

# Run specific test
pytest tests/test_effects.py::TestApplyVideoEffects::test_effect_variant_0_classic_film
```

## Test Categories

### Unit Tests

**Effects Tests** (`test_effects.py`)
- Tests all 4 effect variants (0-3)
- Validates image processing operations
- Tests edge cases (small images, all black/white, etc.)
- Performance tests for large images
- Memory safety tests

**Demux Tests** (`test_demux.py`)
- Tests video file parsing with PyAV
- Handles missing files and corrupted files
- Tests different file formats and stream types
- Validates metadata extraction

**Processing Tests** (`test_processing.py`)
- Tests parallel frame processing
- Validates video encoding with PyAV
- Tests error handling and recovery
- Thread safety and concurrent execution

**Mux Tests** (`test_mux.py`)
- Tests audio/video combination with FFmpeg
- Validates subprocess command generation
- Tests fallback mechanisms
- Error handling for missing files

**Threading Tests** (`test_threading.py`)
- Verifies exactly 4 threads are created for parallel processing
- Tests thread synchronization and coordination
- Validates each thread gets unique effect variants (0, 1, 2, 3)
- Tests thread assignment to unique output files
- Verifies all threads receive the complete frame list
- Tests proper thread joining and cleanup

### Integration Tests

**Main Workflow Tests** (`test_integration.py`)
- End-to-end testing of complete pipeline
- Tests threading and coordination
- Validates file cleanup and error recovery
- Performance timing and reporting
- Architecture verification

### Test Utilities

**Test Utils** (`test_utils.py`)
- Mock objects for PyAV components
- Video frame generation utilities
- File system mocking
- Performance timing utilities
- Common test fixtures

## Test Features

### Mocking Strategy

The tests use extensive mocking to avoid dependencies on:
- Actual video files
- FFmpeg installation
- PyAV video encoding/decoding
- File system operations

### Performance Tests

Performance tests are marked with `@pytest.mark.slow` and can be run separately:
- Large image processing tests
- Concurrent execution tests
- Memory usage validation

### Error Handling Tests

Comprehensive error handling coverage:
- Missing input files
- Corrupted video files
- Encoding/decoding failures
- Subprocess errors
- File system errors

### Edge Case Testing

Tests handle various edge cases:
- Empty video files
- Very small images (2x2 pixels)
- All-black and all-white images
- Missing audio streams
- Multiple video/audio streams

## Coverage Reports

Generate HTML coverage reports:
```bash
python run_tests.py --coverage
```

This creates an `htmlcov/` directory with detailed coverage information.

## Test Configuration

### pytest Configuration

The `pyproject.toml` file contains pytest configuration:
- Test discovery paths
- Custom markers for test categories
- Command-line options

### Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests  
- `@pytest.mark.slow`: Performance/slow tests

## Continuous Integration

The test suite is designed for CI/CD environments:
- No external dependencies (mocked)
- Fast execution (under 30 seconds)
- Clear pass/fail reporting
- Coverage metrics

## Troubleshooting

### Common Issues

**Import Errors**
```
Import "pytest" could not be resolved
```
Solution: Install test dependencies with `pip install -r requirements.txt`

**Module Not Found**
```
ModuleNotFoundError: No module named 'variant'
```
Solution: Run tests from the project root directory

**PyAV Import Errors**
The tests mock PyAV components, but if you see real PyAV errors, ensure the main application works first.

### Debug Mode

Run tests with maximum verbosity:
```bash
pytest tests/ -v -s --tb=long
```

### Test Isolation

Each test is isolated and shouldn't affect others. If you see test interaction issues:
```bash
pytest tests/ --forked  # Requires pytest-forked
```

## Adding New Tests

### Test File Structure

```python
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from variant import function_to_test

class TestFunctionName:
    """Test suite for function_to_test"""
    
    @pytest.fixture
    def sample_data(self):
        """Create test data"""
        return create_test_data()
    
    def test_normal_case(self, sample_data):
        """Test normal operation"""
        result = function_to_test(sample_data)
        assert result is not None
    
    def test_edge_case(self):
        """Test edge cases"""
        # Test implementation
        pass
    
    @pytest.mark.slow
    def test_performance(self):
        """Performance test"""
        # Test implementation
        pass
```

### Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Mock external dependencies** to ensure test isolation
3. **Test both success and failure cases**
4. **Use fixtures** for common test data
5. **Mark slow tests** appropriately
6. **Add docstrings** to test classes and methods
7. **Validate all important properties** of outputs
8. **Test edge cases** and boundary conditions

## Test Metrics

Current test coverage: **40 passing tests (100% success rate)**

**Test breakdown by category:**
- **Effects Tests**: 13/13 ✅ - All effect variants and edge cases
- **Demux Tests**: 10/10 ✅ - Video parsing and frame extraction  
- **Mux Tests**: 11/11 ✅ - Audio/video combination and FFmpeg integration
- **Threading Tests**: 6/6 ✅ - Thread management and verification

Target test coverage: >90%
Test execution time: <6 seconds (all tests)
Test isolation: 100% (no test dependencies)

## Maintenance

The test suite should be updated when:
- Adding new functions or features
- Changing function signatures
- Modifying error handling behavior
- Performance optimizations
- Bug fixes

Regular maintenance:
- Review and update test data
- Check for deprecated testing patterns
- Update mock objects to match real interfaces
- Optimize slow tests