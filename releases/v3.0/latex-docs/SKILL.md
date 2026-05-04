---
name: latex-docs
description: Generate professional, branded SnapLogic documents in PDF format using LaTeX. Use this skill whenever users need to create technical documents, customer-facing materials, internal reports, proposals, white papers, or any professional documentation that requires consistent branding and polished formatting. Trigger when users mention creating documents, generating PDFs, writing technical docs, preparing customer materials, or when they describe content that should be formatted as a professional document. Also use when users want to iterate on existing documents to update versions or refine content.
---

# SnapLogic Professional Document Generation

Generate consistent, professionally branded documents for SnapLogic using LaTeX compilation. This skill handles the entire document lifecycle from content creation to final PDF delivery, complete with corporate branding, proper typography, and version management.

## When to Use This Skill

Use this skill when users need to:
- Create technical documentation with citations and references
- Generate customer-facing materials (proposals, solution docs, presentations)
- Produce internal reports or status updates
- Create any professional document that needs SnapLogic branding
- Update existing documents to new versions
- Compile multi-section documents with consistent formatting

**Key indicators:** User mentions "document", "PDF", "technical doc", "write up", "create a report", "proposal", "white paper", or describes content that should be professionally formatted.

## Document Types

Three document types are available, each optimized for different use cases:

### 1. Technical Documents
**Use for:** Architecture docs, API documentation, integration guides, technical specifications

**Characteristics:**
- Includes citation and reference management
- Minimal branding (header-only logos)
- Code-friendly formatting
- Emphasis on clarity and technical detail
- Conditional table of contents (≥3 sections)

### 2. General/Customer-Facing Documents
**Use for:** Proposals, solution documents, executive summaries, customer presentations

**Characteristics:**
- Full branding with title page
- Customer logo integration
- Management summary section
- Professional styling with SnapLogic brand colors
- Marketing-appropriate formatting
- Next steps and contact information sections

### 3. Internal Documents
**Use for:** Status reports, internal memos, project updates, planning docs

**Characteristics:**
- Simplified branding
- Focus on content over style
- Quick to generate and iterate
- Standard corporate document layout

## Document Defaults

All documents are generated with professional defaults optimized for international business:
- **Font size**: 10pt body text (compact, professional)
- **Paper size**: A4 (210mm × 297mm, international standard)
- **Typography**: Helvetica/Arial sans-serif for modern readability
- **Color scheme**: Full SnapLogic branding (navy, blue, jade, orange)

These can be overridden via command-line parameters if needed (e.g., 11pt for accessibility, letterpaper for US-only distribution).

## Document Generation Workflow

### Step 1: Understand the Request

First, determine:
1. **Document type** - Technical, general, or internal?
2. **Purpose** - What problem does this document solve?
3. **Audience** - Who will read this?
4. **Content scope** - How many sections/topics?
5. **Citations needed** - Technical docs require references?
6. **Customer context** - Customer name and logo?
7. **Images needed** - Will the document include diagrams or figures?

Ask clarifying questions if unclear. Understanding the context helps you generate appropriate content.

**Note:** Documents with images automatically include a **List of Figures** after the Table of Contents. Documents with tables include a **List of Tables**.


**📚 Complete Feature Documentation:** See `REFERENCE.md` for detailed table styles, box types, and advanced features.

**⚠️ Input Requirements:** See `CONTENT_REQUIREMENTS.md` for syntax validation and common errors.

## Content Input Requirements ⚠️

**CRITICAL:** All content must follow these exact formatting rules. Invalid syntax will cause compilation failures.

### Tables - REQUIRED Format

**Every table MUST use this exact syntax:**
```
[TABLE:style:caption]
| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |
[/TABLE]
```

**Required components:**
- `[TABLE:` - Opening tag (never use bare `[TABLE]`)
- `style` - Table style: `simple`, `minimal`, `accent-blue`, `accent-jade`, `accent-orange`, `bordered`, `status-colors`
- `caption` - Table caption text (or `_` for no caption)
- Markdown table content with `|` separators
- `[/TABLE]` - Closing tag

**Optional components (order matters):**
```
[TABLE:style:caption:emphasis:label]
```
- `emphasis` - Comma-separated: `first-bold`, `last-jade`, `last-orange`, `last-blue`, `total-row`, `widths=1,2,1.5`
- `label` - Semantic label for cross-references (e.g., `pricing-table`, `customer-refs`)

