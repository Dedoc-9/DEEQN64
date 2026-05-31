//! DEEQN64: Q64 Spectral Stability Certification Engine
//!
//! A high-performance Rust implementation of the Q64 spectral stability operator
//! for real-time structural certification of complex systems.
//!
//! # Overview
//!
//! Q64 is a nonlinear stochastic dynamical system that certifies structural
//! stability through spectral analysis. It stratifies heterogeneous system state
//! into independent domains and detects convergence to low-rank manifolds.
//!
//! # Features
//!
//! - **Stratified spectral analysis** — Independent analysis per domain
//! - **Real-time convergence detection** — Low-rank manifold detection
//! - **Immutable state binding** — Hash-verified state evolution
//! - **Python bindings** — C-compatible FFI for Python integration
//!
//! # Example
//!
//! ```rust,no_run
//! use deeqn64::Q64StratifiedEngine;
//!
//! let mut engine = Q64StratifiedEngine::new();
//! let state = vec![0.5; 64];
//! let metrics = engine.update(&state)?;
//!
//! for (domain, metric) in metrics.iter() {
//!     println!("{}: converged={}", domain, metric.converged);
//! }
//! # Ok::<(), deeqn64::Error>(())
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs)]

pub mod engine;
pub mod error;
pub mod metrics;
pub mod operator;

// Re-export main types
pub use engine::{Q64DomainEngine, Q64StratifiedEngine};
pub use error::{Error, Result};
pub use metrics::DomainMetrics;
pub use operator::Q64Operator;

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Python FFI binding module (only compiled when `python` feature is enabled)
#[cfg(feature = "python")]
pub mod python {
    use pyo3::prelude::*;
    use crate::Q64StratifiedEngine;

    /// Python wrapper for Q64StratifiedEngine
    #[pyclass]
    pub struct PyQ64Engine {
        engine: Q64StratifiedEngine,
    }

    #[pymethods]
    impl PyQ64Engine {
        /// Create a new Q64 stratified engine
        #[new]
        pub fn new() -> Self {
            Self {
                engine: Q64StratifiedEngine::new(),
            }
        }

        /// Update engine with 64-dimensional state vector
        pub fn update(&mut self, state: Vec<f64>) -> PyResult<Vec<(String, (bool, usize))>> {
            self.engine
                .update(&state)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
                .map(|metrics| {
                    metrics
                        .iter()
                        .map(|(k, v)| (k.clone(), (v.converged, v.rank)))
                        .collect()
                })
        }

        /// Evaluate H₁ gate
        pub fn h1_gate(&self) -> PyResult<(bool, Vec<(String, f64)>)> {
            self.engine
                .h1_gate_evaluation()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
                .map(|(passes, detail)| {
                    let pct_stable: Vec<_> = detail
                        .iter()
                        .map(|(k, v)| (k.clone(), v.pct_stable))
                        .collect();
                    (passes, pct_stable)
                })
        }
    }

    /// Python module initialization
    #[pymodule]
    pub fn deeqn64(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_class::<PyQ64Engine>()?;
        m.add("__version__", env!("CARGO_PKG_VERSION"))?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
    }
}
