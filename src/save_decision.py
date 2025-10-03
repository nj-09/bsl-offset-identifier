#!/usr/bin/env python3
"""
Simple script to save a decision to CSV
Usage: python3 save_decision.py filename accept/reject
"""

import sys
import csv
import os
from datetime import datetime

def save_decision(filename, decision):
    csv_file = os.path.join(os.getcwd(), "decisions.csv")

    # Ensure CSV exists
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'decision', 'timestamp', 'notes'])

    # Read existing data
    existing_data = []
    updated = False

    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['filename'] == filename:
                    # Update existing entry
                    row['decision'] = decision
                    row['timestamp'] = datetime.now().isoformat()
                    updated = True
                existing_data.append(row)

    # Add new entry if not updated
    if not updated:
        existing_data.append({
            'filename': filename,
            'decision': decision,
            'timestamp': datetime.now().isoformat(),
            'notes': ''
        })

    # Write back to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if existing_data:
            writer = csv.DictWriter(f, fieldnames=['filename', 'decision', 'timestamp', 'notes'])
            writer.writeheader()
            writer.writerows(existing_data)

    print(f"✅ Decision saved: {filename} -> {decision}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 save_decision.py filename accept/reject")
        sys.exit(1)

    filename = sys.argv[1]
    decision = sys.argv[2]

    if decision not in ['accept', 'reject']:
        print("Decision must be 'accept' or 'reject'")
        sys.exit(1)

    save_decision(filename, decision)