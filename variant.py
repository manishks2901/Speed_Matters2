from scipy import ndimage
import av            # PyAV: Python bindings for FFmpeg (demux/encode/mux)
import numpy as np   # For frame manipulation (filtergraph stage)
import threading     # For parallel processing
import time
import os

def apply_video_effects(img, effect_variant=0):
    """Apply 25 different visual effects based on variant"""
    
    if effect_variant == 0:
        # Variant 1: Classic Film Processing (25 transformations)
        # 1. Color inversion
        img = 255 - img
        
        # 2. Brightness adjustment
        img = np.clip(img + 30, 0, 255).astype(np.uint8)
        
        # 3. Contrast enhancement
        img = np.clip((img - 128) * 1.2 + 128, 0, 255).astype(np.uint8)
        
        # 4. Sepia tone
        sepia = np.array([[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]])
        img = np.dot(img, sepia.T)
        img = np.clip(img, 0, 255).astype(np.uint8)
        
        # 5. Gamma correction
        img = np.power(img / 255.0, 0.8) * 255
        img = img.astype(np.uint8)
        
        # 6. Color channel shift
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.1, 0, 255)
        
        # 7. Saturation boost
        hsv = np.zeros_like(img, dtype=np.float32)
        hsv[:, :, 2] = np.max(img, axis=2) / 255.0
        img = np.clip(img * 1.15, 0, 255).astype(np.uint8)
        
        # 8. Film grain simulation
        noise = np.random.normal(0, 5, img.shape)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        
        # 9. Edge enhancement
        img = np.clip(img * 1.1 - 10, 0, 255).astype(np.uint8)
        
        # 10. Color temperature adjustment (warmer)
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.05, 0, 255)
        img[:, :, 2] = np.clip(img[:, :, 2] * 0.95, 0, 255)
        
        # 11. Slight blur
        img = ndimage.gaussian_filter(img, sigma=0.5)
        img = img.astype(np.uint8)
        
        # 12. Highlights compression
        bright_mask = img > 200
        img[bright_mask] = (img[bright_mask] * 0.9).astype(np.uint8)
        
        # 13. Shadows lift
        dark_mask = img < 50
        img[dark_mask] = (img[dark_mask] * 1.2).astype(np.uint8)
        
        # 14. Color grading (orange/teal)
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.1, 0, 255)
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.05, 0, 255)
        
        # 15. Midtone contrast
        mid_mask = (img > 50) & (img < 200)
        img[mid_mask] = np.clip((img[mid_mask] - 128) * 1.1 + 128, 0, 255)
        
        # 16. Chromatic aberration simulation
        img[:, :, 0] = np.roll(img[:, :, 0], 1, axis=1)
        img[:, :, 2] = np.roll(img[:, :, 2], -1, axis=1)
        
        # 17. Vintage fade
        img = img * 0.95 + 20
        
        # 18. Color balance adjustment
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.02, 0, 255)
        
        # 19. Film curve simulation
        img = np.power(img / 255.0, 0.9) * 255
        
        # 20. Texture enhancement
        img = np.clip(img * 1.03, 0, 255)
        
        # 21. Color space compression
        img = np.clip(img * 0.98 + 5, 0, 255)
        
        # 22. Lens distortion compensation
        center_y, center_x = img.shape[0] // 2, img.shape[1] // 2
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        distortion = 1 + 0.1 * (distance / max_distance)
        img = np.clip(img / distortion[:, :, np.newaxis], 0, 255)
        
        # 23. Color isolation
        img[:, :, 1] = np.clip(img[:, :, 1] * 0.98, 0, 255)
        
        # 24. Final color correction
        img = np.clip(img * 1.01, 0, 255)
        
        # 25. Vignette effect
        h, w = img.shape[:2]
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - (distance / max_distance) ** 1.5
        vignette = np.clip(vignette, 0.3, 1)
        img = (img * vignette[:, :, np.newaxis])
        
    elif effect_variant == 1:
        # Variant 2: Cyberpunk/Neon Style (25 transformations)
        # 1. Blue channel enhancement
        img[:, :, 2] = np.clip(img[:, :, 2] * 1.4, 0, 255)
        
        # 2. Red channel reduction
        img[:, :, 0] = img[:, :, 0] * 0.6
        
        # 3. Green channel adjustment
        img[:, :, 1] = img[:, :, 1] * 0.8
        
        # 4. High contrast
        img = np.clip((img - 128) * 1.6 + 128, 0, 255)
        
        # 5. Digital noise
        noise = np.random.randint(-10, 10, img.shape)
        img = np.clip(img + noise, 0, 255)
        
        # 6. Cyan tint in highlights
        bright_mask = img > 180
        img[:, :, 1][bright_mask[:, :, 1]] = np.clip(img[:, :, 1][bright_mask[:, :, 1]] * 1.2, 0, 255)
        img[:, :, 2][bright_mask[:, :, 2]] = np.clip(img[:, :, 2][bright_mask[:, :, 2]] * 1.2, 0, 255)
        
        # 7. Magenta tint in shadows
        dark_mask = img < 80
        img[:, :, 0][dark_mask[:, :, 0]] = np.clip(img[:, :, 0][dark_mask[:, :, 0]] * 1.3, 0, 255)
        img[:, :, 2][dark_mask[:, :, 2]] = np.clip(img[:, :, 2][dark_mask[:, :, 2]] * 1.2, 0, 255)
        
        # 8. Scanline effect
        img[::4, :, :] = img[::4, :, :] * 0.8
        
        # 9. Color banding
        img = (img // 16) * 16
        
        # 10. Neon glow simulation
        img = np.clip(img * 1.2, 0, 255)
        
        # 11. Digital artifact
        img[::8, ::8, :] = np.clip(img[::8, ::8, :] * 1.5, 0, 255)
        
        # 12. Blue glow in edges
        edges = ndimage.sobel(np.mean(img, axis=2))
        edges = (edges > np.percentile(edges, 90)).astype(float)
        img[:, :, 2] = np.clip(img[:, :, 2] + edges * 50, 0, 255)
        
        # 13. Saturation push
        img = np.clip(img * 1.1, 0, 255)
        
        # 14. RGB shift
        img[:, :, 0] = np.roll(img[:, :, 0], 2, axis=0)
        img[:, :, 2] = np.roll(img[:, :, 2], -2, axis=0)
        
        # 15. Pixelation effect
        h, w = img.shape[:2]
        img_small = img[::2, ::2]
        img = np.repeat(np.repeat(img_small, 2, axis=0), 2, axis=1)[:h, :w]
        
        # 16. Electric blue enhancement
        img[:, :, 2] = np.clip(img[:, :, 2] * 1.1, 0, 255)
        
        # 17. Holographic shimmer
        shimmer = np.sin(np.arange(img.shape[0])[:, np.newaxis] * 0.1) * 5
        img = np.clip(img + shimmer[:, :, np.newaxis], 0, 255)
        
        # 18. Data corruption simulation
        corrupt_mask = np.random.random(img.shape[:2]) < 0.001
        if np.any(corrupt_mask):
            for i in range(3):
                img[:, :, i][corrupt_mask] = np.random.randint(0, 255, np.sum(corrupt_mask))
        
        # 19. Circuit pattern overlay
        circuit = np.zeros_like(img[:, :, 0])
        circuit[::20, :] = 255
        circuit[:, ::20] = 255
        img = np.clip(img + circuit[:, :, np.newaxis] * 0.1, 0, 255)
        
        # 20. Neon border effect
        border_mask = np.zeros_like(img[:, :, 0])
        border_mask[:5, :] = 1
        border_mask[-5:, :] = 1
        border_mask[:, :5] = 1
        border_mask[:, -5:] = 1
        img[:, :, 2] = np.clip(img[:, :, 2] + border_mask * 100, 0, 255)
        
        # 21. Digital color grading
        img = np.clip(img * 0.95 + 15, 0, 255)
        
        # 22. Matrix-style color wash
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.05, 0, 255)
        
        # 23. Cybernetic enhancement
        img = np.clip(img * 1.02, 0, 255)
        
        # 24. Final neon adjustment
        img[:, :, 2] = np.clip(img[:, :, 2] * 1.03, 0, 255)
        
        # 25. Vignette with blue tint
        h, w = img.shape[:2]
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - (distance / max_distance) ** 1.2
        vignette = np.clip(vignette, 0.4, 1)
        img = (img * vignette[:, :, np.newaxis])
        img[:, :, 2] = np.clip(img[:, :, 2] + (1 - vignette) * 20, 0, 255)
        
    elif effect_variant == 2:
        # Variant 3: Nature/Organic Style (25 transformations)
        # 1. Green channel enhancement
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.5, 0, 255)
        
        # 2. Red channel reduction
        img[:, :, 0] = img[:, :, 0] * 0.7
        
        # 3. Blue channel reduction
        img[:, :, 2] = img[:, :, 2] * 0.7
        
        # 4. Organic blur
        img = ndimage.gaussian_filter(img, sigma=1.2)
        
        # 5. Forest lighting simulation
        img = np.clip(img * 0.9 + 10, 0, 255)
        
        # 6. Moss texture enhancement
        texture = np.random.normal(0, 3, img.shape)
        img = np.clip(img + texture, 0, 255)
        
        # 7. Leaf shadow simulation
        shadow_pattern = np.sin(np.arange(img.shape[0])[:, np.newaxis] * 0.3) * 0.1
        img = img * (1 + shadow_pattern[:, :, np.newaxis])
        
        # 8. Natural saturation
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.2, 0, 255)
        
        # 9. Bark texture overlay
        bark = np.random.random(img.shape) * 5
        img = np.clip(img + bark, 0, 255)
        
        # 10. Sunlight filtering
        sunlight = np.random.random(img.shape[:2]) < 0.1
        img[sunlight] = np.clip(img[sunlight] * 1.3, 0, 255)
        
        # 11. Organic edge softening
        img = ndimage.median_filter(img, size=2)
        
        # 12. Chlorophyll boost
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.1, 0, 255)
        
        # 13. Natural contrast
        img = np.clip((img - 128) * 0.9 + 128, 0, 255)
        
        # 14. Dappled light effect
        dapples = np.sin(np.arange(img.shape[1])[np.newaxis, :] * 0.2) * 10
        img = np.clip(img + dapples[:, :, np.newaxis], 0, 255)
        
        # 15. Earth tone adjustment
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.05, 0, 255)
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.1, 0, 255)
        
        # 16. Organic noise reduction
        img = ndimage.uniform_filter(img, size=2)
        
        # 17. Natural color grading
        img = np.clip(img * 1.05, 0, 255)
        
        # 18. Photosynthesis simulation
        green_boost = (img[:, :, 1] > img[:, :, 0]) & (img[:, :, 1] > img[:, :, 2])
        img[green_boost, 1] = np.clip(img[green_boost, 1] * 1.2, 0, 255)
        
        # 19. Natural light falloff
        img = img * 0.98 + 5
        
        # 20. Organic film grain
        grain = np.random.normal(0, 2, img.shape)
        img = np.clip(img + grain, 0, 255)
        
        # 21. Seasonal color shift
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.02, 0, 255)
        
        # 22. Natural warmth
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.03, 0, 255)
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.02, 0, 255)
        
        # 23. Humidity effect
        img = img * 0.99 + 3
        
        # 24. Growth pattern enhancement
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.01, 0, 255)
        
        # 25. Natural vignette
        h, w = img.shape[:2]
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - (distance / max_distance) ** 1.3
        vignette = np.clip(vignette, 0.5, 1)
        img = (img * vignette[:, :, np.newaxis])
        img[:, :, 1] = np.clip(img[:, :, 1] + (1 - vignette) * 10, 0, 255)
        
    elif effect_variant == 3:
        # Variant 4: Fire/Energy Style (25 transformations)
        # 1. Red channel amplification
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.6, 0, 255)
        
        # 2. Green channel reduction
        img[:, :, 1] = img[:, :, 1] * 0.6
        
        # 3. Blue channel elimination
        img[:, :, 2] = img[:, :, 2] * 0.4
        
        # 4. Fire edge enhancement
        img = np.clip(img * 1.3 - 30, 0, 255)
        
        # 5. Heat shimmer simulation
        shimmer_y = np.sin(np.arange(img.shape[1])[np.newaxis, :] * 0.5) * 2
        img = np.clip(img + shimmer_y[:, :, np.newaxis], 0, 255)
        
        # 6. Ember particle effect
        embers = np.random.random(img.shape[:2]) < 0.005
        img[embers, 0] = 255
        img[embers, 1] = np.random.randint(100, 200, np.sum(embers))
        
        # 7. Heat wave distortion
        wave = np.sin(np.arange(img.shape[0])[:, np.newaxis] * 0.8) * 5
        img = np.clip(img + wave[:, :, np.newaxis], 0, 255)
        
        # 8. Flame color grading
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.2, 0, 255)
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.1, 0, 255)
        
        # 9. Combustion enhancement
        hot_mask = img[:, :, 0] > 150
        img[:, :, 0][hot_mask] = np.clip(img[:, :, 0][hot_mask] * 1.2, 0, 255)
        
        # 10. Smoke simulation
        smoke_areas = np.random.random(img.shape[:2]) < 0.02
        img[smoke_areas] = (img[smoke_areas] * 0.7 + 50).astype(np.uint8)
        
        # 11. Orange glow
        glow_mask = (img[:, :, 0] > 100) & (img[:, :, 1] > 50)
        img[:, :, 1][glow_mask] = np.clip(img[:, :, 1][glow_mask] * 1.3, 0, 255)
        
        # 12. Heat intensity mapping
        intensity = (img[:, :, 0] + img[:, :, 1]) / 2
        img[:, :, 0] = np.clip(img[:, :, 0] + intensity * 0.1, 0, 255)
        
        # 13. Molten metal effect
        molten_mask = img[:, :, 0] > 200
        img[:, :, 1][molten_mask] = np.clip(img[:, :, 1][molten_mask] * 1.5, 0, 255)
        
        # 14. Flicker simulation
        flicker = np.random.normal(1, 0.05, img.shape)
        img = np.clip(img * flicker, 0, 255)
        
        # 15. Thermal gradient
        thermal = np.linspace(0, 20, img.shape[0])[:, np.newaxis, np.newaxis]
        img[:, :, 0] = np.clip(img[:, :, 0] + thermal[:, :, 0], 0, 255)
        
        # 16. Burn edge effect
        edges = ndimage.sobel(np.mean(img, axis=2))
        edges = (edges > np.percentile(edges, 85)).astype(float)
        img[:, :, 0] = np.clip(img[:, :, 0] + edges * 40, 0, 255)
        
        # 17. Lava flow simulation
        flow = np.sin(np.arange(img.shape[1])[np.newaxis, :] * 0.3) * 15
        img[:, :, 0] = np.clip(img[:, :, 0] + flow, 0, 255)
        
        # 18. Inferno color mapping
        img = np.clip(img * 1.1, 0, 255)
        
        # 19. Coal glow effect
        dark_areas = np.mean(img, axis=2) < 80
        img[:, :, 0][dark_areas] = np.clip(img[:, :, 0][dark_areas] * 1.4, 0, 255)
        
        # 20. Heat distortion
        distort_shift = int(np.sin(img.shape[0] * 0.1))
        if distort_shift != 0:
            img = np.roll(img, distort_shift, axis=1)
        
        # 21. Flame texture
        texture = np.random.normal(0, 8, img.shape)
        img = np.clip(img + texture, 0, 255)
        
        # 22. Solar flare effect
        flare_center = (img.shape[0] // 3, img.shape[1] // 3)
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        flare_dist = np.sqrt((x - flare_center[1])**2 + (y - flare_center[0])**2)
        flare_effect = np.exp(-flare_dist / 50) * 30
        img[:, :, 0] = np.clip(img[:, :, 0] + flare_effect, 0, 255)
        
        # 23. Plasma enhancement
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.05, 0, 255)
        
        # 24. Final fire polish
        img = np.clip(img * 1.02, 0, 255)
        
        # 25. Fire vignette
        h, w = img.shape[:2]
        
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - (distance / max_distance) ** 1.1
        vignette = np.clip(vignette, 0.4, 1)
        img = (img * vignette[:, :, np.newaxis])
        img[:, :, 0] = np.clip(img[:, :, 0] + (1 - vignette) * 30, 0, 255)
    
    return img.astype(np.uint8)

