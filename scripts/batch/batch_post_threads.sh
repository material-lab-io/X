#!/bin/bash
# Batch processing script for posting multiple threads with diagrams

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DIAGRAM_DIR="/home/kushagra/X/optimized"
DRY_RUN=false
THREAD_DIR="."
PATTERN="*.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --diagram-dir)
            DIAGRAM_DIR="$2"
            shift 2
            ;;
        --thread-dir)
            THREAD_DIR="$2"
            shift 2
            ;;
        --pattern)
            PATTERN="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run        Preview without posting"
            echo "  --diagram-dir    Directory containing optimized diagrams (default: $DIAGRAM_DIR)"
            echo "  --thread-dir     Directory containing thread JSON files (default: current)"
            echo "  --pattern        File pattern to match (default: *.json)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Header
echo -e "${GREEN}🚀 Batch Thread Posting Script${NC}"
echo "================================"
echo "Diagram directory: $DIAGRAM_DIR"
echo "Thread directory: $THREAD_DIR"
echo "File pattern: $PATTERN"
echo "Dry run: $DRY_RUN"
echo ""

# Check for required environment variables
if [ "$DRY_RUN" = false ]; then
    MISSING_VARS=()
    
    [ -z "$API_KEY" ] && MISSING_VARS+=("API_KEY")
    [ -z "$API_SECRET" ] && MISSING_VARS+=("API_SECRET")
    [ -z "$ACCESS_TOKEN" ] && MISSING_VARS+=("ACCESS_TOKEN")
    [ -z "$ACCESS_TOKEN_SECRET" ] && MISSING_VARS+=("ACCESS_TOKEN_SECRET")
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing Twitter API credentials:${NC}"
        for var in "${MISSING_VARS[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "Set them with:"
        echo "   export API_KEY='your_key'"
        echo "   export API_SECRET='your_secret'"
        echo "   export ACCESS_TOKEN='your_token'"
        echo "   export ACCESS_TOKEN_SECRET='your_token_secret'"
        exit 1
    fi
fi

# Find thread files
THREAD_FILES=($(find "$THREAD_DIR" -maxdepth 1 -name "$PATTERN" -type f))

if [ ${#THREAD_FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}No thread files found matching pattern: $PATTERN${NC}"
    exit 0
fi

echo -e "${GREEN}Found ${#THREAD_FILES[@]} thread files to process${NC}"
echo ""

# Process each file
SUCCESS_COUNT=0
FAIL_COUNT=0

for file in "${THREAD_FILES[@]}"; do
    echo -e "${YELLOW}Processing: $(basename "$file")${NC}"
    
    # Build command
    CMD="venv/bin/python tweet_diagram_binder.py \"$file\" --diagram-dir \"$DIAGRAM_DIR\""
    
    if [ "$DRY_RUN" = true ]; then
        CMD="$CMD --dry-run"
    fi
    
    # Run the command
    if eval $CMD; then
        echo -e "${GREEN}✅ Success${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ Failed${NC}"
        ((FAIL_COUNT++))
    fi
    
    echo ""
    
    # Add delay between posts (if not dry run)
    if [ "$DRY_RUN" = false ] && [ "$file" != "${THREAD_FILES[-1]}" ]; then
        echo "Waiting 30 seconds before next post..."
        sleep 30
    fi
done

# Summary
echo "================================"
echo -e "${GREEN}📊 BATCH PROCESSING SUMMARY${NC}"
echo "================================"
echo "Total files: ${#THREAD_FILES[@]}"
echo -e "Successful: ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"

# Generate report if not dry run
if [ "$DRY_RUN" = false ] && [ $SUCCESS_COUNT -gt 0 ]; then
    echo ""
    echo "Generating posting report..."
    venv/bin/python posting_summary.py --report
fi

echo ""
echo "✨ Done!"