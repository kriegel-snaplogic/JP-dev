# Architecture: 3-Skill Document Generation System

**Last Updated:** 2026-05-04  
**Migration Status:** Phase 3 Complete (Modular architecture live)

## Overview

The LaTeX document generation system has been refactored from a monolithic 2,185-line script into a modular 3-skill architecture. This improves maintainability, testability, and enables reuse of formatting logic across different document generation tools.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                            │
│                    "Generate RFP document"                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ├── Optional: Pre-validation
                             │
                    ┌────────▼────────┐
                    │ doc-quality-    │
                    │    advisor      │ (Standalone skill)
                    │                 │
                    │ • JSON validation│
                    │ • Quality scoring│
                    │ • Issue detection│
                    └────────┬────────┘
                             │
                             │ Quality gate: ≥85 for customer docs
                             │
                    ┌────────▼────────┐
                    │   latex-docs    │ (Orchestrator)
                    │                 │
                    │ • Manifest res. │
                    │ • LaTeX template│
                    │ • Asset mgmt    │
                    │ • PDF compile   │
                    └────────┬────────┘
                             │
                             │ Internal API call
                             │
              ┌──────────────▼──────────────┐
              │ latex-content-processor     │ (Format Handler)
              │                             │
              │ • Table rendering (7 styles)│
              │ • Image extraction          │
              │ • Box formatting (8 types)  │
              │ • List processing           │
              │ • Markdown → LaTeX          │
              │ • Cross-reference system    │
              │ • LaTeX escaping            │
              └──────────────┬──────────────┘
                             │
                             │ LaTeX code
                             │
                    ┌────────▼────────┐
                    │    pdflatex     │
                    │   (3 passes)    │
                    └────────┬────────┘
                             │
                             ▼
                       PDF OUTPUT
```

## Skills

### 1. latex-docs (Orchestrator & Compiler)

**Purpose:** User-facing entry point for all document generation.

**Responsibilities:**
- Manifest resolution and variable substitution
- JSON structure validation
- LaTeX template generation (preamble, title page, sections)
- Asset management (logo/image copying)
- PDF compilation via pdflatex (3 passes for TOC/cross-refs)
- Error handling and work directory management

**Size:** 899 lines (down from 2,185)

**Key Methods:**
- `compile(input_json, output_pdf, doc_type, options)` - Main entry point
- `_resolve_manifest(manifest_path)` - Multi-file document assembly
- `_generate_latex(structure, doc_type)` - LaTeX document generation
- `_generate_title_page(structure, style)` - Brand-specific title pages
- `_generate_main_content(sections)` - Delegates to ContentProcessor
- `_copy_assets(work_dir, structure)` - Image/logo management
- `_compile_latex(work_dir)` - pdflatex invocation

**Input:** JSON document structure or manifest file  
**Output:** PDF file + metadata (pages, version, status)

**Dependencies:**
- latex-content-processor (internal API)
- pdflatex (system command)
- SnapLogic brand assets (templates/assets/)

---

### 2. latex-content-processor (Format Handler)

**Purpose:** Internal content processing for markdown-like syntax to LaTeX conversion.

**Responsibilities:**
- Extract and process special content tags ([TABLE:...], [IMAGE:...], [BOX:...])
- Convert markdown formatting to LaTeX (**bold**, *italic*)
- Process multi-level lists (bullet and numbered, 4 levels deep)
- Render tables (7 styles, 6 emphasis options, multipage support)
- Extract and restore images with proper figure environments
- Render highlight boxes (4 types: info, success, warning, note)
- Render KPI boxes (4-per-row), feature boxes (3-per-row), badge boxes
- Manage placeholder system (@TABLE:X@, @IMAGE:X@)
- Handle cross-reference extraction and restoration
- LaTeX escaping (with line break protection)

**Size:** 1,192 lines

**API Contract:**

```python
@dataclass
class ProcessingContext:
    content: str                                # Raw markdown with [TABLE:...] tags
    doc_type: str                              # "general" | "technical" | "internal"
    brand_colors: Dict[str, str]               # {"navy": "#003087", ...}
    image_counter: int                         # State for unique placeholders
    table_counter: int
    global_image_map: Dict[str, Any]
    table_registry: Dict[str, Tuple[int, str]]

