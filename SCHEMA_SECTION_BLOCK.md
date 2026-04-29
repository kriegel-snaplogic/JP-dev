# Section Block Schema

## Overview
Section blocks are reusable content units stored in the content library. Each block is a self-contained JSON file with metadata and content that can be referenced by multiple document manifests.

## Section Block Format

```json
{
  "metadata": {
    "id": "platform_overview_v3",
    "version": "3.0",
    "title": "SnapLogic Platform Overview",
    "description": "Comprehensive overview of SnapLogic's enterprise integration platform including architecture, capabilities, and differentiators",
    "created": "2024-01-15",
    "last_updated": "2026-04-20",
    "author": "Solutions Engineering",
    "maintainer": "solutions-team@snaplogic.com",
    "status": "active",
    "
    "tags": ["platform", "architecture", "overview", "reusable", "standard"],
    "category": "platform",
    "subcategory": "overview",
    
    "usage_stats": {
      "usage_count": 47,
      "last_used": "2026-04-27",
      "documents": [
        "airbus_rfp_2026_04",
        "boeing_proposal_2026_03",
        "rolls_royce_poc_2026_04"
      ]
    },
    
    "variables": {
      "required": ["customer_name", "deployment_type"],
      "optional": ["focus", "show_pricing", "include_competitor_comparison"],
      "defaults": {
        "focus": "general",
        "show_pricing": false,
        "include_competitor_comparison": false
      }
    },
    
    "dependencies": {
      "images": [
        "High_Level_Architecture.png",
        "Ground_Plex_Architecture.png"
      ],
      "sections": [],
      "external_resources": []
    },
    
    "compliance": {
      "review_required": false,
      "legal_approved": true,
      "last_review_date": "2026-04-01",
      "next_review_date": "2026-07-01"
    }
  },
  
  "content": {
    "title": "SnapLogic Platform Overview",
    "content": "SnapLogic is an enterprise integration platform purpose-built for connecting applications, databases, APIs, and data streams across complex, hybrid environments. Founded in 2006 by Gaurav Dhillon — who previously co-founded Informatica — SnapLogic combines deep enterprise integration heritage with a modern, AI-augmented, low-code design philosophy.\n\nThe platform is in production at 500+ enterprise customers, processing over 5 billion documents per month. SnapLogic holds SOC 2 Type II certification, is recognised in 11 consecutive Gartner Magic Quadrant reports for iPaaS, and has been named a Leader in the Forrester Wave for iPaaS (Q3 2025).",
    
    "subsections": [
      {
        "title": "High-Level Architecture",
        "content": "SnapLogic's architecture separates the control plane (cloud-hosted) from the data plane ({{deployment_type}}). All pipeline execution, data movement, and transformation occur in the data plane — within {{customer_name}}'s own infrastructure.\n\n[IMAGE:images/High_Level_Architecture.png:SnapLogic Deployment Architecture]\n\nCore architectural components..."
      },
      {
        "title": "Ground Plex — On-Premises Data Plane",
        "content": "The Ground Plex is SnapLogic's containerised data plane engine...",
        "subsubsections": [
          {
            "title": "Container Architecture",
            "content": "Deployed as Docker containers on OpenShift/Kubernetes..."
          }
        ]
      }
    ]
  }
}
```

## Field Definitions

### metadata

#### Core Identity
- `id`: Unique identifier (kebab-case, versioned: `platform_overview_v3`)
- `version`: Semantic version of this content block
- `title`: Human-readable title
- `description`: Brief description of content and purpose (for discovery)
- `created`: ISO 8601 date when first created
- `last_updated`: ISO 8601 date of last modification
- `author`: Original creator
- `maintainer`: Current owner/team email
- `status`: Lifecycle status
  - `draft`: Work in progress, not for production use
  - `active`: Production-ready, current version
  - `deprecated`: Older version, use newer version instead
  - `archived`: Historical, do not use

#### Classification
- `tags`: Array of keywords for discovery
  - Examples: `["platform", "architecture", "security", "compliance", "reusable", "standard", "template"]`
- `category`: Primary category
  - Examples: `platform`, `security`, `services`, `appendices`, `use_cases`, `pricing`
- `subcategory`: Secondary classification within category
  - Examples: `overview`, `architecture`, `compliance`, `technical_specs`

