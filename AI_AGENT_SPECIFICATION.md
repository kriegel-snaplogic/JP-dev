# LaTeX Document Generation Skill - AI Agent Specification

## Document Overview

**Purpose:** This specification defines how AI agents should prepare content for the SnapLogic LaTeX document generation skill.

**Target Audience:** AI agents, automation systems, and programmatic document generators that need to produce professional PDF documents with SnapLogic branding.

**Skill Location:** `/Users/konstantinriegel/.claude/skills/latex-docs/`

**Compilation Script:** `scripts/compile_document.py`

---

## Quick Start

### Minimal Working Example

```json
{
  "title": "My Document Title",
  "author": "SnapLogic",
  "date": "2026-04-27",
  "version": "1.0",
  "sections": [
    {
      "title": "Introduction",
      "content": "This is a simple paragraph with **bold text** and *italic text*."
    },
    {
      "title": "Conclusion",
      "content": "Summary of key points."
    }
  ]
}
```

### How to Compile

```python
import subprocess
import json
import sys
from pathlib import Path

# 1. Create your document structure (JSON)
document = {
    "title": "Test Document",
    "version": "1.0",
    "sections": [
        {"title": "Section 1", "content": "Content here"}
    ]
}

# 2. Save to temporary file
content_file = "/tmp/my_document.json"
with open(content_file, 'w') as f:
    json.dump(document, f, indent=2)

# 3. Compile to PDF
skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
output_pdf = "/tmp/my_document.pdf"
doc_type = "technical"  # Options: "technical", "general", "internal"

result = subprocess.run([
    sys.executable,
    str(skill_dir / "scripts" / "compile_document.py"),
    content_file,
    output_pdf,
    doc_type
], capture_output=True, text=True)

# 4. Check result
if result.returncode == 0:
    output = json.loads(result.stdout)
    print(f"Success! PDF: {output['output_path']}")
    print(f"Pages: {output['pages']}")
else:
    print(f"Error: {result.stdout}")
```

---

## Document Types

Choose the appropriate document type based on the use case:

| Document Type | Use Cases | Key Features |
|--------------|-----------|--------------|
| **technical** | Architecture docs, API documentation, integration guides, technical specs | Citations, references, code-friendly, minimal branding |
| **general** | Proposals, solution docs, executive summaries, customer presentations | Full branding, title page, customer logo, management summary |
| **internal** | Status reports, memos, project updates, planning docs | Simplified branding, content-focused, quick generation |

---

## JSON Document Structure

### Top-Level Fields

```json
{
  "title": "string (REQUIRED)",
  "subtitle": "string (optional)",
  "author": "string (default: 'SnapLogic')",
  "date": "string (format: 'YYYY-MM-DD' or 'Month Day, Year')",
  "version": "string (REQUIRED, e.g., '1.0', '0.1')",
  "customer_name": "string (for general docs)",
  "customer_logo": "string (absolute path to logo PNG/PDF)",
  "management_summary": "string (for general docs, 2-3 paragraphs)",
  "abstract": "string (for technical docs, brief overview)",
  "sections": [array of section objects, REQUIRED],
  "next_steps": [array of strings, optional],
  "contacts": [array of contact objects, optional],
  "links": {object with URL keys, optional},
  "citations": [array of citation keys, for technical docs],
  "include_lof": boolean (default: true, controls List of Figures),
  "include_lot": boolean (default: true, controls List of Tables)
}
```

### Section Structure

```json
{
  "title": "string (REQUIRED)",
  "content": "string (REQUIRED, supports markdown-like syntax)",
  "subsections": [
    {
      "title": "string",
      "content": "string",
      "subsubsections": [
        {
          "title": "string",
          "content": "string"
        }
      ]
    }
  ]
}
```

**Nesting Rules:**
- **Level 1:** Section (appears in TOC, numbered)
- **Level 2:** Subsection (appears in TOC, numbered)
- **Level 3:** Subsubsection (appears in TOC, numbered)
- **Level 4:** Paragraph header (NOT in TOC, NOT numbered, renders as **bold**, use `**Bold Text:**` syntax)
- **Level 5:** Subparagraph header (NOT in TOC, NOT numbered, renders as *italic*, use `*Italic Text:*` syntax)

**Visual Rendering:**
- Level 4 (`\paragraph`): Normal size, black, **bold**, run-in style
- Level 5 (`\subparagraph`): Normal size, black, *italic*, run-in style

**Best Practice:** Use 3-10 sections for optimal readability. Maximum 30 sections supported.

---

## Content Formatting Syntax

### Text Formatting

| Syntax | Renders As |
|--------|-----------|
| `**bold text**` | **bold text** |
| `*italic text*` | *italic text* |
| `\\n\\n` | Paragraph break (double newline) |

**Important:** Use `\\n\\n` (escaped newlines) in JSON strings for paragraph breaks.

### Headers (Levels 4-5)

Levels 4-5 headers are NOT separate sections—they are inline formatted text within content:

```json
{
  "content": "Some introduction text.\n\n**Level 4 Header (Paragraph): Implementation Details**\n\nDetails here. This renders as bold.\n\n*Level 5 Header (Subparagraph): Edge Cases*\n\nMore specific details. This renders as italic."
}
```

**Important Distinction:**
- Level 4 uses `**bold markdown**` → renders as **bold** text
- Level 5 uses `*italic markdown*` → renders as *italic* text

### Lists

#### Numbered Lists

```
1. First item
2. Second item
   1. Nested item (3-space indent)
   2. Another nested item
3. Third item
```

#### Bullet Lists

```
- First bullet
- Second bullet
  - Nested bullet (3-space indent)
  - Another nested bullet
- Third bullet
```

#### Mixed Lists

```
1. Ordered item
   - Unordered sub-item
   - Another sub-item
2. Second ordered item
```

**Indentation Rules:**
- Use exactly **3 spaces** per nesting level
- Maximum 4 levels deep
- Consistent indentation is critical for proper rendering

### Tables

#### Basic Table Syntax

```
[TABLE:style:caption]
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| More     | Data     | Here     |
[/TABLE]
```

#### Table Styles

| Style | Use Case | Visual |
|-------|----------|--------|
| `simple` | Default, general-purpose tables | Navy header, alternating rows |
| `minimal` | Technical specs, academic docs | Horizontal rules only, no colors |
| `accent-blue` | Informational tables, API endpoints | Blue header, white rows |
| `accent-jade` | Recommended configs, best practices | Jade/green header, white rows |
| `accent-orange` | Warning tables, critical maintenance | Orange header, white rows |
| `bordered` | Reference tables, error code lookups | Gray header, all cells bordered |
| `status-[colors]` | Project status, timeline tables | Row colors indicate semantic state |

**Status Table Example:**

