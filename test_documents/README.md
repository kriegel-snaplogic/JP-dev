# Test Documents

This directory contains comprehensive test documents for validating the LaTeX compiler.

**Post-Migration Note (2026-05-04):** These test documents were used to validate the migration from monolithic architecture to the 3-skill modular system. All tests passed with zero regressions.

**v3.1 Note (2026-05-06):** Added grid layout test documents to validate KPI and Feature box grid rendering.

## grid_layout_test.json

**Purpose:** Basic validation of grid layout system for KPI and Feature boxes

**Document specifications:**
- **Pages:** 5 (was 11 without grid layout - 54% reduction)
- **Feature boxes:** 12 (3-per-row grid, 4 complete rows)
- **KPI boxes:** 20 (4-per-row grid, 5 complete rows)
- **Colors:** Navy, blue, jade, orange (varied patterns)

**Features tested:**
1. **Feature grid:** 3 boxes per row with tight spacing
2. **KPI grid:** 4 boxes per row with tight spacing
3. **Mixed content:** Text between box groups handled correctly
4. **Color variation:** No repetitive column patterns
5. **Row spacing:** Negative spacing (`\\[-6pt]`) for seamless rows

**Validation checklist:**
- [ ] 12 feature boxes render in 4 rows of 3
- [ ] 20 KPI boxes render in 5 rows of 4
- [ ] No white space between rows within grids
- [ ] Text between grids renders normally
- [ ] Page count reduced from 11 → 5 pages

---

## large_grid_test.json

**Purpose:** Stress test for grid layout with production-scale box counts

**Document specifications:**
- **Pages:** 6
- **Feature boxes:** 28 (9 complete rows + 1 partial row with 1 box)
- **KPI boxes:** 40 (10 complete rows of 4)
- **Colors:** Navy, blue, jade, orange (highly varied to avoid patterns)

**Features tested:**
1. **Large grids:** Validates layout with many rows
2. **Color diversity:** Mixed colors throughout (no repetitive patterns)
3. **Partial rows:** Tests rendering when last row not full (28 features = 9 full + 1 partial)
4. **Content variety:** Realistic feature descriptions and KPI metrics

**Validation checklist:**
- [ ] 28 feature boxes render correctly (9 full rows + 1 box)
- [ ] 40 KPI boxes render in 10 complete rows
- [ ] Color patterns varied (not just navy-blue-jade-orange repeating)
- [ ] Partial row (1 feature box) renders without issues
- [ ] Page count reasonable for content volume

---

## airbus_rfp_v3_test.json

**Purpose:** Comprehensive integration test for professional RFP document generation

**Document specifications:**
- **Pages:** 70
- **Version:** 3.0
- **Sections:** 4 main sections + 3 appendices
- **Tables:** 15 (mix of simple, multipage-simple, accent styles)
- **Images:** Multiple full-width images
- **Special features:** Management Summary with feature/KPI boxes, info boxes, cross-references

**Features tested:**
1. **Line breaks:** `<br/>` tags between feature box rows (tests escaping fix)
2. **Feature boxes:** 3-per-row layout with proper spacing and mixed colors (navy, jade, blue, orange)
3. **KPI boxes:** 4-per-row layout with no spacing between boxes
4. **Info boxes:** Default highlight box with blue accent
5. **Tables:**
   - Simple style with navy header
   - Multipage-simple for page-spanning tables
   - Accent-blue with colored headers
   - First-bold emphasis for first column
   - Total-row emphasis for summary rows
   - Category headers (ALL CAPS rows with bold + light background)
   - Custom column widths (widths parameter)
6. **Bullet lists with bold labels:** `**Label:** content` format in sections 1.2, 1.3, 1.4
7. **Executive team formatting:** Names and roles in bold
8. **Cross-references:** Table and figure references using `\ref{}`
9. **Section numbering:** Automatic numbering with unnumbered Management Summary
10. **Appendices:** Letter-based numbering (A, B, C)
11. **Page numbering:** Continuous Arabic from TOC onwards

**Validation checklist:**
- [ ] All 15 tables render correctly
- [ ] Feature boxes display in 2 rows of 3 with proper line break
- [ ] KPI boxes display in 1 row of 4 with no gaps
- [ ] Info box renders with blue accent
- [ ] All cross-references resolve correctly
- [ ] Page numbering is continuous
- [ ] TOC shows correct page numbers
- [ ] Management Summary is unnumbered but in TOC
- [ ] Executive names are bold
- [ ] Bullet list labels are bold
- [ ] No LaTeX compilation errors
- [ ] No artifacts or escaped characters in output

**Known issues:**
- Reference warning for `sec:1.5` on page 55 (undefined reference in requirements table)

**Compilation command:**
```bash
python3 scripts/compile_document.py \
  test_documents/airbus_rfp_v3_test.json \
  /tmp/airbus_rfp_test_output.pdf \
  general \
  --font-size 10pt
```

**Expected output:**
- Status: success
- Pages: 70
- Version: 3.0
- Warnings: sec:1.5 undefined reference (acceptable)

## Adding new test documents

When adding test documents, include:
1. The JSON source file
2. Documentation in this README covering:
   - Purpose and what features are tested
   - Expected page count and specifications
   - Validation checklist
   - Compilation command
   - Known issues or expected warnings
