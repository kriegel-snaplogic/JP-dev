#!/usr/bin/env python3
"""
Unit tests for image extraction and restoration in ContentProcessor

Tests image placeholder system, figure environment generation, and label handling.
Target: 6 tests for image processing component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from content_processor import ContentProcessor, ProcessingContext

LATEX_COLORS = {
    'navy': '#003087',
    'blue': '#0077C8',
    'jade': '#00BFA5',
    'orange': '#FF6B35'
}


def create_test_context(content: str) -> ProcessingContext:
    """Helper to create test context"""
    return ProcessingContext(
        content=content,
        doc_type="general",
        brand_colors=LATEX_COLORS,
        image_counter=0,
        table_counter=0,
        global_image_map={},
        table_registry={}
    )


def test_basic_image():
    """Test basic image extraction and figure generation"""
    content = "[IMAGE:diagram.png:System Architecture:0.8:arch]"

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should generate figure environment
    assert "\\begin{figure}[H]" in result.processed_content
    assert "\\includegraphics[width=0.8\\linewidth]{diagram.png}" in result.processed_content
    assert "\\caption{System Architecture}" in result.processed_content
    assert "\\label{fig:arch}" in result.processed_content
    assert "\\end{figure}" in result.processed_content

    # Should increment counter
    assert result.updated_image_counter == 1


def test_image_no_caption():
    """Test image with underscore (no caption)"""
    content = "[IMAGE:logo.png:_:0.5]"

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should NOT have caption or label
    assert "\\caption" not in result.processed_content
    assert "\\label" not in result.processed_content

    # Should still have figure and image
    assert "\\includegraphics[width=0.5\\linewidth]{logo.png}" in result.processed_content
    assert result.updated_image_counter == 1


def test_image_default_width():
    """Test image with default width (1.0 = full width)"""
    content = "[IMAGE:chart.jpg:Performance Chart::perf-chart]"

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should use default width (1.0)
    assert "\\includegraphics[width=1.0\\linewidth]{chart.jpg}" in result.processed_content
    assert "\\caption{Performance Chart}" in result.processed_content
    assert "\\label{fig:perf-chart}" in result.processed_content


def test_multiple_images():
    """Test multiple images increment counter correctly"""
    content = """
Some text before.

[IMAGE:img1.png:First Image:0.6:img1]

Middle text.

[IMAGE:img2.png:Second Image:0.8:img2]

End text.
"""

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should have both figures
    assert "\\includegraphics[width=0.6\\linewidth]{img1.png}" in result.processed_content
    assert "\\includegraphics[width=0.8\\linewidth]{img2.png}" in result.processed_content

    # Should have both captions
    assert "\\caption{First Image}" in result.processed_content
    assert "\\caption{Second Image}" in result.processed_content

    # Counter should be 2
    assert result.updated_image_counter == 2

    # Text should be preserved
    assert "Some text before" in result.processed_content
    assert "Middle text" in result.processed_content
    assert "End text" in result.processed_content


def test_image_with_path():
    """Test image with full path"""
    content = "[IMAGE:/tmp/assets/diagram.png:Architecture:0.7:arch-diag]"

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Should preserve full path
    assert "\\includegraphics[width=0.7\\linewidth]{/tmp/assets/diagram.png}" in result.processed_content
    assert "\\label{fig:arch-diag}" in result.processed_content


def test_image_escaping():
    """Test image with special characters in caption"""
    content = "[IMAGE:test.png:Cost & Performance Analysis (Q1):0.8]"

    processor = ContentProcessor()
    context = create_test_context(content)
    result = processor.process_content(context)

    # Caption should have escaped special chars
    assert "\\&" in result.processed_content  # & escaped
    # Parentheses are OK in LaTeX, shouldn't be escaped


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    import traceback

    tests = [
        ("Basic Image", test_basic_image),
        ("Image No Caption", test_image_no_caption),
        ("Image Default Width", test_image_default_width),
        ("Multiple Images", test_multiple_images),
        ("Image With Path", test_image_with_path),
        ("Image Escaping", test_image_escaping),
    ]

    passed = 0
    failed = 0

    print(f"Running {len(tests)} image extraction tests...")
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
