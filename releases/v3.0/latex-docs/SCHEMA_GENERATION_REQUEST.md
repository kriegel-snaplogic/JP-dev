# Document Generation Request Schema

## Overview

This schema defines how agents receive structured input for document generation. The request format provides all context, requirements, and constraints needed to build a complete document.

## Request Format

```json
{
  "request_metadata": {
    "request_id": "airbus_rfp_2026_04_req",
    "request_type": "rfp_response",
    "created": "2026-04-27T10:00:00Z",
    "deadline": "2026-05-15T17:00:00Z",
    "priority": "high",
    "requestor": "emea-sales@snaplogic.com"
  },
  
  "document_spec": {
    "document_type": "solution",
    "title": "Airbus Helicopters RFP Response",
    "subtitle": "On-Premises ETL/ELT Platform Proposal",
    "output_filename": "Airbus_RFP_Response.pdf",
    "page_target": "20-30",
    "tone": "professional",
    "technical_depth": "detailed"
  },
  
  "customer_context": {
    "name": "Airbus Helicopters",
    "industry": "Aerospace & Defense",
    "industry_tags": ["manufacturing", "aerospace", "defense"],
    "size": "Enterprise",
    "region": "Europe",
    "country": "France",
    "headquarters": "Marignane, France",
    
    "technical_environment": {
      "deployment_preference": "on-premises",
      "data_residency_requirements": ["France", "EU"],
      "compliance_requirements": ["SOC 2", "ISO 27001", "GDPR", "ITAR"],
      "existing_systems": ["SAP ECC", "Informatica PowerCenter 10.2", "Oracle Data Warehouse", "Teamcenter PLM"],
      "infrastructure": ["VMware vSphere", "Red Hat OpenShift"],
      "data_volume": "50TB/month",
      "transaction_volume": "100M records/day"
    },
    
    "business_context": {
      "primary_driver": "Informatica license renewal - seeking modern alternative",
      "pain_points": [
        "High Informatica licensing costs",
        "Slow development cycles with traditional ETL",
        "Lack of modern API integration capabilities",
        "Limited self-service for business analysts"
      ],
      "success_criteria": [
        "70% reduction in development time",
        "50% cost savings vs. Informatica renewal",
        "Self-service capability for business users",
        "Modern API-first architecture"
      ],
      "budget": "€500K-800K",
      "timeline": "Q3 2026 implementation"
    },
    
    "stakeholders": [
      {
        "name": "Jean-Pierre Dubois",
        "role": "VP IT Infrastructure",
        "influence": "decision_maker",
        "concerns": ["data sovereignty", "security", "stability"]
      },
      {
        "name": "Marie Laurent",
        "role": "Director of Data Engineering",
        "influence": "technical_buyer",
        "concerns": ["ease of use", "migration effort", "skill requirements"]
      }
    ]
  },
  
  "requirements": {
    "source": "RFP Document",
    "source_file": "/path/to/airbus_rfp.xlsx",
    "total_requirements": 114,
    "mandatory_requirements": 98,
    "optional_requirements": 16,
    
    "categories": [
      {
        "category": "Technical Capabilities",
        "requirement_count": 45,
        "key_requirements": [
          {
            "id": "REQ-001",
            "text": "Support on-premises deployment with no cloud data transit",
            "priority": "mandatory",
            "response_status": "met",
            "evidence": "Ground Plex architecture provides fully on-premises data plane"
          },
          {
            "id": "REQ-002",
            "text": "Connect to SAP ECC for real-time data extraction",
            "priority": "mandatory",
            "response_status": "met",
            "evidence": "SAP Snap Pack with 50+ pre-built snaps"
          },
          {
            "id": "REQ-003",
            "text": "Process 100M records/day with sub-second latency",
            "priority": "mandatory",
            "response_status": "met",
            "evidence": "Ground Plex scales to 500M+ documents/day in production"
          }
        ]
      },
      {
        "category": "Security & Compliance",
        "requirement_count": 28,
        "key_requirements": [
          {
            "id": "REQ-045",
            "text": "SOC 2 Type II certification",
            "priority": "mandatory",
            "response_status": "met",
            "evidence": "Current SOC 2 Type II certified"
          },
          {
            "id": "REQ-046",
            "text": "Data encryption at rest (AES-256) and in transit (TLS 1.3)",
            "priority": "mandatory",
            "response_status": "met",
            "evidence": "AES-256 at rest, TLS 1.3 in transit, configurable per environment"
          }
        ]
      },
      {
        "category": "Services & Support",
        "requirement_count": 22,
        "key_requirements": [
          {
            "id": "REQ-087",
            "text": "Professional services for migration from Informatica",
            "priority": "mandatory",
            "response_status": "met",
            "evidence": "Dedicated migration methodology, 50+ Informatica migration projects completed"
          }
        ]
      },
      {
        "category": "Pricing & Licensing",
        "requirement_count": 19,
        "key_requirements": [
          {
            "id": "REQ-105",
            "text": "Perpetual licensing option available",
            "priority": "optional",
            "response_status": "met",
            "evidence": "Both subscription and perpetual licensing available"
          }
        ]
      }
    ],
    
    "sections_required": [
      "management_summary",
      "company_overview",
      "platform_architecture",
      "technical_capabilities",
      "use_cases",
      "migration_approach",
      "security_compliance",
      "professional_services",
      "pricing",
      "requirements_matrix"
    ]
  },
  
  "use_cases": [
    {
      "id": "uc_001",
      "title": "SAP to Data Warehouse ETL",
      "description": "Extract manufacturing data from SAP ECC, transform, load to Oracle DW",
      "systems": ["SAP ECC", "Oracle Data Warehouse"],
      "data_volume": "10M records/day",
      "frequency": "Real-time (CDC)",
      "business_value": "Real-time manufacturing analytics",
      "current_solution": "Informatica PowerCenter",
      "pain_points": ["Batch-only, 24hr latency", "Complex mapping maintenance"]
    },
    {
      "id": "uc_002",
      "title": "PLM-MES Integration",
      "description": "Bi-directional sync between Teamcenter PLM and MES systems",
      "systems": ["Teamcenter PLM", "MES"],
      "data_volume": "500K records/day",
      "frequency": "Near real-time (5min)",
      "business_value": "Synchronized work instructions and quality records",
      "current_solution": "Custom Java middleware",
      "pain_points": ["High maintenance cost", "Brittle error handling", "No retry logic"]
    },
    {
      "id": "uc_003",
      "title": "Supplier Portal API Integration",
      "description": "REST API integration with 200+ supplier portals for order status",
      "systems": ["Supplier APIs", "SAP MM"],
      "data_volume": "5K API calls/day",
      "frequency": "Hourly",
      "business_value": "Automated supplier order tracking",
      "current_solution": "None - manual process",
      "pain_points": ["No current automation", "Manual data entry"]
    }
  ],
  
  "assets": {
    "images": [
      {
        "id": "arch_diagram",
        "path": "/Users/konstantinriegel/Desktop/High_Level_Architecture.png",
        "description": "SnapLogic deployment architecture diagram",
        "usage": "Platform architecture section",
        "width": "1.0"
      },
      {
        "id": "use_case_flow",
        "path": "/Users/konstantinriegel/Desktop/SAP_Integration_Flow.png",
        "description": "SAP integration data flow",
        "usage": "Use cases section",
        "width": "0.8"
      }
    ],
    
    "data_files": [
      {
        "id": "requirements_matrix",
        "path": "/Users/konstantinriegel/Desktop/airbus_requirements.xlsx",
        "type": "excel",
        "description": "Full requirements matrix with 114 requirements",
        "usage": "Generate requirements response table"
      },
      {
        "id": "competitor_analysis",
        "path": "/Users/konstantinriegel/Desktop/informatica_comparison.json",
        "type": "json",
        "description": "Feature comparison: SnapLogic vs. Informatica",
        "usage": "Competitive positioning"
      }
    ],
    
    "reference_documents": [
      {
        "id": "security_whitepaper",
        "path": "/library/whitepapers/security_architecture.pdf",
        "description": "SnapLogic security architecture whitepaper",
        "usage": "Security section reference"
      }
    ]
  },
  
  "content_preferences": {
    "reuse_existing": true,
    "query_library_first": true,
    "preferred_sections": [
      "library/platform/platform_overview_v3",
      "library/security/security_compliance_overview_v2"
    ],
    "exclude_sections": [
      "library/platform/cloud_only_architecture_v1"
    ],
    "variable_defaults": {
      "customer_name": "Airbus Helicopters",
      "deployment_type": "on-premises",
      "primary_use_case": "ETL/ELT modernization",
      "incumbent_vendor": "Informatica PowerCenter"
    },
    "custom_sections_needed": [
      "management_summary",
      "use_cases",
      "migration_approach",
      "requirements_matrix"
    ]
  },
  
  "constraints": {
    "page_limit": 30,
    "language": "English",
    "formatting_requirements": [
      "Include table of contents",
      "Include list of tables",
      "Number all sections",
      "Include page numbers"
    ],
    "legal_review_required": true,
    "approval_chain": ["SE Lead", "Legal", "Sales Director"]
  },
  
  "output_requirements": {
    "formats": ["pdf", "docx"],
    "deliverables": [
      {
        "type": "pdf",
        "path": "/output/Airbus_RFP_Response.pdf",
        "description": "Main proposal document"
      },
      {
        "type": "excel",
        "path": "/output/Airbus_Requirements_Matrix.xlsx",
        "description": "Detailed requirements response matrix"
      }
    ]
  }
}
```