```
[TABLE:status-jade,orange,blue,white:Project Status]
| Task | Owner | Status |
|------|-------|--------|
| Complete | Alice | Done |
| At Risk | Bob | In Progress |
| On Track | Carol | In Progress |
| Not Started | Dave | Planned |
[/TABLE]
```

Colors for status rows: `jade` (success), `orange` (warning), `blue` (info), `gray` (neutral), `white` (default)

#### Table Emphasis Options

Add emphasis options after the caption, separated by colons:

```
[TABLE:style:caption:emphasis-options]
```

**Available Options:**
- `first-bold` - Makes first column bold (for row labels)
- `last-jade` - Highlights last column with jade/green background
- `last-orange` - Highlights last column with orange background
- `last-blue` - Highlights last column with blue background
- `last-navy` - Highlights last column with navy background
- `total-row` - Styles last row as total/summary row

**Combine Multiple Options:**

```
[TABLE:simple:Regional Performance:first-bold,last-jade,total-row]
| Region | Q1 | Q2 | Q3 | Q4 | Owner |
|--------|----|----|----|----|-------|
| North America | $2.1M | $2.4M | $2.8M | $3.1M | Alice |
| EMEA | $1.5M | $1.7M | $1.9M | $2.2M | Bob |
| Total | $3.6M | $4.1M | $4.7M | $5.3M | - |
[/TABLE]
```

#### Landscape Tables

For wide tables (7-8 columns), use landscape orientation:

```
[TABLE:landscape-simple:Caption:emphasis-options]
| Col1 | Col2 | Col3 | Col4 | Col5 | Col6 | Col7 | Col8 |
|------|------|------|------|------|------|------|------|
| Data | Data | Data | Data | Data | Data | Data | Data |
[/TABLE]
```

**Validation Limits:**
- **Portrait tables:** Max 6 columns
- **Landscape tables:** Max 8 columns, max 25 rows

**Technical Notes:**
- Rotates entire page (table + headers + footers)
- Uses smart column width algorithm based on content length
- Supports all table styles: `landscape-simple`, `landscape-minimal`, `landscape-accent-blue`, etc.

### Images

#### Image Syntax

```
[IMAGE:path:caption:width]
```

**Parameters:**
- `path` - Relative or absolute path to image file (PNG, JPG, PDF)
- `caption` - Caption text (use `_` for no caption)
- `width` - Optional width as decimal (e.g., `0.6` = 60% of text width, default `0.8`)

**Examples:**

```
[IMAGE:diagram.png:System Architecture:0.7]
[IMAGE:/tmp/chart.png:_:0.5]
[IMAGE:assets/logo.png:Company Logo]
[IMAGE:assets/citizen-integrator/screenshot.png:Pipeline Designer Interface:0.95]
```

#### How Image Paths Work

**Absolute Paths:**
- Use full filesystem paths: `/tmp/chart.png` or `/Users/username/documents/diagram.png`
- The compilation script copies the image file to the working directory using **just the filename**
- Example: `/tmp/my_diagram.png` → copied to working directory as `my_diagram.png`
- **Use absolute paths for:** Temporary files, images outside the skill directory

**Relative Paths:**
- Resolved relative to the **skill directory** (`/Users/konstantinriegel/.claude/skills/latex-docs/`)
- The compilation script copies the image preserving the directory structure
- Example: `assets/logos/logo.png` → copied to working directory as `assets/logos/logo.png`
- **Use relative paths for:** Images stored within the skill's asset directory structure

**Path Resolution Examples:**

```json
{
  "sections": [
    {
      "title": "Architecture",
      "content": "[IMAGE:assets/diagrams/architecture.png:System Architecture:0.8]"
    }
  ]
}
```

This resolves to: `/Users/konstantinriegel/.claude/skills/latex-docs/assets/diagrams/architecture.png`

---

## 🤖 AI Agent Image Preparation Guide

**This section is specifically for AI agents preparing document content with images.**

### Decision Tree: How to Handle Images

```
START: I need to include an image in the document
│
├─ Does the image already exist?
│  │
│  ├─ YES: Is it in the skill's assets directory?
│  │  │
│  │  ├─ YES: ✅ Use relative path
│  │  │      Example: "assets/diagrams/workflow.png"
│  │  │
│  │  └─ NO: Is it a temporary file?
│  │     │
│  │     ├─ YES: ✅ Use absolute path
│  │     │      Example: "/tmp/generated_chart_12345.png"
│  │     │
│  │     └─ NO: Should I copy it to assets first?
│  │            │
│  │            ├─ YES (reusable): Copy to assets/, use relative path
│  │            └─ NO (one-time): ✅ Use absolute path
│  │
│  └─ NO: I need to generate/download the image
│     │
│     ├─ Is it reusable across documents?
│     │  │
│     │  ├─ YES: Generate → Save to assets/ → Use relative path
│     │  │      Example: Generate chart → assets/charts/revenue_2026.png
│     │  │
│     │  └─ NO: Generate → Save to /tmp/ → Use absolute path
│     │         Example: Generate chart → /tmp/chart_abc123.png
│     │
│     └─ Do I need to fetch from URL?
│        │
│        ├─ Download image → Determine if reusable → Choose path type
│        └─ Verify format (PNG/JPG/PDF only, NO SVG)
```

### Step-by-Step Workflow for AI Agents

#### Scenario 1: Using Existing Images from Assets

**When:** Images already exist in the skill's asset directory

```python
from pathlib import Path

# 1. Define skill directory
skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
assets_dir = skill_dir / "assets"

# 2. Verify image exists
image_path = assets_dir / "diagrams" / "architecture.png"
if not image_path.exists():
    raise FileNotFoundError(f"Asset not found: {image_path}")

# 3. Build relative path for JSON (relative to skill_dir)
relative_path = image_path.relative_to(skill_dir)
# Result: "assets/diagrams/architecture.png"

# 4. Create content with relative path
content = f"""
Our system architecture is shown below:

[IMAGE:{relative_path}:System Architecture Diagram:0.8]

As shown in Figure 1, the system consists of three main layers.
"""

# 5. Add to document structure
document = {
    "title": "Architecture Overview",
    "version": "1.0",
    "sections": [
        {
            "title": "System Design",
            "content": content
        }
    ]
}
```

#### Scenario 2: Generating Images Dynamically

**When:** Creating charts, graphs, or visualizations programmatically