def demux_video_once(input_file):
    """Demux video once and store all frames and metadata in memory"""
    print(f"🎞️ Demuxing {input_file} once...")
    
    try:
        container = av.open(input_file)
        
        # Extract video frames and metadata
        frames = []
        video_info = None
        audio_info = None
        
        # Get video stream info
        for stream in container.streams:
            if stream.type == 'video':
                video_info = {
                    'width': stream.width,
                    'height': stream.height,
                    'rate': stream.average_rate,
                    'time_base': stream.time_base
                }
                break
        
        # Get audio stream info
        for stream in container.streams:
            if stream.type == 'audio':
                audio_info = {
                    'rate': stream.rate,
                    'channels': stream.channels,
                    'layout': stream.layout
                }
                break
        
        # Extract all video frames into memory
        print("📽️ Loading all frames into memory...")
        for frame in container.decode(video=0):
            img = frame.to_ndarray(format='rgb24')
            frames.append(img)
        
        container.close()
        
        print(f"✅ Loaded {len(frames)} frames into memory")
        return frames, video_info, audio_info
        
    except Exception as e:
        print(f"❌ Error demuxing {input_file}: {str(e)}")
        return None, None, None

def process_all_frames(all_frames, output_file, effect_variant, thread_id):
    """Process ALL frames with a specific effect variant to create a complete unique video"""
    print(f"🎬 Thread {thread_id + 1}: Processing ALL {len(all_frames)} frames with effect variant {effect_variant} -> {output_file}")
    
    try:
        # Open output container
        out_container = av.open(output_file, mode='w')
        
        # Setup video stream for output
        video_stream = out_container.add_stream('libx264', rate=30)
        video_stream.width = 640
        video_stream.height = 480
        video_stream.pix_fmt = 'yuv420p'
        
        processed_count = 0
        
        # Process ALL frames with the assigned effect variant
        for img in all_frames:
            # Apply the specific effect variant to create unique video
            processed_img = apply_video_effects(img, effect_variant)
            
            # Convert back to PyAV frame
            new_frame = av.VideoFrame.from_ndarray(processed_img, format='rgb24')
            
            # Encode the frame
            for packet in video_stream.encode(new_frame):
                out_container.mux(packet)
            
            processed_count += 1
            if processed_count % 50 == 0:  # Progress update every 50 frames
                print(f"📹 Thread {thread_id + 1} (Effect {effect_variant}): Processed {processed_count}/{len(all_frames)} frames")
        
        # Flush the encoder
        for packet in video_stream.encode():
            out_container.mux(packet)
        
        # Close container
        out_container.close()
        
        print(f"✅ Thread {thread_id + 1}: Completed full video with effect variant {effect_variant} -> {output_file}")
        
    except Exception as e:
        print(f"❌ Thread {thread_id + 1}: Error processing {output_file}: {str(e)}")