@dataclass
class ProcessingResult:
    processed_content: str                     # LaTeX-ready content
    image_map: Dict[str, Any]                  # Updated image placeholders
    updated_image_counter: int
    updated_table_counter: int

def process_content(context: ProcessingContext) -> ProcessingResult
```

**Processing Pipeline (15 steps):**
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

**Why Separate Skill:**
1. **Testability** - Can unit test table rendering, box formatting independently
2. **Reusability** - Other tools (HTML generators, Markdown processors) can use formatting logic
3. **Complexity isolation** - 500-line table rendering method gets its own module
4. **Clear API boundary** - ProcessingContext/Result dataclasses define contract

**Dependencies:** None (stdlib only: re, typing, dataclasses)

---

### 3. doc-quality-advisor (Validator)

**Purpose:** Pre-compilation JSON validation and quality scoring.

**Responsibilities:**
- JSON structure validation
- Content quality scoring across 7 dimensions:
  1. Structure & Organization (20%)
  2. Content Completeness (20%)
  3. Technical Depth (15%)
  4. Formatting & Style (15%)
  5. References & Citations (10%)
  6. Consistency (10%)
  7. Document Metadata (10%)
- Issue detection (structure, formatting, content, technical, references, consistency, completeness)
- Recommendation generation
- Quality gate enforcement (≥85 for customer-facing, ≥75 for internal)

**Integration Point:** Used BEFORE latex-docs compilation

```
User creates JSON → doc-quality-advisor validates → User fixes issues → latex-docs compiles PDF
```

**Status:** No changes during migration (standalone skill)

---

## Data Flow

### Typical Document Generation Flow

1. **User creates JSON document structure**
   - Either monolithic JSON file
   - Or manifest + content blocks in content_library/

2. **Optional: Quality validation**
   ```bash
   /doc-quality-advisor path/to/document.json
   ```
   - Get quality score (0-100)
   - Review issues and recommendations
   - Fix problems before compilation

3. **Document compilation**
   ```bash
   /latex-docs compile path/to/document.json output.pdf general --font-size 10pt
   ```
   - latex-docs resolves manifest (if applicable)
   - Generates LaTeX template
   - Calls ContentProcessor for each section
   - Copies assets (logos, images)
   - Runs pdflatex (3 passes)
   - Returns PDF + metadata

4. **Content processing (internal)**
   - For each section, latex-docs creates ProcessingContext
   - Calls `ContentProcessor.process_content(context)`
   - ContentProcessor returns LaTeX-ready content
   - latex-docs assembles into final document

### Inter-Skill Communication

**latex-docs → latex-content-processor:**
- **Type:** Internal Python API call (not subprocess)
- **Method:** Direct import and method invocation
- **Path resolution:** `sys.path.insert(0, parent / 'latex-content-processor' / 'scripts')`
- **Contract:** ProcessingContext → ProcessingResult dataclasses

**doc-quality-advisor → latex-docs:**
- **Type:** Sequential workflow (manual)
- **Method:** User runs quality check, then runs compilation
- **Contract:** JSON file (no direct API call)

---

## Performance Characteristics

### Compilation Times (Baseline)

| Document Type | Pages | Tables | Images | Time (sec) |
|---------------|-------|--------|--------|------------|
| Simple test | 6 | 3 | 0 | 3-4 |
| Table styles test | 11 | 8 | 0 | 5-6 |
| Airbus RFP | 70 | 15 | 20 | 15-20 |

**Bottleneck:** pdflatex (3 passes) accounts for 90%+ of compile time

**ContentProcessor overhead:** <5% (measured before/after migration, no regression)

### Memory Usage

| Document Type | Peak Memory |
|---------------|-------------|
| Simple (6 pages) | ~100 MB |
| Medium (20 pages) | ~150 MB |
| Large (70 pages) | ~250 MB |

**Note:** LaTeX compilation is memory-intensive, especially with tables and images.

---

## Migration History

### Original Architecture (Pre-Phase 1)

**Structure:** Monolithic single-skill
- File: `compile_document.py` (2,185 lines)
- Class: `SnapLogicDocumentCompiler` (69 methods)
- Complexity: Cyclomatic complexity ~30 for table rendering

**Pain Points:**
- Hard to test (integration tests only)
- Hard to maintain (2,000-line file)
- Hard to reuse (all-or-nothing)
- Hard to extend (adding table style = navigating 500-line method)

### Phase 1: Extract ContentProcessor (Completed 2026-05-04)

**Goal:** Extract processing logic with rollback safety

**Changes:**
- Created latex-content-processor skill (1,192 lines)
- Added dual-path execution to compile_document.py
- Implemented ProcessingContext/Result dataclass API

**Validation:** Airbus RFP (70 pages) compiled identically through both paths (3,458 lines extracted, byte-for-byte identical)

### Phase 2: Enable External Processor (Completed 2026-05-04)

**Goal:** Validate new path with multiple test documents

**Changes:**
- Set `USE_EXTERNAL_PROCESSOR = True`
- Created regression test suite (3 test documents)
- Created brand_config.py for LATEX_COLORS

**Validation:**
- simple_test.json (6 pages) ✓
- table_styles_test.json (11 pages) ✓
- airbus_rfp_v3_test.json (70 pages) ✓
- Performance: Within ±5% baseline
- Zero regressions detected

### Phase 3: Remove Duplicate Code (Completed 2026-05-04)

**Goal:** Delete old processing methods, finalize architecture

**Changes:**
- Deleted 1,286 lines of duplicate code (58.9% reduction)
- Removed `USE_EXTERNAL_PROCESSOR` flag
- Removed 16 old processing methods
- Kept essential utilities (_escape_latex, _copy_assets, _compile_latex)

**Validation:**
- simple_test: 6 pages ✓
- airbus_rfp_v3_test: 70 pages ✓
- compile_document.py: 2,185 → 899 lines

**Result:** 3-skill architecture fully operational

### Phase 4: Documentation (Current)

**Goal:** Document architecture for future maintainers

**Deliverables:**
- ARCHITECTURE.md (this file)
- MIGRATION_NOTES.md (migration details)
- Updated test_documents/README.md

---

## Maintenance Guide

### Adding a New Table Style

**Before (Monolithic):**
1. Navigate 2,185-line file
2. Find `_restore_tables()` method (500 lines)
3. Add style detection logic
4. Add LaTeX generation code
5. Test entire document generation pipeline
6. **Time:** 45 minutes

**After (Modular):**
1. Open `latex-content-processor/scripts/content_processor.py`
2. Find `_restore_tables()` method (500 lines, but isolated)
3. Add style detection logic
4. Add LaTeX generation code
5. Write unit test for new style
6. Test only ContentProcessor (faster feedback)
7. **Time:** 20 minutes

**Example:**
```python
# In _restore_tables() method
elif style == 'accent-purple':  # New style
    # Define color
    header_color = 'snapPurple'
    # Generate header row
    headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
    latex.append(f'\\rowcolor{{{header_color}}}{" & ".join(headers)} \\\\')
