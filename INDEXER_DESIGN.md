# Content Library Indexer Design

## Overview
The indexer enables AI agents and tools to discover, search, and select appropriate content blocks from the library. It maintains a searchable catalog with metadata, usage stats, and semantic capabilities.

## Architecture

### Index Structure
```
content_library/
├── library/              # Reusable content blocks
│   ├── platform/
│   ├── security/
│   ├── services/
│   └── appendices/
├── documents/            # Document-specific custom content
│   ├── airbus_rfp/
│   └── boeing_proposal/
└── .index/              # Generated index files
    ├── catalog.json     # Full searchable catalog
    ├── tags.json        # Tag index for fast lookup
    ├── categories.json  # Category hierarchy
    └── usage.json       # Usage analytics
```

### Index Generation

**Trigger**: Run indexer after any content change
```bash
python3 scripts/index_library.py
```

**Process**:
1. Scan `content_library/library/` and `content_library/documents/`
2. Parse each `*.json` section block
3. Extract metadata, validate schema
4. Build searchable catalog with:
   - Full-text search on title/description
   - Tag-based filtering
   - Category hierarchy
   - Usage statistics
   - Dependency mapping
5. Write to `.index/*.json`

### Catalog Format

**catalog.json**:
```json
{
  "generated": "2026-04-27T15:30:00Z",
  "version": "1.0",
  "total_blocks": 127,
  "blocks": [
    {
      "id": "platform_overview_v3",
      "path": "library/platform/platform_overview_v3.json",
      "version": "3.0",
      "title": "SnapLogic Platform Overview",
      "description": "Comprehensive overview of SnapLogic's enterprise integration platform including architecture, capabilities, and differentiators",
      "category": "platform",
      "subcategory": "overview",
      "tags": ["platform", "architecture", "overview", "reusable", "standard"],
      "status": "active",
      "author": "Solutions Engineering",
      "created": "2024-01-15",
      "last_updated": "2026-04-20",
      "usage_count": 47,
      "last_used": "2026-04-27",
      "variables_required": ["customer_name", "deployment_type"],
      "variables_optional": ["focus", "show_pricing"],
      "dependencies": {
        "images": ["High_Level_Architecture.png"],
        "sections": []
      },
      "compliance": {
        "review_required": false,
        "legal_approved": true
      },
      "file_size_kb": 12.5,
      "estimated_pages": 2.5
    }
  ]
}
```

**tags.json**:
```json
{
  "platform": [
    "platform_overview_v3",
    "architecture_ground_plex_v2",
    "architecture_hybrid_v1"
  ],
  "security": [
    "security_compliance_overview_v2",
    "data_protection_v1"
  ],
  "reusable": [
    "platform_overview_v3",
    "security_compliance_overview_v2"
  ]
}
```

**categories.json**:
```json
{
  "platform": {
    "overview": [
      {
        "id": "platform_overview_v3",
        "title": "SnapLogic Platform Overview",
        "status": "active"
      },
      {
        "id": "company_overview_v3",
        "title": "Company Overview",
        "status": "active"
      }
    ],
    "architecture": [
      {
        "id": "architecture_ground_plex_v2",
        "title": "Ground Plex Architecture",
        "status": "active"
      }
    ]
  },
  "security": {
    "compliance": [
      {
        "id": "security_compliance_overview_v2",
        "title": "Security & Compliance Overview",
        "status": "active"
      }
    ]
  }
}
```

**usage.json**:
```json
{
  "most_used": [
    {
      "id": "platform_overview_v3",
      "usage_count": 47,
      "last_used": "2026-04-27"
    },
    {
      "id": "security_compliance_overview_v2",
      "usage_count": 89,
      "last_used": "2026-04-27"
    }
  ],
  "least_used": [
    {
      "id": "legacy_pricing_v1",
      "usage_count": 2,
      "last_used": "2025-06-15"
    }
  ],
  "never_used": [
    {
      "id": "experimental_ai_features_v1",
      "usage_count": 0
    }
  ],
  "recent_updates": [
    {
      "id": "security_compliance_overview_v2",
      "last_updated": "2026-04-20"
    }
  ]
}
```

## Query Interface

