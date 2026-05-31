# GitHub Repository Setup for DEEQN64

**Repository:** https://github.com/Dedoc-9/DEEQN64  
**License:** GNU Affero General Public License v3.0 (AGPL-3.0)  
**Status:** Week 1 validation complete, ready for public contribution

---

## Repository Configuration

### Basic Settings

**Repository Name:** DEEQN64  
**Owner:** Dedoc-9  
**Visibility:** Public  
**License:** AGPL-3.0  

### Branch Configuration

**Default Branch:** `main`

**Protected Branches (main):**
- Require pull request reviews before merging (1+ approver)
- Require status checks to pass (GitHub Actions tests)
- Require branches to be up to date before merging
- Dismiss stale pull request approvals when new commits are pushed

### Topics/Tags
- `spectral-analysis`
- `stability-certification`
- `q64`
- `dynamical-systems`
- `structural-assurance`

---

## Continuous Integration

### GitHub Actions Workflow

**File:** `.github/workflows/tests.yml`

**Triggers:**
- Push to `main` or `develop` branch
- Pull requests to `main` or `develop` branch

**Test Matrix:**
```
OS:       Ubuntu, macOS, Windows
Python:   3.10, 3.11, 3.12, 3.13, 3.14
```

**Workflow Steps:**
1. Checkout code
2. Set up Python
3. Install dependencies (`pip install -r _runtime/requirements.txt`)
4. Run unit tests (`cd _runtime && python q64_reference_test.py`)
5. Run engine demo (`cd _runtime && python q64_stratified_engine.py`)

**Status Badge** (add to README.md):
```markdown
![Tests](https://github.com/Dedoc-9/DEEQN64/workflows/Tests/badge.svg)
```

---

## Issue & PR Labels

### Suggested Labels

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `d73a4a` | Defect or unexpected behavior |
| `enhancement` | `a2eeef` | New feature or improvement |
| `documentation` | `0075ca` | Documentation or docstring improvements |
| `good first issue` | `7057ff` | Good for newcomers |
| `help wanted` | `008672` | Community contributions encouraged |
| `question` | `d876e3` | User question or clarification |
| `invalid` | `e4e669` | Not reproducible or outside scope |
| `duplicate` | `cccccc` | Duplicate of existing issue |
| `Week-1` | `fbca04` | Week 1 (complete) |
| `Week-2a` | `fbca04` | Week 2a infrastructure |
| `Week-2b` | `fbca04` | Week 2b runtime |
| `Week-3` | `fbca04` | Week 3 analysis & validation |

---

## Milestones

### Phase Milestones

| Milestone | Target | Status | Description |
|-----------|--------|--------|-------------|
| Week 1 | Complete | ✅ Closed | Reference engine validation on synthetic data |
| Week 2a | In Progress | ⏳ Open | Game telemetry capture infrastructure |
| Week 2b | Planned | ⏳ Open | Real-time monitoring and logging |
| Week 3 | Planned | ⏳ Open | H₁ validation on 5 games, final analysis |

---

## Initial Issues to Create

### Setup Issues

```markdown
# Issue 1: Week 2a Task 1 - Game Capture Configuration
**Assignee:** First contributor
**Milestone:** Week 2a
**Labels:** Week-2a, enhancement

Create `game_capture_config.json` per DEVELOPMENT.md § Phase 2a Task 1.
- [ ] JSON schema defined
- [ ] All 5 games specified
- [ ] Telemetry methods documented
- [ ] Tests pass
```

```markdown
# Issue 2: Week 2a Task 2 - Capture Profile Configuration
**Assignee:** First contributor
**Milestone:** Week 2a
**Labels:** Week-2a, enhancement

Create `capture_profile.yaml` per DEVELOPMENT.md § Phase 2a Task 2.
- [ ] YAML schema defined
- [ ] Thresholds match Week 1 locked values
- [ ] Sampling rate configured
- [ ] Tests pass
```

