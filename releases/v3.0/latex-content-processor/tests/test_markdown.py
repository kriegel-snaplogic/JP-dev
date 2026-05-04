#!/usr/bin/env python3
"""
Unit tests for markdown formatting in ContentProcessor

Tests bold, italic, and combined formatting.
Target: 4 tests for markdown component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from content_processor import ContentProcessor, ProcessingContext

LATEX_COLORS = {'navy': '#003087', 'blue': '#0077C8', 'jade': '#00BFA5', 'orange': '#FF6B35'}


def create_test_context(content: str) -> ProcessingContext:
    return ProcessingContext(content=content, doc_type="general", brand_colors=LATEX_COLORS,
                           image_counter=0, table_counter=0, global_image_map={}, table_registry={})


def test_bold_formatting():
    """Test bold markdown conversion"""
    content = "This is **bold text** in a sentence."
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\textbf{bold text}" in result.processed_content
    assert "in a sentence" in result.processed_content


def test_italic_formatting():
    """Test italic markdown conversion"""
    content = "This is *italic text* in a sentence."
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\textit{italic text}" in result.processed_content


def test_combined_formatting():
    """Test bold and italic together"""
    content = "We have **bold** and *italic* and **more bold**."
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\textbf{bold}" in result.processed_content
    assert "\\textit{italic}" in result.processed_content
    assert "\\textbf{more bold}" in result.processed_content


def test_nested_bold_italic():
    """Test nested bold and italic"""
    content = "This is **bold with *italic* inside** text."
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    # Should handle nested formatting (exact output may vary)
    assert "\\textbf{" in result.processed_content
    assert "\\textit{" in result.processed_content


if __name__ == "__main__":
    tests = [
        ("Bold Formatting", test_bold_formatting),
        ("Italic Formatting", test_italic_formatting),
        ("Combined Formatting", test_combined_formatting),
        ("Nested Bold Italic", test_nested_bold_italic),
    ]

    passed = failed = 0
    print(f"Running {len(tests)} markdown formatting tests...")
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
