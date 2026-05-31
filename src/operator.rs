//! Core Q64 operator implementation

/// Q64 spectral operator
///
/// Implements the 10-layer transformation pipeline:
/// Preprocessing → Gram → Eigendecomposition → Rank Estimation
/// → Projection → Residual → Drift Audit → Convergence Predicate → Hash Binding
pub struct Q64Operator {
    /// Window size (frames)
    pub window_size: usize,
    /// Rank threshold (fraction of max eigenvalue)
    pub tau: f64,
    /// Residual threshold
    pub epsilon_r: f64,
    /// Drift threshold
    pub delta_l: f64,
}

impl Q64Operator {
    /// Create a new operator with default thresholds
    pub fn new() -> Self {
        Self {
            window_size: 20,
            tau: 0.4,
            epsilon_r: 1e-2,
            delta_l: 0.2,
        }
    }

    /// Create an operator with custom thresholds
    pub fn with_thresholds(window_size: usize, tau: f64, epsilon_r: f64, delta_l: f64) -> Self {
        Self {
            window_size,
            tau,
            epsilon_r,
            delta_l,
        }
    }
}

impl Default for Q64Operator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_operator_creation() {
        let op = Q64Operator::new();
        assert_eq!(op.window_size, 20);
        assert_eq!(op.tau, 0.4);
    }

    #[test]
    fn test_custom_operator() {
        let op = Q64Operator::with_thresholds(30, 0.5, 2e-2, 0.3);
        assert_eq!(op.window_size, 30);
        assert_eq!(op.tau, 0.5);
    }
}