def mux_videos(processed_files, final_outputs):
    """Mux processed videos with original audio into final output files"""
    print("🔧 Starting muxing process...")
    
    import shutil
    import subprocess
    
    for i, (processed_file, final_output) in enumerate(zip(processed_files, final_outputs)):
        try:
            print(f"🎯 Adding audio to {processed_file} -> {final_output}")
            
            # Check if processed file exists
            if not os.path.exists(processed_file):
                print(f"❌ Processed file {processed_file} not found!")
                continue
            
            # Use FFmpeg to combine processed video with original audio
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output files
                '-i', processed_file,  # processed video (no audio)
                '-i', 'test.mp4',      # original video with audio
                '-c:v', 'copy',        # copy video stream from processed file
                '-c:a', 'aac',         # encode audio to AAC
                '-map', '0:v:0',       # use video from first input (processed)
                '-map', '1:a:0',       # use audio from second input (original)
                '-shortest',           # finish when shortest stream ends
                final_output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created: {final_output}")
            else:
                print(f"❌ FFmpeg error for {final_output}: {result.stderr}")
                # Fallback: just copy the processed file without audio
                shutil.copy2(processed_file, final_output)
                print(f"⚠️  Copied video without audio: {final_output}")
            
        except Exception as e:
            print(f"❌ Error processing {processed_file}: {str(e)}")

