use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use ed25519_dalek::{Signature, Signer, SigningKey, VerifyingKey};
use rand::Rng;
use anyhow::{Context, Result};
use zeroize::Zeroizing;

/// Generate cryptographically secure 32 random bytes
pub fn gen_bytes_32() -> Zeroizing<[u8; 32]> {
    let mut bytes = [0u8; 32];
    OsRng.fill(&mut bytes);
    Zeroizing::new(bytes)
}

/// Generate random password with alphanumeric chars only
pub fn gen_password(len: usize) -> Zeroizing<String> {
    const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let mut rng = rand::thread_rng();

    let pwd: String = (0..len)
        .map(|_| {
            let idx = rng.gen_range(0..CHARSET.len());
            CHARSET[idx] as char
        })
        .collect();
    
    Zeroizing::new(pwd)
}

/// Encrypt plaintext using AES-GCM-256
/// Returns "base64(nonce):base64(ciphertext)"
pub fn aead_encrypt(master: &[u8; 32], plaintext: &[u8]) -> Result<String> {
    let cipher = Aes256Gcm::new(master.into());

    // Generate random 96-bit nonce
    let mut nonce_bytes = [0u8; 12];
    OsRng.fill(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    // Encrypt
    let ciphertext = cipher
        .encrypt(nonce, plaintext)
        .map_err(|_| anyhow::anyhow!("encryption failed"))?;

    // Encode nonce and ciphertext separately
    let nonce_b64 = BASE64.encode(&nonce_bytes);
    let cipher_b64 = BASE64.encode(&ciphertext);

    Ok(format!("{}:{}", nonce_b64, cipher_b64))
}

/// Decrypt AES-GCM-256 encrypted payload
/// Expects format "base64(nonce):base64(ciphertext)"
pub fn aead_decrypt(master: &[u8; 32], payload: &str) -> Result<Zeroizing<Vec<u8>>> {
    let parts: Vec<&str> = payload.split(':').collect();
    if parts.len() != 2 {
        anyhow::bail!("invalid encrypted payload format");
    }

    let nonce_bytes = BASE64
        .decode(parts[0])
        .context("failed to decode nonce")?;
    let ciphertext = BASE64
        .decode(parts[1])
        .context("failed to decode ciphertext")?;

    if nonce_bytes.len() != 12 {
        anyhow::bail!("invalid nonce length");
    }

    let cipher = Aes256Gcm::new(master.into());
    let nonce = Nonce::from_slice(&nonce_bytes);

    let plaintext = cipher
        .decrypt(nonce, ciphertext.as_ref())
        .map_err(|_| anyhow::anyhow!("decryption failed"))?;

    Ok(Zeroizing::new(plaintext))
}

/// Generate Ed25519 keypair for signing
/// Returns (private_key_b64, public_key_b64)
pub fn ed25519_generate() -> (Zeroizing<String>, String) {
    let signing_key = SigningKey::generate(&mut OsRng);
    let verifying_key = signing_key.verifying_key();

    let sk_bytes = signing_key.to_bytes();
    let pk_bytes = verifying_key.to_bytes();

    (Zeroizing::new(BASE64.encode(sk_bytes)), BASE64.encode(pk_bytes))
}

/// Sign a message using Ed25519 private key
/// Returns base64(signature)
pub fn sign_audit(sk_b64: &str, message: &str) -> Result<String> {
    let sk_bytes = BASE64
        .decode(sk_b64)
        .context("failed to decode signing key")?;

    if sk_bytes.len() != 32 {
        anyhow::bail!("invalid signing key length");
    }

    let signing_key = SigningKey::from_bytes(&sk_bytes.try_into().unwrap());
    let signature = signing_key.sign(message.as_bytes());

    Ok(BASE64.encode(signature.to_bytes()))
}

/// Verify Ed25519 signature
pub fn verify_audit(pk_b64: &str, message: &str, sig_b64: &str) -> Result<bool> {
    let pk_bytes = BASE64
        .decode(pk_b64)
        .context("failed to decode public key")?;
    let sig_bytes = BASE64
        .decode(sig_b64)
        .context("failed to decode signature")?;

    if pk_bytes.len() != 32 {
        anyhow::bail!("invalid public key length");
    }
    if sig_bytes.len() != 64 {
        anyhow::bail!("invalid signature length");
    }

    let verifying_key = VerifyingKey::from_bytes(&pk_bytes.try_into().unwrap())
        .context("invalid public key")?;
    let signature = Signature::from_bytes(&sig_bytes.try_into().unwrap());

    Ok(verifying_key.verify_strict(message.as_bytes(), &signature).is_ok())
}

/// Generate secret based on type
pub fn generate_secret(secret_type: &str) -> Result<Zeroizing<String>> {
    match secret_type {
        "jwt_signing_key" => {
            let (sk, _pk) = ed25519_generate();
            Ok(sk)
        }
        "postgres_password" | "redis_password" => {
            Ok(gen_password(64))
        }
        "database_url" => {
            let pwd = gen_password(32);
            Ok(Zeroizing::new(format!("postgres://jarvis:{}@postgres:5432/jarvis_db", *pwd)))
        }
        "backup_encryption_key" | "jarvis_encryption_key" => {
            Ok(Zeroizing::new(BASE64.encode(*gen_bytes_32())))
        }
        _ => {
            Ok(gen_password(32))
        }
    }
}