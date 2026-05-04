# Complete Document Generation Flow Example

## Overview

This document shows the complete end-to-end flow: Generation Request → Content Discovery → Manifest → Section Blocks → PDF

## Scenario

**Customer**: Airbus Helicopters  
**Document**: RFP Response for on-premises ETL/ELT platform  
**Requirements**: 114 total (98 mandatory, 16 optional)  
**Timeline**: 2 weeks  
**Complexity**: High (technical + business + pricing + requirements matrix)

---

## Step 1: Generation Request (INPUT)

**File**: `requests/airbus_rfp_2026_04.json`

```json
{
  "request_metadata": {
    "request_id": "airbus_rfp_2026_04",
    "request_type": "rfp_response",
    "created": "2026-04-27T10:00:00Z",
    "deadline": "2026-05-15T17:00:00Z",
    "priority": "high"
  },
  
  "document_spec": {
    "document_type": "solution",
    "title": "Airbus Helicopters RFP Response",
    "subtitle": "On-Premises ETL/ELT Platform Proposal",
    "page_target": "20-30",
    "tone": "professional",
    "technical_depth": "detailed"
  },
  
  "customer_context": {
    "name": "Airbus Helicopters",
    "industry": "Aerospace & Defense",
    "region": "Europe",
    "country": "France",
    
    "technical_environment": {
      "deployment_preference": "on-premises",
      "data_residency_requirements": ["France", "EU"],
      "compliance_requirements": ["SOC 2", "ISO 27001", "GDPR"],
      "existing_systems": ["SAP ECC", "Informatica PowerCenter", "Oracle DW"],
      "infrastructure": ["Red Hat OpenShift"],
      "data_volume": "50TB/month"
    },
    
    "business_context": {
      "primary_driver": "Informatica license renewal",
      "pain_points": [
        "High Informatica licensing costs",
        "Slow development with traditional ETL",
        "No modern API integration"
      ],
      "success_criteria": [
        "70% reduction in development time",
        "50% cost savings vs. Informatica"
      ]
    }
  },
  
  "requirements": {
    "total_requirements": 114,
    "mandatory_requirements": 98,
    "sections_required": [
      "management_summary",
      "company_overview",
      "platform_architecture",
      "use_cases",
      "migration_approach",
      "security_compliance",
      "professional_services",
      "pricing"
    ],
    
    "categories": [
      {
        "category": "Technical Capabilities",
        "requirement_count": 45,
        "key_requirements": [
          {
            "id": "REQ-001",
            "text": "Support on-premises deployment",
            "response_status": "met",
            "evidence": "Ground Plex provides fully on-premises data plane"
          }
        ]
      },
      {
        "category": "Security & Compliance",
        "requirement_count": 28
      }
    ]
  },
  
  "use_cases": [
    {
      "id": "uc_001",
      "title": "SAP to Data Warehouse ETL",
      "systems": ["SAP ECC", "Oracle DW"],
      "data_volume": "10M records/day",
      "current_solution": "Informatica PowerCenter"
    },
    {
      "id": "uc_002",
      "title": "PLM-MES Integration",
      "systems": ["Teamcenter PLM", "MES"],
      "frequency": "Near real-time"
    }
  ],
  
  "assets": {
    "images": [
      {
        "id": "arch_diagram",
        "path": "/assets/High_Level_Architecture.png",
        "usage": "Platform architecture section"
      }
    ]
  },
  
  "content_preferences": {
    "reuse_existing": true,
    "query_library_first": true,
    "variable_defaults": {
      "customer_name": "Airbus Helicopters",
      "deployment_type": "on-premises",
      "incumbent_vendor": "Informatica PowerCenter"
    },
    "custom_sections_needed": [
      "management_summary",
      "use_cases",
      "migration_approach"
    ]
  }
}
```

---

## Step 2: Agent Processes Request

### 2.1 Query Content Library

**Agent action**: Check what sections can be reused

```python
import json
from pathlib import Path

# Load request
with open('requests/airbus_rfp_2026_04.json') as f:
    request = json.load(f)

# Load content library index
with open('content_library/.index/catalog.json') as f:
    catalog = json.load(f)

# What sections does document need?
required_sections = request['requirements']['sections_required']
deployment = request['customer_context']['technical_environment']['deployment_preference']

# Query library for each section
reusable_sections = {}
for section_type in required_sections:
    # Search by section type + deployment compatibility
    matches = [
        b for b in catalog['blocks']
        if section_type in b['tags']
        and b['status'] == 'active'
        and (deployment in b.get('tags', []) or 'reusable' in b['tags'])
    ]
    
    if matches:
        # Use most popular (highest usage_count)
        best_match = sorted(matches, key=lambda x: x['usage_count'], reverse=True)[0]
        reusable_sections[section_type] = best_match['id']
        print(f"✓ {section_type}: Reuse {best_match['id']} ({best_match['usage_count']} uses)")
    else:
        print(f"✗ {section_type}: Must generate custom")
```

