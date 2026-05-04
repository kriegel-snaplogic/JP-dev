---
name: latex-content-processor
description: Internal content processor for LaTeX document generation. Converts markdown-like syntax with special tags ([TABLE:...], [IMAGE:...], [BOX:...]) into proper LaTeX commands. Not user-facing - used internally by latex-docs skill.
required_tools: []
---

# LaTeX Content Processor

**Internal Processing Module for LaTeX Document Generation**

This skill provides content processing functionality for converting markdown-like content with special tags into LaTeX commands. It is designed as an internal component used by the `latex-docs` skill and is not intended for direct user invocation.

## Purpose

The content processor handles the complex transformation pipeline that converts user-friendly markup syntax into proper LaTeX commands. This includes:

- Table rendering (7 styles with various emphasis options)
- Image extraction and figure environment generation
- Highlight boxes (info, success, warning, note)
- KPI boxes (4-per-row layout)
- Feature boxes (3-per-row layout)
- Multi-level list processing (bullet and numbered, 4 levels deep)
- Markdown formatting (**bold**, *italic*)
- Cross-reference management
- LaTeX special character escaping

## Architecture

### Processing Pipeline

Content flows through a 15-step pipeline:

1. Clean HTML/markdown artifacts (`<br/>` → `\\\\`)
2. Extract images ([IMAGE:...] → placeholders)
3. Process highlight boxes ([BOX:...], [KPI:...], [FEATURE:...])
4. Process tables ([TABLE:...])
5. Process lists (bullet/numbered)
6. Process markdown headers (###)
7. Process markdown formatting (**bold**, *italic*)
8. Extract cross-references (Table 3 → @TABREF:3@)
9. Escape LaTeX special characters
10. Restore markdown formatting
11. Restore lists
12. Restore markdown headers
13. Restore tables (convert placeholders to LaTeX tabular environments)
14. Restore boxes
15. Restore images (convert placeholders to LaTeX figure environments)
16. Restore cross-references (@TABREF:3@ → \\ref{tab:label})

The extraction-then-restoration pattern protects content from being mangled by LaTeX escaping.

### API Contract

**Input**: `ProcessingContext`
```python
@dataclass
class ProcessingContext:
    content: str  # Raw markdown with [TABLE:...] tags
    doc_type: str  # "general" | "technical" | "internal"
    brand_colors: Dict[str, str]  # {"navy": "#003087", ...}
    
    # State for placeholder management
    image_counter: int
    table_counter: int
    global_image_map: Dict[str, Any]
    table_registry: Dict[str, Tuple[int, str]]
```

**Output**: `ProcessingResult`
```python
@dataclass
class ProcessingResult:
    processed_content: str  # LaTeX-ready content
    image_map: Dict[str, Any]  # Updated image placeholders
    updated_image_counter: int
    updated_table_counter: int
```

### Usage Example

```python
from latex_content_processor import ContentProcessor, ProcessingContext

processor = ContentProcessor()

context = ProcessingContext(
    content="[TABLE:simple:Test]\\n| A | B |\\n|---|---|\\n| 1 | 2 |\\n[/TABLE]",
    doc_type="general",
    brand_colors=LATEX_COLORS,
    image_counter=0,
    table_counter=0,
    global_image_map={},
    table_registry={}
)

result = processor.process_content(context)
# result.processed_content contains LaTeX tabular environment
# result.updated_table_counter == 1
```

## Supported Features

### Table Styles

- **simple**: Navy header, alternating white/gray rows
- **minimal**: No colors, booktabs lines only
- **accent-blue/jade/orange/navy**: Colored header with zebra striping
- **bordered**: All cells bordered
- **status-colors**: Row-based coloring (red/yellow/green)

### Table Emphasis

- **first-bold**: Bold first column
- **total-row**: Bold last row
- **last-jade/orange/blue**: Highlight last column
- **widths=x,y,z**: Manual column width ratios

### Box Types

- **[BOX:info]...**: Blue info box
- **[BOX:success]...**: Green success box
- **[BOX:warning]...**: Orange warning box
- **[BOX:note]...**: Navy note box
- **[KPI:color|title|value]**: Compact metric box (4-per-row)
- **[FEATURE:color|title]content**: Feature highlight (3-per-row)
- **[BADGE:color|text]**: Inline badge

### Cross-References

Automatic conversion:
- "Table 3" → `\\ref{tab:label}` (if label exists)
- "Figure 2" → `\\ref{fig:label}`
- "Section 4.2" → `\\ref{sec:4.2}`

## Internal Use Only

This skill is **not intended for direct user invocation**. It is called internally by `latex-docs` as part of the document compilation pipeline.

Users should interact with `latex-docs`, which orchestrates manifest resolution, asset management, and PDF compilation, calling this processor internally for content transformation.

## Testing

Unit tests cover:
- Table rendering (7 styles × 3 emphasis = 21 tests)
- Image extraction (6 tests)
- Box rendering (8 tests)
- List processing (8 tests)
- Markdown formatting (4 tests)
- Cross-reference system (6 tests)

Target: 70% code coverage

## Maintenance

When adding new features:
1. **New table style**: Add to `_restore_tables()` style detection
2. **New box type**: Add to `_process_highlight_boxes()` and `_restore_boxes()`
3. **New emphasis**: Extend table rendering logic in `_restore_tables()`

The 500-line `_restore_tables()` method is the most complex component, handling 7 table styles with various column configurations and emphasis options.

## Dependencies

- Python 3.7+
- No external packages (uses only stdlib: `re`, `typing`, `dataclasses`)

## See Also

- `latex-docs`: Primary skill that uses this processor
- `doc-quality-advisor`: Pre-compilation validation
- `brand_config.py`: Brand color definitions (LATEX_COLORS)