### 1. Agent Query Tool

Agents use standardized queries to discover content:

```python
# Query by tags
results = index.query(tags=["platform", "architecture"], status="active")

# Query by category
results = index.query(category="security", subcategory="compliance")

# Full-text search
results = index.query(search="ground plex deployment architecture")

# Combined query
results = index.query(
    search="security",
    tags=["compliance", "reusable"],
    status="active",
    variables_required_subset=["customer_name"]  # Only blocks requiring these vars
)

# Most used blocks in category
results = index.query(category="platform", sort_by="usage_count", limit=5)
```

### 2. CLI Search Tool

```bash
# Search by keyword
python3 scripts/search_library.py "ground plex architecture"

# List by category
python3 scripts/search_library.py --category platform --subcategory architecture

# Filter by tags
python3 scripts/search_library.py --tags security,compliance,reusable

# Show most used
python3 scripts/search_library.py --most-used --limit 10

# Show blocks needing review
python3 scripts/search_library.py --review-due

# Validate all blocks
python3 scripts/search_library.py --validate
```

### 3. Web Interface (Optional)

Simple Flask/FastAPI app serving the index:

```
GET /api/blocks                    # List all blocks
GET /api/blocks/{id}               # Get block details
GET /api/search?q=security         # Full-text search
GET /api/tags                      # List all tags
GET /api/categories                # List categories
GET /api/usage/top                 # Top 20 most used
GET /api/compliance/review-due     # Blocks needing review
```

Web UI for browsing:
- Browse by category/tag
- Search bar with autocomplete
- Click to copy block ID/path
- Usage statistics dashboard

## Agent Workflow Examples

### Example 1: Agent Needs Standard Security Section

**Agent prompt**: "I need a security section covering SOC 2, ISO 27001, and data residency for an RFP"

**Agent action**:
```python
results = index.query(
    search="security compliance SOC 2 ISO 27001",
    category="security",
    status="active",
    tags=["reusable"]
)

# Returns: security_compliance_overview_v2
# Agent adds to manifest:
{
  "id": "security",
  "type": "section",
  "source": "library/security/security_compliance_overview_v2.json",
  "variables": {
    "certifications": ["SOC 2", "ISO 27001"],
    "data_residency": "France"
  }
}
```

### Example 2: Agent Discovers Available Architecture Options

**Agent prompt**: "What architecture sections are available?"

**Agent action**:
```python
results = index.query(category="platform", subcategory="architecture")

# Returns:
# - architecture_ground_plex_v2 (on-premises)
# - architecture_cloud_v1 (cloud-only)
# - architecture_hybrid_v1 (cloud + on-prem)

# Agent selects based on customer deployment_type
```

### Example 3: Agent Checks Variable Requirements

**Agent prompt**: "Build manifest for customer 'Acme Corp', deployment 'hybrid'"

**Agent action**:
```python
# Agent selects sections
selected = [
    "platform_overview_v3",
    "architecture_hybrid_v1",
    "security_compliance_overview_v2"
]

# Check all required variables
all_required_vars = set()
for block_id in selected:
    block = index.get_block(block_id)
    all_required_vars.update(block['variables_required'])

# all_required_vars = {"customer_name", "deployment_type", "cloud_regions", "on_prem_locations"}

# Agent checks: do we have all variables?
# If missing, agent prompts user or infers from context
```

### Example 4: Agent Finds Deprecated Content

**Agent action**:
```python
# Check if using deprecated blocks
deprecated = index.query(status="deprecated")

# Returns:
# - platform_overview_v1 → Use platform_overview_v3
# - security_old_v1 → Use security_compliance_overview_v2

# Agent warns or auto-upgrades manifest
```

## Indexer Implementation

### Script: `scripts/index_library.py`

