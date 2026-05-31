# DEEQN64 Public Repository Structure

**Repository:** https://github.com/Dedoc-9/DEEQN64

This document describes the organization of the Q64 GitHub repository for public distribution.

---

## Directory Layout

```
DEEQN64/
│
├── README.md                          Main project documentation
├── LICENSE                            AGPL-3.0 license text
├── CONTRIBUTING.md                    Contribution guidelines
├── DEVELOPMENT.md                     Development roadmap & schedule
├── REPO_STRUCTURE.md                  This file
│
├── .gitignore                         Git ignore patterns
├── .github/
│   └── workflows/
│       └── tests.yml                  GitHub Actions CI/CD
│
├── _runtime/                          Week 1 Reference Implementation
│   ├── README.md                      Usage guide & examples
│   ├── requirements.txt               Python dependencies
│   ├── q64_stratified_engine.py       Core Q64 operator (344 lines)
│   └── q64_reference_test.py          Unit tests (236 lines)
│
├── refined_protocol/                  Specification & Governance (Read-Only)
│   ├── Q64_MATHEMATICAL_FOUNDATIONS.md (Operator definition, proofs)
│   ├── Q64_GOVERNANCE_KERNEL_FINAL.md  (Normative rules, lifecycle)
│   ├── Q64_EXECUTION_LAYER_SPEC.md     (Operational mechanics)
│   └── Q64_KERNEL_BRIDGE.md            (Mapping reference)
│
└── _archive/                          Historical Documentation (Reference)
    ├── CONSOLIDATION_NOTES.md         (Why docs were consolidated)
    └── (original planning docs)
```

---

## File Purposes

### Root Documentation

| File | Purpose | Read When |
|------|---------|-----------|
| `README.md` | Project overview, quick start, core concepts | First time here |
| `LICENSE` | AGPL-3.0 license terms | Legal/compliance check |
| `CONTRIBUTING.md` | How to contribute, code standards, PR process | Before submitting PR |
| `DEVELOPMENT.md` | Week-by-week roadmap, task breakdown, timelines | Planning development work |
| `REPO_STRUCTURE.md` | This file — repository organization | Understanding structure |

### Implementation (_runtime/)

| File | Purpose |
|------|---------|
| `q64_stratified_engine.py` | Core Q64 operator—two classes (Q64DomainEngine, Q64StratifiedEngine) |
| `q64_reference_test.py` | Unit tests (3 test suites, all passing) |
| `requirements.txt` | Python package dependencies (6 packages) |
| `README.md` | How to run tests, integration examples, troubleshooting |

### Specification (refined_protocol/)

**These are read-only reference documents.** Do not edit without careful consideration.

| File | Content |
|------|---------|
| `Q64_MATHEMATICAL_FOUNDATIONS.md` | Operator T definition, convergence predicate, Lyapunov analysis, proofs |
| `Q64_GOVERNANCE_KERNEL_FINAL.md` | Normative rules, phase lifecycle, guard evaluation, immutable binding |
| `Q64_EXECUTION_LAYER_SPEC.md` | Operational mechanics, state persistence, hash binding, CI compiler |
| `Q64_KERNEL_BRIDGE.md` | Mapping semantics, referential clarity, bridging theory to code |

### CI/CD (.github/workflows/)

| File | Purpose |
|------|---------|
| `tests.yml` | GitHub Actions workflow—runs unit tests on push/PR across OS and Python versions |

---

## Public vs. Internal Structure

### Public (Included in GitHub)
- ✅ README.md — Project overview
- ✅ LICENSE — Legal terms
- ✅ CONTRIBUTING.md — How to contribute
- ✅ DEVELOPMENT.md — Roadmap
- ✅ _runtime/ — Validated Week 1 code
- ✅ refined_protocol/ — Specifications
- ✅ .github/workflows/ — CI/CD

### Internal (Not Included, or Archived)
- 📁 _archive/ — Consolidation history (included, for reference)
- 📁 MANIFEST.md — Internal navigation (included, for reference)
- 📝 Q64_IMPLEMENTATION_PLAN.md — Internal task tracking (not needed publicly; use DEVELOPMENT.md instead)

---

## Getting Started for Contributors

### 1. Fork & Clone
```bash
git clone https://github.com/Dedoc-9/DEEQN64.git
cd DEEQN64
```

### 2. Install & Test
```bash
pip install -r _runtime/requirements.txt
cd _runtime
python q64_reference_test.py  # Should see 3/3 PASS
```

### 3. Read Documentation
- **Quick overview:** README.md (top-level)
- **What to build:** DEVELOPMENT.md (§ Phase 2a)
- **How to contribute:** CONTRIBUTING.md
- **Understand the math:** refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md

### 4. Start Contributing
- Pick an issue from GitHub Issues
- Create a feature branch: `git checkout -b feature/your-name`
- Submit a PR with clear description

---

## Key Design Principles

### One Source of Truth
- **Master plan:** DEVELOPMENT.md (public, non-implementation)
- **Specs:** refined_protocol/ files (authority, not duplicated)
- **Code:** _runtime/ (implementation)

### No Embedded Rhetoric
- Documentation avoids internal explanations
- Focuses on what, why, and how—not process notes
- Professional, suitable for external audience

