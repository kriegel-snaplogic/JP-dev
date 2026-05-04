# SnapLogic Content Library

## Overview

This directory contains the modular content library for SnapLogic document generation. Content is organized into reusable blocks that can be referenced by document manifests.

## Directory Structure

```
content_library/
├── library/                      # Reusable content blocks
│   ├── standard/                 # Title pages, templates
│   ├── platform/                 # Platform overviews, architecture
│   ├── security/                 # Security & compliance sections
│   ├── services/                 # Professional services, support
│   ├── use_cases/                # Standard use case descriptions
│   └── appendices/               # Technical appendices, user stories
│       └── citizen_integrator_user_story_v1.json  ✅ FIRST BLOCK
│
├── documents/                    # Document-specific custom content
│   └── <project_name>/
│       ├── manifest.json         # Document blueprint
│       └── *.json                # Custom section blocks
│
└── .index/                       # Generated search indexes (auto-created)
    ├── catalog.json              # Full searchable catalog
    ├── tags.json                 # Tag-based index
    ├── categories.json           # Category hierarchy
    └── usage.json                # Usage analytics
```

## Current Content

### Appendices (1 block)

| ID | Title | Version | Tags | Usage |
|----|-------|---------|------|-------|
| `citizen_integrator_user_story_v1` | Citizen Integrator User Story with SnapGPT | 1.0 | citizen_integrator, snapgpt, ai, low_code, user_story | 0 uses |

**Description**: Detailed walkthrough demonstrating how business analysts and non-developers use SnapGPT to create integration pipelines through natural language. Includes 7 annotated screenshots showing the complete workflow from prompt to validation.

**Images Required**: 7 screenshots in `assets/citizen-integrator/`

## Usage

### Query the Library

Once the indexer is implemented:

```bash
# Search for citizen integrator content
python3 scripts/search_library.py "citizen integrator"

# Browse appendices
python3 scripts/search_library.py --category appendices
```

### Reference in Manifest

```json
{
  "sections": [
    {
      "id": "appendix_citizen_integrator",
      "type": "appendix",
      "source": "library/appendices/citizen_integrator_user_story_v1.json",
      "required": false
    }
  ]
}
```

### Add New Content Block

1. Create JSON file following `SCHEMA_SECTION_BLOCK.md`
2. Place in appropriate category directory
3. Regenerate index: `python3 scripts/index_library.py`
4. Content now discoverable by all agents

## Content Block Schema

See `../SCHEMA_SECTION_BLOCK.md` for complete schema documentation.

**Minimal required fields**:
```json
{
  "metadata": {
    "id": "unique_id_v1",
    "version": "1.0",
    "title": "Block Title",
    "status": "active",
    "category": "appendices",
    "tags": ["tag1", "tag2"]
  },
  "content": {
    "title": "Section Title",
    "content": "Section content...",
    "subsections": []
  }
}
```

## Roadmap

### Phase 1: Initial Library (In Progress)
- [x] Create directory structure
- [x] Add first content block (Citizen Integrator User Story)
- [ ] Add 5 more appendices
- [ ] Add 5 platform blocks
- [ ] Add 5 security blocks
- [ ] Add 3 services blocks

### Phase 2: Indexer (Next)
- [ ] Implement `index_library.py`
- [ ] Implement `search_library.py`
- [ ] Generate initial index
- [ ] Test query functionality

### Phase 3: Compiler Support
- [ ] Update `compile_document.py` for manifest format
- [ ] Add variable substitution engine
- [ ] Add cross-reference resolution
- [ ] Test end-to-end compilation

### Phase 4: Migration
- [ ] Extract reusable sections from existing documents
- [ ] Convert to section block format
- [ ] Organize into library
- [ ] Update usage statistics

## Contributing

When adding content blocks:

1. **Use semantic IDs**: `category_topic_v1`, not `block_001`
2. **Version semantically**: Increment version for breaking changes
3. **Tag generously**: More tags = better discovery
4. **Track dependencies**: List all images, sections referenced
5. **Set compliance dates**: Review quarterly for active blocks

## Support

- **Schema questions**: See `../SCHEMA_SECTION_BLOCK.md`
- **Workflow questions**: See `../EXAMPLE_COMPLETE_FLOW.md`
- **Architecture overview**: See `../README_MODULAR.md`

---

**Last Updated**: 2026-04-27  
**Maintainer**: Jean-Claude, Advisor to the CEO
