# Agent Infrastructure Deployment Checklist

**Package:** latex-skills-v3.0-modular.tar.gz  
**Target:** Agent infrastructure (automated deployment)

## Pre-Deployment Validation

### Step 1: Run Automated Validation

```bash
# Extract package
tar -xzf latex-skills-v3.0-modular.tar.gz
cd latex-skills-package/

# Run validation script
chmod +x validate_prerequisites.sh
./validate_prerequisites.sh
```

**Expected result:** ✅ ALL CHECKS PASSED

**If checks fail:**
1. Review failed components in output
2. Consult `PREREQUISITES.md` for installation instructions
3. Install missing components
4. Re-run validation script

---

### Step 2: Verify System Resources

**Minimum requirements:**
- [ ] Python 3.7+
- [ ] pdflatex (TeX Live or MiKTeX)
- [ ] pdftotext (poppler-utils)
- [ ] 500MB free disk space in /tmp/
- [ ] 512MB RAM
- [ ] Write permissions to ~/.claude/skills/

**Check commands:**
```bash
python3 --version              # >= 3.7
pdflatex --version            # Any version
pdftotext -v                  # Any version
df -h /tmp                    # >= 500MB free
free -m                       # >= 512MB (Linux)
sysctl hw.memsize             # >= 536870912 bytes (macOS)
```

---

## Deployment Steps

### Step 3: Install Skills

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills/

# Extract skills
cd ~/.claude/skills/
tar -xzf /path/to/latex-skills-v3.0-modular.tar.gz --strip-components=1

# Verify extraction
ls -la ~/.claude/skills/
# Should see: latex-docs/, latex-content-processor/, doc-quality-advisor/
```

**Verify files:**
```bash
# Check key files exist
test -f ~/.claude/skills/latex-docs/scripts/compile_document.py && echo "✓ Main compiler found"
test -f ~/.claude/skills/latex-content-processor/scripts/content_processor.py && echo "✓ Content processor found"
test -f ~/.claude/skills/doc-quality-advisor/SKILL.md && echo "✓ Quality advisor found"
```

---

### Step 4: Test Basic Compilation

```bash
cd ~/.claude/skills/latex-docs/

# Test simple document (6 pages)
python3 scripts/compile_document.py \
  test_documents/simple_test.json \
  /tmp/agent_test_simple.pdf \
  general

# Verify output
test -f /tmp/agent_test_simple.pdf && echo "✓ Simple test passed"
pdfinfo /tmp/agent_test_simple.pdf | grep Pages
# Expected: Pages: 6
```

---

### Step 5: Test Table Styles

```bash
# Test all table styles (11 pages)
python3 scripts/compile_document.py \
  test_documents/table_styles_test.json \
  /tmp/agent_test_tables.pdf \
  general

# Verify output
test -f /tmp/agent_test_tables.pdf && echo "✓ Table styles test passed"
pdfinfo /tmp/agent_test_tables.pdf | grep Pages
# Expected: Pages: 11
```

---

### Step 6: Test Complex Document

```bash
# Test comprehensive document (70 pages)
python3 scripts/compile_document.py \
  test_documents/airbus_rfp_v3_test.json \
  /tmp/agent_test_complex.pdf \
  general

# Verify output
test -f /tmp/agent_test_complex.pdf && echo "✓ Complex test passed"
pdfinfo /tmp/agent_test_complex.pdf | grep Pages
# Expected: Pages: 70
```

---

### Step 7: Performance Baseline

```bash
# Measure compilation time
time python3 scripts/compile_document.py \
  test_documents/simple_test.json \
  /tmp/perf_test.pdf \
  general

# Expected: 3-5 seconds for 6-page document
# Note: First run may be slower (LaTeX package loading)
```

**Performance targets:**
- Simple (6 pages): 3-5 seconds
- Medium (11 pages): 5-10 seconds
- Complex (70 pages): 15-25 seconds

**If slower:** Check CPU, disk I/O, LaTeX package installation

---

## Post-Deployment Validation

### Step 8: Integration Test

Create a test document and compile:

```bash
cat > /tmp/integration_test.json << 'EOF'
{
  "title": "Agent Infrastructure Test",
  "author": "Automated Test",
  "version": "1.0",
  "date": "2026-05-04",
  "sections": [
    {
      "title": "Test Section",
      "content": "This is a test document.\n\n**Bold text** and *italic text*.\n\n- Bullet 1\n- Bullet 2"
    },
    {
      "title": "Table Test",
      "content": "[TABLE:simple:Test Table]\n| A | B |\n|---|---|\n| 1 | 2 |\n[/TABLE]"
    }
  ]
}
EOF

python3 ~/.claude/skills/latex-docs/scripts/compile_document.py \
  /tmp/integration_test.json \
  /tmp/integration_test.pdf \
  general

# Verify
test -f /tmp/integration_test.pdf && echo "✓ Integration test passed"
```

---

### Step 9: Error Handling Test

Test compilation failure handling:

```bash
# Create invalid JSON
echo '{"invalid": json}' > /tmp/invalid_test.json

python3 ~/.claude/skills/latex-docs/scripts/compile_document.py \
  /tmp/invalid_test.json \
  /tmp/should_fail.pdf \
  general 2>&1 | grep -E '(error|Error)'