```python
import tempfile
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Generate the image
def generate_chart():
    """Generate a sample chart and return path"""
    # Create chart
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
    ax.set_title("Revenue Growth")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Revenue ($M)")
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(
        suffix='.png',
        delete=False,
        dir='/tmp'
    )
    fig.savefig(temp_file.name, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return temp_file.name

# 2. Generate and get absolute path
chart_path = generate_chart()
# Result: "/tmp/tmpxyz123.png"

# 3. Verify file was created
if not Path(chart_path).exists():
    raise FileNotFoundError(f"Generated image not found: {chart_path}")

# 4. Use absolute path in content
content = f"""
Revenue trends for 2026:

[IMAGE:{chart_path}:Revenue Growth by Quarter:0.7]

Figure 1 shows consistent growth across all quarters.
"""

# 5. Add to document
document = {
    "title": "Q4 2026 Report",
    "version": "1.0",
    "sections": [
        {
            "title": "Financial Performance",
            "content": content
        }
    ]
}

# Note: Temporary file will be copied during compilation,
# so it's safe to clean up after PDF generation
```

#### Scenario 3: Downloading Images from URLs

**When:** Fetching logos, diagrams, or screenshots from web sources

```python
import requests
from pathlib import Path
import tempfile

def download_image(url: str, save_to_assets: bool = False) -> str:
    """
    Download image from URL and return path for use in document.
    
    Args:
        url: Image URL to download
        save_to_assets: If True, save to assets/ (reusable).
                       If False, save to /tmp/ (one-time use)
    
    Returns:
        Path to downloaded image (str)
    """
    # Download image
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    # Determine file extension
    content_type = response.headers.get('content-type', '')
    if 'png' in content_type:
        ext = '.png'
    elif 'jpeg' in content_type or 'jpg' in content_type:
        ext = '.jpg'
    elif 'pdf' in content_type:
        ext = '.pdf'
    else:
        raise ValueError(f"Unsupported image format: {content_type}")
    
    if save_to_assets:
        # Save to assets directory (reusable)
        skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
        assets_dir = skill_dir / "assets" / "downloaded"
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename from URL
        filename = url.split('/')[-1].replace(' ', '_')
        if not filename.endswith(ext):
            filename += ext
        
        save_path = assets_dir / filename
        save_path.write_bytes(response.content)
        
        # Return relative path
        return str(save_path.relative_to(skill_dir))
    else:
        # Save to temp directory (one-time use)
        temp_file = tempfile.NamedTemporaryFile(
            suffix=ext,
            delete=False,
            dir='/tmp'
        )
        temp_file.write(response.content)
        temp_file.close()
        
        # Return absolute path
        return temp_file.name

# Example: Download customer logo (reusable)
logo_url = "https://example.com/acme-logo.png"
logo_path = download_image(logo_url, save_to_assets=True)
# Result: "assets/downloaded/acme-logo.png"

# Example: Download one-time screenshot
screenshot_url = "https://example.com/temp-screenshot.png"
screenshot_path = download_image(screenshot_url, save_to_assets=False)
# Result: "/tmp/tmpxyz456.png"

# Use in document
document = {
    "title": "Customer Overview",
    "customer_logo": logo_path,  # Can use for customer_logo field
    "sections": [
        {
            "title": "Product Screenshot",
            "content": f"[IMAGE:{screenshot_path}:Product Interface:0.8]"
        }
    ]
}
```

#### Scenario 4: Converting SVG to PNG

