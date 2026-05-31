# Q64 Governance Kernel: Declarative System Specification

**Version:** 1.0.0-kernel-final  
**Authority:** Single source of truth for q64 architecture & policy  
**Nature:** Declarative ontology (defines normative constraints, not underlying dynamics)  
**Immutability:** Changes only via ADR amendment  
**Relationship:** Orthogonal to Q64_MATHEMATICAL_FOUNDATIONS.md (which specifies the dynamical system itself)

---

## Critical Clarification: Governance vs. Dynamics

```
This document specifies GOVERNANCE (normative, policy-based)
Q64_MATHEMATICAL_FOUNDATIONS.md specifies DYNAMICS (geometric, operator-based)

These are orthogonal formalisms:
  Governance: rules that constrain valid evolution
  Dynamics: equations that define what evolution looks like

Governance does NOT prove dynamics work.
Dynamics does NOT prove governance is sufficient.
Both must be satisfied for complete system assurance.
```

---

## Invariant: This Document Defines Normative Truth Only

This specification defines:
- What the system is
- How components relate
- What invariants must hold
- What transitions are possible
- What "correct system shape" is

This specification does NOT define:
- How rules are checked
- How state is stored
- How validation happens
- Runtime behavior or timing

**Property:** This document is complete and self-sufficient. A human can understand q64's architecture entirely from this document without reference to execution layer or bridge.

---

## 1. System Namespace (What Exists)

```yaml
namespaces:
  
  adr/:
    role: "Authority tier (binding decisions)"
    contents: [ADR-001, ADR-002 (future)]
    imports_from: []
    imported_by: [documentation, justified_actions]
    mutability: append_only (new ADRs, never edits)
    property: "Normative truth; defines system intent"
  
  schemas/:
    role: "Contracts tier (observable interfaces)"
    contents: [event_v1.0.json, reference_v1.0.json, metrics_v1.0.json]
    imports_from: [adr]
    imported_by: [core, protocols, analysis, research]
    mutability: versioned (v1.0, v1.1, v2.0, never overwrite)
    property: "Immutable once locked; defines observable boundaries"
  
  core/:
    role: "Production tier (authoritative implementation)"
    contents: [core_dynamics.py (v1.0.0), core_dynamics_v1_1.py (post-H₁), analysis/empirical_tools.py (post-H₁)]
    imports_from: [schemas]
    imported_by: [protocols, (only)]
    mutability: v1.0.0 frozen; v1.1 added post-H₁; no imports from research or analysis
    property: "Production path; empirical covariance based; deterministic"
  
  analysis/:
    role: "Evaluation tier (interpretation layer)"
    contents: [metric_definitions.py, effectiveness.py, auditability.py, notebooks/]
    imports_from: [core (read-only), schemas, protocols (read-only)]
    imported_by: [protocols (only)]
    mutability: true
    property: "Pure interpretation; cannot control production; cannot import from research"
  
  protocols/:
    role: "Validation tier (empirical execution)"
    contents: [PROTOCOL_V2_EMPIRICAL_FRAMEWORK.md, telemetry_collector.py, phase_*.py, decision_gate/evaluate_hypothesis.py]
    imports_from: [core (executes), analysis (reads), schemas]
    imported_by: []
    mutability: true
    property: "Generates ground truth via H₁ validation; produces observable data"
  
  research/:
    role: "Challenger tier (isolated sandbox)"
    contents: [dependency_matrix/, (future challengers)]
    imports_from: [schemas (optional)]
    imported_by: []
    mutability: true
    property: "Non-production; can evolve freely; never touches core; must declare non-production status"
  
  archive/:
    role: "History tier (immutable context)"
    contents: [DEFECT_REPAIR_DEBATE.md, DEFECT_REPAIR_RECONSIDERATION.md, early_sketches/]
    imports_from: []
    imported_by: []
    mutability: false (read-only reference)
    property: "Frozen reasoning trace; never imported by live code; never executed"
  
  docs/:
    role: "Explanation tier (non-normative)"
    contents: [SYSTEM_OVERVIEW.md, getting_started.md, troubleshooting.md]
    imports_from: [adr (references only), schemas]
    imported_by: []
    mutability: true
    property: "Explanatory only; cannot define behavior; cannot contradict adr/ or schemas/"
```

