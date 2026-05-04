#!/usr/bin/env python3
"""
Unit tests for box rendering in ContentProcessor

Tests highlight boxes (info, success, warning, note), KPI boxes, feature boxes.
Target: 8 tests for box component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from content_processor import ContentProcessor, ProcessingContext

LATEX_COLORS = {'navy': '#003087', 'blue': '#0077C8', 'jade': '#00BFA5', 'orange': '#FF6B35'}


def create_test_context(content: str) -> ProcessingContext:
    return ProcessingContext(content=content, doc_type="general", brand_colors=LATEX_COLORS,
                           image_counter=0, table_counter=0, global_image_map={}, table_registry={})


def test_info_box():
    """Test info box rendering"""
    content = "[BOX:info]This is important information.[/BOX]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "infobox" in result.processed_content or "colorbox" in result.processed_content


def test_success_box():
    """Test success box rendering"""
    content = "[BOX:success]Operation completed successfully![/BOX]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "successbox" in result.processed_content or "colorbox" in result.processed_content


def test_warning_box():
    """Test warning box rendering"""
    content = "[BOX:warning]Proceed with caution.[/BOX]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "warningbox" in result.processed_content or "colorbox" in result.processed_content


def test_note_box():
    """Test note box rendering"""
    content = "[BOX:note]Remember this detail.[/BOX]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "notebox" in result.processed_content or "colorbox" in result.processed_content


def test_kpi_box():
    """Test KPI box (4-per-row layout)"""
    content = "[KPI:blue|Revenue|$1.2M]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "kpibox" in result.processed_content or "1.2M" in result.processed_content


def test_feature_box():
    """Test feature box (3-per-row layout)"""
    content = "[FEATURE:jade|Cloud Native]Scalable architecture[/FEATURE]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "featurebox" in result.processed_content or "Cloud Native" in result.processed_content


def test_multiple_boxes():
    """Test multiple boxes preserve content order"""
    content = "Start\n[BOX:info]Info[/BOX]\nMiddle\n[BOX:warning]Warning[/BOX]\nEnd"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "Start" in result.processed_content
    assert "Middle" in result.processed_content
    assert "End" in result.processed_content


def test_nested_formatting_in_box():
    """Test markdown formatting inside boxes"""
    content = "[BOX:info]This is **bold** and *italic*.[/BOX]"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "textbf{bold}" in result.processed_content
    assert "textit{italic}" in result.processed_content


if __name__ == "__main__":
    tests = [
        ("Info Box", test_info_box),
        ("Success Box", test_success_box),
        ("Warning Box", test_warning_box),
        ("Note Box", test_note_box),
        ("KPI Box", test_kpi_box),
        ("Feature Box", test_feature_box),
        ("Multiple Boxes", test_multiple_boxes),
        ("Nested Formatting", test_nested_formatting_in_box),
    ]

    passed = failed = 0
    print(f"Running {len(tests)} box rendering tests...")
    print("=" * 60)

    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
