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

## Advanced Features

### Cross-References (Auto-Generated) ✅

The skill automatically converts text references into clickable hyperlinks:

**Section References:**
- Write: "For more details, see Section 2.1"
- Renders as: Black clickable text that jumps to Section 2.1
- Supports: "Section X", "Section X.Y", "Section X.Y.Z" (any depth)

**Figure References:**
- Write: "As shown in Figure 3, the architecture..."
- Renders as: Black clickable text that jumps to Figure 3
- All figures must have captions to be referenceable
- LaTeX automatically numbers figures (1, 2, 3...)

**Table References:**
- Write: "The data in Table 2 shows..."
- Renders as: Black clickable text that jumps to Table 2
- All tables must be wrapped with `[TABLE:caption]...[/TABLE]` syntax
- LaTeX automatically numbers tables (1, 2, 3...)

**How It Works:**
- Requires two LaTeX compilation passes (handled automatically)
- First pass: Writes figure/table/section labels to `.aux` file
- Second pass: Resolves `\ref{}` commands to actual numbers
- Uses non-breaking space `~` to prevent line breaks (e.g., `Figure~\ref{fig:3}`)

**Best Practices:**
- Reference every figure and table at least once in the text
- Use specific references ("Section 2.1") not vague ones ("as mentioned above")
- Place references near the target (within same section preferred)
- Use forward references sparingly, prefer backward references
- Tables: Place reference before or after table, not in different section

### Header Hierarchy (5 Levels) ✅

Support for deep document structure following IEEE/academic best practices:

1. **Section** (`\section`) - Main topics, numbered (1, 2, 3...)
2. **Subsection** (`\subsection`) - Subtopics, numbered (2.1, 2.2...)
3. **Subsubsection** (`\subsubsection`) - Details, numbered (2.1.1, 2.1.2...)
4. **Paragraph** (`\paragraph`) - Fine details, NOT numbered (run-in style)
5. **Subparagraph** (`\subparagraph`) - Finest level, NOT numbered (run-in style)

**Visual Styling:**
- **Levels 1-3**: Large → large → normal size, colored (navy/blue), bold, numbered
- **Levels 4-5**: Normal size, black, bold/italic, run-in style (inline with text), NOT numbered

**Markdown Format in Content:**
```
# Level 1: Section Title
## Level 2: Subsection Title
### Level 3: Subsubsection Title
**Level 4 Header (Paragraph): Title Here**
**Level 5 Header (Subparagraph): Title Here**
```

**Table of Contents and Numbering:**
- TOC displays levels 1-3 only (Section → Subsection → Subsubsection)
- Numbering depth matches TOC depth (levels 1-3 numbered, 4-5 not numbered)
- This follows professional documentation standards (IEEE, arc42)
- **Why?** Prevents confusion from numbered sections (2.1.3.4.5) that don't appear in TOC
- Levels 4-5 use run-in style: bold/italic text inline with paragraph (not standalone headers)

**Best Practices:**
- Most professional documents use 3 levels maximum
- Levels 4-5 should be rare (deep nesting indicates structure problems)
- If you need level 4-5 frequently, consider restructuring the document
- Run-in style for 4-5 is intentional: they're emphasis, not true section headers

### Lists (Multi-Level Support) ✅

Support for nested lists up to 4 levels deep with proper LaTeX rendering:

**Numbered Lists (Ordered):**
```
1. First main item
   1. First sub-item (3-space indent)
      1. First sub-sub-item (6-space indent)
         1. Deep item (9-space indent)
2. Second main item
```

**Bullet Lists (Unordered):**
```
- Main bullet
  - Sub-bullet (3-space indent)
    - Sub-sub-bullet (6-space indent)
      - Deep bullet (9-space indent)
```

**Mixed Lists:**
```
1. Ordered item
   - Unordered sub-item
   - Another sub-item
      1. Nested numbered item
2. Second ordered item
```

**Indentation Rules:**
- Use exactly **3 spaces** per nesting level
- Level 1: no indent
- Level 2: 3 spaces
- Level 3: 6 spaces
- Level 4: 9 spaces (maximum recommended depth)

