# 📊 Bad Offset Identifier Tool - Annotation Requirements

## 🎯 **File Selection Criteria (Updated)**

### **✅ Files Must Have:**
1. **≥20 total annotations** in dominant hand tier
2. **≥5 exact "GOOD" annotations** in dominant hand tier
3. **>100KB file size** (ensures substantial content)

### **❌ Files Discarded If:**
- <20 total annotations → Incomplete file
- <5 "GOOD" annotations → Insufficient target signs
- <100KB → Too small/empty

## 🔍 **How File Scanning Works**

### **Step-by-Step Process:**
1. **Check file size** → Skip if <100KB
2. **Determine dominant hand** → `_LH.eaf` = left hand, others = right hand
3. **Count total annotations** → Must be ≥20 in dominant tier
4. **Count "GOOD" annotations** → Must be ≥5 exact matches
5. **Add to processing queue** → Only if both criteria met

### **Console Output Example:**
```
🔍 Scanning files for annotation requirements:
   • Minimum 20 total annotations per file
   • Minimum 5 'GOOD' annotations per file

  ✅ BF01F28WDC.eaf: 45 total annotations, 12 GOOD
  ❌ BF02M25WDC.eaf: Only 18 total annotations (need 20+)
  ⏭️ BF03F30WDC.eaf: 25 total annotations, only 3 GOOD (need 5+)
  ✅ BF04M32WDC.eaf: 38 total annotations, 8 GOOD
```

## 🎯 **Why These Requirements?**

### **20 Total Annotations:**
- **Supervisor requirement**: "Minimum 20 annotations (skip if less than 20 total annotations)"
- **Purpose**: Ensures file has substantial content for meaningful assessment
- **Quality control**: Incomplete annotation files not worth reviewing

### **5 "GOOD" Annotations:**
- **Practical minimum**: Need enough examples to assess timing quality
- **Statistical validity**: Multiple samples reduce chance assessment errors
- **Efficiency**: Avoids files with too few target signs

### **Dominant Hand Only:**
- **Reduces confusion**: Focus on primary signing hand
- **Follows BSL conventions**: Signers have dominant hand preference
- **Cleaner assessment**: Eliminates redundant annotations

## 🔧 **Technical Implementation**

### **Code Logic:**
```python
# Check total annotations first
total_annotations = len([1 for _, _, value in dominant_data
                        if value and value.strip()])

if total_annotations >= 20:  # Must have 20+ total
    # Then check for GOOD annotations
    good_count = sum(1 for _, _, value in dominant_data
                    if value and value.strip().upper() == "GOOD")
    if good_count >= 5:  # Must have 5+ GOOD
        suitable_files.append(file_path)  # ✅ Meets criteria
```

### **File Processing Order:**
1. **Size filter** → >100KB files only
2. **Annotation count** → ≥20 total annotations
3. **Target sign count** → ≥5 "GOOD" signs
4. **Processing queue** → Add to assessment list

## 📊 **Expected Results**

### **Typical Corpus Statistics:**
- **Total files**: ~249 conversation files
- **Size filtered**: ~200 files >100KB
- **Annotation filtered**: ~150 files ≥20 annotations
- **GOOD filtered**: ~100 files ≥5 "GOOD" signs
- **Final queue**: ~100 files for assessment

### **Quality Benefits:**
- ✅ **Higher completion rates**: Only substantial files processed
- ✅ **Better assessment quality**: Sufficient examples per file
- ✅ **Efficient workflow**: No time wasted on incomplete files
- ✅ **Consistent standards**: All files meet minimum criteria

## 🎉 **Summary for Supervisor**

**The system now properly filters files with:**
- ✅ **Minimum 20 total annotations** (as requested)
- ✅ **Minimum 5 "GOOD" target signs** (for meaningful assessment)
- ✅ **Automatic dominant hand detection** (reduces confusion)
- ✅ **Clear console reporting** (shows why files included/excluded)

**Result: Only complete, substantial annotation files are processed for assessment!** 🎯