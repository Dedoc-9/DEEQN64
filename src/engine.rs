//! Q64 Stratified Engine implementation

use crate::error::Result;
use crate::metrics::DomainMetrics;
use crate::operator::Q64Operator;
use std::collections::HashMap;

/// Single-domain Q64 operator
pub struct Q64DomainEngine {
    /// Domain name (input, physics, system, rendering)
    pub name: String,

    /// Dimension of domain
    pub n: usize,

    /// Max rank truncation
    pub k: usize,

    /// Q64 operator
    pub operator: Q64Operator,

    /// Current metrics
    pub metrics: DomainMetrics,

    /// Frame count
    pub frame_count: u64,

    /// Convergence history
    pub convergence_history: Vec<bool>,
}

impl Q64DomainEngine {
    /// Create a new domain engine
    pub fn new(name: &str, n: usize, k: usize) -> Self {
        Self {
            name: name.to_string(),
            n,
            k: k.min(n),
            operator: Q64Operator::new(),
            metrics: DomainMetrics::new(),
            frame_count: 0,
            convergence_history: Vec::new(),
        }
    }

    /// Create with custom operator thresholds
    pub fn with_thresholds(name: &str, n: usize, k: usize, operator: Q64Operator) -> Self {
        Self {
            name: name.to_string(),
            n,
            k: k.min(n),
            operator,
            metrics: DomainMetrics::new(),
            frame_count: 0,
            convergence_history: Vec::new(),
        }
    }

    /// Update domain with state vector
    pub fn update(&mut self, state: &[f64]) -> Result<DomainMetrics> {
        if state.len() != self.n {
            return Err(crate::error::Error::InvalidStateDimension(state.len()));
        }

        self.frame_count += 1;

        // Placeholder: In full implementation, run spectral analysis
        self.metrics.converged = self.frame_count > 100; // Simplified for illustration
        self.metrics.rank = (self.k as u64 % (self.frame_count / 50).max(1)) as usize;
        self.convergence_history.push(self.metrics.converged);

        // Update pct_stable
        let stable_count = self.convergence_history.iter().filter(|&&c| c).count();
        self.metrics.pct_stable = stable_count as f64 / self.convergence_history.len() as f64;

        Ok(self.metrics.clone())
    }
}

/// Multi-domain Q64 stratified engine
pub struct Q64StratifiedEngine {
    /// Domain engines
    domains: HashMap<String, Q64DomainEngine>,

    /// Global frame count
    frame_count: u64,
}

impl Q64StratifiedEngine {
    /// Create new stratified engine with default configuration
    pub fn new() -> Self {
        let mut domains = HashMap::new();

        domains.insert(
            "input".to_string(),
            Q64DomainEngine::new("input", 10, 3),
        );
        domains.insert(
            "physics".to_string(),
            Q64DomainEngine::new("physics", 6, 5),
        );
        domains.insert(
            "system".to_string(),
            Q64DomainEngine::new("system", 12, 3),
        );
        domains.insert(
            "rendering".to_string(),
            Q64DomainEngine::new("rendering", 36, 10),
        );

        Self {
            domains,
            frame_count: 0,
        }
    }

    /// Update all domains with 64-dimensional state
    pub fn update(&mut self, state: &[f64]) -> Result<HashMap<String, DomainMetrics>> {
        if state.len() != 64 {
            return Err(crate::error::Error::InvalidStateDimension(state.len()));
        }

        self.frame_count += 1;
        let mut results = HashMap::new();

        // Split state by domain
        let input_state = &state[0..10];
        let physics_state = &state[10..16];
        let system_state = &state[16..28];
        let rendering_state = &state[28..64];

        // Update each domain
        if let Some(engine) = self.domains.get_mut("input") {
            let metrics = engine.update(input_state)?;
            results.insert("input".to_string(), metrics);
        }

        if let Some(engine) = self.domains.get_mut("physics") {
            let metrics = engine.update(physics_state)?;
            results.insert("physics".to_string(), metrics);
        }

        if let Some(engine) = self.domains.get_mut("system") {
            let metrics = engine.update(system_state)?;
            results.insert("system".to_string(), metrics);
        }

        if let Some(engine) = self.domains.get_mut("rendering") {
            let metrics = engine.update(rendering_state)?;
            results.insert("rendering".to_string(), metrics);
        }

        Ok(results)
    }

    /// Evaluate H₁ gate (≥3 of 4 domains pass thresholds)
    pub fn h1_gate_evaluation(&self) -> Result<(bool, HashMap<String, (f64, bool)>)> {
        let thresholds = [
            ("input", 0.80),
            ("physics", 0.70),
            ("system", 0.60),
            ("rendering", 0.40),
        ];

        let mut detail = HashMap::new();
        let mut passing = 0;

        for (name, threshold) in thresholds.iter() {
            if let Some(engine) = self.domains.get(*name) {
                let passes = engine.metrics.pct_stable >= *threshold;
                detail.insert(
                    name.to_string(),
                    (engine.metrics.pct_stable, passes),
                );
                if passes {
                    passing += 1;
                }
            }
        }

        Ok((passing >= 3, detail))
    }
}

impl Default for Q64StratifiedEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_domain_creation() {
        let engine = Q64DomainEngine::new("test", 10, 3);
        assert_eq!(engine.name, "test");
        assert_eq!(engine.n, 10);
        assert_eq!(engine.frame_count, 0);
    }

    #[test]
    fn test_stratified_engine() {
        let engine = Q64StratifiedEngine::new();
        assert_eq!(engine.domains.len(), 4);
    }

    #[test]
    fn test_invalid_state() {
        let mut engine = Q64StratifiedEngine::new();
        let state = vec![0.5; 32]; // Wrong dimension
        assert!(engine.update(&state).is_err());
    }
}
