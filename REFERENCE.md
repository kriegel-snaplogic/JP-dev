# latex-docs Feature Reference

**Audience:** Agents and developers who need detailed feature documentation

**Purpose:** Comprehensive reference for all table styles, box types, emphasis options, and advanced syntax

---

## Quick Reference

For basic usage and workflow, see `skill.md`.
For input requirements and validation, see `CONTENT_REQUIREMENTS.md`.

This document covers:
- All 7 table styles with examples
- All table emphasis options
- Landscape tables
- KPI, FEATURE, and BOX highlight types
- Column width algorithms
- Advanced cross-referencing
- Edge cases and detailed syntax

---

## Advanced Features

### Cross-References (Auto-Generated) ✅

The skill provides two cross-reference systems: **automatic numeric** (backward compatible) and **semantic labels** (recommended for reusable content).

#### Automatic Numeric References (Simple)

The skill automatically converts text references into clickable hyperlinks:

**Section References:**
- Write: "For more details, see Section 2.1"
- Renders as: Black clickable text that jumps to Section 2.1
- Supports: "Section X", "Section X.Y", "Section X.Y.Z" (any depth)

**Figure References (Numeric):**
- Write: "As shown in Figure 3, the architecture..."
- Renders as: Black clickable text that jumps to Figure 3
- Works for simple documents where figure order is stable

**Table References (Numeric):**
- Write: "The data in Table 2 shows..."
- Renders as: Black clickable text that jumps to Table 2
- Works for simple documents where table order is stable

#### Semantic Label References (Recommended)

For **reusable content blocks** or documents where figures/tables may be reordered, use semantic labels:

**Figure References with Labels:**
```
Figure~\ref{fig:system-architecture} shows the high-level design.

[IMAGE:assets/arch.png:System Architecture:0.8:system-architecture]
```
- Label: `system-architecture` (descriptive, not position-dependent)
- Reference: `Figure~\ref{fig:system-architecture}`
- LaTeX resolves to correct number automatically (e.g., "Figure 5")
- **Robust**: Move figure anywhere, reference still works

**Table References with Labels:**
```
Table~\ref{tab:customer-refs} summarizes our aerospace customers.

[TABLE:accent-blue:Customer References::customer-refs]
| Customer | Industry | Status |
|----------|----------|--------|
| Airbus   | Aerospace | Active |
[/TABLE]
```
- Label: `customer-refs` (4th parameter, after empty emphasis field)
- Reference: `Table~\ref{tab:customer-refs}`
- LaTeX resolves to correct number automatically (e.g., "Table 3")
- **Robust**: Add/remove tables anywhere, reference still works

#### How It Works

- **Extraction**: Cross-references extracted BEFORE LaTeX escaping (prevents `\ref{}` from being escaped)
- **Placeholder**: Converted to `@FIGREF:label@` or `@TABREF:label@` during processing
- **Restoration**: Placeholders restored to `\ref{}` commands AFTER escaping
- **Compilation**: LaTeX performs two passes:
  - **Pass 1**: Writes labels to `.aux` file
  - **Pass 2**: Resolves `\ref{}` to actual numbers
- **Non-breaking space**: Uses `~` to prevent line breaks (e.g., `Figure~\ref{fig:X}`)

#### Best Practices

- ✅ **Always reference** every figure and table at least once
- ✅ **Use semantic labels** for reusable content blocks
- ✅ **Descriptive labels**: `system-architecture` not `fig1` or `diagram`
- ✅ **Place references near target** (within same section preferred)
- ✅ **Prefer backward references** over forward references ("as shown above" vs "as shown below")
- ❌ **Avoid hardcoded numbers** ("see Figure 3") in reusable content
- ❌ **Don't reference from distant sections** (weakens document flow)

#### Document Quality Validation

The `/doc-quality-advisor` skill automatically validates these best practices:
- ✅ Checks that all figures and tables are referenced at least once
- ✅ Identifies unreferenced visual content
- ✅ Validates cross-reference proximity (within 2 pages preferred)
- ✅ Assesses figure/table density (1 per 2-3 pages optimal)
- ✅ Scores overall document quality (0-100)

**When to use:**
- Before finalizing any professional document
- After adding new figures/tables to ensure references exist
- When user feedback suggests structure issues
- Recommended for all customer-facing documents

**How to use:**
```
/doc-quality-advisor path/to/document.json
```

The validator returns severity-based issues (CRITICAL, WARNING, SUGGESTION) with specific locations and actionable recommendations. Address CRITICAL issues (like unreferenced tables) before delivery.

### Header Hierarchy (5 Levels) ✅

Support for deep document structure following IEEE/academic best practices:

1. **Section** (`\section`) - Main topics, numbered (1, 2, 3...)
2. **Subsection** (`\subsection`) - Subtopics, numbered (2.1, 2.2...)
3. **Subsubsection** (`\subsubsection`) - Details, numbered (2.1.1, 2.1.2...)
4. **Paragraph** (`\paragraph`) - Fine details, NOT numbered (run-in style)
5. **Subparagraph** (`\subparagraph`) - Finest level, NOT numbered (run-in style)

**Visual Styling:**
- **Levels 1-3**: Large → large → normal size, colored (navy/blue), bold, numbered
- **Level 4 (Paragraph)**: Normal size, black, **bold**, run-in style (inline with text), NOT numbered
- **Level 5 (Subparagraph)**: Normal size, black, **italic**, run-in style (inline with text), NOT numbered

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
[TABLE:style:caption:emphasis:label]
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| More     | Data     | Here     |
[/TABLE]
```

- **style**: Table style (simple, minimal, accent-blue, etc.)
- **caption**: Table caption text (appears above table)
- **emphasis**: Optional emphasis options (`first-bold`, `last-jade`, `widths=1,2,3`, etc.)
- **label**: Optional semantic label for cross-references (e.g., `customer-refs`, `pricing-table`)

**Key Features:**
- **Automatic numbering**: Tables numbered sequentially (Table 1, Table 2, etc.)
- **Caption placement**: Appears ABOVE table (professional standard per Chicago/IEEE)
- **Caption spacing**: 10pt space below caption (prevents cramped appearance)
- **List of Tables**: Automatically generated when document contains tables (configurable)
- **Semantic labels**: Reference tables by meaningful names, not numbers
- **Smart column widths**: Analyzes total content volume per column (70% weight) + max cell length (30% weight)
- **Text wrapping**: Multi-line text supported in cells with proper alignment
- **Multiple styles**: 7 different table styles for different purposes

**Caption and Label Examples:**
- Basic: `[TABLE:simple:Platform Tier Comparison]`
- With emphasis: `[TABLE:simple:Regional Sales:first-bold,last-jade]`
- With label: `[TABLE:simple:Customer References::customer-refs]` (empty emphasis, semantic label)
- Full syntax: `[TABLE:simple:Pricing:first-bold,widths=1,2,1.5:pricing-table]`

**Cross-Referencing Tables:**
Use `Table~\ref{tab:label}` to reference tables with semantic labels. LaTeX will automatically resolve to the correct table number.

```
Table~\ref{tab:customer-refs} summarizes our aerospace manufacturing customers.

[TABLE:accent-blue:Aerospace Customer References::customer-refs]
| Customer | Industry | Use Case | Status |
|----------|----------|----------|--------|
| Airbus   | Aerospace | Supply Chain | Active |
[/TABLE]
```

This renders as: "Table 3 summarizes our aerospace manufacturing customers." (clickable link to the table)

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

**Table Emphasis Options:**

Add optional emphasis to any table style using colon-separated syntax:

```
[TABLE:style:caption:emphasis-options]
```

Available emphasis options:
- **first-bold**: Makes first column text bold (for row labels/identifiers)
- **last-jade**: Highlights last column with jade/green background (success/recommended)
- **last-orange**: Highlights last column with orange background (warning/urgent)
- **last-blue**: Highlights last column with blue background (information)
- **last-navy**: Highlights last column with navy background (emphasis)
- **total-row**: Styles the last row as a total/summary (bold + light background)

Combine multiple options with commas:
```
[TABLE:simple:Regional Performance:first-bold,last-jade,total-row]
```

**Use Cases:**
- `first-bold`: Region names, product SKUs, task names, person names
- `last-jade`: Recommended options, success metrics, owner columns
- `last-orange`: Priority levels, warning indicators, cost columns
- `last-blue`: Status indicators, information columns
- `total-row`: Sum rows, aggregate rows, summary rows

**Example:**
```json
{
  "content": "[TABLE:simple:Sales by Region:first-bold,last-jade,total-row]\n| Region | Q1 | Q2 | Q3 | Q4 | Owner |\n|--------|----|----|----|----|-------|\n| North America | $2.1M | $2.4M | $2.8M | $3.1M | Alice |\n| EMEA | $1.5M | $1.7M | $1.9M | $2.2M | Bob |\n| Total | $3.6M | $4.1M | $4.7M | $5.3M | - |\n[/TABLE]"
}
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
- **Portrait tables:** Max 6 columns for optimal readability
- **Landscape tables:** Use for 7-8 column tables (see Landscape Tables section below)
- Use bold for header row emphasis (automatic)

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

### Landscape Tables (Wide Data) ✅

