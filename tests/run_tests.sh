#!/bin/bash
#
# Test runner for LaTeX document compilation
# Compiles all test documents and reports results
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$SCRIPT_DIR/documents"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}LaTeX Document Compiler Test Suite${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Counter for results
TOTAL=0
PASSED=0
FAILED=0

# Function to compile a test document
compile_test() {
    local json_file="$1"
    local basename="$(basename "$json_file" .json)"
    local output_pdf="$OUTPUT_DIR/${basename}.pdf"

    TOTAL=$((TOTAL + 1))

    echo -e "${YELLOW}Testing:${NC} $basename"

    # Run compilation
    if python3 "$REPO_ROOT/scripts/compile_document.py" \
        "$json_file" \
        "$output_pdf" \
        "general" > /dev/null 2>&1; then

        # Get page count from output
        local pages=$(pdfinfo "$output_pdf" 2>/dev/null | grep "Pages:" | awk '{print $2}')

        echo -e "  ${GREEN}✓ PASSED${NC} - Generated $pages pages"
        echo -e "  Output: $output_pdf"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${RED}✗ FAILED${NC} - Compilation error"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Find and compile all test documents
echo -e "Searching for test documents in: $DOCS_DIR"
echo ""

if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}Error: Documents directory not found: $DOCS_DIR${NC}"
    exit 1
fi

# Compile each JSON file
for json_file in "$DOCS_DIR"/*.json; do
    if [ -f "$json_file" ]; then
        compile_test "$json_file"
    fi
done

# Print summary
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "Total:  $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "Failed: $FAILED"
fi
echo ""

# Exit with appropriate code
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
