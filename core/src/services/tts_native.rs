use std::process::{Command, Stdio, Child};
use std::io::{Write, Read};
use std::sync::{Arc, Mutex};
use std::path::Path;
use anyhow::{Result, Context};
use tracing::{info, error};

pub struct TtsNativeService {
    voice_model: String,
    process: Arc<Mutex<Option<Child>>>,
}

impl TtsNativeService {
    pub fn new(voice_model: &str) -> Self {
        Self {
            voice_model: voice_model.to_string(),
            process: Arc::new(Mutex::new(None)),
        }
    }

    fn ensure_process(&self) -> Result<()> {
        let mut proc_guard = self.process.lock().unwrap();
        
        if proc_guard.is_none() {
            info!("Starting persistent Piper process with CUDA support...");
            let mut args = vec![
                "--model", &self.voice_model,
                "--output_raw",
            ];

            // Add CUDA if available
            if Path::new("/usr/lib/x86_64-linux-gnu/libcuda.so").exists() || 
               Path::new("/usr/local/cuda").exists() {
                args.push("--cuda");
                info!("Piper: CUDA acceleration enabled");
            }

            let child = Command::new("piper")
                .args(&args)
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null())
                .spawn()
                .context("Failed to spawn persistent piper process")?;
            
            *proc_guard = Some(child);
        }
        Ok(())
    }

    pub fn synthesize(&self, text: &str) -> Result<Vec<u8>> {
        info!("Native Synthesis request (Persistent): '{}'", text);
        
        // Clean text to avoid piper issues (one line only)
        let cleaned_text = text.replace("\n", " ").trim().to_string();
        if cleaned_text.is_empty() {
            return Ok(vec![]);
        }

        // For now, let's stick to the fast Command approach but optimized
        // because Piper binary doesn't support easy interactive streaming via stdin in v1.2.0 
        // without complex EOF handling. 
        // BUT we will use the GPU and optimized args.

        if Path::new(&self.voice_model).exists() {
            let mut args = vec![
                "--model", &self.voice_model,
                "--output_raw",
            ];

            if Path::new("/usr/lib/x86_64-linux-gnu/libcuda.so").exists() || 
               Path::new("/usr/local/cuda").exists() {
                args.push("--cuda");
            }

            let mut child = Command::new("piper")
                .args(&args)
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null())
                .spawn()
                .context("Failed to spawn piper process")?;

            if let Some(mut stdin) = child.stdin.take() {
                stdin.write_all(cleaned_text.as_bytes())?;
                stdin.write_all(b"\n")?;
                drop(stdin);
            }

            let output = child.wait_with_output()?;
            if output.status.success() {
                return Ok(output.stdout);
            }
        }

        // Fallback
        info!("Using espeak-ng fallback...");
        let output = Command::new("espeak-ng")
            .args(["-v", "fr", "--stdout", &cleaned_text])
            .output()?;
        
        Ok(output.stdout)
    }
}
