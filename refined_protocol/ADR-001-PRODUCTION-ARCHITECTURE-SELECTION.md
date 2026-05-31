# ADR-001: Production Architecture Selection

**Status:** Accepted  
**Date:** 2026-05-29  
**Decision Maker:** Architecture Review  
**Revision:** Final

---

## 1. Purpose

Close the architectural fork between dependency-matrix dynamics (v1.0.0) and empirical covariance stream (refined_protocol). Establish a clear promotion pathway for challenger architectures. Define governance requirements that apply to both paths. Enable production deployment of the empirical stream without blocking the dependency-matrix research track.

---

## 2. The Decision

```
Production Architecture:
  Empirical Covariance Stream
  (centered covariance → Gram matrix → entropy rank → persistence → transitions)

Research Architecture (Challenger):
  Dependency-Matrix Dynamics
  (MI estimation → spectral filtering → state dynamics → convergence)

Promotion Mechanism:
  Evidence-based (empirical)
  
Validation Gate:
  H₁ acceptance (PROTOCOL_V2_EMPIRICAL_FRAMEWORK.md)
```

---

## 3. Production Architecture: Empirical Covariance Stream

### Canonical Pipeline

```
Telemetry (7-dim: frame_time, gpu_load, cpu_load, temp, input_lag, power_draw, frame_count)
    ↓
Mean-centering (64-frame sliding window)
    ↓
Gram matrix: G_t = (1/w) Σ s̃_i s̃_i^T
    ↓
Eigendecomposition: λ₁ ≥ λ₂ ≥ ... ≥ λ₇
    ↓
Effective rank: r_eff = exp(-Σ p_i log(p_i)) where p_i = λ_i / Σλ_j
    ↓
Persistence analysis: regime duration, stable vs. transient classification
    ↓
Transition detection: rank jumps, unsupervised discovery
    ↓
Decision: H₀ (no structure) or H₁ (structure exists)
```

### Advantages (Why This Is Default)

- **Minimal assumptions:** Centered covariance is close to observable data
- **Deterministic:** No parameter adaptation, no hidden state
- **Auditable:** Each stage has clear meaning (variance concentration, not information geometry)
- **Bounded:** No expansion dynamics, no convergence required
- **Real-world validated:** Empirical protocol tests on 150+ min game telemetry

### Implementation Status

- **Code:** `refined_protocol/core_dynamics_empirical.py` (complete)
- **Tests:** `refined_protocol/test_integration_empirical.py` (complete)
- **Analysis library:** `refined_protocol/ANALYSIS_CODE_LIBRARY.py` (complete)
- **Protocol:** `refined_protocol/PROTOCOL_V2_EMPIRICAL_FRAMEWORK.md` (complete)

### Production Scope (v1.0.x)

What is included:
- Mean-centered Gram computation
- Eigenspectrum analysis
- Effective rank (entropy-based)
- Persistence spectrum
- Transition detection
- Reference versioning and validation

What is excluded (deferred):
- Hierarchical (multi-scale) analysis
- Stochastic dynamics
- Advanced convergence proofs
- Optimization (cross-game universal calibration)

---

## 4. Research Architecture: Dependency-Matrix Dynamics

### Canonical Pipeline

```
Telemetry
    ↓
Kraskov k-NN MI estimation → M (NxN matrix, heterogeneous diagonal)
    ↓
SVD spectral filtering: P = U Σ_gated U^T
    ↓
State amplification: S_new = S + η(PS)
    ↓
Convergence detection: (spectral residual, rank stability, state residual)
    ↓
Decision: Converged structure found
```

### Status

- **Code:** `python/q64/core_dynamics.py` (implemented)
- **Tests:** `tests/test_integration.py` (implemented)
- **Documentation:** `docs/THE_CRITICAL_TURN.md` (theoretical foundation)

### Known Defects (Requires Research Resolution)

| Defect | Impact | Category |
|--------|--------|----------|
| D1: Self-MI diagonal approximation | Semantic heterogeneity | Auditability (fixable: rename to dependency_matrix) |
| D2: Non-idempotent projection | Expansive dynamics | Stability (research: B5 redesign or alternatives) |
| D3: Mutable η parameter | Path-dependent reproducibility | Determinism (fixable: external controller) |

### Research Track Activities

- D1 hygiene: Rename, clarify heterogeneous measurement
- D3 hygiene: Remove mutation, log adaptation
- D2 investigation: Compare amplification vs. residual dynamics (B5) vs. alternative formulations
- Convergence proof: Establish bounds or characterize empirically
- Hierarchical extension: Menger Sponge framework (deferred pending D2 resolution)

