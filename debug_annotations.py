#!/usr/bin/env python3
"""
Debug script to check what annotations are found in EAF files
"""

import os
import pympi

def debug_eaf_file(file_path):
    """Debug annotations in a single EAF file"""
    filename = os.path.basename(file_path)
    print(f"\n🔍 Debugging: {filename}")
    print("=" * 50)

    try:
        eaf = pympi.Elan.Eaf(file_path)

        # Check dominant hand based on filename
        is_left_handed = filename.upper().endswith('_LH.EAF')
        dominant_tier = "LH-IDgloss" if is_left_handed else "RH-IDgloss"

        print(f"📋 Dominant hand: {'Left' if is_left_handed else 'Right'}")
        print(f"🎯 Target tier: {dominant_tier}")

        # Get all tier names
        all_tiers = list(eaf.get_tier_names())
        print(f"📊 Available tiers: {all_tiers}")

        if dominant_tier not in all_tiers:
            print(f"❌ Dominant tier '{dominant_tier}' not found!")
            return False

        # Get dominant tier data
        dominant_data = eaf.get_annotation_data_for_tier(dominant_tier)

        # Check all annotations
        all_annotations = []
        good_annotations = []

        for start_time, end_time, value in dominant_data:
            if value and value.strip():
                all_annotations.append(value.strip())
                if value.strip().upper() == "GOOD":
                    good_annotations.append({
                        'value': value.strip(),
                        'start': start_time,
                        'end': end_time
                    })

        print(f"📊 Total annotations: {len(all_annotations)}")
        print(f"🎯 GOOD annotations: {len(good_annotations)}")

        if len(all_annotations) >= 20 and len(good_annotations) >= 5:
            print("✅ File meets requirements!")
        else:
            print(f"❌ File doesn't meet requirements (need ≥20 total, ≥5 GOOD)")

        # Show unique annotation values
        unique_values = list(set(all_annotations))
        unique_values.sort()
        print(f"🏷️ Unique annotation values ({len(unique_values)}):")
        for i, value in enumerate(unique_values[:20]):  # Show first 20
            print(f"   {i+1:2d}. '{value}'")
        if len(unique_values) > 20:
            print(f"   ... and {len(unique_values) - 20} more")

        # Show GOOD annotations details
        if good_annotations:
            print(f"\n🎯 GOOD annotation details:")
            for i, ann in enumerate(good_annotations[:5]):
                duration = (ann['end'] - ann['start']) / 1000.0
                print(f"   {i+1}. '{ann['value']}' at {ann['start']/1000:.1f}s-{ann['end']/1000:.1f}s ({duration:.1f}s)")

        return len(all_annotations) >= 20 and len(good_annotations) >= 5

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return False

def main():
    """Debug the first few EAF files"""
    eaf_folder = "/Volumes/2TB HD/BSLC EAFs (copy)/Conversation"

    if not os.path.exists(eaf_folder):
        print(f"❌ EAF folder not found: {eaf_folder}")
        return

    print("🎯 Bad Offset Identifier Tool - Annotation Debug Tool")
    print("=" * 50)

    files_found = []
    for root, dirs, files in os.walk(eaf_folder):
        for file in files:
            if file.endswith('.eaf'):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > 100 * 1024:  # >100KB
                    files_found.append(file_path)

    print(f"📁 Found {len(files_found)} EAF files to check")

    # Debug first 3 files
    suitable_count = 0
    for i, file_path in enumerate(files_found[:3]):
        if debug_eaf_file(file_path):
            suitable_count += 1

    print(f"\n📊 Summary: {suitable_count}/3 files suitable")

if __name__ == "__main__":
    main()