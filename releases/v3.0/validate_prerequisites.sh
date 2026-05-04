#!/bin/bash
# LaTeX Skills Infrastructure Validation Script
# Checks all prerequisites for latex-docs skill deployment

set +e  # Don't exit on errors, we want to collect all results

echo "=========================================="
echo "LaTeX Skills - Infrastructure Validation"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    WARNINGS=$((WARNINGS + 1))
}

echo "=== System Information ==="
echo "OS: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "Hostname: $(hostname)"
echo ""

# 1. Python Check
echo "=== Python Version Check ==="
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
        check_pass "Python $PYTHON_VERSION (>= 3.7 required)"
        echo "  Location: $(which python3)"
    else
        check_fail "Python $PYTHON_VERSION found, but 3.7+ required"
    fi
else
    check_fail "python3 not found in PATH"
fi
echo ""

# 2. Python Standard Library Check
echo "=== Python Standard Library Check ==="
python3 -c "import json, os, re, shutil, subprocess, sys, tempfile" 2>/dev/null
if [ $? -eq 0 ]; then
    check_pass "All required Python stdlib modules available"
else
    check_fail "Missing required Python stdlib modules"
fi

python3 -c "from pathlib import Path; from typing import Dict, Any, List, Tuple; from dataclasses import dataclass" 2>/dev/null
if [ $? -eq 0 ]; then
    check_pass "Python typing and dataclasses available"
else
    check_fail "Python typing/dataclasses not available (need Python 3.7+)"
fi
echo ""

# 3. pdflatex Check
echo "=== LaTeX Distribution Check ==="
if command -v pdflatex &> /dev/null; then
    PDFLATEX_VERSION=$(pdflatex --version 2>&1 | head -n1)
    check_pass "pdflatex found"
    echo "  Version: $PDFLATEX_VERSION"
    echo "  Location: $(which pdflatex)"

    # Check for required LaTeX packages
    echo ""
    echo "  Checking LaTeX packages..."

    # Test LaTeX compilation
    TEST_TEX="/tmp/latex_test_$$.tex"
    cat > "$TEST_TEX" << 'EOF'
\documentclass{article}
\usepackage{geometry}
\usepackage{fontenc}
\usepackage{helvet}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{colortbl}
\usepackage{hyperref}
\begin{document}
Test
\end{document}
EOF

    pdflatex -interaction=nonstopmode -output-directory=/tmp "$TEST_TEX" &>/dev/null
    if [ $? -eq 0 ]; then
        check_pass "All required LaTeX packages available"
        rm -f "/tmp/latex_test_$$."* 2>/dev/null
    else
        check_fail "Some required LaTeX packages missing"
        echo "  Run: pdflatex -interaction=nonstopmode $TEST_TEX"
        echo "  to see which packages are missing"
    fi
else
    check_fail "pdflatex not found"
    echo ""
    echo "  Installation instructions:"
    echo "  - macOS: brew install --cask mactex"
    echo "  - Ubuntu/Debian: sudo apt-get install texlive-full"
    echo "  - RHEL/CentOS: sudo yum install texlive-scheme-full"
    echo "  - Windows: Download MiKTeX from miktex.org"
fi
echo ""

# 4. pdftotext Check
echo "=== PDF Utilities Check ==="
if command -v pdftotext &> /dev/null; then
    PDFTOTEXT_VERSION=$(pdftotext -v 2>&1 | head -n1)
    check_pass "pdftotext found"
    echo "  Version: $PDFTOTEXT_VERSION"
    echo "  Location: $(which pdftotext)"
else
    check_fail "pdftotext not found"
    echo ""
    echo "  Installation instructions:"
    echo "  - macOS: brew install poppler"
    echo "  - Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "  - RHEL/CentOS: sudo yum install poppler-utils"
    echo "  - Windows: Download from poppler-windows releases"
fi
echo ""

# 5. pdfinfo Check (optional but useful)
echo "=== Optional Utilities Check ==="
if command -v pdfinfo &> /dev/null; then
    check_pass "pdfinfo found (for page counting)"
    echo "  Location: $(which pdfinfo)"
else
    check_warn "pdfinfo not found (page counting may fail)"
    echo "  Install with same package as pdftotext (poppler-utils)"
fi
echo ""

# 6. Disk Space Check
echo "=== Disk Space Check ==="
if [ -d "/tmp" ]; then
    TMP_SPACE=$(df -h /tmp | tail -1 | awk '{print $4}')
    TMP_SPACE_BYTES=$(df /tmp | tail -1 | awk '{print $4}')

    # Need at least 500MB for LaTeX compilation work directory
    if [ "$TMP_SPACE_BYTES" -gt 512000 ]; then
        check_pass "/tmp has $TMP_SPACE available (>500MB required)"
    else
        check_warn "/tmp has only $TMP_SPACE available (500MB+ recommended)"
    fi
