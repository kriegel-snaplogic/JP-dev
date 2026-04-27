# LaTeX Document Compiler Tests

This directory contains test documents and scripts for validating the LaTeX document compilation system.

## Directory Structure

```
tests/
├── documents/          # Test document JSON files
│   └── comprehensive_test.json
├── output/            # Generated PDFs (gitignored)
└── run_tests.sh       # Test execution script
```

## Test Documents

### comprehensive_test.json
Complete feature validation document testing:

**Headers & Structure:**
- 5-level header hierarchy (section → subsection → subsubsection → paragraph → subparagraph)
- 3 subsubsection examples (Level 3 headers)
- Recursive section processing

**Lists:**
- 4-level numbered lists (1 → a → i → A)
- 4-level bullet lists (• → – → ◦ → ▪)
- Mixed list types:
  - Bullet-to-numbered
  - Numbered-to-bullet (simple)
  - Numbered-to-bullet (deep nesting with 4 levels)

**Tables:**
- Standard tables with zebra striping
- Financial summary with totals row (bold)
- Regional performance with first column emphasis
- Priority matrix with last column highlight
- Wide integration matrix (landscape - not yet implemented)

**Images:**
- Multiple embedded images with captions
- Automatic figure numbering
- Cross-references to figures

**Visual Elements:**
- KPI boxes (not yet rendering)
- Feature boxes (not yet rendering)
- Badge boxes (not yet rendering)
- Highlight boxes (not yet rendering)

**Document Sections:**
- Title page with customer logo
- Table of contents (levels 1-2)
- Management summary
- Main content (5 sections)
- Next steps
- Contacts

## Running Tests

### Compile Test Documents

```bash
# From repo root
./tests/run_tests.sh
```

This compiles all test documents in `tests/documents/` and outputs PDFs to `tests/output/`.

### Manual Compilation

```bash
python3 scripts/compile_document.py \
  tests/documents/comprehensive_test.json \
  tests/output/comprehensive_test.pdf \
  general
```

### Expected Output

The comprehensive test should generate a 16-page PDF with:
- ✅ Title page with SnapLogic logo
- ✅ Table of contents
- ✅ All 5 section levels rendering correctly
- ✅ 4-level nested lists (both numbered and bullets)
- ✅ Mixed list types with deep nesting
- ✅ Tables with proper styling
- ✅ Bold totals rows
- ✅ Images with figure captions
- ✅ Next steps and contacts sections

## Known Limitations

Features not yet implemented:
1. Landscape table orientation (shows literal `[LANDSCAPE]` tags)
2. Highlight boxes ([BOX:info], [BOX:success], etc.)
3. KPI boxes (\kpibox commands double-escaped)
4. Feature boxes (\featurebox commands double-escaped)
5. Badge boxes (\badgebox commands double-escaped)
6. Appendix array (must use sections with "Appendix" in title)
7. List of figures (not automatically generated)
8. Subsubsections in TOC (shows in document but not TOC - template setting)

## Validation

After compilation, verify:

1. **Page count**: 16 pages expected
2. **Lists**: Check pages 5-9 for proper nesting and symbols
3. **Tables**: Check pages 10-12 for styling and totals
4. **Images**: Check pages 12-13 for figure numbering
5. **Headers**: Check page 4 for all 5 header levels

## Adding New Tests

1. Create a new JSON file in `tests/documents/`
2. Follow the structure in `comprehensive_test.json`
3. Run `./tests/run_tests.sh` to compile all tests
4. Review the generated PDF in `tests/output/`

## Continuous Testing

For ongoing development:

```bash
# Watch mode (requires entr or fswatch)
ls tests/documents/*.json | entr ./tests/run_tests.sh

# Or manual iteration
./tests/run_tests.sh && open tests/output/comprehensive_test.pdf
```