## Field Definitions

### request_metadata
Basic request tracking information.
- `request_id`: Unique identifier for this generation request
- `request_type`: Type of document request
  - `rfp_response`, `proposal`, `technical_doc`, `executive_brief`, `poc_document`
- `created`: ISO 8601 timestamp when request was created
- `deadline`: When document must be completed
- `priority`: `low`, `medium`, `high`, `critical`
- `requestor`: Who requested this document

### document_spec
High-level document parameters.
- `document_type`: LaTeX document type (`solution`, `technical`, `internal`)
- `title`: Document title (goes on cover page)
- `subtitle`: Optional subtitle
- `output_filename`: Suggested filename for PDF
- `page_target`: Target page count (e.g., "20-30", "10", "<15")
- `tone`: Writing tone
  - `professional`, `technical`, `executive`, `conversational`
- `technical_depth`: Level of technical detail
  - `high_level`, `detailed`, `expert`, `mixed`

### customer_context
All customer/prospect information.

#### Basic Info
- `name`: Customer name
- `industry`: Primary industry
- `industry_tags`: Array of industry tags for content selection
- `size`: `SMB`, `Mid-Market`, `Enterprise`, `Fortune 500`
- `region`: Geographic region
- `country`: Specific country

#### technical_environment
Customer's technical landscape.
- `deployment_preference`: `on-premises`, `cloud`, `hybrid`
- `data_residency_requirements`: Countries/regions where data must stay
- `compliance_requirements`: Required certifications/standards
- `existing_systems`: Current systems to integrate with
- `infrastructure`: Infrastructure platforms in use
- `data_volume`: Data processing volume (TB/month, GB/day, etc.)
- `transaction_volume`: Transaction throughput (records/day, API calls/sec)

