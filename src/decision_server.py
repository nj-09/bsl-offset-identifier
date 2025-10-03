#!/usr/bin/env python3
"""
Simple HTTP server to handle CSV decisions
Run this alongside the HTML interface
"""

import http.server
import socketserver
import json
import csv
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class DecisionHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/record_decision':
            # Handle decision recording
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Record to CSV
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
                        if row['filename'] == data['filename']:
                            # Update existing entry
                            row['decision'] = data['decision']
                            row['timestamp'] = datetime.now().isoformat()
                            row['notes'] = data.get('notes', '')
                            updated = True
                        existing_data.append(row)

            # Add new entry if not updated
            if not updated:
                existing_data.append({
                    'filename': data['filename'],
                    'decision': data['decision'],
                    'timestamp': datetime.now().isoformat(),
                    'notes': data.get('notes', '')
                })

            # Write back to CSV
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if existing_data:
                    writer = csv.DictWriter(f, fieldnames=['filename', 'decision', 'timestamp', 'notes'])
                    writer.writeheader()
                    writer.writerows(existing_data)

            print(f"✅ Recorded: {data['filename']} -> {data['decision']}")

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    Handler = DecisionHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Decision server running at http://localhost:{PORT}")
        print(f"📊 CSV decisions will be saved to: {os.path.join(os.getcwd(), 'decisions.csv')}")
        print("Press Ctrl+C to stop")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            httpd.shutdown()