# LaTeX Skills v3.0 - Release Manifest

**Release Date:** 2026-05-04  
**Version:** 3.0 (Modular Architecture)  
**Status:** Production-ready

## Package Information

**Filename:** `latex-skills-v3.0-modular.tar.gz`  
**Size:** 44 MB  
**SHA256:** `434bb5645aea1e44a4aee7f5507376c4954b7d4a68cf7a28b8d7ac00ff084a47`

## Build Package

To rebuild the release package:

```bash
cd /Users/konstantinriegel/.claude/skills
tar -czf /tmp/latex-skills-v3.0-modular.tar.gz \
  --transform 's,^,latex-skills-package/,' \
  latex-docs/ \
  latex-content-processor/ \
  doc-quality-advisor/
```

## Package Contents

This directory contains the extracted package for version control:

- `latex-docs/` - Main orchestrator skill (899 lines)
- `latex-content-processor/` - Format handler skill (1,192 lines)
- `doc-quality-advisor/` - Quality validator skill (unchanged)
- `README.md` - Package overview
- `DEPLOYMENT.md` - Installation guide
- `PREREQUISITES.md` - Infrastructure requirements
- `AGENT_DEPLOYMENT_CHECKLIST.md` - Deployment steps
- `validate_prerequisites.sh` - Automated validation

## Distribution

**For agent infrastructure deployment:**
1. Build package from source using command above
2. Verify SHA256 checksum matches
3. Follow AGENT_DEPLOYMENT_CHECKLIST.md

**Note:** The tarball is NOT committed to git (44MB). Build from source or download from releases.