---

## 2. Dependency Graph (How Components Relate)

### 2.1 Canonical Edges (Allowed Dependencies)

```yaml
allowed_edges:
  
  # Authority flows down
  adr → documentation: "Decisions inform explanation"
  adr → justified_actions: "Authority justifies actions"
  
  # Contracts are universal
  schemas → core: "Production conforms to contract"
  schemas → protocols: "Validation produces conformant data"
  schemas → analysis: "Evaluation understands contract"
  schemas → research: "Research optionally references contract"
  schemas → docs: "Documentation references contracts"
  
  # Core is production
  core → schemas: "Production implements contracts"
  
  # Validation depends on core
  protocols → core: "Validation executes production"
  protocols → schemas: "Validation produces conformant data"
  protocols → analysis: "Validation reads metrics"
  
  # Analysis reads outputs
  analysis → core: "Evaluation reads production outputs (read-only, file I/O only)"
  analysis → schemas: "Evaluation understands contract"
  analysis → protocols: "Evaluation reads protocol outputs"
  
  # Research is isolated
  research → schemas: "Research optionally references contract"
  
  # Archive is reference only
  docs → archive: "Documentation may reference history"
```

### 2.2 Forbidden Edges (Strictly Disallowed)

```yaml
forbidden_edges:
  
  core → analysis:
    reason: "Production cannot depend on evaluation logic"
    consequence: "Evaluation would influence production behavior"
  
  core → research:
    reason: "Production cannot depend on challenger architectures"
    consequence: "Production would become ambiguous"
  
  core → protocols:
    reason: "Production does not know about testing"
    consequence: "Production logic would become test-aware"
  
  analysis → core:
    reason: "Evaluation cannot control production"
    consequence: "Evaluation would become prescriptive instead of descriptive"
  
  analysis → research:
    reason: "Evaluation of research is separate from evaluation system"
    consequence: "Research would be confused with production paths"
  
  protocols → adr:
    reason: "Validation does not interpret architecture decisions"
    consequence: "Validation would become decision-making"
  
  research → core:
    reason: "Challenger cannot be imported by production"
    consequence: "Production would mix paradigms"
  
  research → analysis:
    reason: "Research results ≠ live code"
    consequence: "Analysis would become unstable if research changed"
  
  adr → anything:
    reason: "Authority is not importable; it is normative only"
    consequence: "Decisions become code; decisions lose authority"
```

---

## 3. System Invariants (What Must Always Be True)