#### business_context
Business drivers and constraints.
- `primary_driver`: Main reason for this project
- `pain_points`: Array of current problems/challenges
- `success_criteria`: How success will be measured
- `budget`: Budget range (if known)
- `timeline`: Implementation timeline

#### stakeholders
Key people involved in decision.
- `name`: Stakeholder name
- `role`: Job title
- `influence`: `decision_maker`, `technical_buyer`, `influencer`, `user`, `blocker`
- `concerns`: Array of their specific concerns/priorities

### requirements
Structured requirement information.

- `source`: Where requirements came from ("RFP Document", "SOW", "Customer Brief")
- `source_file`: Path to original requirements file
- `total_requirements`: Total count
- `mandatory_requirements`: Count of mandatory reqs
- `optional_requirements`: Count of optional reqs

#### categories[]
Requirements organized by category.
- `category`: Category name
- `requirement_count`: Number of requirements in category
- `key_requirements[]`: Array of important requirements
  - `id`: Requirement ID (e.g., "REQ-001")
  - `text`: Requirement text
  - `priority`: `mandatory`, `optional`, `nice_to_have`
  - `response_status`: `met`, `partially_met`, `not_met`, `not_applicable`
  - `evidence`: How SnapLogic meets this requirement

- `sections_required`: Array of section IDs that must be in document

