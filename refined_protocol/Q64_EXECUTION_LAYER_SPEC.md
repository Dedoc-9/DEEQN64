# Q64 Execution Layer Specification: Operational Enforcement System

**Version:** 1.0.0-execution-layer  
**Authority:** Implements Q64_GOVERNANCE_KERNEL.md  
**Nature:** Operational interpreter (defines how; does not define what)  
**Mutability:** Replaceable (alternative implementations allowed)

---

## Invariant: This Document Implements Kernel Only

This specification defines:
- How to evaluate rules
- How to compute metrics
- How to track state over time
- How to enforce constraints mechanically
- How CI becomes executable logic
- How to authorize state transitions
- How to verify immutability

This specification does NOT define:
- What the system is (that is kernel)
- What architecture means (that is kernel)
- Why constraints exist (that is kernel)
- What is forbidden or required (that is kernel)

**Property:** This document can be replaced with an alternative implementation without changing q64. Only constraint: behavior must respect Q64_GOVERNANCE_KERNEL.md.

---

## 1. CI Compiler Architecture

### 1.1 Compilation Pipeline (7-Step Process)

```yaml
ci_compiler:
  
  step_1_parse_repo_ast:
    description: "Build import dependency graph from source"
    input: "proposed changeset + current repo state"
    algorithm: |
      for each .py file in changeset:
        parse AST
        extract imports
        build directed graph: module → imports
    output: "import_graph = {module: [imports]}"
    time_complexity: "O(n * m) where n = files, m = imports per file"
  
  step_2_check_import_rules:
    description: "Validate against import constraints (RULE_1 through RULE_10)"
    input: "import_graph, rule_set"
    for_each_rule: |
      pattern_match = regex_search(import_graph, rule.pattern)
      if pattern_match and not rule.exclusion:
        FAIL(rule.message)
    output: "import_violations = []"
    action: |
      if import_violations non-empty:
        return FAIL
      else:
        continue to step 3
  
  step_3_check_write_constraints:
    description: "Validate that writes respect namespace boundaries"
    input: "changeset.files, namespace_definitions"
    algorithm: |
      for each file in changeset.files:
        source_namespace = infer_namespace(file.path)
        for each write_target in file.content:
          sink_namespace = infer_namespace(write_target)
          if (source_namespace, sink_namespace) in forbidden_writes:
            FAIL(cross_namespace_write_violation)
    output: "write_violations = []"
    action: |
      if write_violations non-empty:
        return FAIL
      else:
        continue to step 4
  
  step_4_check_semantic_rules:
    description: "Validate content patterns (no 'empirical' in core, etc.)"
    input: "changeset.files, semantic_rules"
    for_each_rule: |
      for each file in changeset.files:
        if rule.applies_to(file.path):
          content_match = regex_search(file.content, rule.pattern)
          if content_match and not rule.exclusion:
            action = rule.action (WARN or FAIL)
    output: "semantic_violations = []"
    action: |
      if any FAIL violation:
        return FAIL
      else:
        log WARN violations and continue to step 5
  
  step_5_validate_dependency_graph:
    description: "Verify no new forbidden edges introduced"
    input: "import_graph, canonical_dependency_graph"
    algorithm: |
      actual_edges = extract_edges(import_graph)
      canonical_edges = load_from(Q64_GOVERNANCE_KERNEL.md)
      forbidden_edges = load_from(Q64_GOVERNANCE_KERNEL.md)
      
      for each edge in actual_edges:
        if edge in forbidden_edges:
          FAIL(forbidden_edge_violation)
        if edge not in canonical_edges and edge is new:
          FAIL(unauthorized_edge)
    output: "graph_violations = []"
    action: |
      if graph_violations non-empty:
        return FAIL
      else:
        continue to step 6
  
  step_6_check_promotion_state:
    description: "Verify state transition is allowed"
    input: "changeset, current_state from .q64_governance_state.json"
    algorithm: |
      proposed_state = infer_state(changeset)
      
      if proposed_state == current_state:
        continue (no transition)
      else:
        transition = (current_state → proposed_state)
        if transition in Q64_GOVERNANCE_KERNEL.allowed_transitions:
          validate_guards(transition)
        else:
          FAIL(invalid_state_transition)
    output: "state_transition_status"
    action: |
      if transition invalid:
        return FAIL
      else:
        continue to step 7
  
  step_7_evaluate_guards:
    description: "Check guard conditions for proposed transition"
    input: "guard_conditions[current_state → proposed_state]"
    algorithm: |
      for each guard in guards:
        guard_result = evaluate_guard(guard, repo_state)
        if guard_result == FALSE:
          FAIL(guard_condition_not_met: guard.description)
    output: "all_guards_pass = TRUE | FALSE"
    action: |
      if all_guards_pass:
        return PASS (merge allowed)
      else:
        return FAIL (merge blocked)

  final_output:
    status: "PASS | FAIL"
    violations: ["list of specific violations"]
    state_transition: "current_state → proposed_state (if PASS)"
    merge_decision: |
      if status == PASS:
        allow_merge()
        update_state_file()
      else:
        block_merge()
        report_violations()
```

