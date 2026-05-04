# Asset & Content Management Design

## The Problem

Current architecture has critical gaps:

1. **Images have no home**: Content blocks reference `assets/citizen-integrator/1-Designer.png` but where does this actually live?
2. **No promotion workflow**: How does new content go from draft → review → approved → library?
3. **No asset reuse tracking**: Which content blocks use which images? Can I delete this image?
4. **No lifecycle management**: How do images get updated? How are old versions archived?
5. **No staging area**: New content created by agents needs review before becoming "official"

## Proposed Structure

```
content_library/
├── assets/                       # Asset repository
│   ├── images/                   # Image library
│   │   ├── platform/
│   │   │   ├── architecture/
│   │   │   │   ├── ground_plex_v1.png
│   │   │   │   ├── ground_plex_v2.png
│   │   │   │   └── cloud_hybrid_v1.png
│   │   │   ├── screenshots/
│   │   │   │   ├── designer_interface_v1.png
│   │   │   │   └── pipeline_canvas_v2.png
│   │   │   └── diagrams/
│   │   │       └── data_flow_etl_v1.png
│   │   ├── security/
│   │   │   ├── architecture_overview_v1.png
│   │   │   └── encryption_diagram_v1.png
│   │   ├── use_cases/
│   │   │   ├── citizen_integrator/
│   │   │   │   ├── step1_designer_v1.png
│   │   │   │   ├── step2_snapgpt_preview_v1.png
│   │   │   │   ├── step3_snap_config_v1.png
│   │   │   │   ├── step4_drag_drop_v1.png
│   │   │   │   ├── step5_validation_v1.png
│   │   │   │   └── step6_output_preview_v1.png
│   │   │   └── etl_modernization/
│   │   ├── branding/
│   │   │   ├── snaplogic-logo-white.png
│   │   │   ├── snaplogic-logo-color.png
│   │   │   └── partner-logos/
│   │   └── customer/              # Customer-specific assets
│   │       ├── airbus/
│   │       └── boeing/
│   ├── metadata/                  # Asset metadata & tracking
│   │   ├── image_catalog.json     # Central asset catalog
│   │   └── usage_map.json         # Which blocks use which assets
│   └── README.md
│
├── library/                       # Approved reusable content
│   ├── platform/
│   ├── security/
│   ├── appendices/
│   │   └── citizen_integrator_user_story_v1.json
│   └── ...
│
├── staging/                       # New content awaiting review
│   ├── pending_review/
│   │   ├── platform_overview_v4_DRAFT.json
│   │   └── new_security_section_DRAFT.json
│   ├── in_review/
│   │   └── compliance_update_v2_REVIEW.json
│   └── rejected/
│       └── outdated_feature_v1_REJECTED.json
│
├── documents/                     # Project-specific content
│   └── <project_name>/
│
├── .index/                        # Generated search indexes
│   ├── catalog.json
│   ├── asset_index.json           # NEW: Asset catalog
│   └── ...
│
└── .metadata/                     # Repository metadata
    ├── promotion_log.json         # History of promotions
    ├── review_queue.json          # Content awaiting review
    └── deprecation_log.json       # Deprecated content tracking
```

## Asset Library Design

### Image Catalog Schema

**File**: `assets/metadata/image_catalog.json`

```json
{
  "version": "1.0",
  "last_updated": "2026-04-27T21:30:00Z",
  "total_images": 47,
  "images": [
    {
      "id": "citizen_integrator_step1_v1",
      "filename": "step1_designer_v1.png",
      "path": "assets/images/use_cases/citizen_integrator/step1_designer_v1.png",
      "category": "use_cases",
      "subcategory": "citizen_integrator",
      "type": "screenshot",
      "version": "1.0",
      
      "metadata": {
        "title": "SnapLogic Designer Interface with SnapGPT Sidebar",
        "description": "Shows the Designer canvas with SnapGPT panel open on the right side",
        "created": "2024-08-15",
        "last_updated": "2024-08-15",
        "author": "Product Marketing",
        "source": "SnapLogic Platform v6.2",
        "tags": ["designer", "snapgpt", "ui", "screenshot", "citizen_integrator"],
        "resolution": "1920x1080",
        "format": "png",
        "file_size_kb": 342
      },
      
      "usage": {
        "used_by_blocks": [
          "citizen_integrator_user_story_v1"
        ],
        "usage_count": 1,
        "last_used": "2026-04-27"
      },
      
      "licensing": {
        "license": "SnapLogic Internal",
        "customer_facing": true,
        "approval_required": false,
        "approved_by": "legal@snaplogic.com",
        "approved_date": "2024-08-20"
      },
      
      "versions": {
        "current": "1.0",
        "previous": [],
        "deprecated": []
      },
      
      "related_assets": [
        "citizen_integrator_step2_v1",
        "citizen_integrator_step3_v1"
      ]
    }
  ]
}
```