**Examples:**
```
[TABLE:simple:Customer List]                           ← Basic table
[TABLE:accent-blue:Pricing::pricing]                   ← With label, no emphasis
[TABLE:simple:Sales Data:first-bold,last-jade]         ← With emphasis
[TABLE:simple:Regional:first-bold,widths=1,2,3:sales]  ← Full syntax
```

**❌ NEVER use:**
- `[TABLE]` without style/caption - WILL BREAK
- `[TABLE:Customer List]` with only one parameter - INVALID
- Unmatched `[TABLE]` without `[/TABLE]` - WILL BREAK
- HTML `<table>` tags - NOT SUPPORTED

### Images - REQUIRED Format

**Every image MUST use this syntax:**
```
[IMAGE:path:caption:width:label]
```

**Required components:**
- `path` - File path (relative or absolute): `diagram.png`, `/tmp/chart.jpg`, `assets/images/logo.png`
- `caption` - Caption text (or `_` for no caption)

**Optional components:**
- `width` - Decimal value: `0.5` (50% width), `0.8` (80%), `1.0` (full width, default)
- `label` - Semantic label: `system-arch`, `pipeline-flow`

**Examples:**
```
[IMAGE:diagram.png:System Architecture:0.8:arch]       ← Full syntax
[IMAGE:logo.png:_:0.5]                                 ← No caption
[IMAGE:/tmp/chart.jpg:Performance::chart]              ← Default width
```

**Supported formats:** PNG, JPG, PDF (avoid SVG)

### Line Breaks and HTML

**✅ ALLOWED:**
- `\n` - Single newline (paragraph continuation)
- `\n\n` - Double newline (paragraph break)
- `<br/>` or `<br>` - Converted automatically to LaTeX line breaks

**❌ NOT ALLOWED:**
- `<p>`, `</p>` - Use `\n\n` instead
- `<div>`, `<span>` - NOT SUPPORTED
- `&nbsp;`, `&mdash;`, HTML entities - Use UTF-8 characters directly
- `<strong>`, `<em>` - Use markdown `**bold**`, `*italic*` instead

### Text Formatting

**✅ Use markdown:**
- `**bold text**` - Bold
- `*italic text*` - Italic
- `# Header` - Section headers (automatic numbering)
- `## Subheader` - Subsection headers
- `### Sub-subheader` - Subsubsection headers

**❌ Don't mix HTML and markdown:**
- NOT: `<strong>Bold</strong>` or `<b>Bold</b>`
- NOT: `<em>Italic</em>` or `<i>Italic</i>`
- NOT: `<h1>Header</h1>`

### Section Numbering

**⚠️ CRITICAL:** Do NOT include numbers in section titles. LaTeX adds them automatically.

**❌ WRONG:**
```json
{
  "title": "2.1 Architecture Components",  ← WILL CAUSE DOUBLE NUMBERING
  "content": "..."
}
```

**✅ CORRECT:**
```json
{
  "title": "Architecture Components",  ← LaTeX adds "2.1" automatically
  "content": "..."
}
```

If your content has numbered titles, remove them before compilation:
```bash
python3 scripts/strip_section_numbers.py input.json output.json
```

### Validation Checklist

Before compiling, verify:
- [ ] All `[TABLE:...]` tags have style AND caption
- [ ] All tables have matching `[/TABLE]` closing tags
- [ ] All `[IMAGE:...]` tags have at least path and caption
- [ ] No HTML tags except `<br/>` (which gets converted)
- [ ] Section titles have NO numbers (no "1.", "2.1", etc.)
- [ ] Text uses markdown (`**bold**`) not HTML (`<strong>`)

**If compilation fails:** Check the generated `.tex` file for malformed tags or escaped characters that shouldn't be escaped.


## Features Overview

This skill supports:

### Tables
```
[TABLE:style:caption:emphasis:label]
| Col1 | Col2 |
|------|------|
| Data | Data |
[/TABLE]
```
- **7 styles**: `simple` (default), `minimal`, `accent-blue`, `accent-jade`, `accent-orange`, `bordered`, `status-colors`
- **Emphasis**: `first-bold`, `last-jade`, `last-orange`, `last-blue`, `total-row`, `widths=N,N,N`
- **Semantic labels**: Reference with `Table~\ref{tab:label}`
- See `REFERENCE.md` for all styles and examples