**Output**:
```
✓ company_overview: Reuse company_overview_v3 (89 uses)
✓ platform_architecture: Reuse architecture_ground_plex_v2 (47 uses)
✓ security_compliance: Reuse security_compliance_overview_v2 (92 uses)
✓ professional_services: Reuse services_standard_v1 (34 uses)
✗ management_summary: Must generate custom
✗ use_cases: Must generate custom
✗ migration_approach: Must generate custom
✗ pricing: Must generate custom
```

**Result**: Can reuse 4/8 sections (50% reuse rate)

### 2.2 Generate Custom Sections

**Agent generates 4 custom sections in parallel**:

#### Custom Section 1: Management Summary

**File**: `content_library/documents/airbus_rfp/management_summary.json`

```json
{
  "metadata": {
    "id": "airbus_mgmt_summary",
    "version": "1.0",
    "title": "Executive Summary",
    "category": "custom",
    "tags": ["airbus", "executive", "rfp_response"],
    "status": "active",
    "created": "2026-04-27",
    "variables": {
      "required": ["customer_name"],
      "optional": []
    }
  },
  "content": {
    "title": "Executive Summary",
    "content": "SnapLogic proposes an on-premises ETL/ELT platform for {{customer_name}} that addresses all 114 requirements outlined in your RFP.\n\n**Why SnapLogic:**\n\n- **Proven Informatica Alternative**: 50+ customers have successfully migrated from Informatica to SnapLogic, achieving 50-70% cost savings\n- **On-Premises Data Sovereignty**: Ground Plex architecture ensures all data processing occurs within your French data centers\n- **Rapid Time-to-Value**: Low-code development reduces pipeline creation time by 70% vs. traditional ETL\n- **Modern Architecture**: API-first, containerized on OpenShift, scales horizontally\n\n**Requirements Coverage**: 114/114 requirements met (98 mandatory + 16 optional)\n\n**Implementation Timeline**: 12 weeks from contract signature to production cutover\n\n**Investment**: €650K total (platform licensing + professional services) — 50% savings vs. Informatica renewal",
    "subsections": []
  }
}
```

#### Custom Section 2: Use Cases

**File**: `content_library/documents/airbus_rfp/use_cases.json`

```json
{
  "metadata": {
    "id": "airbus_use_cases",
    "version": "1.0",
    "title": "Use Cases for Airbus Helicopters",
    "category": "use_cases",
    "tags": ["airbus", "manufacturing", "aerospace", "use_cases"],
    "status": "active"
  },
  "content": {
    "title": "Use Cases",
    "content": "The following use cases address {{customer_name}}'s specific integration requirements:",
    "subsections": [
      {
        "title": "SAP to Data Warehouse ETL",
        "content": "**Objective**: Extract manufacturing data from SAP ECC, transform for analytics, load to Oracle Data Warehouse.\n\n**Current Solution**: Informatica PowerCenter — 15 mappings, batch-only processing, 24-hour latency\n\n**SnapLogic Solution**: Real-time CDC from SAP using SAP Snap Pack, in-memory transformations, streaming load to Oracle\n\n**Volume**: 10M records/day\n\n**Benefits**:\n- Real-time analytics (vs. 24hr batch)\n- 80% faster pipeline development\n- Self-service for business analysts\n\n**Migration Effort**: 2 weeks (automated conversion from Informatica mappings)"
      },
      {
        "title": "PLM-MES Integration",
        "content": "**Objective**: Bi-directional sync between Teamcenter PLM and MES systems for work instructions and quality records.\n\n**Current Solution**: Custom Java middleware — brittle, high maintenance, no retry logic\n\n**SnapLogic Solution**: REST API-based integration with built-in error handling, retry policies, and monitoring\n\n**Frequency**: Near real-time (5min intervals)\n\n**Benefits**:\n- Eliminate custom code maintenance\n- Robust error handling\n- Real-time operational visibility\n\n**Migration Effort**: 3 weeks"
      }
    ]
  }
}
```

#### Custom Section 3 & 4: Migration + Pricing

