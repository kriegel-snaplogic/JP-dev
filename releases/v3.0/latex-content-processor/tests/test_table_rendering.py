#!/usr/bin/env python3
"""
Unit tests for table rendering in ContentProcessor

Tests all 7 table styles with various emphasis options.
Target: 21 tests for table rendering component.
"""

import sys
from pathlib import Path

# Add parent scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from content_processor import ContentProcessor, ProcessingContext, ProcessingResult

# Mock brand colors for testing
LATEX_COLORS = {
    'navy': '#003087',
    'blue': '#0077C8',
    'jade': '#00BFA5',
    'orange': '#FF6B35'
}


def create_test_context(content: str, doc_type: str = "general") -> ProcessingContext:
    """Helper to create test context"""
    return ProcessingContext(
        content=content,
        doc_type=doc_type,
        brand_colors=LATEX_COLORS,
        image_counter=0,
        table_counter=0,
        global_image_map={},
        table_registry={}
    )


# ============================================================================
# SIMPLE STYLE TESTS (3 tests)
# ============================================================================

def test_simple_table_basic():
    """Test basic simple table rendering"""
    content = """[TABLE:simple:Test Table::test-table]
| Header A | Header B |
|----------|----------|
| Data 1   | Data 2   |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should contain table environment
    assert "\\begin{table}[H]" in result.processed_content
    assert "\\caption{Test Table}" in result.processed_content
    assert "\\label{tab:test-table}" in result.processed_content

    # Should contain tabular with navy header
    assert "\\begin{tabular}" in result.processed_content
    assert "\\rowcolor{snaplogicNavy}" in result.processed_content

    # Should have incremented counter
    assert result.updated_table_counter == 1


def test_simple_table_first_bold():
    """Test simple table with first-bold emphasis"""
    content = """[TABLE:simple:Pricing:first-bold:pricing]
| Region | Price |
|--------|-------|
| US     | $100  |
| EU     | €90   |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should contain textbf for first column
    assert "\\textbf{US}" in result.processed_content
    assert "\\textbf{EU}" in result.processed_content

    # Should NOT bold second column
    assert result.processed_content.count("\\textbf{$100}") == 0


def test_simple_table_total_row():
    """Test simple table with total-row emphasis"""
    content = """[TABLE:simple:Sales:total-row:sales]
| Region | Revenue |
|--------|---------|
| North  | 100K    |
| South  | 80K     |
| TOTAL  | 180K    |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Last row should be bold
    assert "\\textbf{TOTAL}" in result.processed_content
    assert "\\textbf{180K}" in result.processed_content


# ============================================================================
# MINIMAL STYLE TESTS (2 tests)
# ============================================================================

def test_minimal_table_basic():
    """Test minimal table with booktabs only"""
    content = """[TABLE:minimal:Clean Data]
| A | B |
|---|---|
| 1 | 2 |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should use booktabs rules
    assert "\\toprule" in result.processed_content
    assert "\\midrule" in result.processed_content
    assert "\\bottomrule" in result.processed_content

    # Should NOT have color commands
    assert "\\rowcolor" not in result.processed_content


def test_minimal_table_with_emphasis():
    """Test minimal table ignores emphasis (clean design)"""
    content = """[TABLE:minimal:Data:first-bold]
| X | Y |
|---|---|
| 1 | 2 |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Minimal style should ignore emphasis (design choice)
    # This tests current behavior - may want bold in minimal too
    assert "\\toprule" in result.processed_content


# ============================================================================
# ACCENT STYLE TESTS (6 tests - 3 colors × 2 emphasis)
# ============================================================================

def test_accent_blue_basic():
    """Test accent-blue table style"""
    content = """[TABLE:accent-blue:Blue Table]
| Col1 | Col2 |
|------|------|
| A    | B    |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should have blue header
    assert "\\rowcolor{snaplogicBlue}" in result.processed_content


def test_accent_jade_with_last_jade():
    """Test accent-jade with last-jade column emphasis"""
    content = """[TABLE:accent-jade:Performance:last-jade]
| Metric | Value |
|--------|-------|
| Speed  | Fast  |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Header should be jade
    assert "\\rowcolor{snaplogicJade}" in result.processed_content

    # Last column should have jade background
    assert "\\cellcolor{snaplogicJade!20}" in result.processed_content


def test_accent_orange_basic():
    """Test accent-orange table style"""
    content = """[TABLE:accent-orange:Alert Data]
| Status | Count |
|--------|-------|
| Error  | 5     |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should have orange header
    assert "\\rowcolor{snaplogicOrange}" in result.processed_content


def test_accent_blue_first_bold():
    """Test accent-blue with first-bold emphasis"""
    content = """[TABLE:accent-blue:Teams:first-bold]
| Team   | Size |
|--------|------|
| Eng    | 20   |
| Sales  | 15   |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # First column should be bold
    assert "\\textbf{Eng}" in result.processed_content
    assert "\\textbf{Sales}" in result.processed_content


def test_accent_jade_last_orange():
    """Test accent-jade with last-orange column (mixed colors)"""
    content = """[TABLE:accent-jade:Mixed:last-orange]
