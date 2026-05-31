# Q64 Reference Implementation

This directory contains the Week 1 reference implementation of Q64—the stratified spectral stability operator validated on synthetic data.

**Status:** Week 1 validation complete. All tests passing (3/3).

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- numpy ≥1.24.0 — Numerical computing
- scipy ≥1.10.0 — Scientific algorithms
- h5py ≥3.8.0 — HDF5 data storage
- pandas ≥2.0.0 — Data structures
- matplotlib ≥3.7.0 — Plotting
- pyyaml ≥6.0 — Configuration files

### 2. Run Unit Tests

```bash
python q64_reference_test.py
```

**Expected output:**
```
======================================================================
 Q64 REFERENCE IMPLEMENTATION: UNIT TESTS
======================================================================

======================================================================
TEST 1: INITIALIZATION
======================================================================
✓ Engine initialized with 4 domains
  - input (N=10, k=3)
  - physics (N=6, k=5)
  - system (N=12, k=3)
  - rendering (N=36, k=10)

======================================================================
TEST 2: SYNTHETIC CONVERGENCE
======================================================================
Generating 500 frames of synthetic stratified telemetry...
...
✓ Synthetic convergence test PASSED (4 domains converged)

======================================================================
TEST 3: H₁ GATE EVALUATION
======================================================================
...
✓ H₁ gate evaluation test PASSED

======================================================================
 TEST SUMMARY
======================================================================
✓ Initialization                            PASS
✓ Synthetic Convergence                     PASS
✓ H₁ Gate Evaluation                        PASS

3/3 tests passed

✓ ALL TESTS PASSED - Week 1 Validation Complete
```

### 3. Run Engine Demo

```bash
python q64_stratified_engine.py
```

This generates 1000 frames of synthetic 64-dimensional telemetry and evaluates Q64 convergence across all 4 domains. Output includes per-domain stability metrics and H₁ gate evaluation.

---

## Core Components

### `q64_stratified_engine.py`

Implementation of the Q64 stratified spectral operator.

#### `Q64DomainEngine`

Single-domain spectral operator:

```python
from q64_stratified_engine import Q64DomainEngine
import numpy as np

# Initialize for a specific domain
engine = Q64DomainEngine(
    N=10,          # Dimension of domain
    k=3,           # Max rank truncation
    name="input",  # Domain identifier
    w=20,          # Sliding window size
    tau=0.4,       # Rank threshold
    epsilon_R=1e-2, # Residual threshold
    delta_L=0.2    # Drift threshold
)

# Update with state vector
s_t = np.random.randn(10)
metrics = engine.update(s_t)

# Check convergence
print(f"c_t (converged): {metrics.c_t}")
print(f"Rank: {metrics.rank}")
print(f"Residual R_t: {metrics.R_t:.6f}")
print(f"Drift L_t: {metrics.L_t:.6f}")
```

#### `Q64StratifiedEngine`

Multi-domain orchestrator:

```python
from q64_stratified_engine import Q64StratifiedEngine
import numpy as np

# Initialize
engine = Q64StratifiedEngine()

# Update with 64-dimensional state vector
s_t = np.random.randn(64)
results = engine.update(s_t)

# Per-domain convergence status
for domain, metrics in results.items():
    print(f"{domain}: c_t={metrics.c_t}, rank={metrics.rank}")

# Evaluate H₁ gate (needs ≥3 of 4 domains converged)
gate_passes, detail = engine.h1_gate_evaluation()
print(f"H₁ gate: {'PASS' if gate_passes else 'FAIL'}")
print(f"Domains passing: {detail['domains_passing']}/4")
```

### `q64_reference_test.py`

Unit tests validating core functionality:

1. **Initialization:** All 4 domains created with correct dimensions
2. **Synthetic Convergence:** Domains converge on low-rank synthetic data (500+ frames)
3. **H₁ Gate:** Gate logic correctly evaluates ≥3 domains passing (1000 frames)

---

## State Vector Format

Q64 accepts 64-dimensional heterogeneous state vectors with domain stratification:

| Domain | Dimensions | k | Purpose |
|--------|-----------|---|---------|
| Input | 0–9 (10 dims) | 3 | Controller/user input state |
| Physics | 10–15 (6 dims) | 5 | Position, velocity, forces |
| System | 16–27 (12 dims) | 3 | CPU, GPU, thermal metrics |
| Rendering | 28–63 (36 dims) | 10 | Graphics pipeline, memory |

