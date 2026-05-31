# SYSTEM_LAYOUT_SPEC: DEEQN64 Repository Structure

**Status:** Public GitHub repository  
**Version:** 1.0.0 (Week 1 Complete)  
**Repository:** https://github.com/Dedoc-9/DEEQN64  
**License:** AGPL-3.0

---

## Purpose

Repository structure reflects the Q64 stratified spectral engine architecture and enables clear separation between specification, implementation, and validation.

This spec defines:
- What belongs in each folder
- File organization principles
- Documentation boundaries
- Code organization for Python + Rust hybrid project

---

## Repository Layers

### Layer 1: Documentation & Governance

**Purpose:** Authority and guidance  
**Location:** `/` (root)

**Contents:**
```
README.md                    — Project overview & quick start
LICENSE                      — AGPL-3.0 license
CONTRIBUTING.md              — Contribution guidelines & code standards
DEVELOPMENT.md               — Week-by-week development roadmap
REPO_STRUCTURE.md            — Repository organization guide
GITHUB_SETUP.md              — GitHub configuration guide
BUILD_AND_CI_SUMMARY.md      — Build configuration details
.gitignore                   — Git ignore patterns
```

**Rules:**
- ✅ Professional, public-facing documentation
- ✅ No internal notes or personal paths
- ✅ Clear contribution guidelines
- ✅ Transparent development plan
- ❌ No internal process notes
- ❌ No local development instructions

---

### Layer 2: Configuration

**Purpose:** Build and project configuration  
**Location:** `/`

**Contents:**
```
pyproject.toml               — Python project configuration (setuptools, dev tools)
Cargo.toml                   — Rust workspace configuration (cdylib + rlib)
build.rs                     — Rust build script (optimization, Python bindings)
.cargo/config.toml           — Cargo build profiles and aliases
```

**Rules:**
- ✅ Single source of truth for dependencies
- ✅ Feature gates for optional components
- ✅ Build profile optimization
- ✅ Cross-platform compatibility
- ❌ No version duplication

---

### Layer 3: Python Runtime

**Purpose:** Q64 reference implementation (Week 1 validated)  
**Location:** `/_runtime/`

**Contents:**
```
_runtime/
  README.md                  — Python usage guide & examples
  requirements.txt           — Python dependencies (6 packages)
  q64_stratified_engine.py   — Core Q64 stratified engine (344 lines)
  q64_reference_test.py      — Unit tests (3/3 passing)
```

**Rules:**
- ✅ Week 1 validated on synthetic data
- ✅ All tests passing (3/3)
- ✅ Thresholds locked: ε_R=1e-2, δ_L=0.2, τ=0.4, w=20
- ✅ Ready for Week 2 game integration
- ❌ No experimental modifications without re-validation
- ❌ No threshold changes without testing

**Dependency Rules:**
```
_runtime → numpy, scipy      (numerical computing, allowed)
_runtime → h5py, pandas      (data storage, allowed)
_runtime → matplotlib, yaml  (visualization, configuration, allowed)
_runtime → stdlib            (allowed)

Forbidden:
  _runtime → external ML libraries (prevents drift)
  _runtime → modified thresholds (must re-validate)
```

---

### Layer 4: Rust Implementation

**Purpose:** High-performance spectral engine + Python FFI  
**Location:** `/src/`

**Contents:**
```
src/
  lib.rs                     — Main library with PyO3 FFI bindings (cdylib)
  engine.rs                  — Q64DomainEngine and Q64StratifiedEngine
  operator.rs                — Core Q64 operator definition
  error.rs                   — Error types
  metrics.rs                 — Convergence metrics & H₁ evaluation
```

