# 🎯 Bad Offset Identifier Tool

> **Reliable, standalone system for identifying BSL video files with bad offset alignment**

## 🚀 Quick Start

### Installation
```bash
git clone <repository-url>
cd BadOffsetIdentifier
pip3 install -r requirements.txt
```

### Configuration
Set environment variables for your BSL data sources:
```bash
export BSL_EAF_FOLDER="/path/to/your/eaf/files"
export BSL_VIDEO_FOLDER="/path/to/your/video/files"
```

Or place your data in:
```bash
BadOffsetIdentifier/CAVA_Data/EAFs/
BadOffsetIdentifier/CAVA_Data/Videos/
```

### Run
```bash
python3 run_bot.py
```

**That's it!** The system will:
1. ✅ Generate HTML assessment interface
2. 📊 Create CSV tracking file
3. 🌐 Open browser automatically
4. 🔄 Ready to reload for each new file

## 📁 **Clean Project Structure**

```
BadOffsetIdentifier/
├── run_bot.py                   # 🎯 MAIN SCRIPT - Run this!
├── simple_viewer.py             # Core assessment logic
├── collect_decisions.py         # Merge downloaded decisions
├── save_decision.py             # Manual CSV save script (backup)
├── requirements.txt             # Python dependencies
├── offset_assessment.html       # Generated HTML (reloadable)
├── decisions.csv               # Your decision tracking
└── README.md                   # This file
```

## 🎭 **What This Tool Does (Simple Explanation)**

1. **Finds Files**: Looks for complete annotation files (≥20 total annotations + ≥5 "GOOD" signs)
2. **Smart Detection**: Only looks at the person's dominant hand (left or right)
3. **Takes Pictures**: Captures 4 key moments of each "GOOD" sign
4. **Shows You**: Displays one main picture (45%) + 3 smaller ones (25%)
5. **Remembers**: Saves your Accept/Reject decisions in CSV file
6. **Never Repeats**: Skips files you've already checked

## 🖼️ **Gallery Layout Features**

### **45%/25% Layout (Default)**
- **Main Frame (45%)**: Shows the peak gesture moment (most important)
- **Secondary Frames (25% each)**: Shows start, hold, and end moments
- **Less cluttered**: Focus on main gesture with supporting context

### **Grid View (Toggle)**
- **Equal-sized frames**: Traditional grid layout
- **All frames visible**: See everything at once
- **Switch easily**: Toggle between views

## 📊 **CSV Tracking System**

### **File Location**
```
BadOffsetIdentifier/decisions.csv
```

### **Format**
```csv
filename,decision,timestamp,notes
BF01F28WDC.eaf,accept,2024-09-26T11:30:15,Good alignment
BF02M25WDC.eaf,reject,2024-09-26T11:35:22,Poor timing
```

### **How It Works**
1. 🏃‍♂️ **First run**: Creates empty CSV
2. 👆 **Every decision**: Adds new line immediately
3. 🔄 **Next run**: Reads CSV and skips processed files
4. 💾 **Always saved**: Never lose your progress

## ⌨️ **Usage Instructions**

### **Basic Workflow**
1. Run: `python3 run_bot.py`
2. Browser opens with first unprocessed file
3. Review frames showing "GOOD" signs
4. Click **Accept ✅** or **Reject ❌**
5. Decision downloads automatically to Downloads folder
6. Page refreshes automatically for next file
7. Run `python3 collect_decisions.py` to merge all decisions

### **Keyboard Shortcuts**
- `Alt + A`: Accept (faster than clicking)
- `Alt + R`: Reject (faster than clicking)

### **If Page Won't Load**
- Check: BSL data sources configured correctly?
- Check: Run from project root directory?
- Check: Python dependencies installed? (`pip3 install -r requirements.txt`)

## 🔧 **Technical Details**

### **Requirements Met**
- ✅ **Minimum 20 total annotations**: Files with <20 annotations discarded as incomplete
- ✅ **Only "GOOD" signs**: Exact string matching (`== "GOOD"`)
- ✅ **Dominant hand only**: Auto-detects from filename (`_LH` = left hand)
- ✅ **Gallery viewpoint**: 45% main + 25% secondary layout
- ✅ **CSV tracking**: Filename + decision columns
- ✅ **Resume functionality**: Never check same file twice
- ✅ **Reloadable**: Single HTML file you can refresh

### **Performance Targets**
- 🎯 **50 files/hour**: 72 seconds per file
- ⚡ **Frame extraction**: <2 seconds per annotation
- 🖼️ **Display**: Instant gallery layout
- 💾 **CSV write**: <1ms per decision

## 🛠️ **For Your Supervisor**

### **Q: "How does the standalone system work?"**
**A:** Single Python script generates one HTML file with all frames embedded as base64. No external dependencies - just reload the page for next file.

### **Q: "How reliable is the CSV tracking?"**
**A:** Atomic writes prevent corruption. Each decision immediately saved. System reads CSV on startup to determine which files to skip.

### **Q: "What if the system crashes?"**
**A:** All decisions up to crash point are saved in CSV. Restart the script and it continues from where it left off.

### **Q: "How do I verify it's working correctly?"**
**A:**
1. Check `decisions.csv` file exists and grows
2. Reload page shows different file each time
3. Console shows "Skipping X (already processed)" messages

## 🎉 **Success Indicators**

**You know it's working when:**
- ✅ HTML file opens in browser showing real video frames
- ✅ CSV file appears and grows with each decision
- ✅ Reloading page shows next unprocessed file
- ✅ Console shows processing progress and skip messages
- ✅ Only exact "GOOD" signs appear (not "GOODBYE", etc.)
- ✅ Gallery shows 1 large + 3 small frames per annotation

---

**🎯 This is your complete Bad Offset Identifier Tool - ready for production use!**