### Asset Usage Map

**File**: `assets/metadata/usage_map.json`

Tracks which content blocks use which assets:

```json
{
  "content_to_assets": {
    "citizen_integrator_user_story_v1": [
      "citizen_integrator_step1_v1",
      "citizen_integrator_step2_v1",
      "citizen_integrator_step3_v1",
      "citizen_integrator_step4_v1",
      "citizen_integrator_step5_v1",
      "citizen_integrator_step6_v1"
    ],
    "platform_architecture_ground_plex_v2": [
      "ground_plex_architecture_v2",
      "deployment_diagram_v1"
    ]
  },
  
  "asset_to_content": {
    "citizen_integrator_step1_v1": [
      "citizen_integrator_user_story_v1"
    ],
    "ground_plex_architecture_v2": [
      "platform_architecture_ground_plex_v2",
      "airbus_rfp_platform_section_custom",
      "technical_whitepaper_architecture_v1"
    ]
  }
}
```

**Purpose**: 
- Before deleting an image, check if any content blocks reference it
- When updating an image, know which content blocks are affected
- Identify orphaned images (not used by any content)

## Content Promotion Workflow

### Lifecycle States

```
DRAFT → PENDING_REVIEW → IN_REVIEW → APPROVED → LIBRARY
  ↓         ↓               ↓            ↓
REJECTED  REJECTED      REJECTED     DEPRECATED
```

### State Definitions

1. **DRAFT**: Being created by agent or human, work in progress
   - Location: `staging/pending_review/`
   - Filename: `*_DRAFT.json`
   - Status: `"status": "draft"`

2. **PENDING_REVIEW**: Ready for review, in queue
   - Location: `staging/pending_review/`
   - Filename: `*_DRAFT.json`
   - Metadata: Added to `review_queue.json`

3. **IN_REVIEW**: Actively being reviewed
   - Location: `staging/in_review/`
   - Filename: `*_REVIEW.json`
   - Reviewer assigned, review in progress

4. **APPROVED**: Passed review, ready for promotion
   - Location: `staging/in_review/`
   - Filename: `*_APPROVED.json`
   - Next: Promote to library

5. **LIBRARY**: Production-ready, in official library
   - Location: `library/<category>/`
   - Filename: `<id>_v<version>.json`
   - Status: `"status": "active"`

6. **REJECTED**: Failed review, needs rework
   - Location: `staging/rejected/`
   - Filename: `*_REJECTED.json`
   - Rejection reason logged

7. **DEPRECATED**: Old version, superseded by newer
   - Location: `library/<category>/`
   - Filename: `<id>_v<old_version>.json`
   - Status: `"status": "deprecated"`
   - Points to newer version

### Promotion Commands

**Command**: `scripts/promote_content.py`

```bash
# Submit draft for review
python3 scripts/promote_content.py submit \
  staging/pending_review/platform_overview_v4_DRAFT.json \
  --reviewer="solutions-team@snaplogic.com"

# Approve content (moves to library)
python3 scripts/promote_content.py approve \
  staging/in_review/platform_overview_v4_REVIEW.json

# Reject content (with reason)
python3 scripts/promote_content.py reject \
  staging/in_review/platform_overview_v4_REVIEW.json \
  --reason="Outdated feature references, needs update"

# Deprecate old version
python3 scripts/promote_content.py deprecate \
  library/platform/platform_overview_v3.json \
  --successor="platform_overview_v4"
```

### Review Queue

**File**: `.metadata/review_queue.json`