---

## 5. Validation Gate: H₁ Acceptance

### Empirical Protocol (5 weeks)

**Execution:** `refined_protocol/PROTOCOL_V2_EMPIRICAL_FRAMEWORK.md`

**Success Criteria:** Accept H₁ if ≥4 of 5 primary metrics pass:

| Metric | Target | Acceptable | Failure |
|--------|--------|-----------|---------|
| r_eff (entropy-based) | ≤10 | ≤14 | >18 |
| H (spectral entropy) | ≤log(12) | ≤log(14) | >log(16) |
| % stable regimes | >70% | >60% | <40% |
| θ_median (subspace angle) | <0.5 rad | <0.65 rad | >0.8 rad |
| ΔF1 (transition alignment) | >0.30 | >0.20 | <0.10 |

**Data Collection:**
- 5 game titles
- 30 min per game (60 FPS)
- 540,000 total samples
- Mean-centered, per specification

**Outcome:**
```
H₁ ACCEPTED → Proceed to Production Hardening
H₁ REJECTED → Pivot to alternative architecture or research redesign
```

---

## 6. Promotion Criteria: Dependency-Matrix as Challenger

For dependency-matrix dynamics to replace empirical covariance as production architecture:

### Performance Metrics (Must Outperform Baseline)

1. **Transition Detection F₁**
   ```
   F₁(dependency-matrix) > F₁(covariance) + 0.10
   across all 5 test games
   ```

2. **False Positive Rate**
   ```
   FPR(dependency-matrix) < FPR(covariance) - 0.05
   at equivalent sensitivity
   ```

3. **Detection Latency**
   ```
   latency(dependency-matrix) < latency(covariance)
   under <150μs/frame constraint
   ```

4. **Cross-Game Portability**
   ```
   L_drift(universal_Φ_ref) < 0.5 across game pairs
   OR per-game calibration overhead < covariance calibration cost
   ```

### Quality Constraints (Must Maintain Baseline)

5. **Memory Budget**
   ```
   <1 MB resident memory (vs. covariance <80KB)
   Justification required if exceeded
   ```

6. **Latency Budget**
   ```
   <150 μs per frame (vs. covariance <100μs target)
   Real-time deadline absolute
   ```

7. **Determinism**
   ```
   No hidden parameter mutation
   All state changes logged and reproducible
   Replay validation: identical inputs → identical outputs
   ```

8. **Auditability**
   ```
   Every state variable has operational meaning
   λ₁ interpretation unambiguous
   Convergence criterion operationally justified
   Decision trace complete
   ```

### Interpretability Burden (Must Not Degrade)

9. **Complexity Justification**
   ```
   Dependency-matrix introduces: MI estimation, heterogeneous diagonals, 
   spectral filtering, state dynamics, convergence detection.
   
   For each added layer, demonstrate:
     • Operational value (what enables this layer?)
     • Auditability (what does it mean if it fails?)
     • Necessity (cannot be achieved by covariance alone?)
   
   If any layer cannot be justified: remove it.
   ```

### Evidence Standard

**Promotion requires:**
1. Real telemetry validation (H₁ gate passed)
2. Objective performance advantage on metrics 1–4
3. Maintenance of constraints 5–8
4. Clear interpretability justification for added complexity

**If any criterion fails:** Research continues; covariance remains production.

---

## 7. Reference Governance Requirements (D4)

### Purpose

Reference (`Φ_ref`) is the calibration anchor. Without governance, reference becomes untraceable, unauditable, and untrustworthy.

### Reference Lifecycle

#### Creation
```
Who:         Role with calibration authority
Requirements:
  • Minimum 500 frames of telemetry
  • Mean-centered covariance computed
  • Eigenspectrum analysis complete
  • r_eff and entropy measured
  • Validation gate applied
Approval:    Architecture review (can be automated if metrics meet thresholds)
Output:      Reference version tagged with hash and timestamp
```

#### Validation
```
Test Protocol:
  1. Compute Gram matrix from reference frames
  2. Verify symmetric: ||G - G^T|| < 1e-8
  3. Verify PSD: min(eig(G)) > -1e-6
  4. Measure r_eff, entropy, condition number
  5. Compare to baseline expectations
  6. Approve or reject
```

