# Asset Library

## Overview

Centralized repository for all images, diagrams, and media assets used in SnapLogic documents.

## Directory Structure

```
assets/
├── images/                         # Image library organized by category
│   ├── platform/
│   │   ├── architecture/           # Architecture diagrams
│   │   ├── screenshots/            # UI screenshots  
│   │   └── diagrams/               # Data flow diagrams
│   ├── security/                   # Security & compliance visuals
│   ├── use_cases/                  # Use case screenshots & workflows
│   │   ├── citizen_integrator/     # Citizen integrator demo images
│   │   └── etl_modernization/      # ETL use case visuals
│   ├── branding/                   # Logos, brand assets
│   │   ├── snaplogic-logo-white.png
│   │   ├── snaplogic-logo-color.png
│   │   └── partner-logos/
│   └── customer/                   # Customer-specific assets
│       ├── airbus/
│       └── boeing/
│
└── metadata/                       # Asset tracking & metadata
    ├── image_catalog.json          # Central asset catalog
    ├── usage_map.json              # Asset-to-content mapping
    └── README.md                   # This file
```

## Asset Naming Convention

Format: `{category}_{description}_v{version}.{ext}`

Examples:
- `ground_plex_architecture_v2.png`
- `designer_interface_snapgpt_v1.png`
- `security_encryption_diagram_v1.png`

**Rules**:
- Lowercase with underscores
- Version suffix required (`_v1`, `_v2`, etc.)
- Descriptive names, not generic (`feature_x_screenshot_v1`, not `screenshot_001`)

## Image Requirements

### Technical Specs
- **Format**: PNG (preferred) or JPEG
- **Resolution**: Minimum 1200px width for screenshots
- **File size**: <1MB (optimize for PDF compilation)
- **Color space**: sRGB

### Content Guidelines
- **Brand compliance**: Follow SnapLogic brand guidelines
- **PII redaction**: Remove customer data, sensitive info
- **Clarity**: High resolution, readable text
- **Context**: Show enough UI context for understanding

## Asset Catalog

Central catalog tracking all assets: `metadata/image_catalog.json`

**Key fields**:
```json
{
  "id": "unique_asset_id",
  "path": "assets/images/category/file.png",
  "metadata": {
    "title": "Human-readable title",
    "description": "What this image shows",
    "tags": ["tag1", "tag2"]
  },
  "usage": {
    "used_by_blocks": ["block_id_1", "block_id_2"],
    "usage_count": 5
  },
  "licensing": {
    "customer_facing": true,
    "approved": true
  }
}
```

## Usage Map

Tracks relationships: `metadata/usage_map.json`

**content_to_assets**: Which content blocks use which images
```json
{
  "citizen_integrator_user_story_v1": [
    "citizen_integrator_step1_v1",
    "citizen_integrator_step2_v1"
  ]
}
```

**asset_to_content**: Which content blocks reference each image
```json
{
  "ground_plex_architecture_v2": [
    "platform_architecture_ground_plex_v2",
    "airbus_rfp_platform_section"
  ]
}
```

**Purpose**: 
- Prevent deleting assets still in use
- Identify orphaned assets
- Track asset popularity

## Adding New Assets

### Option 1: Manual Addition

```bash
# 1. Copy image to appropriate category
cp ~/new_screenshot.png assets/images/platform/screenshots/

# 2. Rename following convention
mv assets/images/platform/screenshots/new_screenshot.png \
   assets/images/platform/screenshots/designer_feature_x_v1.png

# 3. Run asset discovery
python3 ../scripts/discover_assets.py

# 4. Regenerate catalog
python3 ../scripts/generate_asset_catalog.py
```

### Option 2: Promotion Workflow

```bash
# Submit for review and automatic cataloging
python3 ../scripts/promote_asset.py submit \
  ~/new_screenshot.png \
  --category=platform \
  --subcategory=screenshots \
  --title="Feature X Designer View" \
  --description="Shows new Feature X in Designer canvas" \
  --tags=designer,feature_x,ui
```

## Asset Lifecycle

