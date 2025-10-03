#!/usr/bin/env python3
"""
Bad Offset Identifier Tool Main Runner
Single command to run the complete assessment system
"""

import subprocess
import sys
import os
import time

def main():
    print("🎯 Bad Offset Identifier Tool")
    print("=" * 50)

    # Check if required files exist
    base_dir = os.getcwd()

    # Check for CAVA data folder
    cava_folder = os.path.join(base_dir, "CAVA_Data")
    if not os.path.exists(cava_folder):
        print("⚠️  CAVA_Data folder not found. Please download narrative files first.")
        print(f"   Expected folder: {cava_folder}")
        return

    print("✅ CAVA data folder found")
    print("🔄 Starting assessment system...")

    try:
        # Start decision server in background
        print("🌐 Starting decision server...")
        server_process = subprocess.Popen([
            sys.executable, "decision_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())

        # Give server time to start and verify it's working
        time.sleep(3)

        # Test if server is responding
        try:
            import urllib.request
            import json

            # Test with a simple request
            test_data = json.dumps({"test": "connection"}).encode('utf-8')
            req = urllib.request.Request('http://localhost:8000/', data=test_data,
                                       headers={'Content-Type': 'application/json'})
            response = urllib.request.urlopen(req, timeout=2)
            print("✅ Decision server started and responding on port 8000")
        except:
            print("⚠️  Decision server started but may not be fully ready")
            print("   (This is normal - it will work when you make decisions)")

        # Run the simple arrow navigation viewer
        from simple_viewer import SimpleSignAnnotate

        processor = SimpleSignAnnotate()
        processor.generate_html()

        print("\n🎉 Bad Offset Identifier Tool is ready!")
        print(f"📁 HTML file: {processor.output_file}")
        print(f"📊 CSV file: {processor.csv_file}")
        print("🌐 Decision server: http://localhost:8000")
        print("📊 Data source: CAVA BSL Corpus Narratives")
        print("\n📋 Simple Instructions:")
        print("1. The HTML file will open automatically in your browser")
        print("2. Review all 'GOOD' sign frames (scroll down to see all)")
        print("3. Click Accept ✅ or Reject ❌ for the entire file")
        print("4. ✨ Main CSV updates IMMEDIATELY + backup downloads to Downloads")
        print("5. Page refreshes automatically for next file")
        print("6. 🎯 No need to run collect_decisions.py - CSV updates in real-time!")

    except ImportError:
        print("❌ Missing dependencies. Please install:")
        print("   pip3 install pympi-ling")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()