### 1.2 Import Graph Parser (Detailed)

```yaml
import_parser:
  
  language: "Python (can be extended to other languages)"
  
  algorithm:
    step_1_ast_parse:
      for_each: ".py file in changeset"
      action: |
        tree = ast.parse(file.content)
        imports = []
        for node in ast.walk(tree):
          if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append((node.module, node.names))
      result: "imports = [(module, names)]"
    
    step_2_build_graph:
      action: |
        graph = defaultdict(set)
        for (source_module, target_imports) in imports:
          for target in target_imports:
            graph[source_module].add(target.module)
      result: "import_graph = {module: set([imports])}"
    
    step_3_transitive_closure:
      description: "Optional: compute transitive imports"
      action: |
        closure = transitive_closure(graph)
      result: "closure = {module: set([direct + transitive imports])}"
    
    output:
      import_graph: "direct imports only"
      closure: "direct + transitive imports"
```

---

## 2. State Persistence Model

### 2.1 State File (.q64_governance_state.json)

```yaml
state_file_location: ".q64_governance_state.json (repo root)"

file_structure:
  {
    "version": "1.0.0",
    "current_state": "PRE_H1 | H1_VALIDATION_IN_PROGRESS | ...",
    "kernel_version": "1.0.0-kernel-final",
    "timestamps": {
      "initialized_at": "ISO8601",
      "last_transition_at": "ISO8601"
    },
    "snapshots": {
      "q64_hash_v1_0_0": "SHA256(q64/ at time of v1.0.0 freeze)",
      "refined_protocol_hash": "SHA256(refined_protocol/ at time of empirical-final tag)"
    },
    "transitions_log": [
      {
        "timestamp": "ISO8601",
        "from_state": "PRE_H1",
        "to_state": "H1_VALIDATION_IN_PROGRESS",
        "authorized_by": "project_lead_name | automated_evaluate_hypothesis",
        "commit_hash": "git commit SHA",
        "guards_checked": ["guard_name_1", "guard_name_2"],
        "all_guards_pass": true,
        "signature": "gpg_signature (optional, for non-repudiation)"
      }
    ]
  }

properties:
  - source_of_truth: "not git history; this file is authoritative"
  - immutability: "protected; state changes only via authorized transitions"
  - append_only: "log never rewritten; only appended to"
  - validation: "CI verifies consistency with git state before merge"
```

### 2.2 State Validation Protocol

```yaml
state_validation:
  
  on_every_commit:
    check_1: "state_file exists"
    check_2: "state_file is valid JSON"
    check_3: "kernel_version in state_file matches current kernel"
    check_4: "current_state in state_file matches expected state"
    check_5: "transitions_log is append-only (no deletions)"
  
  on_state_transition:
    check_1: "proposed_state is in allowed_transitions[current_state]"
    check_2: "all guard_conditions pass"
    check_3: "commit is clean (no uncommitted changes)"
    check_4: "authorizer has permission for this transition"
    
  on_merge_request:
    check_1: "state_file has not been modified (except append)"
    check_2: "if state transition is proposed, all guards validated"
    check_3: "proposed transition is consistent with code changes"
```

---

## 3. Guard Evaluation System

### 3.1 Guard Condition Evaluation

