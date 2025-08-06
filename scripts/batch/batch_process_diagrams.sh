#!/bin/bash
# Batch process all generated thread JSON files for diagram extraction

echo "🚀 Batch Diagram Processing Pipeline"
echo "===================================="

# Set up environment
export PATH="/home/kushagra/X/XPosts/node_modules/.bin:$PATH"
source venv/bin/activate

# Create output directory
OUTPUT_DIR="processed_diagrams"
mkdir -p $OUTPUT_DIR

# Find all thread JSON files (excluding samples)
echo -e "\n📂 Finding thread JSON files..."
JSON_FILES=$(find . -name "*.json" -path "./generated_*" -o -name "*thread*.json" | grep -v sample | head -20)

if [ -z "$JSON_FILES" ]; then
    echo "❌ No thread JSON files found!"
    echo "   Generate some threads first with: python unified_tweet_generator.py"
    exit 1
fi

echo "Found $(echo "$JSON_FILES" | wc -l) files to process"

# Process with Python pipeline
echo -e "\n⚙️ Processing diagrams..."
python diagram_automation_pipeline.py $JSON_FILES --output-dir $OUTPUT_DIR --index

# Generate summary report
echo -e "\n📊 Generating summary report..."
cat > $OUTPUT_DIR/processing_report.md << EOF
# Diagram Processing Report
Generated on: $(date)

## Summary
- Total files processed: $(echo "$JSON_FILES" | wc -l)
- Output directory: $OUTPUT_DIR

## Processed Files
$(echo "$JSON_FILES" | while read f; do echo "- $f"; done)

## Directory Structure
\`\`\`
$(tree $OUTPUT_DIR 2>/dev/null || ls -la $OUTPUT_DIR)
\`\`\`

## Next Steps
1. Review generated PNGs in \`$OUTPUT_DIR/png/\`
2. Check metadata in \`$OUTPUT_DIR/metadata/\`
3. Use diagrams in your Twitter threads!
EOF

echo -e "\n✅ Processing complete!"
echo "   📁 Output directory: $OUTPUT_DIR"
echo "   📄 Report: $OUTPUT_DIR/processing_report.md"
echo "   🖼️ PNG files: $OUTPUT_DIR/png/"