```

### Adding a New Box Type

**Location:** `latex-content-processor/scripts/content_processor.py`

**Steps:**
1. Add tag detection in `_process_highlight_boxes()`
2. Add LaTeX generation in `_restore_boxes()`
3. Define color/style in brand_config.py (if needed)
4. Write unit test
5. **Time:** 15 minutes

**Example:**
```python
# In _process_highlight_boxes()
text = re.sub(r'\[BOX:danger\](.*?)\[/BOX\]', r'@DANGERBOX:\1@', text, flags=re.DOTALL)

# In _restore_boxes()
elif match_type == 'danger':
    latex_box = f'\\begin{{dangerbox}}\n{content}\n\\end{{dangerbox}}'
```

### Modifying Table Rendering Logic

**Critical Method:** `_restore_tables()` in ContentProcessor (500 lines)

**Cyclomatic Complexity:** ~30 (high, but isolated)

**Testing Strategy:**
1. Write unit test for specific case
2. Modify rendering logic
3. Run unit tests (fast feedback)
4. Run integration test (full document)

**Known Complexity Areas:**
- Column width calculation (auto vs manual)
- Emphasis options (first-bold, last-jade, total-row combinations)
- Multipage table handling (longtable vs table)
- Category headers (ALL CAPS detection)

### Debugging Compilation Failures

**Step 1: Check LaTeX error output**
```bash
# Error preserved in work_dir
cat /tmp/snaplogic_doc_xyz/document.log
```

**Step 2: Inspect generated LaTeX**
```bash
cat /tmp/snaplogic_doc_xyz/document.tex
```

**Step 3: Identify problem section**
- Search for malformed tags: `[TABLE:` without matching `[/TABLE]`
- Check special character escaping: `&`, `%`, `$`, `#`, `_`
- Verify image paths exist

**Step 4: Test ContentProcessor in isolation**
```python
from content_processor import ContentProcessor, ProcessingContext

context = ProcessingContext(
    content="[TABLE:simple:Test]...",
    doc_type="general",
    brand_colors=LATEX_COLORS,
    image_counter=0,
    table_counter=0,
    global_image_map={},
    table_registry={}
)

processor = ContentProcessor()
result = processor.process_content(context)
print(result.processed_content)
```

---

## Future Enhancements

### Potential Improvements

1. **HTML Output Backend**
   - Reuse ContentProcessor for HTML generation
   - New skill: `html-content-processor` (similar API)
   - Same JSON input → HTML instead of LaTeX

2. **Real-time Preview**
   - Watch JSON file for changes
   - Auto-recompile on save
   - PDF viewer auto-refresh

3. **Template System**
   - User-defined document templates
   - Custom table styles without code changes
   - Template marketplace?

4. **Performance Optimization**
   - Cache intermediate LaTeX for unchanged sections
   - Parallel processing for independent sections
   - Incremental compilation (only changed sections)

5. **Enhanced Testing**
   - Visual regression testing (PDF screenshots)
   - Property-based testing for ContentProcessor
   - Performance benchmarking in CI

### Design Principles for Future Changes

1. **Keep skills focused** - Each skill should do one thing well
2. **Use dataclasses for APIs** - Clear contracts, easy to evolve
3. **Favor composition over inheritance** - Skills call other skills via APIs
4. **Test at multiple levels** - Unit tests for logic, integration tests for workflows
5. **Document the WHY** - Explain decisions, not just implementation

---

## Support & Resources

### Key Files

| File | Purpose | Lines |
|------|---------|-------|
| latex-docs/scripts/compile_document.py | Orchestrator & compiler | 899 |
| latex-content-processor/scripts/content_processor.py | Format handler | 1,192 |
| latex-docs/SKILL.md | User documentation | ~800 |
| latex-content-processor/SKILL.md | Internal documentation | 793 |
| latex-docs/test_documents/ | Test suite & regression tests | - |

### Contact

For questions or issues related to this architecture:
- Migration lead: Jean-Claude (Advisor to the CEO, field CTO-like, reason SnapLogic functions)
- Documentation: This file + MIGRATION_NOTES.md
- Test suite: test_documents/README.md

---

**Last Updated:** 2026-05-04  
**Architecture Version:** 3.0 (Modular, Post-Migration)
