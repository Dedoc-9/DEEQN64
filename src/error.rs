//! Error types for DEEQN64

use thiserror::Error;

/// DEEQN64 error type
#[derive(Error, Debug)]
pub enum Error {
    /// Invalid state dimension
    #[error("Invalid state dimension: expected 64, got {0}")]
    InvalidStateDimension(usize),

    /// Convergence predicate not satisfied
    #[error("Convergence predicate not satisfied: {reason}")]
    ConvergencePredicateFailed { reason: String },

    /// Numerical computation failed
    #[error("Numerical computation failed: {0}")]
    NumericalError(String),

    /// Invalid threshold parameters
    #[error("Invalid threshold: {0}")]
    InvalidThreshold(String),

    /// IO error
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    /// Serialization error
    #[error("Serialization error: {0}")]
    SerializationError(String),

    /// Other errors
    #[error("{0}")]
    Other(String),
}

/// Result type alias
pub type Result<T> = std::result::Result<T, Error>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_dimension() {
        let err = Error::InvalidStateDimension(32);
        assert!(err.to_string().contains("expected 64"));
    }

    #[test]
    fn test_error_display() {
        let err: Result<()> = Err(Error::InvalidThreshold("tau > 1.0".into()));
        assert!(err.is_err());
    }
}