**Assembly example:**
```python
import numpy as np

# Gather per-domain telemetry
input_state = np.array([...])      # (10,)
physics_state = np.array([...])    # (6,)
system_metrics = np.array([...])   # (12,)
render_metrics = np.array([...])   # (36,)

# Concatenate into 64-dim vector
s_t = np.concatenate([
    input_state,      # dims 0-9
    physics_state,    # dims 10-15
    system_metrics,   # dims 16-27
    render_metrics    # dims 28-63
])

assert s_t.shape == (64,)
```

---

## Week 1 Results (Reference)

| Metric | Result | Status |
|--------|--------|--------|
| Initialization test | All 4 domains created | ✅ PASS |
| Synthetic convergence (500 frames) | All 4 domains converge | ✅ PASS |
| H₁ gate (1000 frames) | ≥3 domains pass thresholds | ✅ PASS |
| Domain stability (synthetic) | Input 80%+, Physics 70%+, System 60%+, Rendering 40%+ | ✅ PASS |

**Thresholds locked (Week 1):**
- ε_R (residual): 1e-2
- δ_L (drift): 0.2
- τ (rank threshold): 0.4
- w (window size): 20 frames

---

## Troubleshooting

### ImportError: No module named numpy

```bash
pip install -r requirements.txt
```

### ValueError: Expected 64-dim state, got N

State vectors must be exactly 64 dimensions. Verify your assembly:
```python
s_t = np.concatenate([input_state, physics_state, system_metrics, render_metrics])
assert len(s_t) == 64, f"Expected 64 dims, got {len(s_t)}"
```

### Convergence never triggers

Week 1 tests use synthetic data with carefully constructed low-rank structure (manifold hypothesis). Real telemetry may have:
- Higher noise
- Different manifold dimension
- Non-stationary dynamics

Thresholds are locked; don't adjust them without re-validation.

---

## Integration with Phase 2

In Week 2, Q64StratifiedEngine is integrated into a full telemetry pipeline:

```python
from q64_stratified_engine import Q64StratifiedEngine
from state_vector_mapper import StateVectorAssembler
from hardware_monitor_adapter import OpenHardwareMonitorAdapter

# Initialize components
engine = Q64StratifiedEngine()
mapper = StateVectorAssembler(config)
hardware = OpenHardwareMonitorAdapter()

# Streaming loop (pseudocode)
for frame in range(num_frames):
    # Acquire telemetry
    controller_state = acquire_controller()
    physics_state = acquire_physics()
    system_metrics = hardware.poll()
    render_data = acquire_render()
    
    # Assemble 64-dim vector
    s_t = mapper.assemble(
        controller_state, physics_state, 
        system_metrics, render_data
    )
    
    # Run Q64 update
    results = engine.update(s_t)
    
    # Log metrics
    for domain, metrics in results.items():
        logger.write(domain, metrics)

# Evaluate H₁ gate at end
gate_passes, detail = engine.h1_gate_evaluation()
```

---

## Running with Different Configurations

To test with custom parameters:

```python
from q64_stratified_engine import Q64DomainEngine

# Non-default configuration
engine = Q64DomainEngine(
    N=20, k=5, name="custom",
    w=30,        # Larger window
    tau=0.5,     # Higher rank threshold (more selective)
    epsilon_R=5e-3,  # Tighter residual bound
    delta_L=0.1      # Tighter drift bound
)

# Then run updates as normal
results = engine.update(s_t)
```

**Note:** Changes to thresholds are not recommended without re-validation on synthetic data. See [DEVELOPMENT.md](../DEVELOPMENT.md) for validation procedures.

---

## References

- [DEEQN64 README](../README.md) — Project overview
- [DEVELOPMENT.md](../DEVELOPMENT.md) — Week-by-week roadmap
- [Q64_MATHEMATICAL_FOUNDATIONS.md](../refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md) — Mathematical specification

---

## Support

For issues, questions, or contributions:

1. Check [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Review [DEVELOPMENT.md](../DEVELOPMENT.md) for context
3. Open an issue at https://github.com/Dedoc-9/DEEQN64/issues with reproduction steps and environment info

---

**Status:** Week 1 complete ✅  
**Next:** Week 2a infrastructure (game capture configuration)