### Images
```
[IMAGE:path:caption:width:label]
```
- Supported formats: PNG, JPG, PDF
- Width: `0.5` = 50%, `1.0` = full width
- Semantic labels: Reference with `Figure~\ref{fig:label}`

### Highlight Boxes
```
[BOX:type]content[/BOX]
[KPI:color|title|value]
[FEATURE:color|title]content[/FEATURE]
```
- Types: `info`, `success`, `warning`, `note`
- Colors: `navy`, `blue`, `jade`, `orange`
- See `REFERENCE.md` for detailed styling options

### Lists and Headers
- Multi-level lists (4 levels deep, 3-space indent)
- 5-level header hierarchy (3 levels in TOC)
- Markdown formatting: `**bold**`, `*italic*`

### Cross-References
- Numeric: "Section 2.1", "Table 3", "Figure 2"
- Semantic: `Section~\ref{sec:label}`, `Table~\ref{tab:label}`, `Figure~\ref{fig:label}`
- Auto-generated clickable links

## Multi-File Document Projects (Large RFPs)

For large documents like RFPs with multiple content files and asset folders, use the **content_library** structure:

### Directory Structure

```
content_library/
├── documents/<project_name>/       # Project-specific workspace
│   ├── manifest.json              # Document assembly blueprint
│   ├── section_*.json             # Custom section content files
│   └── final_document.json        # Assembled final JSON (generated)
│
├── assets/images/<project_name>/  # Project-specific images
│   ├── architecture_diagram.png
│   ├── workflow.png
│   └── screenshots/
│
└── library/                       # Reusable content blocks (shared)
    ├── platform/                  # Platform overviews, architecture
    ├── security/                  # Security & compliance sections
    ├── appendices/                # Technical appendices, user stories
    └── use_cases/                 # Standard use case descriptions
```

### Workflow for Large Documents

**1. Create Project Directory**
```bash
mkdir -p content_library/documents/<project_name>
mkdir -p content_library/assets/images/<project_name>
```

**2. Break Content into Logical Files**
```
content_library/documents/airbus_vendor_profile/
├── section_01_company_profile.json
├── section_02_technical_capabilities.json
├── section_03_requirements_matrix.json
├── section_04_implementation.json
└── appendices.json
```

**3. Store Images in Project Assets**
```
content_library/assets/images/airbus_vendor_profile/
├── architecture_overview.png
├── platform_deployment_model.png
└── screenshots/
    ├── snapgpt_demo_01.png
    └── snapgpt_demo_02.png
```

**4. Reference Images with Relative Paths**

In your JSON content files, use paths relative to `content_library`:
```json
{
  "content": "The architecture is shown below.\n\n[IMAGE:assets/images/airbus_vendor_profile/architecture_overview.png:System Architecture:0.8:arch-overview]"
}
```

**Image Path Resolution Order:**
1. `content_library/` directory (checked first)
2. Skill root directory
3. Relative to assets_dir

**5. Assemble Final Document**

Merge all section files into a single JSON:
```python
# Manual assembly or use a manifest-based assembler
import json

final = {
    "title": "Vendor Profile",
    "sections": []
}

# Load each section file
with open('content_library/documents/airbus/section_01.json') as f:
    final['sections'].append(json.load(f))
# ... repeat for all sections

# Save assembled document
with open('content_library/documents/airbus/final_document.json', 'w') as f:
    json.dump(final, f, indent=2)
```

**6. Compile Final Document**
```bash
python3 scripts/compile_document.py \
  content_library/documents/airbus/final_document.json \
  output/airbus_vendor_profile.pdf \
  general
```

### Best Practices for Multi-File Projects

**Content Organization:**
- One JSON file per major section (5-10 sections typical)
- Keep files under 500 lines for maintainability
- Use semantic file names: `section_02_technical_capabilities.json` not `part2.json`

**Image Management:**
- Project images: `assets/images/<project_name>/`
- Shared images: `assets/images/shared/` or `library/assets/`
- Use descriptive names: `architecture_overview.png` not `img1.png`

**Version Control:**
- Commit individual section files (easier to track changes)
- Gitignore assembled `final_document.json` (regenerate from source)
- Gitignore generated PDFs

**Reusable Content:**
- Extract frequently-used sections to `library/`
- Examples: security compliance, platform overview, support model
- Reference library content via manifest (future feature)

### Troubleshooting Multi-File Projects

