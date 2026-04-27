# LaTeX Document Generation - Changelog

## 2026-04-27 - Table Formatting & Professional Headers/Footers

### Major Features Added

#### 1. List of Figures (LOF) and List of Tables (LOT) ✅
- Automatically generated when document contains captioned images or tables
- Appears after Table of Contents (TOC → LOF → LOT sequence)
- Uses LaTeX `\listoffigures` and `\listoftables` commands
- Clickable entries with page numbers

#### 2. Cross-Reference System ✅
**Figure References:**
- Syntax: "Figure N" in text automatically becomes clickable hyperlink
- Implementation: `Figure~\ref{fig:N}` (non-breaking space prevents line breaks)
- All figures get automatic `\label{fig:N}` labels
- Requires two LaTeX compilation passes to resolve (handled automatically)

**Table References:**
- Syntax: "Table N" in text automatically becomes clickable hyperlink  
- Implementation: `Table~\ref{tab:N}`
- All tables get automatic `\label{tab:N}` labels

**Section References:**
- Syntax: "Section X.Y.Z" in text automatically becomes clickable hyperlink
- Implementation: `Section~\ref{sec:X.Y.Z}`
- Supports multi-level section numbering

**Processing Pipeline:**
```
Extract to placeholders → Escape LaTeX → Restore with \ref{}
  @FIGREF:N@                              Figure~\ref{fig:N}
  @TABREF:N@                              Table~\ref{tab:N}
  @SECREF:X.Y@                            Section~\ref{sec:X.Y}
```

#### 3. Table Numbering and Captioning ✅
- All tables automatically numbered (Table 1, Table 2, etc.)
- Syntax: `[TABLE:style:caption]...[/TABLE]`
- Caption appears ABOVE table (professional standard)
- Empty caption `_` still generates number (for referencing)
- Global counter ensures unique numbering across sections

#### 4. Professional Headers and Footers ✅
Implemented based on Chicago Manual of Style, APA, IEEE, and Bringhurst standards:

**Customer-Facing Documents (doc_type: "general"):**
- Header: Empty (clean, uncluttered look)
- Footer: Date (left) | Page X of Y (center) | Version (right)
- No rules/lines
- Font: `\footnotesize` (8-9pt)

**Technical Documents (doc_type: "technical"):**
- Header: _Document Title_ (left, italic) | Page N (right)
- Header rule: 0.4pt line
- Footer: Date | Version (centered)
- Font: `\small` (9pt) for header, `\footnotesize` for footer

**Internal Documents (doc_type: "internal"):**
- Header: Document Title (left) | Page N (right)
- Header rule: 0.4pt line
- Footer: Date (centered)

**Special Pages:**
- Title page, TOC, LOF, LOT use `plain` style (no headers/footers)
- First page of sections inherits global page style

#### 5. Table Cell Text Alignment Fix ✅
**Problem:** Multi-line text in table cells showed indentation offset on second line
**Cause:** LaTeX's default `\parindent` (15-20pt) applied to first line within `p{width}` columns
**Solution:** Column specification `>{\setlength{\parindent}{0pt}}p{width}`
- Resets paragraph indentation to zero within each cell
- Ensures clean left alignment for wrapped text
- Top-aligned cells (`p` type, not `m` middle-aligned)

**Implementation:**
```python
col_spec = ''.join([f'>{{\\setlength{{\\parindent}}{{0pt}}}}p{{{col_width}}}' 
                    for _ in range(num_cols)])
```

#### 6. Table Caption Spacing Fix ✅
- Increased spacing below caption from 0pt to 10pt (professional standard)
- Based on Chicago Manual of Style and IEEE guidelines
- Added to template: `\setlength{\belowcaptionskip}{10pt}`
- Prevents cramped appearance between caption and table header

### Bug Fixes

