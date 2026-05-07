# Test Documents

This directory contains comprehensive test documents for validating the LaTeX compiler.

**Post-Migration Note (2026-05-04):** These test documents were used to validate the migration from monolithic architecture to the 3-skill modular system. All tests passed with zero regressions.

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