#### Versioning
```
Format:    game-name_v{major}.{minor}-{timestamp}-{hash}
Example:   fortnite_v1.0-2026-06-15-abc123def
Major:     Game version (1.0, 2.0, etc.)
Minor:     Calibration iteration within game version
Timestamp: ISO 8601 (enables chronological ordering)
Hash:      SHA256(telemetry_source + creation_params) for immutability
```

#### Refresh Triggers
```
Automatic (no approval needed):
  • Game patch detected (version change in telemetry)
  • Firmware update detected (host system change)
  • Hardware change detected (device identifier change)
  
Manual (requires approval):
  • Statistically significant drift: ||Σ_current - Σ_ref||_F > threshold
  • Operational change: new thermal profile, new power envelope
  • Experimental: testing alternative calibration approach
  
Forbidden (retire reference):
  • Reference age > 90 days without validation
  • Telemetry quality < threshold (NaN, gaps, outliers)
  • Audit trail incomplete or tampered
```

#### Retirement
```
A reference is retired if:
  • Superseded by newer reference (marked as obsolete, kept for audit)
  • Telemetry source corrupted or invalid
  • Responsible party unavailable to justify it
  • Expiration policy triggered (e.g., 90-day rule)

Retired references:
  • Remain in archive (never deleted)
  • Marked with retirement_reason and retirement_timestamp
  • Cannot be used for new calibrations
  • Can be used for historical analysis/audit only
```

### Audit Trail

Every production decision must record:
```json
{
  "reference_id": "fortnite_v1.0-2026-06-15-abc123def",
  "reference_creation_time": "2026-06-15T14:22:33Z",
  "reference_dataset_hash": "sha256_of_calibration_frames",
  "reference_version": "1.0",
  "reference_created_by": "user@team",
  "reference_approved_by": "architect@team",
  "reference_approval_time": "2026-06-15T15:45:00Z"
}
```

### Governance Authority

- **Creation/approval:** Architecture or authorized calibration engineer
- **Retirement:** Same authority as creation
- **Audit:** Automatic (logged with every decision event)
- **Escalation:** Reference governance violations block production deployment

---

## 8. Event Schema Requirements (D5)

### Purpose

Event schema is the contract between system and analysis. Instability causes:
```
Telemetry from week 1 ≠ telemetry from week 5 (interpretation)
→ Cannot compare results
→ Empirical validation becomes unreliable
```

Lock schema now. Implement tooling iteratively.

### Canonical Event Schema (Immutable)

```json
{
  "version": "1.0",
  "timestamp": "2026-06-15T14:22:33.456789Z",
  "frame_number": 10234,
  
  "reference_id": "fortnite_v1.0-2026-06-15-abc123def",
  "algorithm_version": "empirical-covariance-v1.0",
  
  "state": {
    "rank_eff": 9.2,
    "rank_eff_delta": 0.1,
    "largest_eigenvalue": 28.5,
    "smallest_eigenvalue": 0.12,
    "spectral_entropy": 2.14,
    "condition_number": 237.5
  },
  
  "stability": {
    "persistence_score": 0.72,
    "regime_duration_frames": 245,
    "regime_classification": "stable"
  },
  
  "transition": {
    "detected": true,
    "magnitude": 2,
    "magnitude_reason": "rank_jump_8to10",
    "confidence": 0.91
  },
  
  "drift": {
    "from_reference": 0.34,
    "drift_reason": "within_normal_range"
  },
  
  "convergence": {
    "state": "stable",
    "confidence": 0.88
  },
  
  "performance": {
    "latency_microseconds": 127,
    "memory_bytes": 65536
  },
  
  "telemetry_input": {
    "frame_time_ms": 16.67,
    "gpu_load": 0.82,
    "cpu_load": 0.45,
    "temp_celsius": 52.3,
    "input_lag_ms": 2.1,
    "power_draw_watts": 18.5
  }
}
```

### Schema Evolution Rules

- **v1.0 → v1.1:** Additive fields only (backward compatible)
- **Field deletion:** Forbidden (breaks historical analysis)
- **Field renaming:** Forbidden (create new field, deprecate old)
- **Breaking changes:** Require major version bump + 90-day dual-write period

### Two-Year Interpretation Guarantee

```
A telemetry file captured today must be interpretable 2 years from now.

Guarantee mechanism:
  • Schema version immutable (v1.0 files always parse as v1.0)
  • Field semantics documented at schema version
  • Reference ID included (enables lookup of calibration context)
  • Algorithm version included (enables understanding of decision logic)
```

---

## 9. Deferred Research Questions

These are **not production blockers**. They are active research tracks:

### D2: Projection Operator Stability