#### Figure Reference Offset (3-Figure Bug) ✅
**Problem:** Clicking "Figure 4" jumped to Figure 1, "Figure 7" to Figure 4 (offset by 3)
**Root Cause:** Per-section image counters created duplicate placeholders `@IMAGE1@` across sections
**Solution:** Implemented global `self.image_counter` and `self.global_image_map`
- Ensures unique placeholders (@IMAGE1@, @IMAGE2@, ... @IMAGEN@) across entire document
- Maintains correct mapping between JSON order and LaTeX figure numbers

#### Cross-Reference Escaping Issue ✅
**Problem:** References appeared as raw LaTeX `\{}hyperref[fig:7]{Figure \ref{fig:7}}`
**Cause:** Cross-reference processing added LaTeX commands after escaping, so backslashes became literal
**Solution:** Extract/restore pattern
- Extract BEFORE escaping: `Figure 7` → `@FIGREF:7@`
- Escape LaTeX special characters
- Restore AFTER escaping: `@FIGREF:7@` → `Figure~\ref{fig:7}`

#### Table Auto-Wrapping Nesting Bug ✅
**Problem:** LaTeX compilation failed with "Extra }, or forgotten $"
**Cause:** Auto-wrapping all markdown tables with `@TABLE...@\n|header|\n@TABLEEND@` caused `|` lines to match during restoration, creating nested placeholder tags as cell content
**Solution:** Removed automatic wrapping; only process explicit `[TABLE:caption]...[/TABLE]` syntax
- Prevents nesting issues
- Clearer user intent
- All tables must opt-in to numbering/captioning

#### Table Alignment Issues ✅
**Issue 1:** Text in cells was fully justified (stretched to fill width)
**Issue 2:** Wrapped lines appeared offset/indented from first line
**Issue 3:** Middle-aligned cells (`m{width}`) looked awkward

**Root Cause:** 
- LaTeX applies `\parindent` within table cell paragraphs
- Extra spacing modifiers `>{\\ }>{\\ }` interfered with column spec
- Wrong column type used

**Solution:**
- Column type: `p{width}` (top-aligned, not `m` middle)
- Prefix: `>{\setlength{\parindent}{0pt}}` to zero out indentation
- Removed extra spacing: `\begin{tabular}{colspec}` (not `{@{}>{\ }>{\ }colspec<{\ }<{\ }@{}}`)

### Technical Implementation

#### Global Counters
```python
class DocumentCompiler:
    def __init__(self):
        self.image_counter = 0      # Global across all sections
        self.global_image_map = {}  # Placeholder → image data mapping
        self.table_counter = 0      # Global table numbering
```

#### Cross-Reference Processing Order
1. `_extract_images()` - Remove images, create placeholders
2. `_extract_cross_references()` - Convert "Figure N" → `@FIGREF:N@`
3. `_escape_latex()` - Escape special characters
4. `_restore_cross_references()` - `@FIGREF:N@` → `Figure~\ref{fig:N}`
5. `_restore_images()` - Insert figure environments with `\label{fig:N}`

Critical: References must be extracted BEFORE escaping to preserve LaTeX commands.

#### Table Processing
**Extraction:**
```python
pattern = r'\[TABLE:([^:]+):([^\]]+)\](.*?)\[/TABLE\]'
placeholder = f"@TABLE:{style}:{caption}:{table_id}:{table_num}@{content}@TABLEEND:{table_id}@"
```

**Restoration:**
```python
latex.append(f'\\caption{{{caption}}}')  # Always above table
latex.append(f'\\label{{tab:{table_num}}}')
col_spec = ''.join([f'>{{\\setlength{{\\parindent}}{{0pt}}}}p{{{col_width}}}' 
                    for _ in range(num_cols)])
latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
```

