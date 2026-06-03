"""
Q64 Stratified Multi-Domain Engine (Production Reference Implementation)
==========================================================================
Implementation of domain-stratified spectral analysis for heterogeneous telemetry.

Architecture:
  - Accepts 64-dimensional heterogeneous state vector
  - Stratifies into 4 independent domains (Input 10D, Physics 6D, System 12D, Rendering 36D)
  - Computes convergence predicate c_t per domain with soft recovery
  - Returns per-domain stability profile with confidence scoring
  - Tracks manifold velocity via Grassmannian distance (innovation metric)

Mathematical Foundations:
  - Rank estimation: mode filter on 5-frame persistence window (robust to noise)
  - Residual: PCA truncation ||G - G_k||_F normalized by ||G||_F (scale-invariant)
  - Spectral energy: L_t = Σ λ_i² with symmetric normalized stability check
  - Gap conditioning: log(λ_r / λ_{r+1}) with spectrum floor guard (PSD-clipped)
  - Principal angles: θ_max = arccos(σ_min) for subspace distance (sign-invariant)
  - Innovation: η_t = sqrt(Σ(1 - σ_i²)) as Grassmannian manifold velocity
  - Recovery geometry: EWMA mean/covariance with domain-specific α, speculative confidence decay

Week 1: Reference validation (synthetic data)
Week 2b: Calibration (real TF2 telemetry at 60 Hz)
Week 3+: H₁ empirical validation with soft-go decision automation
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class DomainMetrics:
    """Per-domain convergence and spectral metrics"""
    c_t: bool                      # Convergence predicate (all 4 conditions met)
    rank: int                      # Estimated rank (mode of 5-frame persistence window)
    R_t: float                     # PCA truncation residual: ||G - G_k||_F
    L_t: float                     # Spectral energy: Σ λ_i² (rank stability guard)
    rank_stable: bool              # Rank bounded variability (within ±1 of median)
    drift_stable: bool             # Spectral energy stable (symmetric normalized)
    time_converged: int            # Frame when c_t first triggered (-1 if never)
    spectral_gap: float = 0.0      # Raw gap: λ_r - λ_{r+1}
    gap_ratio: float = 1.0         # Scale-invariant: λ_r / λ_{r+1}
    conditioning: float = 0.0      # log(gap_ratio) for Davis-Kahan guard
    prediction_error: float = 0.0  # Principal angle (subspace distance, rendering only)
    rollback: bool = False         # Speculative prediction failed (rendering only)
    convergence_state: str = "unknown"  # "converged", "speculative", or "diverged"
    speculative_confidence: float = 1.0 # exp(-frames/τ_budget) for soft-go decay
    innovation: float = 0.0        # Grassmannian distance (manifold velocity)


class Q64DomainEngine:
    """Single-domain Q64 operator with convergence detection and shared spectral analysis"""

    # Numerical stability bounds
    SPECTRUM_FLOOR = 1e-8  # Minimum eigenvalue magnitude for gap-ratio computation
    RESIDUAL_SCALE_FLOOR = 1e-10  # Minimum Gramian norm for residual normalization

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
            epsilon_R: Residual threshold (fractional, normalized by ||G||_F)
            delta_L: Drift threshold (fractional, symmetric normalized)
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
        self.rank_candidate_history = []
        self.rank_persistence_window = 5
        self.frame_count = 0
        self.time_converged = -1
        self.converged_ever = False
        self.convergence_state = "unknown"

        # Soft Recovery state
        self.ewma_recovery_mode = False
        self.rollback_frame = -1
        self.tau_locked_until = -1

    def analyze_gramian(self, G: np.ndarray, s_t: np.ndarray = None,
                       update_state: bool = True, warmup: bool = False) -> DomainMetrics:
        """
        Pure spectral analysis: decompose Gramian and extract all convergence metrics.

        Single source of truth for spectral computation.
        Called by both normal and recovery paths.

        Args:
            G: (N, N) covariance/Gramian matrix (will be PSD-clipped)
            s_t: (N,) current state (optional, for diagnostics)
            update_state: bool, whether to update rank/energy history
                         (False during recovery to avoid contaminating convergence statistics)
            warmup: bool, if True, skip analysis and return zeros (insufficient data)

        Returns:
            DomainMetrics with all spectral quantities computed
        """
        if warmup or G is None:
            return DomainMetrics(
                c_t=False, rank=0, R_t=float('inf'), L_t=0.0,
                rank_stable=False, drift_stable=False,
                time_converged=-1,
                spectral_gap=0.0, gap_ratio=1.0, conditioning=0.0
            )

        # === Layer 3: Spectral decomposition with PSD clipping ===
        try:
            vals, vecs = np.linalg.eigh(G)
            vals = np.maximum(vals, 0.0)  # Clip negative eigenvalues (numerical errors)
            idx = np.argsort(vals)[::-1]  # Descending order
            vals = vals[idx]
            vecs = vecs[:, idx]
        except np.linalg.LinAlgError:
            return DomainMetrics(
                c_t=False, rank=0, R_t=float('inf'), L_t=0.0,
                rank_stable=False, drift_stable=False,
                time_converged=self.frame_count,
                spectral_gap=0.0, gap_ratio=1.0, conditioning=0.0
            )

        Lambda_k = vals[:self.k]
        U_k = vecs[:, :self.k]

        # === Layer 4: Rank estimation (mode filter on persistence window) ===
        if Lambda_k[0] > self.SPECTRUM_FLOOR:
            threshold_margin = 0.05 * self.tau * Lambda_k[0]
            rank_candidate = np.sum(Lambda_k > (self.tau * Lambda_k[0] - threshold_margin))
        else:
            rank_candidate = 0

        if update_state:
            self.rank_candidate_history.append(int(rank_candidate))
            if len(self.rank_candidate_history) > self.rank_persistence_window:
                self.rank_candidate_history.pop(0)

            if len(self.rank_candidate_history) == self.rank_persistence_window:
                mode_rank = Counter(self.rank_candidate_history).most_common(1)[0][0]
                rank_t = mode_rank
            else:
                rank_t = self.rank_history[-1] if self.rank_history else 0

            self.rank_history.append(int(rank_t))
            self.rank_history.pop(0)
        else:
            # Recovery mode: report current estimate without updating history
            rank_t = int(rank_candidate)

        # === Layer 4b: Spectral gap and conditioning (scale-invariant) ===
        spectral_gap = 0.0
        gap_ratio = 1.0
        conditioning = 0.0

        if rank_t > 0 and rank_t < len(vals):
            lambda_r = vals[int(rank_t) - 1]
            lambda_r_plus_1 = vals[int(rank_t)]

            spectral_gap = lambda_r - lambda_r_plus_1

            # Gap ratio with spectrum floor guard
            if lambda_r > self.SPECTRUM_FLOOR and lambda_r_plus_1 > self.SPECTRUM_FLOOR:
                gap_ratio = lambda_r / (lambda_r_plus_1 + 1e-10)
                conditioning = np.log(gap_ratio)
            else:
                gap_ratio = 1.0
                conditioning = 0.0

        # === Layer 5 & 6: PCA reconstruction residual (normalized by ||G||_F) ===
        G_k = U_k @ np.diag(Lambda_k) @ U_k.T
        R_t = np.linalg.norm(G - G_k, ord='fro')

        # Normalize by total Gramian energy (not single eigenvalue)
        G_norm = np.linalg.norm(G, ord='fro') + self.RESIDUAL_SCALE_FLOOR
        R_t_normalized = R_t / G_norm

        # === Layer 7: Spectral energy (stability of rank) ===
        spectral_energy = np.sum(Lambda_k ** 2)
        L_t = spectral_energy

        # === Layer 8: Convergence predicates ===
        # cond1: residual bounded (normalized by total energy)
        cond1 = R_t_normalized < self.epsilon_R

        # cond2: rank stable (bounded variability, within ±1 of median)
        median_rank = int(np.median(self.rank_history))
        rank_range = set(range(max(1, median_rank - 1), median_rank + 2))
        cond2 = all(r in rank_range for r in self.rank_history)

        # cond3: spectral energy stable (symmetric normalized, scale-free)
        if L_t > 0 and self.L_prev > 0:
            energy_change = abs(L_t - self.L_prev) / max(L_t, self.L_prev, 1e-10)
            cond3 = energy_change < self.delta_L
        else:
            cond3 = True

        # cond4: Davis-Kahan guard (eigenvalue gap sufficient for reliability)
        cond4 = conditioning > 0.1 if rank_t > 0 else True

        c_t = cond1 and cond2 and cond3 and cond4

        # Record first convergence
        if c_t and not self.converged_ever:
            self.time_converged = self.frame_count
            self.converged_ever = True

        if update_state:
            self.L_prev = L_t

        return DomainMetrics(
            c_t=c_t,
            rank=int(rank_t),
            R_t=R_t,
            L_t=L_t,
            rank_stable=cond2,
            drift_stable=cond3,
            time_converged=self.time_converged,
            spectral_gap=spectral_gap,
            gap_ratio=gap_ratio,
            conditioning=conditioning
        )

    def update(self, s_t: np.ndarray) -> DomainMetrics:
        """Standard update path: window-based covariance analysis."""
        self.frame_count += 1

        # Maintain sliding window
        self.window.append(s_t.copy())
        if len(self.window) > self.w:
            self.window.pop(0)

        # Compute window covariance
        if len(self.window) < 2:
            return DomainMetrics(
                c_t=False, rank=0, R_t=float('inf'), L_t=0.0,
                rank_stable=False, drift_stable=False,
                time_converged=-1,
                spectral_gap=0.0, gap_ratio=1.0, conditioning=0.0
            )

        W = np.array(self.window)
        mu = np.mean(W, axis=0)
        W_centered = W - mu
        self.G = (W_centered.T @ W_centered) / len(self.window)

        # Analyze using shared method (with state updates, no warmup)
        metrics = self.analyze_gramian(self.G, s_t, update_state=True, warmup=False)

        # Determine convergence state
        if metrics.c_t:
            self.convergence_state = "converged"
        elif self.ewma_recovery_mode:
            self.convergence_state = "speculative"
        else:
            self.convergence_state = "diverged"

        metrics.convergence_state = self.convergence_state
        metrics.speculative_confidence = 1.0

        return metrics


class RenderingDomainMill(Q64DomainEngine):
    """Rendering domain with Mill-inspired speculative dispatch and soft recovery"""

    def __init__(self, N: int, k: int, name: str, w: int = 20, tau: float = 0.4,
                 epsilon_R: float = 1e-2, delta_L: float = 0.2,
                 prediction_threshold: float = 0.15, ewma_alpha_normal: float = 0.4,
                 ewma_alpha_recovery: float = 0.8):
        super().__init__(N, k, name, w, tau, epsilon_R, delta_L)
        self.prediction_threshold = prediction_threshold
        self.ewma_alpha_normal = ewma_alpha_normal
        self.ewma_alpha_recovery = ewma_alpha_recovery

        # Speculative state
        self.vecs_emitted = None
        self.prediction_error = 0.0
        self.rollback_count = 0

        # Recovery EWMA state
        self.mu_ewma = None
        self.G_ewma = None
        self.recovery_mode_depth = 0
        self.speculative_frame_count = 0
        self.speculative_budget_frames = 40

    def process_rollback(self, s_t: np.ndarray):
        """Initialize EWMA recovery geometry."""
        if self.mu_ewma is None:
            W = np.array(self.window) if self.window else np.zeros((1, self.N))
            self.mu_ewma = np.mean(W, axis=0) if len(W) > 0 else np.zeros(self.N)
            self.G_ewma = self.G.copy()

        # Joint EWMA update (mean + covariance centered)
        self.mu_ewma = (self.ewma_alpha_recovery * self.mu_ewma +
                        (1 - self.ewma_alpha_recovery) * s_t)
        delta = s_t.reshape(-1, 1) - self.mu_ewma.reshape(-1, 1)
        self.G_ewma = (self.ewma_alpha_recovery * self.G_ewma +
                       (1 - self.ewma_alpha_recovery) * (delta @ delta.T))

        # Spectral gap anchor on EWMA geometry
        try:
            vals, _ = np.linalg.eigh(self.G_ewma)
            vals = np.maximum(vals, 0.0)
            vals = np.sort(vals)[::-1]
            gap_ratio = vals[:-1] / (vals[1:] + 1e-10)
            discovery_limit = min(len(gap_ratio), self.k)
            if discovery_limit > 0:
                best_gap_idx = np.argmax(gap_ratio[:discovery_limit])
                tau_new = (vals[best_gap_idx] + vals[best_gap_idx + 1]) / (2 * vals[0] + 1e-10)
                self.tau = np.clip(tau_new, 0.1, 0.9)
        except np.linalg.LinAlgError:
            pass

        # Enter recovery mode
        self.ewma_recovery_mode = True
        self.rollback_frame = self.frame_count
        self.tau_locked_until = self.frame_count + 15
        self.recovery_mode_depth = 0
        self.speculative_frame_count = 0
        self.rollback_count += 1

    def principal_angle_max(self, U1: np.ndarray, U2: np.ndarray) -> float:
        """Largest principal angle between subspaces (sign-invariant, conservative)."""
        try:
            _, sigma, _ = np.linalg.svd(U1.T @ U2, full_matrices=False)
            sigma = np.clip(sigma, -1.0, 1.0)
            theta_max = np.arccos(sigma[-1])  # Smallest singular value → largest angle
            error = theta_max / (np.pi / 2)
        except (np.linalg.LinAlgError, IndexError):
            error = 1.0
        return error

    def grassmannian_distance(self, U1: np.ndarray, U2: np.ndarray) -> float:
        """
        Geodesic distance on Grassmannian manifold (manifold velocity).

        Measures rate of subspace rotation: η_t = sqrt(Σ(1 - σ_i²))
        where σ_i = singular values of U1^T @ U2 (cosines of principal angles)

        Returns:
            innovation ∈ [0, sqrt(k)] | manifold rotation rate
            0 = identical subspaces (no change)
            sqrt(k) = completely orthogonal (maximum rotation)
        """
        try:
            _, sigma, _ = np.linalg.svd(U1.T @ U2, full_matrices=False)
            sigma = np.clip(sigma, -1.0, 1.0)
            # Grassmannian distance: sqrt(sum of squared sines of angles)
            innovation = np.sqrt(np.sum(1 - sigma**2))
        except (np.linalg.LinAlgError, IndexError):
            innovation = np.sqrt(min(U1.shape[1], U2.shape[1]))
        return innovation

    def update(self, s_t: np.ndarray) -> DomainMetrics:
        """Update with speculative dispatch."""
        self.frame_count += 1

        # === Release τ lock if cooldown expired ===
        if self.frame_count > self.tau_locked_until and self.tau_locked_until >= 0:
            self.tau = self.tau_original
            self.tau_locked_until = -1

        # === Window synchronization (always append, regardless of mode) ===
        self.window.append(s_t.copy())
        if len(self.window) > self.w:
            self.window.pop(0)

        # === Conditional geometry: recovery vs. normal ===
        if self.ewma_recovery_mode:
            # Recovery branch: use EWMA geometry
            self.recovery_mode_depth += 1

            # Joint EWMA update (same as process_rollback)
            self.mu_ewma = (self.ewma_alpha_recovery * self.mu_ewma +
                            (1 - self.ewma_alpha_recovery) * s_t)
            delta = s_t.reshape(-1, 1) - self.mu_ewma.reshape(-1, 1)
            self.G_ewma = (self.ewma_alpha_recovery * self.G_ewma +
                           (1 - self.ewma_alpha_recovery) * (delta @ delta.T))

            # Analyze EWMA geometry (no state contamination)
            metrics = self.analyze_gramian(self.G_ewma, s_t, update_state=False, warmup=False)

            # Exit recovery after 5 frames
            if self.recovery_mode_depth > 5:
                self.ewma_recovery_mode = False
                self.mu_ewma = None
                self.G_ewma = None
        else:
            # Normal branch: use window covariance
            if len(self.window) < 2:
                return DomainMetrics(
                    c_t=False, rank=0, R_t=float('inf'), L_t=0.0,
                    rank_stable=False, drift_stable=False,
                    time_converged=-1, spectral_gap=0.0, gap_ratio=1.0,
                    conditioning=0.0)

            W = np.array(self.window)
            mu = np.mean(W, axis=0)
            W_centered = W - mu
            self.G = (W_centered.T @ W_centered) / len(self.window)

            # Analyze window geometry (with state updates)
            metrics = self.analyze_gramian(self.G, s_t, update_state=True, warmup=False)

        # === Extract eigenvectors for validation ===
        vecs_new = None
        if len(self.window) >= 2:
            try:
                G_for_vecs = self.G_ewma if self.ewma_recovery_mode else self.G
                vals, vecs = np.linalg.eigh(G_for_vecs)
                vals = np.maximum(vals, 0.0)
                idx = np.argsort(vals)[::-1]
                vecs = vecs[:, idx]
                vecs_new = vecs[:, :self.k]
            except:
                vecs_new = None

        # === Validate prediction (only in normal mode, after warm-up) ===
        prediction_error = 0.0
        innovation = 0.0
        rollback = False

        # Compute manifold velocity (Grassmannian distance) whenever eigenvectors available
        if vecs_new is not None and self.vecs_emitted is not None:
            innovation = self.grassmannian_distance(self.vecs_emitted, vecs_new)

        if self.frame_count > 30 and not self.ewma_recovery_mode:
            if vecs_new is not None and self.vecs_emitted is not None:
                # Principal angle metric (sign-invariant)
                prediction_error = self.principal_angle_max(self.vecs_emitted, vecs_new)

                if prediction_error > self.prediction_threshold:
                    rollback = True
                    self.process_rollback(s_t)

        # === Store for next frame speculation ===
        self.vecs_emitted = vecs_new if vecs_new is not None else self.vecs_emitted

        # === Determine convergence state ===
        if rollback or self.ewma_recovery_mode:
            convergence_state = "speculative"
        elif metrics.c_t:
            convergence_state = "converged"
        else:
            convergence_state = "diverged"

        # === Track speculative duration for confidence decay ===
        if convergence_state == "speculative":
            self.speculative_frame_count += 1
        else:
            self.speculative_frame_count = 0

        speculative_confidence = np.exp(-self.speculative_frame_count / self.speculative_budget_frames)

        # === Return metrics with rendering-specific fields ===
        metrics.prediction_error = prediction_error
        metrics.rollback = rollback
        metrics.convergence_state = convergence_state
        metrics.speculative_confidence = speculative_confidence
        metrics.innovation = innovation

        return metrics


class Q64StratifiedEngine:
    """Multi-domain Q64 engine with per-domain convergence tracking and graduated H₁ gate"""

    EWMA_ALPHA_RECOVERY_MAP = {
        "rendering": 0.80,  # Visual coherence: instant adaptation
        "physics": 0.60,    # Momentum preservation: smooth blend
        "system": 0.50,     # Hardware baseline: conservative
        "input": 0.70,      # Control inputs: responsive
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
        """Update all domains with a new 64-dimensional state vector."""
        if len(s_t) != 64:
            raise ValueError(f"Expected 64-dim state, got {len(s_t)}")

        self.frame_count += 1

        s_input = s_t[0:10]
        s_physics = s_t[10:16]
        s_system = s_t[16:28]
        s_rendering = s_t[28:64]

        results = {}
        for domain_name, domain_vec in [("input", s_input), ("physics", s_physics),
                                         ("system", s_system), ("rendering", s_rendering)]:
            engine = self.domains[domain_name]
            metrics = engine.update(domain_vec)
            results[domain_name] = metrics
            self.metrics_history[domain_name].append(metrics)

        return results

    def stability_profile(self) -> Dict[str, bool]:
        """Return current convergence status for all domains"""
        return {d: engine.converged_ever for d, engine in self.domains.items()}

    def h1_gate_evaluation(self) -> Tuple[str, float, Dict]:
        """
        Graduated H₁ Gate with Confidence Weighting and Speculative Decay.

        Returns (status, confidence, detail):
        - status ∈ {"green", "yellow", "orange", "red"}
        - confidence ∈ [0.0, 1.0] scaled monotonically by domain quality
        - detail: per-domain and aggregate metrics
        """
        detail = {}
        domains_converged = 0
        domains_speculative_weighted = 0.0

        for domain_name, engine in self.domains.items():
            if not self.metrics_history[domain_name]:
                detail[domain_name] = {
                    "convergence_state": "unknown",
                    "pct_converged": 0.0,
                    "status": "inactive"
                }
                continue

            metrics_list = self.metrics_history[domain_name]
            latest_metric = metrics_list[-1]

            # Count convergence states
            converged_count = sum(1 for m in metrics_list if m.convergence_state == "converged")
            speculative_count = sum(1 for m in metrics_list if m.convergence_state == "speculative")

            pct_converged = converged_count / len(metrics_list) if metrics_list else 0.0
            pct_speculative = speculative_count / len(metrics_list) if metrics_list else 0.0

            # Domain-specific thresholds
            thresholds = {
                "input": 0.80,      # Input: rock-solid control
                "physics": 0.70,    # Physics: stable motion tracking
                "system": 0.60,     # System: hardware baseline
                "rendering": 0.40,  # Rendering: most complex, lower bar
            }

            threshold = thresholds.get(domain_name, 0.5)
            passes_converged = pct_converged >= threshold

            if passes_converged:
                domains_converged += 1
                status = "converged"
            elif pct_speculative > 0:
                # Weight by recency and age (confidence decay)
                domains_speculative_weighted += latest_metric.speculative_confidence
                status = "recovering"
            else:
                status = "diverged"

            detail[domain_name] = {
                "convergence_state": status,
                "pct_converged": pct_converged,
                "pct_speculative": pct_speculative,
                "threshold": threshold,
                "latest_confidence": latest_metric.speculative_confidence,
                "innovation": latest_metric.innovation
            }

        # === Gate decision with monotonic confidence scaling ===
        if domains_converged >= 3:
            gate_status = "green"
            confidence = 1.0
        elif domains_converged == 2 and domains_speculative_weighted >= 0.7:
            gate_status = "yellow"
            # Confidence between orange (0.4) and green (1.0)
            # Scale speculative weight into [0.4, 0.7] range monotonically
            normalized_speculative = min(1.0, domains_speculative_weighted / 2.0)
            confidence = 0.4 + 0.3 * normalized_speculative
        elif domains_converged == 2:
            gate_status = "orange"
            confidence = 0.4
        else:
            gate_status = "red"
            confidence = 0.0

        detail["domains_converged"] = domains_converged
        detail["domains_speculative_weighted"] = domains_speculative_weighted
        detail["gate_status"] = gate_status
        detail["confidence"] = confidence
        detail["soft_go_enabled"] = gate_status in ["green", "yellow"]

        return gate_status, confidence, detail