#### Usage Tracking
- `usage_stats.usage_count`: Number of times referenced by documents
- `usage_stats.last_used`: ISO 8601 date last compiled
- `usage_stats.documents`: Array of document IDs that reference this block

#### Variable Requirements
- `variables.required`: Array of variable names that MUST be provided
- `variables.optional`: Array of optional variable names
- `variables.defaults`: Default values for optional variables

#### Dependencies
- `dependencies.images`: Image files referenced in content (for asset management)
- `dependencies.sections`: Other section blocks this references (for cross-refs)
- `dependencies.external_resources`: External files/resources needed

#### Compliance & Governance
- `compliance.review_required`: Boolean, requires legal/compliance review before use
- `compliance.legal_approved`: Boolean, approved for customer-facing docs
- `compliance.last_review_date`: ISO 8601 date
- `compliance.next_review_date`: ISO 8601 date

### content

Standard document content structure (same as previous monolithic format):

- `title`: Section title
- `content`: Main content with markdown-style formatting
- `subsections[]`: Array of nested subsections
  - `title`: Subsection title
  - `content`: Subsection content
  - `subsubsections[]`: Further nesting
    - `title`: Subsubsection title
    - `content`: Subsubsection content

**Content Formatting**: Same as monolithic format
- Markdown-style: `**bold**`, `*italic*`, inline code
- Special tags: `[IMAGE:path:caption:width]`, `[TABLE:style:caption]`, `[BOX:type]`, etc.
- Variable substitution: `{{variable_name}}`

## Section Types

### title_page
Cover page content. Typically minimal metadata.

```json
{
  "metadata": {
    "id": "standard_title_page_v1",
    "version": "1.0",
    "title": "Standard Title Page",
    "category": "standard",
    "tags": ["title", "cover", "standard"]
  },
  "content": {
    "title": "{{document_title}}",
    "content": "Prepared for: {{customer_name}}\n\nDate: {{date}}\n\nVersion: {{version}}"
  }
}
```

### management_summary
Executive summary or management overview. Usually custom per document but can have template.

```json
{
  "metadata": {
    "id": "mgmt_summary_template_v1",
    "version": "1.0",
    "title": "Management Summary Template",
    "category": "standard",
    "tags": ["template", "executive", "summary"]
  },
  "content": {
    "title": "Management Summary",
    "content": "[Brief executive overview for {{customer_name}}]\n\n**Key Points:**\n- Point 1\n- Point 2\n- Point 3"
  }
}
```

### section (standard numbered section)
Main content sections. Highly reusable.

Example: Platform overview, architecture, security, use cases, services

### appendix
Supplementary material (lettered: A, B, C...)

Example: Technical specifications, compliance certificates, glossary

## Variable Substitution

Variables injected at compile time:

**Global variables** (from manifest):
```json
"variables": {
  "customer_name": "Acme Corp",
  "deployment_type": "hybrid"
}
```

**Section-level overrides** (from manifest section config):
```json
{
  "id": "architecture",
  "source": "library/platform/architecture_v2.json",
  "variables": {
    "focus": "on_premises_security"
  }
}
```

**Content usage**:
```
The {{deployment_type}} architecture serves {{customer_name}}'s requirements...
```

**Resolution order**: Section variables → Global variables → Section defaults → Error if missing required variable

## Validation Rules

1. **Required metadata fields**: `id`, `version`, `title`, `status`, `category`
2. **ID format**: Lowercase, underscores/hyphens, version suffix: `platform_overview_v3`
3. **Status values**: Must be one of: `draft`, `active`, `deprecated`, `archived`
4. **Content structure**: Must have `content.title` and `content.content`
5. **Variable references**: All `{{variable}}` tags must be declared in `metadata.variables.required` or `optional`
6. **Dependencies**: All referenced images/sections must be listed in `metadata.dependencies`

## Best Practices

### Versioning
- **Semantic versioning**: Major version for breaking changes, minor for additions
- **Keep old versions**: Don't delete `platform_overview_v2.json`, documents may reference it
- **Deprecation path**: Mark old versions `"status": "deprecated"` with pointer to new version

### Modularity
- **One topic per block**: "Platform Architecture" ≠ "Platform Architecture + Security + Pricing"
- **Reasonable size**: 1-3 pages typical, 5 pages max
- **Standalone**: Should make sense if read in isolation

