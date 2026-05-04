#!/bin/bash
# Phase 2 Regression Test Suite
# Compiles test documents through both OLD and NEW paths and compares outputs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILE_SCRIPT="$SCRIPT_DIR/../scripts/compile_document.py"

# Test documents
TESTS=(
    "simple_test.json"
    "table_styles_test.json"
    "airbus_rfp_v3_test.json"
)

echo "=========================================="
echo "Phase 2 Regression Test Suite"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

for test_doc in "${TESTS[@]}"; do
    echo "Testing: $test_doc"
    echo "------------------------------------------"

    # Extract base name
    base=$(basename "$test_doc" .json)

    # Compile with OLD path (USE_EXTERNAL_PROCESSOR=False)
    echo "  Compiling with OLD path..."
    # Temporarily disable external processor
    sed -i.bak 's/USE_EXTERNAL_PROCESSOR = True/USE_EXTERNAL_PROCESSOR = False/' "$COMPILE_SCRIPT"

    if python3 "$COMPILE_SCRIPT" "$SCRIPT_DIR/$test_doc" "/tmp/regression_old_${base}.pdf" general --font-size 10pt > /tmp/old_${base}.log 2>&1; then
        echo "  ✓ OLD path compiled successfully"
    else
        echo "  ✗ OLD path FAILED"
        cat /tmp/old_${base}.log
        FAILED=$((FAILED + 1))
        # Restore
        mv "$COMPILE_SCRIPT.bak" "$COMPILE_SCRIPT"
        continue
    fi

    # Compile with NEW path (USE_EXTERNAL_PROCESSOR=True)
    echo "  Compiling with NEW path..."
    # Re-enable external processor
    sed -i.bak 's/USE_EXTERNAL_PROCESSOR = False/USE_EXTERNAL_PROCESSOR = True/' "$COMPILE_SCRIPT"

    if python3 "$COMPILE_SCRIPT" "$SCRIPT_DIR/$test_doc" "/tmp/regression_new_${base}.pdf" general --font-size 10pt > /tmp/new_${base}.log 2>&1; then
        echo "  ✓ NEW path compiled successfully"
    else
        echo "  ✗ NEW path FAILED"
        cat /tmp/new_${base}.log
        FAILED=$((FAILED + 1))
        # Restore
        mv "$COMPILE_SCRIPT.bak" "$COMPILE_SCRIPT"
        continue
    fi

    # Compare PDFs
    echo "  Comparing outputs..."
    pdftotext "/tmp/regression_old_${base}.pdf" "/tmp/old_${base}.txt"
    pdftotext "/tmp/regression_new_${base}.pdf" "/tmp/new_${base}.txt"

    if diff "/tmp/old_${base}.txt" "/tmp/new_${base}.txt" > "/tmp/diff_${base}.txt"; then
        echo "  ✓ Output IDENTICAL"
        PASSED=$((PASSED + 1))
    else
        echo "  ✗ Output DIFFERS"
        echo "  Diff saved to /tmp/diff_${base}.txt"
        head -20 "/tmp/diff_${base}.txt"
        FAILED=$((FAILED + 1))
    fi

    # Get page counts
    old_pages=$(pdfinfo "/tmp/regression_old_${base}.pdf" 2>/dev/null | grep "^Pages:" | awk '{print $2}')
    new_pages=$(pdfinfo "/tmp/regression_new_${base}.pdf" 2>/dev/null | grep "^Pages:" | awk '{print $2}')

    echo "  Pages: OLD=$old_pages, NEW=$new_pages"
    echo ""

    # Restore original file
    rm -f "$COMPILE_SCRIPT.bak"
done

echo "=========================================="
echo "Results: $PASSED passed, $FAILED failed"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo "✓ All regression tests PASSED"
    exit 0
else
    echo "✗ Some tests FAILED"
    exit 1
fi
