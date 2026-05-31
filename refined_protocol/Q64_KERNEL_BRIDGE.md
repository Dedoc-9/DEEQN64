# Q64 Kernel Bridge: Specification-to-Implementation Mapping

**Version:** 1.0.0-bridge  
**Nature:** Purely referential mapping (maps kernel constructs to execution layer mechanisms)  
**Property:** Non-authoritative (kernel is authority; bridge is navigation only)

---

## Invariant: This Document Is Unidirectional

```
Q64_GOVERNANCE_KERNEL.md → Q64_EXECUTION_LAYER_SPEC.md
Kernel defines what.
Execution layer defines how.
Bridge points from what to how.

Forbidden:
- Explanations ("because...")
- Justifications ("this ensures...")
- Interpretations ("means that...")
- Redefinitions ("also requires...")

Allowed:
- Mappings ("kernel rule X implemented by execution mechanism Y")
- Pointers ("subspace angle computed in section 4.4")
- Lists ("guard conditions defined in section 3.1")
```

---

## 1. Namespace Mappings

| Kernel Construct | Execution Layer Implementation |
|---|---|
| **adr/** | Not enforced at runtime; kernel defines authority |
| **schemas/** | Enforced by: Q64_EXECUTION_LAYER_SPEC §6.1 (schema version checks in CI) |
| **core/** | Enforced by: Q64_EXECUTION_LAYER_SPEC §1.2 (import graph parser excludes research/ from core/ imports) |
| **analysis/** | Enforced by: Q64_EXECUTION_LAYER_SPEC §1.2 (read-only file I/O check in step 3) |
| **protocols/** | Not enforced; assumes correct usage |
| **research/** | Enforced by: Q64_EXECUTION_LAYER_SPEC §1 (forbidden edges in import graph validation) |
| **archive/** | Enforced by: Q64_EXECUTION_LAYER_SPEC §6.1 (immutability hash verification) |
| **docs/** | Not enforced at runtime |

---

## 2. Structural Invariant Mappings

| Kernel Invariant | Execution Layer Enforcement |
|---|---|
| **I1_CORE_PURITY** | Q64_EXECUTION_LAYER_SPEC §1 (RULE_3 check in import graph validation; semantic rule scan for "empirical" in core/) |
| **I2_RESEARCH_ISOLATION** | Q64_EXECUTION_LAYER_SPEC §1.2 (forbidden edges: research/ → core/ blocked in step 5) |
| **I3_ANALYSIS_PURITY** | Q64_EXECUTION_LAYER_SPEC §1.2 (read-only check in step 3; write constraint in step 3) |
| **I4_PROTOCOLS_INDEPENDENCE** | Not enforced; assumed by design |
| **I5_SCHEMA_IMMUTABILITY** | Q64_EXECUTION_LAYER_SPEC §6.1 (hash verification on schema files; version checking) |
| **I6_ARCHIVE_IMMUTABILITY** | Q64_EXECUTION_LAYER_SPEC §6.1 (hash-based immutability verification; write protection) |
| **I7_DUAL_ENGINE_COHERENCE** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard: Q64_ENGINE_MODE flag defined; both engines conform to same schemas) |
| **I8_AUTHORITY_CENTRALIZATION** | Q64_EXECUTION_LAYER_SPEC §5.1 (authorization protocol checks allowed_authorizers for each transition) |

---

## 3. Rule-to-Implementation Mappings

| Kernel Rule | Execution Layer Enforcement |
|---|---|
| **RULE_1_NO_REFINED_PROTOCOL_TO_Q64** | Q64_EXECUTION_LAYER_SPEC §1.1 step 2 (import rule check; pattern: "from refined_protocol") |
| **RULE_2_NO_Q64_TO_REFINED_PROTOCOL** | Q64_EXECUTION_LAYER_SPEC §1.1 step 2 (import rule check; pattern: "from q64" in refined_protocol/) |
| **RULE_3_CORE_PURITY** | Q64_EXECUTION_LAYER_SPEC §1.1 step 4 (semantic rule: "empirical" forbidden in core/core_dynamics.py) |
| **RULE_4_ANALYSIS_ISOLATION** | Q64_EXECUTION_LAYER_SPEC §1.1 step 3 (write constraint check: analysis/ cannot write to core/) |
| **RULE_5_RESEARCH_ISOLATION** | Q64_EXECUTION_LAYER_SPEC §1.1 step 5 (dependency graph validation: forbidden edges from research/) |
| **RULE_6_ARCHIVE_IMMUTABILITY** | Q64_EXECUTION_LAYER_SPEC §6.1 (hash-based freeze verification; no write allowed) |
| **RULE_7_DUAL_ENGINE_COHERENCE** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard condition: Q64_ENGINE_MODE defined; both engines use same schemas) |
| **RULE_8_SCHEMA_VERSIONING** | Q64_EXECUTION_LAYER_SPEC §6.1 (version check: no overwrites; must be v1.1, v2.0, etc.) |
| **RULE_9_GATE_BINDING** | Q64_EXECUTION_LAYER_SPEC §4 (gate evaluation: H₁ metrics computed; decision is binding) |
| **RULE_10_SNAPSHOT_IMMUTABILITY** | Q64_EXECUTION_LAYER_SPEC §6.1 (hash comparison: current hash vs. stored hash; hotfix exceptions logged) |

---

## 4. Phase Lifecycle Mappings

| Kernel Phase | Execution Layer State Management | Transition Trigger |
|---|---|---|
| **PRE_H1** | Q64_EXECUTION_LAYER_SPEC §2.1 (.q64_governance_state.json: current_state = "PRE_H1") | Initialization |
| **H1_VALIDATION_IN_PROGRESS** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "H1_VALIDATION_IN_PROGRESS") | Guard passes: H1_VALIDATION_READY (§3.1) |
| **H1_GATE_CLOSED_ACCEPTED** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "H1_GATE_CLOSED_ACCEPTED") | Guard passes: H1_GATE_SATISFIED (§3.1); automated via evaluate_hypothesis() |
| **H1_GATE_CLOSED_REJECTED** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "H0_ACCEPTED") | Guard fails: H1_GATE_SATISFIED; automated via evaluate_hypothesis() |
| **SNAPSHOT_FREEZE** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "SNAPSHOT_FREEZE"; snapshots.q64_hash, snapshots.refined_hash stored) | Guard passes: SNAPSHOT_FROZEN (§3.1); manual authorization |
| **CODE_PROMOTION** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "CODE_PROMOTION") | Guard passes: CODE_PROMOTION_READY (§3.1); manual authorization |
| **DUAL_ENGINE_MODE** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "DUAL_ENGINE_MODE") | Guard passes: DUAL_ENGINE_READY (§3.1); manual authorization |
| **STABILITY_VALIDATION** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "STABILITY_VALIDATION") | Manual authorization; guard STABILITY_PROVEN (§3.1) active during this phase |
| **DEPRECATION_ELIGIBLE** | Q64_EXECUTION_LAYER_SPEC §2.1 (state = "DEPRECATION_ELIGIBLE") | Guard passes: DEPRECATION_AUTHORIZED (§3.1); manual authorization |

---

## 5. Gate Mappings

| Kernel Gate | Execution Layer Evaluation | Computed Metrics |
|---|---|---|
| **H1_DECISION_GATE** | Q64_EXECUTION_LAYER_SPEC §4 (gate evaluation: all 5 metrics computed) | r_eff (§4.1), entropy (§4.2), pct_time_stable (§4.3), theta_median (§4.4), delta_f1 (§4.5) |
| **SNAPSHOT_FREEZE_GUARD** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard: SNAPSHOT_FROZEN predicate) | Checks: repos clean, tags exist, time elapsed |
| **CODE_PROMOTION_GUARD** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard: CODE_PROMOTION_READY predicate) | Checks: snapshot frozen, v1.1 code not yet in q64 |
| **DUAL_ENGINE_ACTIVATION_GUARD** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard: DUAL_ENGINE_READY predicate) | Checks: promotion complete, files exist, flag defined |
| **STABILITY_VALIDATION_GATE** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard: STABILITY_PROVEN predicate) | Checks: weeks elapsed, metrics replicated, no regression |
| **DEPRECATION_GATE** | Q64_EXECUTION_LAYER_SPEC §3.1 (guard: DEPRECATION_AUTHORIZED predicate) | Checks: stability proven, authorization given, v1.0.0 preserved |

---

## 6. Metric Computation Mappings

| Kernel Metric | Execution Layer Computation | Section |
|---|---|---|
| **r_eff** | Q64_EXECUTION_LAYER_SPEC §4.1 | Shannon entropy of eigenvalue distribution; r_eff = exp(H) |
| **entropy** | Q64_EXECUTION_LAYER_SPEC §4.2 | Spectral entropy: H = -Σ (λ_i / Σλ_j) log(λ_i / Σλ_j) |
| **pct_time_stable** | Q64_EXECUTION_LAYER_SPEC §4.3 | Rank transition detection; stable regime = duration > 100 frames |
| **theta_median** | Q64_EXECUTION_LAYER_SPEC §4.4 | Subspace angle: θ = arccos(largest_sv(U_k^T @ U_k')) |
| **delta_f1** | Q64_EXECUTION_LAYER_SPEC §4.5 | F1 score vs. random baseline; ΔF1 = F1_discovered - F1_random |

---

## 7. Validation Timing Mappings

| Kernel Requirement | Execution Layer Timing | Location |
|---|---|---|
| **Import rules enforced** | Pre-commit + CI pipeline | Q64_EXECUTION_LAYER_SPEC §7.1 (stage 1 + stage 2) |
| **State consistency checked** | CI pipeline | Q64_EXECUTION_LAYER_SPEC §7.1 (stage 2) |
| **Guards evaluated** | CI pipeline | Q64_EXECUTION_LAYER_SPEC §7.1 (stage 2) |
| **State file updated** | Post-merge | Q64_EXECUTION_LAYER_SPEC §7.1 (post-merge stage) |
| **Transition logged** | Immediately after merge | Q64_EXECUTION_LAYER_SPEC §2.1 (append to transitions_log) |

---

## 8. Authorization Mappings

| Kernel Authorization | Execution Layer Implementation | Section |
|---|---|---|
| **PRE_H1 → H1_VALIDATION** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: project_lead) | Manual authorization |
| **H1_VALIDATION → H1_GATE_CLOSED** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: automated) | Automatic via evaluate_hypothesis() |
| **H1_GATE → SNAPSHOT_FREEZE** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: project_lead) | Manual authorization |
| **SNAPSHOT_FREEZE → CODE_PROMOTION** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: project_lead) | Manual authorization |
| **CODE_PROMOTION → DUAL_ENGINE** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: project_lead) | Manual authorization |
| **DUAL_ENGINE → STABILITY_VALIDATION** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: project_lead) | Manual authorization |
| **STABILITY_VALIDATION → DEPRECATION** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: project_lead) | Manual authorization |
| **H1_VALIDATION → H0_ACCEPTED** | Q64_EXECUTION_LAYER_SPEC §5.1 (allowed_authorizers: automated) | Automatic via evaluate_hypothesis() |

---

## 9. State Persistence Mappings

| Kernel Requirement | Execution Layer Implementation |
|---|---|
| **State file exists** | Q64_EXECUTION_LAYER_SPEC §2.1 (.q64_governance_state.json) |
| **Transitions are append-only** | Q64_EXECUTION_LAYER_SPEC §2.1 (transitions_log is never rewritten) |
| **Snapshots are hashed** | Q64_EXECUTION_LAYER_SPEC §2.1 (q64_hash_v1_0_0, refined_protocol_hash stored) |
| **Authorization is signed** | Q64_EXECUTION_LAYER_SPEC §2.1 (optional gpg_signature in log) |
| **Consistency is validated** | Q64_EXECUTION_LAYER_SPEC §2.2 (state_validation protocol on every commit) |

---

## Final Property: Mapping Is Unidirectional

```
Kernel → Execution Layer (forward mapping only)

If execution layer changes:
  Bridge is updated to point to new sections

If kernel changes:
  Execution layer must be updated to implement new rules
  Bridge is updated to map to new implementations

Kernel is never inferred from execution layer.
Bridge never explains kernel.
Execution layer never extends kernel.
```

---

**Status:** ✅ Mapping complete  
**Authority:** Non-authoritative (reference only)  
**Maintenance:** Updated when kernel or execution layer changes  
**Direction:** Kernel → Execution Layer only (never reversed)
