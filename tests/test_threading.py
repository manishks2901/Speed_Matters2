"""
Tests for thread management and verification in variant.py
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import threading
import os
import sys

# Add parent directory to path to import variant
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import variant


class TestThreadManagement(unittest.TestCase):
    """Test thread creation and management in the main function"""

    @patch('variant.os.path.exists')
    @patch('variant.demux_video_once')
    @patch('variant.threading.Thread')
    @patch('variant.mux_videos')
    @patch('variant.os.path.getsize')
    @patch('variant.time.time')
    def test_exactly_four_threads_created(self, mock_time, mock_getsize, mock_mux_videos, 
                                        mock_thread_class, mock_demux, mock_exists):
        """Test that exactly 4 threads are created for processing"""
        print("🧵 Testing exactly 4 threads are created...")
        # Mock video data
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(10)]
        video_info = {'width': 640, 'height': 480, 'rate': 30}
        audio_info = {'channels': 2, 'layout': 'stereo', 'rate': 44100}
        
        # Mock input file exists
        mock_exists.return_value = True
        
        # Mock successful demuxing
        mock_demux.return_value = (frames, video_info, audio_info)
        
        # Mock time progression with enough values for the entire execution
        mock_time.return_value = 1.0  # Just return constant time
        
        # Mock file size
        mock_getsize.return_value = 1024 * 1024  # 1 MB
        
        # Track thread creation
        mock_thread_instances = []
        def create_mock_thread(*args, **kwargs):
            mock_thread = MagicMock()
            mock_thread_instances.append(mock_thread)
            return mock_thread
        
        mock_thread_class.side_effect = create_mock_thread
        
        # Call main function
        variant.main()
        
        # Verify exactly 4 threads were created
        self.assertEqual(mock_thread_class.call_count, 4, 
                        "Expected exactly 4 threads to be created")
        print(f"   ✅ Verified exactly {mock_thread_class.call_count} threads created")
        
        # Verify all 4 thread instances were started
        for i, thread_instance in enumerate(mock_thread_instances):
            thread_instance.start.assert_called_once()
            thread_instance.join.assert_called_once()
        print("   ✅ All threads started and joined correctly")
        
        # Verify thread creation arguments
        thread_calls = mock_thread_class.call_args_list
        for i, call in enumerate(thread_calls):
            args, kwargs = call
            
            # Check that target function is process_all_frames
            self.assertEqual(kwargs['target'], variant.process_all_frames)
            
            # Check that args contain the correct parameters
            call_args = kwargs['args']
            self.assertEqual(call_args[0], frames)  # all_frames
            self.assertEqual(call_args[1], f"temp_processed_{i+1}.mp4")  # output_file
            self.assertEqual(call_args[2], i)  # effect_variant (0, 1, 2, 3)
            self.assertEqual(call_args[3], i)  # thread_id (0, 1, 2, 3)
        print("   ✅ Thread arguments validated for all 4 variants")

    @patch('variant.os.path.exists')
    @patch('variant.demux_video_once')
    @patch('variant.threading.Thread')
    @patch('variant.mux_videos')
    @patch('variant.os.path.getsize')
    @patch('variant.time.time')
    def test_thread_effect_variants_assignment(self, mock_time, mock_getsize, mock_mux_videos,
                                             mock_thread_class, mock_demux, mock_exists):
        """Test that each thread gets assigned a different effect variant"""
        print("🧵 Testing unique effect variant assignment to threads...")
        # Mock video data
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(5)]
        video_info = {'width': 640, 'height': 480, 'rate': 30}
        audio_info = {'channels': 2, 'layout': 'stereo', 'rate': 44100}
        
        # Setup mocks
        mock_exists.return_value = True
        mock_demux.return_value = (frames, video_info, audio_info)
        mock_time.return_value = 1.0  # Just return constant time
        mock_getsize.return_value = 1024 * 1024
        
        # Track thread creation
        mock_thread_instances = [MagicMock() for _ in range(4)]
        mock_thread_class.side_effect = mock_thread_instances
        
        # Call main function
        variant.main()
        
        # Verify each thread gets a unique effect variant (0, 1, 2, 3)
        thread_calls = mock_thread_class.call_args_list
        effect_variants = []
        
        for call in thread_calls:
            args, kwargs = call
            call_args = kwargs['args']
            effect_variant = call_args[2]  # effect_variant parameter
            effect_variants.append(effect_variant)
        
        # Should have exactly 4 different effect variants: [0, 1, 2, 3]
        self.assertEqual(sorted(effect_variants), [0, 1, 2, 3],
                        "Each thread should get a unique effect variant from 0 to 3")
        print(f"   ✅ Verified unique effect variants assigned: {sorted(effect_variants)}")

    @patch('variant.os.path.exists')
    @patch('variant.demux_video_once')
    @patch('variant.threading.Thread')
    @patch('variant.mux_videos')
    @patch('variant.os.path.getsize')
    @patch('variant.time.time')
    def test_thread_output_files_assignment(self, mock_time, mock_getsize, mock_mux_videos,
                                          mock_thread_class, mock_demux, mock_exists):
        """Test that each thread gets assigned a unique output file"""
        # Mock video data
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(5)]
        video_info = {'width': 640, 'height': 480, 'rate': 30}
        audio_info = {'channels': 2, 'layout': 'stereo', 'rate': 44100}
        
        # Setup mocks
        mock_exists.return_value = True
        mock_demux.return_value = (frames, video_info, audio_info)
        mock_time.return_value = 1.0  # Just return constant time
        mock_getsize.return_value = 1024 * 1024
        
        # Track thread creation
        mock_thread_instances = [MagicMock() for _ in range(4)]
        mock_thread_class.side_effect = mock_thread_instances
        
        # Call main function
        variant.main()
        
        # Verify each thread gets a unique output file
        thread_calls = mock_thread_class.call_args_list
        output_files = []
        
        for call in thread_calls:
            args, kwargs = call
            call_args = kwargs['args']
            output_file = call_args[1]  # output_file parameter
            output_files.append(output_file)
        
        expected_files = ["temp_processed_1.mp4", "temp_processed_2.mp4", 
                         "temp_processed_3.mp4", "temp_processed_4.mp4"]
        
        self.assertEqual(sorted(output_files), sorted(expected_files),
                        "Each thread should get a unique output file")

    @patch('variant.os.path.exists')
    @patch('variant.demux_video_once')
    @patch('variant.threading.Thread')
    @patch('variant.mux_videos')
    @patch('variant.os.path.getsize')
    @patch('variant.time.time')
    def test_all_threads_get_same_frames(self, mock_time, mock_getsize, mock_mux_videos,
                                       mock_thread_class, mock_demux, mock_exists):
        """Test that all threads receive the same complete frame list"""
        # Mock video data
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(8)]
        video_info = {'width': 640, 'height': 480, 'rate': 30}
        audio_info = {'channels': 2, 'layout': 'stereo', 'rate': 44100}
        
        # Setup mocks
        mock_exists.return_value = True
        mock_demux.return_value = (frames, video_info, audio_info)
        mock_time.return_value = 1.0  # Just return constant time
        mock_getsize.return_value = 1024 * 1024
        
        # Track thread creation
        mock_thread_instances = [MagicMock() for _ in range(4)]
        mock_thread_class.side_effect = mock_thread_instances
        
        # Call main function
        variant.main()
        
        # Verify all threads get the same complete frame list
        thread_calls = mock_thread_class.call_args_list
        
        for i, call in enumerate(thread_calls):
            args, kwargs = call
            call_args = kwargs['args']
            thread_frames = call_args[0]  # all_frames parameter
            
            # Each thread should get the complete frame list
            self.assertEqual(len(thread_frames), len(frames),
                           f"Thread {i+1} should receive all {len(frames)} frames")
            
            # Verify it's the same frame list (by checking if it's the same object reference)
            self.assertIs(thread_frames, frames,
                         f"Thread {i+1} should receive the exact same frame list object")

    @patch('variant.os.path.exists')
    @patch('variant.demux_video_once')
    @patch('variant.threading.Thread')
    @patch('variant.mux_videos')
    @patch('variant.os.path.getsize')
    @patch('variant.time.time')
    def test_thread_join_called_for_all_threads(self, mock_time, mock_getsize, mock_mux_videos,
                                              mock_thread_class, mock_demux, mock_exists):
        """Test that join() is called on all 4 threads to wait for completion"""
        # Mock video data
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(3)]
        video_info = {'width': 640, 'height': 480, 'rate': 30}
        audio_info = {'channels': 2, 'layout': 'stereo', 'rate': 44100}
        
        # Setup mocks
        mock_exists.return_value = True
        mock_demux.return_value = (frames, video_info, audio_info)
        mock_time.return_value = 1.0  # Just return constant time
        mock_getsize.return_value = 1024 * 1024
        
        # Track thread creation and method calls
        mock_thread_instances = []
        for i in range(4):
            mock_thread = MagicMock()
            mock_thread_instances.append(mock_thread)
        
        mock_thread_class.side_effect = mock_thread_instances
        
        # Call main function
        variant.main()
        
        # Verify start() was called on all threads
        for i, thread_instance in enumerate(mock_thread_instances):
            thread_instance.start.assert_called_once()
            
        # Verify join() was called on all threads (waiting for completion)
        for i, thread_instance in enumerate(mock_thread_instances):
            thread_instance.join.assert_called_once()
        
        # Verify the order: all start() calls before any join() calls
        # (This is important for parallel execution)
        all_calls = []
        for i, thread_instance in enumerate(mock_thread_instances):
            all_calls.extend([
                (f"thread_{i}_start", thread_instance.start.call_count > 0),
                (f"thread_{i}_join", thread_instance.join.call_count > 0)
            ])
        
        # Both start and join should have been called for each thread
        for call_name, was_called in all_calls:
            self.assertTrue(was_called, f"{call_name} should have been called")

    @patch('variant.os.path.exists')
    @patch('variant.demux_video_once') 
    @patch('variant.threading.Thread')
    @patch('variant.mux_videos')
    @patch('variant.os.path.getsize')
    @patch('variant.time.time')
    def test_thread_count_verification(self, mock_time, mock_getsize, mock_mux_videos,
                                     mock_thread_class, mock_demux, mock_exists):
        """Test specifically that exactly 4 threads are created (user requirement)"""
        print("🧵 Testing EXACT 4-thread count verification (USER REQUIREMENT)...")
        # Mock video data
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8) for _ in range(6)]
        video_info = {'width': 640, 'height': 480, 'rate': 30}
        audio_info = {'channels': 2, 'layout': 'stereo', 'rate': 44100}
        
        # Setup mocks
        mock_exists.return_value = True
        mock_demux.return_value = (frames, video_info, audio_info)
        mock_time.return_value = 1.0
        mock_getsize.return_value = 1024 * 1024
        
        # Counter to track thread creation
        thread_creation_count = 0
        created_threads = []
        
        def count_thread_creation(*args, **kwargs):
            nonlocal thread_creation_count
            thread_creation_count += 1
            mock_thread = MagicMock()
            created_threads.append(mock_thread)
            return mock_thread
        
        mock_thread_class.side_effect = count_thread_creation
        
        # Call main function
        variant.main()
        
        # CRITICAL TEST: Verify exactly 4 threads were created
        self.assertEqual(thread_creation_count, 4, 
                        f"Expected exactly 4 threads, but {thread_creation_count} were created")
        print(f"   ✅ Thread creation count verified: {thread_creation_count}/4")
        
        # Additional verification: ensure threading.Thread was called exactly 4 times
        self.assertEqual(mock_thread_class.call_count, 4,
                        f"threading.Thread() should be called exactly 4 times")
        print(f"   ✅ Threading.Thread call count verified: {mock_thread_class.call_count}/4")
        
        # Verify we have 4 distinct thread objects
        self.assertEqual(len(created_threads), 4,
                        f"Should have 4 distinct thread objects")
        print(f"   ✅ Distinct thread objects verified: {len(created_threads)}/4")
        
        # Verify each thread was started and joined
        for i, thread in enumerate(created_threads):
            thread.start.assert_called_once()
            thread.join.assert_called_once()
        print("   ✅ All threads started and joined correctly")
            
        print(f"🎯 VERIFIED: Exactly {thread_creation_count} threads were created as required!")


if __name__ == '__main__':
    unittest.main()