# Expected: Error message displayed
# Work directory preserved for debugging
```

---

### Step 10: Cleanup Test

Verify temporary files are cleaned up:

```bash
# Count temp directories before
BEFORE=$(ls -1d /tmp/snaplogic_doc_* 2>/dev/null | wc -l)

# Run successful compilation
python3 ~/.claude/skills/latex-docs/scripts/compile_document.py \
  ~/.claude/skills/latex-docs/test_documents/simple_test.json \
  /tmp/cleanup_test.pdf \
  general

# Count temp directories after
AFTER=$(ls -1d /tmp/snaplogic_doc_* 2>/dev/null | wc -l)

# Should be same (temp directory cleaned up)
if [ "$BEFORE" -eq "$AFTER" ]; then
  echo "✓ Cleanup test passed"
else
  echo "⚠ Warning: Temp directory may not have been cleaned up"
fi
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

**Compilation Success Rate:**
```bash
# Track successful vs failed compilations
# Alert if success rate < 95%
```

**Compilation Time:**
```bash
# Track average compilation time per page
# Alert if > 1 second per page (baseline: 0.3-0.5s/page)
```

**Disk Usage:**
```bash
# Monitor /tmp/ usage
df -h /tmp
# Alert if < 500MB free
```

**Memory Usage:**
```bash
# Monitor pdflatex memory usage
ps aux | grep pdflatex
# Alert if > 1GB per process
```

### Error Patterns to Watch

1. **"No module named 'content_processor'"**
   - Cause: latex-content-processor not installed
   - Fix: Verify skill installation

2. **"pdflatex: command not found"**
   - Cause: LaTeX not in PATH
   - Fix: Add to PATH or reinstall

3. **"No space left on device"**
   - Cause: /tmp/ full
   - Fix: Clean up or increase disk

4. **LaTeX compilation timeout**
   - Cause: Very large document or system overload
   - Fix: Increase timeout or split document

---

## Rollback Procedure

If deployment fails or issues are discovered:

### Quick Rollback

```bash
# Remove new skills
rm -rf ~/.claude/skills/latex-docs/
rm -rf ~/.claude/skills/latex-content-processor/

# Restore from previous version (if available)
# Or wait for fixes and redeploy
```

### Partial Rollback

If only one skill is problematic:

```bash
# Extract only specific skill from backup
tar -xzf latex-skills-v2.0-backup.tar.gz \
  --strip-components=1 \
  latex-skills-package/latex-docs/
```

---

## Production Readiness Checklist

Before enabling for production traffic:

- [ ] All validation checks pass
- [ ] All 3 test documents compile successfully
- [ ] Performance meets baselines (<1s per page)
- [ ] Error handling tested
- [ ] Cleanup verified
- [ ] Monitoring configured
- [ ] Rollback procedure documented
- [ ] Team notified of deployment
- [ ] Documentation accessible
- [ ] Support contacts identified

---

## Containerized Deployment

### Docker Example

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-lang-european \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy skills
COPY latex-skills-package/latex-docs /root/.claude/skills/latex-docs
COPY latex-skills-package/latex-content-processor /root/.claude/skills/latex-content-processor
COPY latex-skills-package/doc-quality-advisor /root/.claude/skills/doc-quality-advisor

# Run validation
RUN cd /root/.claude/skills/latex-docs && \
    python3 scripts/compile_document.py \
    test_documents/simple_test.json \
    /tmp/test.pdf \
    general && \
    test -f /tmp/test.pdf

# Cleanup test files
RUN rm -rf /tmp/*.pdf /tmp/snaplogic_doc_*

WORKDIR /root/.claude/skills/latex-docs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 scripts/compile_document.py \
    test_documents/simple_test.json \
    /tmp/health_check.pdf \
    general && test -f /tmp/health_check.pdf

# Entry point
ENTRYPOINT ["python3", "scripts/compile_document.py"]
```

**Build:**
```bash
docker build -t latex-skills:v3.0 .
```

**Test:**
```bash
docker run --rm \
  -v $(pwd)/input.json:/tmp/input.json \
  -v $(pwd)/output:/tmp/output \
  latex-skills:v3.0 \
  /tmp/input.json \
  /tmp/output/document.pdf \
  general
```

---

## Kubernetes Deployment

### Resource Requirements

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: latex-docs-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: latex-docs
  template:
    metadata:
      labels:
        app: latex-docs
    spec:
      containers:
      - name: latex-docs
        image: latex-skills:v3.0
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir:
          sizeLimit: 2Gi
```

---

## Support

**Deployment issues:**
1. Run `./validate_prerequisites.sh`
2. Check `PREREQUISITES.md` for missing components
3. Review error messages in compilation logs
4. Check `/tmp/snaplogic_doc_*/document.log` for LaTeX errors

**Contact:**
- Documentation: See ARCHITECTURE.md, DEPLOYMENT.md
- Migration notes: See MIGRATION_NOTES.md
- Test suite: See test_documents/README.md

---

**Deployment Date:** _____________________  
**Deployed By:** _____________________  
**Validation Status:** _____________________  
**Production Enabled:** _____________________