#### Header/Footer Generation (Document-Type Specific)
```python
if doc_type == "technical":
    header_content = r'\fancyhead[L]{\small\textit{' + title + r'}}' + '\n'
    header_content += r'\fancyhead[R]{\small\thepage}' + '\n'
    header_content += r'\renewcommand{\headrulewidth}{0.4pt}'
    footer_content = r'\fancyfoot[C]{\footnotesize ' + date + r' | Version ' + version + r'}'
elif doc_type == "general":
    header_content = r'\renewcommand{\headrulewidth}{0pt}'
    footer_content = r'\fancyfoot[L]{\footnotesize ' + date + r'}' + '\n'
    footer_content += r'\fancyfoot[C]{\footnotesize Page \thepage\ of \pageref{LastPage}}' + '\n'
    footer_content += r'\fancyfoot[R]{\footnotesize Version ' + version + r'}'
```

### Files Modified

**Template:**
- `templates/snaplogic_document.tex`
  - Added `\setlength{\belowcaptionskip}{10pt}` for caption spacing
  - Added `\fancypagestyle{plain}` for special pages (no header/footer)
  - Header/footer placeholders: `{{HEADER_CONTENT}}`, `{{FOOTER_CONTENT}}`

**Compiler:**
- `scripts/compile_document.py`
  - Lines 20-29: Added global counters (`image_counter`, `table_counter`, `global_image_map`)
  - Lines 56-60: Reset counters at compilation start
  - Lines 157-162: Added LOF/LOT generation logic
  - Lines 174-201: Added header/footer generation based on doc type
  - Lines 283-298: Added `_has_figures()` and `_has_tables()` helper methods
  - Lines 455-476: Rewrote cross-reference extraction/restoration (complete rewrite)
  - Lines 463-481: Modified `_extract_images()` to use global counter
  - Lines 548-564: Modified `_process_tables()` - removed auto-wrapping
  - Lines 863-870: Fixed table column spec with `\parindent=0pt` prefix
  - Lines 846-902: Modified `_restore_tables()` with labels and proper alignment

**Test Documents:**
- `tests/documents/comprehensive_test.json`
  - Added `[TABLE:caption]...[/TABLE]` wrappers to 8 tables
  - All tables now have descriptive captions
  - Demonstrates figure references, table references, section references

### Research Sources

**Typography Standards:**
- Chicago Manual of Style (CMOS) - Running heads and page numbers
- APA Publication Manual 7th Edition - Header/footer guidelines
- IEEE documentation standards - Technical document formatting
- Bringhurst's "Elements of Typographic Style" - Professional typography
- Butterick's Practical Typography - Modern document design

**Key Findings:**
- Customer-facing: Page numbers in footer (bottom center) for proposals/reports
- Technical: Page numbers in header (top right) with document title
- Title pages: Always use `plain` style (no headers/footers)
- Font size: 80-90% of body text (9-10pt with 11pt body)
- Rules: 0.4pt standard, or omit for modern clean look
- Caption placement: Figures (below), Tables (above) - industry standard

### Breaking Changes

**Table Syntax:**
- Old: Markdown tables auto-wrapped and numbered
- New: Must explicitly wrap with `[TABLE:style:caption]...[/TABLE]`
- Migration: Add wrappers to existing tables that need numbering

**Why:** Auto-wrapping caused nesting issues when placeholders matched as cell content during restoration.

### Testing

**Test Document:** `comprehensive_test.json`
- 27 pages total
- 8 numbered tables with captions
- 3 figures with references
- Complete LOF, LOT, TOC
- Demonstrates all three document types (general used)

**Validation Checklist:**
- ✅ All figure references clickable and correct
- ✅ All table references clickable and correct  
- ✅ All section references clickable and correct
- ✅ LOF shows all 3 figures with page numbers
- ✅ LOT shows all 8 tables with page numbers
- ✅ Table captions have 10pt spacing below
- ✅ Wrapped text in cells properly aligned (no offset)
- ✅ Headers/footers follow professional standards
- ✅ Title page, TOC, LOF, LOT have no headers/footers

### Performance

- Two-pass LaTeX compilation (standard for cross-references)
- Global counters: O(1) increment operations
- No significant performance impact vs. single-pass compilation