```markdown
# Issue 3: Week 2a Task 3 - State Vector Mapper
**Milestone:** Week 2a
**Labels:** Week-2a, enhancement

Create `state_vector_mapper.py` per DEVELOPMENT.md § Phase 2a Task 3.
Depends on: Issue 1
- [ ] StateVectorAssembler class implemented
- [ ] All 4 domain splits verified
- [ ] Tests pass
- [ ] Integration with data_pipeline validated
```

---

## File Changes Summary

All files have been updated to reference the correct GitHub repository:

✅ **README.md**
- Added GitHub repository URL
- Maintained professional tone

✅ **CONTRIBUTING.md**
- Updated issue/PR references
- Changed to GitHub Issues link

✅ **DEVELOPMENT.md**
- Added repository URL in header
- Updated GitHub references

✅ **REPO_STRUCTURE.md**
- Updated clone commands
- Changed all GitHub URLs to correct repository
- Updated badge URL

✅ **LICENSE**
- Added copyright attribution
- Added repository URL

✅ **.github/workflows/tests.yml**
- Added repository comment

✅ **_runtime/README.md**
- Updated documentation links
- Added GitHub Issues reference

---

## Pre-Push Checklist

Before pushing to GitHub for the first time:

- [x] All markdown links verified and working
- [x] LICENSE file properly formatted
- [x] .gitignore correctly configured
- [x] No sensitive data in commits
- [x] README.md has correct project description
- [x] CONTRIBUTING.md is clear
- [x] DEVELOPMENT.md is current
- [x] Week 1 code passes all 3 tests

---

## After Repository Push

1. **Verify GitHub Actions**
   - Check https://github.com/Dedoc-9/DEEQN64/actions
   - Confirm all tests pass across all platforms

2. **Configure Repository Settings**
   - Set default branch to `main`
   - Enable branch protection rules
   - Add issue labels
   - Create milestones
   - Add topics/tags

3. **Create Initial Issues**
   - Week 2a Tasks 1-5 as GitHub Issues
   - Set appropriate labels and milestones
   - Assign reviewers if known

4. **Announce Project**
   - Share repository publicly
   - Invite contributors
   - Document on project website

---

## Maintenance Workflow

### For New PRs

1. **Automatic (GitHub Actions):**
   - Tests run on all platforms/Python versions
   - Status check blocks merge if tests fail

2. **Manual (Maintainers):**
   - Review code against CONTRIBUTING.md standards
   - Verify documentation updated
   - Check for new test coverage
   - Approve and merge

### For Releases

1. Create release tag: `v1.0.0`, `v1.1.0`, etc.
2. Update version in code/docs
3. Create GitHub Release with changelog
4. Announce on project channels

### For Issues

1. **Triage:** Label, assign, milestone
2. **Respond:** Comment within 48 hours
3. **Resolve:** Link to PR when fixed
4. **Close:** After PR merges

---

## Common Git Workflows

### Creating a Feature Branch

```bash
# Clone the repository
git clone https://github.com/Dedoc-9/DEEQN64.git
cd DEEQN64

# Create and checkout feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Descriptive commit message"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Syncing with Main Branch

```bash
git fetch origin
git rebase origin/main
git push origin feature/your-feature-name -f
```

---

## Documentation References

- **Main README:** `README.md`
- **Contributing:** `CONTRIBUTING.md`
- **Development Plan:** `DEVELOPMENT.md`
- **Repository Guide:** `REPO_STRUCTURE.md`
- **Runtime Usage:** `_runtime/README.md`

---

## GitHub URLs

**Repository:** https://github.com/Dedoc-9/DEEQN64  
**Issues:** https://github.com/Dedoc-9/DEEQN64/issues  
**Pull Requests:** https://github.com/Dedoc-9/DEEQN64/pulls  
**Actions:** https://github.com/Dedoc-9/DEEQN64/actions  
**Settings:** https://github.com/Dedoc-9/DEEQN64/settings  

---

## Support

For questions about the GitHub setup:
1. Review this document
2. Check REPO_STRUCTURE.md
3. Consult CONTRIBUTING.md for code guidelines
4. Open an issue if something is unclear

---

**Repository Ready for Deployment ✅**  
**Status:** All files configured for GitHub  
**License:** AGPL-3.0  
**First Push:** Ready
