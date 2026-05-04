# Document Manifest Schema

## Overview
The manifest defines document structure by referencing reusable content blocks from the library. It acts as a blueprint that the compiler assembles into a complete document.

## Manifest Format

```json
{
  "metadata": {
    "document_id": "airbus_rfp_2026_04",
    "document_title": "Airbus Helicopters RFP Response",
    "document_type": "solution",
    "customer": "Airbus Helicopters",
    "date": "2026-04-27",
    "version": "1.0",
    "author": "Solutions Engineering"
  },
  
  "variables": {
    "customer_name": "Airbus Helicopters",
    "deployment_type": "on-premises",
    "primary_use_case": "ETL/ELT modernization",
    "deployment_region": "Europe",
    "data_residency": "France",
    "compliance_requirements": ["SOC 2", "ISO 27001", "GDPR"],
    "custom_any_key": "any_value"
  },
  
  "branding": {
    "logo": "snaplogic-logo-white.png",
    "color_scheme": "default",
    "font_family": "helvetica"
  },
  
  "sections": [
    {
      "id": "title_page",
      "type": "title_page",
      "source": "library/standard/title_page.json",
      "required": true
    },
    {
      "id": "mgmt_summary",
      "type": "management_summary",
      "source": "documents/airbus_rfp/custom_mgmt_summary.json",
      "required": true
    },
    {
      "id": "platform_intro",
      "type": "section",
      "source": "library/platform/company_overview_v3.json",
      "required": true
    },
    {
      "id": "architecture",
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
      "source": "documents/airbus_rfp/custom_use_cases.json",
      "required": true
    },
    {
      "id": "connectors",
      "type": "section",
      "source": "library/platform/connector_ecosystem_v1.json",
      "required": false
    },
    {
      "id": "security",
      "type": "section",
      "source": "library/security/security_compliance_overview_v2.json",
      "required": true,
      "variables": {
        "certifications": ["SOC 2", "ISO 27001"],
        "focus_area": "data_sovereignty"
      }
    },
    {
      "id": "services",
      "type": "section",
      "source": "library/services/professional_services_v1.json",
      "required": false
    },
    {
      "id": "pricing",
      "type": "section",
      "source": "documents/airbus_rfp/custom_pricing.json",
      "required": false
    },
    {
      "id": "appendix_tech_specs",
      "type": "appendix",
      "source": "library/appendices/technical_specifications_v1.json",
      "required": false
    },
    {
      "id": "appendix_compliance",
      "type": "appendix",
      "source": "library/appendices/compliance_certifications_v1.json",
      "required": false
    }
  ],
  
  "table_of_contents": {
    "enabled": true,
    "depth": 3,
    "page_break_after": true
  },
  
  "list_of_tables": {
    "enabled": true,
    "page_break_after": true
  },
  
  "output_config": {
    "filename": "Airbus_Helicopters_RFP_Response.pdf",
    "page_numbers": true,
    "header_footer": true
  }
}
```

## Field Definitions

### metadata
- `document_id`: Unique identifier for this document
- `document_title`: Full title appearing on title page
- `document_type`: One of: `solution`, `proposal`, `technical`, `executive`, `report`
- `customer`: Customer/prospect name
- `date`: Document date (ISO 8601 format)
- `version`: Document version (semver recommended)
- `author`: Creator/team name

### variables
Key-value pairs injected into section content. Common patterns:
- `{{variable_name}}` replaced with value during compilation
- Available to all sections unless overridden
- Section-level variables in `sections[].variables` override global variables
- **No schema restriction**: Any key-value pairs allowed for flexibility

Common variables:
- `customer_name`, `deployment_type`, `primary_use_case`
- `deployment_region`, `data_residency`, `compliance_requirements`
- Custom variables as needed per document

### branding
- `logo`: Path to logo file (relative to working directory or absolute)
- `color_scheme`: `default`, `blue`, `navy` (maps to LaTeX color definitions)
- `font_family`: `helvetica` (default), `arial`, `times`