```yaml
structural_invariants:
  
  I1_CORE_PURITY:
    definition: |
      core/ contains only empirical covariance implementation
      No dependency-matrix code in core/
      No experimental flags in core/
      No research variants in core/
    consequence: |
      Production path is unambiguous
      core ≠ choice point between paradigms
  
  I2_RESEARCH_ISOLATION:
    definition: |
      research/ is never imported by core/
      research/ never imported by analysis/
      research/ never imported by protocols/
      research/ never imported by validation gates
    consequence: |
      Challenger architectures cannot leak into production
      Production remains stable under research evolution
  
  I3_ANALYSIS_PURITY:
    definition: |
      analysis/ reads core/ outputs only (file I/O, not runtime coupling)
      analysis/ cannot write to core/
      analysis/ cannot call core/ functions
      analysis/ is pure interpretation layer
    consequence: |
      Evaluation does not influence production decisions
      Analysis results are advisory, not prescriptive
  
  I4_PROTOCOLS_INDEPENDENCE:
    definition: |
      protocols/ does not contain system logic
      protocols/ uses core/ as executable (trusts it)
      protocols/ generates observable data conforming to schemas/
      protocols/ produces decision inputs for evaluate_hypothesis()
    consequence: |
      Validation is external to production
      Test results are ground truth, not validation of assumptions
  
  I5_SCHEMA_IMMUTABILITY:
    definition: |
      Once schemas/ is locked to v1.0, no changes to v1.0
      New schemas must be v1.1, v2.0, etc.
      All observable outputs conform to locked schema version
    consequence: |
      Observable interface is stable across versions
      Historical data remains interpretable
  
  I6_ARCHIVE_IMMUTABILITY:
    definition: |
      archive/ is read-only
      No modifications, deletions, or additions
      Never imported by live code
      Never executed
    consequence: |
      Historical reasoning is preserved
      Cannot accidentally depend on historical artifacts
  
  I7_DUAL_ENGINE_COHERENCE:
    definition: |
      v1.0.0 and v1.1 coexist but do not share state
      Selection via single source (Q64_ENGINE_MODE flag)
      Both engines conform to identical schemas/
      No blending between v1.0.0 and v1.1 code
    consequence: |
      Either engine can be used independently
      No hybrid mode or fallback mixing allowed
  
  I8_AUTHORITY_CENTRALIZATION:
    definition: |
      adr/ is single source of binding architecture truth
      All decisions recorded there
      No distributed decision-making in code
      No silent redesign via implementation choices
    consequence: |
      System intent is auditable
      All architectural choices are traceable
```

---

## 4. Conceptual State Machine (What Transitions Are Possible)

```yaml
lifecycle_phases:
  
  PRE_H1:
    definition: "Before empirical validation"
    property: |
      q64 (v1.0.0) is baseline research implementation
      refined_protocol contains empirical candidate
      no promotion occurs
    q64_state:
      - core_dynamics.py v1.0.0 (frozen)
      - no v1.1 exists
    transition_to_next: "Begin hardware deployment weeks 1-5"
  
  H1_VALIDATION_IN_PROGRESS:
    definition: "Weeks 1-5: Data collection and spectral analysis"
    property: |
      core_dynamics.py remains frozen
      refined_protocol candidates under test
      no code changes to q64
    invariant: "No promotion until gate closes"
    transition_to_next: "evaluate_hypothesis() completes"
  
  H1_GATE_CLOSED_ACCEPTED:
    definition: "≥4/5 empirical metrics satisfied; H₁ accepted"
    property: |
      empirical validation confirms structure exists
      promotion path is now open
      q64 remains unchanged pending Phase 1
    transition_to_next: "Authorize Phase 1 (snapshot freeze)"
  
  SNAPSHOT_FREEZE:
    definition: "Both systems tagged as immutable snapshots"
    property: |
      q64 tagged: v1.0.0-freeze
      refined_protocol tagged: v1.0.0-empirical-final
      no code changes to either (hotfix patches only)
    transition_to_next: "Authorize Phase 2 (code promotion)"
  
  CODE_PROMOTION:
    definition: "Non-destructive code promotion to q64"
    property: |
      core_dynamics_empirical.py → q64/python/q64/core_dynamics_v1_1.py
      analysis_code_library.py → q64/python/q64/analysis/empirical_tools.py
      test_integration_empirical.py → q64/tests/test_empirical_validation.py
      v1.0.0 NOT replaced; v1.1 is NEW
    transition_to_next: "Authorize Phase 3 (dual-engine mode activation)"
  
  DUAL_ENGINE_MODE:
    definition: "Both v1.0.0 and v1.1 available; selectable"
    property: |
      Q64_ENGINE_MODE controls which engine is used
      both engines coexist
      no shared state between engines
      both conform to identical schemas/
    transition_to_next: "Enter optional Phase 4 (stability validation) or remain in dual mode"
  
  STABILITY_VALIDATION:
    definition: "Optional: Prove v1.1 is production-ready over time"
    property: |
      v1.1 undergoes extended testing
      H₁ metrics must be maintained across multiple sessions
      no regression vs. v1.0.0
    transition_to_next: "If stability proven: deprecation eligible. If not: remain in dual-engine mode indefinitely"
  
  DEPRECATION_ELIGIBLE:
    definition: "Optional Phase 4: v1.0.0 moved to deprecated/"
    property: |
      core_dynamics.py → deprecated/core_dynamics_v1_0_0.py
      v1.1 becomes default engine
      v1.0.0 preserved but no longer imported by default
    final_state: true
  
  H0_ACCEPTED:
    definition: "Empirical validation failed; <4/5 metrics pass"
    property: |
      no promotion occurs
      core_dynamics_empirical.py archived as research artifact
      contingency strategy from FAILURE_MODES_AND_V2_VISION.md executed
    final_state: true
```

