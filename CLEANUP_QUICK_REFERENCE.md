# Quick Cleanup Reference Checklist

## ✅ Files That Are Already Great

```
LICENSE                      MIT License ✅
README.md                    Comprehensive ✅
README.pt-BR.md              Localized ✅
pyproject.toml               Modern Python packaging ✅
setup.py                     Present as fallback ✅
.gitignore                   Comprehensive ✅
.gitattributes               Configured ✅
.github/workflows/test.yml   CI/CD setup ✅
DOCS/                        Excellent documentation ✅
polly/                       Clean package structure ✅
tests/                       Test directory present ✅
examples/                    Examples provided ✅
```

---

## 🧹 Priority 1: Must Remove (5 minutes)

These should be deleted immediately:

```bash
# Delete these 8 shell scripts (development/maintenance only)
rm -f add_dashboard_to_main.sh
rm -f diagnose_backend.sh
rm -f diagnose_dashboard_routes.sh
rm -f fix_backend.sh
rm -f fix_dashboard_location.sh
rm -f fix_database_paths.sh
rm -f fix_database_paths_proper.sh
rm -f verify_and_restart.sh

# Delete this test/placeholder file
rm -f pergunta.txt
```

**Why:** These are internal development tools that clutter the repository. Users don't need them.

**Commit:** `git commit -am "chore: remove development scripts"`

---

## ⚠️ Priority 2: Decide & Handle (5-10 minutes)

### The `web/` Directory

Currently ignored in .gitignore (lines 91-92). Options:

1. **DELETE** (recommended if not active)
   ```bash
   rm -rf web/
   ```