### Reusability
- **Generic language**: "The customer" not "Boeing"
- **Variable-driven**: `{{customer_name}}` not hardcoded names
- **Conditional content**: Use variables for optional sections
  ```
  {{#if show_pricing}}
  Pricing details...
  {{/if}}
  ```

### Maintenance
- **Review cycle**: Update `next_review_date`, check quarterly
- **Usage tracking**: Monitor which blocks are popular vs. dead
- **Deprecation notices**: Add migration guide when deprecating

## Example: Reusable Security Section

```json
{
  "metadata": {
    "id": "security_compliance_overview_v2",
    "version": "2.0",
    "title": "Security & Compliance Overview",
    "description": "Standard security and compliance section covering SOC 2, ISO 27001, GDPR, data residency, encryption, and access control",
    "created": "2024-06-01",
    "last_updated": "2026-03-15",
    "author": "Security Team",
    "maintainer": "security-docs@snaplogic.com",
    "status": "active",
    "tags": ["security", "compliance", "soc2", "iso27001", "gdpr", "reusable"],
    "category": "security",
    "subcategory": "compliance",
    "usage_stats": {
      "usage_count": 89,
      "last_used": "2026-04-27"
    },
    "variables": {
      "required": ["customer_name"],
      "optional": ["certifications", "focus_area", "data_residency"],
      "defaults": {
        "certifications": ["SOC 2", "ISO 27001"],
        "focus_area": "general",
        "data_residency": "global"
      }
    },
    "dependencies": {
      "images": ["Security_Architecture.png"],
      "sections": [],
      "external_resources": []
    },
    "compliance": {
      "review_required": true,
      "legal_approved": true,
      "last_review_date": "2026-03-01",
      "next_review_date": "2026-06-01"
    }
  },
  "content": {
    "title": "Security & Compliance",
    "content": "SnapLogic maintains enterprise-grade security controls to protect {{customer_name}}'s data and meet regulatory requirements in {{data_residency}} regions.\n\n**Certifications**: {{certifications}}\n\n[IMAGE:images/Security_Architecture.png:SnapLogic Security Architecture]",
    "subsections": [
      {
        "title": "Data Protection",
        "content": "All data is encrypted at rest (AES-256) and in transit (TLS 1.3)..."
      },
      {
        "title": "Access Control",
        "content": "Role-based access control (RBAC), SSO, MFA..."
      },
      {
        "title": "Compliance Certifications",
        "content": "SnapLogic holds the following certifications relevant to {{customer_name}}:\n\n[TABLE:simple:Security Certifications]..."
      }
    ]
  }
}
```

## Example: Custom Document-Specific Section

```json
{
  "metadata": {
    "id": "airbus_custom_use_cases",
    "version": "1.0",
    "title": "Airbus Helicopters Use Cases",
    "description": "Customer-specific use cases for Airbus Helicopters RFP response",
    "created": "2026-04-25",
    "last_updated": "2026-04-27",
    "author": "SE Team - EMEA",
    "maintainer": "emea-se@snaplogic.com",
    "status": "active",
    "tags": ["custom", "airbus", "use_cases", "manufacturing", "aerospace"],
    "category": "use_cases",
    "subcategory": "manufacturing",
    "usage_stats": {
      "usage_count": 1,
      "documents": ["airbus_rfp_2026_04"]
    },
    "variables": {
      "required": ["customer_name"],
      "optional": [],
      "defaults": {}
    },
    "dependencies": {
      "images": [],
      "sections": [],
      "external_resources": []
    },
    "compliance": {
      "review_required": false,
      "legal_approved": false,
      "last_review_date": "2026-04-27",
      "next_review_date": null
    }
  },
  "content": {
    "title": "Use Cases for {{customer_name}}",
    "content": "The following use cases address {{customer_name}}'s specific integration requirements for ETL/ELT modernization...",
    "subsections": [
      {
        "title": "SAP to Data Warehouse ETL",
        "content": "Extract manufacturing data from SAP ECC..."
      },
      {
        "title": "PLM System Integration",
        "content": "Bi-directional sync between Teamcenter PLM and MES..."
      }
    ]
  }
}
```