**When:** You have SVG images that need conversion (LaTeX doesn't support SVG)

```python
import subprocess
from pathlib import Path

def convert_svg_to_png(svg_path: str, output_path: str = None, dpi: int = 300) -> str:
    """
    Convert SVG to PNG for LaTeX compatibility.
    
    Requires: ImageMagick installed (brew install imagemagick)
    
    Args:
        svg_path: Path to SVG file
        output_path: Where to save PNG (default: same name, .png extension)
        dpi: Resolution for conversion (default 300 for print quality)
    
    Returns:
        Path to generated PNG file
    """
    svg_path = Path(svg_path)
    
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG not found: {svg_path}")
    
    # Determine output path
    if output_path is None:
        output_path = svg_path.with_suffix('.png')
    else:
        output_path = Path(output_path)
    
    # Convert using ImageMagick
    result = subprocess.run([
        'convert',
        '-density', str(dpi),
        '-background', 'white',
        '-alpha', 'remove',
        str(svg_path),
        str(output_path)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"SVG conversion failed: {result.stderr}")
    
    if not output_path.exists():
        raise RuntimeError(f"PNG was not created: {output_path}")
    
    return str(output_path)

# Example usage
svg_file = "/Users/konstantinriegel/.claude/skills/latex-docs/assets/diagrams/workflow.svg"
png_file = convert_svg_to_png(svg_file)
# Result: "/Users/konstantinriegel/.claude/skills/latex-docs/assets/diagrams/workflow.png"

# Use converted PNG in document
content = f"[IMAGE:assets/diagrams/workflow.png:Workflow Diagram:0.8]"
```

#### Scenario 5: Multiple Images in Sequence

**When:** Adding multiple images to a single section

```python
from pathlib import Path

skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")

# Define multiple images with their metadata
images = [
    {
        "path": "assets/screenshots/step1.png",
        "caption": "Step 1: Login Screen",
        "width": 0.6
    },
    {
        "path": "assets/screenshots/step2.png",
        "caption": "Step 2: Dashboard",
        "width": 0.6
    },
    {
        "path": "assets/screenshots/step3.png",
        "caption": "Step 3: Configuration",
        "width": 0.6
    }
]

# Verify all images exist
for img in images:
    img_path = skill_dir / img["path"]
    if not img_path.exists():
        raise FileNotFoundError(f"Image missing: {img_path}")

# Build content with image references
content_parts = ["Follow these steps to configure the system:\n\n"]

for idx, img in enumerate(images, start=1):
    content_parts.append(
        f"**Step {idx}:** {img['caption'].split(':')[1].strip()}\n\n"
        f"[IMAGE:{img['path']}:{img['caption']}:{img['width']}]\n\n"
        f"As shown in Figure {idx}, ...\n\n"
    )

content = "".join(content_parts)

# Add to document
document = {
    "title": "Setup Guide",
    "version": "1.0",
    "sections": [
        {
            "title": "Configuration Steps",
            "content": content
        }
    ]
}
```

### Common Pitfalls and Solutions

#### ❌ Pitfall 1: Using Relative Paths Without Skill Directory Context

```python
# WRONG - This assumes current working directory
content = "[IMAGE:diagram.png:My Diagram:0.7]"
# This will fail because compilation happens in /tmp/
```

```python
# CORRECT - Use relative to skill directory OR absolute
content = "[IMAGE:assets/diagrams/diagram.png:My Diagram:0.7]"
# or
content = "[IMAGE:/full/path/to/diagram.png:My Diagram:0.7]"
```

#### ❌ Pitfall 2: Not Verifying Image Exists Before Compilation

```python
# WRONG - Assume image exists
document = {
    "sections": [
        {"title": "Overview", "content": "[IMAGE:missing.png:Oops:0.7]"}
    ]
}
# Compilation will fail with cryptic LaTeX error
```

```python
# CORRECT - Verify first
from pathlib import Path

def verify_image(path: str, skill_dir: Path) -> bool:
    """Verify image exists before adding to document"""
    if Path(path).is_absolute():
        return Path(path).exists()
    else:
        return (skill_dir / path).exists()

skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
image_path = "assets/diagram.png"

if verify_image(image_path, skill_dir):
    content = f"[IMAGE:{image_path}:My Diagram:0.7]"
else:
    raise FileNotFoundError(f"Image not found: {image_path}")
```

#### ❌ Pitfall 3: Using SVG Files Directly

```python
# WRONG - SVG not supported
content = "[IMAGE:diagram.svg:Architecture:0.8]"
# LaTeX will fail to render
```

```python
# CORRECT - Convert SVG to PNG first
svg_path = "assets/diagram.svg"
png_path = svg_path.replace('.svg', '.png')

if not Path(png_path).exists():
    convert_svg_to_png(svg_path, png_path)

content = f"[IMAGE:{png_path}:Architecture:0.8]"
```

#### ❌ Pitfall 4: Forgetting to Reference Images in Text

```python
# WRONG - Image appears but no text reference
content = """
System architecture overview.

[IMAGE:assets/arch.png:System Architecture:0.8]

The system consists of three layers.
"""
# Image numbered but not referenced - looks unprofessional
```

```python
# CORRECT - Always reference figures
content = """
System architecture overview is shown in Figure 1.

[IMAGE:assets/arch.png:System Architecture:0.8]

As illustrated in Figure 1, the system consists of three layers.
"""
```

### Validation Checklist for AI Agents

Before adding images to a document, verify:

```python
def validate_image_for_document(image_path: str, skill_dir: Path) -> dict:
    """
    Validate image is ready for document compilation.
    
    Returns dict with: {"valid": bool, "errors": list, "warnings": list}
    """
    errors = []
    warnings = []
    
    # Resolve path
    if Path(image_path).is_absolute():
        full_path = Path(image_path)
    else:
        full_path = skill_dir / image_path
    
    # Check 1: File exists
    if not full_path.exists():
        errors.append(f"File not found: {full_path}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    # Check 2: File is readable
    if not full_path.is_file():
        errors.append(f"Not a file: {full_path}")
    
    # Check 3: Supported format
    supported_formats = ['.png', '.jpg', '.jpeg', '.pdf']
    if full_path.suffix.lower() not in supported_formats:
        if full_path.suffix.lower() == '.svg':
            errors.append(f"SVG not supported. Convert to PNG first: {full_path}")
        else:
            errors.append(f"Unsupported format {full_path.suffix}. Use PNG, JPG, or PDF.")
    
    # Check 4: File size (warn if > 5MB)
    file_size_mb = full_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 5:
        warnings.append(f"Large file ({file_size_mb:.1f}MB). Consider resizing: {full_path}")
    
    # Check 5: Spaces in filename (auto-converted, but warn)
    if ' ' in full_path.name:
        warnings.append(f"Filename contains spaces. Will be converted to underscores: {full_path.name}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

# Example usage
skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
result = validate_image_for_document("assets/diagram.png", skill_dir)

if not result["valid"]:
    print("❌ Image validation failed:")
    for error in result["errors"]:
        print(f"  - {error}")
else:
    print("✅ Image validation passed")
    if result["warnings"]:
        print("⚠️  Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
```

---

**Spaces in Filenames:**
- **CRITICAL:** The compilation script automatically replaces spaces with underscores
- If your file is named `my diagram.png`, reference it as `my diagram.png` in JSON
- The script converts it to `my_diagram.png` for LaTeX compatibility
- **Recommendation:** Avoid spaces in filenames to prevent confusion

#### Image File Preparation Workflow

When preparing images for AI agents to use:

1. **Store images in the skill's asset directory:**
   ```bash
   /Users/konstantinriegel/.claude/skills/latex-docs/assets/
   ├── diagrams/
   ├── screenshots/
   ├── logos/
   └── customer-specific/
   ```

2. **Use relative paths in JSON:**
   ```json
   {
     "content": "[IMAGE:assets/diagrams/workflow.png:Workflow Diagram:0.7]"
   }
   ```

3. **For dynamic/temporary images, use absolute paths:**
   ```json
   {
     "content": "[IMAGE:/tmp/generated_chart.png:Performance Chart:0.6]"
   }
   ```

4. **Verify image exists before compilation:**
   ```python
   from pathlib import Path
   
   skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
   image_path = skill_dir / "assets" / "diagrams" / "workflow.png"
   
   if not image_path.exists():
       raise FileNotFoundError(f"Image not found: {image_path}")
   ```

#### Image Automatic Numbering and Cross-References

**How It Works:**
- Images are automatically numbered in the order they appear in the JSON structure (1, 2, 3...)
- Each image gets a LaTeX label `\label{fig:N}` where N is the JSON order number
- Text references like "Figure 3" are converted to clickable hyperlinks
- LaTeX automatically generates "List of Figures" with all captions

**Example with Cross-References:**

```json
{
  "sections": [
    {
      "title": "System Overview",
      "content": "Our platform architecture is shown in Figure 1.\n\n[IMAGE:assets/architecture.png:Platform Architecture:0.8]\n\nAs you can see in Figure 1, the system consists of three layers."
    },
    {
      "title": "User Interface",
      "content": "The dashboard design is illustrated in Figure 2.\n\n[IMAGE:assets/dashboard.png:Dashboard Screenshot:0.7]\n\nFigure 2 demonstrates the clean, modern interface."
    }
  ]
}
```

**Important:** The figure number in your text must match the order images appear in the JSON, not the section they're in.

#### Best Practices

**File Formats:**
- ✅ **PNG**: Best for logos, diagrams, screenshots (lossless, supports transparency)
- ✅ **JPG**: Best for photos (smaller file size, lossy compression)
- ✅ **PDF**: Vector graphics (scales without pixelation)
- ❌ **SVG**: NOT supported by LaTeX - convert to PNG first using `convert image.svg image.png`

**Image Quality:**
- Use **300 DPI minimum** for printed documents
- Keep file sizes under **5MB** per image (resize large images before embedding)
- Test images open correctly before adding to JSON

**Width Guidelines:**
- `0.3` - Small inline images, icons
- `0.5` - Medium images, side-by-side comparisons
- `0.7` - Standard diagrams and screenshots
- `0.8` - Default, works well for most content
- `0.9` - Large images that need detail
- `1.0` - Full page width (use sparingly)

**Content Integration:**
- Reference every figure in the text ("As shown in Figure 1...")
- Place image reference **before** or **right after** the image tag in content
- Use descriptive captions that explain what the image shows
- Avoid generic captions like "Image 1" or "Screenshot"

**Directory Organization:**
```
assets/
├── logos/              # Company and product logos
├── diagrams/           # Architecture and flow diagrams
├── screenshots/        # UI screenshots and screen captures
├── charts/             # Data visualizations and graphs
└── customer-specific/  # Customer-provided images
```

### Highlight Boxes

#### Standard Boxes (Info, Success, Warning, Note)

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

**Use for:** Multi-sentence explanatory content, technical notes, warnings

#### KPI Boxes (Metrics)

```
[KPI:color|title|value]
```

**Example:**

```
[KPI:navy|Active Pipelines|1,247]
[KPI:blue|Integrations|328]
[KPI:jade|Success Rate|98.5%]
[KPI:orange|Avg Response|2.3s]
```

**Colors:** `navy`, `blue`, `jade`, `orange`

**⚠️ CRITICAL CONTENT LIMITS:**
- **Title:** 1-3 words, 15 characters maximum
- **Value:** 1-10 characters maximum
- Displays 4 boxes per row

**Use for:** Single metrics, dashboard-style statistics

#### Feature Boxes

```
[FEATURE:color|title]
Content here (2-3 sentences).
[/FEATURE]
```

**Example:**

```
[FEATURE:blue|Cost Savings]
Predictable subscription pricing with automated migration tools reducing effort by 40-70%. Forrester confirms 181% ROI over 3 years.
[/FEATURE]
```

**Colors:** `navy`, `blue`, `jade`, `orange`

**⚠️ CRITICAL CONTENT LIMITS:**
- **Title:** 2-4 words, 25 characters maximum
- **Content:** 2-3 sentences, 40-60 words MAX
- Displays 3 boxes per row

**Use for:** Marketing-style feature highlights, value propositions

### Cross-References

The system automatically converts text references into clickable hyperlinks:

**Section References:**
- Write: "For more details, see Section 2.1"
- Renders as: Clickable text that jumps to Section 2.1
- Supports: "Section X", "Section X.Y", "Section X.Y.Z"

**Figure References:**
- Write: "As shown in Figure 3, the architecture..."
- Renders as: Clickable text that jumps to Figure 3
- Figures are automatically numbered (1, 2, 3...)

**Table References:**
- Write: "The data in Table 2 shows..."
- Renders as: Clickable text that jumps to Table 2
- Tables are automatically numbered (1, 2, 3...)

**Best Practices:**
- Reference every figure and table at least once
- Place references near the target (same section preferred)
- Use specific references ("Section 2.1") not vague ones ("as mentioned above")

---

## Common Patterns and Examples

### Example 1: Technical Documentation

```json
{
  "title": "API Integration Guide",
  "author": "SnapLogic Engineering",
  "date": "2026-04-27",
  "version": "1.0",
  "abstract": "This document provides a comprehensive guide to integrating with the SnapLogic API, including authentication, endpoints, and best practices.",
  "sections": [
    {
      "title": "Getting Started",
      "content": "The SnapLogic API uses REST principles and OAuth 2.0 authentication.\n\n[BOX:info]\n**API Endpoint**: All API requests should be sent to `https://api.snaplogic.com/v1/`\n[/BOX]\n\nSee Section 2 for authentication details."
    },
    {
      "title": "Authentication",
      "content": "OAuth 2.0 is required for all API requests.\n\n**Client Credentials Flow:**\n\n1. Obtain client ID and secret from SnapLogic console\n2. Request access token from `/oauth/token` endpoint\n3. Include token in `Authorization: Bearer <token>` header\n4. Token expires after 3600 seconds\n\n[TABLE:simple:OAuth Endpoints]\n| Endpoint | Method | Purpose |\n|----------|--------|--------|\n| /oauth/token | POST | Obtain access token |\n| /oauth/refresh | POST | Refresh expired token |\n| /oauth/revoke | POST | Revoke access token |\n[/TABLE]",
      "subsections": [
        {
          "title": "Token Management",
          "content": "Access tokens should be cached and reused until expiration.\n\n[BOX:warning]\n**Security Note**: Never commit access tokens to source control or log them in plaintext.\n[/BOX]"
        }
      ]
    },
    {
      "title": "API Endpoints",
      "content": "The following endpoints are available:\n\n[TABLE:accent-blue:Available API Endpoints]\n| Endpoint | Method | Description |\n|----------|--------|-------------|\n| /pipelines | GET | List all pipelines |\n| /pipelines/{id} | GET | Get pipeline details |\n| /pipelines/{id}/execute | POST | Execute pipeline |\n| /pipelines/{id}/logs | GET | Retrieve execution logs |\n[/TABLE]\n\nFor detailed examples, see Section 4."
    },
    {
      "title": "Error Handling",
      "content": "The API returns standard HTTP status codes.\n\n[TABLE:simple:Error Codes]\n| Code | Meaning | Action |\n|------|---------|--------|\n| 401 | Unauthorized | Check authentication |\n| 403 | Forbidden | Verify permissions |\n| 404 | Not Found | Validate resource ID |\n| 429 | Rate Limited | Reduce request rate |\n| 500 | Server Error | Contact support |\n[/TABLE]"
    }
  ],
  "next_steps": [
    "Register application in SnapLogic developer console",
    "Obtain OAuth credentials",
    "Test authentication flow in sandbox environment",
    "Implement error handling and retry logic"
  ],
  "contacts": [
    {
      "name": "API Support Team",
      "role": "Developer Relations",
      "email": "api-support@snaplogic.com"
    }
  ]
}
```

### Example 2: Customer Proposal

```json
{
  "title": "Integration Modernization Proposal",
  "subtitle": "Transforming Data Workflows with SnapLogic",
  "customer_name": "Acme Corporation",
  "customer_logo": "/tmp/acme_logo.png",
  "author": "SnapLogic Solutions Engineering",
  "date": "2026-04-27",
  "version": "1.0",
  "management_summary": "This proposal outlines a comprehensive approach to modernizing Acme Corporation's integration infrastructure using the SnapLogic platform.\n\n**Key Benefits:**\n\n[KPI:blue|Cost Reduction|45%] [KPI:jade|Faster Delivery|60%] [KPI:orange|ROI Period|8 months] [KPI:navy|Integration Count|240+]\n\nThe solution addresses current pain points including manual ETL processes, limited scalability, and high maintenance costs.",
  "sections": [
    {
      "title": "Current State Analysis",
      "content": "Acme Corporation's current integration landscape consists of point-to-point connections and legacy ETL tools.\n\n**Identified Challenges:**\n\n- Manual data transformations require 120+ hours/month\n- Limited visibility into data flows and errors\n- Difficult to scale for new business requirements\n- High maintenance costs for aging infrastructure\n\n[BOX:warning]\n**Business Impact**: Current bottlenecks delay critical reporting by 48-72 hours, impacting decision-making velocity.\n[/BOX]"
    },
    {
      "title": "Proposed Solution",
      "content": "SnapLogic provides a modern, cloud-native integration platform.\n\n[FEATURE:blue|Visual Development]\nBuild integrations using drag-and-drop interface with no coding required for most use cases.\n[/FEATURE]\n[FEATURE:jade|Pre-Built Connectors]\nAccess 650+ pre-built connectors for SaaS, databases, APIs, and enterprise applications.\n[/FEATURE]\n[FEATURE:orange|AI-Powered]\nSnapGPT generates pipelines from natural language, reducing development time by 60%.\n[/FEATURE]",
      "subsections": [
        {
          "title": "Solution Architecture",
          "content": "The proposed architecture consists of three layers:\n\n1. **Data Sources**: Salesforce, SAP, Workday, on-premises databases\n2. **Integration Layer**: SnapLogic Intelligent Integration Platform\n3. **Data Destinations**: Snowflake data warehouse, analytics tools, downstream applications\n\n[IMAGE:/tmp/architecture_diagram.png:Proposed Solution Architecture:0.8]\n\nAs shown in Figure 1, all integrations flow through the SnapLogic platform."
        }
      ]
    },
    {
      "title": "Implementation Timeline",
      "content": "Phased rollout over 12 weeks:\n\n[TABLE:simple:Implementation Phases:first-bold]\n| Phase | Duration | Key Activities |\n|-------|----------|---------------|\n| Phase 1: Foundation | 3 weeks | Platform setup, authentication, pilot integrations |\n| Phase 2: Migration | 5 weeks | Migrate existing ETL jobs, build new pipelines |\n| Phase 3: Optimization | 2 weeks | Performance tuning, monitoring setup |\n| Phase 4: Launch | 2 weeks | Production cutover, training, documentation |\n[/TABLE]"
    },
    {
      "title": "ROI Analysis",
      "content": "Expected return on investment:\n\n[TABLE:simple:Cost-Benefit Analysis:first-bold,total-row]\n| Category | Current Annual Cost | Projected Cost | Savings |\n|----------|---------------------|----------------|--------|\n| Infrastructure | $180K | $85K | $95K |\n| Development | $240K | $120K | $120K |\n| Maintenance | $160K | $60K | $100K |\n| Total | $580K | $265K | $315K |\n[/TABLE]\n\nProjected **45% cost reduction** with **8-month payback period**."
    }
  ],
  "next_steps": [
    "Schedule technical deep-dive session with Acme IT team",
    "Provide access to SnapLogic trial environment",
    "Conduct proof-of-concept with two priority integrations",
    "Finalize statement of work and project timeline"
  ],
  "contacts": [
    {
      "name": "Sarah Johnson",
      "role": "Solutions Engineer",
      "email": "sarah.johnson@snaplogic.com"
    },
    {
      "name": "Michael Chen",
      "role": "Account Executive",
      "email": "michael.chen@snaplogic.com"
    }
  ],
  "links": {
    "documentation": "https://docs-snaplogic.atlassian.net/",
    "academy": "https://academy.snaplogic.com/",
    "events": "https://www.snaplogic.com/events"
  }
}
```

### Example 3: Internal Status Report

```json
{
  "title": "Q2 2026 Platform Updates",
  "author": "Engineering Team",
  "date": "2026-04-27",
  "version": "1.0",
  "sections": [
    {
      "title": "Summary",
      "content": "Key performance indicators for Q2 2026:\n\n[KPI:blue|Features Shipped|24] [KPI:jade|Uptime|99.97%] [KPI:orange|Bug Fixes|156] [KPI:navy|Customers|1,240]\n\nAll major milestones achieved on schedule."
    },
    {
      "title": "New Features",
      "content": "Major feature releases this quarter:\n\n- SnapGPT pipeline generation (April)\n- Advanced error handling (May)\n- Real-time monitoring dashboard (June)\n- Custom connector SDK v2 (June)\n\n[BOX:success]\n**Adoption**: SnapGPT reached 45% adoption rate within first 30 days of launch.\n[/BOX]"
    },
    {
      "title": "Performance Metrics",
      "content": "Platform performance comparison:\n\n[TABLE:simple:Quarterly Performance Metrics:total-row]\n| Metric | Q1 | Q2 | Change |\n|--------|----|----|--------|\n| Avg Response Time | 125ms | 98ms | -22% |\n| Throughput | 8.2K req/sec | 10.1K req/sec | +23% |\n| Error Rate | 0.05% | 0.03% | -40% |\n[/TABLE]"
    },
    {
      "title": "Next Quarter Priorities",
      "content": "Focus areas for Q3 2026:\n\n1. Enhanced security features\n   - Multi-factor authentication enhancements\n   - Role-based access control v2\n   - Audit log improvements\n2. Performance optimization\n   - Query optimization\n   - Caching strategy\n   - Load balancing improvements\n3. Developer experience\n   - Improved SDK documentation\n   - Interactive API explorer\n   - Code generation tools"
    }
  ],
  "next_steps": [
    "Review Q2 retrospective feedback",
    "Finalize Q3 roadmap with product team",
    "Schedule customer advisory board meeting",
    "Update public roadmap on website"
  ]
}
```

---

## Validation Rules and Constraints

### Document Constraints

| Element | Constraint |
|---------|-----------|
| Sections | Min: 1, Max: 30 |
| Section title | Max: 200 characters |
| Nesting depth | Max: 3 levels (section → subsection → subsubsection) |
| List depth | Max: 4 levels |
| Portrait table columns | Max: 6 columns |
| Landscape table columns | Max: 8 columns |
| Landscape table rows | Max: 25 rows |
| Image width | 0.1 - 1.0 (as decimal, e.g., 0.8 = 80%) |

### Required Fields by Document Type

**Technical Documents:**
- `title` ✅
- `version` ✅
- `sections` ✅
- `abstract` (recommended)

**General/Customer Documents:**
- `title` ✅
- `version` ✅
- `sections` ✅
- `customer_name` (recommended)
- `customer_logo` (recommended)
- `management_summary` (recommended)

**Internal Documents:**
- `title` ✅
- `version` ✅
- `sections` ✅

### Special Characters

Escape these characters if they appear in content:

| Character | LaTeX Escape | JSON Escape |
|-----------|-------------|-------------|
| `&` | `\&` | `&` (no escape needed in JSON) |
| `%` | `\%` | `%` |
| `$` | `\$` | `$` |
| `#` | `\#` | `#` |
| `_` | `\_` | `_` |
| `{` | `\{` | `{` |
| `}` | `\}` | `}` |
| `\` | `\textbackslash{}` | `\\` |

**Best Practice:** The compilation script handles most escaping automatically. Only manually escape if you encounter LaTeX compilation errors.

---

## Error Handling

### Common Compilation Errors

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Usage: compile_document.py <input.json> <output.pdf> <doc_type>" | Missing command-line arguments | Provide all 3 arguments: input file, output file, document type |
| "ERROR: Portrait table has N columns (max 6 allowed)" | Too many columns in portrait table | Use landscape table (`landscape-simple`) or reduce columns |
| "ERROR: Landscape table has N columns (max 8 allowed)" | Too many columns in landscape table | Split into multiple tables or reduce columns |
| "LaTeX Error: File 'image.png' not found" | Image path incorrect or file missing | Verify image path is absolute or relative to working directory |
| "JSON decode error" | Invalid JSON syntax | Validate JSON with linter before compilation |

### Debugging Failed Compilations

When compilation fails:

1. **Check return code:**
   ```python
   if result.returncode != 0:
       print(f"Compilation failed: {result.stdout}")
   ```

2. **Examine working directory:**
   - The script preserves the working directory on error
   - Check `/tmp/snaplogic_doc_*/document.tex` for generated LaTeX
   - Read `/tmp/snaplogic_doc_*/document.log` for detailed LaTeX errors

3. **Common fixes:**
   - Validate JSON structure with `json.loads()`
   - Check image paths exist
   - Verify special characters are properly escaped
   - Ensure table column counts are within limits

### Validation Checklist

Before compilation, validate:

- [ ] JSON is well-formed and parseable
- [ ] Required fields are present (`title`, `version`, `sections`)
- [ ] Section count is between 1-30
- [ ] Table column counts are within limits (6 for portrait, 8 for landscape)
- [ ] Image paths are absolute or relative to working directory
- [ ] Image files exist and are readable
- [ ] List indentation uses exactly 3 spaces per level
- [ ] Cross-references use correct syntax ("Section X", "Figure Y", "Table Z")

---

## Advanced Features

### Version Management

Follow semantic versioning:

- **0.1 - 0.9**: Draft versions during initial creation
- **1.0**: First release-ready version
- **1.1 - 1.9**: Minor updates to released version
- **2.0, 3.0**: Major revisions or significant changes

**Increment automatically:**
- For iterative improvements: `0.1 → 0.2 → 0.3`
- For release: `0.9 → 1.0`
- For major revisions: `1.x → 2.0`

### Automatic Features

These features are enabled automatically when conditions are met:

| Feature | Trigger | Configuration |
|---------|---------|--------------|
| Table of Contents | 3+ sections | Automatic |
| List of Figures | 1+ images with captions | `include_lof: true` (default) |
| List of Tables | 1+ tables | `include_lot: true` (default) |
| Bibliography | Technical doc with citations | Automatic |

**Disable List of Figures/Tables:**

```json
{
  "title": "My Document",
  "include_lof": false,
  "include_lot": false,
  ...
}
```

### Citations (Technical Documents Only)

Add citations to technical documents:

```json
{
  "title": "Technical Paper",
  "abstract": "Research on integration patterns.",
  "citations": ["smith2026", "jones2025"],
  "sections": [
    {
      "title": "Literature Review",
      "content": "Smith et al. demonstrated that integration patterns improve maintainability \\cite{smith2026}. This was further validated by Jones \\cite{jones2025}."
    }
  ]
}
```

**Citation Format:**
- Use `\\cite{key}` in content (double backslash for JSON escaping)
- Citation keys must exist in `bibliography/references.bib`
- Bibliography automatically generated at document end

### Custom Configuration

Optional command-line arguments:

```python
result = subprocess.run([
    sys.executable,
    str(skill_dir / "scripts" / "compile_document.py"),
    content_file,
    output_pdf,
    doc_type,
    "--font-size", "12pt",           # Options: 10pt, 11pt (default), 12pt
    "--paper-size", "a4paper",       # Options: letterpaper (default), a4paper
    "--color-scheme", "monochrome"   # Options: default, monochrome, high_contrast
], ...)
```

**When to Use:**
- `--font-size 12pt`: For accessibility or easier reading
- `--paper-size a4paper`: For international audiences
- `--color-scheme monochrome`: For printing or accessibility

---

## Performance and Best Practices

### Content Preparation

1. **Structure first, content second:** Design document outline before writing content
2. **Use appropriate nesting:** 3 levels (section → subsection → subsubsection) is optimal
3. **Reference everything:** Every figure and table should be referenced in text
4. **Keep sections focused:** Each section should cover one topic
5. **Use visual elements:** Break up text with tables, images, and boxes

### Optimization

- **Image sizes:** Keep images under 5MB each, resize large images before embedding
- **Table complexity:** Portrait tables with 4-5 columns are easiest to read
- **Content length:** Aim for 10-20 pages for most documents
- **Version control:** Save JSON input files alongside PDFs for iteration

### Testing Strategy

1. **Start simple:** Create minimal document first, then add features
2. **Test incrementally:** Add one feature at a time (images, tables, boxes)
3. **Validate early:** Check JSON structure before compilation
4. **Review output:** Always open generated PDF to verify rendering

---

## Troubleshooting Guide

### Issue: "Compilation takes too long"

**Possible causes:**
- Very large images (>10MB)
- Excessive sections (>20)
- Complex nested tables

**Solutions:**
- Resize images before embedding
- Split document into multiple parts
- Simplify table structures

### Issue: "Images not appearing in PDF"

**Possible causes:**
- Incorrect file path (relative path not resolved correctly)
- SVG format (not supported by LaTeX)
- File permissions (file not readable)
- Image file doesn't exist at specified path
- Spaces in filename not handled correctly

**Debugging Steps:**

1. **Verify file exists:**
   ```bash
   ls -la /path/to/image.png
   # or for relative paths
   ls -la /Users/konstantinriegel/.claude/skills/latex-docs/assets/diagram.png
   ```

2. **Check compilation log:**
   - On error, working directory is preserved: `/tmp/snaplogic_doc_*/`
   - Read `document.log` for LaTeX errors
   - Look for: `File 'image.png' not found`

3. **Test path resolution:**
   ```python
   from pathlib import Path
   
   skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
   
   # For relative path
   image_path = skill_dir / "assets" / "diagram.png"
   print(f"Resolved to: {image_path}")
   print(f"Exists: {image_path.exists()}")
   
   # For absolute path
   image_path = Path("/tmp/chart.png")
   print(f"Exists: {image_path.exists()}")
   ```

**Solutions:**

- **Use absolute paths for temporary files:** `/tmp/generated_chart.png`
- **Use relative paths for skill assets:** `assets/diagrams/workflow.png`
- **Convert SVG to PNG:** `convert image.svg image.png` (requires ImageMagick)
- **Check file permissions:** `chmod 644 /path/to/image.png`
- **Verify spaces in filename:** If file is `my image.png`, reference as `my image.png` (script auto-converts to `my_image.png`)
- **Test image opens:** `open /path/to/image.png` (macOS) or `xdg-open /path/to/image.png` (Linux)

**Common Path Mistakes:**

```json
// ❌ WRONG - relative to current directory (compilation happens in /tmp/)
{"content": "[IMAGE:diagram.png:My Diagram:0.7]"}

