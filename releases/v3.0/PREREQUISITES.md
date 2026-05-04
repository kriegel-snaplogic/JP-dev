# LaTeX Skills - Infrastructure Prerequisites

**Package Version:** v3.0  
**Last Updated:** 2026-05-04

## Quick Validation

Run the included validation script to check all prerequisites:

```bash
cd /path/to/latex-skills-package
chmod +x validate_prerequisites.sh
./validate_prerequisites.sh
```

The script will check all requirements and report PASS/FAIL/WARN status for each.

---

## Required Components

### 1. Python 3.7+

**Required for:** Orchestration, content processing, document compilation

**Check:**
```bash
python3 --version
# Expected: Python 3.7.0 or higher
```

**Installation:**
- **macOS:** Pre-installed (3.9+), or `brew install python3`
- **Ubuntu/Debian:** `sudo apt-get install python3 python3-pip`
- **RHEL/CentOS:** `sudo yum install python3 python3-pip`
- **Windows:** Download from python.org

**Required Python stdlib modules:**
- `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`
- `pathlib`, `typing`, `dataclasses` (Python 3.7+)

**Note:** No external pip packages required (stdlib only)

---

### 2. pdflatex (LaTeX Distribution)

**Required for:** PDF compilation (3 passes for TOC/cross-references)

**Check:**
```bash
pdflatex --version
# Expected: pdfTeX 3.14159... (any version from last 10 years)
```

**Installation:**

#### macOS
```bash
# Option 1: Full TeX Live (4GB, recommended)
brew install --cask mactex

# Option 2: Smaller distribution (1.5GB)
brew install --cask basictex
# Then install required packages:
sudo tlmgr update --self
sudo tlmgr install collection-latex collection-fontsrecommended
```

#### Ubuntu/Debian
```bash
# Full installation (recommended)
sudo apt-get update
sudo apt-get install texlive-full

# Minimal installation (if space constrained)
sudo apt-get install texlive-latex-base texlive-fonts-recommended \
  texlive-latex-extra texlive-lang-european
```

#### RHEL/CentOS
```bash
sudo yum install texlive-scheme-full
```

#### Windows
Download and install from: https://miktex.org/download

**Required LaTeX Packages:**
- `geometry` - Page layout
- `fontenc` - Font encoding
- `helvet` - Helvetica/Arial fonts
- `xcolor` - Color support
- `graphicx` - Image inclusion
- `longtable` - Multi-page tables
- `booktabs` - Professional tables
- `tabularx` - Flexible tables
- `colortbl` - Colored table cells
- `hyperref` - Clickable cross-references

**Verify packages:**
```bash
# Test compilation
cat > /tmp/test.tex << 'EOF'
\documentclass{article}
\usepackage{geometry,fontenc,helvet,xcolor,graphicx}
\usepackage{longtable,booktabs,tabularx,colortbl,hyperref}
\begin{document}
Test
\end{document}
EOF

pdflatex -interaction=nonstopmode /tmp/test.tex
```

If compilation fails, install missing packages:
```bash
# TeX Live
sudo tlmgr install <package-name>

# MiKTeX (Windows)
# Packages auto-install on first use
```

---

### 3. pdftotext (Poppler Utils)

**Required for:** PDF validation, regression testing, text extraction

**Check:**
```bash
pdftotext -v
# Expected: pdftotext version 0.x or higher
```

**Installation:**

#### macOS
```bash
brew install poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils
```

#### RHEL/CentOS
```bash
sudo yum install poppler-utils
```

#### Windows
Download from: https://github.com/oschwartz10612/poppler-windows/releases

Add `bin/` directory to PATH.

---

### 4. pdfinfo (Poppler Utils) - Optional

**Required for:** Page counting, PDF metadata extraction

**Check:**
```bash
pdfinfo -v
# Expected: pdfinfo version 0.x or higher
```

**Installation:** Same package as pdftotext (poppler-utils)

**Note:** If not available, page counting will fall back to alternative methods.

---

## System Requirements

### Disk Space

**Temporary files:**
- Each document compilation needs 10-50MB in `/tmp/`
- Work directory cleaned up automatically
- Large documents (100+ pages): up to 100MB temporary space

**Minimum:** 500MB free in `/tmp/`  
**Recommended:** 2GB+ free

**Check:**
```bash
df -h /tmp
```

### Memory

**Typical usage:**
- Small docs (<10 pages): ~100MB RAM
- Medium docs (10-50 pages): ~150MB RAM
- Large docs (50-100 pages): ~250MB RAM

**Minimum:** 512MB RAM  
**Recommended:** 2GB+ RAM

**Check:**
```bash
# macOS
sysctl hw.memsize

# Linux
free -m
```

### CPU

**Requirements:** Any modern CPU (x86_64 or ARM64)

**Performance:**
- pdflatex is single-threaded
- Compilation time scales linearly with page count
- Typical: 0.3-0.5 seconds per page

---

## File System Requirements

### Permissions

**Required directories:**
```bash
# Skills installation
~/.claude/skills/               # Read/Write
~/.claude/skills/latex-docs/    # Read/Write
~/.claude/skills/latex-content-processor/  # Read/Write

# Temporary compilation
/tmp/                          # Read/Write
```

**Check:**
```bash
# Test write permissions
touch ~/.claude/skills/test_file
rm ~/.claude/skills/test_file

touch /tmp/test_file
rm /tmp/test_file
```

### Path Resolution

**LaTeX must be in PATH:**
```bash
which pdflatex
# Expected: /Library/TeX/texbin/pdflatex (macOS)
#          /usr/bin/pdflatex (Linux)
```

