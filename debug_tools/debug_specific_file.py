#!/usr/bin/env python3
"""
Debug specific file BF01F28WDC.eaf to check GOOD annotations and timing
"""

import os
import pympi

def debug_specific_file():
    file_path = "/Volumes/2TB HD/BSLC EAFs (copy)/Conversation/Belfast/BF01F28WDC.eaf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print("🔍 Debugging BF01F28WDC.eaf")
    print("=" * 50)

    try:
        eaf = pympi.Elan.Eaf(file_path)

        # Check dominant hand (should be right hand for this file)
        filename = "BF01F28WDC.eaf"
        is_left_handed = filename.upper().endswith('_LH.EAF')
        dominant_tier = "LH-IDgloss" if is_left_handed else "RH-IDgloss"

        print(f"📋 Filename: {filename}")
        print(f"📋 Dominant hand: {'Left' if is_left_handed else 'Right'}")
        print(f"🎯 Target tier: {dominant_tier}")

        # Get dominant tier data
        dominant_data = eaf.get_annotation_data_for_tier(dominant_tier)

        # Find all GOOD annotations with detailed timing
        good_annotations = []
        for start_time, end_time, value in dominant_data:
            if value and value.strip().upper() == "GOOD":
                duration_ms = end_time - start_time
                midpoint_ms = start_time + (duration_ms * 0.475)  # 47.5%

                good_annotations.append({
                    'value': value.strip(),
                    'start_ms': start_time,
                    'end_ms': end_time,
                    'duration_ms': duration_ms,
                    'start_s': start_time / 1000.0,
                    'end_s': end_time / 1000.0,
                    'duration_s': duration_ms / 1000.0,
                    'midpoint_s': midpoint_ms / 1000.0
                })

        print(f"🎯 Found {len(good_annotations)} GOOD annotations:")
        print()

        for i, ann in enumerate(good_annotations, 1):
            print(f"Annotation {i}:")
            print(f"  Value: '{ann['value']}'")
            print(f"  Time: {ann['start_s']:.1f}s - {ann['end_s']:.1f}s (duration: {ann['duration_s']:.1f}s)")
            print(f"  Frame extracted at: {ann['midpoint_s']:.1f}s (47.5% midpoint)")
            print()

        # Check if corresponding video files exist
        print("📹 Checking video files:")
        video_folder = "/Volumes/2TB HD/BSLC media/Conversation"

        # For BF01F28WDC.eaf, we expect BF/BF01+2c.mp4 and BF/BF01c.mp4
        base_name = "BF01F28WDC"
        region_code = base_name[:2]  # "BF"
        number = base_name[2:4].lstrip('0') or '0'  # "01" -> "1"

        video_patterns = [
            f"{region_code}/{region_code}{number}+2c.mp4",   # BF/BF1+2c.mp4
            f"{region_code}/{region_code}{number}c.mp4",     # BF/BF1c.mp4
        ]

        found_videos = []
        for pattern in video_patterns:
            video_path = os.path.join(video_folder, pattern)
            if os.path.exists(video_path):
                found_videos.append(video_path)
                print(f"  ✅ Found: {pattern}")
            else:
                print(f"  ❌ Missing: {pattern}")

        if len(found_videos) < 2:
            print(f"⚠️  Warning: Only found {len(found_videos)} video files, expected 2")

        return good_annotations, found_videos

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None, None

if __name__ == "__main__":
    debug_specific_file()