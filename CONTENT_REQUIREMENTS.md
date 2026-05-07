# Content Input Requirements for latex-docs

**Audience:** Content authors, AI agents, anyone creating JSON input for latex-docs skill

**Purpose:** Define exact syntax requirements to prevent compilation failures

---

## Critical Rules ⚠️

### 1. Tables Must Have Style AND Caption

**❌ BREAKS COMPILATION:**
```
[TABLE]
| Header | Data |
|--------|------|
| Row 1  | Val  |
[/TABLE]
```

**✅ CORRECT:**
```
[TABLE:simple:Table Caption Here]
| Header | Data |
|--------|------|
| Row 1  | Val  |
[/TABLE]
```

**Syntax:** `[TABLE:style:caption:emphasis:label]`
- **style** (REQUIRED): `simple` (the only style)
- **caption** (REQUIRED): Text or `_` for no caption
- **emphasis** (optional): `colN-bold`, `colN-jade`, `colN-orange`, `colN-blue`, `colN-status`, `total-row`, `status`, `widths=1,2,3`
- **label** (optional): Semantic cross-reference label

**Examples:**
```
[TABLE:simple:Customer References]
[TABLE:simple:Pricing Tiers::pricing]
[TABLE:simple:Regional Sales:col1-bold,col4-jade:sales]
[TABLE:simple:System Requirements:widths=2,1,1,3]
```

---

### 2. Images Must Have Path AND Caption

**Syntax:** `[IMAGE:path:caption:width:label]`

- **path** (REQUIRED): `diagram.png`, `/tmp/chart.jpg`, `assets/logo.png`
- **caption** (REQUIRED): Text or `_` for no caption
- **width** (optional): `0.5` = 50%, `0.8` = 80%, `1.0` = full width (default)
- **label** (optional): Semantic cross-reference label

**Examples:**
```
[IMAGE:architecture.png:System Architecture:0.8:arch]
[IMAGE:/tmp/logo.jpg:_:0.5]
[IMAGE:diagram.pdf:Data Flow::flow-diagram]
```

---

### 3. NO HTML Tags (Except `<br/>`)

**✅ ALLOWED:**
- `<br/>` or `<br>` → Converted to LaTeX line breaks automatically
- Markdown: `**bold**`, `*italic*`, `# Headers`
- Newlines: `\n` (continuation), `\n\n` (paragraph break)

**❌ NOT ALLOWED:**
- `<p>`, `</p>`, `<div>`, `<span>`
- `<strong>`, `<b>`, `<em>`, `<i>`
- `<h1>`, `<h2>`, `<h3>`
- `&nbsp;`, `&mdash;`, `&lt;`, `&gt;` (use UTF-8 directly)
- `<table>`, `<tr>`, `<td>` (use `[TABLE:...]` syntax)

**Replacement Guide:**
- `<strong>text</strong>` → `**text**`
- `<em>text</em>` → `*text*`
- `<p>text</p>` → `text\n\n` (double newline)
- `<br>` → `<br/>` (both work, cleaned automatically)

---

### 4. NO Section Numbers in Titles

LaTeX adds section numbers automatically. Including them causes double numbering.

**❌ WRONG:**
```json
{
  "title": "2.1 Architecture Components"  ← Renders as "2.1 2.1 Architecture Components"
}
```

**✅ CORRECT:**
```json
{
  "title": "Architecture Components"  ← Renders as "2.1 Architecture Components"
}
```

**Fix existing content with numbers:**
```bash
python3 scripts/strip_section_numbers.py input.json output.json
```

---

### 5. Cross-References Use `~\ref{}` Syntax

**Semantic labels (recommended):**
```
Table~\ref{tab:pricing-table} shows our pricing tiers.
Figure~\ref{fig:architecture} illustrates the system design.
Section~\ref{sec:implementation} covers deployment details.
```

**Numeric references (automatic):**
```
Table 3 shows the pricing comparison.
Figure 2 illustrates the architecture.
Section 2.1 covers the implementation.
```

Both work, but semantic labels are position-independent and survive content reordering.

---

## File Format: JSON Structure