// ✅ CORRECT - relative to skill directory
{"content": "[IMAGE:assets/diagrams/diagram.png:My Diagram:0.7]"}

// ✅ CORRECT - absolute path
{"content": "[IMAGE:/tmp/diagram.png:My Diagram:0.7]"}
```

### Issue: "Table formatting looks wrong"

**Possible causes:**
- Too many columns for portrait orientation
- Content exceeds cell width
- Incorrect markdown table syntax

**Solutions:**
- Use landscape table for 7-8 columns
- Reduce column count or split table
- Verify markdown table has proper alignment row (`|---|---|---|`)

### Issue: "Cross-references not working"

**Possible causes:**
- Incorrect reference syntax
- Referenced element doesn't exist
- Capitalization mismatch

**Solutions:**
- Use exact syntax: "Section 2.1", "Figure 3", "Table 1"
- Verify referenced sections/figures/tables exist
- Match capitalization: "Section" not "section"

---

## API Reference

### Compilation Script

**Location:** `scripts/compile_document.py`

**Syntax:**
```bash
python compile_document.py <input.json> <output.pdf> <doc_type> [options]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `input.json` | string | ✅ | Path to JSON document structure |
| `output.pdf` | string | ✅ | Path for generated PDF output |
| `doc_type` | string | ✅ | Document type: `technical`, `general`, `internal` |
| `--font-size` | string | ❌ | Font size: `10pt`, `11pt`, `12pt` |
| `--paper-size` | string | ❌ | Paper size: `letterpaper`, `a4paper` |
| `--color-scheme` | string | ❌ | Color scheme: `default`, `monochrome`, `high_contrast` |