**Rendering:**
- Numbered lists use LaTeX `enumerate` environment
- Bullet lists use LaTeX `itemize` environment
- LaTeX automatically handles different numbering styles (1, a, i, etc.) per level
- Bullet symbols change automatically per level (•, ◦, ▪, etc.)

### Tables (Professional Formatting) ✅

Support for professional tables with automatic numbering, captions, and cross-references:

**Syntax:**
```
[TABLE:style:caption]
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| More     | Data     | Here     |
[/TABLE]
```

**Key Features:**
- **Automatic numbering**: Tables numbered sequentially (Table 1, Table 2, etc.)
- **Caption placement**: Appears ABOVE table (professional standard per Chicago/IEEE)
- **Caption spacing**: 10pt space below caption (prevents cramped appearance)
- **List of Tables**: Automatically generated when document contains tables (configurable)
- **Cross-references**: Reference with "Table N" in text (becomes clickable)
- **Equal column widths**: Columns automatically sized to fit page width
- **Text wrapping**: Multi-line text supported in cells with proper alignment
- **Multiple styles**: 7 different table styles for different purposes

**Caption Options:**
- Descriptive caption: `[TABLE:simple:Platform Tier Comparison]`
- Empty caption: `[TABLE:simple:_]` (still numbered, just no caption text)

**Table Styles:**

1. **simple** (default)
   - Navy header with white text
   - Alternating row colors (white/light gray)
   - Use: General-purpose tables, comparison tables, data tables
   - 80% of use cases

2. **minimal**
   - Horizontal rules only (booktabs style: toprule, midrule, bottomrule)
   - No colored backgrounds
   - Bold headers only
   - Use: Technical specifications, academic docs, dense numeric data
   - When: Color would be distracting

3. **accent-blue**
   - Blue header with white text
   - White background rows
   - Use: Informational tables, API endpoints, feature highlights
   - Semantic: Information/neutral emphasis

4. **accent-jade**
   - Jade (green) header with white text
   - White background rows
   - Use: Recommended configurations, success metrics, best practices
   - Semantic: Success/positive/recommended

5. **accent-orange**
   - Orange header with white text
   - White background rows
   - Use: Warning tables, critical maintenance, attention-needed items
   - Semantic: Warning/urgent/cost data

6. **bordered**
   - Light gray header with navy text
   - All cells have visible borders
   - White background
   - Use: Reference tables, error code lookups, API specs
   - When: Clear cell boundaries aid scanning

7. **status-[colors]**
   - White header with navy text
   - Row colors indicate semantic state
   - First column bold for row labels
   - Syntax: `status-jade,orange,blue` (comma-separated colors for each row)
   - Colors: jade (success), orange (warning), blue (info), gray (neutral), white (default)
   - Use: Project status, timeline tables, requirement tracking
   - When: Each row has a semantic meaning

**Style Selection Guide:**
```
| Need | Use Style | Example |
|------|-----------|---------|
| Default/general | simple | Feature comparison |
| Technical specs | minimal | System requirements |
| Information | accent-blue | API endpoints |
| Recommended | accent-jade | Best practices |
| Warnings | accent-orange | Maintenance windows |
| Reference/lookup | bordered | Error codes |
| Status tracking | status-[colors] | Task progress |
```

**Cell Text Formatting:**
- Top-aligned cells (standard for professional documents)
- Left-aligned text with no indentation on wrapped lines
- LaTeX column spec: `>{\setlength{\parindent}{0pt}}p{width}`
- Proper text wrapping without offset/indentation issues

**Best Practices:**
- Always provide descriptive captions (aids accessibility and navigation)
- Reference every table in the text ("As shown in Table 2...")
- Place reference near the table (same section preferred)
- Keep tables focused (5-10 columns maximum for readability)
- Use bold for header row emphasis (automatic)
- Consider landscape mode for very wide tables (future feature)

**Example:**
```json
{
  "sections": [
    {
      "title": "Pricing Comparison",
      "content": "We offer three pricing tiers as detailed in Table 1 below.\n\n[TABLE:simple:Platform Tier Comparison]\n| Feature | Basic | Professional | Enterprise |\n|---------|-------|--------------|------------|\n| API Calls | 10K | 100K | Unlimited |\n| Support | Email | Email + Chat | 24/7 Phone |\n[/TABLE]\n\nTable 1 shows our competitive pricing structure."
    }
  ]
}
```

