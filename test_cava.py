#!/usr/bin/env python3
"""
Test script for CAVA files
Download some sample files and test the Bad Offset Identifier Tool
"""

import os
import sys
import subprocess
from pathlib import Path

def test_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg is available")
            return True
        else:
            print("❌ ffmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg is not installed")
        print("Install with:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False

def test_dependencies():
    """Check if Python dependencies are available"""
    try:
        import pympi
        print("✅ pympi-ling is available")
        return True
    except ImportError:
        print("❌ pympi-ling is not installed")
        print("Install with: pip3 install -r requirements.txt")
        return False

def check_data_structure():
    """Check if CAVA_Data structure exists"""
    base_dir = os.getcwd()
    eaf_folder = os.path.join(base_dir, "CAVA_Data", "EAFs")
    video_folder = os.path.join(base_dir, "CAVA_Data", "Videos")

    print(f"\n📁 Checking data structure:")
    print(f"  EAF folder: {eaf_folder}")
    print(f"  Video folder: {video_folder}")

    if os.path.exists(eaf_folder):
        eaf_files = list(Path(eaf_folder).rglob("*.eaf"))
        print(f"  ✅ Found {len(eaf_files)} EAF files")
    else:
        print(f"  ⚠️  EAF folder not found")

    if os.path.exists(video_folder):
        mp4_files = list(Path(video_folder).rglob("*.mp4"))
        mov_files = list(Path(video_folder).rglob("*.mov"))
        total_videos = len(mp4_files) + len(mov_files)
        print(f"  ✅ Found {total_videos} video files ({len(mp4_files)} MP4, {len(mov_files)} MOV)")
    else:
        print(f"  ⚠️  Video folder not found")

    return os.path.exists(eaf_folder) and os.path.exists(video_folder)

def main():
    print("🧪 Testing Bad Offset Identifier Tool with CAVA files")
    print("=" * 60)

    # Test dependencies
    deps_ok = test_dependencies() and test_ffmpeg()

    if not deps_ok:
        print("\n❌ Dependencies not met. Please install required software.")
        return

    # Check data structure
    data_ok = check_data_structure()

    if not data_ok:
        print("\n📥 To test with CAVA files:")
        print("1. Visit https://bslcorpusproject.org/cava/")
        print("2. Download narrative EAF and video files")
        print("3. Create CAVA_Data/EAFs/ and CAVA_Data/Videos/ folders")
        print("4. Place downloaded files in respective folders")
        print("5. Run this test again")
        return

    print("\n✅ All checks passed! Ready to test with:")
    print("python3 run_bot.py")

if __name__ == "__main__":
    main()