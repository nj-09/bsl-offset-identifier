#!/usr/bin/env python3
"""
Simple script to examine EAF file contents
"""

import pympi
import sys

def check_eaf_file(eaf_path):
    print(f"📋 Analyzing EAF file: {eaf_path}")
    print("=" * 60)

    try:
        eaf = pympi.Elan.Eaf(eaf_path)

        print("🎯 Available tiers:")
        tier_names = eaf.get_tier_names()
        for i, tier_name in enumerate(tier_names, 1):
            print(f"  {i}. {tier_name}")

        print(f"\n📊 Total tiers: {len(tier_names)}")

        # Check each tier
        for tier_name in tier_names:
            print(f"\n🔍 Tier: '{tier_name}'")
            try:
                data = eaf.get_annotation_data_for_tier(tier_name)
                print(f"   📈 Total annotations: {len(data)}")

                if data:
                    print("   📝 Sample annotations:")
                    for i, (start, end, value) in enumerate(data[:3]):
                        if value:
                            print(f"      {i+1}: \"{value[:50]}{'...' if len(value) > 50 else ''}\"")

                    # Check for sign-like annotations
                    sign_like = [ann[2] for ann in data if ann[2] and len(ann[2].strip()) < 20 and ann[2].strip().isupper()]
                    if sign_like:
                        print(f"   🎯 Possible signs found: {sign_like[:10]}")

            except Exception as e:
                print(f"   ❌ Error reading tier: {e}")

        # Check media descriptors
        print(f"\n📹 Media files referenced:")
        for i, desc in enumerate(eaf.media_descriptors, 1):
            if 'MEDIA_URL' in desc:
                media_url = desc['MEDIA_URL']
                print(f"   {i}. {media_url}")
                if 'TIME_ORIGIN' in desc:
                    print(f"      ⏰ Offset: {desc['TIME_ORIGIN']}ms")

    except Exception as e:
        print(f"❌ Error loading EAF file: {e}")

if __name__ == "__main__":
    eaf_path = "CAVA_Data/EAFs/L10n.eaf"
    check_eaf_file(eaf_path)