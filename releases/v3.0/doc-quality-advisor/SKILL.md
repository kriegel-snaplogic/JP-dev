# Document Quality Advisor

Analyze document structure and content for professional quality, providing actionable feedback for improvement.

## Quick Start

```
/doc-quality-advisor path/to/document.json
```

**Target:** ≥85/100 score with no CRITICAL issues  
**Tool:** Python script (`validator.py`) that analyzes JSON structure and outputs quality report

## Purpose

This skill is designed for AI agents (like Claude) to validate and improve document quality during content generation WITHOUT requiring user approval for every iteration. It checks professional standards for technical documentation, proposals, architecture docs, and RFPs.

## When to Use

- **Before finalizing** any professional document
- **During content generation** to iterate toward quality
- **After receiving user feedback** to validate improvements
- **When creating** new documents from scratch

## What It Checks

### 1. Visual Content Balance
- Figure/image density (target: 1 per 2-3 pages)
- Section-level visual distribution
- Unreferenced figures/tables
- Over-reliance on visuals vs text

### 2. Content Type Diversity
- Paragraph-only sections (needs lists/tables)
- Excessive bullet lists (needs prose)
- Missing tables for comparative data
- Lack of visual breaks (every 2-3 paragraphs)

### 3. Cross-Reference Quality
- All figures/tables referenced at least once (supports both numeric and semantic labels)
- Detects: `Figure 1`, `Table 2` (numeric) and `Figure~\ref{fig:label}`, `Table~\ref{tab:label}` (semantic)
- All sections referenced appropriately
- Forward vs backward reference balance
- Proximity of references (within 2 pages)

### 4. Document Structure
- **Section length** (optimal: 300-500 words for sections without subsections, 200-400 words per subsection)
- **Subsections per section** (optimal: 0-3, max 6 before splitting recommended)
- **Header hierarchy depth** (max 3 levels for TOC: Section → Subsection → Subsubsection)
- **Management summary length** (5-10% of document)
- **TOC depth appropriateness** (3 levels recommended)

### 5. Readability
- Paragraph length (target: 3-7 sentences)
- Section flow and coherence
- Appropriate use of emphasis (bold, italic)
- White space distribution

### 6. Technical Quality
- Tables vs figures usage
- Diagram density for architecture docs
- Content organization (inline vs appendix)
- Actionable next steps

## Severity Levels

- **🔴 CRITICAL**: Must fix (broken references, structural issues)
- **🟡 WARNING**: Should fix (unreferenced figures, poor balance)
- **🔵 SUGGESTION**: Nice to have (style improvements)

## Output Format

The skill provides a comprehensive quality report with:

1. **Overall Score** (0-100) - Weighted average across all dimensions
2. **Quality Dimensions** - Individual scores for:
   - Visual Content Balance (0-100)
   - Content Type Diversity (0-100)
   - Cross-Reference Quality (0-100)
   - Document Structure (0-100)
   - Readability (0-100)
   - Technical Quality (0-100)
3. **Issues by Severity** - Grouped by CRITICAL, WARNING, SUGGESTION with specific locations
4. **Actionable Recommendations** - Specific fixes with examples
5. **Quick Wins** - Easy fixes for immediate improvement
6. **Validation** - What's already working well

## Usage

```
/doc-quality-advisor path/to/document.json
```

The skill analyzes the JSON structure (compatible with latex-docs format) and returns a detailed quality report.

## For Agents: Integration with latex-docs

**⚠️ REQUIRED WORKFLOW**: This skill MUST be used with latex-docs for all customer-facing documents.

### When to Run Validation
- **ALWAYS** validate BEFORE final PDF compilation
- **After** drafting content JSON structure
- **After** fixing issues (re-validate to confirm)
- **Before** delivering to user

### Workflow Integration
```
1. Generate content with latex-docs → document.json
2. /doc-quality-advisor document.json ← YOU ARE HERE
3. Fix CRITICAL issues (broken refs, structure)
4. Fix WARNING issues (unreferenced tables/figures)
5. /doc-quality-advisor document.json (re-check)
6. If score <85: Go to step 3
7. If score ≥85 and no CRITICAL: Compile PDF
```

### Issue Priorities
1. **CRITICAL** (must fix): Broken references, invalid structure, missing required sections
2. **WARNING** (should fix): Unreferenced figures/tables, poor balance, readability issues
3. **SUGGESTION** (optional): Style improvements, nice-to-haves

### Target Scores
- **Customer-facing**: ≥85/100 minimum, aim for 90+
- **Internal docs**: ≥75/100 acceptable
- **Drafts/quick docs**: No minimum (validation optional)

### What to Report to User
After validation, summarize:
- Overall score
- Number of CRITICAL/WARNING/SUGGESTION issues
- Top 3 issues to fix
- Quality dimension breakdown if score <80

**Examples:**
- "Document scores 78/100. Found 2 warnings: Figure 3 and Table 2 are unreferenced. I'll add `Figure~\ref{fig:arch}` reference in Section 2.1 and `Table~\ref{tab:pricing}` in Section 3.2, then re-validate."
- "Score: 92/100 ✓ No critical issues. 1 suggestion: Add comparison table in Section 4 for better readability. Ready to compile."
- "Score: 68/100. 1 CRITICAL: Missing management summary. 3 WARNINGS: Sections 2, 4, 5 lack visual content. Fixing now..."

## For Agents: Iteration Workflow

When using this skill during content generation:
1. Run validator after drafting content
2. Address CRITICAL issues immediately (always)
3. Fix WARNINGS that impact professionalism (customer-facing docs)
4. Consider SUGGESTIONS if time allows (optional)
5. Re-run validator after changes
6. Iterate until score ≥85 AND no CRITICAL issues remain
7. Only then proceed to final PDF compilation

## Best Practices Applied

Based on research from:
- Nielsen Norman Group (readability, scanning behavior)
- IEEE documentation standards (technical content)
- arc42 architecture framework (structure)
- Google Developer Style Guide (technical writing)
- Academic publishing standards (IMRAD, APA)

## Limitations

- Does not check content accuracy (that's your job)
- Does not validate LaTeX syntax (latex-docs handles that)
- Focus on structure and presentation, not subject matter
- Best suited for technical/professional documents (not creative writing)