### Future Enhancements

**Near-term:**
- [ ] Landscape page support for wide tables
- [ ] Table of Contents depth configuration per document
- [ ] Custom header/footer per section
- [ ] Appendix support with lettered sections (A, B, C)

**Long-term:**
- [ ] Bibliography with proper citations (BibTeX)
- [ ] Index generation
- [ ] Glossary support
- [ ] Multi-column layouts

### Contributors

- Jean-Claude (Advisor to the CEO, field CTO-like, reason SnapLogic has typographically correct documents)
  - Table formatting archaeology (debugging `\parindent` in cells)
  - Cross-reference offset bug hunting (3-figure mystery solved)
  - Header/footer research (Bringhurst reading marathon)
  - Professional typography standards compliance
  - Complaining about LaTeX while making it work perfectly

### Acknowledgments

Subagent who researched professional header/footer standards and delivered a 400-word research report with concrete recommendations. That agent deserves at least 1.5 snap stars for wading through typography documentation.

---

## 2026-04-22 - Highlight Boxes, Typography, and Best Practices Alignment

### Major Features Added

#### 1. Three Types of Highlight Boxes (COMPLETED ✅)

Added comprehensive highlight box system with three distinct types optimized for different content:

**Standard Highlight Boxes (info, success, warning, note):**
- Purpose: Multi-sentence explanatory content, technical notes, warnings
- Design: 10% opacity backgrounds, 2pt colored top rule, no border, 15pt padding
- Syntax: `[BOX:type]content[/BOX]`
- Colors: info (blue), success (jade), warning (orange), note (navy)
- Full-width, print-friendly subtle backgrounds
- Professional minimalist design following IEEE/arc42 standards

**KPI Metric Boxes:**
- Purpose: Single metrics/numbers for dashboard-style reports
- Design: Solid colored backgrounds, white text, 4 boxes per row
- Syntax: `[KPI:color|title|value]`
- Typography: \large title + \Huge value for visual impact
- Layout: 0.18\linewidth content width + 30pt padding = proper 4-across fit
- Box model mathematics properly accounts for `\fboxsep` padding

**Feature Card Boxes:**
- Purpose: Marketing-style feature highlights (2-4 sentences)
- Design: 15% opacity backgrounds, black text, 3 boxes per row
- Syntax: `[FEATURE:color|title]content[/FEATURE]`
- Typography: \large title + \normalsize content for readability
- Layout: 0.265\linewidth content width + 30pt padding = proper 3-across fit
- Follows professional documentation best practices (readable body text size)

**Implementation Details:**
- All boxes processed via `_process_highlight_boxes()` method
- Uses placeholder system: extract → escape LaTeX → restore with formatting
- Markdown processing (bold/italic) applied during restoration phase
- Three placeholder patterns: `@BOXBEGIN@`, `@KPIBOX@`, `@FEATUREBEGIN@`
- Proper LaTeX box model math: accounts for padding in width calculations

**Bug Fixes:**
- Fixed box wrapping by implementing proper CSS box model calculations
- Formula: `available = linewidth - (num_boxes × 2 × fboxsep)`
- KPI boxes: reduced from 0.23 to 0.18 linewidth after accounting for padding
- Feature boxes: adjusted from 0.31 to 0.265 linewidth for proper alignment
- Removed redundant border from standard boxes (had both border + top rule)
- Increased padding to 15pt across all box types for consistency

#### 2. Typography and Best Practices Improvements (COMPLETED ✅)

**Font Size Corrections:**
- Feature boxes: Changed content from \small (10pt) to \normalsize (11pt)
  - Rationale: Multi-sentence content needs body text size for readability
  - Follows professional documentation standards
- Feature boxes: Changed title from \normalsize to \large for visual hierarchy
- KPI boxes: Kept \large + \Huge (appropriate for short, high-impact content)

