use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use ed25519_dalek::{Signature, Signer, SigningKey, VerifyingKey};
use rand::Rng;
use anyhow::{Context, Result};

/// Generate cryptographically secure 32 random bytes
pub fn gen_bytes_32() -> [u8; 32] {
    let mut bytes = [0u8; 32];
    OsRng.fill(&mut bytes);
    bytes
}

/// Generate random password with alphanumeric chars only
/// No special characters to avoid shell quoting issues
pub fn gen_password(len: usize) -> String {
    const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let mut rng = rand::thread_rng();

    (0..len)
        .map(|_| {
            let idx = rng.gen_range(0..CHARSET.len());
            CHARSET[idx] as char
        })
        .collect()
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
pub fn aead_decrypt(master: &[u8; 32], payload: &str) -> Result<Vec<u8>> {
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

    Ok(plaintext)
}

/// Generate Ed25519 keypair for signing
/// Returns (private_key_b64, public_key_b64)
pub fn ed25519_generate() -> (String, String) {
    let signing_key = SigningKey::generate(&mut OsRng);
    let verifying_key = signing_key.verifying_key();

    let sk_bytes = signing_key.to_bytes();
    let pk_bytes = verifying_key.to_bytes();

    (BASE64.encode(sk_bytes), BASE64.encode(pk_bytes))
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
pub fn generate_secret(secret_type: &str) -> Result<String> {
    match secret_type {
        "jwt_signing_key" => {
            let (sk, _pk) = ed25519_generate();
            Ok(sk)
        }
        "postgres_password" => {
            // 64-char alphanumeric (no specials to avoid quoting issues)
            Ok(gen_password(64))
        }
        "backup_encryption_key" | "jarvis_encryption_key" => {
            // 32 random bytes as base64
            Ok(BASE64.encode(gen_bytes_32()))
        }
        "api_key" => {
            // 32-char alphanumeric key
            Ok(gen_password(32))
        }
        _ => {
            // Default: 32-char random alphanumeric
            Ok(gen_password(32))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gen_bytes_32() {
        let bytes1 = gen_bytes_32();
        let bytes2 = gen_bytes_32();

        assert_eq!(bytes1.len(), 32);
        assert_eq!(bytes2.len(), 32);
        assert_ne!(bytes1, bytes2); // Should be different
    }

    #[test]
    fn test_gen_password() {
        let pwd = gen_password(64);
        assert_eq!(pwd.len(), 64);

        // Should contain only alphanumeric
        assert!(pwd.chars().all(|c| c.is_ascii_alphanumeric()));
    }

    #[test]
    fn test_aead_roundtrip() {
        let master = gen_bytes_32();
        let plaintext = b"hello secret world";

        let encrypted = aead_encrypt(&master, plaintext).unwrap();
        assert!(encrypted.contains(':')); // nonce:cipher format

        let decrypted = aead_decrypt(&master, &encrypted).unwrap();
        assert_eq!(plaintext, decrypted.as_slice());
    }

    #[test]
    fn test_aead_wrong_key() {
        let master1 = gen_bytes_32();
        let master2 = gen_bytes_32();
        let plaintext = b"secret data";

        let encrypted = aead_encrypt(&master1, plaintext).unwrap();
        let result = aead_decrypt(&master2, &encrypted);

        assert!(result.is_err()); // Should fail with wrong key
    }

    #[test]
    fn test_ed25519_roundtrip() {
        let (sk, pk) = ed25519_generate();
        let message = "audit log entry";

        let signature = sign_audit(&sk, message).unwrap();
        let valid = verify_audit(&pk, message, &signature).unwrap();

        assert!(valid);
    }

    #[test]
    fn test_ed25519_invalid_signature() {
        let (sk, pk) = ed25519_generate();
        let message = "audit log entry";

        let signature = sign_audit(&sk, message).unwrap();
        let valid = verify_audit(&pk, "tampered message", &signature).unwrap();

        assert!(!valid);
    }

    #[test]
    fn test_generate_secret_types() {
        let jwt_key = generate_secret("jwt_signing_key").unwrap();
        assert!(!jwt_key.is_empty());

        let pg_pwd = generate_secret("postgres_password").unwrap();
        assert_eq!(pg_pwd.len(), 64);
        assert!(pg_pwd.chars().all(|c| c.is_ascii_alphanumeric()));

        let enc_key = generate_secret("jarvis_encryption_key").unwrap();
        assert!(!enc_key.is_empty());

        let api_key = generate_secret("api_key").unwrap();
        assert_eq!(api_key.len(), 32);
    }
}