For tables with 7-8 columns, use landscape orientation to maximize horizontal space. Landscape tables rotate the **entire page** (table + headers + footers) following professional documentation best practices.

**Syntax:**
```
[TABLE:landscape-<style>:Caption:emphasis-options]
```

**Key Features:**
- **Page rotation**: Entire page rotates 90° (headers/footers included)
- **Full width**: Uses complete page width (~10 inches instead of ~6.5 inches)
- **Smart column widths**: Analyzes cell content and assigns proportional column widths
- **All styles supported**: Works with `simple`, `minimal`, `accent-*`, `bordered`, `zebra-*`
- **Column limits**: Max 8 columns, max 25 rows
- **Emphasis options**: Supports `first-bold`, `last-[color]`, `total-row`

**When to Use Landscape:**
- ✅ Tables with 7-8 columns (portrait limit is 6)
- ✅ Integration matrices, system comparisons, detailed specifications
- ✅ Data that requires many attributes per row
- ✅ When column headers are descriptive (not cramped abbreviations)

**Why Full-Page Rotation:**
- Standard for professional technical documentation (Microsoft, AWS, Salesforce)
- Maintains consistent page geometry and visual hierarchy
- Headers/footers remain in proper position relative to page edges
- Better for printed documents and physical presentations
- Clearer signal to reader: "turn page to read"

**Validation:**
- **Portrait tables**: Max 6 columns (ERROR if exceeded)
- **Landscape tables**: Max 8 columns, max 25 rows (ERROR if exceeded)

**Column Width Algorithm:**
1. Scans all headers and cell content to find longest text per column
2. Assigns relative widths based on content length:
   - Very short (< 6 chars): 0.5x width (IDs, percentages)
   - Short (6-10 chars): 0.7x width
   - Medium (10-14 chars): 1.0x width
   - Long (14-18 chars): 1.4x width
   - Very long (18+ chars): 1.6x width
3. Normalizes widths to sum to page width using `tabularx` X columns
4. Prevents hyphenation with `\raggedright\arraybackslash`

**Example:**
```json
{
  "sections": [
    {
      "title": "System Integration Matrix",
      "content": "The following table shows all active integrations:\n\n[TABLE:landscape-simple:Complete Integration Matrix:first-bold,last-jade]\n| Source System | Target System | Protocol | Frequency | Volume/Day | Error % | Status | Owner |\n|--------------|---------------|----------|-----------|------------|---------|--------|-------|\n| Salesforce | SAP | REST API | Real-time | 2.5GB | 0.02% | Active | IT Ops |\n| SAP | Snowflake | JDBC | Hourly | 15GB | 0.01% | Active | Data Team |\n| Workday | Active Directory | LDAP | Daily | 500MB | 0.05% | Active | HR Tech |\n[/TABLE]\n\nTable 1 demonstrates landscape orientation for wide data matrices."
    }
  ]
}
```

**Technical Implementation:**
- Uses LaTeX `pdflscape` package for page rotation
- Wraps table in `\begin{landscape}...\end{landscape}` environment
- Uses `tabularx` instead of `tabular` for proportional column widths
- Column spec: `>{\hsize=N\hsize\raggedright\arraybackslash}X` for each column
- Works seamlessly with all existing table styles and emphasis options

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
- With 10pt body text: headers are 9-10pt, footers are 8-9pt
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
- **Line count**: ~6-7 lines at 10pt font - content must fit within this

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
- Content: \normalsize (10pt) regular black text
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
- ✅ Body text size (10pt) for content requiring careful reading
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
[IMAGE:path:caption:width:label]
```

- **path**: Relative or absolute path to the image file (PNG, JPG, PDF supported)
- **caption**: Optional caption text (use `_` for no caption)
- **width**: Optional width as decimal (e.g., `0.6` for 60% of text width, default `1.0` for full width)
- **label**: Optional semantic label for cross-references (e.g., `system-arch`, `pipeline-diagram`)

**Examples:**
- `[IMAGE:diagram.png:System Architecture:0.7:system-arch]` - Image with semantic label
- `[IMAGE:/tmp/chart.png:_:0.5]` - Image at 50% width, no caption, no label
- `[IMAGE:assets/logo.png:Company Logo::my-logo]` - Default width with semantic label

**Cross-Referencing Images:**
Use `Figure~\ref{fig:label}` to reference images with semantic labels. LaTeX will automatically resolve to the correct figure number.

```
The system architecture is shown in Figure~\ref{fig:system-arch}, which illustrates...

[IMAGE:assets/architecture.png:System Architecture Diagram:0.8:system-arch]
```

This renders as: "The system architecture is shown in Figure 3, which illustrates..." (clickable link to the figure)

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

