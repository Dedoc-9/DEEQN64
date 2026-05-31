# DEEQN64: Spectral Stability Certification Engine

A reference implementation of Q64, a nonlinear stochastic dynamical system for real-time structural certification of complex systems through spectral stability analysis.

**Repository:** https://github.com/Dedoc-9/DEEQN64  
**Status:** Week 1 validation complete. Week 2+ development in progress.

**Contact:** BigDilly95@gmail.com (Author: Daniel J. Dillberg)

---

## Overview

Q64 certifies structural stability in heterogeneous systems (games, financial systems, medical devices, etc.) by:

1. **Stratifying** the system state into independent spectral domains
2. **Detecting convergence** of low-rank manifold representations
3. **Evaluating stability** through bounded residual, rank stability, and drift constraints
4. **Binding results** to immutable hash-verified state records

The system does not claim to find the ground truth of a system's structure—it certifies whether a *chosen* structural model remains valid under drift.

---

## Core Concept

### Operator Ψ_t = T(Ψ_{t-1}, s_t)

The Q64 operator transforms state tuples across 10 computational layers:

```
Input → Preprocessing → Gram → Eigendecomposition → Rank Estimation 
       → Projection → Residual → Drift Audit → Convergence Predicate → Hash Binding
```

**Convergence predicate c_t** triggers when three conditions hold simultaneously:
- Residual norm: R_t < ε_R
- Rank stability: estimated rank within ±1 of median over window
- Drift bounded: |L_t − L_{t−1}| < δ_L · L_t

Once triggered, c_t indicates the system has converged to a stable low-rank representation.

---

## Architecture

### Domain Stratification

The system accepts 64-dimensional heterogeneous state vectors and partitions them into four independent domains:

| Domain | Dimensions | Rank (k) | Purpose |
|--------|-----------|----------|---------|
| Input | 0–9 (10 dims) | 3 | Controller/user input state |
| Physics | 10–15 (6 dims) | 5 | Position, velocity, forces |
| System | 16–27 (12 dims) | 3 | CPU, GPU, thermal metrics |
| Rendering | 28–63 (36 dims) | 10 | Graphics pipeline, memory, throughput |

Each domain runs an independent spectral operator with domain-specific rank constraints.

### Convergence Evaluation (H₁ Gate)

The system passes H₁ validation when **≥3 of 4 domains** achieve:
- **Input:** ≥80% time converged
- **Physics:** ≥70% time converged
- **System:** ≥60% time converged
- **Rendering:** ≥40% time converged

This mixed-threshold approach reflects domain complexity: input is most constrained, rendering most variable.

---

## Getting Started

### Installation

```bash
pip install -r _runtime/requirements.txt
```

### Run Tests

```bash
cd _runtime
python q64_reference_test.py
```

**Expected output:**
```
✓ TEST 1: INITIALIZATION
✓ TEST 2: SYNTHETIC CONVERGENCE
✓ TEST 3: H₁ GATE EVALUATION

✓ ALL TESTS PASSED - Week 1 Validation Complete
3/3 tests passed
```

### Run Engine Demo

```bash
cd _runtime
python q64_stratified_engine.py
```

This generates 1000 frames of synthetic stratified telemetry and evaluates stability across all 4 domains.

---

## Project Structure

```
├── README.md                     (this file)
├── LICENSE                       (AGPL-3.0)
├── DEVELOPMENT.md                (week-by-week development plan)
├── CONTRIBUTING.md               (contribution guidelines)
│
├── _runtime/                     (validated Week 1 implementation)
│   ├── q64_stratified_engine.py  (core operator)
│   ├── q64_reference_test.py     (unit tests)
│   ├── requirements.txt          (dependencies)
│   └── README.md                 (usage guide)
│
├── _archive/                     (historical consolidation notes)
│
└── refined_protocol/             (specification documents)
    ├── Q64_MATHEMATICAL_FOUNDATIONS.md
    ├── Q64_GOVERNANCE_KERNEL_FINAL.md
    ├── Q64_EXECUTION_LAYER_SPEC.md
    └── Q64_KERNEL_BRIDGE.md
```

---

## Core Components

### `Q64StratifiedEngine`

Multi-domain orchestrator that:
- Accepts 64-dimensional heterogeneous state vectors
- Splits into 4 independent domains
- Runs spectral analysis on each domain independently
- Returns per-domain convergence metrics
- Evaluates H₁ gate (≥3 domains pass)

```python
from _runtime.q64_stratified_engine import Q64StratifiedEngine

engine = Q64StratifiedEngine()
metrics = engine.update(s_t)  # s_t is (64,)

# Check convergence for each domain
for domain, metric in metrics.items():
    print(f"{domain}: c_t={metric.c_t}, rank={metric.rank}")

# Evaluate H₁ gate
gate_passes, detail = engine.h1_gate_evaluation()
```

### `Q64DomainEngine`