### use_cases
Specific use cases to address.

- `id`: Use case identifier
- `title`: Use case title
- `description`: Brief description
- `systems`: Systems involved
- `data_volume`: Data volume for this use case
- `frequency`: How often it runs
- `business_value`: Business benefit
- `current_solution`: What they use today (if anything)
- `pain_points`: Problems with current solution

### assets
Available files and resources.

#### images[]
Image files available for inclusion.
- `id`: Image identifier (for reference)
- `path`: Absolute path to image file
- `description`: What the image shows
- `usage`: Where/how to use it
- `width`: Default width (0.5-1.0)

#### data_files[]
Data files to process/incorporate.
- `id`: File identifier
- `path`: Absolute path to file
- `type`: File type (`excel`, `json`, `csv`, `xml`)
- `description`: What data it contains
- `usage`: How to use the data

#### reference_documents[]
Reference materials.
- `id`: Document identifier
- `path`: Path to reference document
- `description`: What it contains
- `usage`: How to use it

### content_preferences
Agent guidance for content selection.

- `reuse_existing`: Boolean - should agent try to reuse library content?
- `query_library_first`: Boolean - check library before generating new?
- `preferred_sections[]`: Array of section IDs to use if available
- `exclude_sections[]`: Array of section IDs to NOT use
- `variable_defaults`: Default variable values
- `custom_sections_needed[]`: Sections that must be generated custom

### constraints
Document constraints and requirements.

- `page_limit`: Maximum page count
- `language`: Document language
- `formatting_requirements[]`: Specific formatting needs
- `legal_review_required`: Boolean
- `approval_chain[]`: Who needs to approve before delivery

### output_requirements
What should be delivered.

- `formats[]`: Output format(s) needed
- `deliverables[]`: Specific files to produce
  - `type`: File type
  - `path`: Where to write output
  - `description`: What this file contains

## Usage: Agent Processing Flow

### 1. Load Request

```python
import json

with open('generation_request.json') as f:
    request = json.load(f)

customer_name = request['customer_context']['name']
deployment = request['customer_context']['technical_environment']['deployment_preference']
requirements = request['requirements']['sections_required']
```

### 2. Query Content Library

```python
# What sections does customer need?
required_sections = request['requirements']['sections_required']
# ['management_summary', 'company_overview', 'platform_architecture', ...]

# What sections can we reuse?
from content_library import query_index

reusable = {}
for section_type in required_sections:
    results = query_index(
        search=section_type,
        tags=['reusable', 'active'],
        deployment_type=deployment  # Filter: on-premises compatible
    )
    if results:
        reusable[section_type] = results[0]['id']  # Use most popular

print(f"Can reuse {len(reusable)}/{len(required_sections)} sections from library")
```

### 3. Generate Custom Sections

```python
# Which sections need custom generation?
custom_needed = set(required_sections) - set(reusable.keys())
custom_needed.update(request['content_preferences']['custom_sections_needed'])

for section_type in custom_needed:
    if section_type == 'management_summary':
        generate_mgmt_summary(
            customer_context=request['customer_context'],
            requirements=request['requirements'],
            use_cases=request['use_cases']
        )
    elif section_type == 'use_cases':
        generate_use_cases(
            use_cases=request['use_cases'],
            customer_context=request['customer_context']
        )
```