**Question:** Is the amplification dynamics (S_new = S + ηPS) stable on real telemetry?

**Research Options:**
- Original formulation analysis (current code)
- Residual dynamics (B5: S_new = (1-η)S + ηPS)
- Alternative formulations (Lyapunov, contraction arguments)
- Empirical convergence characterization on real data

**Outcome:** If stability proven or demonstrated empirically, D2 resolves. Otherwise, remains research artifact.

### Convergence Proof

**Question:** Can convergence to fixed point be proven? Or characterized empirically?

**Research Track:**
- Lyapunov function construction
- Contraction mapping analysis
- Empirical convergence rate curves (baseline: covariance stream)
- Bounds on time-to-convergence

**Outcome:** Theoretical or empirical characterization required for promotion.

### Hierarchical (Menger Sponge) Framework

**Question:** Can dependency-matrix structure be extended to multi-scale analysis?

**Status:** Blocked until D2 resolved (current formulation is not stable enough for hierarchical recursion)

**Deferred:** v1.1.0 or later, pending D2 resolution

---

## 10. Consequences

### Immediate (v1.0.1)

**Production Path Unblocked:**
- Deploy empirical covariance stream to production
- No D1/D2/D3 fixes required for production
- Architecture is stable, auditable, deterministic

**Dependency-Matrix Research Track Activated:**
- D1 hygiene: Rename to `dependency_matrix`, clarify heterogeneous semantics (improves research auditability)
- D3 hygiene: Remove η mutation, log adaptation (improves research reproducibility)
- D2 investigation: Begin analysis of alternatives (B5, Lyapunov, empirical characterization)

### Validation Phase (Weeks 1–5)

**Empirical Protocol Execution:**
- Collect telemetry from 5 game titles
- Measure H₁ criteria
- Accept or reject hypothesis

**If H₁ Accepted:**
- Proceed to production hardening
- Dependency-matrix becomes formal research track
- Promotion pathway established (must beat baseline on 4 metrics + 5 constraints)

**If H₁ Rejected:**
- Empirical covariance insufficient for this workload
- Redesign required (could favor dependency-matrix if restructured)
- Architecture decision revisited

### v1.1.0 and Beyond

**Production (v1.0.x hardening branch):**
- Reference governance infrastructure
- Observability tooling
- Optimization for real deployment
- No architectural changes

**Research (v1.1.x research branch):**
- D2 stability investigation (B5, alternatives)
- Convergence characterization
- Hierarchical framework (if D2 resolves)
- Dependency-matrix promotion push (if evidence supports)

### Governance Model

```
Architecture Decisions:
  ├─ Production (empirical covariance)
  │  └─ Frozen unless promotion criteria met
  │
  └─ Research (dependency-matrix)
     └─ Mutable; must demonstrate superiority to replace baseline
```

This model:
- Prevents architectural indecision (one clear production path)
- Enables fair challenger research (objective promotion criteria)
- Maintains stability (production path does not change on opinion)
- Preserves optionality (evidence can drive change)

---

## Approval Checklist

- ✅ Production architecture selected: Empirical Covariance Stream
- ✅ Research architecture defined: Dependency-Matrix Dynamics (challenger)
- ✅ Validation gate specified: H₁ acceptance (5-week empirical protocol)
- ✅ Promotion criteria defined: Objective performance + quality constraints + interpretability burden
- ✅ Reference governance specified: Lifecycle, versioning, refresh triggers, audit trail
- ✅ Event schema locked: Immutable v1.0, backward-compatible evolution rules
- ✅ Research roadmap deferred: D2, convergence proof, hierarchical framework
- ✅ Dependencies documented: No circular dependencies, clear sequencing

---

**This ADR is the authoritative source for architecture decisions. All defect-repair documents are historical analysis.**

**Retire:**
- `DEFECT_REPAIR_DEBATE.md` (archived as historical analysis)
- `DEFECT_REPAIR_RECONSIDERATION.md` (archived as historical analysis)

**Keep as supporting context:**
- `CLARIFICATIONS_V1_0_0_DEFECTS.md` (explains D1/D2/D3 in detail)

**Activate:**
- `PROTOCOL_V2_EMPIRICAL_FRAMEWORK.md` (execute per ADR-001)
- `core_dynamics_empirical.py` (production implementation)
- Reference governance framework (implement per Section 7)
- Event schema infrastructure (implement per Section 8)

---

**ADR-001 Status: ACCEPTED**  
**Implementation Start: Upon empirical protocol launch**  
**Next Review: Post-H₁ gate decision (Week 5)**
