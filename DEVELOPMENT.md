# DEEQN64 Development Roadmap

This document outlines the development schedule for DEEQN64 (https://github.com/Dedoc-9/DEEQN64) from Week 1 completion through Week 3 H₁ validation.

---

## Phase 1: Week 1 Validation (✅ COMPLETE)

**Objective:** Prove the mathematical specification works on synthetic data.

### Deliverables
- [x] Reference engine implementation (q64_stratified_engine.py)
- [x] Unit test suite (q64_reference_test.py)
- [x] All tests passing (3/3)
- [x] Empirically tuned thresholds

### Key Results
- All 4 domains converge on synthetic low-rank data
- Convergence predicate c_t triggers reliably
- H₁ gate logic validates correctly
- Thresholds locked: ε_R=1e-2, δ_L=0.2, τ=0.4, w=20

### Locked Parameters (Do Not Change Without Re-validation)
```
Domain Configuration:
  Input:     N=10, k=3   (controller state)
  Physics:   N=6,  k=5   (position + velocity)
  System:    N=12, k=3   (CPU/GPU/thermal)
  Rendering: N=36, k=10  (graphics pipeline)

Thresholds:
  ε_R (residual):       1e-2
  δ_L (drift):          0.2
  τ (rank threshold):   0.4
  w (window size):      20 frames

H₁ Success Criteria:
  ≥3 of 4 domains must achieve pct_stable:
  Input:     ≥80%
  Physics:   ≥70%
  System:    ≥60%
  Rendering: ≥40%
```

### Test Games (Fixed for H₁ Validation)
1. Valorant (competitive FPS)
2. Portal 2 (physics puzzle)
3. Celeste (precision platformer)
4. Minecraft Creative (sandbox)
5. Elden Ring (action RPG)

Each: 30-minute capture @ 60 FPS

---

## Phase 2a: Week 2 Infrastructure (IN PROGRESS)

**Objective:** Build the telemetry capture harness to feed real game data into Q64.

### Task 1: Game Capture Configuration
**File:** `game_capture_config.json`  
**Depends on:** None  
**Time estimate:** 1 hour

**Acceptance criteria:**
- JSON loads without errors
- All 5 games defined with paths
- Telemetry methods specified per game
- Test: `python -c "import json; json.load(open('game_capture_config.json'))"`

**Template structure:**
```json
{
  "games": [
    {
      "name": "valorant",
      "executable_path": "...",
      "capture_method": "network_api|memory_hook|...",
      "telemetry_fields": [...]
    }
  ]
}
```

---

### Task 2: Capture Profile Configuration
**File:** `capture_profile.yaml`  
**Depends on:** None  
**Time estimate:** 30 minutes

**Acceptance criteria:**
- YAML loads without errors
- Thresholds match Week 1 locked values
- Sample rate defined
- Output directories configured

**Template structure:**
```yaml
thresholds:
  epsilon_R: 1e-2
  delta_L: 0.2
  tau: 0.4
  window_size: 20

sampling:
  fps: 60
  duration_seconds: 1800

output:
  telemetry_logs: "./telemetry_logs/"
  convergence_logs: "./convergence_logs/"
```

---

### Task 3: State Vector Mapper
**File:** `state_vector_mapper.py`  
**Depends on:** Task 1 (game_capture_config.json)  
**Time estimate:** 3 hours

**Acceptance criteria:**
- Assembles valid (64,) numpy arrays
- Domain splits verified:
  - input: dims 0-9
  - physics: dims 10-15
  - system: dims 16-27
  - rendering: dims 28-63
- No NaN values in output

**Key class:** `StateVectorAssembler`
```python
assembler = StateVectorAssembler(config)
s_t = assembler.assemble(controller_state, physics_state, system_metrics, render_data)
assert s_t.shape == (64,)
```

---

### Task 4: Hardware Monitor Adapter
**File:** `hardware_monitor_adapter.py`  
**Depends on:** None (but requires Open Hardware Monitor installed)  
**Time estimate:** 2 hours

**Acceptance criteria:**
- Fetches CPU temperature without errors
- Fetches GPU load without errors
- Fetches fan RPM without errors
- Returns numeric values (no exceptions)

**Key class:** `OpenHardwareMonitorAdapter`
```python
adapter = OpenHardwareMonitorAdapter()
cpu_temp = adapter.get_cpu_temperature()  # float
gpu_load = adapter.get_gpu_load()         # float
```

---

### Task 5: Data Pipeline
**File:** `data_pipeline.py`  
**Depends on:** Tasks 1-4  
**Time estimate:** 3 hours

**Acceptance criteria:**
- Streams s_t vectors through engine without errors
- Logs metrics to memory (no file I/O yet)
- Detects convergence events
- Runs 600 frames without crashes

**Key class:** `DataPipeline`
```python
pipeline = DataPipeline(config)
for i in range(600):
    s_t = pipeline.acquire_state()
    metrics = pipeline.update(s_t)
    if metrics["convergence_detected"]:
        pipeline.log_convergence_event(i)
```

### Phase 2a Acceptance Criteria

- [ ] All 5 config/code files created
- [ ] Data pipeline runs for 600 frames without errors
- [ ] q64_stratified_engine.py receives valid s_t vectors
- [ ] Domain convergence is detectable in synthetic test
- [ ] Ready to move to Phase 2b

---

## Phase 2b: Week 2 Runtime (BLOCKED UNTIL 2a COMPLETE)

**Objective:** Integrate Q64 into live game execution.

### Task 6: Real-time Monitor
**File:** `q64_realtime_monitor.py`  
**Depends on:** Phase 2a complete  
**Time estimate:** 5 hours

**Acceptance criteria:**
- Streams live telemetry while game runs
- Logs convergence events to console
- Produces valid HDF5 output file
- Does not impact game performance

---

### Task 7: Game Launcher Wrapper
**File:** `game_launcher_wrapper.sh` (or `.ps1` on Windows)  
**Depends on:** Task 6  
**Time estimate:** 1 hour

**Acceptance criteria:**
- Launches game and Q64 monitor in parallel
- Both terminate together on game exit
- No orphaned processes

---

### Task 8: Telemetry Logger
**File:** `telemetry_logger.py`  
**Depends on:** Phase 2a complete  
**Time estimate:** 2 hours

**Acceptance criteria:**
- Writes valid HDF5 with datasets:
  - /frames (N, 64)
  - /convergence (N,) boolean
  - /ranks (N, 4) per-domain ranks
- File size expected: ~5 MB per 30-min capture

---

### Task 9: Convergence Visualizer (Optional)
**File:** `convergence_visualizer.py`  
**Depends on:** Task 8  
**Time estimate:** 3 hours

**Acceptance criteria:**
- Real-time matplotlib plots of domain convergence
- Updates at 2 Hz without impacting performance
- Shows per-domain c_t, rank, residual R_t

---

## Phase 3: Analysis & H₁ Validation (BLOCKED UNTIL 2b COMPLETE)

**Objective:** Evaluate H₁ success criteria on real game captures.

### Task 10: Forensic Autopsy
**File:** `forensic_autopsy.py`  
**Depends on:** Phase 2b complete (HDF5 logs exist)  
**Time estimate:** 4 hours

**Acceptance criteria:**
- Generates rank evolution plots
- Computes pct_stable per domain
- Exports stability metrics as CSV

---

### Task 11: H₁ Gate Evaluator
**File:** `h1_gate_evaluator.py`  
**Depends on:** Task 10  
**Time estimate:** 3 hours

**Acceptance criteria:**
- Reads forensic metrics
- Evaluates: ≥3 of 4 domains pass
- Returns PASS/FAIL for each game

---

### Task 12: Spectral Report Generator
**File:** `spectral_report_generator.py`  
**Depends on:** Task 11  
**Time estimate:** 4 hours

**Acceptance criteria:**
- Generates HTML/PDF report
- Shows all 5 games + domain metrics
- Includes per-domain plots and thresholds

---

## H₁ Validation Success Criteria

**Each of 5 games must:**
- [x] Capture 30 minutes @ 60 FPS
- [ ] ≥3 of 4 domains show pct_stable ≥ threshold
- [ ] Manifold hypothesis empirically validated across all domains

**If successful:**
- Proceed to hardware mapping
- Document empirical validation results
- Release Week 3 findings

**If unsuccessful:**
- Analyze which domains fail and why
- Re-tune thresholds (if justified)
- Re-run on subset of games
- Document failure modes

---

## Timeline Summary

| Phase | Duration | Status | Blockers |
|-------|----------|--------|----------|
| Week 1 | 1 week | ✅ Complete | None |
| Week 2a | 1 week | ⏳ In Progress | None |
| Week 2b | 1 week | ⏳ Waiting for 2a | Phase 2a complete |
| Week 3 | 1 week | ⏳ Waiting for 2b | Phase 2b complete |

**Total project time:** ~4 weeks from start to H₁ validation complete

---

## Dependency Graph

```
Week 1 (Complete)
    ↓
Week 2a:
    Task 1 ──→ Task 3 ──→
    Task 2 ──→ Task 5 ──→ Phase 2a Complete
    Task 4 ──→ Task 5 ──→
    ↓
Week 2b:
    Task 6 ──→ Task 7 ──→
    Task 8 ──→ Task 9 ──→ Phase 2b Complete
    ↓
Week 3:
    Task 10 ──→ Task 11 ──→ Task 12 ──→ H₁ Validation Complete
```

---

## Architecture Decision Log

### Week 1 Decisions
- **Domain stratification:** Each domain analyzed independently (no cross-domain coupling)
- **Threshold selection:** Empirically tuned on synthetic data, not theoretical
- **Convergence predicate:** AND of 3 conditions (all must hold, not majority vote)
- **H₁ gate:** ≥3 of 4 domains (majority logic at meta level)

### Why Stratification?
Heterogeneous telemetry (controller input, physics, system metrics, rendering) has different noise profiles, rank bounds, and stability timescales. Treating them as one 64-dimensional system would mix incomparable scales. Stratification allows domain-specific thresholds.

### Why These Thresholds?
Week 1 synthetic data was constructed to match expected manifold structure. Thresholds were tuned to trigger convergence reliably on this data without false positives. Real game data may have higher noise; thresholds remain locked to maintain comparability.

---

## Known Limitations

1. **Window size (w=20):** Fixed empirically; may not generalize to all games
2. **Domain rank bounds (k):** Based on expected manifold dimension; real games may differ
3. **Noise assumptions:** Tests assume 2% measurement noise; real telemetry may vary
4. **No adaptive tuning:** Thresholds are static; no online re-calibration
5. **No cross-domain constraints:** Domains are independent; emergent patterns may be missed

These are acceptable for Phase 1 (proof of concept). Phase 2+ may require relaxation.

---

## Testing Strategy

### Unit Tests (Week 1)
- Initialization, synthetic convergence, H₁ gate logic
- All pass on synthetic data

### Integration Tests (Week 2)
- Data pipeline integration
- Real-time monitor performance
- HDF5 logging fidelity

### Validation Tests (Week 3)
- H₁ gate on 5 real games
- Pass/fail per domain per game
- Statistical summary of stability

---

## Contributing to Development

If adding features or modifications:

1. **Threshold changes:** Document justification, re-run synthetic tests
2. **Domain changes:** Update domain configuration, state vector mapper, and acceptance criteria
3. **New tasks:** Update dependency graph and timeline
4. **Bug fixes:** Add regression tests

See [CONTRIBUTING.md](CONTRIBUTING.md) for code guidelines.

For issues and PRs: https://github.com/Dedoc-9/DEEQN64/

---

## References

- [Q64 Mathematical Foundations](refined_protocol/Q64_MATHEMATICAL_FOUNDATIONS.md)
- [Q64 Governance Kernel](refined_protocol/Q64_GOVERNANCE_KERNEL_FINAL.md)
- [README.md](README.md) — Project overview

---

**Last updated:** Week 1 Complete  
**Next milestone:** Phase 2a Task 1 (Game Capture Configuration)
