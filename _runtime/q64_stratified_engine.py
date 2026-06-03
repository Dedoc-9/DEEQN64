"""
Q64 Stratified Multi-Domain Engine
====================================
Implementation of domain-stratified spectral analysis for heterogeneous telemetry.

Architecture:
  - Accepts 64-dimensional heterogeneous state vector
  - Stratifies into 4 independent domains
  - Computes convergence predicate c_t per domain
  - Returns per-domain stability profile

Week 1: Reference validation (synthetic data)
Week 2: Calibration (real game telemetry)
Week 3+: H₁ empirical validation
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DomainMetrics:
    """Per-domain convergence metrics"""
    c_t: bool                    # Convergence predicate
    rank: int                    # Estimated rank
    R_t: float                   # Residual norm
    L_t: float                   # Drift functional
    rank_stable: bool            # Rank stable over window?
    drift_stable: bool           # Drift bounded?
    time_converged: int          # Frame when c_t first triggered (-1 if never)
    spectral_gap: float = 0.0    # Davis-Kahan gap: λ_rank - λ_{rank+1}
    conditioning: float = 1.0    # Normalized gap: gap / λ₁ (guard against clustering)
    prediction_error: float = 0.0      # (Rendering domain) eigenvector change magnitude
    rollback: bool = False             # (Rendering domain) speculative prediction failed
    convergence_state: str = "unknown" # "converged", "speculative", or "diverged"


class Q64DomainEngine:
    """Single-domain Q64 operator with convergence detection"""

    def __init__(self, N: int, k: int, name: str, w: int = 20, tau: float = 0.4,
                 epsilon_R: float = 1e-2, delta_L: float = 0.2):
        """
        Initialize a domain-specific Q64 engine.

        Args:
            N: Dimension of this domain
            k: Max rank truncation
            name: Domain identifier (e.g., "input", "physics")
            w: Sliding window size (frames)
            tau: Rank threshold (fraction of max eigenvalue)
            epsilon_R: Residual threshold
            delta_L: Drift threshold (as fraction of L_t)
        """
        self.N = N
        self.k = min(k, N)
        self.name = name
        self.w = w
        self.tau = tau
        self.tau_original = tau
        self.epsilon_R = epsilon_R
        self.delta_L = delta_L

        # State
        self.window: List[np.ndarray] = []
        self.G = np.zeros((N, N))
        self.L_prev = 0.0
        self.rank_history = [0] * 5
        self.frame_count = 0
        self.time_converged = -1
        self.converged_ever = False
        self.convergence_state = "unknown"

        # Soft Recovery state (inherited by rendering, available for physics)
        self.ewma_recovery_mode = False
        self.rollback_frame = -1
        self.tau_locked_until = -1

    def update(self, s_t: np.ndarray) -> DomainMetrics:
        """
        Update the domain engine with a new state vector s_t.

        Args:
            s_t: (N,) state vector for this domain

        Returns:
            DomainMetrics: convergence metrics for this domain
        """
        self.frame_count += 1

        # Layer 1 & 2: Sliding window Gramian update
        self.window.append(s_t.copy())
        if len(self.window) > self.w:
            self.window.pop(0)

        if len(self.window) < 2:
            # Not enough data yet
            return DomainMetrics(
                c_t=False, rank=0, R_t=float('inf'), L_t=0.0,
                rank_stable=False, drift_stable=False,
                time_converged=-1,
                spectral_gap=0.0, conditioning=1.0
            )

        # Compute local covariance
        W = np.array(self.window)
        mu = np.mean(W, axis=0)
        W_centered = W - mu
        self.G = (W_centered.T @ W_centered) / len(self.window)

        # Layer 3: Spectral decomposition
        try:
            vals, vecs = np.linalg.eigh(self.G)
            idx = np.argsort(vals)[::-1]  # Descending order
            vals = vals[idx]
            vecs = vecs[:, idx]
        except np.linalg.LinAlgError:
            # Degenerate case (e.g., rank-deficient data)
            return DomainMetrics(
                c_t=False, rank=0, R_t=float('inf'), L_t=0.0,
                rank_stable=False, drift_stable=False,
                time_converged=self.frame_count,
                spectral_gap=0.0, conditioning=1.0
            )

        Lambda_k = vals[:self.k]
        U_k = vecs[:, :self.k]

        # Layer 4: Rank estimation (soft cutoff with hysteresis to prevent chatter near threshold)
        if Lambda_k[0] > 0:
            threshold_margin = 0.05 * self.tau * Lambda_k[0]
            rank_candidate = np.sum(Lambda_k > (self.tau * Lambda_k[0] - threshold_margin))
            prev_rank = self.rank_history[-1] if self.rank_history else 0
            if abs(int(rank_candidate) - prev_rank) >= 2:
                rank_t = int(rank_candidate)
            else:
                rank_t = prev_rank
        else:
            rank_t = 0

        self.rank_history.append(int(rank_t))
        self.rank_history.pop(0)

        # Layer 4b: Davis-Kahan spectral gap analysis
        spectral_gap = 0.0
        conditioning = 1.0
        if rank_t > 0 and rank_t < len(vals):
            spectral_gap = vals[int(rank_t) - 1] - vals[int(rank_t)]
            conditioning = spectral_gap / (Lambda_k[0] + 1e-10)

        # Layer 6 & 7: Projection operator and residual
        P_t = U_k @ np.diag(Lambda_k) @ U_k.T
        R_t = np.linalg.norm(self.G - P_t @ self.G, ord='fro')

        # Layer 8: Drift functional
        L_t = np.trace(P_t @ P_t)

        # Layer 9: Convergence predicate with scale-normalized residual
        G_scale = Lambda_k[0] + 1e-10
        R_t_normalized = R_t / G_scale
        cond1 = R_t_normalized < self.epsilon_R

        median_rank = int(np.median(self.rank_history))
        rank_range = set(range(max(1, median_rank - 1), median_rank + 2))
        cond2 = all(r in rank_range for r in self.rank_history)

        cond3 = abs(L_t - self.L_prev) < (self.delta_L * L_t) if L_t > 0 else True

        cond4 = conditioning > 0.05 if rank_t > 0 else True

        c_t = cond1 and cond2 and cond3 and cond4

        # Record first convergence
        if c_t and not self.converged_ever:
            self.time_converged = self.frame_count
            self.converged_ever = True

        self.L_prev = L_t

        # Determine convergence state
        if c_t:
            convergence_state = "converged"
        elif self.ewma_recovery_mode:
            convergence_state = "speculative"
        else:
            convergence_state = "diverged"
        self.convergence_state = convergence_state

        return DomainMetrics(
            c_t=c_t,
            rank=int(rank_t),
            R_t=R_t,
            L_t=L_t,
            rank_stable=cond2,
            drift_stable=cond3,
            time_converged=self.time_converged,
            spectral_gap=spectral_gap,
            conditioning=conditioning,
            convergence_state=convergence_state
        )


class RenderingDomainMill(Q64DomainEngine):
    """Rendering domain with Mill-inspired speculative eigenvector dispatch"""

    def __init__(self, N: int, k: int, name: str, w: int = 20, tau: float = 0.4,
                 epsilon_R: float = 1e-2, delta_L: float = 0.2,
                 prediction_threshold: float = 0.15, ewma_alpha_normal: float = 0.4,
                 ewma_alpha_recovery: float = 0.8):
        super().__init__(N, k, name, w, tau, epsilon_R, delta_L)
        self.prediction_threshold = prediction_threshold
        self.ewma_alpha_normal = ewma_alpha_normal
        self.ewma_alpha_recovery = ewma_alpha_recovery

        # Speculative state
        self.lambda_emitted = None
        self.vecs_emitted = None
        self.prediction_error = 0.0
        self.rollback_count = 0
        self.frame_since_rollback = 0

        # Soft Recovery state
        self.ewma_recovery_mode = False
        self.rollback_frame = -1
        self.tau_locked_until = -1
        self.tau_original = tau
        self.convergence_state = "unknown"

    def process_rollback(self, s_t: np.ndarray):
        """Surgically pivot manifold using EWMA + Spectral Gap Anchor"""
        s_col = s_t.reshape(-1, 1)
        self.G = self.ewma_alpha_recovery * self.G + (1 - self.ewma_alpha_recovery) * (s_col @ s_col.T)

        try:
            vals, _ = np.linalg.eigh(self.G)
            vals = np.sort(vals)[::-1]
            gaps = (vals[:-1] - vals[1:]) / (vals[:-1] + 1e-10)
            discovery_limit = min(len(gaps), self.k)
            if discovery_limit > 0:
                best_gap_idx = np.argmax(gaps[:discovery_limit])
                tau_new = (vals[best_gap_idx] + vals[best_gap_idx + 1]) / (2 * vals[0] + 1e-10)
                self.tau = np.clip(tau_new, 0.1, 0.9)
        except np.linalg.LinAlgError:
            pass

        self.ewma_recovery_mode = True
        self.rollback_frame = self.frame_count
        self.tau_locked_until = self.frame_count + 15

    def update(self, s_t: np.ndarray) -> DomainMetrics:
        """Update with speculative dispatch"""
        self.frame_since_rollback += 1
        metrics_base = super().update(s_t)

        # Extract eigenvectors for validation
        if len(self.window) >= 2:
            W = np.array(self.window)
            mu = np.mean(W, axis=0)
            W_centered = W - mu
            G = (W_centered.T @ W_centered) / len(self.window)

            try:
                vals, vecs = np.linalg.eigh(G)
                idx = np.argsort(vals)[::-1]
                vals = vals[idx]
                vecs = vecs[:, idx]
                vecs_new = vecs[:, :self.k]
            except:
                vecs_new = None
        else:
            vecs_new = None

        # Validate prediction
        prediction_error = 0.0
        rollback = False

        # Release τ lock if cooldown expired
        if self.frame_count > self.tau_locked_until and self.tau_locked_until >= 0:
            self.tau = self.tau_original
            self.tau_locked_until = -1

        # Exit recovery mode after 5 frames
        if self.ewma_recovery_mode and (self.frame_count - self.rollback_frame) > 5:
            self.ewma_recovery_mode = False

        # Only validate if window has stabilized
        if self.frame_count > 30:
            if vecs_new is not None and self.vecs_emitted is not None:
                vecs_prev_norm = np.linalg.norm(self.vecs_emitted, ord='fro')
                if vecs_prev_norm > 1e-10:
                    prediction_error = np.linalg.norm(self.vecs_emitted - vecs_new, ord='fro') / vecs_prev_norm

                    if prediction_error > self.prediction_threshold:
                        rollback = True
                        self.process_rollback(s_t)

        # Determine convergence state
        if rollback or self.ewma_recovery_mode:
            convergence_state = "speculative"
        elif metrics_base.c_t:
            convergence_state = "converged"
        else:
            convergence_state = "diverged"

        # Store for next frame
        self.lambda_emitted = metrics_base.rank
        self.vecs_emitted = vecs_new if vecs_new is not None else self.vecs_emitted
        self.convergence_state = convergence_state

        return DomainMetrics(
            c_t=metrics_base.c_t,
            rank=metrics_base.rank,
            R_t=metrics_base.R_t,
            L_t=metrics_base.L_t,
            rank_stable=metrics_base.rank_stable,
            drift_stable=metrics_base.drift_stable,
            time_converged=metrics_base.time_converged,
            spectral_gap=metrics_base.spectral_gap,
            conditioning=metrics_base.conditioning,
            prediction_error=prediction_error,
            rollback=rollback,
            convergence_state=convergence_state
        )


class Q64StratifiedEngine:
    """Multi-domain Q64 engine with per-domain convergence tracking"""

    EWMA_ALPHA_RECOVERY_MAP = {
        "rendering": 0.80,
        "physics": 0.60,
        "system": 0.50,
        "input": 0.70,
    }

    def __init__(self, rendering_speculative: bool = True, prediction_threshold: float = 0.15):
        self.domains = {
            "input": Q64DomainEngine(N=10, k=3, name="input", w=10),
            "physics": Q64DomainEngine(N=6, k=5, name="physics", w=10),
            "system": Q64DomainEngine(N=12, k=3, name="system", w=10),
        }

        if rendering_speculative:
            alpha_recovery = self.EWMA_ALPHA_RECOVERY_MAP.get("rendering", 0.8)
            self.domains["rendering"] = RenderingDomainMill(
                N=36, k=10, name="rendering", w=10,
                prediction_threshold=prediction_threshold,
                ewma_alpha_normal=0.4,
                ewma_alpha_recovery=alpha_recovery
            )
        else:
            self.domains["rendering"] = Q64DomainEngine(N=36, k=10, name="rendering", w=10)

        self.frame_count = 0
        self.metrics_history = {d: [] for d in self.domains}
        self.rendering_speculative = rendering_speculative

    def update(self, s_t: np.ndarray) -> Dict[str, DomainMetrics]:
        if len(s_t) != 64:
            raise ValueError(f"Expected 64-dim state, got {len(s_t)}")

        self.frame_count += 1

        s_input = s_t[0:10]
        s_physics = s_t[10:16]
        s_system = s_t[16:28]
        s_rendering = s_t[28:64]

        results = {}
        for domain_name, domain_vec in [
            ("input", s_input),
            ("physics", s_physics),
            ("system", s_system),
            ("rendering", s_rendering),
        ]:
            engine = self.domains[domain_name]
            metrics = engine.update(domain_vec)
            results[domain_name] = metrics
            self.metrics_history[domain_name].append(metrics)

        return results

    def stability_profile(self) -> Dict[str, bool]:
        return {d: engine.converged_ever for d, engine in self.domains.items()}

    def h1_gate_evaluation(self) -> Tuple[str, float, Dict]:
        """Primary/Secondary H₁ Gate with Confidence Weighting"""
        detail = {}
        domains_converged = 0
        domains_speculative = 0

        for domain_name, engine in self.domains.items():
            if not self.metrics_history[domain_name]:
                detail[domain_name] = {
                    "convergence_state": "unknown",
                    "pct_converged": 0.0,
                    "status": "inactive"
                }
                continue

            metrics_list = self.metrics_history[domain_name]

            converged_count = sum(1 for m in metrics_list if m.convergence_state == "converged")
            speculative_count = sum(1 for m in metrics_list if m.convergence_state == "speculative")

            pct_converged = converged_count / len(metrics_list) if metrics_list else 0.0
            pct_speculative = speculative_count / len(metrics_list) if metrics_list else 0.0

            thresholds = {
                "input": 0.80,
                "physics": 0.70,
                "system": 0.60,
                "rendering": 0.40,
            }

            threshold = thresholds.get(domain_name, 0.5)
            passes_converged = pct_converged >= threshold
            passes_speculative = pct_speculative >= threshold * 0.5

            if passes_converged:
                domains_converged += 1
                status = "converged"
            elif passes_speculative:
                domains_speculative += 1
                status = "recovering"
            else:
                status = "diverged"

            detail[domain_name] = {
                "convergence_state": status,
                "pct_converged": pct_converged,
                "pct_speculative": pct_speculative,
                "threshold": threshold,
            }

        if domains_converged >= 3:
            gate_status = "green"
            confidence = 1.0
        elif domains_converged == 2 and domains_speculative >= 1:
            gate_status = "yellow"
            confidence = 0.7
        elif domains_converged == 2:
            gate_status = "orange"
            confidence = 0.4
        else:
            gate_status = "red"
            confidence = 0.0

        detail["domains_converged"] = domains_converged
        detail["domains_speculative"] = domains_speculative
        detail["gate_status"] = gate_status
        detail["confidence"] = confidence
        detail["soft_go_enabled"] = gate_status in ["green", "yellow"]

        return gate_status, confidence, detail