---

## 5. Promotion Ordering Constraints (What Must Come Before What)

```yaml
phase_ordering:
  
  constraint_1: |
    PRE_H1 must precede H1_VALIDATION_IN_PROGRESS
    (cannot validate without v1.0.0 frozen)
  
  constraint_2: |
    H1_VALIDATION_IN_PROGRESS must complete before H1_GATE_CLOSED
    (cannot gate without data)
  
  constraint_3: |
    H1_GATE_CLOSED must be ACCEPTED before SNAPSHOT_FREEZE
    (cannot freeze without H₁ acceptance)
  
  constraint_4: |
    SNAPSHOT_FREEZE must precede CODE_PROMOTION
    (cannot promote without immutable reference snapshots)
  
  constraint_5: |
    CODE_PROMOTION must precede DUAL_ENGINE_MODE
    (cannot activate dual mode without v1.1 in q64)
  
  constraint_6: |
    DUAL_ENGINE_MODE may optionally precede STABILITY_VALIDATION
    (stability testing is optional, not required)
  
  constraint_7: |
    STABILITY_VALIDATION may precede DEPRECATION_ELIGIBLE
    (deprecation only after stability proven; may never happen)
  
  constraint_8: |
    H1_VALIDATION_IN_PROGRESS may transition to H0_ACCEPTED
    (gate may fail; gates are not skippable)
```

---

## 6. Gate Definitions (What Determines State Transitions)

```yaml
gates:
  
  H1_DECISION_GATE:
    input_metrics:
      - r_eff (effective rank)
      - entropy (spectral entropy)
      - pct_time_stable (regime persistence)
      - theta_median (subspace angle)
      - delta_f1 (transition alignment)
    acceptance_criterion: |
      ≥4 of 5 metrics pass thresholds:
        r_eff ≤ 14
        entropy ≤ log(12)
        pct_time_stable ≥ 60%
        theta_median < 0.6 rad
        delta_f1 > 0.20
    output: "H₁ accepted" OR "H₀ accepted"
    property: |
      Binding decision gate
      Determines whether promotion path opens
      Only gate that is fully automated
  
  SNAPSHOT_FREEZE_GUARD:
    prerequisites: |
      H₁ accepted
      no uncommitted changes in q64/
      no uncommitted changes in refined_protocol/
    property: |
      Both systems must be in clean state
      Must have explicit authorization to freeze
  
  CODE_PROMOTION_GUARD:
    prerequisites: |
      SNAPSHOT_FREEZE phase complete
      both systems tagged as immutable
      >0 time elapsed since freeze (audit trail)
    property: |
      Prevents accidental immediate promotion
      Ensures snapshot is stable
  
  DUAL_ENGINE_ACTIVATION_GUARD:
    prerequisites: |
      CODE_PROMOTION phase complete
      v1.1 code exists in q64/
      Q64_ENGINE_MODE flag defined
    property: |
      Dual engine mode can only activate after promotion
  
  STABILITY_VALIDATION_GATE:
    prerequisites: |
      DUAL_ENGINE_MODE active for ≥4 weeks
      v1.1 metrics replicated across sessions
      no regression detected
    property: |
      Optional gate; system can remain in dual mode indefinitely
      If not passed, no deprecation occurs
  
  DEPRECATION_GATE:
    prerequisites: |
      STABILITY_VALIDATION gate passed
      explicit authorization to deprecate v1.0.0
    property: |
      Final optional gate
      v1.0.0 is moved, not deleted
      can be undone if needed
```