**Return Value:**

On success (exit code 0), stdout contains JSON:
```json
{
  "success": true,
  "output_path": "/path/to/output.pdf",
  "pages": 15,
  "warnings": []
}
```

On failure (exit code 1), stdout contains error message string.

### Python Integration Example

```python
import subprocess
import json
import sys
from pathlib import Path

def compile_document(content_dict, output_path, doc_type="technical", options=None):
    """
    Compile a JSON document structure to PDF.
    
    Args:
        content_dict: Dictionary containing document structure
        output_path: Path where PDF should be saved
        doc_type: One of "technical", "general", "internal"
        options: Optional dict with keys: font_size, paper_size, color_scheme
        
    Returns:
        dict: Result with keys: success, output_path, pages, warnings
        
    Raises:
        RuntimeError: If compilation fails
    """
    skill_dir = Path("/Users/konstantinriegel/.claude/skills/latex-docs")
    
    # Save content to temp file
    content_file = "/tmp/document_input.json"
    with open(content_file, 'w') as f:
        json.dump(content_dict, f, indent=2)
    
    # Build command
    cmd = [
        sys.executable,
        str(skill_dir / "scripts" / "compile_document.py"),
        content_file,
        output_path,
        doc_type
    ]
    
    # Add optional arguments
    if options:
        if 'font_size' in options:
            cmd.extend(['--font-size', options['font_size']])
        if 'paper_size' in options:
            cmd.extend(['--paper-size', options['paper_size']])
        if 'color_scheme' in options:
            cmd.extend(['--color-scheme', options['color_scheme']])
    
    # Execute
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse result
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise RuntimeError(f"Compilation failed: {result.stdout}")

# Usage
document = {
    "title": "Test Document",
    "version": "1.0",
    "sections": [
        {"title": "Introduction", "content": "Hello world"}
    ]
}

result = compile_document(
    content_dict=document,
    output_path="/tmp/test.pdf",
    doc_type="technical",
    options={"font_size": "12pt"}
)

print(f"Generated {result['pages']} page PDF: {result['output_path']}")
```