*(Similar structure, omitted for brevity)*

### 2.3 Build Manifest

**File**: `content_library/documents/airbus_rfp/manifest.json`

```json
{
  "metadata": {
    "document_id": "airbus_rfp_2026_04",
    "document_title": "Airbus Helicopters RFP Response",
    "document_type": "solution",
    "customer": "Airbus Helicopters",
    "date": "2026-04-27",
    "version": "1.0"
  },
  
  "variables": {
    "customer_name": "Airbus Helicopters",
    "deployment_type": "on-premises",
    "primary_use_case": "ETL/ELT modernization",
    "incumbent_vendor": "Informatica PowerCenter",
    "data_residency": "France",
    "compliance_requirements": ["SOC 2", "ISO 27001", "GDPR"]
  },
  
  "branding": {
    "logo": "snaplogic-logo-white.png",
    "color_scheme": "default"
  },
  
  "sections": [
    {
      "id": "title",
      "type": "title_page",
      "source": "library/standard/title_page.json",
      "required": true
    },
    {
      "id": "mgmt_summary",
      "type": "management_summary",
      "source": "documents/airbus_rfp/management_summary.json",
      "required": true
    },
    {
      "id": "company_overview",
      "type": "section",
      "source": "library/platform/company_overview_v3.json",
      "required": true
    },
    {
      "id": "platform_architecture",
      "type": "section",
      "source": "library/platform/architecture_ground_plex_v2.json",
      "required": true,
      "variables": {
        "focus": "on_premises_security",
        "show_cloud_control_plane": true
      }
    },
    {
      "id": "use_cases",
      "type": "section",
      "source": "documents/airbus_rfp/use_cases.json",
      "required": true
    },
    {
      "id": "migration",
      "type": "section",
      "source": "documents/airbus_rfp/migration_approach.json",
      "required": true
    },
    {
      "id": "security",
      "type": "section",
      "source": "library/security/security_compliance_overview_v2.json",
      "required": true,
      "variables": {
        "certifications": ["SOC 2", "ISO 27001", "GDPR"]
      }
    },
    {
      "id": "services",
      "type": "section",
      "source": "library/services/professional_services_standard_v1.json",
      "required": true
    },
    {
      "id": "pricing",
      "type": "section",
      "source": "documents/airbus_rfp/pricing.json",
      "required": true
    }
  ],
  
  "table_of_contents": {
    "enabled": true,
    "depth": 3
  },
  
  "list_of_tables": {
    "enabled": true
  }
}
```

---

## Step 3: Compilation

### 3.1 Compile Command

```bash
python3 scripts/compile_document.py \
  content_library/documents/airbus_rfp/manifest.json \
  output/Airbus_RFP_Response.pdf \
  solution
```

### 3.2 Compilation Process

**Internal steps**:

1. **Load manifest** → Parse `manifest.json`
2. **Load all section blocks** → Read each `source` file
3. **Variable substitution** → Replace `{{customer_name}}` etc. with values
4. **Merge sections** → Assemble into single document structure
5. **Resolve cross-references** → `[SECTION_REF:platform_architecture]` → "Section 2.1"
6. **Generate LaTeX** → Convert JSON to LaTeX markup
7. **Copy assets** → Copy images to temp directory
8. **Compile PDF** → Run pdflatex
9. **Return result** → Output path + metadata

### 3.3 Compilation Output

```json
{
  "status": "success",
  "output_path": "/output/Airbus_RFP_Response.pdf",
  "pages": 24,
  "version": "1.0",
  "sections": 9,
  "images": 2,
  "tables": 5,
  "compilation_time": "3.2s",
  "content_reuse": {
    "library_sections": 4,
    "custom_sections": 5,
    "reuse_percentage": 44
  }
}
```

---

## Step 4: Update Usage Statistics

After successful compilation, update usage stats in library blocks:

```python
# For each library section used in manifest
for section in manifest['sections']:
    if section['source'].startswith('library/'):
        section_path = f"content_library/{section['source']}"
        
        # Load section block
        with open(section_path) as f:
            block = json.load(f)
        
        # Update usage stats
        block['metadata']['usage_stats']['usage_count'] += 1
        block['metadata']['usage_stats']['last_used'] = datetime.now().isoformat()
        block['metadata']['usage_stats']['documents'].append(manifest['metadata']['document_id'])
        
        # Write back
        with open(section_path, 'w') as f:
            json.dump(block, f, indent=2)

# Regenerate index
subprocess.run(['python3', 'scripts/index_library.py'])
```