---

## 7. Metric Definitions (What Is Measured, Not How)

```yaml
metrics:
  
  r_eff:
    definition: "Effective rank of covariance matrix"
    measurement_concept: |
      Entropy-based effective rank:
      H = -Σ p_i log(p_i) where p_i = λ_i / Σλ_j
      r_eff = exp(H)
    semantic_meaning: |
      How many independent dimensions explain the telemetry?
      Low r_eff → low-rank structure (good for prediction)
      High r_eff → noise (bad for structure)
    unit: dimensionless
    target_value: ≤ 14
  
  entropy:
    definition: "Spectral entropy of eigenvalue distribution"
    measurement_concept: |
      Shannon entropy of normalized eigenvalues:
      H = -Σ (λ_i / Σλ_j) log(λ_i / Σλ_j)
    semantic_meaning: |
      How concentrated is spectral energy?
      Low entropy → few large eigenvalues (coherent)
      High entropy → uniform distribution (noise-like)
    unit: nats
    target_value: ≤ log(12)
  
  pct_time_stable:
    definition: "Percentage of session time in stable regime"
    measurement_concept: |
      Identify regime transitions (rank jumps > 2)
      Compute median regime duration
      Stable regime = duration > 100 frames
      Report: % of session in stable regimes
    semantic_meaning: |
      Does the system stay in recognizable modes?
      High % → predictable, structured behavior
      Low % → constantly transitioning (chaotic)
    unit: percent
    target_value: ≥ 60%
  
  theta_median:
    definition: "Median subspace rotation angle"
    measurement_concept: |
      For each frame, compute angle between U_k(t) and U_k(t+Δt)
      θ_t = arccos(largest_sv(U_k^T(t) @ U_k(t+Δt)))
      Report: median(θ_t)
    semantic_meaning: |
      How much do principal directions rotate?
      Small θ → geometry is stable
      Large θ → directions constantly shift (no predictive value)
    unit: radians
    target_value: < 0.6 rad
  
  delta_f1:
    definition: "F1 score improvement of regime transitions vs. random"
    measurement_concept: |
      Identify automatically discovered transitions
      Compare with manually labeled scene changes
      Compute F1 score
      Compare vs. baseline (random transition hypothesis)
      Report: ΔF1 = F1_discovered - F1_random
    semantic_meaning: |
      Do discovered regimes align with semantic events?
      High ΔF1 → system captures meaningful structure
      Low ΔF1 → structure is statistical artifact
    unit: dimensionless
    target_value: > 0.20
```

---

## 8. Rules and Constraints (What Is Forbidden, What Is Required)

