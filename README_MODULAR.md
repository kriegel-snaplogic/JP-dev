# Modular Content Library Architecture

## Overview

The LaTeX document generation skill now supports a **modular, manifest-based architecture** for building professional documents from reusable content blocks.

## Architecture Components

```
latex-docs/
├── content_library/              # Centralized content repository
│   ├── library/                  # Reusable content blocks
│   │   ├── standard/             # Title pages, templates
│   │   ├── platform/             # Platform overviews, architecture
│   │   ├── security/             # Security & compliance sections
│   │   ├── services/             # Professional services, support
│   │   ├── use_cases/            # Standard use case descriptions
│   │   └── appendices/           # Technical specs, glossaries
│   ├── documents/                # Document-specific custom content
│   │   ├── airbus_rfp/           # Airbus RFP project
│   │   │   ├── manifest.json     # Document blueprint
│   │   │   ├── mgmt_summary.json # Custom executive summary
│   │   │   └── use_cases.json    # Custom use cases
│   │   └── boeing_proposal/      # Boeing proposal project
│   │       └── manifest.json
│   └── .index/                   # Generated search indexes
│       ├── catalog.json          # Full searchable catalog
│       ├── tags.json             # Tag-based index
│       ├── categories.json       # Category hierarchy
│       └── usage.json            # Usage analytics
│
├── scripts/
│   ├── compile_document.py       # Main compiler (supports manifests)
│   ├── index_library.py          # Generate content indexes
│   └── search_library.py         # Query content catalog
│
├── SCHEMA_MANIFEST.md            # Manifest JSON schema
├── SCHEMA_SECTION_BLOCK.md       # Content block JSON schema
├── INDEXER_DESIGN.md             # Indexer architecture & API
└── AI_AGENT_SPECIFICATION.md     # Updated agent guidelines

```

## Key Concepts

### 1. Content Blocks
Self-contained, reusable JSON files with metadata and content.

**Example**: `library/platform/platform_overview_v3.json`
```json
{
  "metadata": {
    "id": "platform_overview_v3",
    "version": "3.0",
    "title": "SnapLogic Platform Overview",
    "tags": ["platform", "architecture", "reusable"],
    "usage_count": 47,
    "variables": {
      "required": ["customer_name", "deployment_type"]
    }
  },
  "content": {
    "title": "SnapLogic Platform Overview",
    "content": "SnapLogic is an enterprise integration platform for {{customer_name}}...",
    "subsections": [...]
  }
}
```

### 2. Manifests
Document blueprints that reference content blocks.

**Example**: `documents/airbus_rfp/manifest.json`
```json
{
  "metadata": {
    "document_title": "Airbus Helicopters RFP Response",
    "customer": "Airbus Helicopters"
  },
  "variables": {
    "customer_name": "Airbus Helicopters",
    "deployment_type": "on-premises"
  },
  "sections": [
    {
      "id": "platform",
      "type": "section",
      "source": "library/platform/platform_overview_v3.json"
    },
    {
      "id": "use_cases",
      "type": "section",
      "source": "documents/airbus_rfp/use_cases.json"
    }
  ]
}
```

### 3. Content Indexer
Searchable catalog enabling content discovery.

**Query examples**:
```bash
# Search by keyword
python3 scripts/search_library.py "security compliance"

# Filter by category
python3 scripts/search_library.py --category platform --subcategory architecture

# Show most used blocks
python3 scripts/search_library.py --most-used --limit 10
```

## Benefits

### For AI Agents
- **Faster generation**: Reuse existing content instead of regenerating
- **Smaller context**: Work with focused content blocks, not entire documents
- **Parallel execution**: Multiple agents prepare different sections simultaneously
- **Discovery**: Search library for relevant content before creating new
- **Consistency**: Same section = same content across all documents

### For Content Maintainers
- **Single source of truth**: Update `platform_overview_v3.json` → affects all referencing documents
- **Version control**: Individual section versioning, clear upgrade paths
- **Usage analytics**: See which blocks are popular, which are dead weight
- **Quality metrics**: Track review dates, compliance status

### For Document Quality
- **Consistency**: Standard sections are identical across documents
- **Refinement**: High-usage blocks are battle-tested and refined over time
- **Governance**: Compliance review tracked at block level
- **Reusability metrics**: Know what works (47 uses) vs. what doesn't (0 uses)

## Workflow Comparison

### Old Monolithic Approach
```
Agent → Generate 20-page JSON → Compile → PDF
         (15 minutes)
```

Problems:
- ❌ Recreates standard sections every time
- ❌ Inconsistent wording across documents
- ❌ Large context (entire document)
- ❌ Sequential generation only
- ❌ No reusability

### New Modular Approach
```
Agent 1 → Query library → Select reusable blocks
Agent 2 → Generate custom mgmt summary        } In parallel
Agent 3 → Generate custom use cases           }
Agent 4 → Build manifest → Compile → PDF

         (5 minutes)
```