### 4. Build Manifest

```python
manifest = {
    'metadata': {
        'document_id': request['request_metadata']['request_id'],
        'document_title': request['document_spec']['title'],
        'document_type': request['document_spec']['document_type'],
        'customer': request['customer_context']['name'],
        'date': datetime.now().isoformat(),
        'version': '1.0'
    },
    'variables': request['content_preferences']['variable_defaults'],
    'sections': []
}

# Add reusable sections
for section_type, section_id in reusable.items():
    manifest['sections'].append({
        'id': section_type,
        'type': 'section',
        'source': f'library/{section_category}/{section_id}.json'
    })

# Add custom sections
for section_type in custom_needed:
    manifest['sections'].append({
        'id': section_type,
        'type': 'section',
        'source': f'documents/{project_id}/{section_type}.json'
    })
```

### 5. Compile Document

```python
compile_result = subprocess.run([
    'python3', 'scripts/compile_document.py',
    f'documents/{project_id}/manifest.json',
    request['output_requirements']['deliverables'][0]['path'],
    request['document_spec']['document_type']
])
```

## Example: Minimal Request

For simple documents, minimal request:

```json
{
  "request_metadata": {
    "request_id": "quick_proposal_001"
  },
  "document_spec": {
    "document_type": "solution",
    "title": "SnapLogic Proposal for Acme Corp"
  },
  "customer_context": {
    "name": "Acme Corp",
    "industry": "Manufacturing",
    "technical_environment": {
      "deployment_preference": "cloud"
    }
  },
  "requirements": {
    "sections_required": ["management_summary", "platform_overview"]
  },
  "content_preferences": {
    "reuse_existing": true,
    "variable_defaults": {
      "customer_name": "Acme Corp"
    }
  }
}
```

## Example: Complete RFP Response Request

See full example at top of this document - includes:
- Detailed customer context (technical + business)
- 114 requirements across 4 categories
- 3 detailed use cases
- Multiple assets (images, data files, references)
- Specific content preferences
- Output requirements

## Best Practices

### For Request Creators
- **Be complete**: Provide all context upfront, agents work better with full information
- **Structure requirements**: Group by category, prioritize, include evidence
- **Specify assets**: List all available images/data files with clear usage guidance
- **Set preferences**: Tell agent what to reuse vs. generate custom
- **Define constraints**: Page limits, deadlines, approval requirements

### For Agent Implementers
- **Validate request**: Check for required fields before processing
- **Query library first**: Check for reusable content before generating
- **Use customer context**: Tailor variable values, filter library results
- **Track coverage**: Ensure all required sections are addressed
- **Report gaps**: If requirements can't be met, report clearly

### For Content
- **Use variables**: Reference `request['customer_context']['name']` not hardcoded names
- **Filter by context**: Only use library sections matching deployment type, industry, etc.
- **Prioritize requirements**: Focus on mandatory requirements, note coverage
- **Include evidence**: For each requirement, cite how SnapLogic meets it

## Schema Validation

Minimal required fields:
```python
required_fields = [
    'request_metadata.request_id',
    'document_spec.document_type',
    'document_spec.title',
    'customer_context.name',
    'requirements.sections_required',
    'content_preferences.variable_defaults.customer_name'
]
```

Validation script:
```python
def validate_request(request):
    errors = []
    
    # Check required fields
    if 'customer_context' not in request:
        errors.append("Missing customer_context")
    if 'requirements' not in request or 'sections_required' not in request['requirements']:
        errors.append("Missing requirements.sections_required")
    
    # Check variable completeness
    required_vars = set()
    # ... query library for required variables of selected sections
    provided_vars = set(request.get('content_preferences', {}).get('variable_defaults', {}).keys())
    missing = required_vars - provided_vars
    if missing:
        errors.append(f"Missing required variables: {missing}")
    
    return errors
```