```json
{
  "title": "Document Title",
  "subtitle": "Optional Subtitle",
  "author": "SnapLogic",
  "date": "2026-04-29",
  "version": "1.0",
  "customer_name": "Customer Name",
  "customer_logo": "/path/to/logo.png",
  "management_summary": "Executive summary (general docs only)",
  "abstract": "Technical abstract (technical docs only)",
  "sections": [
    {
      "title": "Section Title",
      "content": "Content with **markdown** formatting.\n\n[TABLE:simple:Data Summary]\n| Col1 | Col2 |\n|------|------|\n| A    | B    |\n[/TABLE]\n\nMore text.\n\n[IMAGE:diagram.png:System Diagram:0.7:sys-diagram]",
      "subsections": [
        {
          "title": "Subsection Title",
          "content": "Nested content here..."
        }
      ]
    }
  ],
  "next_steps": [
    "Action item 1",
    "Action item 2"
  ],
  "contacts": [
    {
      "name": "Contact Name",
      "role": "Role Title",
      "email": "email@snaplogic.com"
    }
  ]
}
```

---

## Pre-Compilation Validation

**Manual checks:**
1. Search for `[TABLE]` without style/caption → Add style and caption
2. Search for `[TABLE:` without matching `[/TABLE]` → Add closing tag
3. Search for `[IMAGE:` with only one parameter → Add caption (or `_`)
4. Search for HTML tags (`<strong>`, `<p>`, etc.) → Convert to markdown
5. Search for section titles with numbers (`"title": "2.1 ...`) → Remove numbers

**Automated fixes:**
```bash
# Fix malformed tables
python3 scripts/fix_unwrapped_tables.py input.json output.json

# Strip section numbers
python3 scripts/strip_section_numbers.py input.json output.json

# Validate content quality
/doc-quality-advisor output.json
```

---

## Common Errors and Fixes

### Error: "Undefined control sequence"
**Cause:** Special LaTeX characters not escaped: `#`, `$`, `%`, `&`, `_`, `{`, `}`  
**Fix:** Skill auto-escapes these UNLESS they're inside malformed tags

### Error: "File not found" (images)
**Cause:** Image path doesn't exist or is relative to wrong directory  
**Fix:** Use absolute paths or paths relative to content_library directory

### Error: Gibberish in tables (`\{\}\{text\}\{\}`)
**Cause:** Malformed table tag caused content to be double-escaped  
**Fix:** Ensure EVERY `[TABLE` has `:style:caption]` before markdown table

### Error: "Table ??" instead of "Table 3"
**Cause:** Semantic label parsing bug or missing second LaTeX pass  
**Fix:** Skill runs two LaTeX passes automatically - check label syntax

### Error: Double numbering ("2.1 2.1 Title")
**Cause:** JSON titles contain numbers that LaTeX also adds  
**Fix:** Remove numbers from JSON titles, let LaTeX number automatically

---

## Best Practices

1. **Always validate** content with `/doc-quality-advisor` before final compilation
2. **Use semantic labels** for tables/figures in reusable content (position-independent)
3. **Test image paths** before compilation (use absolute paths if unsure)
4. **Prefer markdown** over HTML (markdown is first-class, HTML is converted)
5. **Keep captions descriptive** - aids navigation and accessibility
6. **Reference every table/figure** in the text at least once
7. **Use consistent table styles** - `simple` for 80% of cases, accent colors for semantic meaning

---

## Quick Reference

| Element | Syntax | Example |
|---------|--------|---------|
| **Table** | `[TABLE:simple:caption]...[/TABLE]` | `[TABLE:simple:Pricing]\|A\|B\|\n\|--\|--\|\n\|1\|2\|\n[/TABLE]` |
| **Image** | `[IMAGE:path:caption:width:label]` | `[IMAGE:logo.png:Logo:0.5:logo]` |
| **Bold** | `**text**` | `**Important**` |
| **Italic** | `*text*` | `*emphasis*` |
| **Line break** | `<br/>` or `\n\n` | `Line 1<br/>Line 2` or `Para 1\n\nPara 2` |
| **Table ref** | `Table~\ref{tab:label}` | `Table~\ref{tab:pricing}` |
| **Figure ref** | `Figure~\ref{fig:label}` | `Figure~\ref{fig:arch}` |

---

**Questions?** Check `/Users/konstantinriegel/.claude/skills/latex-docs/skill.md` for full documentation.