Benefits:
- ✅ Reuses 60-80% of content
- ✅ Consistent standard sections
- ✅ Small, focused contexts
- ✅ Parallel execution
- ✅ Content library grows over time

## Quick Start

### 1. Create a Content Library

```bash
mkdir -p content_library/library/{standard,platform,security,services,appendices}
mkdir -p content_library/documents
mkdir -p content_library/.index
```

### 2. Add a Reusable Section

**File**: `content_library/library/platform/platform_overview_v3.json`

```json
{
  "metadata": {
    "id": "platform_overview_v3",
    "version": "3.0",
    "title": "SnapLogic Platform Overview",
    "category": "platform",
    "tags": ["platform", "overview", "reusable"],
    "status": "active",
    "variables": {
      "required": ["customer_name"],
      "optional": []
    }
  },
  "content": {
    "title": "SnapLogic Platform Overview",
    "content": "SnapLogic is an enterprise integration platform...",
    "subsections": []
  }
}
```

### 3. Generate Index

```bash
python3 scripts/index_library.py
```

Output:
```
✅ Indexed 15 content blocks
   📂 Categories: 5
   🏷️  Tags: 23
   📊 Most used: platform_overview_v3 (47 uses)
```

### 4. Create a Manifest

**File**: `content_library/documents/my_proposal/manifest.json`

```json
{
  "metadata": {
    "document_title": "Customer Proposal",
    "document_type": "solution"
  },
  "variables": {
    "customer_name": "Acme Corp"
  },
  "sections": [
    {
      "id": "platform",
      "type": "section",
      "source": "library/platform/platform_overview_v3.json"
    }
  ]
}
```

### 5. Compile

```bash
python3 scripts/compile_document.py \
  content_library/documents/my_proposal/manifest.json \
  output.pdf \
  solution
```

## Implementation Status

### ✅ Completed
- Schema definitions (SCHEMA_MANIFEST.md, SCHEMA_SECTION_BLOCK.md)
- Indexer design (INDEXER_DESIGN.md)
- AI Agent specification updated
- Architecture documentation

### 🚧 To Be Implemented
- [ ] Update `compile_document.py` to support manifest format
- [ ] Implement `index_library.py` script
- [ ] Implement `search_library.py` script
- [ ] Create initial content library with standard blocks
- [ ] Add variable substitution engine
- [ ] Add cross-reference resolution (`[SECTION_REF:id]` → "Section 2.1")
- [ ] Add usage tracking (auto-update `usage_count` on compilation)

### 📋 Future Enhancements
- Semantic search with embeddings
- Web UI for browsing content library
- Recommendation engine ("documents using X also use Y")
- Quality metrics dashboard
- Auto-tagging with ML
- Version diffing tool

## Migration Strategy

### Phase 1: Schema & Tooling (Current)
- ✅ Define schemas
- ✅ Design indexer
- ✅ Update documentation

### Phase 2: Core Implementation
- Update compiler for manifest support
- Build indexer & search tools
- Create initial content library with 10-20 standard blocks

### Phase 3: Content Migration
- Extract reusable sections from existing documents
- Convert to section block format
- Organize into library structure
- Generate indexes

### Phase 4: Agent Integration
- Update AI agents to query library first
- Implement parallel content generation
- Add usage tracking

### Phase 5: Optimization
- Add semantic search
- Build web UI
- Implement advanced analytics

## Best Practices

### Content Block Design
- **One topic per block**: "Platform Architecture" not "Platform + Security + Pricing"
- **Reasonable size**: 1-3 pages typical, 5 pages max
- **Standalone**: Should make sense if read in isolation
- **Generic language**: Use `{{customer_name}}` not hardcoded names
- **Version semantically**: Major version for breaking changes

### Manifest Design
- **Minimal metadata**: Only what's needed
- **Clear section IDs**: Use descriptive names like `platform_arch` not `section_2`
- **Variable completeness**: Provide all required variables
- **Logical ordering**: Title page → Summary → Sections → Appendices

### Library Organization
- **Categorize consistently**: Use standard categories (platform, security, services, etc.)
- **Tag generously**: Multiple tags aid discovery
- **Track usage**: Monitor what's popular vs. unused
- **Review regularly**: Quarterly review of all active blocks

### Agent Behavior
- **Query before creating**: Check library first
- **Prefer high-usage blocks**: More usage = more refined
- **Respect status**: Only use `active` blocks in production
- **Update statistics**: Track usage after compilation

## Documentation

- **SCHEMA_MANIFEST.md**: Complete manifest JSON schema with examples
- **SCHEMA_SECTION_BLOCK.md**: Complete section block schema with examples
- **INDEXER_DESIGN.md**: Indexer architecture, API, and implementation
- **AI_AGENT_SPECIFICATION.md**: Updated with modular workflow guidance

## Support

For questions or issues:
1. Check schema documentation (SCHEMA_*.md files)
2. Review AI agent specification for workflow examples
3. Examine existing content blocks for reference
4. Consult indexer design for search capabilities

## License

Internal SnapLogic tool. Not for external distribution.