---

## Summary Checklist

When preparing content for LaTeX document generation:

### ✅ Structure
- [ ] Choose appropriate document type (technical, general, internal)
- [ ] Define clear section hierarchy (1-3 levels recommended)
- [ ] Keep section count reasonable (3-10 sections optimal)
- [ ] Use descriptive section titles

### ✅ Content
- [ ] Format text with markdown-like syntax (`**bold**`, `*italic*`)
- [ ] Use `\\n\\n` for paragraph breaks in JSON
- [ ] Format lists with proper 3-space indentation
- [ ] Keep list nesting to 4 levels maximum

### ✅ Tables
- [ ] Use portrait tables for ≤6 columns
- [ ] Use landscape tables for 7-8 columns
- [ ] Provide descriptive captions
- [ ] Reference tables in text ("as shown in Table 1...")
- [ ] Apply appropriate emphasis options (first-bold, last-[color], total-row)

### ✅ Images
- [ ] Use PNG/JPG format (not SVG)
- [ ] Provide absolute paths or verify relative paths
- [ ] Set appropriate width (0.3-0.9 recommended)
- [ ] Write descriptive captions
- [ ] Reference figures in text ("as shown in Figure 1...")

### ✅ Visual Elements
- [ ] Use standard boxes for explanatory content
- [ ] Use KPI boxes for metrics (keep titles/values short!)
- [ ] Use feature boxes for marketing content (2-3 sentences max)
- [ ] Choose appropriate colors for semantic meaning

### ✅ Metadata
- [ ] Set version number (start at 0.1 for drafts)
- [ ] Provide customer name and logo (for general docs)
- [ ] Write management summary (for general docs)
- [ ] Include next steps and contacts
- [ ] Add date in consistent format

### ✅ Validation
- [ ] Validate JSON syntax before compilation
- [ ] Check image paths exist
- [ ] Verify table column counts within limits
- [ ] Test cross-references use correct syntax
- [ ] Review generated PDF for formatting issues

---

## Additional Resources

- **Skill Documentation:** `/Users/konstantinriegel/.claude/skills/latex-docs/SKILL.md`
- **Example Documents:** `/Users/konstantinriegel/.claude/skills/latex-docs/tests/documents/`
- **Compilation Script:** `/Users/konstantinriegel/.claude/skills/latex-docs/scripts/compile_document.py`
- **Changelog:** `/Users/konstantinriegel/.claude/skills/latex-docs/CHANGELOG.md`

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-27  
**Maintained By:** Jean-Claude, Advisor to the CEO, AI Team Lead, Chief LaTeX Architect
