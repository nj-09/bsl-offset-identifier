#!/usr/bin/env python3
"""
Debug the current file being processed to check video extraction
"""

import os
import tempfile
import subprocess
import pympi

def debug_current_file():
    # This should match BF02M25WDC.eaf based on the output
    file_path = "/Volumes/2TB HD/BSLC EAFs (copy)/Conversation/Belfast/BF02M25WDC.eaf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    print(f"🔍 Debugging: {filename}")
    print("=" * 50)

    # Get GOOD annotations
    eaf = pympi.Elan.Eaf(file_path)
    is_left_handed = filename.upper().endswith('_LH.EAF')
    dominant_tier = "LH-IDgloss" if is_left_handed else "RH-IDgloss"
    dominant_data = eaf.get_annotation_data_for_tier(dominant_tier)

    good_annotations = []
    for start_time, end_time, value in dominant_data:
        if value and value.strip().upper() == "GOOD":
            good_annotations.append({
                'start_time': start_time,
                'end_time': end_time,
                'value': value
            })

    print(f"📊 Found {len(good_annotations)} GOOD annotations")

    # Check video files
    def find_video_files(eaf_filename):
        base_name = os.path.splitext(eaf_filename)[0]
        region_code = base_name[:2]
        try:
            number = base_name[2:4].lstrip('0') or '0'
        except:
            number = '1'

        video_folder = "/Volumes/2TB HD/BSLC media/Conversation"
        patterns = [
            f"{region_code}/{region_code}{number}+2c.mp4",
            f"{region_code}/{region_code}{number}c.mp4",
        ]

        found_videos = []
        for pattern in patterns:
            video_path = os.path.join(video_folder, pattern)
            if os.path.exists(video_path):
                found_videos.append(video_path)

        # If we only found one video, try to find a complementary video
        if len(found_videos) == 1:
            import glob
            # Look for any other videos with similar number pattern
            search_patterns = [
                f"{region_code}/{region_code}*{number}*c.mp4",
                f"{region_code}/{region_code}{number.zfill(2)}*.mp4"
            ]
            for search_pattern in search_patterns:
                video_pattern = os.path.join(video_folder, search_pattern)
                all_matching = glob.glob(video_pattern)
                for video_path in all_matching:
                    if video_path not in found_videos and len(found_videos) < 2:
                        found_videos.append(video_path)

        return found_videos

    videos = find_video_files(filename)
    print(f"📹 Found {len(videos)} video files:")
    for i, video in enumerate(videos, 1):
        print(f"  Video {i}: {video}")

    # Test frame extraction for first annotation
    if good_annotations and videos:
        print(f"\n🎬 Testing frame extraction for first annotation...")

        annotation = good_annotations[0]
        start_time_ms = annotation['start_time']
        end_time_ms = annotation['end_time']
        duration_ms = end_time_ms - start_time_ms

        # Midpoint calculation
        percentage = 0.475
        frame_time_ms = start_time_ms + (duration_ms * percentage)
        frame_time_seconds = frame_time_ms / 1000.0

        print(f"  📋 Annotation: {start_time_ms/1000:.1f}s - {end_time_ms/1000:.1f}s")
        print(f"  📋 Frame extraction time: {frame_time_seconds:.1f}s (47.5%)")

        temp_dir = tempfile.mkdtemp()

        for vid_idx, video_path in enumerate(videos):
            frame_filename = f"test_v{vid_idx+1}_midpoint.png"
            frame_path = os.path.join(temp_dir, frame_filename)

            try:
                cmd = [
                    'ffmpeg', '-ss', str(frame_time_seconds), '-i', video_path,
                    '-vframes', '1', '-q:v', '2', '-y', frame_path
                ]
                result = subprocess.run(cmd, capture_output=True, check=True)

                if os.path.exists(frame_path):
                    file_size = os.path.getsize(frame_path)
                    print(f"  ✅ Video {vid_idx+1}: Frame extracted ({file_size} bytes)")
                else:
                    print(f"  ❌ Video {vid_idx+1}: Frame file not created")

            except subprocess.CalledProcessError as e:
                print(f"  ❌ Video {vid_idx+1}: FFmpeg error - {e}")
            except Exception as e:
                print(f"  ❌ Video {vid_idx+1}: Error - {e}")

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    debug_current_file()