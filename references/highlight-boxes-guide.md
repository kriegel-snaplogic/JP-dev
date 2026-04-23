# Highlight Boxes Quick Reference

## Three Box Types - When to Use

| Box Type | Purpose | Size | Per Row | Best For |
|----------|---------|------|---------|----------|
| **Standard** (info/success/warning/note) | Multi-sentence explanations | Full-width | 1 | Technical docs, detailed notes |
| **KPI** | Single metrics/numbers | Compact | 4 | Dashboards, executive summaries |
| **Feature** | 2-4 sentence highlights | Medium | 3 | Proposals, marketing content |

## Quick Syntax

### Standard Boxes
```
[BOX:info]
**Title**: Your explanatory content here. Can be multiple sentences with **formatting**.
[/BOX]

[BOX:success]Success message[/BOX]
[BOX:warning]Warning message[/BOX]
[BOX:note]Reference note[/BOX]
```

### KPI Boxes
```
[KPI:navy|Active Pipelines|1,247]
[KPI:blue|Integrations|328]
[KPI:jade|Success Rate|98.5%]
[KPI:orange|Avg Response|2.3s]
```

**CRITICAL CONTENT LIMITS FOR KPI BOXES:**
- **Title**: 1-3 words MAXIMUM (e.g., "Total Users", "ROI", "Uptime")
- **Value**: 1-10 characters MAXIMUM (e.g., "500+", "181%", "2.3s", "114/114")
- **Height**: 80pt fixed - content WILL overflow if too long
- **Width**: Narrow (0.18\linewidth) - long titles will wrap badly

**WRONG - TOO LONG:**
```
❌ [KPI:blue|Supported Sources|Informatica + Talend + SSIS]  (title too long!)
❌ [KPI:jade|Validation|Record-by-record output comparison]   (both too long!)
❌ [KPI:orange|RFP Requirement T-01|Fully Compliant]           (title way too long!)
```

**CORRECT - SHORT:**
```
✅ [KPI:blue|Sources|4 Tools]
✅ [KPI:jade|Validation|Row-Level]
✅ [KPI:orange|T-01|Pass]
```

### Feature Boxes
```
[FEATURE:blue|Cost Savings]
Predictable subscription pricing with automated migration tools reducing effort by 40-70%. Forrester confirms 181% ROI.
[/FEATURE]

[FEATURE:jade|Faster Delivery]
Visual development and AI-generated pipelines reduce integration time by 60-80%.
[/FEATURE]

[FEATURE:orange|Quick Onboarding]
New developers productive in days, not months.
[/FEATURE]
```

**CRITICAL CONTENT LIMITS FOR FEATURE BOXES:**
- **Title**: 2-4 words MAXIMUM (e.g., "Enterprise Security", "Cost Savings")
- **Content**: 2-3 sentences, ~40-60 words MAXIMUM (~6-7 lines at 11pt font)
- **Height**: 130pt fixed - longer content WILL overflow
- **Character count**: Aim for 200-350 characters including spaces

**WRONG - TOO LONG (will overflow):**
```
❌ [FEATURE:blue|SnapGPT — AI Co-Pilot (On-Premises Compatible)]
SnapGPT generates working integration pipelines from plain-language descriptions,
auto-documents every pipeline and mapping, suggests field transformations, and 
diagnoses production errors. It operates from the SnapLogic Manager and processes 
only pipeline metadata — never AH operational data. No other on-premises-compatible 
integration platform offers generative AI development assistance.
[/FEATURE]
(~6 sentences, 350+ chars - TOO LONG, will overflow!)
```

**CORRECT - CONCISE (will fit):**
```
✅ [FEATURE:blue|AI-Powered Development]
SnapGPT generates pipelines from plain language, auto-documents code, and 
diagnoses errors. Only AI assistant available in on-premises integration tools.
[/FEATURE]
(2 sentences, ~160 chars - perfect fit!)
```

## Colors Available