```yaml
guard_evaluator:
  
  input: "guard_conditions[source_state → destination_state]"
  
  evaluation_engine:
    for_each_guard: |
      guard_name = guard.identifier
      guard_condition = guard.predicate (boolean function)
      repo_state = load_current_repo_state()
      
      try:
        result = guard_condition(repo_state)
        log(guard_name, "evaluated to", result)
      except:
        log_error(guard_name, "evaluation failed")
        return FALSE
      
      if result == FALSE:
        reason = guard.reason_if_failed
        return FALSE with reason
    
    return TRUE if all guards evaluate to TRUE

  guard_definitions:
    
    guard_H1_VALIDATION_READY:
      predicate: |
        hardware_ready(ASUS_ROG_ALLY_X) AND
        telemetry_pipeline_operational() AND
        test_integration_empirical_all_passing() AND
        refined_protocol_snapshot_frozen()
      reason_if_failed: "Not all prerequisites for validation ready"
    
    guard_H1_GATE_SATISFIED:
      predicate: |
        metric_count >= 4 AND
        r_eff <= 14 AND
        entropy <= log(12) AND
        pct_time_stable >= 0.60 AND
        theta_median < 0.6 AND
        delta_f1 > 0.20
      reason_if_failed: "Insufficient metrics pass; H₀ hypothesis accepted"
    
    guard_SNAPSHOT_FROZEN:
      predicate: |
        q64_repo_clean(no_uncommitted_changes) AND
        refined_protocol_repo_clean(no_uncommitted_changes) AND
        tag_exists("v1.0.0-freeze") AND
        tag_exists("v1.0.0-empirical-final") AND
        time_since_freeze >= 1_hour (audit trail)
      reason_if_failed: "Snapshot not ready or not frozen long enough"
    
    guard_CODE_PROMOTION_READY:
      predicate: |
        snapshot_freeze_complete AND
        core_dynamics_v1_1_not_in_q64 AND
        refined_protocol_core_dynamics_empirical_exists
      reason_if_failed: "Code is not ready for promotion"
    
    guard_DUAL_ENGINE_READY:
      predicate: |
        code_promotion_complete AND
        q64_contains(core_dynamics_v1_1.py) AND
        q64_contains(analysis/empirical_tools.py) AND
        config_defines(Q64_ENGINE_MODE)
      reason_if_failed: "Dual engine infrastructure not in place"
    
    guard_STABILITY_PROVEN:
      predicate: |
        weeks_in_dual_mode >= 4 AND
        h1_metrics_replicated_across_sessions(ε=0.05) AND
        latency_regression <= 10_percent AND
        memory_regression <= 10_percent AND
        no_new_failures_in_production
      reason_if_failed: "Stability not proven or regression detected"
    
    guard_DEPRECATION_AUTHORIZED:
      predicate: |
        stability_validation_complete AND
        project_lead_authorized_deprecation AND
        v1_0_0_preserved_in_deprecated_folder
      reason_if_failed: "Deprecation not authorized or v1.0.0 not preserved"
```

---

## 4. Metric Computation Pipeline

### 4.1 Effective Rank Computation (r_eff)

```yaml
compute_r_eff:
  
  input: "telemetry_centered (N×d matrix, mean-centered)"
  
  algorithm:
    step_1: |
      Compute Gram matrix:
      G = (1/N) * telemetry_centered.T @ telemetry_centered
    
    step_2: |
      Compute eigenvalues (all):
      λ = eigh(G, return_eigenvalues_only=True)
      λ_sorted = sort(λ, reverse=True)
    
    step_3: |
      Normalize to probability distribution:
      p = λ_sorted / sum(λ_sorted)
      p = clip(p, min=1e-10)  # avoid log(0)
    
    step_4: |
      Compute Shannon entropy:
      H = -sum(p * log(p))
    
    step_5: |
      Convert to effective rank:
      r_eff = exp(H)
  
  output: "r_eff (scalar, typically 1-30)"
  
  validation:
    r_eff >= 1: "always true (rank at least 1)"
    r_eff <= d: "always true (rank at most d dimensions)"
    r_eff == 1: "single eigenvalue dominates (rank-1)"
    r_eff == d: "uniform eigenvalue distribution (full rank, noise)"
```

### 4.2 Spectral Entropy Computation

```yaml
compute_entropy:
  
  input: "telemetry_centered (N×d matrix)"
  
  algorithm:
    step_1: |
      Compute Gram matrix:
      G = (1/N) * telemetry_centered.T @ telemetry_centered
    
    step_2: |
      Compute eigenvalues (all):
      λ = eigh(G, return_eigenvalues_only=True)
    
    step_3: |
      Normalize:
      p = λ / sum(λ)
      p = clip(p, min=1e-10)
    
    step_4: |
      Compute entropy:
      H = -sum(p * log(p))
  
  output: "H (nats, typically 0 to log(d))"
  
  interpretation:
    H ≈ 0: "single eigenvalue dominates"
    H ≈ log(d): "uniform distribution (white noise)"
```