**Rules:**
- ✅ Zero unsafe code (`#![forbid(unsafe_code)]`)
- ✅ PyO3 Python bindings (feature-gated)
- ✅ Full test coverage
- ✅ Serialization support (Serde)
- ❌ No direct game integration (that's in Python layer)
- ❌ No file I/O (library only)

**Dependency Rules:**
```
src → ndarray, scipy         (numerical computing)
src → serde, bincode         (serialization)
src → pyo3                   (Python bindings, optional)
src → stdlib                 (allowed)

Forbidden:
  src → game-specific libraries (portability)
  src → external ML frameworks (scope creep)
```

---

### Layer 5: Specification & Governance

**Purpose:** Authoritative specifications and decision records  
**Location:** `/refined_protocol/`

**Contents:**
```
refined_protocol/
  Q64_MATHEMATICAL_FOUNDATIONS.md         — Operator definition & proofs
  Q64_GOVERNANCE_KERNEL_FINAL.md          — Normative rules & lifecycle
  Q64_EXECUTION_LAYER_SPEC.md             — Operational mechanics
  Q64_KERNEL_BRIDGE.md                    — Mapping reference
  ADR-001-PRODUCTION-ARCHITECTURE-SELECTION.md  — Architecture decision
  SYSTEM_LAYOUT_SPEC.md                   — Governance structure (original)
  DEPLOYMENT_LAYOUT.md                    — Deployment sequence (original)
```

**Rules:**
- ✅ Read-only reference material
- ✅ Explains architecture and design decisions
- ✅ Authoritative for governance questions
- ❌ Never imported by code
- ❌ Never modified (use new ADRs for changes)
- ❌ No implementation details (that's in code)

---

### Layer 6: GitHub Actions CI/CD

**Purpose:** Continuous integration and release automation  
**Location:** `/.github/workflows/`

**Contents:**
```
.github/workflows/
  tests.yml                  — Unit tests (3 OS × 5 Python versions)
  quality.yml                — Code quality (lint, type-check, security)
  release.yml                — PyPI release automation on version tags
```

**Rules:**
- ✅ Tests required for merge to main
- ✅ Quality checks informational (don't block)
- ✅ Release automation on `v*.*.*` tags
- ✅ Coverage tracking via Codecov
- ❌ No manual deployment steps

---

### Layer 7: Archive

**Purpose:** Historical documentation (read-only)  
**Location:** `/_archive/`

**Contents:**
```
_archive/
  CONSOLIDATION_NOTES.md     — Week 1 consolidation history
```

**Rules:**
- ✅ Reference for understanding project evolution
- ❌ Never modified
- ❌ Never imported by code

---

## Q64 Stratified Engine Specification

### Domain Configuration (Locked, Week 1)

**4 Independent Domains:**

| Domain | Dims | k | Purpose | N |
|--------|------|---|---------|---|
| Input | 0-9 (10) | 3 | Controller/user input | 10 |
| Physics | 10-15 (6) | 5 | Position, velocity, forces | 6 |
| System | 16-27 (12) | 3 | CPU, GPU, thermal | 12 |
| Rendering | 28-63 (36) | 10 | Graphics, memory, throughput | 36 |
| **Total** | **64** | — | Heterogeneous state vector | **64** |

### Convergence Predicate c_t (Locked)

**Three conditions (AND logic):**
1. **Residual bound:** R_t < ε_R (1e-2)
2. **Rank stability:** estimated rank within ±1 of median
3. **Drift bound:** |L_t − L_{t−1}| < δ_L · L_t (0.2)

### H₁ Gate Evaluation (Locked)

**Success:** ≥3 of 4 domains pass thresholds

| Domain | Threshold | Rationale |
|--------|-----------|-----------|
| Input | 80% | Most constrained |
| Physics | 70% | Stable most of time |
| System | 60% | Can vary (thermal, power) |
| Rendering | 40% | Most complex |

---

## Development Timeline

### Phase 1: Week 1 ✅ (Complete)
- Reference engine validated on synthetic data
- All tests passing (3/3)
- Thresholds empirically tuned
- Ready for Week 2 infrastructure

### Phase 2a: Week 2 Infrastructure (TODO)
- Game capture configuration
- State vector assembly
- Hardware monitor adapter
- Data pipeline

### Phase 2b: Week 2 Runtime (Blocked on 2a)
- Real-time monitor
- Game launcher wrapper
- Telemetry logger
- Visualization (optional)

### Phase 3: Week 2-3 Analysis (Blocked on 2b)
- Forensic autopsy
- H₁ gate evaluation
- Report generation
- 5-game validation

---

## File Organization Principles

### Single Responsibility
Each file has one clear purpose:
- Code: implements functionality
- Tests: validate behavior
- Docs: explain design
- Config: builds projects

### No Duplication
- Specifications live in refined_protocol/
- Implementation references, not duplicates
- Tests contain truth, docs reference tests

### Cross-Platform
- No OS-specific paths
- No personal file references
- All paths relative or environment-based

### Public-Facing
- Professional documentation
- Clear contribution path
- Transparent development
- No internal process notes

---

## File Size & Scope Guidelines

| Component | Target Lines | Status |
|-----------|-------------|--------|
| q64_stratified_engine.py | <400 | ✅ 344 lines |
| q64_reference_test.py | <300 | ✅ 236 lines |
| src/engine.rs | <300 | ✅ 270 lines |
| src/lib.rs | <500 | ✅ 434 lines |
| README.md | <200 | ✅ Concise |
| DEVELOPMENT.md | <500 | ✅ Detailed roadmap |

---

## Dependency Graph

```
refined_protocol/          (Authority & Specs)
  ↓ (authorizes)
pyproject.toml, Cargo.toml (Build Configuration)
  ↓ (builds)
src/ + _runtime/           (Implementation)
  ↓ (runs)
.github/workflows/         (Validation)
  ↓ (produces)
GitHub Actions CI/CD       (Quality Gates)
  ↓ (enforces)
main branch (Protected)    (Production Ready)
```

---

## Success Criteria

**Code Quality:**
- ✅ Python: Black formatted, mypy passing, pytest 3/3
- ✅ Rust: No unsafe code, all tests pass, 100% coverage
- ✅ Docs: No personal paths, professional tone, links work

**Architecture:**
- ✅ Clear layer separation
- ✅ No circular dependencies
- ✅ Single source of truth for specs
- ✅ Public-facing structure

**Governance:**
- ✅ AGPL-3.0 licensed
- ✅ Contributing guidelines clear
- ✅ Development roadmap transparent
- ✅ CI/CD automated

---

**Status:** ✅ Complete for Week 1  
**Repository:** https://github.com/Dedoc-9/DEEQN64  
**License:** GNU Affero General Public License v3.0  
**Last Updated:** Week 1 Complete