```python
#!/usr/bin/env python3
"""
Content Library Indexer

Scans content_library/ and generates searchable index files in .index/
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

LIBRARY_ROOT = Path(__file__).parent.parent / "content_library"
INDEX_DIR = LIBRARY_ROOT / ".index"

def scan_library() -> List[Dict]:
    """Scan all section block JSON files"""
    blocks = []
    
    # Scan library/ and documents/
    for root_dir in ["library", "documents"]:
        scan_path = LIBRARY_ROOT / root_dir
        if not scan_path.exists():
            continue
            
        for json_file in scan_path.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    block = json.load(f)
                
                # Validate basic schema
                if 'metadata' not in block or 'content' not in block:
                    print(f"⚠️  Skipping {json_file}: missing metadata or content")
                    continue
                
                # Extract metadata for catalog
                meta = block['metadata']
                catalog_entry = {
                    'id': meta['id'],
                    'path': str(json_file.relative_to(LIBRARY_ROOT)),
                    'version': meta.get('version', '1.0'),
                    'title': meta['title'],
                    'description': meta.get('description', ''),
                    'category': meta.get('category', 'uncategorized'),
                    'subcategory': meta.get('subcategory', ''),
                    'tags': meta.get('tags', []),
                    'status': meta.get('status', 'draft'),
                    'author': meta.get('author', ''),
                    'created': meta.get('created', ''),
                    'last_updated': meta.get('last_updated', ''),
                    'usage_count': meta.get('usage_stats', {}).get('usage_count', 0),
                    'last_used': meta.get('usage_stats', {}).get('last_used', ''),
                    'variables_required': meta.get('variables', {}).get('required', []),
                    'variables_optional': meta.get('variables', {}).get('optional', []),
                    'dependencies': meta.get('dependencies', {}),
                    'compliance': meta.get('compliance', {}),
                    'file_size_kb': round(json_file.stat().st_size / 1024, 1)
                }
                
                blocks.append(catalog_entry)
                
            except Exception as e:
                print(f"❌ Error processing {json_file}: {e}")
    
    return blocks

def build_indexes(blocks: List[Dict]):
    """Build all index files"""
    INDEX_DIR.mkdir(exist_ok=True)
    
    # 1. Catalog (full block list)
    catalog = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0',
        'total_blocks': len(blocks),
        'blocks': blocks
    }
    with open(INDEX_DIR / 'catalog.json', 'w') as f:
        json.dump(catalog, f, indent=2)
    
    # 2. Tag index
    tags_index = {}
    for block in blocks:
        for tag in block['tags']:
            if tag not in tags_index:
                tags_index[tag] = []
            tags_index[tag].append(block['id'])
    with open(INDEX_DIR / 'tags.json', 'w') as f:
        json.dump(tags_index, f, indent=2)
    
    # 3. Category index
    categories_index = {}
    for block in blocks:
        cat = block['category']
        subcat = block['subcategory'] or 'general'
        
        if cat not in categories_index:
            categories_index[cat] = {}
        if subcat not in categories_index[cat]:
            categories_index[cat][subcat] = []
        
        categories_index[cat][subcat].append({
            'id': block['id'],
            'title': block['title'],
            'status': block['status']
        })
    with open(INDEX_DIR / 'categories.json', 'w') as f:
        json.dump(categories_index, f, indent=2)
    
    # 4. Usage analytics
    sorted_by_usage = sorted(blocks, key=lambda b: b['usage_count'], reverse=True)
    usage_stats = {
        'most_used': [
            {'id': b['id'], 'usage_count': b['usage_count'], 'last_used': b['last_used']}
            for b in sorted_by_usage[:20]
        ],
        'least_used': [
            {'id': b['id'], 'usage_count': b['usage_count'], 'last_used': b['last_used']}
            for b in sorted_by_usage[-20:]
        ],
        'never_used': [
            {'id': b['id'], 'usage_count': 0}
            for b in blocks if b['usage_count'] == 0
        ]
    }
    with open(INDEX_DIR / 'usage.json', 'w') as f:
        json.dump(usage_stats, f, indent=2)
    
    print(f"✅ Indexed {len(blocks)} content blocks")
    print(f"   📂 Categories: {len(categories_index)}")
    print(f"   🏷️  Tags: {len(tags_index)}")
    print(f"   📊 Most used: {sorted_by_usage[0]['id']} ({sorted_by_usage[0]['usage_count']} uses)")

if __name__ == '__main__':
    blocks = scan_library()
    build_indexes(blocks)
```

### Script: `scripts/search_library.py`