else
    check_warn "/tmp directory not found"
fi
echo ""

# 7. Memory Check
echo "=== Memory Check ==="
if command -v free &> /dev/null; then
    MEMORY_MB=$(free -m | grep Mem: | awk '{print $2}')
    if [ "$MEMORY_MB" -gt 512 ]; then
        check_pass "System has ${MEMORY_MB}MB RAM (>512MB recommended)"
    else
        check_warn "System has only ${MEMORY_MB}MB RAM (512MB+ recommended)"
    fi
elif command -v sysctl &> /dev/null; then
    # macOS
    MEMORY_BYTES=$(sysctl -n hw.memsize 2>/dev/null)
    if [ -n "$MEMORY_BYTES" ]; then
        MEMORY_MB=$((MEMORY_BYTES / 1024 / 1024))
        if [ "$MEMORY_MB" -gt 512 ]; then
            check_pass "System has ${MEMORY_MB}MB RAM (>512MB recommended)"
        else
            check_warn "System has only ${MEMORY_MB}MB RAM (512MB+ recommended)"
        fi
    else
        check_warn "Could not determine system memory"
    fi
else
    check_warn "Could not determine system memory"
fi
echo ""

# 8. File System Permissions Check
echo "=== File System Permissions Check ==="
TEST_FILE="/tmp/latex_perm_test_$$"
touch "$TEST_FILE" 2>/dev/null
if [ $? -eq 0 ]; then
    check_pass "/tmp is writable"
    rm -f "$TEST_FILE"
else
    check_fail "/tmp is not writable"
fi

if [ -w "$HOME/.claude/skills" ] 2>/dev/null || mkdir -p "$HOME/.claude/skills" 2>/dev/null; then
    check_pass "$HOME/.claude/skills is writable"
else
    check_fail "$HOME/.claude/skills is not writable or creatable"
fi
echo ""

# 9. Network Check (for image fetching, if needed)
echo "=== Network Check (Optional) ==="
if command -v curl &> /dev/null || command -v wget &> /dev/null; then
    check_pass "HTTP client available (curl or wget)"
else
    check_warn "No HTTP client found (curl/wget) - image fetching may fail"
fi
echo ""

# 10. Test Compilation (if skills are installed)
echo "=== Skills Installation Check ==="
SKILLS_DIR="$HOME/.claude/skills"

if [ -d "$SKILLS_DIR/latex-docs" ]; then
    check_pass "latex-docs skill found at $SKILLS_DIR/latex-docs"

    if [ -f "$SKILLS_DIR/latex-docs/scripts/compile_document.py" ]; then
        check_pass "compile_document.py found"

        # Check if test documents exist
        if [ -f "$SKILLS_DIR/latex-docs/test_documents/simple_test.json" ]; then
            check_pass "Test documents found"

            echo ""
            echo "  Running test compilation..."
            python3 "$SKILLS_DIR/latex-docs/scripts/compile_document.py" \
                "$SKILLS_DIR/latex-docs/test_documents/simple_test.json" \
                "/tmp/validation_test_$$.pdf" \
                general 2>&1 | grep -E "(success|error)"

            if [ -f "/tmp/validation_test_$$.pdf" ]; then
                PDF_SIZE=$(ls -lh "/tmp/validation_test_$$.pdf" | awk '{print $5}')
                check_pass "Test compilation successful (output: $PDF_SIZE)"
                rm -f "/tmp/validation_test_$$.pdf"
            else
                check_fail "Test compilation failed"
            fi
        else
            check_warn "Test documents not found (skill may not be fully installed)"
        fi
    else
        check_fail "compile_document.py not found"
    fi
else
    check_warn "latex-docs skill not installed yet"
    echo "  Install from: /tmp/latex-skills-v3.0-modular.tar.gz"
fi

if [ -d "$SKILLS_DIR/latex-content-processor" ]; then
    check_pass "latex-content-processor skill found"

    if [ -f "$SKILLS_DIR/latex-content-processor/scripts/content_processor.py" ]; then
        check_pass "content_processor.py found"
    else
        check_fail "content_processor.py not found"
    fi
else
    check_warn "latex-content-processor skill not installed yet"
fi
echo ""

# Summary
echo "=========================================="
echo "Validation Summary"
echo "=========================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Infrastructure is ready for LaTeX skills deployment."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS WARNING(S)${NC}"
    echo ""
    echo "Infrastructure is mostly ready. Review warnings above."
    exit 0
else
    echo -e "${RED}✗ $ERRORS ERROR(S), $WARNINGS WARNING(S)${NC}"
    echo ""
    echo "Infrastructure has issues that must be resolved before deployment."
    echo "Review failed checks above and install missing prerequisites."
    exit 1
fi