**Issue: Image not found**
- Verify path is relative to `content_library/`
- Check: `content_library/assets/images/<project>/image.png` exists
- Images are copied automatically during compilation

**Issue: Section numbering incorrect**
- Ensure sections are in correct order in `final_document.json`
- Do NOT include numbers in section titles (LaTeX auto-numbers)

**Issue: Large assembly time**
- Consider splitting into multiple PDF documents
- Max recommended: 50 sections, 100 images per document

**Issue: Cross-references between section files**
- Use semantic labels (`label` parameter) not numeric references
- Labels work across all sections in final assembled document

### Example: Large RFP Structure

```
content_library/documents/enterprise_rfp_2026/
├── 01_executive_summary.json
├── 02_company_profile.json
├── 03_technical_architecture.json
├── 04_security_compliance.json
├── 05_requirements_response.json    # 20+ pages
├── 06_implementation_plan.json
├── 07_pricing.json
├── 08_appendices.json
├── final_rfp.json                   # Assembled (generated)
└── README.md                        # Project notes

content_library/assets/images/enterprise_rfp_2026/
├── architecture/
│   ├── overview.png
│   ├── deployment.png
│   └── ha_model.png
├── screenshots/
│   ├── dashboard_01.png
│   └── monitoring.png
└── diagrams/
    ├── workflow.png
    └── integration_flow.png
```

**See Also:**
- `content_library/README.md` - Content library documentation
- `REFERENCE.md` - Detailed feature documentation


## Version Management

Follow this versioning scheme:

- **0.1 - 0.9**: Draft versions during initial creation and iteration
- **1.0**: First release-ready version (ask user before assigning)
- **1.1 - 1.9**: Minor updates to released version
- **2.0, 3.0, etc.**: Major revisions or significant content changes

**When to ask about release versions:**
- Moving from 0.x to 1.0 - Always ask
- Moving from 1.x to 2.0 - Always ask
- Incrementing minor versions (1.1 → 1.2) - No need to ask

Example dialogue:
> "I've made the requested changes. This feels pretty solid - should I mark this as version 1.0 (release-ready), or keep it as 0.4 for more iteration?"

## Customization Options

Users can optionally customize:

### Font Size
- **10pt**: Standard, professional (default)
- **10pt**: Slightly larger, easier to read
- **12pt**: Large, accessibility-focused

### Paper Size
- **a4paper**: International standard (default)
- **letterpaper**: US standard

### Color Scheme
- **default**: Full SnapLogic branding (default)
- **monochrome**: Black and white (for printing)
- **high_contrast**: Accessibility-focused

Example with customization:
```python
result = subprocess.run([
    sys.executable,
    str(skill_dir / "scripts" / "compile_document.py"),
    content_file,
    output_path,
    doc_type,
    "--font-size", "12pt",
    "--color-scheme", "monochrome"
], ...)
```

Most users won't need customization - defaults work well.

## Handling Errors

If compilation fails:

1. **Check LaTeX error** - Look at the error output from `compile_document.py`
2. **Common issues:**
   - Special characters not escaped (fix in content)
   - Missing logo files (verify paths)
   - Invalid LaTeX syntax in content (escape `&`, `%`, `$`, `#`, `_`, etc.)
   - Bibliography errors (check BibTeX format)

3. **Debugging:**
   - The working directory is preserved on error
   - Check `/tmp/snaplogic_doc_*/document.tex` to see generated LaTeX
   - Read `/tmp/snaplogic_doc_*/document.log` for detailed error

4. **Fix and retry:**
   - Correct the issue in the JSON structure
   - Rerun compilation

## Tips for Great Documents

### Content Quality
- **Be concise**: Every sentence should add value
- **Use structure**: Headings, lists, and sections improve readability
- **Think about flow**: Each section should lead naturally to the next
- **Proofread**: Check for typos and grammatical errors

### Technical Documents
- **Cite sources**: Every technical claim should have a reference
- **Be precise**: Use exact terminology and specifications
- **Include examples**: Code snippets, diagrams, or sample data help understanding
- **Validate facts**: Double-check technical details before including

### Customer-Facing Documents
- **Focus on value**: What problem does this solve for the customer?
- **Use their language**: Match the customer's terminology and context
- **Be professional**: Polished, error-free, and visually consistent
- **Include next steps**: Make it clear what happens next