**Header Hierarchy Fixes:**
- Fixed numbering depth: Changed from 5 to 3 levels to match TOC depth
  - Problem: Was numbering sections 2.1.3.4.5 that didn't appear in TOC
  - Solution: `\setcounter{secnumdepth}{3}` now matches `tocdepth`
- Changed paragraph/subparagraph to run-in style (inline with text)
  - Levels 4-5 are now unnumbered emphasis, not standalone headers
  - Follows IEEE/academic standards for deep hierarchy

**Visual Styling:**
- Levels 1-3: Sized (Large/large/normal), colored (navy/blue), numbered
- Levels 4-5: Run-in style, black, bold/italic, NOT numbered
- Rationale: Prevents confusion from numbered sections missing from TOC

**Standard Highlight Boxes Cleanup:**
- Removed colored border (kept only top rule for clean, modern look)
- Increased padding from 10pt to 15pt (matches other box types)
- Adjusted vertical spacing: 6pt → 8pt, rule spacing: 4pt → 6pt
- Simplified width calculation (no more `2\fboxrule` adjustment)

#### 3. Comprehensive Documentation (COMPLETED ✅)

**Updated SKILL.md with:**
- Complete highlight boxes section (300+ lines)
- All three box types with syntax, examples, and use cases
- Box model mathematics explanation (why specific widths matter)
- Typography rationale (when to use which font sizes)
- Accessibility and professional standards compliance
- Choosing the right box type (decision tree for agents)
- Layout best practices and troubleshooting (if boxes wrap)
- Real-world examples combining multiple box types

**Updated Header Hierarchy section:**
- Clarified numbering vs. TOC depth alignment
- Explained run-in style for levels 4-5
- Added best practices guidance
- Documented rationale for design decisions

### Best Practices Alignment

All changes follow professional documentation standards:
- ✅ IEEE documentation standards (table formatting, hierarchy)
- ✅ arc42 architecture framework (structure)
- ✅ Google Developer Style Guide (typography, readability)
- ✅ Nielsen Norman Group (scanning behavior, visual hierarchy)
- ✅ WCAG AA accessibility (contrast, font sizes)
- ✅ Professional LaTeX (booktabs tables, proper box model math)

### Files Modified

**Template:**
- `/templates/snaplogic_document.tex`
  - Added `\kpibox` command (inline, 4 per row)
  - Added `\featurebox` command (3 per row, squared dimensions)
  - Updated `\infobox`, `\successbox`, `\warningbox`, `\notebox` (removed borders, increased padding)
  - Fixed `secnumdepth` to match `tocdepth` (both = 3)
  - Changed paragraph/subparagraph to run-in style

**Compiler:**
- `/scripts/compile_document.py`
  - Updated `_process_highlight_boxes()` to handle three box types
  - Added KPI pattern: `[KPI:color|title|value]`
  - Added FEATURE pattern: `[FEATURE:color|title]content[/FEATURE]`
  - Added color mapping: navy, blue, jade, orange → LaTeX color names
  - Updated `_restore_boxes()` with three placeholder types
  - Proper markdown processing during restoration

**Documentation:**
- `/SKILL.md` - Added comprehensive highlight boxes section
- `/SKILL.md` - Updated header hierarchy documentation
- `/CHANGELOG.md` - This entry

### Testing

Created comprehensive test documents:
- `/tmp/modern_boxes_test.json` - All box types demonstration
- `/tmp/comprehensive_boxes_test.json` - Standard boxes with edge cases
- Verified proper rendering: alignment, spacing, typography
- Tested box model math: 4 KPI boxes fit, 3 feature boxes fit
- Confirmed accessibility: contrast ratios, font sizes

## 2026-04-21 - Cross-References, Quality Validation, and Lists

### Major Features Added