**Result**:
- `company_overview_v3.json`: `usage_count` 89 → 90
- `architecture_ground_plex_v2.json`: `usage_count` 47 → 48
- `security_compliance_overview_v2.json`: `usage_count` 92 → 93
- `professional_services_standard_v1.json`: `usage_count` 34 → 35

---

## Final Output

### Generated Files

```
output/
├── Airbus_RFP_Response.pdf           # 24 pages, main deliverable
└── metadata.json                     # Compilation metadata
```

### Document Structure

**PDF Table of Contents**:
```
Executive Summary .................................................. 2

1. SnapLogic Company Overview ...................................... 3
   1.1 Company History ............................................. 3
   1.2 Customer Base ............................................... 4

2. Platform Architecture ........................................... 5
   2.1 High-Level Architecture ..................................... 5
   2.2 Ground Plex — On-Premises Data Plane ........................ 7
   2.3 SnapLogic Manager — Control Plane ........................... 9

3. Use Cases for Airbus Helicopters ................................ 11
   3.1 SAP to Data Warehouse ETL ................................... 11
   3.2 PLM-MES Integration ......................................... 13

4. Migration Approach .............................................. 15
   4.1 Migration Methodology ....................................... 15
   4.2 Informatica Conversion Process .............................. 16
   4.3 Timeline & Milestones ....................................... 17

5. Security & Compliance ........................................... 18
   5.1 Data Protection ............................................. 18
   5.2 Certifications .............................................. 19

6. Professional Services ........................................... 21
   6.1 Implementation Services ..................................... 21
   6.2 Training & Enablement ....................................... 22

7. Investment & Pricing ............................................ 23
```

### Statistics

- **Total Sections**: 9 (1 title page, 1 mgmt summary, 7 numbered sections)
- **Reusable Content**: 4 sections (44% reuse)
- **Custom Content**: 5 sections (56% custom)
- **Images**: 2 diagrams
- **Tables**: 5 tables
- **Pages**: 24 pages
- **Generation Time**: 5 minutes (4 agents in parallel + 1min compilation)
- **Traditional Time**: ~15 minutes (sequential, recreating standard sections)

---

## Comparison: Old vs. New Approach

### Old Monolithic Approach

**Process**:
```
Agent → Generate full 24-page JSON → Compile → PDF
```

**Challenges**:
- ❌ Agent regenerates "Platform Overview" from scratch (seen it 89 times before)
- ❌ Inconsistent: "Platform Overview" wording varies between documents
- ❌ Large context: Agent holds entire 24-page document in memory
- ❌ Sequential: Must finish entire document before compiling
- ❌ No reuse: Next RFP starts from zero again

**Time**: 15 minutes

### New Modular Approach

**Process**:
```
Agent 1 → Query library → Find 4 reusable sections
Agent 2 → Generate mgmt summary           }
Agent 3 → Generate use cases               } In parallel
Agent 4 → Generate migration approach      }
Agent 5 → Generate pricing                 }
Agent 6 → Build manifest → Compile → PDF
```

**Benefits**:
- ✅ Reuses 4/9 sections (44% reuse)
- ✅ Consistent: "Platform Overview" identical across all documents
- ✅ Small contexts: Each agent works on 2-3 pages max
- ✅ Parallel: 4 agents generate custom sections simultaneously
- ✅ Library grows: Next RFP can reuse "Migration Approach" if made generic

**Time**: 5 minutes (70% faster)

---

## Key Takeaways

### For Content Reuse
- **44% reuse rate** on first document in new system
- As library grows, reuse rate increases (target: 60-80% for standard RFPs)
- High-quality sections (like "Security Overview" with 92 uses) are battle-tested

### For Consistency
- "Platform Architecture" section identical in all documents using `architecture_ground_plex_v2`
- Updates to library blocks automatically affect all future documents
- No more "wait, why does this RFP say X but that one says Y?"

### For Speed
- **3x faster** generation (5min vs 15min)
- Scales better: Adding more agents increases parallelism
- Compilation time constant (~1min) regardless of doc size

### For Quality
- Popular sections (high usage_count) are refined over time
- Legal/compliance review at block level, not document level
- Easier to maintain: Update one section vs. find-and-replace across 50 documents

---

## Next Steps

1. **Implement compiler support** for manifest format
2. **Build initial content library** with 20 standard sections
3. **Create indexer scripts** for content discovery
4. **Train agents** on new workflow
5. **Migrate existing content** to library structure