All box types support these SnapLogic brand colors:
- `navy` - Navy (#001934) - Primary brand, professional
- `blue` - Blue (#4073FF) - Informational, optimistic
- `jade` - Jade (#42A5D2) - Success, positive outcomes
- `orange` - Orange (#FF7D3F) - Warnings, call-to-action

## Design Specifications

### Standard Boxes
- **Background**: 10% opacity colored
- **Border**: None (removed for clean look)
- **Top rule**: 2pt colored line
- **Padding**: 15pt all sides
- **Spacing**: 8pt before/after, 6pt after rule
- **Typography**: Body text (11pt)

### KPI Boxes
- **Background**: Solid color (100%)
- **Text color**: White
- **Width**: 0.18\linewidth (content) + 30pt padding
- **Height**: 80pt
- **Spacing**: 0.006\linewidth between boxes
- **Typography**: \large title (14.4pt), \Huge value (24.88pt)
- **Layout**: 4 boxes = 4(0.18+padding) + 3(spacing) ≈ 95% width

### Feature Boxes
- **Background**: 15% opacity colored
- **Text color**: Black
- **Width**: 0.265\linewidth (content) + 30pt padding
- **Height**: 130pt
- **Spacing**: 0.0065\linewidth between boxes
- **Typography**: \large title (14.4pt), \normalsize content (11pt)
- **Layout**: 3 boxes = 3(0.265+padding) + 2(spacing) ≈ 97% width

## Box Model Mathematics

**Critical for proper alignment!**

All widths must account for LaTeX `\fboxsep` padding:
- Padding adds to BOTH sides of content
- Formula: `total_width = content_width + (2 × fboxsep)`
- For 15pt padding: each box is `content + 30pt` wide

**KPI calculation (4 across):**
```
Available space = 468pt (linewidth) - (4 boxes × 30pt) = 348pt
Content per box = (348pt - 3 gaps) / 4 boxes = 85pt
85pt / 468pt ≈ 0.18\linewidth
```

**Feature calculation (3 across):**
```
Available space = 468pt - (3 boxes × 30pt) = 378pt
Content per box = (378pt - 2 gaps) / 3 boxes = 124pt
124pt / 468pt ≈ 0.265\linewidth
```

**If boxes wrap to next line:**
- Padding calculation is wrong
- Reduce content width by 0.01\linewidth
- Or reduce spacing between boxes

## Best Practices

### When to Use Standard Boxes
- ✅ Technical documentation and explanations
- ✅ Content requiring careful reading (5+ sentences)
- ✅ Documents that will be printed
- ✅ Need 5+ boxes on same page
- ❌ Single metrics or numbers (use KPI instead)
- ❌ Short feature highlights (use Feature instead)

### When to Use KPI Boxes
- ✅ Single metrics or numbers only
- ✅ Dashboard-style reports
- ✅ Executive summaries with key stats
- ✅ Content is scannable (no reading required)
- ❌ Multi-sentence content (use Standard instead)
- ❌ More than 8 boxes per page (visual fatigue)

### When to Use Feature Boxes
- ✅ Marketing-style feature highlights (2-4 sentences)
- ✅ Value propositions and benefits
- ✅ Capability overviews
- ✅ Proposals and customer-facing documents
- ❌ Long technical explanations (use Standard instead)
- ❌ Single metrics (use KPI instead)
- ❌ More than 9 boxes per page (2-3 rows max)

## Accessibility & Professional Standards

All boxes follow:
- ✅ WCAG AA contrast compliance
- ✅ Readable font sizes (11pt minimum for body text)
- ✅ Print-friendly (subtle backgrounds)
- ✅ Professional documentation standards (IEEE, arc42, Google)
- ✅ Consistent padding (15pt) across all types

### Typography Rules
- **Body text requiring reading**: Use \normalsize (11pt) minimum
- **Titles/labels**: Can use \large (14.4pt) for hierarchy
- **Short content (metrics)**: Can use \Huge (24.88pt) for impact
- **Never use \small for multi-sentence content** - readability suffers

## Common Patterns

### Dashboard Report
```
**Q4 2025 Platform Performance**

[KPI:navy|Total Users|12,450]
[KPI:blue|Pipeline Runs|2.4M]
[KPI:jade|Uptime|99.97%]
[KPI:orange|Data Processed|847TB]

[BOX:info]
**Quarter Highlights**: Platform adoption grew 34% quarter-over-quarter with significant expansion in financial services.
[/BOX]
```

### Customer Proposal
```
**Why SnapLogic?**

[FEATURE:blue|Enterprise Security]
Role-based access, SSO, MFA, and audit trails built into platform architecture.
[/FEATURE]
[FEATURE:jade|Data Sovereignty]
All processing occurs within customer data centers. No data leaves network boundary.
[/FEATURE]
[FEATURE:orange|Rapid Deployment]
Average time-to-value of 3.2 months from contract to production.
[/FEATURE]
```

### Technical Documentation
```
[BOX:warning]
**Breaking Change**: The legacy endpoint `/api/v1/auth` will be deprecated in version 3.0. Migrate to `/api/v2/authenticate` before June 2026.
[/BOX]

[BOX:note]
**Performance Tip**: For queries over 10,000 records, use pagination with `limit` and `offset` parameters.
[/BOX]
```

## Troubleshooting

### Boxes wrapping to next line
**Problem**: Width + padding + spacing exceeds linewidth  
**Solution**: Reduce content width by 0.01-0.02\linewidth

### Content too small to read
**Problem**: Using \small font for multi-sentence content  
**Solution**: Use \normalsize (11pt) for body text

### Visual clutter
**Problem**: Too many boxes on one page  
**Solution**: 
- Standard boxes: 3-5 per page max
- KPI boxes: 4-8 per page max
- Feature boxes: 6-9 per page max (2-3 rows)

### Poor contrast
**Problem**: Text hard to read against background  
**Solution**: 
- Use white text only on solid dark backgrounds (KPI boxes)
- Use black text on subtle backgrounds (Standard, Feature boxes)
- Navy is darkest color - use for maximum contrast with white text

### Inconsistent padding
**Problem**: Some boxes feel cramped  
**Solution**: All boxes should use 15pt fboxsep for consistency
