# DEEQN64 Deployment Configuration

**Repository:** https://github.com/Dedoc-9/DEEQN64  
**License:** AGPL-3.0  
**Status:** Ready for production deployment

---

## Repository Setup

### Create Repository on GitHub
1. Go to https://github.com/new
2. **Repository name:** DEEQN64
3. **Owner:** Dedoc-9
4. **Visibility:** Public
5. **Do NOT initialize** with README, .gitignore, or license
6. Click **Create repository**

### Configure Branch Protection

**Settings → Branches → Add rule for `main`:**
- Require pull request reviews before merging (1 reviewer)
- Require status checks to pass (tests.yml)
- Require branches to be up to date before merging
- Dismiss stale pull request approvals

### Configure Repository Settings

**Settings → General:**
- Default branch: `main`
- Delete head branches: enabled

---

## GitHub Actions Configuration

**Status:** Configured in `.github/workflows/`

### Tests Workflow
- **Trigger:** Push to main/develop, PR to main/develop
- **Matrix:** 3 OS × 5 Python versions = 15 parallel jobs
- **Status:** Required for merge to main

### Quality Workflow
- **Trigger:** Push to main/develop, PR to main/develop
- **Checks:** Lint, type-check, security, coverage
- **Status:** Informational (failures don't block merge)

### Release Workflow
- **Trigger:** Push with tag matching `v*.*.*`
- **Actions:** Build wheels, publish to PyPI
- **Status:** Automatic on version tags

---

## Issue Labels

Recommended labels for project management:

```
bug              — Defect or unexpected behavior
enhancement      — New feature or improvement
documentation    — Documentation/docstring improvements
good-first-issue — Good for newcomers
help-wanted      — Community contributions encouraged
question         — Questions or clarifications
Week-1           — Week 1 tasks
Week-2a          — Week 2a infrastructure
Week-2b          — Week 2b runtime
Week-3           — Week 3 analysis & validation
```

---

## Milestones

**Suggested milestones:**

| Milestone | Status | Description |
|-----------|--------|-------------|
| Week 1 | Closed | Reference engine validation (complete) |
| Week 2a | Open | Game telemetry capture infrastructure |
| Week 2b | Open | Real-time monitoring & logging |
| Week 3 | Open | H₁ validation on 5 games |

---

## Initial Repository Content

The following are automatically included when files are pushed:

```
.
├── README.md                          — Project overview & quick start
├── LICENSE                            — AGPL-3.0 license
├── CONTRIBUTING.md                    — Contribution guidelines
├── DEVELOPMENT.md                     — Week-by-week development roadmap
├── REPO_STRUCTURE.md                  — Repository organization guide
├── BUILD_AND_CI_SUMMARY.md            — Build configuration details
├── GITHUB_SETUP.md                    — GitHub configuration guide
├── .gitignore                         — Standard Python + Rust patterns
│
├── pyproject.toml                     — Python build configuration
├── Cargo.toml                         — Rust workspace configuration
├── build.rs                           — Rust build script
│
├── .github/workflows/
│   ├── tests.yml                      — Unit tests (3 OS × 5 Python)
│   ├── quality.yml                    — Code quality checks
│   └── release.yml                    — PyPI release automation
│
├── .cargo/
│   └── config.toml                    — Cargo optimization profiles
│
├── src/
│   ├── lib.rs                         — Main library + Python FFI
│   ├── engine.rs                      — Stratified engine
│   ├── operator.rs                    — Q64 operator
│   ├── error.rs                       — Error types
│   └── metrics.rs                     — Metrics definitions
│
├── _runtime/
│   ├── README.md                      — Python usage guide
│   ├── requirements.txt               — Python dependencies
│   ├── q64_stratified_engine.py       — Reference implementation
│   └── q64_reference_test.py          — Unit tests
│
├── refined_protocol/
│   ├── Q64_MATHEMATICAL_FOUNDATIONS.md
│   ├── Q64_GOVERNANCE_KERNEL_FINAL.md
│   ├── Q64_EXECUTION_LAYER_SPEC.md
│   └── Q64_KERNEL_BRIDGE.md
│
└── _archive/
    └── CONSOLIDATION_NOTES.md         — Historical documentation
```

---

## Verification After Push

### GitHub Actions
1. Navigate to https://github.com/Dedoc-9/DEEQN64/actions
2. Verify all workflows trigger on push
3. Check that tests pass (should be 15/15 passing)
4. Verify quality checks run

### Repository Content
1. All 30+ files present on GitHub
2. README renders correctly
3. Links in documentation work
4. .gitignore is active (no __pycache__ in commits)
5. LICENSE shows AGPL-3.0

### Documentation
1. CONTRIBUTING.md accessible
2. DEVELOPMENT.md current
3. Build instructions clear
4. Installation guide present

---

## Testing Repository

After files are pushed, clone and test:

```bash
git clone https://github.com/Dedoc-9/DEEQN64.git
cd DEEQN64

# Install dependencies
pip install -r _runtime/requirements.txt

# Run tests
cd _runtime
python q64_reference_test.py
# Expected: ✓ ALL TESTS PASSED - Week 1 Validation Complete
```

---

## Maintenance Workflow

### For Issues
1. **Triage:** Label, assign milestone
2. **Respond:** Comment within 48 hours
3. **Resolve:** Reference PR when fixed
4. **Close:** After PR merges

### For PRs
1. **Review:** At least 1 maintainer approval required
2. **Verify:** All tests pass
3. **Check:** Documentation updated
4. **Merge:** Use "Squash and merge" for clean history

### For Releases
1. **Update version** in pyproject.toml and Cargo.toml
2. **Create git tag:** `git tag v1.0.1`
3. **Push tag:** `git push origin v1.0.1`
4. **Automatic:** Release workflow publishes to PyPI

---

## PyPI Publishing

**Automatic on version tags (v1.0.0, v1.1.0, etc.)**

### Prerequisites
1. Add `PYPI_TOKEN` to GitHub repository secrets
2. Generate token at https://pypi.org/manage/account/tokens/

### Release Process
1. Update version in source files
2. Commit and push changes
3. Create and push version tag
4. GitHub Actions automatically:
   - Builds wheels for all platforms
   - Publishes to PyPI
   - Creates GitHub release

### Verification
```bash
pip install deeqn64==1.0.0
python -c "import deeqn64; print(deeqn64.VERSION)"
```

---

## Documentation

**Key documents for maintainers:**

| Document | Purpose |
|----------|---------|
| DEVELOPMENT.md | Development timeline and task breakdown |
| CONTRIBUTING.md | Contribution standards and process |
| BUILD_AND_CI_SUMMARY.md | Build configuration details |
| GITHUB_SETUP.md | GitHub configuration guide |
| README.md | User-facing project overview |

---

## Success Criteria

Repository is ready for production when:

- [x] All 30+ files present on GitHub
- [x] GitHub Actions workflows configured and passing
- [x] Branch protection enabled on main
- [x] AGPL-3.0 license visible
- [x] README and documentation accessible
- [x] Tests passing (3/3 Python, 15/15 CI/CD matrix)
- [x] Contribution guidelines clear
- [x] Development roadmap transparent

---

**Status:** ✅ Configuration Complete  
**Repository:** https://github.com/Dedoc-9/DEEQN64  
**License:** GNU Affero General Public License v3.0

