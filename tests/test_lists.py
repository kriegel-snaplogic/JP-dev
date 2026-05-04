#!/usr/bin/env python3
"""
Unit tests for list processing in ContentProcessor

Tests bullet and numbered lists up to 4 levels deep.
Target: 8 tests for list component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from content_processor import ContentProcessor, ProcessingContext

LATEX_COLORS = {'navy': '#003087', 'blue': '#0077C8', 'jade': '#00BFA5', 'orange': '#FF6B35'}


def create_test_context(content: str) -> ProcessingContext:
    return ProcessingContext(content=content, doc_type="general", brand_colors=LATEX_COLORS,
                           image_counter=0, table_counter=0, global_image_map={}, table_registry={})


def test_simple_bullet_list():
    """Test basic bullet list"""
    content = "- Item 1\n- Item 2\n- Item 3"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\begin{itemize}" in result.processed_content
    assert "\\item Item 1" in result.processed_content
    assert "\\end{itemize}" in result.processed_content


def test_nested_bullet_list():
    """Test 2-level nested bullet list"""
    content = "- Level 1\n   - Level 2a\n   - Level 2b\n- Level 1 again"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert result.processed_content.count("\\begin{itemize}") == 2
    assert result.processed_content.count("\\end{itemize}") == 2


def test_simple_numbered_list():
    """Test basic numbered list"""
    content = "1. First\n2. Second\n3. Third"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\begin{enumerate}" in result.processed_content
    assert "\\item First" in result.processed_content
    assert "\\end{enumerate}" in result.processed_content


def test_nested_numbered_list():
    """Test 2-level nested numbered list"""
    content = "1. Main\n   1. Sub A\n   2. Sub B\n2. Main again"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert result.processed_content.count("\\begin{enumerate}") == 2


def test_mixed_list():
    """Test bullet list with numbered sublist"""
    content = "- Bullet\n   1. Numbered sub\n   2. Another\n- Bullet again"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\begin{itemize}" in result.processed_content
    assert "\\begin{enumerate}" in result.processed_content


def test_deep_nesting():
    """Test 4-level nested list"""
    content = "- L1\n   - L2\n      - L3\n         - L4"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert result.processed_content.count("\\begin{itemize}") == 4


def test_bold_labels_in_list():
    """Test bold labels in list items"""
    content = "- **Key Point:** This is important\n- **Another:** Also important"
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "\\textbf{Key Point:}" in result.processed_content
    assert "\\textbf{Another:}" in result.processed_content


def test_list_with_text_before_after():
    """Test list preserves surrounding text"""
    content = "Before list.\n\n- Item 1\n- Item 2\n\nAfter list."
    processor = ContentProcessor()
    result = processor.process_content(create_test_context(content))
    assert "Before list" in result.processed_content
    assert "After list" in result.processed_content
    assert "\\begin{itemize}" in result.processed_content


if __name__ == "__main__":
    tests = [
        ("Simple Bullet List", test_simple_bullet_list),
        ("Nested Bullet List", test_nested_bullet_list),
        ("Simple Numbered List", test_simple_numbered_list),
        ("Nested Numbered List", test_nested_numbered_list),
        ("Mixed List", test_mixed_list),
        ("Deep Nesting", test_deep_nesting),
        ("Bold Labels", test_bold_labels_in_list),
        ("List With Surrounding Text", test_list_with_text_before_after),
    ]

    passed = failed = 0
    print(f"Running {len(tests)} list processing tests...")
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