### sections[]
Ordered list defining document structure.

- `id`: Unique identifier within this manifest (used for cross-references)
- `type`: Section type
  - `title_page`: Cover page with branding
  - `management_summary`: Executive summary (unnumbered section)
  - `section`: Numbered section (Level 1)
  - `appendix`: Appendix section (lettered: A, B, C...)
- `source`: Path to section block JSON file
  - `library/*`: Reusable content library
  - `documents/*`: Document-specific custom content
- `required`: Boolean (for validation/checklist purposes)
- `variables`: Section-specific variable overrides (optional)

### table_of_contents, list_of_tables
Control auto-generated lists.
- `enabled`: Include this list
- `depth`: For TOC, how many heading levels (1-5)
- `page_break_after`: Insert page break after list

### output_config
- `filename`: Suggested output filename (compiler may override)
- `page_numbers`: Show page numbers in footer
- `header_footer`: Include headers/footers with company branding

## Validation Rules

1. **Required fields**: `metadata.document_title`, `metadata.document_type`, `sections`
2. **At least one section** with `type: "section"` or `type: "management_summary"`
3. **Source files must exist** at specified paths
4. **Section IDs must be unique** within manifest
5. **Variable references** in section content must have values in `variables` or section-level `variables`

## Cross-References

Use symbolic references that resolve at compile time:

- `[SECTION_REF:section_id]` → "Section 2.1"
- `[SECTION_TITLE:section_id]` → "SnapLogic Platform Architecture"
- `[APPENDIX_REF:appendix_id]` → "Appendix A"

Example:
```json
{
  "content": "As described in [SECTION_REF:architecture], the Ground Plex..."
}
```

Compiler resolves to:
```
As described in Section 2.1, the Ground Plex...
```

## Example: Minimal Manifest

```json
{
  "metadata": {
    "document_title": "Quick Proposal",
    "document_type": "proposal"
  },
  "variables": {
    "customer_name": "Acme Corp"
  },
  "sections": [
    {
      "id": "title",
      "type": "title_page",
      "source": "library/standard/title_page.json"
    },
    {
      "id": "overview",
      "type": "section",
      "source": "library/platform/company_overview_v3.json"
    }
  ]
}
```

## Example: Complex Multi-Section Manifest

```json
{
  "metadata": {
    "document_id": "enterprise_rfp_001",
    "document_title": "Enterprise Integration Platform Proposal",
    "document_type": "solution",
    "customer": "Global Manufacturing Inc",
    "date": "2026-04-27",
    "version": "2.1"
  },
  "variables": {
    "customer_name": "Global Manufacturing Inc",
    "deployment_type": "hybrid",
    "cloud_regions": ["AWS us-east-1", "Azure westeurope"],
    "on_prem_locations": ["Chicago DC", "Frankfurt DC"],
    "data_volume": "50TB/month",
    "transaction_volume": "100M/day"
  },
  "sections": [
    {
      "id": "title",
      "type": "title_page",
      "source": "library/standard/title_page.json"
    },
    {
      "id": "exec_summary",
      "type": "management_summary",
      "source": "documents/global_mfg/executive_summary.json"
    },
    {
      "id": "company",
      "type": "section",
      "source": "library/platform/company_overview_v3.json"
    },
    {
      "id": "arch_hybrid",
      "type": "section",
      "source": "library/platform/architecture_hybrid_v1.json",
      "variables": {
        "show_multi_plex_diagram": true
      }
    },
    {
      "id": "use_cases",
      "type": "section",
      "source": "documents/global_mfg/manufacturing_use_cases.json"
    },
    {
      "id": "security",
      "type": "section",
      "source": "library/security/security_compliance_overview_v2.json",
      "variables": {
        "certifications": ["SOC 2", "ISO 27001", "TISAX"]
      }
    },
    {
      "id": "appendix_certs",
      "type": "appendix",
      "source": "library/appendices/compliance_certifications_v1.json"
    }
  ]
}
```