### Professional Headers and Footers ✅

Headers and footers automatically configured based on document type following professional typography standards (Chicago Manual of Style, APA, IEEE, Bringhurst):

**Customer-Facing Documents (doc_type: "general"):**
- **Header**: None (clean, uncluttered presentation)
- **Footer**: Date (left) | Page X of Y (center) | Version (right)
- **Font**: 8-9pt footnotesize
- **Rules**: No lines (modern, minimal aesthetic)
- **Rationale**: Proposals and customer docs prioritize clean layout

**Technical Documents (doc_type: "technical"):**
- **Header**: _Document Title_ (left, italic) | Page N (right)
- **Header rule**: 0.4pt line for structure
- **Footer**: Date | Version (centered)
- **Font**: 9pt for header, 8pt for footer
- **Rationale**: Navigation-focused for reference materials

**Internal Documents (doc_type: "internal"):**
- **Header**: Document Title (left) | Page N (right)
- **Header rule**: 0.4pt line
- **Footer**: Date (centered)
- **Rationale**: Quick scanning for reports and memos

**Special Pages:**
- Title page, Table of Contents, List of Figures, List of Tables use `plain` style
- **Plain style**: No headers, no footers, no rules (clean presentation)
- First page of sections inherits global page style

**Typography Details:**
- Header font: `\small` (approximately 80-90% of body text)
- Footer font: `\footnotesize` (approximately 70-80% of body text)
- With 11pt body text: headers are 9-10pt, footers are 8-9pt
- Follows professional publishing standards for running heads

**Customization:**
- Headers/footers automatically generated based on document metadata
- Uses `fancyhdr` LaTeX package for precise control
- Landscape pages (future) will rotate headers/footers appropriately

### Highlight Boxes (Three Types) ✅

The skill provides three distinct types of highlight boxes, each optimized for different content and use cases. All boxes follow professional documentation best practices with proper spacing, padding, and visual hierarchy.

#### 1. Standard Highlight Boxes (Info, Success, Warning, Note)

**Purpose:** Multi-sentence explanatory content, technical notes, warnings, status updates

**Visual Design:**
- Subtle 10% opacity colored backgrounds
- Colored 2pt top rule for visual distinction
- No border (clean, minimalist)
- 15pt padding (comfortable reading)
- Full-width (maximizes readability)

**Syntax in content:**
```
[BOX:info]
**Title**: Your content here with multiple sentences. Can include **bold**, *italic*, lists, etc.
[/BOX]

[BOX:success]
**Operation Complete**: All systems verified and deployed successfully.
[/BOX]

[BOX:warning]
**Critical**: This operation cannot be undone. Backup all data before proceeding.
[/BOX]

[BOX:note]
**Reference**: For detailed API documentation, see docs.snaplogic.com/api
[/BOX]
```

