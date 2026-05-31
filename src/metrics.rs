//! Convergence metrics for domain evaluation

use serde::{Deserialize, Serialize};

/// Per-domain convergence metrics
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DomainMetrics {
    /// Convergence predicate c_t
    pub converged: bool,

    /// Estimated rank
    pub rank: usize,

    /// Residual norm R_t
    pub residual: f64,

    /// Drift functional L_t
    pub drift: f64,

    /// Rank stable over window
    pub rank_stable: bool,

    /// Drift bounded
    pub drift_stable: bool,

    /// Frame when c_t first triggered (-1 if never)
    pub time_converged: i32,

    /// Percentage of time converged
    pub pct_stable: f64,
}

impl DomainMetrics {
    /// Create new metrics
    pub fn new() -> Self {
        Self {
            converged: false,
            rank: 0,
            residual: f64::INFINITY,
            drift: 0.0,
            rank_stable: false,
            drift_stable: false,
            time_converged: -1,
            pct_stable: 0.0,
        }
    }

    /// Create metrics from components
    pub fn from_components(
        converged: bool,
        rank: usize,
        residual: f64,
        drift: f64,
    ) -> Self {
        Self {
            converged,
            rank,
            residual,
            drift,
            rank_stable: false,
            drift_stable: false,
            time_converged: if converged { 0 } else { -1 },
            pct_stable: if converged { 1.0 } else { 0.0 },
        }
    }

    /// Check if domain passes H₁ criteria
    pub fn passes_h1_threshold(&self, threshold: f64) -> bool {
        self.pct_stable >= threshold
    }
}

impl Default for DomainMetrics {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_creation() {
        let metrics = DomainMetrics::new();
        assert!(!metrics.converged);
        assert_eq!(metrics.rank, 0);
    }

    #[test]
    fn test_h1_threshold() {
        let mut metrics = DomainMetrics::new();
        metrics.pct_stable = 0.75;
        assert!(metrics.passes_h1_threshold(0.70));
        assert!(!metrics.passes_h1_threshold(0.80));
    }
}