Single-domain spectral operator with:
- Sliding window Gramian computation
- Eigendecomposition and rank estimation
- Residual projection and drift tracking
- Convergence predicate evaluation

---

## Thresholds (Week 1 Locked)

These parameters were empirically tuned on synthetic data and are frozen for Week 2:

```
Residual threshold (ε_R):    1e-2
Drift threshold (δ_L):        0.2
Rank threshold (τ):           0.4
Window size (w):              20 frames
```

Changing these requires re-validation against synthetic data and justification in development notes.

---

## Development Roadmap

### Week 1 ✅ (Complete)
- [x] Reference engine specification
- [x] Stratified implementation
- [x] Unit tests (3/3 pass)
- [x] Threshold tuning

### Week 2a (In Progress)
- [ ] Game capture configuration
- [ ] State vector assembly
- [ ] Hardware monitor adapter
- [ ] Data pipeline

### Week 2b (Planned)
- [ ] Real-time monitor
- [ ] Game launcher wrapper
- [ ] Telemetry logger (HDF5/CSV)
- [ ] Convergence visualizer

### Week 3 (Planned)
- [ ] Forensic autopsy
- [ ] H₁ gate evaluation
- [ ] Spectral report generator
- [ ] 5-game validation (Valorant, Portal 2, Celeste, Minecraft, Elden Ring)

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed task breakdown.

---

## Mathematical Foundation

### Operator Definition

State tuple: (μₜ, Zₜ, Sₜ, Wₜ) where:
- **μₜ:** Primary spectral projection
- **Zₜ:** Full-rank covariance (observation space)
- **Sₜ:** Residual accumulation (EMA)
- **Wₜ:** Auxiliary state (rank history, drift tracking)

**Transition law:**
```
μ_{t+1} = Lτ(Zₜ)              [spectral truncation]
Z_{t+1} = Bτ(s_t, Zₜ)        [Gramian update via sliding window]
S_{t+1} = αS_t + (1−α)G_t    [residual EMA accumulation]
W_{t+1} = Rτ(Z_{t+1}, μ_{t+1})  [auxiliary state evolution]
H_t = HASH(μₜ ⊕ Zₜ ⊕ Sₜ ⊕ Wₜ ⊕ version)  [irreversible binding]
```

### Convergence Predicate

Three simultaneous conditions (AND logic):

1. **Residual bound:** ||Zₜ − μₜZ^H_tμₜ||_F < ε_R
2. **Rank stability:** rank(·) within ±1 of median over window
3. **Drift bound:** |L_t − L_{t−1}| < δ_L · L_t

For full mathematical treatment, see [Q64_MATHEMATICAL_FOUNDATIONS.md](refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md).

---

## Testing

### Unit Tests

Three test suites validate core functionality:

1. **Initialization:** 4 domains created with correct dimensions
2. **Synthetic Convergence:** All domains converge on low-rank synthetic data
3. **H₁ Gate:** Gate logic correctly identifies ≥3 passing domains

Run all tests:
```bash
cd _runtime
python q64_reference_test.py
```

### Test Data

Tests use synthetic 64-dimensional telemetry with per-domain low-rank structure:
- Domain-specific orthonormal bases (QR-decomposed)
- Smooth latent code perturbation (maintains manifold coherence)
- 2% measurement noise

---

## Contributing

Contributions are welcome under AGPL-3.0. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Test requirements
- Pull request process
- Licensing agreement

Key constraints for contributors:
- All thresholds changes require synthetic data re-validation
- Mathematical changes require peer review against specification
- New domains must define k (rank bound) and domain semantics

---

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](LICENSE) for details. In summary:
- You may use, modify, and distribute this software freely
- If you distribute modified versions, you must provide source code
- If you deploy this in a service, users of that service can request your source modifications

---

## References

### Specification Documents
- [Q64 Mathematical Foundations](refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md) — Operator definition, proofs, Lyapunov analysis
- [Q64 Governance Kernel](refined_protocol/Q64_GOVERNANCE_KERNEL_FINAL.md) — Normative rules and lifecycle
- [Q64 Execution Layer](refined_protocol/Q64_EXECUTION_LAYER_SPEC.md) — Operational mechanics and state persistence
- [Q64 Kernel Bridge](refined_protocol/Q64_KERNEL_BRIDGE.md) — Mapping and referential semantics

### Project Documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) — Week-by-week development plan
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines

---

## Authors

Q64 is developed as a structural assurance infrastructure for real-time system certification.

---

## Acknowledgments

This implementation draws on spectral methods, adaptive estimation, and stability theory from control systems and dynamical systems analysis.

---

## Status & Support

- **Current Version:** 1.0 (Week 1 complete)
- **Python:** 3.14+ required
- **Dependencies:** numpy, scipy, h5py, pandas, matplotlib, pyyaml

For issues, questions, or contributions: See [CONTRIBUTING.md](CONTRIBUTING.md).