```python
#!/usr/bin/env python3
"""
Content Library Search Tool

Search and query the content library index
"""

import json
import argparse
from pathlib import Path

INDEX_DIR = Path(__file__).parent.parent / "content_library" / ".index"

def load_catalog():
    with open(INDEX_DIR / 'catalog.json', 'r') as f:
        return json.load(f)

def search(query: str = None, category: str = None, tags: List[str] = None, 
           status: str = "active", limit: int = 10):
    """Search blocks"""
    catalog = load_catalog()
    results = catalog['blocks']
    
    # Filter by status
    if status:
        results = [b for b in results if b['status'] == status]
    
    # Filter by category
    if category:
        results = [b for b in results if b['category'] == category]
    
    # Filter by tags
    if tags:
        results = [b for b in results if any(t in b['tags'] for t in tags)]
    
    # Full-text search
    if query:
        query_lower = query.lower()
        results = [
            b for b in results
            if query_lower in b['title'].lower() 
            or query_lower in b['description'].lower()
            or any(query_lower in tag for tag in b['tags'])
        ]
    
    # Sort by usage count (most used first)
    results = sorted(results, key=lambda b: b['usage_count'], reverse=True)
    
    return results[:limit]

def main():
    parser = argparse.ArgumentParser(description='Search content library')
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    parser.add_argument('--status', default='active', help='Filter by status')
    parser.add_argument('--limit', type=int, default=10, help='Max results')
    parser.add_argument('--most-used', action='store_true', help='Show most used blocks')
    
    args = parser.parse_args()
    
    if args.most_used:
        with open(INDEX_DIR / 'usage.json', 'r') as f:
            usage = json.load(f)
        print("📊 Most Used Content Blocks:\n")
        for i, block in enumerate(usage['most_used'][:args.limit], 1):
            print(f"{i}. {block['id']} ({block['usage_count']} uses)")
        return
    
    tags = args.tags.split(',') if args.tags else None
    results = search(args.query, args.category, tags, args.status, args.limit)
    
    if not results:
        print("No results found")
        return
    
    print(f"Found {len(results)} results:\n")
    for i, block in enumerate(results, 1):
        print(f"{i}. {block['id']}")
        print(f"   Title: {block['title']}")
        print(f"   Path: {block['path']}")
        print(f"   Category: {block['category']}/{block['subcategory']}")
        print(f"   Tags: {', '.join(block['tags'])}")
        print(f"   Used: {block['usage_count']} times")
        print()

if __name__ == '__main__':
    main()
```

## Integration with Compilation

When compiling a document from manifest:

1. **Load manifest** → `manifest.json`
2. **For each section**:
   - Read `source` path
   - Load section block JSON
   - **Update usage stats** in section block's `metadata.usage_stats`
   - Add `document_id` to `documents` array
3. **After compilation**:
   - Write updated section blocks back to library
   - **Regenerate index**: `python3 scripts/index_library.py`

This keeps usage statistics current automatically.

## Best Practices

### For Agents
- **Query before creating**: Check if reusable content exists before generating new
- **Prefer high-usage blocks**: More usage = more proven/refined content
- **Check variable requirements**: Ensure all required variables are available
- **Respect status**: Only use `active` blocks in production documents

### For Content Maintainers
- **Run indexer after changes**: `python3 scripts/index_library.py`
- **Review low-usage blocks**: Consider deprecating or improving
- **Monitor compliance dates**: Flag blocks needing review
- **Keep metadata accurate**: Tags and descriptions power discovery

### Performance
- **Index is cheap**: Regenerates in <1 second for 1000 blocks
- **Query is instant**: JSON file reads, no database needed
- **Scale**: Works fine up to 10,000+ blocks, then consider SQLite/PostgreSQL

## Future Enhancements

1. **Semantic search**: Embed descriptions with sentence transformers for similarity search
2. **Recommendation engine**: "Customers who used X also used Y"
3. **Version diffing**: Show what changed between `platform_overview_v2` and `v3`
4. **Auto-tagging**: ML model suggests tags based on content
5. **Quality metrics**: Track "satisfaction" score from document reviewers
6. **Dependency visualization**: Graph showing which blocks reference which images/sections