```json
{
  "pending": [
    {
      "id": "platform_overview_v4",
      "path": "staging/pending_review/platform_overview_v4_DRAFT.json",
      "submitted_by": "agent_rfp_builder",
      "submitted_date": "2026-04-27T10:00:00Z",
      "priority": "normal",
      "reviewer": "solutions-team@snaplogic.com",
      "review_deadline": "2026-04-30T17:00:00Z"
    }
  ],
  
  "in_review": [
    {
      "id": "compliance_update_v2",
      "path": "staging/in_review/compliance_update_v2_REVIEW.json",
      "reviewer": "legal@snaplogic.com",
      "review_started": "2026-04-26T14:00:00Z",
      "status": "awaiting_legal_approval"
    }
  ],
  
  "approved": [
    {
      "id": "security_overview_v3",
      "path": "staging/in_review/security_overview_v3_APPROVED.json",
      "approved_by": "security-team@snaplogic.com",
      "approved_date": "2026-04-25T16:30:00Z",
      "ready_for_promotion": true
    }
  ]
}
```

### Promotion Log

**File**: `.metadata/promotion_log.json`

```json
{
  "promotions": [
    {
      "id": "citizen_integrator_user_story_v1",
      "promoted_date": "2026-04-27T21:00:00Z",
      "promoted_by": "jean-claude@snaplogic.com",
      "source_path": "staging/in_review/citizen_integrator_story_APPROVED.json",
      "destination_path": "library/appendices/citizen_integrator_user_story_v1.json",
      "review_status": "approved",
      "reviewer": "solutions-team@snaplogic.com"
    }
  ]
}
```

## Asset Promotion Workflow

### New Image Submission

**Location**: `assets/images/staging/`

```bash
# Submit new image for approval
python3 scripts/promote_asset.py submit \
  /path/to/new_screenshot.png \
  --category=platform \
  --subcategory=screenshots \
  --title="New Platform Feature X" \
  --description="Screenshot showing Feature X in Designer" \
  --tags=designer,feature_x,screenshot

# Generates:
# - Copies image to staging area
# - Creates metadata entry
# - Adds to review queue
# - Assigns reviewer
```

**Output**:
```
✅ Asset submitted for review
   ID: platform_feature_x_v1
   Path: assets/images/staging/platform_feature_x_v1_DRAFT.png
   Reviewer: product-marketing@snaplogic.com
   Review deadline: 2026-05-01
```

### Image Review & Approval

```bash
# Approve image (moves to library)
python3 scripts/promote_asset.py approve \
  platform_feature_x_v1

# Moves from:
#   assets/images/staging/platform_feature_x_v1_DRAFT.png
# To:
#   assets/images/platform/screenshots/platform_feature_x_v1.png

# Updates:
#   - image_catalog.json (adds official entry)
#   - Removes from staging
#   - Sets status: approved
```

## Automatic Asset Discovery

When content blocks are created, automatically detect and register images:

**Script**: `scripts/discover_assets.py`

```python
#!/usr/bin/env python3
"""
Scan content blocks for image references and register them in asset catalog
"""

import json
import re
from pathlib import Path

def scan_content_block(block_path):
    """Find all image references in a content block"""
    with open(block_path) as f:
        block = json.load(f)
    
    content_str = json.dumps(block['content'])
    
    # Find [IMAGE:path:caption:width] tags
    image_pattern = r'\[IMAGE:([^:]+):[^\]]+\]'
    images = re.findall(image_pattern, content_str)
    
    return images

def register_asset(image_path, used_by_block):
    """Register image in asset catalog"""
    # Check if image exists in assets/images/
    # If not, flag as missing
    # Add to usage_map.json linking to content block
    pass

# Scan all content blocks
for block_file in Path('library').rglob('*.json'):
    images = scan_content_block(block_file)
    for img in images:
        register_asset(img, block_file.stem)
```

## Migration Strategy

### Phase 1: Organize Existing Assets

```bash
# Step 1: Create asset directory structure
mkdir -p assets/images/{platform,security,use_cases,branding,customer}
mkdir -p assets/metadata
mkdir -p staging/{pending_review,in_review,rejected}

# Step 2: Copy existing images to organized structure
# Example: citizen integrator images
mkdir -p assets/images/use_cases/citizen_integrator
cp assets/citizen-integrator/*.png \
   assets/images/use_cases/citizen_integrator/

# Step 3: Generate asset catalog
python3 scripts/generate_asset_catalog.py

# Step 4: Update content block references
# From: assets/citizen-integrator/1-Designer.png
# To:   assets/images/use_cases/citizen_integrator/step1_designer_v1.png
```