### 4.3 Regime Persistence Computation

```yaml
compute_pct_time_stable:
  
  input: "telemetry_centered (N×d matrix, time-indexed)"
  
  algorithm:
    step_1_detect_transitions: |
      For each frame t:
        compute rank_t = count(λ_i > τ * max(λ))
      
      For each frame t:
        if |rank_t - rank_{t-1}| >= 2:
          mark_transition(t)
    
    step_2_identify_regimes: |
      regimes = []
      for each contiguous segment between transitions:
        regime = {
          start_frame: t_start,
          end_frame: t_end,
          duration_frames: t_end - t_start,
          rank: rank[t_start],
          stable: duration_frames > 100
        }
        regimes.append(regime)
    
    step_3_compute_stability_fraction: |
      total_frames = len(telemetry_centered)
      stable_frames = sum(r.duration for r in regimes if r.stable)
      pct_time_stable = stable_frames / total_frames
  
  output: "pct_time_stable (percentage, 0-100)"
```

### 4.4 Subspace Angle Computation

```yaml
compute_theta_median:
  
  input: "telemetry_centered (N×d matrix)"
  
  algorithm:
    step_1_compute_subspaces: |
      For each frame t (stride = 5):
        U_k_t = top_k_eigenvectors(G_t)
        U_k_t_plus_delta = top_k_eigenvectors(G_{t+Δt})
    
    step_2_compute_angles: |
      angles = []
      for each pair (t, t+Δt):
        M = U_k_t.T @ U_k_t_plus_delta
        singular_values = svd(M, return_singular_values_only=True)
        largest_sv = singular_values[0]
        θ_t = arccos(clip(largest_sv, -1, 1))
        angles.append(θ_t)
    
    step_3_compute_median: |
      θ_median = median(angles)
  
  output: "θ_median (radians, 0 to π/2)"
```

### 4.5 Transition F1 Score Computation

```yaml
compute_delta_f1:
  
  input: |
    discovered_transitions (from rank jumps)
    manual_labels (from human annotation)
    frame_tolerance = 30 frames (±30 allowed error)
  
  algorithm:
    step_1_match_transitions: |
      tp = 0  # true positives
      fp = 0  # false positives
      fn = 0  # false negatives
      
      for each discovered_transition d:
        matched = False
        for each manual_label m:
          if |d - m| <= frame_tolerance:
            tp += 1
            matched = True
            break
        if not matched:
          fp += 1
      
      for each manual_label m:
        if no discovered transition within frame_tolerance:
          fn += 1
    
    step_2_compute_f1: |
      precision = tp / (tp + fp) if (tp + fp) > 0 else 0
      recall = tp / (tp + fn) if (tp + fn) > 0 else 0
      f1_discovered = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    step_3_baseline_f1: |
      f1_random = random_transition_hypothesis(manual_labels, telemetry_length)
    
    step_4_compute_delta: |
      delta_f1 = f1_discovered - f1_random
  
  output: "delta_f1 (scalar, typically -0.2 to 0.5)"
```

---

## 5. Transition Authorization System

### 5.1 State Transition Authorization Protocol

```yaml
authorization_protocol:
  
  for_each_transition: "(source_state → destination_state)"
    
    step_1_verify_authorization:
      check: "is authorizer in allowed_authorizers[transition]?"
      allowed_authorizers:
        PRE_H1_to_H1_VALIDATION: ["project_lead"]
        H1_VALIDATION_to_H1_GATE_CLOSED: ["automated (evaluate_hypothesis)"]
        H1_GATE_to_SNAPSHOT_FREEZE: ["project_lead"]
        SNAPSHOT_FREEZE_to_CODE_PROMOTION: ["project_lead"]
        CODE_PROMOTION_to_DUAL_ENGINE: ["project_lead"]
        DUAL_ENGINE_to_STABILITY_VALIDATION: ["project_lead"]
        STABILITY_VALIDATION_to_DEPRECATION: ["project_lead"]
        H1_VALIDATION_to_H0_ACCEPTED: ["automated (evaluate_hypothesis)"]
    
    step_2_validate_guards: |
      for each guard in guard_conditions[source → destination]:
        if not evaluate_guard(guard):
          return REJECT with reason
    
    step_3_update_state_file: |
      append_to_transitions_log({
        timestamp: now(),
        from_state: source_state,
        to_state: destination_state,
        authorized_by: authorizer_name,
        commit_hash: current_commit_sha,
        guards_checked: [guard names],
        all_guards_pass: true,
        signature: gpg_sign_transition()
      })
      
      write_state_file(current_state = destination_state)
    
    step_4_return: |
      return ACCEPT
```