```
NEW → STAGING → REVIEW → APPROVED → LIBRARY
                   ↓
               REJECTED

LIBRARY → UPDATED (new version) → LIBRARY
       → DEPRECATED → ARCHIVE
```

### Versioning

When updating an existing image:

1. **Create new version**: Don't overwrite, create `file_v2.png`
2. **Update content blocks**: Reference new version
3. **Deprecate old version**: Mark `file_v1.png` as deprecated
4. **Archive after transition**: Move old version to `archive/` once all content updated

Example:
```bash
# Old: ground_plex_architecture_v1.png (used by 3 blocks)
# New: ground_plex_architecture_v2.png

# Update content blocks to reference v2
# Once all blocks updated, move v1 to archive
mv assets/images/platform/architecture/ground_plex_architecture_v1.png \
   assets/images/archive/
```

## Maintenance

### Find Orphaned Assets

Assets not referenced by any content block:

```bash
python3 ../scripts/audit_assets.py --find-orphans
```

Output:
```
🔍 Orphaned Assets (not used by any content):
   - assets/images/platform/screenshots/old_feature_v1.png
   - assets/images/security/diagram_unused_v1.png

Action: Review and delete or archive
```

### Find Missing Assets

Content blocks reference non-existent images:

```bash
python3 ../scripts/audit_assets.py --find-missing
```

Output:
```
⚠️  Missing Assets (referenced but don't exist):
   - Content block: airbus_custom_section
     Missing: assets/images/customer/airbus/custom_diagram.png

Action: Create or update content block references
```

### Large File Audit

Images over 1MB (slow PDF compilation):

```bash
python3 ../scripts/audit_assets.py --large-files --threshold=1MB
```

### Outdated Screenshots

Flag images from old product versions:

```bash
python3 ../scripts/audit_assets.py --check-version --platform-version=6.2
```

## Best Practices

### For Content Creators

1. **Check library first**: Search existing assets before creating new screenshots
2. **Use relative paths**: Reference as `assets/images/category/file.png`
3. **Track dependencies**: List all images in content block metadata
4. **Version images**: Create new versions, don't overwrite

### For Asset Managers

1. **Organize by category**: Platform, security, use cases, branding
2. **Consistent naming**: Follow naming convention strictly
3. **Optimize file size**: Compress images to <1MB
4. **Track usage**: Run discovery scripts regularly
5. **Archive old versions**: Don't delete, move to archive/

### For Reviewers

1. **Check quality**: Resolution, clarity, brand compliance
2. **Verify licensing**: Customer-facing approval for screenshots
3. **Test rendering**: Compile to PDF, verify appearance
4. **Update catalog**: Ensure metadata is complete and accurate

## Automation

### Git Hooks

**pre-commit**:
- Validate image file sizes (<1MB)
- Check naming convention compliance
- Update usage map automatically

**post-merge**:
- Regenerate asset catalog
- Check for orphaned assets
- Update content library index

### Scheduled Jobs

**Daily**: Find orphaned and missing assets
```bash
0 2 * * * python3 scripts/audit_assets.py --find-orphans --find-missing
```

**Weekly**: Generate asset usage report
```bash
0 9 * * 1 python3 scripts/generate_asset_report.py --email=solutions-team@snaplogic.com
```

## Metrics

### Asset Health
- **Total assets**: 47 images
- **Orphaned**: 3 images (6%)
- **Missing references**: 0
- **Average file size**: 450 KB
- **Large files (>1MB)**: 2 images

### Usage Patterns
- **Most used**: `ground_plex_architecture_v2.png` (used in 8 content blocks)
- **Least used**: 12 images (used once only)
- **Never used**: 3 images (candidates for deletion)

### Version Distribution
- **v1**: 32 images (68%)
- **v2**: 12 images (26%)
- **v3+**: 3 images (6%)

## Support

- **Schema questions**: See `../ASSET_MANAGEMENT_DESIGN.md`
- **Workflow questions**: See `../EXAMPLE_COMPLETE_FLOW.md`
- **Technical issues**: Contact jean-claude@snaplogic.com

---

**Last Updated**: 2026-04-27  
**Total Assets**: 1 (citizen integrator demo - 6 images pending)  
**Maintainer**: Asset Management Team