2. **KEEP & DOCUMENT** (if it's an active dashboard)
   ```bash
   # Explain in README why web/ is excluded/deprecated
   ```

3. **MOVE TO SEPARATE REPO** (if it's a companion project)
   ```bash
   # Create new repo: polly-dashboard
   # Move contents there
   ```

**Recommendation:** ✅ **DELETE** - The .gitignore exclusion suggests it was planned for removal.

```bash
# After decision:
rm -rf web/
```

---

## 📚 Priority 3: Review DOCS/ (10 minutes)

### Files to Review/Clean

| File | Status | Action |
|------|--------|--------|
| ATUALIZACAO_IDIOMA.md | ✅ Keep | User-facing translation guide |
| AUR_SETUP.md | ✅ Keep | Installation guide |
| CHANGELOG.md | ✅ Keep | Project history |
| CONTRIBUTING.md | ✅ Keep | Contributor guide |
| INSTALL.md | ✅ Keep | Installation instructions |
| QUICKSTART.md | ✅ Keep | Quick start guide |
| PROJECT_SUMMARY.md | ✅ Keep | Project overview |
| OS_AWARE_PROMPTS_SUMMARY.md | ✅ Keep | Feature documentation |
| README.md | ✅ Keep | DOCS overview |
| CRITICAL_IMPROVEMENTS.md | ⚠️ Review | Development notes |
| IMPLEMENTATION_SUMMARY.md | ⚠️ Review | Development notes |
| REFACTORING_SUMMARY.md | ⚠️ Review | Development notes |
| OS_DETECTION_TEST_REPORT.md | ❌ Remove | Test artifact |
| RELEASE_CHECKLIST.md | ❌ Remove | Internal process |

**Action:**
```bash
# Remove test artifacts
rm -f DOCS/OS_DETECTION_TEST_REPORT.md
rm -f DOCS/RELEASE_CHECKLIST.md

# Review development notes - consider moving to GitHub Wiki if not needed by users
# Keep if helpful for understanding implementation
```

---

## 🔗 Priority 4: Add Root References (Optional)

If CONTRIBUTING.md and CHANGELOG.md are only in DOCS/, GitHub won't find them. Options:

### Option A: Create Symlinks
```bash
ln -s DOCS/CONTRIBUTING.md CONTRIBUTING.md
ln -s DOCS/CHANGELOG.md CHANGELOG.md
```

### Option B: Create Redirect Files
```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to Polly

See [Contributing Guide](DOCS/CONTRIBUTING.md)
EOF

cat > CHANGELOG.md << 'EOF'
# Changelog

See [Full Changelog](DOCS/CHANGELOG.md)
EOF
```

### Option C: Do Nothing
GitHub will find them in DOCS/ folder, just not as prominently.

**Recommendation:** ✅ **Option A or B** - Makes contributing easier for newcomers

---

## 🚀 Priority 5: Optional Enhancements

### Add to Root (High-Impact)

1. **CODE_OF_CONDUCT.md**
   ```markdown
   # Code of Conduct

   [Use standard CoC from:]
   - Contributor Covenant (https://www.contributor-covenant.org/)
   ```

2. **SECURITY.md**
   ```markdown
   # Security Policy

   Please report security vulnerabilities to [your-email]
   ```

3. **.github/ISSUE_TEMPLATE/**
   ```bash
   # Create templates for:
   # - Bug reports
   # - Feature requests
   # - Question/Discussion
   ```

4. **.github/PULL_REQUEST_TEMPLATE.md**
   ```bash
   # Create PR template with checklist
   ```

**Recommendation:** ✅ Add at least CODE_OF_CONDUCT.md and SECURITY.md

---

## 📋 Complete Cleanup Steps

### Before You Start
```bash
cd /home/user/polly
git status  # Should be clean
```

### Step 1: Delete Development Scripts (2 min)
```bash
rm -f add_dashboard_to_main.sh
rm -f diagnose_backend.sh
rm -f diagnose_dashboard_routes.sh
rm -f fix_backend.sh
rm -f fix_dashboard_location.sh
rm -f fix_database_paths.sh
rm -f fix_database_paths_proper.sh
rm -f verify_and_restart.sh
rm -f pergunta.txt
```

### Step 2: Handle Web Directory (1 min)
```bash
# Option A: Delete (RECOMMENDED)
rm -rf web/

# Option B: (if keeping, update README to explain)
```

### Step 3: Clean DOCS Directory (2 min)
```bash
# Remove test artifacts
rm -f DOCS/OS_DETECTION_TEST_REPORT.md
rm -f DOCS/RELEASE_CHECKLIST.md
```

### Step 4: Add Root References (Optional, 3 min)
```bash
# Create symlinks or redirect files
ln -s DOCS/CONTRIBUTING.md CONTRIBUTING.md
ln -s DOCS/CHANGELOG.md CHANGELOG.md
```

### Step 5: Verify Changes
```bash
# Check what changed
git status

# Verify no critical files were removed
ls -la | grep -E "^[^.]"  # Check root contents
```

### Step 6: Test Package Installation
```bash
# Make sure package still works
pip install -e .
polly --help
```

### Step 7: Commit Changes
```bash
# Stage removals
git add -A

# Commit with clear message
git commit -m "chore: clean up development artifacts for open source

- Remove 8 diagnostic/maintenance shell scripts
- Remove pergunta.txt placeholder file
- Remove web/ directory (legacy)
- Remove OS test report from DOCS/
- Add root-level references to CONTRIBUTING.md and CHANGELOG.md"
```

### Step 8: Push to Remote
```bash
git push origin claude/fix-model-listing-013AzMbfkz2HJj3mrN6NmHbC
```

---

## 🎯 What Gets Removed (9 items)

```
Removing from root:
  1. add_dashboard_to_main.sh         (diagnostic script)
  2. diagnose_backend.sh              (diagnostic script)
  3. diagnose_dashboard_routes.sh     (diagnostic script)
  4. fix_backend.sh                   (maintenance script)
  5. fix_dashboard_location.sh        (maintenance script)
  6. fix_database_paths.sh            (maintenance script)
  7. fix_database_paths_proper.sh     (maintenance script)
  8. verify_and_restart.sh            (maintenance script)
  9. pergunta.txt                     (test file)

Removing from directory:
  10. web/                            (legacy/unclear)

Removing from DOCS/:
  11. OS_DETECTION_TEST_REPORT.md    (test artifact)
  12. RELEASE_CHECKLIST.md            (internal process)

Total: 12 files/directories removed
Impact: Repository becomes significantly cleaner
```

---

## ✅ Final Checklist

After cleanup, verify:

```
[ ] All 9 root .sh files deleted
[ ] pergunta.txt deleted
[ ] web/ directory removed or justified
[ ] DOCS/ artifacts removed
[ ] Root symlinks created (CONTRIBUTING.md, CHANGELOG.md)
[ ] git status shows clean
[ ] pip install -e . still works
[ ] polly --help works
[ ] All commits pushed
[ ] README still looks good
[ ] No broken links in documentation
```

---

## 📊 Final Repository Structure

After cleanup:

```
polly/                              (clean!)
├── .github/
│   └── workflows/test.yml         ✅
├── .gitattributes                 ✅
├── .gitignore                     ✅
├── CONTRIBUTING.md → DOCS/        🔗 NEW
├── CHANGELOG.md → DOCS/           🔗 NEW
├── CODE_OF_CONDUCT.md             🆕 OPTIONAL
├── SECURITY.md                    🆕 OPTIONAL
├── LICENSE                        ✅
├── README.md                      ✅
├── README.pt-BR.md                ✅
├── pyproject.toml                 ✅
├── setup.py                       ✅
├── DOCS/
│   ├── (all essential docs)       ✅
│   └── (no test artifacts)        ✅
├── polly/                         ✅
├── tests/                         ✅
├── examples/                      ✅
└── images/                        ✅

Removed:
❌ add_dashboard_to_main.sh
❌ diagnose_backend.sh
❌ diagnose_dashboard_routes.sh
❌ fix_backend.sh
❌ fix_dashboard_location.sh
❌ fix_database_paths.sh
❌ fix_database_paths_proper.sh
❌ verify_and_restart.sh
❌ pergunta.txt
❌ web/
❌ DOCS/OS_DETECTION_TEST_REPORT.md
❌ DOCS/RELEASE_CHECKLIST.md
```

---

## 🎉 Result: Open-Source Ready Repository!

**Time to complete:** 45 minutes (Priority 1-3)
**Risk level:** VERY LOW
**Impact:** VERY HIGH

The repository will be significantly cleaner, more professional, and ready for open source distribution.
