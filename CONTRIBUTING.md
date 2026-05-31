# Contributing to DEEQN64

Thank you for your interest in contributing to Q64! This document outlines the contribution process, code standards, and requirements for submissions.

---

## Code of Conduct

- Be respectful and constructive in all interactions
- Welcome diverse perspectives and backgrounds
- Focus on technical merit and project goals
- Report violations to project maintainers

---

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** to avoid duplicates
2. **Provide clear reproduction steps** for bugs
3. **Include environment info:**
   - Python version
   - OS platform
   - Output of `pip list | grep -E "numpy|scipy|h5py|pandas|matplotlib|pyyaml"`
4. **Be specific:** Show error messages, code snippets, and expected vs. actual behavior

### Proposing Changes

For significant changes (new domains, threshold modifications, algorithmic changes):

1. **Open a discussion issue** first—don't send a large PR without discussion
2. **Explain motivation:** Why is this change needed?
3. **Propose design:** How would it work?
4. **Outline validation:** How will you verify it works?

### Submitting Code

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Write code** following the style guide below
4. **Add tests** for all new functionality
5. **Update documentation** (README.md, DEVELOPMENT.md, docstrings)
6. **Submit a pull request** with clear description

---

## Code Standards

### Style Guide

**Python:**
- Follow PEP 8 (use `black` or `autopep8` for formatting)
- Use type hints where possible
- Keep functions under 50 lines when feasible
- Use descriptive variable names

Example:
```python
def compute_spectral_residual(covariance: np.ndarray, projection: np.ndarray) -> float:
    """
    Compute Frobenius norm of residual between covariance and projection.
    
    Args:
        covariance: (N, N) symmetric positive semi-definite matrix
        projection: (N, N) rank-truncated projection operator
    
    Returns:
        Residual norm ||covariance - projection @ covariance||_F
    """
    residual = covariance - projection @ covariance
    return np.linalg.norm(residual, ord='fro')
```

### Docstring Format

Use NumPy-style docstrings:

```python
def update(self, s_t: np.ndarray) -> DomainMetrics:
    """
    Update domain engine with new state vector.
    
    Args:
        s_t: (N,) state vector for this domain
    
    Returns:
        DomainMetrics: convergence metrics including c_t predicate, rank, residual
    
    Raises:
        ValueError: If s_t.shape != (N,)
    """
```

### Comments

- Comment *why*, not *what*
- Use comments for non-obvious logic
- Keep comments up-to-date with code changes

Example:
```python
# Relax rank stability: allow rank to vary within ±1 of median
# (Previously required exact equality, which was too strict for noisy data)
median_rank = int(np.median(self.rank_history))
rank_range = set(range(max(1, median_rank - 1), median_rank + 2))
cond2 = all(r in rank_range for r in self.rank_history)
```

---

## Testing Requirements

### All Code Changes Must Include Tests

**New functions:** Add unit tests in appropriate test file  
**Bug fixes:** Add regression test that would fail with old code  
**Threshold changes:** Re-run synthetic data tests with new thresholds

### Running Tests

```bash
cd _runtime
python q64_reference_test.py
```

### Test File Structure

```python
def test_new_feature():
    """Test description of what is being validated."""
    # Setup
    engine = Q64StratifiedEngine()
    
    # Execute
    result = engine.some_method()
    
    # Assert
    assert result.expected_property == expected_value, "Error message"
    print("✓ Test passed")
```

### Test Coverage Goals

- Unit tests for all public methods
- Integration tests for pipeline components
- Synthetic data validation for new domains/operators

---

## Threshold and Parameter Changes

**Critical:** Any changes to convergence thresholds (ε_R, δ_L, τ, w) must:

1. **Be justified** with clear reasoning
2. **Re-validate** on synthetic data (run `q64_reference_test.py`)
3. **Document** the change in commit message and DEVELOPMENT.md
4. **Include** before/after performance metrics

Example commit message:
```
Increase residual threshold ε_R from 1e-2 to 2e-2

Motivation: Phase 2a testing revealed real game data has higher
noise floor than synthetic test data. Original threshold was too
strict, preventing convergence on valid low-rank structures.

Validation:
- Re-ran q64_reference_test.py: 3/3 PASS with new threshold
- No false positives on synthetic data
- Expect 15-20% increase in convergence rate on game telemetry

Related: #123
```

---

## Domain and Architecture Changes

Adding new domains or modifying stratification:

1. **Update domain configuration** (DEVELOPMENT.md, Q64_IMPLEMENTATION_PLAN.md)
2. **Specify new k (rank bound)** with justification
3. **Implement StateVectorAssembler** mapping for new domain
4. **Add domain-specific tests** to q64_reference_test.py
5. **Update H₁ threshold** (if new domain has different complexity)
6. **Document rationale** in commit message

Example: Adding a new "Network" domain (dims 64-75, k=8)
```python
# Update domain config
self.domains["network"] = Q64DomainEngine(
    N=12, k=8, name="network", w=20, ...
)

# Update state splitting
s_network = s_t[64:76]  # dims 64-75, 12 total

# Add H₁ threshold
thresholds["network"] = 0.50  # network is variable; lower bar

# Add test
def test_network_domain():
    """Verify network domain converges independently."""
    # ... test code ...
```

---

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Code follows style guide
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change needed? Link to issues if applicable.

## Changes
- Specific change 1
- Specific change 2

## Testing
How was this tested? Include test results or console output.

## Checklist
- [ ] Tests pass (run `cd _runtime && python q64_reference_test.py`)
- [ ] Documentation updated
- [ ] Commits are atomic and well-described
- [ ] No breaking API changes
```

### Review Process

1. At least one maintainer review required
2. All tests must pass (CI/CD checks)
3. Address review feedback
4. Maintainer merges when approved

---

## Documentation

### Update These Files When:

| Change | Update |
|--------|--------|
| New tasks / timeline changes | DEVELOPMENT.md § Phase X |
| New public API / functions | README.md § Usage |
| Algorithm changes | relevant spec file in refined_protocol/ |
| Bug fixes | DEVELOPMENT.md § Known Limitations (if appropriate) |
| New domains | DEVELOPMENT.md § Locked Parameters |

### Docstring Requirements

- All public classes and functions must have docstrings
- Docstrings must include Args, Returns, and (if applicable) Raises
- Include example usage for complex functions

---

## Licensing

By contributing to Q64, you agree that:

1. Your contributions are licensed under AGPL-3.0
2. You have the right to grant this license
3. You understand the implications of AGPL-3.0 (network copyleft)

If you have copyright concerns, discuss with maintainers before submitting.

---

## Questions?

- **For technical questions:** Open an issue at https://github.com/Dedoc-9/DEEQN64/issues
- **For process questions:** Open an issue labeled "question"
- **For security issues:** Do NOT open a public issue. Contact maintainers privately.

---

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md (once file is created)
- Release notes
- GitHub contributors graph

Thank you for helping improve Q64!

---

**Last updated:** Week 1 Complete  
**Maintained by:** Q64 Core Team
