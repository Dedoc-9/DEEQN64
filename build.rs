// Build script for DEEQN64 Rust compilation
// Handles Python binding configuration and native library optimization

fn main() {
    // Set rustc flags for optimization
    println!("cargo:rustc-env=RUSTFLAGS=-C target-cpu=native");

    // Python integration (only when python feature is enabled)
    #[cfg(feature = "pyo3")]
    {
        pyo3_build_config::add_extension_module_link_args();
    }

    // Build configuration messages
    println!("cargo:warning=Building DEEQN64 with LTO enabled (slower build, faster runtime)");

    // Version info
    let version = env!("CARGO_PKG_VERSION");
    println!("cargo:rustc-env=DEEQN64_VERSION={}", version);

    // Feature detection
    let features = std::env::var("CARGO_FEATURE_")
        .unwrap_or_else(|_| "none".to_string());
    if features.contains("python") {
        println!("cargo:warning=Python bindings enabled");
    }
}