def main():
    """Main function: 1 demux → 4 threads each processing ALL frames with different effects"""
    input_file = "test.mp4"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found!")
        return
    
    print("🚀 Starting: 1 demux → 4 complete unique videos with different effects...")
    start_time = time.time()
    
    # Step 1: Demux video once and load all frames into memory
    demux_start = time.time()
    all_frames, video_info, audio_info = demux_video_once(input_file)
    
    if all_frames is None:
        print("❌ Failed to demux video!")
        return
    
    demux_time = time.time() - demux_start
    print(f"⏱️ Single demux completed in {demux_time:.2f} seconds")
    print(f"📦 Loaded {len(all_frames)} frames into memory for processing")
    
    # Define output files for 4 unique effect variants
    processed_files = ["temp_processed_1.mp4", "temp_processed_2.mp4", "temp_processed_3.mp4", "temp_processed_4.mp4"]
    final_outputs = ["out1.mp4", "out2.mp4", "out3.mp4", "out4.mp4"]
    effect_names = ["Classic Film", "Neon/Cyberpunk", "Nature/Organic", "Fire/Energy"]
    
    # Step 2: Each thread processes ALL frames with different effects
    print("🎯 Starting parallel processing: Each thread = 1 complete unique video...")
    print("📹 Effect variants:")
    for i in range(4):
        print(f"   Thread {i+1}: {effect_names[i]} style (Effect variant {i})")
    
    processing_start = time.time()
    
    # Create and start 4 threads - each processes ALL frames
    threads = []
    for i in range(4):
        thread = threading.Thread(
            target=process_all_frames,
            args=(all_frames, processed_files[i], i, i)  # Each thread gets ALL frames
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    processing_time = time.time() - processing_start
    print(f"⏱️ Parallel processing completed in {processing_time:.2f} seconds")
    
    # Step 3: Mux each processed video with original audio
    print("🔄 Starting muxing phase: Adding audio to all 4 unique videos...")
    mux_start_time = time.time()
    mux_videos(processed_files, final_outputs)
    mux_time = time.time() - mux_start_time
    print(f"⏱️ Muxing completed in {mux_time:.2f} seconds")
    
    # Verify output files were created
    print("🔍 Verifying output files...")
    for i, output in enumerate(final_outputs):
        if os.path.exists(output):
            file_size = os.path.getsize(output) / (1024 * 1024)  # Size in MB
            print(f"   ✅ {output} ({file_size:.1f} MB) - {effect_names[i]} style")
        else:
            print(f"   ❌ {output} (not found) - {effect_names[i]} style")
    
    # Clean up temporary files only if all outputs were created successfully
    all_outputs_exist = all(os.path.exists(output) for output in final_outputs)
    if all_outputs_exist:
        print("🧹 Cleaning up temporary files...")
        for temp_file in processed_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"🗑️ Removed: {temp_file}")
            except Exception as e:
                print(f"⚠️ Warning: Could not remove {temp_file}: {str(e)}")
    else:
        print("⚠️ Keeping temporary files for debugging since some outputs failed")
    
    total_time = time.time() - start_time
    print(f"\n🎉 All processing complete! Total time: {total_time:.2f} seconds")
    print(f"📊 Performance breakdown:")
    print(f"   🎞️ Single demux: {demux_time:.2f}s")
    print(f"   🎬 Parallel processing (4 full videos): {processing_time:.2f}s") 
    print(f"   🔄 Audio muxing (4 videos): {mux_time:.2f}s")
    print(f"📈 Architecture:")
    print(f"   ✅ 1 demux operation → {len(all_frames)} frames in memory")
    print(f"   ✅ 4 threads each processing ALL {len(all_frames)} frames")
    print(f"   ✅ 4 unique complete videos with different effects")
    print(f"   ✅ 4 audio muxing operations")
    print("📁 Complete unique videos created:")
    for i, output in enumerate(final_outputs):
        if os.path.exists(output):
            print(f"   ✅ {output} - {effect_names[i]} style")
        else:
            print(f"   ❌ {output} - {effect_names[i]} style (failed)")

if __name__ == "__main__":
    main()