If not in PATH, add to shell profile:
```bash
# macOS TeX Live
export PATH="/Library/TeX/texbin:$PATH"

# Linux
export PATH="/usr/local/texlive/2024/bin/x86_64-linux:$PATH"
```

---

## Optional Components

### curl or wget

**Purpose:** Fetching images from URLs (if using remote image references)

**Installation:**
```bash
# macOS: Pre-installed
# Ubuntu/Debian
sudo apt-get install curl

# RHEL/CentOS
sudo yum install curl
```

### git

**Purpose:** Version control for document projects, skill updates

**Installation:**
```bash
# macOS: Pre-installed (or Xcode tools)
# Ubuntu/Debian
sudo apt-get install git

# RHEL/CentOS
sudo yum install git
```

---

## Agent Infrastructure Specific

### For Containerized Deployments

**Dockerfile example:**
```dockerfile
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    texlive-full \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install skills
COPY latex-skills-package /root/.claude/skills/

# Test installation
RUN cd /root/.claude/skills/latex-docs && \
    python3 scripts/compile_document.py \
    test_documents/simple_test.json \
    /tmp/test.pdf \
    general
```

**Image size:** ~4-5GB (TeX Live is large)

**Optimization:** Use basictex + required packages only (~1.5GB)

### For AWS Lambda / Serverless

**Challenges:**
- LaTeX distribution is large (4GB+)
- Lambda has 250MB deployment limit (50MB zipped)
- Compilation time may exceed Lambda timeout

**Solutions:**
1. **Use Lambda Layers:** Package TeX Live in a layer
2. **Pre-compiled templates:** Generate LaTeX → PDF on larger instance
3. **ECS/Fargate:** Better suited for LaTeX compilation

**Alternative:** Run skills on EC2/ECS, expose via API

### For Kubernetes

**Resource requests:**
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

**Volume requirements:**
```yaml
volumes:
  - name: tmp
    emptyDir:
      sizeLimit: 2Gi
```

---

## Validation Checklist

Use this checklist to manually verify prerequisites:

- [ ] Python 3.7+ installed and in PATH
- [ ] `python3 --version` shows 3.7.0 or higher
- [ ] Python stdlib modules available (json, re, dataclasses, etc.)
- [ ] pdflatex installed and in PATH
- [ ] `pdflatex --version` shows version info
- [ ] All required LaTeX packages installed
- [ ] Test LaTeX compilation succeeds
- [ ] pdftotext installed and in PATH
- [ ] pdfinfo installed (optional but recommended)
- [ ] At least 500MB free in /tmp/
- [ ] At least 512MB system RAM
- [ ] ~/.claude/skills/ directory writable
- [ ] /tmp/ directory writable
- [ ] Skills extracted to ~/.claude/skills/
- [ ] Test compilation succeeds: simple_test.json → PDF

---

## Troubleshooting

### "python3: command not found"

**Fix:** Install Python 3.7+ or create symlink:
```bash
# If python3.9 exists but python3 doesn't
sudo ln -s /usr/bin/python3.9 /usr/bin/python3
```

### "pdflatex: command not found"

**Fix:** Install LaTeX distribution or add to PATH:
```bash
# Find pdflatex
find /usr -name pdflatex 2>/dev/null

# Add to PATH
export PATH="/path/to/tex/bin:$PATH"
```

### "Package 'xcolor' not found"

**Fix:** Install missing LaTeX package:
```bash
# TeX Live
sudo tlmgr install xcolor

# MiKTeX
# Auto-installs on first use, or use MiKTeX Console
```

### "No space left on device"

**Fix:** Clean up /tmp/ or increase disk space:
```bash
# Clean old temporary files
sudo rm -rf /tmp/snaplogic_doc_*
```

### "Permission denied" writing to ~/.claude/skills/

**Fix:** Check ownership and permissions:
```bash
ls -ld ~/.claude/skills/
# Should show your user as owner

# Fix permissions
chmod 755 ~/.claude/skills/
```

---

## Performance Tuning

### Compilation Speed

**Bottleneck:** pdflatex (3 passes)

**Optimization tips:**
1. Use SSD for /tmp/ (faster I/O)
2. Disable network lookups in LaTeX: `export TEXMFHOME=/dev/null`
3. Pre-compile large documents, cache results
4. For repeated compilations, use `latexmk` with caching

### Memory Usage

**Large documents (100+ pages):**
- Increase pdflatex memory: `export main_memory=12000000`
- Monitor with: `ps aux | grep pdflatex`

### Concurrent Compilations

**Safe:** LaTeX work directories are unique (temp files in /tmp/snaplogic_doc_<random>/)

**Limits:** CPU cores (pdflatex is single-threaded per compilation)

---

## Security Considerations

### LaTeX Compilation Risks

**Shell escape disabled by default** - LaTeX cannot execute shell commands

**Input validation** - JSON structure validated before compilation

**Temporary file cleanup** - Work directories cleaned up (or preserved on error for debugging)

### Recommended Hardening

```bash
# Restrict pdflatex permissions (Linux)
# Run in restricted shell mode
pdflatex -no-shell-escape <file>

# Run as non-root user (always)
# Never run LaTeX compilation as root

# Set ulimits for resource control
ulimit -t 60      # 60 second CPU time limit
ulimit -v 2097152 # 2GB virtual memory limit
```

---

## Support

For issues with prerequisites:

1. Run validation script: `./validate_prerequisites.sh`
2. Check specific failed component above
3. Review error messages from installation commands
4. Consult distribution-specific documentation:
   - TeX Live: https://tug.org/texlive/
   - Poppler: https://poppler.freedesktop.org/
   - Python: https://python.org/

---

**Last Validated:** 2026-05-04 on macOS (Darwin, arm64)  
**Validation Status:** ✅ ALL CHECKS PASSED
