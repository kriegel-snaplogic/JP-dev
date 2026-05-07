# latex-docs Skill

**Version:** 3.0  
**Last Updated:** 2026-04-29  
**Size:** ~6.8K tokens (agent-friendly)

## What It Does

Generates professional, branded SnapLogic PDF documents from JSON structure using LaTeX compilation. Supports technical documentation, customer proposals, RFPs, internal reports with full branding, tables, images, cross-references, and multi-file projects.

## Quick Start

```bash
# Basic usage
/latex-docs

# Agent will guide you through document creation:
# 1. Document type (technical/general/internal)
# 2. Content structure (JSON)
# 3. Images and assets
# 4. Compilation and delivery
```

## Key Features

- **7 table styles** with emphasis options (bold columns, colored cells, total rows)
- **3 highlight box types** (BOX, KPI, FEATURE) with 4 color schemes
- **Semantic cross-references** (position-independent labels for tables/figures/sections)
- **Multi-file projects** for large RFPs (50+ pages, 100+ images)
- **Auto-generated TOC/LOF/LOT** with proper appendix handling
- **Professional typography** (10pt default, A4 paper, SnapLogic branding)

## Installation

1. Extract `latex-docs.zip` to `~/.claude/skills/latex-docs/`
2. Ensure LaTeX is installed (MacTeX, TeX Live, or MiKTeX)
3. Verify Python 3.7+ is available
4. Skill is immediately available as `/latex-docs`

## Files Included

### Documentation
- `SKILL.md` - Main skill documentation (agents read this)
- `REFERENCE.md` - Detailed feature reference (all table styles, box types, advanced syntax)
- `CONTENT_REQUIREMENTS.md` - Input format validation guide (syntax requirements, common errors)
- `README.md` - This file

### Scripts
- `scripts/compile_document.py` - Main compilation engine (1,700+ lines)
- `scripts/brand_config.py` - SnapLogic brand configuration (colors, logos, fonts)

### Assets
- `assets/logos/` - SnapLogic logos (blue, white, logomark)
- `assets/fonts/` - Corporate fonts (if needed)

## Document Types

1. **Technical** - Architecture docs, API documentation, integration guides
2. **General/Customer-facing** - Proposals, solution docs, RFPs, executive summaries
3. **Internal** - Status reports, memos, project updates

## Content Structure

### Simple Document (Single JSON)
```json
{
  "title": "Document Title",
  "author": "SnapLogic",
  "date": "2026-04-29",
  "version": "1.0",
  "sections": [
    {
      "title": "Section Title",
      "content": "Content with **markdown** and [TABLE:simple:Caption]...[/TABLE]"
    }
  ]
}
```

### Multi-File Project (Large RFPs)
```
content_library/
├── documents/<project_name>/
│   ├── section_01_company.json
│   ├── section_02_technical.json
│   ├── section_03_requirements.json
│   └── final_document.json (assembled)
└── assets/images/<project_name>/
    ├── architecture.png
    └── screenshots/
```

## Syntax Quick Reference

### Tables
```
[TABLE:style:caption:emphasis:label]
| Col1 | Col2 |
|------|------|
| Data | Data |
[/TABLE]
```

Styles: `simple`, `minimal`, `accent-blue`, `accent-jade`, `accent-orange`, `bordered`, `status-colors`  
Emphasis: `first-bold`, `last-jade`, `last-orange`, `total-row`, `widths=1,2,3`

### Images
```
[IMAGE:path:caption:width:label]
```

Example: `[IMAGE:diagram.png:System Architecture:0.8:arch]`

### Boxes
```
[BOX:type]content[/BOX]
[KPI:color|title|value]
[FEATURE:color|title]content[/FEATURE]
```

Types: `info`, `success`, `warning`, `note`  
Colors: `navy`, `blue`, `jade`, `orange`

### Cross-References
```
Table~\ref{tab:label}
Figure~\ref{fig:label}
Section~\ref{sec:label}
```

## Document Defaults

- **Font size**: 10pt (compact, professional)
- **Paper size**: A4 (210mm × 297mm)
- **Typography**: Helvetica/Arial sans-serif
- **Colors**: Full SnapLogic branding (navy, blue, jade, orange)

Override via command-line: `--font-size 11pt --paper-size letterpaper`

## Quality Validation

**⚠️ REQUIRED**: Use `doc-quality-advisor` skill before final compilation:

```bash
1. Generate content → document.json
2. /doc-quality-advisor document.json
3. Fix CRITICAL/WARNING issues
4. Re-validate until score ≥85
5. Compile final PDF
```

## Section Guidelines

- **Top-level sections**: 3-10 optimal (1, 2, 3...)
- **Subsections per section**: 0-3 normal, max 6 (1.1, 1.2, 1.3...)
- **Section length**: 300-500 words (without subsections)
- **Subsection length**: 200-400 words each

## Common Issues

### Image not found
- Use paths relative to `content_library/`
- Check: `content_library/assets/images/<project>/image.png` exists

### Table rendering broken
- Verify: `[TABLE:style:caption]` (not bare `[TABLE]`)
- Every table needs style AND caption
- Must have closing `[/TABLE]`

### Cross-references show "??"
- LaTeX requires two compilation passes (automatic)
- Check semantic labels match: `[TABLE:...:label]` and `Table~\ref{tab:label}`

### Double numbering in TOC
- Remove numbers from JSON titles
- LaTeX auto-numbers: `"title": "Architecture"` not `"title": "2. Architecture"`

## Version Management

- **0.1-0.9**: Draft versions
- **1.0**: First release (ask user before assigning)
- **1.1-1.9**: Minor updates
- **2.0+**: Major revisions (ask user)

## Best Practices

1. **Always validate** with `/doc-quality-advisor` before delivery
2. **Use semantic labels** for tables/figures in reusable content
3. **Test image paths** before compilation
4. **Break large docs** into multi-file projects (50+ pages)
5. **Reference every table/figure** in the text at least once
6. **Prefer markdown** over HTML (markdown is first-class)

## Requirements

- **Python**: 3.7+ (for compilation script)
- **LaTeX**: MacTeX (macOS), TeX Live (Linux), MiKTeX (Windows)
- **LaTeX packages**: geometry, graphicx, hyperref, xcolor, fancyhdr, longtable, booktabs, colortbl, tabularx, caption, tocloft, pdflscape

## Support

- **Usage questions**: See `SKILL.md`
- **Feature details**: See `REFERENCE.md`
- **Input validation**: See `CONTENT_REQUIREMENTS.md`
- **Issues**: Check error messages in `.tex` file (preserved on error)

## Example Projects

See `content_library/documents/` for real-world examples:
- `airbus_vendor_profile/` - 50-page enterprise RFP with 100+ references

---

**Created by:** Jean-Claude, Advisor to the CEO and AI team  
**Powered by:** LaTeX, Python, professional documentation standards (IEEE, Chicago, arc42)