```yaml
rules:
  
  RULE_1_NO_REFINED_PROTOCOL_TO_Q64:
    type: structural
    states: PRE_H1, H1_VALIDATION_IN_PROGRESS, H1_GATE_CLOSED, H0_ACCEPTED
    constraint: |
      q64 namespace cannot import from refined_protocol
    justification: |
      Candidate layer cannot influence production
      Production path must be independent of research path
  
  RULE_2_NO_Q64_TO_REFINED_PROTOCOL:
    type: structural
    states: all
    constraint: |
      refined_protocol cannot import from q64
    justification: |
      Research candidate must not depend on production code
      Allows independent evolution
  
  RULE_3_CORE_PURITY:
    type: structural
    states: all
    constraint: |
      core/ contains ONLY empirical covariance implementation
      No dependency-matrix code in core/
      No experimental flags in core/
      No research variants in core/
    justification: |
      Production path is unambiguous
      core ≠ paradigm choice point
  
  RULE_4_ANALYSIS_ISOLATION:
    type: structural
    states: all
    constraint: |
      analysis/ cannot import core/ functions
      analysis/ can only read core/ outputs (file I/O)
      analysis/ cannot write to core/
    justification: |
      Evaluation is advisory, not prescriptive
      Prevents evaluation from influencing production
  
  RULE_5_RESEARCH_ISOLATION:
    type: structural
    states: all
    constraint: |
      research/ is never imported by core/
      research/ is never imported by analysis/
      research/ is never imported by protocols/
    justification: |
      Challenger architectures cannot leak into production
      Production stability is independent of research
  
  RULE_6_ARCHIVE_IMMUTABILITY:
    type: structural
    states: all
    constraint: |
      archive/ is read-only
      No modifications, deletions, additions
      Never imported by live code
    justification: |
      Historical reasoning is preserved
      Cannot accidentally reactivate old artifacts
  
  RULE_7_DUAL_ENGINE_COHERENCE:
    type: structural
    states: DUAL_ENGINE_MODE and beyond
    constraint: |
      v1.0.0 and v1.1 do not share mutable state
      Selection via single Q64_ENGINE_MODE flag
      Both engines conform to identical schemas/
    justification: |
      Either engine can be used independently
      No hybrid mode or fallback mixing
  
  RULE_8_SCHEMA_VERSIONING:
    type: structural
    states: all
    constraint: |
      Once schemas/v1.0 is locked, it is immutable
      New schemas must be v1.1, v2.0, etc.
      Never overwrite or modify locked schema versions
    justification: |
      Observable interface is stable
      Historical data remains interpretable
  
  RULE_9_GATE_BINDING:
    type: temporal
    states: H1_VALIDATION_IN_PROGRESS
    constraint: |
      H₁ gate MUST be evaluated at end of Week 5
      Decision is binding (cannot be overridden)
      If H₁ accepted: promotion path opens
      If H₀ accepted: contingency strategy executed
    justification: |
      Validation is external arbiter of system viability
      Gate cannot be skipped or delayed indefinitely
  
  RULE_10_SNAPSHOT_IMMUTABILITY:
    type: temporal
    states: SNAPSHOT_FREEZE
    constraint: |
      During snapshot phase: no code changes to q64/ or refined_protocol/
      Only hotfix patches allowed (documented)
      Both systems are tagged as immutable
    justification: |
      Frozen reference enables auditable promotion
      Prevents code drift during snapshot period
```

---

## 9. Immutability Guarantees (What Cannot Be Changed)

```yaml
immutable_components:
  
  adr_decisions:
    immutability: forever (append-only)
    reason: "Decisions are binding authority"
    enforcement: "git history is source of truth; no rewriting"
  
  schemas_versions:
    immutability: "once locked to vX.Y"
    reason: "Observable interface must be stable"
    enforcement: "semantic versioning enforced; no v1.0 overwrites"
  
  core_v1_0_0:
    immutability: "post-H₁-validation"
    reason: "Baseline must be stable reference"
    enforcement: "code review gate; no edits after freeze tag"
  
  archive:
    immutability: "forever (read-only)"
    reason: "Historical reasoning is proof of decision process"
    enforcement: "no write permissions; git history immutable"
  
  promotion_ordering:
    immutability: "forever"
    reason: "Phases must occur in defined order"
    enforcement: "state machine enforces; no skipping phases"
  
  metrics_definitions:
    immutability: "forever (in this kernel)"
    reason: "What is measured defines success"
    enforcement: "changes only via ADR amendment"
```

---

## Final Property: System Completeness

**This specification is sufficient to understand q64's architecture.**

A human can read this document and understand:
- What components exist and their roles
- How components relate
- What must always be true
- What transitions are possible
- What gates determine outcomes
- What metrics matter and why
- What is forbidden and why

**A human cannot answer from this document:**
- How the CI system works
- How state is persisted
- How metrics are computed
- How enforcement rules are checked
- How transitions are executed at runtime

Those questions belong to the Execution Layer Specification.

---

**Status:** ✅ Authority established  
**Authority:** ADR-001 (this kernel makes ADR-001 executable)  
**Immutability:** Changes only via ADR amendment  
**Subordinate Documents:** Q64_EXECUTION_LAYER_SPEC.md, Q64_KERNEL_BRIDGE.md
