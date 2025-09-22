import pytest
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import tempfile

# Add the parent directory to path so we can import variant module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from variant import demux_video_once


class TestDemuxVideoOnce:
    """Test suite for the demux_video_once function"""
    
    @pytest.fixture
    def mock_av_container(self):
        """Create a mock PyAV container"""
        print("🔧 Creating mock AV container...")
        mock_container = MagicMock()
        
        # Mock video stream
        mock_video_stream = MagicMock()
        mock_video_stream.type = 'video'
        mock_video_stream.width = 640
        mock_video_stream.height = 480
        mock_video_stream.average_rate = 30
        mock_video_stream.time_base = MagicMock()
        
        # Mock audio stream
        mock_audio_stream = MagicMock()
        mock_audio_stream.type = 'audio'
        mock_audio_stream.rate = 44100
        mock_audio_stream.channels = 2
        mock_audio_stream.layout = 'stereo'
        
        # Mock other stream type
        mock_other_stream = MagicMock()
        mock_other_stream.type = 'data'
        
        mock_container.streams = [mock_video_stream, mock_audio_stream, mock_other_stream]
        
        # Mock frames
        mock_frame1 = MagicMock()
        mock_frame1.to_ndarray.return_value = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        
        mock_frame2 = MagicMock()
        mock_frame2.to_ndarray.return_value = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        
        mock_container.decode.return_value = [mock_frame1, mock_frame2]
        print("   ✅ Mock container created with video, audio, and data streams")
        
        return mock_container
    
    @patch('variant.av.open')
    def test_successful_demux(self, mock_av_open, mock_av_container):
        """Test successful video demuxing"""
        print("🎬 Testing successful video demuxing...")
        mock_av_open.return_value = mock_av_container
        
        frames, video_info, audio_info = demux_video_once("test_video.mp4")
        print(f"   ✅ Extracted {len(frames)} frames from video")
        
        # Check that av.open was called correctly
        mock_av_open.assert_called_once_with("test_video.mp4")
        print("   ✅ av.open called with correct filename")
        
        # Check that frames were extracted
        assert frames is not None
        assert len(frames) == 2
        assert all(isinstance(frame, np.ndarray) for frame in frames)
        assert all(frame.shape == (480, 640, 3) for frame in frames)
        assert all(frame.dtype == np.uint8 for frame in frames)
        print(f"   ✅ Frame validation passed: {frames[0].shape} dtype={frames[0].dtype}")
        
        # Check video info
        assert video_info is not None
        assert video_info['width'] == 640
        assert video_info['height'] == 480
        assert video_info['rate'] == 30
        print(f"   ✅ Video info: {video_info['width']}x{video_info['height']} @ {video_info['rate']}fps")
        
        # Check audio info
        assert audio_info is not None
        assert audio_info['rate'] == 44100
        assert audio_info['channels'] == 2
        assert audio_info['layout'] == 'stereo'
        print(f"   ✅ Audio info: {audio_info['channels']}ch @ {audio_info['rate']}Hz ({audio_info['layout']})")
        
        # Check container was closed
        mock_av_container.close.assert_called_once()
        print("   ✅ Container properly closed")
        print("🎉 Successful demux test completed!")
    
    @patch('variant.av.open')
    def test_video_only_file(self, mock_av_open):
        """Test demuxing a video file with no audio stream"""
        print("🎬 Testing video-only file demuxing...")
        mock_container = MagicMock()
        
        # Only video stream, no audio
        mock_video_stream = MagicMock()
        mock_video_stream.type = 'video'
        mock_video_stream.width = 1920
        mock_video_stream.height = 1080
        mock_video_stream.average_rate = 24
        mock_video_stream.time_base = MagicMock()
        
        mock_container.streams = [mock_video_stream]
        print("   🔧 Created container with video stream only (1920x1080 @ 24fps)")
        
        # Mock frames
        mock_frame = MagicMock()
        mock_frame.to_ndarray.return_value = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        mock_container.decode.return_value = [mock_frame]
        
        mock_av_open.return_value = mock_container
        
        frames, video_info, audio_info = demux_video_once("video_only.mp4")
        
        # Check results
        assert frames is not None
        assert len(frames) == 1
        assert video_info is not None
        assert video_info['width'] == 1920
        assert video_info['height'] == 1080
        assert audio_info is None  # No audio stream
        
        print(f"   ✅ Successfully processed video-only file: {len(frames)} frame(s)")
        print(f"   ✅ Video info correct: {video_info['width']}x{video_info['height']}")
        print("   ✅ Audio info correctly None (no audio stream)")
        print("🎉 Video-only test completed!")
    
    @patch('variant.av.open')
    def test_audio_only_file(self, mock_av_open):
        """Test demuxing an audio-only file"""
        print("🎵 Testing audio-only file demuxing...")
        mock_container = MagicMock()
        
        # Only audio stream, no video
        mock_audio_stream = MagicMock()
        mock_audio_stream.type = 'audio'
        mock_audio_stream.rate = 48000
        mock_audio_stream.channels = 6
        mock_audio_stream.layout = '5.1'
        
        mock_container.streams = [mock_audio_stream]
        mock_container.decode.return_value = []  # No video frames
        print("   🔧 Created container with audio stream only (6ch @ 48kHz 5.1)")
        
        mock_av_open.return_value = mock_container
        
        frames, video_info, audio_info = demux_video_once("audio_only.mp3")
        
        # Check results
        assert frames is not None
        assert len(frames) == 0  # No video frames
        assert video_info is None  # No video stream
        assert audio_info is not None
        assert audio_info['rate'] == 48000
        assert audio_info['channels'] == 6
        
        print(f"   ✅ Successfully processed audio-only file: {len(frames)} frame(s)")
        print("   ✅ Video info correctly None (no video stream)")
        print(f"   ✅ Audio info correct: {audio_info['channels']}ch @ {audio_info['rate']}Hz")
        print("🎉 Audio-only test completed!")
    
    @patch('variant.av.open')
    def test_file_not_found(self, mock_av_open):
        """Test handling of non-existent file"""
        print("❌ Testing file not found error handling...")
        mock_av_open.side_effect = FileNotFoundError("File not found")
        
        frames, video_info, audio_info = demux_video_once("nonexistent.mp4")
        
        # Should return None values for all
        assert frames is None
        assert video_info is None
        assert audio_info is None
        
        print("   ✅ FileNotFoundError handled correctly - all returns are None")
        print("🎉 File not found test completed!")
    
    @patch('variant.av.open')
    def test_corrupted_file(self, mock_av_open):
        """Test handling of corrupted video file"""
        print("💥 Testing corrupted file error handling...")
        mock_av_open.side_effect = Exception("Corrupted file")
        
        frames, video_info, audio_info = demux_video_once("corrupted.mp4")
        
        # Should return None values for all
        assert frames is None
        assert video_info is None
        assert audio_info is None
        
        print("   ✅ Corruption error handled correctly - all returns are None")
        print("🎉 Corrupted file test completed!")
    
    @patch('variant.av.open')
    def test_decode_error(self, mock_av_open, mock_av_container):
        """Test handling of decoding errors"""
        print("⚠️ Testing decode error handling...")
        mock_av_container.decode.side_effect = Exception("Decode error")
        mock_av_open.return_value = mock_av_container
        
        frames, video_info, audio_info = demux_video_once("decode_error.mp4")
        
        # Should return None values for all
        assert frames is None
        assert video_info is None
        assert audio_info is None
        
        print("   ✅ Decode error handled correctly - all returns are None")
        print("🎉 Decode error test completed!")
        
        # Container close may or may not be called depending on when the exception occurs
    
    @patch('variant.av.open')
    def test_empty_video_file(self, mock_av_open):
        """Test handling of empty video file (no streams)"""
        print("📭 Testing empty video file (no streams)...")
        mock_container = MagicMock()
        mock_container.streams = []  # No streams
        mock_container.decode.return_value = []
        mock_av_open.return_value = mock_container
        print("   🔧 Created container with no streams")
        
        frames, video_info, audio_info = demux_video_once("empty.mp4")
        
        # Should have empty frames list but not None
        assert frames is not None
        assert len(frames) == 0
        assert video_info is None
        assert audio_info is None
        
        print(f"   ✅ Empty file handled correctly: {len(frames)} frames")
        print("   ✅ Video and audio info correctly None")
        print("🎉 Empty file test completed!")
    
    @patch('variant.av.open')
    def test_multiple_video_streams(self, mock_av_open):
        """Test file with multiple video streams (should use first one)"""
        print("🎬🎬 Testing multiple video streams (should use first)...")
        mock_container = MagicMock()
        
        # Two video streams
        mock_video_stream1 = MagicMock()
        mock_video_stream1.type = 'video'
        mock_video_stream1.width = 1280
        mock_video_stream1.height = 720
        mock_video_stream1.average_rate = 30
        mock_video_stream1.time_base = MagicMock()
        
        mock_video_stream2 = MagicMock()
        mock_video_stream2.type = 'video'
        mock_video_stream2.width = 640
        mock_video_stream2.height = 480
        mock_video_stream2.average_rate = 15
        mock_video_stream2.time_base = MagicMock()
        
        mock_container.streams = [mock_video_stream1, mock_video_stream2]
        print("   🔧 Created container with 2 video streams:")
        print("      Stream 1: 1280x720 @ 30fps")
        print("      Stream 2: 640x480 @ 15fps")
        
        mock_frame = MagicMock()
        mock_frame.to_ndarray.return_value = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
        mock_container.decode.return_value = [mock_frame]
        
        mock_av_open.return_value = mock_container
        
        frames, video_info, audio_info = demux_video_once("multi_video.mp4")
        
        # Should use info from first video stream
        assert video_info is not None
        assert video_info['width'] == 1280  # From first stream
        assert video_info['height'] == 720
        assert video_info['rate'] == 30
        
        print(f"   ✅ Used first video stream: {video_info['width']}x{video_info['height']} @ {video_info['rate']}fps")
        print("🎉 Multiple video streams test completed!")
    
    @patch('variant.av.open')
    def test_multiple_audio_streams(self, mock_av_open):
        """Test file with multiple audio streams (should use first one)"""
        print("🎵🎵 Testing multiple audio streams (should use first)...")
        mock_container = MagicMock()
        
        # Video stream
        mock_video_stream = MagicMock()
        mock_video_stream.type = 'video'
        mock_video_stream.width = 640
        mock_video_stream.height = 480
        mock_video_stream.average_rate = 30
        mock_video_stream.time_base = MagicMock()
        
        # Two audio streams
        mock_audio_stream1 = MagicMock()
        mock_audio_stream1.type = 'audio'
        mock_audio_stream1.rate = 44100
        mock_audio_stream1.channels = 2
        mock_audio_stream1.layout = 'stereo'
        
        mock_audio_stream2 = MagicMock()
        mock_audio_stream2.type = 'audio'
        mock_audio_stream2.rate = 48000
        mock_audio_stream2.channels = 6
        mock_audio_stream2.layout = '5.1'
        
        mock_container.streams = [mock_video_stream, mock_audio_stream1, mock_audio_stream2]
        print("   🔧 Created container with 1 video + 2 audio streams:")
        print("      Audio 1: 2ch @ 44.1kHz stereo")
        print("      Audio 2: 6ch @ 48kHz 5.1")
        
        mock_frame = MagicMock()
        mock_frame.to_ndarray.return_value = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        mock_container.decode.return_value = [mock_frame]
        
        mock_av_open.return_value = mock_container
        
        frames, video_info, audio_info = demux_video_once("multi_audio.mp4")
        
        # Should use info from first audio stream
        assert audio_info is not None
        assert audio_info['rate'] == 44100  # From first stream
        assert audio_info['channels'] == 2
        assert audio_info['layout'] == 'stereo'
        
        print(f"   ✅ Used first audio stream: {audio_info['channels']}ch @ {audio_info['rate']}Hz ({audio_info['layout']})")
        print("🎉 Multiple audio streams test completed!")
    
    @patch('variant.print')
    @patch('variant.av.open')
    def test_output_messages(self, mock_av_open, mock_print, mock_av_container):
        """Test that appropriate messages are printed"""
        print("📝 Testing output messages from demux function...")
        mock_av_open.return_value = mock_av_container
        
        frames, _, _ = demux_video_once("test.mp4")
        
        # Check that print was called with expected messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        print(f"   📋 Function made {len(print_calls)} print calls")
        
        assert any("Demuxing test.mp4 once..." in msg for msg in print_calls)
        print("   ✅ Found 'Demuxing...' message")
        
        assert any("Loading all frames into memory..." in msg for msg in print_calls)
        print("   ✅ Found 'Loading all frames...' message")
        
        assert any("Loaded 2 frames into memory" in msg for msg in print_calls)
        print("   ✅ Found 'Loaded X frames...' message")
        
        print("🎉 Output messages test completed!")