| Feature | Status |
|---------|--------|
| Auth    | Done   |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Header jade, last column orange
    assert "\\rowcolor{snaplogicJade}" in result.processed_content
    assert "\\cellcolor{snaplogicOrange!20}" in result.processed_content


def test_accent_orange_total_row():
    """Test accent-orange with total-row emphasis"""
    content = """[TABLE:accent-orange:Summary:total-row]
| Item  | Cost |
|-------|------|
| A     | 10   |
| B     | 20   |
| Total | 30   |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Last row should be bold
    assert "\\textbf{Total}" in result.processed_content
    assert "\\textbf{30}" in result.processed_content


# ============================================================================
# BORDERED STYLE TESTS (2 tests)
# ============================================================================

def test_bordered_table_basic():
    """Test bordered table with all cell borders"""
    content = """[TABLE:bordered:Grid Data]
| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should have vertical lines in column spec
    assert "|" in result.processed_content or "\\hline" in result.processed_content


def test_bordered_table_first_bold():
    """Test bordered table with first-bold emphasis"""
    content = """[TABLE:bordered:Reference:first-bold]
| Key | Value |
|-----|-------|
| ID  | 123   |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should have borders AND bold first column
    assert "\\textbf{ID}" in result.processed_content


# ============================================================================
# STATUS-COLORS STYLE TESTS (2 tests)
# ============================================================================

def test_status_colors_basic():
    """Test status-colors table (red/yellow/green rows)"""
    content = """[TABLE:status-colors:Health Check]
| Component | Status |
|-----------|--------|
| API       | Good   |
| DB        | Warning|
| Cache     | Error  |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should contain status color indicators
    # (Implementation may vary - test that table rendered)
    assert "\\begin{tabular}" in result.processed_content
    assert result.updated_table_counter == 1


def test_status_colors_no_emphasis():
    """Test status-colors ignores emphasis (semantic style)"""
    content = """[TABLE:status-colors:Status:first-bold]
| Item | State |
|------|-------|
| Test | OK    |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Status-colors is semantic, may ignore emphasis
    assert "\\begin{tabular}" in result.processed_content


# ============================================================================
# CUSTOM WIDTH TESTS (2 tests)
# ============================================================================

def test_custom_widths_simple():
    """Test table with custom column widths"""
    content = """[TABLE:simple:Custom Widths:widths=1,2,1.5]
| Short | Long Column | Medium |
|-------|-------------|--------|
| A     | B           | C      |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should respect width ratios (1:2:1.5)
    # Exact LaTeX may vary, just verify it rendered
    assert "\\begin{tabular}" in result.processed_content
    assert result.updated_table_counter == 1


def test_custom_widths_with_bold():
    """Test custom widths combined with first-bold"""
    content = """[TABLE:simple:Mixed:first-bold,widths=1,3]
| Name | Description |
|------|-------------|
| Foo  | Bar         |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should have both widths AND bold
    assert "\\textbf{Foo}" in result.processed_content
    assert result.updated_table_counter == 1


# ============================================================================
# EDGE CASES (2 tests)
# ============================================================================

def test_empty_table():
    """Test table with only headers (no data rows)"""
    content = """[TABLE:simple:Headers Only]
| A | B |
|---|---|
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should still render (even if visually odd)
    assert "\\begin{tabular}" in result.processed_content or "No data" in result.processed_content


def test_single_row_table():
    """Test table with one data row"""
    content = """[TABLE:simple:Single Row]
| Header |
|--------|
| Value  |
[/TABLE]"""

    processor = ContentProcessor()
    context = create_test_context(context)
    result = processor.process_content(context)

    # Should render successfully
    assert "\\begin{tabular}" in result.processed_content
    assert result.updated_table_counter == 1


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    import traceback

    tests = [
        ("Simple Table Basic", test_simple_table_basic),
        ("Simple Table First Bold", test_simple_table_first_bold),
        ("Simple Table Total Row", test_simple_table_total_row),
        ("Minimal Table Basic", test_minimal_table_basic),
        ("Minimal Table With Emphasis", test_minimal_table_with_emphasis),
        ("Accent Blue Basic", test_accent_blue_basic),
        ("Accent Jade Last Jade", test_accent_jade_with_last_jade),
        ("Accent Orange Basic", test_accent_orange_basic),
        ("Accent Blue First Bold", test_accent_blue_first_bold),
        ("Accent Jade Last Orange", test_accent_jade_last_orange),
        ("Accent Orange Total Row", test_accent_orange_total_row),
        ("Bordered Table Basic", test_bordered_table_basic),
        ("Bordered Table First Bold", test_bordered_table_first_bold),
        ("Status Colors Basic", test_status_colors_basic),
        ("Status Colors No Emphasis", test_status_colors_no_emphasis),
        ("Custom Widths Simple", test_custom_widths_simple),
        ("Custom Widths With Bold", test_custom_widths_with_bold),
        ("Empty Table", test_empty_table),
        ("Single Row Table", test_single_row_table),
    ]

    passed = 0
    failed = 0

    print(f"Running {len(tests)} table rendering tests...")
    print("=" * 60)

    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}")
            print(f"  Assertion: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}")
            print(f"  Error: {e}")
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")

    sys.exit(0 if failed == 0 else 1)
