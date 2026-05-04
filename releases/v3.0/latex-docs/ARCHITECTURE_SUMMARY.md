# Modular Content Architecture - Summary

## The Big Picture

```
Generation Request (INPUT)
         ↓
    Content Agent
    - Queries library
    - Generates custom sections
    - Builds manifest
         ↓
    Manifest + Section Blocks
         ↓
    Compiler
    - Assembles sections
    - Substitutes variables
    - Generates LaTeX
    - Produces PDF
         ↓
    Professional PDF (OUTPUT)
```

## Four-Layer Architecture

### Layer 1: Generation Request (INPUT)
**File**: `requests/<project>.json`  
**Schema**: `SCHEMA_GENERATION_REQUEST.md`

What agents receive as input:
- Customer context (technical + business)
- Requirements (structured, categorized)
- Use cases (detailed scenarios)
- Assets (images, data files)
- Content preferences (reuse vs. custom)

**Example**: Airbus RFP with 114 requirements, 3 use cases, compliance needs

### Layer 2: Asset Library (IMAGES & MEDIA)
**Location**: `content_library/assets/`  
**Schema**: `ASSET_MANAGEMENT_DESIGN.md`

Centralized asset repository:
```
assets/
├── images/
│   ├── platform/          # Platform screenshots, diagrams
│   ├── security/          # Security architecture visuals
│   ├── use_cases/         # Use case workflows
│   ├── branding/          # Logos, brand assets
│   └── customer/          # Customer-specific assets
└── metadata/
    ├── image_catalog.json # Central asset catalog
    └── usage_map.json     # Asset-to-content mapping
```

**Key Features**:
- Organized by category (platform, security, use cases)
- Version tracking (`file_v1.png`, `file_v2.png`)
- Usage tracking (which content blocks use which assets)
- Licensing metadata (customer-facing approval)
- Promotion workflow (staging → review → approved)

### Layer 3: Content Library (MODULAR BLOCKS)
**Location**: `content_library/library/`  
**Schema**: `SCHEMA_SECTION_BLOCK.md`

Reusable content blocks:
```
library/
├── platform/           # Platform overviews, architecture
├── security/           # Security & compliance
├── services/           # Professional services
├── use_cases/          # Standard use case templates
└── appendices/         # Technical specs, glossaries

staging/
├── pending_review/     # New content awaiting review
├── in_review/          # Currently being reviewed
└── rejected/           # Failed review, needs rework

documents/
└── <project>/          # Project-specific custom content
```

**Key Features**:
- Metadata (version, tags, usage stats, variables)
- Content (title, text, subsections)
- Dependencies (images, other sections)
- Compliance tracking (review dates, approval status)
- Promotion workflow (draft → review → approved → library)

### Layer 4: Document Manifest (BLUEPRINT)
**File**: `documents/<project>/manifest.json`  
**Schema**: `SCHEMA_MANIFEST.md`

Document blueprint:
- Metadata (title, customer, date)
- Variables (customer_name, deployment_type, etc.)
- Sections array (references to library + custom blocks)
- Configuration (TOC, branding, output)

**Example**:
```json
{
  "sections": [
    {"source": "library/platform/overview_v3.json"},     // Reusable
    {"source": "documents/airbus/use_cases.json"}        // Custom
  ]
}
```

## Content Discovery: The Indexer

**Location**: `.index/`  
**Design**: `INDEXER_DESIGN.md`

Searchable catalog enabling content discovery:

```bash
# Search by keyword
python3 scripts/search_library.py "security compliance"

# Filter by category
python3 scripts/search_library.py --category platform

# Show most used
python3 scripts/search_library.py --most-used
```

**Index Files**:
- `catalog.json` — Full searchable catalog
- `tags.json` — Tag-based lookup
- `categories.json` — Category hierarchy
- `usage.json` — Usage analytics

**Agent API**:
```python
results = index.query(
    search="security",
    tags=["reusable"],
    deployment_type="on-premises"
)
```

## Agent Workflow

### Sequential (Old Monolithic Approach)
```
Agent → Generate 20-page JSON → Compile → PDF
Time: 15 minutes
Reuse: 0%
```

### Parallel (New Modular Approach)
```
Step 1: Query Library
  ↓ Find 4 reusable sections (platform, security, services, appendix)

Step 2: Generate Custom Sections (PARALLEL)
  Agent A → Management Summary
  Agent B → Use Cases
  Agent C → Migration Approach
  Agent D → Pricing

Step 3: Build Manifest
  ↓ Reference 4 library + 4 custom sections

Step 4: Compile
  ↓ Assemble → PDF

Time: 5 minutes (3x faster)
Reuse: 44% (first document), 60-80% (mature library)
```

## Key Benefits

### For Speed
- ⚡ **3x faster**: 5min vs 15min (parallel execution + reuse)
- ⚡ **Scales**: More agents = more parallelism
- ⚡ **No redundant work**: Don't regenerate standard sections

### For Consistency
- 🎯 **Single source of truth**: Update once, affects all documents
- 🎯 **Battle-tested**: High-usage blocks refined over time
- 🎯 **Version control**: Track changes at section level

### For Quality
- ✅ **Usage analytics**: See what works (92 uses) vs. dead weight (0 uses)
- ✅ **Compliance tracking**: Review dates, legal approval per block
- ✅ **Dependency mapping**: Know what images/sections each block needs