**Colors:**
- `info`: Blue (#4073FF) - informational content
- `success`: Jade (#42A5D2) - positive outcomes, completions
- `warning`: Orange (#FF7D3F) - cautions, important notices
- `note`: Navy (#001934) - references, side information

**Best Practices:**
- Use for content requiring careful reading (2+ sentences)
- Appropriate for technical documentation and explanations
- Print-friendly subtle backgrounds
- Use 3-5 boxes per page maximum to maintain impact

#### 2. KPI Metric Boxes

**Purpose:** Single metrics, dashboard-style statistics, key numbers that need visual impact

**Visual Design:**
- Solid bold colored backgrounds with white text
- Compact size (80pt height)
- Centered layout for numbers
- Display 4 boxes per row horizontally
- Minimal spacing between boxes (0.006\linewidth)

**Syntax in content:**
```
[KPI:navy|Active Pipelines|1,247]
[KPI:blue|Integrations|328]
[KPI:jade|Success Rate|98.5%]
[KPI:orange|Avg Response|2.3s]
```

**Format:** `[KPI:color|title|value]`
- **color**: navy, blue, jade, or orange
- **title**: Short label (1-3 words MAX - will wrap if longer!)
- **value**: The metric/number to display (1-10 characters MAX)

**⚠️ CRITICAL CONTENT LIMITS:**
- **Title**: 1-3 words, 15 characters maximum (e.g., "Total Users", "ROI", "Uptime")
- **Value**: 1-10 characters maximum (e.g., "500+", "181%", "2.3s", "114/114")
- **Box height**: 80pt fixed - content WILL overflow if too long
- **Box width**: Narrow (0.18\linewidth) - long titles wrap badly

**WRONG - TOO LONG (will overflow/wrap):**
```
❌ [KPI:blue|Supported Sources|Informatica + Talend + SSIS]
❌ [KPI:jade|Validation|Record-by-record output comparison]
❌ [KPI:orange|RFP Requirement T-01|Fully Compliant]
```

**CORRECT - SHORT (will fit properly):**
```
✅ [KPI:blue|Sources|4 Tools]
✅ [KPI:jade|Validation|Row-Level]
✅ [KPI:orange|T-01|Pass]
```

**Typography:**
- Title: \large (\~14.4pt) bold white text
- Value: \Huge (\~24.88pt) bold white text

**Layout Mathematics:**
- Box width: 0.18\linewidth for minipage content
- Total width including padding: 0.18\linewidth + 30pt (15pt padding × 2)
- Spacing: 0.006\linewidth between boxes
- 4 boxes fit per row: 4(0.18 + padding) + 3(spacing) ≈ 0.95\linewidth

**Best Practices:**
- Use for single numbers/metrics ONLY (not sentences or phrases)
- Display 4 metrics in a row for dashboard effect
- Maximum 4-8 KPI boxes per page
- Vibrant colors acceptable here (short content, high impact needed)
- Perfect for executive summaries and status reports
- If your content is longer than 1-3 words, use a Standard or Feature box instead

#### 3. Feature Card Boxes

**Purpose:** Marketing-style feature highlights, value propositions, 2-4 sentence descriptions

**Visual Design:**
- Subtle 15% opacity colored backgrounds with black text
- No border or top rule (clean, modern)
- Larger size (130pt height × 0.265\linewidth width)
- Display 3 boxes per row horizontally
- 15pt padding (matches standard boxes)

**Syntax in content:**
```
[FEATURE:blue|Cost Savings]
Predictable subscription pricing with automated migration tools reducing effort by 40-70%. Forrester confirms 181% ROI over 3 years.
[/FEATURE]

[FEATURE:jade|Faster Delivery]
Visual development and AI-generated pipelines reduce integration time by 60-80% compared to traditional tools.
[/FEATURE]

[FEATURE:orange|Quick Onboarding]
New developers productive in days, not months. Self-paced training accelerates team enablement.
[/FEATURE]
```

**Format:** `[FEATURE:color|title]content[/FEATURE]`
- **color**: navy, blue, jade, or orange
- **title**: Feature name (2-4 words MAX)
- **content**: 2-3 sentences describing the feature/benefit

**⚠️ CRITICAL CONTENT LIMITS:**
- **Title**: 2-4 words, 25 characters maximum (e.g., "Enterprise Security", "Cost Savings")
- **Content**: 2-3 sentences, 40-60 words MAX (~200-350 characters including spaces)
- **Box height**: 130pt fixed - longer content WILL overflow
- **Line count**: ~6-7 lines at 11pt font - content must fit within this

**WRONG - TOO LONG (will overflow):**
```
❌ [FEATURE:blue|SnapGPT — AI Co-Pilot (On-Premises Compatible)]
SnapGPT generates working integration pipelines from plain-language descriptions,
auto-documents every pipeline and mapping, suggests field transformations, and 
diagnoses production errors. It operates from the SnapLogic Manager and processes 
only pipeline metadata — never AH operational data. No other on-premises-compatible 
integration platform offers generative AI development assistance.
[/FEATURE]
(6 sentences, 350+ chars - TOO LONG, WILL OVERFLOW!)
```

**CORRECT - CONCISE (will fit):**
```
✅ [FEATURE:blue|AI-Powered Development]
SnapGPT generates pipelines from plain language, auto-documents code, and 
diagnoses errors. Only AI assistant available in on-premises integration tools.
[/FEATURE]
(2 sentences, ~160 chars - perfect fit!)
```

**Typography:**
- Title: \large (\~14.4pt) bold black text
- Content: \normalsize (11pt) regular black text
- Both use document base font size for readability

**Layout Mathematics:**
- Box width: 0.265\linewidth for minipage content
- Total width including padding: 0.265\linewidth + 30pt (15pt padding × 2)
- Spacing: 0.0065\linewidth between boxes
- 3 boxes fit per row: 3(0.265 + padding) + 2(spacing) ≈ 0.97\linewidth

**Best Practices:**
- Use for feature highlights that need 2-4 sentences
- Display 3 cards per row for consistency
- Maximum 6-9 feature cards per page (2-3 rows)
- Subtle colors with black text for readability (follows professional standards)
- Appropriate for proposals, solution documents, marketing materials
- Content needs careful reading, so body text size is essential

#### Choosing the Right Box Type

**Use Standard Boxes (info/success/warning/note) when:**
- Content is technical documentation or explanations
- You need 5+ boxes on the same page
- Content will be printed (subtle backgrounds print better)
- Readers need to carefully read multi-sentence content

**Use KPI Boxes when:**
- Displaying single metrics or numbers
- Creating dashboard-style reports
- Executive summaries highlighting key stats
- Maximum visual impact needed for metrics
- Content is scannable (just numbers, no reading required)

**Use Feature Boxes when:**
- Marketing-style feature highlights (2-4 sentences)
- Value propositions and benefits
- Capability overviews
- Proposals and customer-facing documents
- Content needs to be scannable but also readable

#### Box Sizing and Layout Best Practices

**Why the specific widths matter:**

All box widths are calculated using proper CSS box model mathematics:
- LaTeX `\fboxsep` padding adds to BOTH sides of content
- Must account for padding in width calculations to prevent wrapping
- Formula: `available_space = linewidth - (num_boxes × 2 × padding)`

**KPI boxes (4 across):**
```
Available = 468pt - (4 boxes × 30pt padding) = 348pt
Per box content = (348pt - 3 gaps) / 4 boxes = 85pt ≈ 0.18\linewidth
```

**Feature boxes (3 across):**
```
Available = 468pt - (3 boxes × 30pt padding) = 378pt
Per box content = (378pt - 2 gaps) / 3 boxes = 124pt ≈ 0.265\linewidth
```

**If boxes wrap to next line:**
- Padding/spacing calculations are wrong
- Reduce minipage width slightly (try 0.01\linewidth less)
- Or reduce padding/spacing

#### Accessibility and Professional Standards

**All boxes follow these standards:**
- ✅ WCAG AA contrast compliance (tested)
- ✅ Subtle backgrounds (10-15% opacity) for standard/feature boxes
- ✅ Bold backgrounds only for short content (KPI boxes)
- ✅ Body text size (11pt) for content requiring careful reading
- ✅ Larger text (14pt+) only for titles and metrics
- ✅ Print-friendly (subtle colors print well in grayscale)
- ✅ Consistent padding (15pt) across all box types
- ✅ Professional documentation standards (IEEE, arc42, Google Style Guide)

#### Examples

**Dashboard-style report:**
```
**Q4 2025 Platform Performance**

[KPI:navy|Total Users|12,450]
[KPI:blue|Pipeline Runs|2.4M]
[KPI:jade|Uptime|99.97%]
[KPI:orange|Data Processed|847TB]

[BOX:info]
**Quarter Highlights**: Platform adoption grew 34% quarter-over-quarter with significant expansion in financial services and healthcare verticals.
[/BOX]
```

**Customer-facing proposal:**
```
**Why SnapLogic?**

[FEATURE:blue|Enterprise Security]
Role-based access, SSO, MFA, and audit trails built into platform architecture. SOC 2 Type II certified.
[/FEATURE]
[FEATURE:jade|Data Sovereignty]
All processing occurs within customer data centers. No operational data leaves network boundary.
[/FEATURE]
[FEATURE:orange|Rapid Deployment]
Average time-to-value of 3.2 months from contract to first production deployment.
[/FEATURE]
```

**Technical documentation:**
```
[BOX:warning]
**Breaking Change**: The legacy authentication endpoint `/api/v1/auth` will be deprecated in version 3.0. Migrate to `/api/v2/authenticate` before June 2026.
[/BOX]

[BOX:note]
**Performance Tip**: For queries over 10,000 records, use pagination with `limit` and `offset` parameters to avoid timeouts.
[/BOX]
```

### Step 2: Research and Gather Content

For technical documents:
- Research technical details from relevant sources (documentation, APIs, etc.)
- Identify citations and add to bibliography
- Verify technical accuracy

For customer-facing documents:
- Research customer logo (search online or ask user to provide)
- Understand customer's industry and needs
- Tailor messaging appropriately

For all documents:
- Gather facts, not speculation
- Structure content logically
- Keep sections focused (aim for 3-10 sections for readability)

### Step 3: Structure the Content (Including Images)

Build a JSON structure representing the document. You can embed images directly in section content using a simple tag format.

**Image Embedding Syntax:**
```
[IMAGE:path:caption:width]
```

- **path**: Relative or absolute path to the image file (PNG, JPG, PDF supported)
- **caption**: Optional caption text (use `_` for no caption)
- **width**: Optional width as decimal (e.g., `0.6` for 60% of text width, default `0.8`)

**Examples:**
- `[IMAGE:diagram.png:System Architecture:0.7]` - Image at 70% width with caption
- `[IMAGE:/tmp/chart.png:_:0.5]` - Image at 50% width, no caption
- `[IMAGE:assets/logo.png:Company Logo]` - Image at default 80% width

Build a JSON structure representing the document:

```json
{
  "title": "Document Title",
  "subtitle": "Optional subtitle",
  "author": "SnapLogic",
  "date": "April 14, 2026",
  "version": "0.1",
  "customer_name": "Acme Corporation",
  "customer_logo": "/path/to/customer/logo.png",
  "management_summary": "Brief executive summary (for general docs)",
  "abstract": "Technical abstract (for technical docs)",
  "sections": [
    {
      "title": "Section Title",
      "content": "Section content with paragraphs, lists, etc.\\n\\n[IMAGE:diagram.png:Figure Description:0.6]\\n\\nMore text after the image.",
      "subsections": [
        {
          "title": "Subsection Title",
          "content": "Subsection content can also include images:\\n\\n[IMAGE:chart.png:_:0.5]"
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
      "role": "Role/Title",
      "email": "email@snaplogic.com"
    }
  ],
  "links": {
    "documentation": "https://docs-snaplogic.atlassian.net/",
    "academy": "https://academy.snaplogic.com/",
    "events": "https://www.snaplogic.com/events",
    "homepage": "https://www.snaplogic.com/"
  },
  "citations": ["citation_key1", "citation_key2"]
}
```

**Important content guidelines:**
- **Sections:** Aim for 5-10 sections for most documents. Maximum 30 supported.
- **Section content:** Each section should be self-contained and focused. Use `\\n\\n` for paragraph breaks.
- **Images:** Use `[IMAGE:path:caption:width]` syntax to embed images in content. Images are copied automatically.
- **Tables:** Use `[TABLE:style:caption]...[/TABLE]` syntax to embed tables. See Table Styles section for available styles.
- **List of Figures (LOF):** Automatically generated when images are present (configurable via `include_lof: false`)
- **List of Tables (LOT):** Automatically generated when tables are present (configurable via `include_lot: false`)
- **Management summary:** 2-3 paragraphs highlighting key points (general docs only).
- **Abstract:** Brief technical overview (technical docs only).
- **Next steps:** Concrete, actionable items.
- **Citations:** Only for technical documents. Keys reference `bibliography/references.bib`.

**Optional Configuration Flags:**
```json
{
  "title": "My Document",
  "include_lof": false,   // Set to false to disable List of Figures (default: true)
  "include_lot": false,   // Set to false to disable List of Tables (default: true)
  ...
}
```

**When to disable LOF/LOT:**
- Documents with only 1-2 figures/tables (not worth a full page)
- Internal documents where lists add unnecessary formality
- Documents where page count must be minimized
- Keep enabled (default) for professional/customer-facing documents with 3+ figures/tables

### Step 4: Handle Images and Customer Logos

**For images in document content:**
- Reference images using the `[IMAGE:path:caption:width]` syntax in section content
- Provide relative or absolute paths to image files
- Supported formats: PNG, JPG, PDF (avoid SVG - LaTeX compatibility issues)
- Images are automatically copied to the compilation directory

**For customer logos on title page:**
1. **Search online** for official logo (PNG or PDF format preferred)
2. **Download** to temporary location
3. **Provide path** in the customer_logo field
4. **Ask user** if you can't find a suitable logo

Quality matters - use official logos from company websites, not low-resolution or unofficial versions.

**Image best practices:**
- Use PNG for logos and diagrams (best quality)
- Use JPG for photos (smaller file size)
- Avoid SVG (LaTeX compatibility issues - convert to PNG first)
- Test image paths before compilation
- Keep width between 0.3 and 0.9 for best results
- Use descriptive captions to add context

### Step 5: Manage Citations (Technical Docs Only)

For technical documents requiring citations:

1. **Search central bibliography** (`bibliography/references.bib`) for existing references
2. **Validate date** - References older than 30 days should be revalidated
3. **Add new references** if not found in bibliography
4. **Use proper BibTeX format**:

```bibtex
@article{key2026,
  author = {Author Name},
  title = {Article Title},
  journal = {Journal Name},
  year = {2026},
  url = {https://example.com},
  note = {Last validated: 2026-04-14}
}
```

**Citation validation workflow:**
- Check if reference exists in `references.bib`
- If exists, check `note` field for validation date
- If > 30 days old, verify URL still works and content is current
- Update `note` field with new validation date
- If doesn't exist, research and add new entry

### Step 6: Compile the Document

Save the JSON structure to a temporary file and call the compilation script:

```python
import json
import subprocess
import sys
from pathlib import Path

# Get skill directory
skill_dir = Path(__file__).parent

# Save content
content_file = "/tmp/document_content.json"
with open(content_file, 'w') as f:
    json.dump(document_structure, f, indent=2)

# Compile document
doc_type = "general"  # or "technical" or "internal"
output_path = f"/tmp/output_document_v{version}.pdf"

result = subprocess.run([
    sys.executable,
    str(skill_dir / "scripts" / "compile_document.py"),
    content_file,
    output_path,
    doc_type
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Compilation failed: {result.stdout}")
    # Check error and potentially fix
else:
    output = json.loads(result.stdout)
    print(f"Document generated: {output['output_path']}")
    print(f"Pages: {output['pages']}")
```

The compilation script handles all LaTeX complexity - you just provide the structure.

### Step 7: Iterate Based on Feedback

When user requests changes:

1. **Determine change type:**
   - Content updates → Modify JSON, recompile
   - Minor fixes → Increment version (0.1 → 0.2)
   - Major revisions → Ask if ready for release version (0.x → 1.0)

2. **Version management:**
   - Start at 0.1 for first draft
   - Increment by 0.1 for each iteration (0.1 → 0.2 → 0.3)
   - Ask before moving to 1.0 (indicates "release ready")
   - Major versions for significant revisions (1.0 → 2.0)

3. **Iterative changes:**
   - Read user feedback carefully
   - Update relevant sections
   - Maintain document structure
   - Recompile and deliver

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
- **10pt**: Compact, fits more on page
- **11pt**: Standard (default)
- **12pt**: Larger, easier to read

### Paper Size
- **letterpaper**: US standard (default)
- **a4paper**: International standard

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

## Section Count Guidelines

- **1-2 sections**: Very brief docs - skip table of contents
- **3-10 sections**: Sweet spot for most documents - include TOC
- **11-15 sections**: Longer docs - ensure good structure
- **16-30 sections**: Maximum - warn user about readability, suggest splitting
- **30+ sections**: Error - too long, must be split into multiple documents

The skill will automatically include/exclude table of contents based on section count.

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

## Remember

- Hide LaTeX complexity from users - they should only see the final PDF
- Always start with version 0.1
- Research content thoroughly - accuracy matters
- Use appropriate document type for the use case
- Validate citations before including them
- Iterate based on feedback until user is satisfied
- Ask questions if requirements are unclear

The goal is professional, branded documents that make SnapLogic look good and communicate effectively. Quality over speed.