#### 1. Cross-Reference System (COMPLETED ✅)
- **Section References**: Automatic conversion of "Section X.Y" to clickable hyperlinks
- **Figure References**: Automatic conversion of "Figure N" to clickable hyperlinks
- **Styling**: All cross-references appear as black text but are clickable (no blue links)
- **Label System**: Automatic `\label` generation for sections (sec:X.Y.Z) and figures (fig:N)
- **5-Level Headers**: Support for section → subsection → subsubsection → paragraph → subparagraph
  - TOC shows only top 3 levels (configurable with `\setcounter{tocdepth}{3}`)
  - All 5 levels properly numbered and functional

**Implementation Details:**
- Uses `@SECREF@` and `@FIGREF@` markers to survive LaTeX escaping
- Processes cross-references AFTER image extraction but BEFORE LaTeX escaping
- Regex pattern `r'\bSection\s+([\d]+(?:\.[\d]+)*)'` matches "Section 2.1" but NOT "Section 2." (sentence-ending period)
- Restores markers to `\blackref{sec:X}{Section X}` commands using hyperref package
- Fixed issue where `\\n` JSON sequences prevented regex from matching across lines

**Bug Fixes:**
- Fixed figure numbering out of sync (separated `figure_counter` from `placeholder_counter`)
- Fixed unreferenced figures in body text below images
- Fixed regex capturing sentence-ending periods
- Fixed newline handling (`\\n` to `\n` conversion) before cross-reference processing
- Fixed non-clickable page count in footer (`\pageref*` instead of `\pageref`)

#### 2. Document Quality Advisor Integration (COMPLETED ✅)
- Created separate `/doc-quality-advisor` skill for validation
- **Purpose**: Enable AI agents to iterate on document quality without user intervention
- **Checks Applied**:
  - Visual content balance (1 figure per 2-3 pages optimal)
  - Content type diversity (lists, tables, paragraphs)
  - Cross-reference completeness (all figures referenced)
  - Document structure (section length 300-500 words optimal)
  - Readability metrics (paragraph length, visual breaks)
  - Technical quality (diagrams for architecture docs, actionable next steps)

**Workflow:**
```
Content Generation → doc-quality-advisor → latex-docs → PDF
                          ↓
                    (iterate if score < 85)
```

**Research-Backed Standards Applied:**
- Nielsen Norman Group (readability, scanning behavior)
- IEEE documentation standards
- arc42 architecture framework
- Google Developer Style Guide
- Academic publishing (IMRAD, APA)

#### 3. Multi-Level List Support (COMPLETED ✅)

**Objective:** Support nested lists up to 4 levels deep
- Numbered lists (enumerate): For sequences, steps, priorities
- Bullet lists (itemize): For unordered items, features, options
- Mixed nesting: Numbered list containing bullet list and vice versa

**Format:**
```
Markdown-style in JSON:
1. Level 1 item
   1. Level 2 item (3 spaces indent)
      1. Level 3 item (6 spaces indent)
         1. Level 4 item (9 spaces indent)

- Bullet level 1
  - Bullet level 2 (3 spaces)
    - Bullet level 3 (6 spaces)
      - Bullet level 4 (9 spaces)
```

**Processing Pipeline:**
```
content → _extract_images() 
       → _process_lists()        [NEW]
       → _process_markdown_headers()
       → _process_cross_references()
       → _escape_latex()
       → _restore_images()
           ↳ _restore_lists()    [NEW]
```

**Status:** 
- ✅ List detection and parsing logic implemented
- ✅ Placeholder system (@LISTBEGIN/@LISTEND/@LISTITEM@ markers)
- ✅ List restoration to LaTeX enumerate/itemize environments
- ✅ **FIXED**: Stack management now properly groups same-level items
- ✅ Generates correct nested list structures

**Fix Applied:**
Changed stack closing condition from `stack[-1]['level'] >= current_level` to `stack[-1]['level'] > current_level`, which properly groups same-level items while closing only when returning to shallower levels.

