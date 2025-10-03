#!/usr/bin/env python3
"""
Bad Offset Identifier Tool - Standalone Version
Creates a single HTML file that can be reloaded reliably
"""

import os
import sys
import subprocess
import tempfile
import shutil
import base64
from pathlib import Path
from datetime import datetime
import pympi
import csv

class BadOffsetIdentifierStandalone:
    def __init__(self, eaf_folder=None, video_folder=None, output_dir=None):
        # Configuration - can be overridden via environment variables or parameters
        base_dir = output_dir or os.getcwd()
        self.eaf_folder = eaf_folder or os.environ.get('BSL_EAF_FOLDER', '/Volumes/2TB HD/BSLC EAFs (copy)/Conversation')
        self.video_folder = video_folder or os.environ.get('BSL_VIDEO_FOLDER', '/Volumes/2TB HD/BSLC media/Conversation')
        self.output_file = os.path.join(base_dir, "offset_assessment.html")
        self.csv_file = os.path.join(base_dir, "decisions.csv")
        self.target_sign = "GOOD"

    def ensure_csv_exists(self):
        """Create CSV file if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['filename', 'decision', 'timestamp', 'notes'])

    def find_conversation_files(self):
        """Find EAF files with minimum 20 total annotations and GOOD annotations"""
        suitable_files = []
        print("🔍 Scanning files for annotation requirements:")
        print("   • Minimum 20 total annotations per file")
        print("   • Minimum 5 'GOOD' annotations per file")
        print()

        for root, dirs, files in os.walk(self.eaf_folder):
            for file in files:
                if file.endswith('.eaf'):
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) > 100 * 1024:  # >100KB
                        try:
                            eaf = pympi.Elan.Eaf(file_path)

                            # Check dominant hand based on filename
                            is_left_handed = file.upper().endswith('_LH.EAF')
                            dominant_tier = "LH-IDgloss" if is_left_handed else "RH-IDgloss"

                            dominant_data = eaf.get_annotation_data_for_tier(dominant_tier)

                            # Check total annotations first (must be >= 20)
                            total_annotations = len([1 for _, _, value in dominant_data if value and value.strip()])

                            if total_annotations >= 20:  # Minimum 20 total annotations
                                # Then check for GOOD annotations
                                good_count = sum(1 for _, _, value in dominant_data
                                               if value and value.strip().upper() == "GOOD")
                                if good_count >= 5:  # Minimum 5 GOOD annotations
                                    suitable_files.append(file_path)
                                    print(f"  ✅ {file}: {total_annotations} total annotations, {good_count} GOOD")
                                else:
                                    print(f"  ⏭️ {file}: {total_annotations} total annotations, only {good_count} GOOD (need 5+)")
                            else:
                                print(f"  ❌ {file}: Only {total_annotations} total annotations (need 20+)")
                        except:
                            continue

        return suitable_files

    def extract_frame_at_time(self, video_path, time_seconds, output_path):
        """Extract frame using FFmpeg"""
        try:
            cmd = [
                'ffmpeg', '-ss', str(time_seconds), '-i', video_path,
                '-vframes', '1', '-q:v', '2', '-y', output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except:
            return False

    def find_video_files(self, eaf_filename):
        """Find corresponding video files for BSL Corpus"""
        base_name = os.path.splitext(eaf_filename)[0]
        region_code = base_name[:2]

        try:
            number = base_name[2:4].lstrip('0') or '0'
        except:
            number = '1'

        patterns = [
            f"{region_code}/{region_code}{number}+2c.mp4",   # Combined view
            f"{region_code}/{region_code}{number}c.mp4",     # Single view
        ]

        found_videos = []
        for pattern in patterns:
            video_path = os.path.join(self.video_folder, pattern)
            if os.path.exists(video_path):
                found_videos.append(video_path)

        return found_videos

    def get_processed_files(self):
        """Get already processed files from CSV"""
        processed = set()
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed.add(row['filename'])
        return processed

    def generate_html(self):
        """Generate standalone HTML assessment interface"""
        self.ensure_csv_exists()

        # Get files to process
        all_files = self.find_conversation_files()
        processed_files = self.get_processed_files()

        # Filter to unprocessed files
        unprocessed_files = [f for f in all_files if os.path.basename(f) not in processed_files]

        if not unprocessed_files:
            print("🎉 All files have been processed!")
            return

        # Process first unprocessed file
        file_path = unprocessed_files[0]
        filename = os.path.basename(file_path)

        print(f"🔄 Processing: {filename}")
        print(f"📊 Remaining files: {len(unprocessed_files)}")

        # Create temporary directory for frames
        temp_dir = tempfile.mkdtemp()

        try:
            # Parse EAF and extract frames
            eaf = pympi.Elan.Eaf(file_path)

            # Get GOOD annotations from dominant hand
            is_left_handed = filename.upper().endswith('_LH.EAF')
            dominant_tier = "LH-IDgloss" if is_left_handed else "RH-IDgloss"

            dominant_data = eaf.get_annotation_data_for_tier(dominant_tier)
            good_annotations = []
            for start_time, end_time, value in dominant_data:
                if value and value.strip().upper() == self.target_sign.upper():
                    good_annotations.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'value': value
                    })

            # Find videos
            videos = self.find_video_files(filename)

            # Extract frames
            all_frames = []
            for ann_idx, annotation in enumerate(good_annotations):
                for vid_idx, video_path in enumerate(videos):
                    frames = self.extract_annotation_frames(
                        annotation, video_path, temp_dir, f"ann{ann_idx+1}", vid_idx+1
                    )
                    for frame in frames:
                        frame['annotation_idx'] = ann_idx + 1
                        frame['annotation_value'] = annotation['value']
                        frame['video_name'] = f"Video {vid_idx+1}"
                        frame['filename'] = filename
                    all_frames.extend(frames)

            # Generate HTML
            html_content = self.generate_html_content(filename, all_frames, len(unprocessed_files))

            # Write HTML file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✅ HTML generated: {self.output_file}")

            # Open in browser
            os.system(f'open "{self.output_file}"')

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def extract_annotation_frames(self, annotation, video_path, temp_dir, file_prefix, video_num):
        """Extract 4 frames per annotation"""
        start_time_ms = annotation['start_time']
        end_time_ms = annotation['end_time']
        duration_ms = end_time_ms - start_time_ms

        # Multi-point sampling strategy
        sampling_points = [
            ("early", 0.30),    # 30% - gesture formation
            ("peak1", 0.45),    # 45% - primary peak
            ("peak2", 0.65),    # 65% - sustained peak
            ("late", 0.80)      # 80% - completion
        ]

        extracted_frames = []

        for point_name, percentage in sampling_points:
            sample_time_ms = start_time_ms + (duration_ms * percentage)
            sample_time_s = sample_time_ms / 1000.0

            output_path = os.path.join(temp_dir, f"{file_prefix}_v{video_num}_{point_name}.png")

            if self.extract_frame_at_time(video_path, sample_time_s, output_path):
                with open(output_path, 'rb') as f:
                    frame_data = base64.b64encode(f.read()).decode('utf-8')

                extracted_frames.append({
                    'point': point_name,
                    'percentage': percentage,
                    'time_s': sample_time_s,
                    'data': frame_data
                })

        return extracted_frames

    def generate_html_content(self, filename, all_frames, remaining_count):
        """Generate HTML content with 45%/25% layout"""

        # Group frames by annotation
        frames_by_annotation = {}
        for frame in all_frames:
            ann_idx = frame['annotation_idx']
            if ann_idx not in frames_by_annotation:
                frames_by_annotation[ann_idx] = []
            frames_by_annotation[ann_idx].append(frame)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bad Offset Identifier Tool - Assessment</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f5f7fa; }}
        .container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}

        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; text-align: center; }}

        .progress-info {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}

        .frame-gallery {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }}
        .annotation-group {{ margin-bottom: 30px; padding: 20px; background: white; border-radius: 12px; }}

        .main-frame {{ width: 45%; }}
        .secondary-frames {{ width: 25%; display: flex; flex-direction: column; gap: 10px; }}

        .frame-card {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
        .frame-card.main {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 3px solid #667eea; }}

        .frame-img {{ max-width: 100%; height: auto; object-fit: cover; border-radius: 6px; border: 2px solid #ddd; }}
        .frame-img.main {{ height: 300px; }}
        .frame-img.secondary {{ height: 120px; }}

        .frame-label {{ font-size: 11px; margin-top: 8px; color: #666; font-weight: bold; }}
        .annotation-label {{ font-size: 14px; color: #e74c3c; font-weight: bold; margin-bottom: 15px; }}

        .view-toggle {{ margin: 20px 0; text-align: center; }}
        .toggle-btn {{ padding: 8px 16px; margin: 0 5px; border: none; border-radius: 4px; cursor: pointer; background: #f0f0f0; }}
        .toggle-btn.active {{ background: #667eea; color: white; }}

        .frame-grid {{ display: none; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }}

        .assessment-section {{ background: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .assessment-buttons {{ display: flex; gap: 20px; justify-content: center; margin: 20px 0; }}
        .btn {{ padding: 15px 40px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 18px; transition: all 0.3s; }}
        .btn-good {{ background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); color: white; }}
        .btn-bad {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bad Offset Identifier Tool - Assessment</h1>
            <h2>{filename}</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="progress-info">
            <h3>📊 File Status</h3>
            <p><strong>Current file:</strong> {filename}</p>
            <p><strong>Remaining files:</strong> {remaining_count}</p>
            <p><strong>✅ Requirements met:</strong> ≥20 total annotations + ≥5 "GOOD" signs</p>
            <p><strong>👁️ Focus:</strong> Only exact "GOOD" signs from dominant hand shown</p>
            <p><strong>🎯 Task:</strong> Check if video timing matches the annotation timing</p>
        </div>

        <div class="view-toggle">
            <button class="toggle-btn active" onclick="switchView('gallery')">Gallery View (45%/25%)</button>
            <button class="toggle-btn" onclick="switchView('grid')">Grid View</button>
        </div>

        <div id="gallery-container">"""

        # Create gallery layout
        for ann_idx, ann_frames in frames_by_annotation.items():
            if ann_frames:
                html += f"""
            <div class="annotation-group">
                <div class="annotation-label">Annotation {ann_idx}: "{ann_frames[0]['annotation_value']}"</div>
                <div class="frame-gallery">"""

                # Main frame (peak1 at 45%)
                main_frame = ann_frames[1] if len(ann_frames) > 1 else ann_frames[0]
                html += f"""
                    <div class="main-frame">
                        <div class="frame-card main">
                            <img src="data:image/png;base64,{main_frame['data']}" class="frame-img main" alt="Main Frame">
                            <div class="frame-label"><strong>MAIN:</strong> {main_frame['video_name']}<br>{main_frame['point']} ({int(main_frame['percentage']*100)}%)</div>
                        </div>
                    </div>"""

                # Secondary frames
                secondary_frames = [f for f in ann_frames if f != main_frame]
                if secondary_frames:
                    html += f"""
                        <div class="secondary-frames">"""
                    for frame in secondary_frames[:3]:
                        html += f"""
                            <div class="frame-card">
                                <img src="data:image/png;base64,{frame['data']}" class="frame-img secondary" alt="Secondary Frame">
                                <div class="frame-label">{frame['video_name']}<br>{frame['point']} ({int(frame['percentage']*100)}%)</div>
                            </div>"""
                    html += f"""
                        </div>"""

                html += f"""
                </div>
            </div>"""

        html += f"""
        </div>

        <!-- Grid view (hidden by default) -->
        <div id="grid-container" class="frame-grid">"""

        for frame in all_frames:
            html += f"""
            <div class="frame-card">
                <div class="annotation-label">Ann {frame['annotation_idx']}: "{frame['annotation_value']}"</div>
                <img src="data:image/png;base64,{frame['data']}" class="frame-img" alt="Frame">
                <div class="frame-label">{frame['video_name']}<br>{frame['point']} ({int(frame['percentage']*100)}%)</div>
            </div>"""

        html += f"""
        </div>

        <div class="assessment-section">
            <h2>🎯 File Assessment</h2>
            <p>Based on ALL frames above, is the media offset correct for <strong>{filename}</strong>?</p>

            <div class="assessment-buttons">
                <button class="btn btn-good" onclick="recordDecision('accept')">
                    ✅ Accept<br><small>Good offset alignment</small>
                </button>
                <button class="btn btn-bad" onclick="recordDecision('reject')">
                    ❌ Reject<br><small>Poor offset alignment</small>
                </button>
            </div>

            <div id="result" style="margin-top: 20px; font-weight: bold; font-size: 18px;"></div>
        </div>
    </div>

    <script>
        function switchView(viewType) {{
            const galleryContainer = document.getElementById('gallery-container');
            const gridContainer = document.getElementById('grid-container');
            const buttons = document.querySelectorAll('.toggle-btn');

            buttons.forEach(btn => btn.classList.remove('active'));

            if (viewType === 'gallery') {{
                galleryContainer.style.display = 'block';
                gridContainer.style.display = 'none';
                document.querySelector('button[onclick="switchView(\\'gallery\\')"]').classList.add('active');
            }} else {{
                galleryContainer.style.display = 'none';
                gridContainer.style.display = 'grid';
                document.querySelector('button[onclick="switchView(\\'grid\\')"]').classList.add('active');
            }}
        }}

        function recordDecision(decision) {{
            // Save decision locally and show command to run
            const resultDiv = document.getElementById('result');
            const timestamp = new Date().toISOString();

            if (decision === 'accept') {{
                resultDiv.innerHTML = `✅ <span style="color: #27ae60;"><strong>Decision: ACCEPT</strong><br>
                    Run in terminal: <code style="background:#f0f0f0; padding:2px;">python3 save_decision.py "{filename}" accept</code><br>
                    Then refresh page for next file.</span>`;
            }} else {{
                resultDiv.innerHTML = `❌ <span style="color: #e74c3c;"><strong>Decision: REJECT</strong><br>
                    Run in terminal: <code style="background:#f0f0f0; padding:2px;">python3 save_decision.py "{filename}" reject</code><br>
                    Then refresh page for next file.</span>`;
            }}

            // Copy command to clipboard
            const command = `python3 save_decision.py "{filename}" ${{decision}}`;
            navigator.clipboard.writeText(command).then(() => {{
                resultDiv.innerHTML += '<br><small>📋 Command copied to clipboard!</small>';
            }});

            // Disable buttons
            document.querySelectorAll('.btn').forEach(btn => btn.disabled = true);
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.altKey) {{
                if (e.key === 'a') {{
                    recordDecision('accept');
                }} else if (e.key === 'r') {{
                    recordDecision('reject');
                }}
            }}
        }});

        console.log('🎯 Bad Offset Identifier Tool loaded - Alt+A (Accept) | Alt+R (Reject)');
    </script>
</body>
</html>"""

        return html

if __name__ == "__main__":
    processor = BadOffsetIdentifierStandalone()
    processor.generate_html()