//! Build script pour Jarvis Rust Backend
//! 
//! Génère des informations de build intégrées dans le binaire

use vergen::EmitBuilder;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Générer les constantes de build
    EmitBuilder::builder()
        .build_timestamp()
        .git_sha(false)
        .emit()?;

    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=Cargo.toml");
    
    Ok(())
}