### Locked Parameters
All Week 1 decisions are frozen in:
- DEVELOPMENT.md § "Locked Parameters"
- _runtime/q64_stratified_engine.py defaults
- _runtime/q64_reference_test.py synthetic data setup

Changes require justification and re-validation.

### Clear Dependency Graph
DEVELOPMENT.md § "Dependency Graph" shows:
- Phase 1 (complete) → Phase 2a → Phase 2b → Phase 3
- Per-task dependencies
- Blocked tasks and prerequisites

---

## Typical Workflows

### "I want to run Week 1 tests"
1. `cd _runtime`
2. `pip install -r requirements.txt`
3. `python q64_reference_test.py`

### "I want to understand the Q64 operator"
1. Read README.md § "Core Concept"
2. Read refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md § "Operator Definition"
3. Read _runtime/q64_stratified_engine.py source code

### "I want to contribute"
1. Read CONTRIBUTING.md
2. Review DEVELOPMENT.md for open tasks
3. Open an issue to discuss
4. Submit a PR

### "I'm lost"
1. Check DEVELOPMENT.md § "Dependency Graph"
2. Find your task in the timeline
3. See what it depends on and what depends on it

---

## Hosting on GitHub

### Repository Settings Recommended

**Branch Protection (main):**
- Require pull request reviews (1+ approver)
- Require status checks to pass (tests.yml)
- Dismiss stale PR approvals
- Require branches up to date before merge

**Labels:**
- `bug` — Defect report
- `enhancement` — Feature request
- `documentation` — Docs only
- `help-wanted` — Looking for contributors
- `question` — User question

**Milestones:**
- Week 1 ✅ (closed)
- Week 2a (in progress)
- Week 2b (planned)
- Week 3 (planned)

---

## Continuous Integration

GitHub Actions workflow (`.github/workflows/tests.yml`):

**Triggers on:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Tests across:**
- OS: Ubuntu, macOS, Windows
- Python: 3.10, 3.11, 3.12, 3.13, 3.14

**Runs:**
- Install dependencies
- Execute `q64_reference_test.py`
- Execute `q64_stratified_engine.py` demo

**Status badge in README:**
```markdown
![Tests](https://github.com/Dedoc-9/DEEQN64/workflows/Tests/badge.svg)
```

---

## Release Strategy

### Version Format: MAJOR.MINOR.PATCH

**1.0.0 (Week 1 Complete)**
- Initial public release
- Week 1 validation complete
- Reference implementation validated

**1.1.0 (After Week 2 Complete)**
- Week 2a infrastructure
- Week 2b runtime
- Real game data integration

**1.2.0 (After Week 3 Complete)**
- H₁ validation on 5 games
- Analysis tools
- Full telemetry pipeline

**2.0.0 (Hardware Mapping)**
- New domain additions
- Performance optimizations
- Breaking API changes (if needed)

### Release Checklist
- [ ] All tests pass
- [ ] DEVELOPMENT.md updated with completion date
- [ ] README.md updated with new features
- [ ] Tag released version in Git
- [ ] Create GitHub Release with notes

---

## Maintenance

### Code Review Standards
- At least 1 maintainer approval required
- All tests must pass
- No merge conflicts
- Documentation updated
- Commit messages are clear

### Issue Triage
- Respond to new issues within 48 hours
- Label appropriately
- Assign to milestone
- Close resolved issues with reference to PR

### Security
- No sensitive data in commits
- Follow CONTRIBUTING.md guidelines
- Report security issues privately to maintainers

---

## Future Expansion

As the project grows, consider:

1. **Additional directories:**
   - `examples/` — Example notebooks and scripts
   - `benchmarks/` — Performance benchmarks
   - `docs/` — Sphinx documentation
   - `tools/` — Utility scripts

2. **New branches:**
   - `main` — Stable releases
   - `develop` — Integration branch
   - `feature/*` — Feature branches (auto-deleted after merge)

3. **Package distribution:**
   - PyPI package (`pip install q64`)
   - Conda package
   - Docker image

4. **Expanded documentation:**
   - Sphinx auto-generated API docs
   - Jupyter notebooks with tutorials
   - Video tutorials

---

## Quick Reference

| Task | File | Section |
|------|------|---------|
| Understand project | README.md | Overview, Getting Started |
| See development plan | DEVELOPMENT.md | Phase descriptions, timeline |
| Contribute code | CONTRIBUTING.md | Code standards, PR process |
| Run tests | _runtime/README.md | Quick Start |
| Understand math | refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md | All sections |
| Check governance | refined_protocol/Q64_GOVERNANCE_KERNEL_FINAL.md | All sections |

---

## Archive & Historical Docs

The `_archive/` folder contains:
- Original consolidation notes
- Superseded planning documents
- Historical context for Week 1→2 transition

These are for reference and understanding project evolution. **Do not use for active development.**

---

## Next Steps

1. **Configure GitHub repository** with settings recommended above
2. **Push to GitHub** under AGPL-3.0 license
3. **Enable GitHub Actions** for CI/CD
4. **Announce** the public repository
5. **Begin Week 2a** with community open to contributions

---

**Repository Status:** Week 1 complete, ready for public GitHub  
**Maintained by:** Q64 Core Team  
**License:** GNU Affero General Public License v3.0