---

## 6. Freeze Verification System

### 6.1 Hash-Based Immutability Verification

```yaml
freeze_verification:
  
  at_snapshot_freeze:
    action: |
      h_q64_v1_0_0 = HASH(q64_directory)
      h_refined_v1_0_0_empirical = HASH(refined_protocol_directory)
      
      store in .q64_governance_state.json:
        snapshots.q64_hash_v1_0_0 = h_q64_v1_0_0
        snapshots.refined_protocol_hash = h_refined_v1_0_0_empirical
  
  during_promotion_phases:
    validation: |
      current_h_q64 = HASH(q64_directory)
      stored_h_q64 = state_file.snapshots.q64_hash_v1_0_0
      
      if current_h_q64 == stored_h_q64:
        frozen_state_verified = TRUE
      else:
        git_diff = git_diff(snapshot_tag, HEAD)
        allowed_diffs = ["hotfix patches", "documentation updates"]
        if git_diff in allowed_diffs:
          frozen_state_verified = TRUE
        else:
          frozen_state_verified = FALSE
  
  properties:
    - prevents_code_drift: "changes are detectable"
    - allows_hotfixes: "documented exceptions permitted"
    - auditable: "all diffs from frozen baseline available"
```

---

## 7. Enforcement Timing Model

### 7.1 When Each Check Happens

```yaml
enforcement_timing:
  
  on_commit_push:
    stage_1_pre_commit_hook:
      - import_rules validation
      - semantic_rules validation
      - no_write_outside_namespace check
      timing: < 100ms
    
    stage_2_ci_pipeline:
      - full CI compiler (steps 1-7)
      - state consistency check
      - guard evaluation
      timing: < 5s
  
  on_merge_request:
    stage_1_automated_checks:
      - dependency_graph validation
      - state_transition validation
      - guard_conditions evaluation
      timing: < 10s
      
      action: |
        if PASS:
          mark merge as "governance-approved"
        else:
          block merge with violation report
    
    stage_2_human_review:
      - code review (separate from governance)
      - semantic review (separate from automation)
  
  on_merge_commit:
    stage_1_post_merge:
      - verify state_file consistency
      - log transition in append-only log
      - tag commit with transition metadata
      
      action: |
        if state_file update required:
          commit state_file change
          record in transitions_log
```

---

## 8. Merge Gating System

### 8.1 Merge Approval Logic

```yaml
merge_gate:
  
  input: "pull_request (with proposed changeset)"
  
  evaluation:
    step_1_run_ci_compiler: |
      result = ci_compiler(changeset)
      if result.status == FAIL:
        return BLOCK with result.violations
    
    step_2_check_state_consistency: |
      if state_transition proposed:
        guards = guard_conditions[source → destination]
        if not all_guards_pass(guards):
          return BLOCK with guard_failures
    
    step_3_human_approval: |
      (separate process; not automated)
  
  output:
    status: "APPROVED | BLOCKED"
    reason: "list of violations or approval summary"
    next_action: "merge allowed" or "fix violations and resubmit"
```

---

## Final Property: Replaceability

**This execution layer is a pluggable implementation.**

An alternative execution layer could provide the same guarantees via:
- Different CI tool (not AST-based, but still enforces rules)
- Different state persistence (not JSON, but still append-only and immutable)
- Different metric computation (same result, different algorithm)

Only constraint: must enforce all rules in Q64_GOVERNANCE_KERNEL.md.

---

**Status:** ✅ Implementation specified  
**Authority:** Implements Q64_GOVERNANCE_KERNEL.md only  
**Mutability:** Replaceable (alternative implementations allowed if kernel-compliant)  
**Subordinate To:** Q64_GOVERNANCE_KERNEL.md (authority), Q64_KERNEL_BRIDGE.md (mapping)
