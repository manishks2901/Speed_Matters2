import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call
import subprocess
import tempfile

# Add the parent directory to path so we can import variant module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from variant import mux_videos


class TestMuxVideos:
    """Test suite for the mux_videos function"""
    
    @pytest.fixture
    def sample_files(self):
        """Create sample file lists for testing"""
        processed_files = ["temp_processed_1.mp4", "temp_processed_2.mp4", "temp_processed_3.mp4"]
        final_outputs = ["out1.mp4", "out2.mp4", "out3.mp4"]
        return processed_files, final_outputs
    
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_successful_muxing(self, mock_subprocess_run, mock_exists, sample_files):
        """Test successful video muxing with audio"""
        print("🔄 Testing successful video muxing with audio...")
        processed_files, final_outputs = sample_files
        print(f"   📋 Processing {len(processed_files)} files: {processed_files}")
        
        # Mock file existence checks
        mock_exists.return_value = True
        
        # Mock successful subprocess runs
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        # Call function
        mux_videos(processed_files, final_outputs)
        print("   ✅ Mux videos function completed")
        
        # Verify file existence was checked for each processed file
        assert mock_exists.call_count == len(processed_files)
        for processed_file in processed_files:
            mock_exists.assert_any_call(processed_file)
        print(f"   ✅ File existence checked for all {len(processed_files)} files")
        
        # Verify subprocess.run was called for each file
        assert mock_subprocess_run.call_count == len(processed_files)
        print(f"   ✅ FFmpeg subprocess called {mock_subprocess_run.call_count} times")
        
        # Verify correct FFmpeg commands were generated
        for i, (processed_file, final_output) in enumerate(zip(processed_files, final_outputs)):
            expected_cmd = [
                'ffmpeg', '-y',
                '-i', processed_file,
                '-i', 'test.mp4',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                final_output
            ]
            mock_subprocess_run.assert_any_call(expected_cmd, capture_output=True, text=True)
        print(f"   ✅ FFmpeg commands validated for all outputs: {final_outputs}")
        print("🎉 Successful muxing test completed!")

    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_processed_file_not_found(self, mock_subprocess_run, mock_exists, sample_files):
        """Test handling when processed file doesn't exist"""
        print("❌ Testing processed file not found error handling...")
        processed_files, final_outputs = sample_files
        
        # First file doesn't exist, others do
        mock_exists.side_effect = [False, True, True]
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result
        
        # Call function
        mux_videos(processed_files, final_outputs)
        
        # Should skip first file, process others
        assert mock_subprocess_run.call_count == 2  # Only 2 files processed
        print(f"   ✅ Skipped missing file, processed {mock_subprocess_run.call_count} existing files")
        print("🎉 File not found test completed!")

    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    @patch('shutil.copy2')
    def test_ffmpeg_failure_fallback(self, mock_copy2, mock_subprocess_run, mock_exists, sample_files):
        """Test fallback to copying file when FFmpeg fails"""
        print("🔄 Testing FFmpeg failure fallback to file copy...")
        processed_files, final_outputs = sample_files
        
        mock_exists.return_value = True
        
        # Mock FFmpeg failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "FFmpeg error: codec not found"
        mock_subprocess_run.return_value = mock_result
        
        # Call function
        mux_videos(processed_files, final_outputs)
        
        # Should try FFmpeg for each file
        assert mock_subprocess_run.call_count == len(processed_files)
        print(f"   ✅ FFmpeg attempted for all {len(processed_files)} files")
        
        # Should fallback to copy for each failed file
        assert mock_copy2.call_count == len(processed_files)
        for processed_file, final_output in zip(processed_files, final_outputs):
            mock_copy2.assert_any_call(processed_file, final_output)
        print(f"   ✅ Fallback copy used for all {len(processed_files)} files")
        print("🎉 FFmpeg failure fallback test completed!")

    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_mixed_success_failure(self, mock_subprocess_run, mock_exists, sample_files):
        """Test mixed success and failure scenarios"""
        print("⚡ Testing mixed success and failure scenarios...")
        processed_files, final_outputs = sample_files
        
        mock_exists.return_value = True
        
        # Mock mixed results: success, failure, success
        results = [
            MagicMock(returncode=0, stderr=""),
            MagicMock(returncode=1, stderr="Encoding failed"),
            MagicMock(returncode=0, stderr="")
        ]
        mock_subprocess_run.side_effect = results
        
        with patch('shutil.copy2') as mock_copy2:
            # Call function
            mux_videos(processed_files, final_outputs)
            
            # Should try FFmpeg for all files
            assert mock_subprocess_run.call_count == len(processed_files)
            
            # Should only fallback copy for the failed one (middle file)
            assert mock_copy2.call_count == 1
            mock_copy2.assert_called_once_with(processed_files[1], final_outputs[1])
    
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_subprocess_exception(self, mock_subprocess_run, mock_exists, sample_files):
        """Test handling of subprocess exceptions"""
        processed_files, final_outputs = sample_files
        
        mock_exists.return_value = True
        
        # Mock subprocess exception
        mock_subprocess_run.side_effect = Exception("Subprocess failed")
        
        # Should not raise exception, but handle gracefully
        try:
            mux_videos(processed_files, final_outputs)
        except Exception:
            pytest.fail("mux_videos should handle subprocess exceptions gracefully")
    
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    @patch('shutil.copy2')
    def test_copy_fallback_exception(self, mock_copy2, mock_subprocess_run, mock_exists, sample_files):
        """Test handling of copy fallback exceptions"""
        processed_files, final_outputs = sample_files
        
        mock_exists.return_value = True
        
        # Mock FFmpeg failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "FFmpeg error"
        mock_subprocess_run.return_value = mock_result
        
        # Mock copy failure
        mock_copy2.side_effect = Exception("Copy failed")
        
        # Should not raise exception, but handle gracefully
        try:
            mux_videos(processed_files, final_outputs)
        except Exception:
            pytest.fail("mux_videos should handle copy exceptions gracefully")
    
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_empty_file_lists(self, mock_subprocess_run, mock_exists):
        """Test with empty file lists"""
        empty_processed = []
        empty_final = []
        
        # Should complete without errors
        mux_videos(empty_processed, empty_final)
        
        # Should not call any external functions
        mock_exists.assert_not_called()
        mock_subprocess_run.assert_not_called()
    
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_mismatched_file_lists(self, mock_subprocess_run, mock_exists):
        """Test with mismatched length file lists"""
        processed_files = ["file1.mp4", "file2.mp4", "file3.mp4"]
        final_outputs = ["out1.mp4", "out2.mp4"]  # Shorter list
        
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result
        
        # Should process only the pairs that exist (2 files)
        mux_videos(processed_files, final_outputs)
        
        # Should only process 2 files (length of shorter list)
        assert mock_subprocess_run.call_count == 2
    
    @patch('variant.print')
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_output_messages(self, mock_subprocess_run, mock_exists, mock_print, sample_files):
        """Test that appropriate messages are printed"""
        processed_files, final_outputs = sample_files
        
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result
        
        # Call function
        mux_videos(processed_files, final_outputs)
        
        # Check that print was called with expected messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        # Should have starting message
        assert any("Starting muxing process..." in msg for msg in print_calls)
        
        # Should have progress messages for each file
        for processed_file, final_output in zip(processed_files, final_outputs):
            assert any(f"Adding audio to {processed_file} -> {final_output}" in msg for msg in print_calls)
            assert any(f"Created: {final_output}" in msg for msg in print_calls)
    
    @patch('variant.print')
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_error_messages(self, mock_subprocess_run, mock_exists, mock_print, sample_files):
        """Test error messages are printed correctly"""
        processed_files, final_outputs = sample_files
        
        # First file doesn't exist, second fails FFmpeg
        mock_exists.side_effect = [False, True, True]
        
        results = [
            MagicMock(returncode=1, stderr="FFmpeg failed"),
            MagicMock(returncode=0, stderr="")
        ]
        mock_subprocess_run.side_effect = results
        
        with patch('shutil.copy2'):
            mux_videos(processed_files, final_outputs)
        
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        # Should have error message for missing file
        assert any(f"Processed file {processed_files[0]} not found!" in msg for msg in print_calls)
        
        # Should have FFmpeg error message
        assert any(f"FFmpeg error for {final_outputs[1]}: FFmpeg failed" in msg for msg in print_calls)
        
        # Should have fallback message
        assert any(f"Copied video without audio: {final_outputs[1]}" in msg for msg in print_calls)
    
    @patch('variant.os.path.exists')
    @patch('subprocess.run')
    def test_ffmpeg_command_structure(self, mock_subprocess_run, mock_exists):
        """Test that FFmpeg command is structured correctly"""
        processed_files = ["input.mp4"]
        final_outputs = ["output.mp4"]
        
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result
        
        mux_videos(processed_files, final_outputs)
        
        # Get the command that was called
        called_args = mock_subprocess_run.call_args[0][0]
        
        # Verify command structure
        assert called_args[0] == 'ffmpeg'
        assert '-y' in called_args  # Overwrite output
        assert '-i' in called_args  # Input flag
        assert 'input.mp4' in called_args  # Processed video
        assert 'test.mp4' in called_args  # Original video with audio
        assert '-c:v' in called_args and 'copy' in called_args  # Copy video
        assert '-c:a' in called_args and 'aac' in called_args  # Encode audio
        assert '-map' in called_args  # Map streams
        assert '-shortest' in called_args  # Stop at shortest stream
        assert 'output.mp4' in called_args  # Final output