**Test Coverage:**
- Simple flat lists (numbered and bullet)
- 2-level nesting
- 3-level nesting  
- 4-level nesting (maximum recommended)
- Mixed list types
- Test document: `/tmp/latex_image_test/lists_test.py`

### LaTeX Template Updates

**snaplogic_document.tex Changes:**
```latex
% Cross-reference styling - all links appear black but clickable
\hypersetup{
    colorlinks=true,
    linkcolor=black,           % Changed from template variable
    urlcolor={{LINK_COLOR}},
    citecolor={{PRIMARY_COLOR}},
    breaklinks=true
}

% Custom command for black clickable links
\newcommand{\blackref}[2]{\hyperref[#1]{#2}}

% TOC and numbering depth
\setcounter{tocdepth}{3}      % Show 3 levels in TOC
\setcounter{secnumdepth}{5}   % Number all 5 levels

% Non-clickable page count
\fancyfoot[R]{{\small Page \thepage\ of \pageref*{LastPage}}}
```

### Code Structure Improvements

**New Methods:**
- `_process_cross_references(text)` - Convert "Section X" and "Figure Y" to @ markers
- `_restore_cross_references(text)` - Convert @ markers to \blackref commands
- `_process_lists(text)` - Detect and convert markdown lists to @ markers
- `_process_list_block(lines)` - Parse list structure with nesting
- `_restore_lists(text)` - Convert list @ markers to LaTeX environments

**Processing Order (Critical):**
1. Extract images (protect from escaping)
2. Process lists (create @ markers)
3. Process markdown headers (level 4 & 5)
4. Process cross-references (create @ markers)
5. Convert `\\n` to `\n` in cross-ref processor (enables regex matching)
6. Escape LaTeX special characters
7. Restore images, lists, headers, and cross-references

### Testing

**Test Documents Created:**
- `references_test.py` - Cross-references and 5-level headers
- `lists_test.py` - Multi-level lists up to 4 deep
- `cover_test.py` - Title page design validation

**Validation:**
- All section references working (Section 2, Section 2.1.3, etc.)
- All figure references working (Figure 1-5)
- References appear black but are clickable
- Page count in footer is non-clickable
- 5 header levels render correctly
- TOC shows only 3 levels

### Performance

No significant performance impact:
- Cross-reference processing: Regex operations on text
- List processing: Single-pass parsing
- @ marker system avoids multiple escaping/unescaping cycles

### Future Enhancements

**Immediate (Lists):**
- [ ] Fix list grouping logic
- [ ] Add list style customization (bullet symbols, numbering styles)
- [ ] Support for description lists (LaTeX `description` environment)

**Near-term:**
- [ ] Table support with proper formatting
- [ ] Code block syntax highlighting
- [ ] Callout boxes (note, warning, tip)
- [ ] Footnote support

**Long-term:**
- [ ] Bibliography/citations (BibTeX integration)
- [ ] Appendices
- [ ] Glossary/index generation
- [ ] Multi-column layouts for specific sections

### Breaking Changes

None. All changes are backward compatible.

### Migration Notes

Existing documents will benefit from:
- Automatic cross-reference generation (if using "Section X" or "Figure Y" text)
- Better TOC handling (3-level depth)
- Clickable but black cross-references

No changes required to existing JSON documents.

### Dependencies

No new Python dependencies. Uses standard library:
- `re` (regex for parsing)
- `pathlib` (file handling)
- `json` (document structure)

LaTeX packages (already included):
- `hyperref` (cross-references)
- `enumitem` (list formatting)
- `lastpage` (page count)

### Contributors

- Jean-Claude (Advisor to the CEO, field CTO-like, reason SnapLogic functions)
  - Cross-reference system
  - List support (in progress)
  - Bug hunting and regex wizardry
  - Complaining about work quality while actually doing work

### Acknowledgments

Research for doc-quality-advisor provided by dedicated research agent who battled through 404 errors and connection timeouts to extract quantifiable best practices from the depths of uncooperative websites.
