#!/usr/bin/env python3
"""
Debug video file finding for BF01F28WDC.eaf
"""

import os

def debug_video_finding():
    filename = "BF01F28WDC.eaf"
    video_folder = "/Volumes/2TB HD/BSLC media/Conversation"

    print(f"🔍 Debugging video finding for: {filename}")
    print("=" * 50)

    # Replicate the logic from simple_viewer.py
    base_name = os.path.splitext(filename)[0]  # "BF01F28WDC"
    region_code = base_name[:2]  # "BF"

    print(f"📋 Base name: {base_name}")
    print(f"📋 Region code: {region_code}")

    try:
        number = base_name[2:4].lstrip('0') or '0'  # "01" -> "1"
        print(f"📋 Number: {number}")
    except:
        number = '1'
        print(f"📋 Number (fallback): {number}")

    patterns = [
        f"{region_code}/{region_code}{number}+2c.mp4",   # BF/BF1+2c.mp4
        f"{region_code}/{region_code}{number}c.mp4",     # BF/BF1c.mp4
    ]

    print(f"🎯 Expected patterns:")
    for pattern in patterns:
        print(f"  - {pattern}")

    print(f"🔍 Checking video files:")
    found_videos = []
    for pattern in patterns:
        video_path = os.path.join(video_folder, pattern)
        print(f"  📁 Checking: {video_path}")
        if os.path.exists(video_path):
            found_videos.append(video_path)
            print(f"    ✅ Found!")
        else:
            print(f"    ❌ Not found")

    print(f"\n📊 Summary:")
    print(f"  Found {len(found_videos)} videos:")
    for i, video in enumerate(found_videos, 1):
        print(f"    Video {i}: {video}")

    return found_videos

if __name__ == "__main__":
    debug_video_finding()