#!/usr/bin/env python3
"""
Collect all individual decision CSV files from Downloads folder
and merge them into one master decisions.csv file
"""

import os
import csv
import glob
from datetime import datetime
from pathlib import Path

def collect_decisions():
    """Collect decision files from Downloads and merge into master CSV"""

    # Common Downloads folder locations
    downloads_folders = [
        os.path.expanduser("~/Downloads"),
        os.path.join(os.path.expanduser("~"), "Downloads")
    ]

    # Find Downloads folder
    downloads_folder = None
    for folder in downloads_folders:
        if os.path.exists(folder):
            downloads_folder = folder
            break

    if not downloads_folder:
        print("❌ Could not find Downloads folder")
        return

    print(f"🔍 Searching in: {downloads_folder}")

    # Find all decision CSV files
    decision_files = glob.glob(os.path.join(downloads_folder, "decision_*.csv"))

    if not decision_files:
        print("📭 No decision files found in Downloads folder")
        print("   Files should be named like: decision_accept_BF01F28WDC.eaf.csv")
        return

    print(f"📊 Found {len(decision_files)} decision files")

    # Collect all decisions
    all_decisions = []
    processed_files = set()

    for file_path in sorted(decision_files):
        filename = os.path.basename(file_path)
        print(f"  📁 Processing: {filename}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    # Parse CSV line
                    parts = content.split(',')
                    if len(parts) >= 3:
                        eaf_filename = parts[0]
                        decision = parts[1]
                        timestamp = parts[2]
                        notes = parts[3] if len(parts) > 3 else ''

                        # Avoid duplicates (keep latest decision for same file)
                        if eaf_filename not in processed_files:
                            all_decisions.append({
                                'filename': eaf_filename,
                                'decision': decision,
                                'timestamp': timestamp,
                                'notes': notes
                            })
                            processed_files.add(eaf_filename)
                            print(f"    ✅ {eaf_filename} -> {decision}")
                        else:
                            print(f"    ⏭️  {eaf_filename} (duplicate, skipped)")
        except Exception as e:
            print(f"    ❌ Error reading {filename}: {e}")

    if not all_decisions:
        print("❌ No valid decisions found")
        return

    # Write master CSV file
    master_csv = os.path.join(os.getcwd(), "decisions.csv")

    try:
        with open(master_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['filename', 'decision', 'timestamp', 'notes'])
            writer.writeheader()
            writer.writerows(all_decisions)

        print(f"✅ Master CSV created: {master_csv}")
        print(f"📊 Total decisions: {len(all_decisions)}")
        print(f"   Accept: {sum(1 for d in all_decisions if d['decision'] == 'accept')}")
        print(f"   Reject: {sum(1 for d in all_decisions if d['decision'] == 'reject')}")

        # Optionally clean up individual files
        print(f"\\n🧹 Clean up individual decision files? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            for file_path in decision_files:
                os.remove(file_path)
                print(f"  🗑️  Deleted: {os.path.basename(file_path)}")

    except Exception as e:
        print(f"❌ Error writing master CSV: {e}")

if __name__ == "__main__":
    print("🎯 Bad Offset Identifier Tool - Decision Collector")
    print("=" * 40)
    collect_decisions()