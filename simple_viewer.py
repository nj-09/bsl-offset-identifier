#!/usr/bin/env python3
"""
Simple Navigation Version of Bad Offset Identifier Tool
Shows one main frame at a time with arrow navigation
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

class SimpleSignAnnotate:
    def __init__(self, eaf_folder=None, video_folder=None, output_dir=None):
        # Use provided paths or fallback to CAVA_Data subfolder
        base_dir = output_dir or os.getcwd()
        self.eaf_folder = eaf_folder or os.path.join(base_dir, "CAVA_Data", "EAFs")
        self.video_folder = video_folder or os.path.join(base_dir, "CAVA_Data", "Videos")
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
        print("🔍 Scanning files for annotation requirements...")

        for root, dirs, files in os.walk(self.eaf_folder):
            for file in files:
                if file.endswith('.eaf'):
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) > 100 * 1024:  # >100KB
                        try:
                            eaf = pympi.Elan.Eaf(file_path)
                            is_left_handed = file.upper().endswith('_LH.EAF')
                            dominant_tier = "LH-IDgloss" if is_left_handed else "RH-IDgloss"
                            dominant_data = eaf.get_annotation_data_for_tier(dominant_tier)

                            total_annotations = len([1 for _, _, value in dominant_data if value and value.strip()])

                            if total_annotations >= 20:
                                good_count = sum(1 for _, _, value in dominant_data
                                               if value and value.strip().upper() == "GOOD")
                                if good_count >= 5:
                                    suitable_files.append(file_path)
                                    print(f"  ✅ {file}: {total_annotations} total, {good_count} GOOD")
                        except:
                            continue

        return suitable_files

    def get_processed_files(self):
        """Get already processed files from CSV"""
        processed = set()
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed.add(row['filename'])
        return processed

    def get_video_offset(self, eaf, video_filename):
        """Get video offset from EAF media descriptors"""
        offset = 0
        try:
            for descriptor in eaf.media_descriptors:
                if (offset == 0) and ("MEDIA_URL" in descriptor) and ("TIME_ORIGIN" in descriptor) and (video_filename in descriptor["MEDIA_URL"]):
                    offset = int(descriptor["TIME_ORIGIN"])
                    break
        except (AttributeError, KeyError, ValueError) as e:
            print(f"   ⚠️  Warning: Could not get video offset for {video_filename}: {e}")
            offset = 0
        return offset

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
            f"{region_code}/{region_code}{number}+2c.mp4",
            f"{region_code}/{region_code}{number}c.mp4",
        ]

        found_videos = []
        for pattern in patterns:
            video_path = os.path.join(self.video_folder, pattern)
            if os.path.exists(video_path):
                found_videos.append(video_path)

        # If we only found one video, try to find a complementary video
        if len(found_videos) == 1:
            import glob
            # Look for any other videos with similar number pattern
            search_patterns = [
                f"{region_code}/{region_code}*{number}*c.mp4",
                f"{region_code}/{region_code}{number.zfill(2)}*.mp4"
            ]
            for search_pattern in search_patterns:
                video_pattern = os.path.join(self.video_folder, search_pattern)
                all_matching = glob.glob(video_pattern)
                for video_path in all_matching:
                    if video_path not in found_videos and len(found_videos) < 2:
                        found_videos.append(video_path)

        return found_videos

    def generate_html(self):
        """Generate simple arrow navigation interface"""
        self.ensure_csv_exists()

        all_files = self.find_conversation_files()
        processed_files = self.get_processed_files()
        unprocessed_files = [f for f in all_files if os.path.basename(f) not in processed_files]

        if not unprocessed_files:
            print("🎉 All files have been processed!")
            return

        file_path = unprocessed_files[0]
        filename = os.path.basename(file_path)

        print(f"🔄 Processing: {filename}")
        print(f"📊 Remaining files: {len(unprocessed_files)}")

        temp_dir = tempfile.mkdtemp()

        try:
            eaf = pympi.Elan.Eaf(file_path)
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

            videos = self.find_video_files(filename)
            all_frames = []

            # Extract frames from all annotations and videos
            for ann_idx, annotation in enumerate(good_annotations):
                for vid_idx, video_path in enumerate(videos):
                    frames = self.extract_annotation_frames(
                        annotation, video_path, temp_dir, f"ann{ann_idx+1}", vid_idx+1, eaf
                    )
                    for frame in frames:
                        frame['annotation_idx'] = ann_idx + 1
                        frame['annotation_value'] = annotation['value']
                        frame['video_name'] = f"Video {vid_idx+1}"
                        frame['filename'] = filename
                    all_frames.extend(frames)

            # Generate simple navigation HTML
            html_content = self.generate_simple_html(filename, all_frames, len(unprocessed_files))

            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✅ HTML generated: {self.output_file}")
            os.system(f'open "{self.output_file}"')

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def extract_annotation_frames(self, annotation, video_path, temp_dir, file_prefix, video_num, eaf):
        """Extract only midpoint frame (45%-50%) per annotation per video"""
        start_time_ms = annotation['start_time']
        end_time_ms = annotation['end_time']
        duration_ms = end_time_ms - start_time_ms

        # Get video filename for offset lookup
        video_filename = os.path.basename(video_path)

        # Get video offset from EAF media descriptors
        video_offset_ms = self.get_video_offset(eaf, video_filename)

        # Debug output for offset information
        if video_offset_ms > 0:
            print(f"   📐 Video {video_num} offset: {video_offset_ms}ms for {video_filename}")
        else:
            print(f"   ⚠️  Video {video_num} no offset found for {video_filename}")

        # Extract frame at midpoint (47.5% - perfect middle between 45-50%)
        percentage = 0.475
        point = "midpoint"

        # Apply video offset to get correct timing
        frame_time_ms = start_time_ms + (duration_ms * percentage) + video_offset_ms
        frame_time_seconds = frame_time_ms / 1000.0

        frame_filename = f"{file_prefix}_v{video_num}_{point}.png"
        frame_path = os.path.join(temp_dir, frame_filename)

        frames = []
        if self.extract_frame_at_time(video_path, frame_time_seconds, frame_path):
            with open(frame_path, 'rb') as f:
                frame_data = base64.b64encode(f.read()).decode('utf-8')

            frames.append({
                'data': frame_data,
                'point': point,
                'percentage': percentage,
                'time_seconds': frame_time_seconds,
                'video_path': video_path,
                'video_offset_ms': video_offset_ms,
                'annotation_start_ms': start_time_ms,
                'annotation_end_ms': end_time_ms
            })

        return frames

    def generate_simple_html(self, filename, all_frames, remaining_count):
        """Generate simple HTML with arrow navigation"""

        # Convert frames to JavaScript array
        frames_js = "["
        for i, frame in enumerate(all_frames):
            if i > 0:
                frames_js += ","
            frames_js += f"""{{
                data: "{frame['data']}",
                point: "{frame['point']}",
                percentage: {frame['percentage']},
                annotation: {frame['annotation_idx']},
                video: "{frame['video_name']}",
                time: {frame['time_seconds']:.1f}
            }}"""
        frames_js += "]"

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bad Offset Identifier Tool</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }}
        .navigation-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
        }}
        .nav-btn {{
            padding: 15px 25px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            background: #3498db;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
            min-width: 120px;
        }}
        .nav-btn:hover {{
            background: #2980b9;
            transform: translateY(-2px);
        }}
        .nav-btn:disabled {{
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
        }}
        .annotation-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .annotation-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            padding: 10px;
            background: #ecf0f1;
            border-radius: 10px;
        }}
        .video-comparison {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
        }}
        .video-column {{
            flex: 1;
            max-width: 400px;
        }}
        .video-header {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            padding: 8px;
            background: #d5dbdb;
            border-radius: 8px;
        }}
        .frame-card {{
            border: 3px solid #3498db;
            border-radius: 15px;
            overflow: hidden;
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }}
        .frame-img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .frame-info {{
            padding: 10px;
            background: #ecf0f1;
            font-size: 14px;
            color: #2c3e50;
        }}
        .sync-status {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #f39c12;
        }}
        .file-header {{
            text-align: center;
            margin: 30px 0 20px 0;
            padding: 20px;
            background: #e8f4fd;
            border-radius: 10px;
            border: 2px solid #3498db;
        }}
        .annotations-container {{
            max-height: 70vh;
            overflow-y: auto;
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #dee2e6;
        }}
        .annotation-item {{
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }}
        .progress-info {{
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        .assessment-buttons {{
            text-align: center;
            margin: 30px 0;
            display: flex;
            justify-content: center;
            gap: 30px;
        }}
        .btn {{
            padding: 20px 40px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            min-width: 150px;
        }}
        .btn-good {{
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            color: white;
        }}
        .btn-bad {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
        }}
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }}
        .result {{
            margin: 20px 0;
            text-align: center;
            font-size: 16px;
            font-weight: bold;
        }}
        #frame-counter {{
            font-size: 18px;
            color: #2c3e50;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Bad Offset Identifier Tool</h1>
            <h2>{filename}</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="progress-info">
            <h3>📊 File Status</h3>
            <p><strong>Current file:</strong> {filename}</p>
            <p><strong>Remaining files:</strong> {remaining_count}</p>
            <p><strong>Total frames:</strong> {len(all_frames)} (4 time points × annotations × videos)</p>
            <p><strong>🎯 Task:</strong> Check if video timing matches annotation timing for "GOOD" signs</p>
        </div>

        <div class="file-header">
            <h3>📊 All "GOOD" Annotations in File</h3>
            <p>Scroll down to review all annotations, then make one decision for the entire file</p>
        </div>

        <div class="annotations-container">
            <!-- All annotations will be loaded here by JavaScript -->
        </div>

        <div class="assessment-buttons">
            <button class="btn btn-good" onclick="recordDecision('accept')">
                ✅ Accept<br><small>Good offset alignment</small>
            </button>
            <button class="btn btn-bad" onclick="recordDecision('reject')">
                ❌ Reject<br><small>Poor offset alignment</small>
            </button>
        </div>

        <div id="result" class="result"></div>
    </div>

    <script>
        const frames = {frames_js};

        // Group frames by annotation
        const annotations = {{}};
        frames.forEach(frame => {{
            if (!annotations[frame.annotation]) {{
                annotations[frame.annotation] = {{}};
            }}
            annotations[frame.annotation][frame.video] = frame;
        }});

        const annotationList = Object.keys(annotations).map(Number).sort((a, b) => a - b);

        function loadAllAnnotations() {{
            const container = document.querySelector('.annotations-container');
            let html = '';

            annotationList.forEach(annotationNum => {{
                const annotationFrames = annotations[annotationNum];

                html += `
                    <div class="annotation-item">
                        <div class="annotation-title">
                            Annotation ${{annotationNum}}: "GOOD" (Midpoint: 47.5%)
                        </div>
                        <div class="video-comparison">
                `;

                // Video 1 column
                if (annotationFrames['Video 1']) {{
                    const frame1 = annotationFrames['Video 1'];
                    html += `
                        <div class="video-column">
                            <div class="video-header">📹 Video 1</div>
                            <div class="frame-card">
                                <img src="data:image/png;base64,${{frame1.data}}" class="frame-img" alt="Video 1">
                                <div class="frame-info">Time: ${{frame1.time}}s</div>
                            </div>
                        </div>
                    `;
                }}

                // Video 2 column
                if (annotationFrames['Video 2']) {{
                    const frame2 = annotationFrames['Video 2'];
                    html += `
                        <div class="video-column">
                            <div class="video-header">📹 Video 2</div>
                            <div class="frame-card">
                                <img src="data:image/png;base64,${{frame2.data}}" class="frame-img" alt="Video 2">
                                <div class="frame-info">Time: ${{frame2.time}}s</div>
                            </div>
                        </div>
                    `;
                }}

                html += `
                        </div>
                        <div class="sync-status">
                            <strong>🎯 Check:</strong> Do both videos show the "GOOD" sign at the same moment?
                            If timing looks off or signs don't match, this indicates bad offset alignment.
                        </div>
                    </div>
                `;
            }});

            container.innerHTML = html;
        }}

        function recordDecision(decision) {{
            const resultDiv = document.getElementById('result');
            const timestamp = new Date().toISOString();

            // Update main CSV via server (immediate update)
            fetch('http://localhost:8000/record_decision', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    filename: '{filename}',
                    decision: decision,
                    timestamp: timestamp,
                    notes: decision === 'accept' ? 'Good offset alignment' : 'Poor offset alignment'
                }})
            }}).then(response => {{
                if (response.ok) {{
                    console.log('✅ Main CSV updated successfully');
                }} else {{
                    console.log('⚠️ Server update failed (response not ok), backup download still works');
                    console.log('Status:', response.status, response.statusText);
                }}
            }}).catch(error => {{
                console.log('⚠️ Server not available, backup download still works');
                console.log('Error:', error.message);
            }});

            // Create backup CSV download (keep existing functionality)
            const csvRecord = `{filename},${{decision}},${{timestamp}},\\n`;
            const blob = new Blob([csvRecord], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `decision_${{decision}}_{filename}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            if (decision === 'accept') {{
                resultDiv.innerHTML = `✅ <span style="color: #27ae60;"><strong>Decision: ACCEPT for entire file</strong><br>
                    ✅ Main CSV updated immediately!<br>
                    ✅ Backup file downloaded to Downloads folder!<br>
                    📁 File: decision_accept_{filename}.csv<br>
                    🔄 Refreshing page for next file in 3 seconds...</span>`;
            }} else {{
                resultDiv.innerHTML = `❌ <span style="color: #e74c3c;"><strong>Decision: REJECT for entire file</strong><br>
                    ✅ Main CSV updated immediately!<br>
                    ✅ Backup file downloaded to Downloads folder!<br>
                    📁 File: decision_reject_{filename}.csv<br>
                    🔄 Refreshing page for next file in 3 seconds...</span>`;
            }}

            // Disable buttons
            document.querySelectorAll('.btn').forEach(btn => btn.disabled = true);

            // Scroll to result
            resultDiv.scrollIntoView({{ behavior: 'smooth' }});

            // Auto-refresh for next file
            setTimeout(() => {{
                window.location.reload();
            }}, 3000);
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

        // Initialize - load all annotations
        loadAllAnnotations();
        console.log('🎯 Review all annotations, then: Alt+A (Accept) | Alt+R (Reject)');
    </script>
</body>
</html>'''

        return html

if __name__ == "__main__":
    processor = SimpleSignAnnotate()
    processor.generate_html()