### Internal Documents
- **Get to the point**: Internal docs should be scannable
- **Use bullet points**: Lists are easier to digest than paragraphs
- **Include dates and owners**: Who does what by when?
- **Keep updated**: Internal docs should reflect current state

## Section Structure Guidelines

### Terminology

- **Section** (Level 1): Top-level numbered sections (1, 2, 3...) - Main topics
- **Subsection** (Level 2): Numbered subsections (1.1, 1.2, 2.1...) - Subtopics within sections
- **Subsubsection** (Level 3): Numbered subsubsections (1.1.1, 1.2.1...) - Details within subsections
- **Paragraph/Subparagraph** (Level 4-5): NOT numbered, run-in style - Fine details

### Section Count Guidelines

**Top-level sections (1, 2, 3...):**
- **1-2 sections**: Very brief docs - skip table of contents
- **3-10 sections**: Sweet spot for most documents - include TOC
- **11-15 sections**: Longer docs - ensure good structure
- **16-30 sections**: Maximum - warn user about readability, suggest splitting
- **30+ sections**: Error - too long, must be split into multiple documents

**Subsections per section (1.1, 1.2, 1.3...):**
- **0-3 subsections**: Normal, well-focused section
- **4-6 subsections**: Acceptable for complex topics
- **7+ subsections**: Consider splitting into multiple top-level sections

**Content length guidelines:**
- **Section (without subsections)**: 300-500 words optimal, max 1000 words
- **Section (with subsections)**: Can be longer, subsections should be 200-400 words each
- **Subsection**: 200-400 words optimal
- **Subsubsection**: 100-200 words (use sparingly)

### Example Structure

```json
{
  "sections": [
    {
      "title": "Professional Services & Partner Network",  // Section 1.6
      "content": "Overview paragraph introducing the section topic...",
      "subsections": [
        {
          "title": "Professional Services",  // Subsection 1.6.1
          "content": "200-400 words about PS organization, capabilities..."
        },
        {
          "title": "Partner Network",  // Subsection 1.6.2
          "content": "200-400 words about partner ecosystem..."
        },
        {
          "title": "SnapGPT AI",  // Subsection 1.6.3
          "content": "200-400 words about AI capabilities..."
        }
      ]
    }
  ]
}
```

The skill automatically includes/excludes table of contents based on section count.

## Automatic Features

The following features are automatically enabled when appropriate:

- **Table of Contents**: Included when document has 3+ sections
- **List of Figures**: Included when document contains any images with captions
- **Bibliography**: Included for technical documents with citations

No special configuration needed - the compiler detects and enables these automatically.

## Brand Assets

The skill uses official SnapLogic branding:

**Colors:**
- Navy (#001934) - Primary headers
- Blue (#4073FF) - Primary brand color
- Jade (#42A5D2) - Accents
- Orange (#FF7D3F) - Call-to-actions

**Logos:**
- Blue logo for title pages and headers
- White logo for dark backgrounds (if needed)

**Typography:**
- Helvetica for headings and body (LaTeX helvet package)
- Clean, professional, readable

All branding is applied automatically - you don't need to specify colors or fonts.

## Example Usage

**Document with images:**
```python
document = {
    "title": "System Architecture Overview",
    "version": "1.0",
    "sections": [
        {
            "title": "Overview",
            "content": "Our system architecture consists of three main layers:\\n\\n[IMAGE:architecture_diagram.png:System Architecture Diagram:0.8]\\n\\nAs shown above, the presentation, business logic, and data layers are clearly separated."
        },
        {
            "title": "API Design",
            "content": "The API follows REST principles. Below are two key diagrams:\\n\\n[IMAGE:api_flow.png:API Request Flow:0.6]\\n\\nAnd the authentication sequence:\\n\\n[IMAGE:auth_diagram.png:Authentication Sequence:0.6]"
        },
        {
            "title": "Performance Metrics",
            "content": "Current performance metrics show excellent results:\\n\\n[IMAGE:metrics_chart.png:_:0.7]\\n\\nNote: This chart has no caption (using _ placeholder)."
        }
    ]
}
```

**Simple internal document:**
```python
document = {
    "title": "Q2 Platform Updates",
    "version": "1.0",
    "sections": [
        {
            "title": "Overview",
            "content": "Summary of Q2 platform improvements..."
        },
        {
            "title": "Performance Enhancements",
            "content": "Details on performance work..."
        },
        {
            "title": "New Features",
            "content": "List of new capabilities..."
        }
    ],
    "next_steps": [
        "Roll out to production by end of Q2",
        "Conduct customer training sessions"
    ]
}
```

**Customer-facing proposal:**
```python
document = {
    "title": "Integration Solution Proposal",
    "subtitle": "Modernizing Data Workflows with SnapLogic",
    "customer_name": "Acme Corporation",
    "customer_logo": "/tmp/acme_logo.png",
    "version": "1.0",
    "management_summary": "This proposal outlines a comprehensive approach...",
    "sections": [
        {"title": "Current State Analysis", "content": "..."},
        {"title": "Proposed Solution", "content": "..."},
        {"title": "Implementation Timeline", "content": "..."},
        {"title": "ROI Analysis", "content": "..."}
    ],
    "next_steps": [
        "Schedule technical deep-dive session",
        "Provide access to SnapLogic trial environment",
        "Finalize statement of work"
    ],
    "contacts": [
        {
            "name": "John Smith",
            "role": "Solutions Engineer",
            "email": "john.smith@snaplogic.com"
        }
    ],
    "links": {
        "documentation": "https://docs-snaplogic.atlassian.net/",
        "academy": "https://academy.snaplogic.com/"
    }
}
```

## Troubleshooting

**"Document compilation failed"**
- Check content for unescaped special characters
- Verify logo file paths exist
- Check LaTeX error in preserved working directory

**"Customer logo not found"**
- Verify file path is absolute
- Check file format (PNG, PDF, or SVG)
- Ensure logo file is readable

**"Bibliography errors"**
- Verify citation keys exist in `references.bib`
- Check BibTeX syntax in bibliography file
- Ensure bibliography file is not corrupted

**"Document is too long"**
- Reduce number of sections (maximum 30)
- Consider splitting into multiple documents
- Focus content on key points only

**"Image not found" errors**
- Verify image file path is correct (absolute or relative)
- Check file actually exists at that location
- Ensure file format is supported (PNG, JPG, PDF - not SVG)
- Check file permissions are readable

**Images don't appear or look wrong**
- SVG files need conversion to PNG first (use `convert` or online tool)
- Try adjusting width parameter (0.3 to 0.9 recommended)
- Very large images may cause LaTeX memory issues - resize before embedding
- Check image isn't corrupted by opening it separately

## For Agents: Required Workflow

**⚠️ CRITICAL**: When generating documents, you MUST follow this workflow:

### Standard Workflow (Customer-Facing Documents)
1. **Generate** content JSON structure
2. **Validate** with `/doc-quality-advisor path/to/document.json` (BEFORE compiling PDF)
3. **Fix** CRITICAL issues (broken references, structural problems)
4. **Fix** WARNING issues (unreferenced figures/tables, poor balance)
5. **Re-validate** until score ≥85 or no CRITICAL/WARNING issues remain
6. **Compile** final PDF: `python3 scripts/compile_document.py document.json output.pdf general`
7. **Report** quality score to user

### Quick Workflow (Internal Documents Only)
If user explicitly requests "quick internal doc" or "draft":
1. Generate content JSON
2. Compile PDF directly
3. *Optionally* validate if time allows

### Why This Matters
- **Professional credibility**: Unreferenced figures/tables look unfinished
- **Usability**: Broken cross-references frustrate readers
- **Completeness**: The validator catches missing content
- **Consistency**: Ensures all documents meet SnapLogic standards

### Example
```
# After generating content to airbus_proposal.json
/doc-quality-advisor airbus_proposal.json

# Review output:
# Overall Score: 78/100
# 🔴 CRITICAL: None
# 🟡 WARNING: Figure 3 never referenced, Table 2 never referenced

# Fix warnings by adding references
# Then re-validate
/doc-quality-advisor airbus_proposal.json

# Score now 92/100 - safe to compile
python3 scripts/compile_document.py airbus_proposal.json airbus_proposal.pdf general
```

**DO NOT SKIP** validation for customer-facing documents (proposals, technical docs, solution documents). This is not optional.

## Remember

- Hide LaTeX complexity from users - they should only see the final PDF
- Always start with version 0.1
- Research content thoroughly - accuracy matters
- Use appropriate document type for the use case
- **Validate all customer-facing documents before final compilation**
- Iterate based on feedback until user is satisfied
- Ask questions if requirements are unclear

The goal is professional, branded documents that make SnapLogic look good and communicate effectively. Quality over speed.