### Phase 2: Update Content Blocks

Update existing content blocks to use new asset paths:

```python
# Update citizen_integrator_user_story_v1.json
old_path = "assets/citizen-integrator/1-Designer.png"
new_path = "assets/images/use_cases/citizen_integrator/step1_designer_v1.png"

# Update references in content
# Update dependencies.images array
```

### Phase 3: Implement Promotion Tools

```bash
# Implement promotion scripts
scripts/
├── promote_content.py      # Content block promotion
├── promote_asset.py        # Asset promotion
├── discover_assets.py      # Automatic asset discovery
└── generate_asset_catalog.py  # Build asset catalog
```

## Best Practices

### For Content Creators

1. **Start in staging**: Create new content in `staging/pending_review/`
2. **Use relative paths**: Reference assets as `assets/images/category/file.png`
3. **Submit for review**: Use `promote_content.py submit` when ready
4. **Track dependencies**: List all images in `dependencies.images`

### For Asset Managers

1. **Organize by category**: Platform, security, use cases, etc.
2. **Version images**: `feature_x_v1.png`, `feature_x_v2.png`
3. **Track usage**: Run `discover_assets.py` regularly
4. **Archive old versions**: Move to `assets/images/archive/` not delete

### For Reviewers

1. **Check asset quality**: Resolution, clarity, branding compliance
2. **Verify licensing**: Customer-facing approval for screenshots
3. **Test content**: Compile to PDF, verify renders correctly
4. **Approve or reject**: Use promotion scripts with clear feedback

### For Agents

1. **Query staging first**: Check if draft content exists before creating new
2. **Use approved assets**: Reference `assets/images/` not random paths
3. **Submit for review**: Don't auto-promote to library
4. **Track asset usage**: Update `usage_map.json` when using images

## Automation Opportunities

### Git Hooks

```bash
# pre-commit hook
# - Validate content block JSON schema
# - Check all image references exist
# - Update usage_map.json automatically

# post-merge hook
# - Regenerate asset catalog
# - Update content library index
# - Check for orphaned assets
```

### Scheduled Jobs

```bash
# Daily: Check for unused assets
python3 scripts/audit_assets.py --find-orphans

# Weekly: Review queue digest
python3 scripts/review_digest.py --email=solutions-team@snaplogic.com

# Monthly: Deprecation audit
python3 scripts/audit_deprecated.py --older-than=6months
```

## Metrics to Track

### Asset Health
- **Orphaned images**: Images not referenced by any content block
- **Missing images**: Content blocks reference non-existent images
- **Large files**: Images >1MB (optimize for PDF compilation)
- **Outdated screenshots**: Images from old product versions

### Content Health
- **Review queue depth**: How many blocks awaiting review
- **Time to approval**: Average time from submission to approval
- **Rejection rate**: % of content rejected on first review
- **Deprecation rate**: How often content needs updating

### Usage Patterns
- **Popular assets**: Most-referenced images (reuse candidates)
- **Underutilized assets**: Images created but rarely used
- **Content churn**: Blocks that get updated frequently
- **Stable content**: Blocks that remain unchanged (good quality)

## Implementation Priority

### Phase 1: Asset Organization (Week 1)
- [x] Design asset structure
- [ ] Create directory structure
- [ ] Move existing images to organized structure
- [ ] Generate initial asset catalog
- [ ] Update first content block with new paths

### Phase 2: Promotion Workflow (Week 2)
- [ ] Implement `promote_content.py`
- [ ] Implement `promote_asset.py`
- [ ] Create review queue system
- [ ] Set up staging directories
- [ ] Document promotion process

### Phase 3: Automation (Week 3)
- [ ] Implement `discover_assets.py`
- [ ] Build usage map generator
- [ ] Create orphan asset detector
- [ ] Set up Git hooks
- [ ] Add validation checks

### Phase 4: Integration (Week 4)
- [ ] Update compiler to handle asset paths
- [ ] Integrate with content library indexer
- [ ] Add asset search to query tools
- [ ] Test end-to-end workflow
- [ ] Train agents on new system

---

**Status**: Design phase complete  
**Next**: Implement Phase 1 (Asset Organization)
