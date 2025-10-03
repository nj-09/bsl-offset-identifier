#!/usr/bin/env python3
"""
Quick download script for CAVA narrative files
Usage: python3 download_cava_files.py
"""

import os
import urllib.request
import urllib.parse

def download_file(url, filename, folder):
    """Download a file to the specified folder"""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    try:
        print(f"📥 Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def main():
    # Base folders
    eaf_folder = "/Users/nj/Projects/BadOffsetIdentifier/CAVA_Data/EAFs"
    video_folder = "/Users/nj/Projects/BadOffsetIdentifier/CAVA_Data/Videos"

    # Example URLs - replace these with actual CAVA URLs
    files_to_download = [
        # Format: (url, filename, folder)
        # ("https://example.ucl.ac.uk/BF01F28n.eaf", "BF01F28n.eaf", eaf_folder),
        # ("https://example.ucl.ac.uk/BF01F28n.mp4", "BF01F28n.mp4", video_folder),
    ]

    if not files_to_download:
        print("📋 No download URLs configured yet.")
        print("To use this script:")
        print("1. Find narrative file URLs on CAVA")
        print("2. Add them to the files_to_download list")
        print("3. Run the script again")
        return

    print("🚀 Starting CAVA narrative downloads...")

    success_count = 0
    for url, filename, folder in files_to_download:
        if download_file(url, filename, folder):
            success_count += 1

    print(f"\n🎉 Downloaded {success_count}/{len(files_to_download)} files successfully!")

    if success_count > 0:
        print("\n✅ Ready to test Bad Offset Identifier Tool:")
        print("   python3 run_bot.py")

if __name__ == "__main__":
    main()