### For Maintenance
- 🔧 **Update once**: Change `security_v2.json` → affects 50 documents
- 🔧 **Clear deprecation**: Mark old versions, point to new
- 🔧 **Usage visibility**: Which blocks are popular? Which unused?

## Implementation Status

### ✅ Phase 1: Design (COMPLETE)
- [x] Schema definitions (Manifest, Section Block, Generation Request)
- [x] Indexer architecture design
- [x] AI Agent specification updated
- [x] Complete workflow documentation
- [x] Example end-to-end flow

### 🚧 Phase 2: Implementation (NEXT)
- [ ] Update `compile_document.py` for manifest support
- [ ] Implement `index_library.py` (catalog generator)
- [ ] Implement `search_library.py` (query tool)
- [ ] Build initial content library (20 standard blocks)
- [ ] Add variable substitution engine
- [ ] Add cross-reference resolution

### 📋 Phase 3: Migration
- [ ] Extract reusable sections from existing documents
- [ ] Convert to section block format
- [ ] Organize into library structure
- [ ] Train agents on new workflow

### 🚀 Phase 4: Enhancement
- [ ] Semantic search with embeddings
- [ ] Web UI for browsing library
- [ ] Recommendation engine
- [ ] Quality metrics dashboard

## Documentation Index

| Document | Purpose | Size |
|----------|---------|------|
| `README_MODULAR.md` | Architecture overview, quick start, best practices | 3,500 words |
| `SCHEMA_MANIFEST.md` | Document manifest JSON schema | 2,500 words |
| `SCHEMA_SECTION_BLOCK.md` | Content block JSON schema | 2,800 words |
| `SCHEMA_GENERATION_REQUEST.md` | Agent input format schema | 4,200 words |
| `INDEXER_DESIGN.md` | Content discovery & search design | 3,200 words |
| `ASSET_MANAGEMENT_DESIGN.md` | **NEW**: Asset library & promotion workflow | 5,500 words |
| `EXAMPLE_COMPLETE_FLOW.md` | End-to-end example (Request → PDF) | 3,800 words |
| `AI_AGENT_SPECIFICATION.md` | Updated agent guidelines | 21,000 words (updated) |
| `ARCHITECTURE_SUMMARY.md` | This document | 1,500 words |
| `content_library/README.md` | Content library user guide | 1,200 words |
| `content_library/assets/README.md` | **NEW**: Asset library user guide | 2,000 words |

**Total**: ~51,000 words of comprehensive documentation

## Quick Start

### For Agents
1. Receive **Generation Request** with customer context + requirements
2. **Query library** for reusable sections
3. **Generate custom** sections for gaps
4. **Build manifest** referencing library + custom blocks
5. **Compile** to PDF

### For Content Creators
1. **Create section block** with metadata + content
2. **Save to library** in appropriate category
3. **Regenerate index**: `python3 scripts/index_library.py`
4. Now discoverable by all agents

### For Compilation
```bash
# Manifest-based (NEW)
python3 scripts/compile_document.py \
  documents/project/manifest.json \
  output.pdf \
  solution

# Monolithic JSON (LEGACY, still supported)
python3 scripts/compile_document.py \
  input.json \
  output.pdf \
  solution
```

## Design Principles

### 1. Composability
Small, focused blocks compose into complete documents.

### 2. Single Responsibility
Each section block has one clear purpose.

### 3. DRY (Don't Repeat Yourself)
Write once, reuse everywhere.

### 4. Discoverability
Tags, categories, search make content easy to find.

### 5. Versioning
Sections evolve independently with clear upgrade paths.

### 6. Observable
Usage stats, compliance tracking, dependency mapping.

### 7. Fail-Safe
Validation at request → manifest → compilation stages.

## Metrics to Track

### Content Reuse
- **Reuse percentage**: Library sections / Total sections
- **Target**: 60-80% for mature library
- **Airbus example**: 44% on first document (4/9 sections)

### Library Health
- **Coverage**: Categories with good selection of blocks
- **Freshness**: Blocks with recent review dates
- **Activity**: High-usage blocks vs. never-used blocks

### Agent Performance
- **Generation time**: Target 5min for 20-page document
- **Parallel efficiency**: Speedup from multiple agents
- **Query success**: % of queries finding suitable blocks

### Quality
- **Compliance coverage**: % blocks with legal approval
- **Dependency completeness**: % blocks with listed dependencies
- **Review current**: % blocks reviewed within last quarter

## ROI

### Time Savings
- **Per document**: 10min saved (15min → 5min)
- **Volume**: 50 documents/year
- **Annual savings**: 500 minutes = 8.3 hours

### Consistency
- **Reduced rework**: Fewer "wait, this section is wrong" moments
- **Faster review**: Legal reviews block, not entire document
- **Quality improvement**: Battle-tested sections get better over time

### Scalability
- **Library grows**: Each new document adds potential reusable content
- **Agent efficiency**: Spend time on custom content, not boilerplate
- **Maintenance**: Update once vs. find-and-replace across 50 docs

## Contact

For questions about this architecture:
- Schema questions → Check `SCHEMA_*.md` files
- Workflow questions → Check `EXAMPLE_COMPLETE_FLOW.md`
- Implementation questions → Check `INDEXER_DESIGN.md`
- Agent integration → Check `AI_AGENT_SPECIFICATION.md`

---

**Status**: Design phase complete, ready for implementation.  
**Next**: Implement compiler manifest support + indexer scripts.
