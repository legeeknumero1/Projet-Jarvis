//! Service vocal pour Jarvis Rust Backend
//! 
//! Interface Rust pour les services STT et TTS
//! Communication avec les conteneurs Whisper et Piper

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

use crate::{
    config::AppConfig,
    models::{AudioFormat, SynthesizeRequest, SynthesizeResponse, TranscribeRequest, TranscribeResponse, WordTimestamp},
};

/// Service de traitement vocal
#[derive(Clone)]
pub struct VoiceService {
    client: Client,
    stt_url: String,
    tts_url: String,
}

/// Requête STT vers le service Whisper
#[derive(Debug, Serialize)]
struct STTServiceRequest {
    audio_data: String,
    language: Option<String>,
    response_format: String,
    timestamp_granularities: Option<Vec<String>>,
}

/// Réponse du service Whisper
#[derive(Debug, Deserialize)]
struct STTServiceResponse {
    text: String,
    language: Option<String>,
    duration: Option<f32>,
    words: Option<Vec<WordTimestampSTT>>,
}

#[derive(Debug, Deserialize)]
struct WordTimestampSTT {
    word: String,
    start: f32,
    end: f32,
}

/// Requête TTS vers le service Piper
#[derive(Debug, Serialize)]
struct TTSServiceRequest {
    text: String,
    voice: Option<String>,
    speed: Option<f32>,
    output_format: String,
}

/// Réponse du service Piper
#[derive(Debug, Deserialize)]
struct TTSServiceResponse {
    audio_data: String,
    sample_rate: u32,
    duration: f32,
    format: String,
}

/// Information sur une voix disponible
#[derive(Debug, Serialize, Deserialize)]
pub struct VoiceInfo {
    pub id: String,
    pub name: String,
    pub language: String,
    pub gender: String,
    pub quality: String,
}

/// Erreurs du service vocal
#[derive(Debug, thiserror::Error)]
pub enum VoiceError {
    #[error("Erreur STT: {0}")]
    STTError(String),
    
    #[error("Erreur TTS: {0}")]
    TTSError(String),
    
    #[error("Format audio non supporté: {0}")]
    UnsupportedFormat(String),
    
    #[error("Timeout du service vocal")]
    Timeout,
    
    #[error("Service vocal indisponible: {0}")]
    ServiceUnavailable(String),
    
    #[error("Données audio invalides")]
    InvalidAudioData,
}

impl VoiceService {
    /// Initialise le service vocal
    pub async fn new(config: &AppConfig) -> anyhow::Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(30)) // Timeout pour les opérations audio
            .build()?;

        let service = Self {
            client,
            stt_url: config.external.stt_url.clone(),
            tts_url: config.external.tts_url.clone(),
        };

        // Test de connexion aux services
        service.test_services().await?;
        
        tracing::info!("✅ Service vocal initialisé (STT: {}, TTS: {})", 
                      config.external.stt_url, config.external.tts_url);
        
        Ok(service)
    }

    /// Teste la connexion aux services STT et TTS
    async fn test_services(&self) -> anyhow::Result<()> {
        // Test STT
        let stt_health_url = format!("{}/health", self.stt_url);
        match self.client.get(&stt_health_url).send().await {
            Ok(response) => {
                if !response.status().is_success() {
                    tracing::warn!("⚠️ Service STT non disponible: {}", response.status());
                }
            }
            Err(e) => {
                tracing::warn!("⚠️ Impossible de joindre le service STT: {}", e);
            }
        }

        // Test TTS
        let tts_health_url = format!("{}/health", self.tts_url);
        match self.client.get(&tts_health_url).send().await {
            Ok(response) => {
                if !response.status().is_success() {
                    tracing::warn!("⚠️ Service TTS non disponible: {}", response.status());
                }
            }
            Err(e) => {
                tracing::warn!("⚠️ Impossible de joindre le service TTS: {}", e);
            }
        }

        Ok(())
    }

    /// Vérifie si le service est prêt
    pub async fn is_ready(&self) -> anyhow::Result<()> {
        self.test_services().await
    }

    /// Transcrit de l'audio en texte (STT)
    pub async fn transcribe_audio(
        &self,
        request: TranscribeRequest,
    ) -> anyhow::Result<TranscribeResponse> {
        tracing::debug!("🎤 Transcription: {} caractères audio", request.audio_data.len());

        // Validation des données audio
        if request.audio_data.is_empty() {
            return Err(VoiceError::InvalidAudioData.into());
        }

        // Préparer la requête pour le service STT
        let stt_request = STTServiceRequest {
            audio_data: request.audio_data,
            language: request.language.clone(),
            response_format: "verbose_json".to_string(),
            timestamp_granularities: Some(vec!["word".to_string()]),
        };

        let url = format!("{}/v1/audio/transcriptions", self.stt_url);
        
        let start_time = std::time::Instant::now();
        
        let response = self.client
            .post(&url)
            .json(&stt_request)
            .send()
            .await
            .map_err(|e| {
                if e.is_timeout() {
                    VoiceError::Timeout
                } else {
                    VoiceError::ServiceUnavailable(e.to_string())
                }
            })?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(VoiceError::STTError(error_text).into());
        }

        let stt_response: STTServiceResponse = response.json().await
            .map_err(|e| VoiceError::STTError(e.to_string()))?;

        let processing_time = start_time.elapsed().as_millis() as f32 / 1000.0;

        // Convertir la réponse au format Jarvis
        let words = stt_response.words.map(|words| {
            words.into_iter().map(|w| WordTimestamp {
                word: w.word,
                start_time: w.start,
                end_time: w.end,
                confidence: 1.0, // Whisper ne fournit pas de score de confiance par mot
            }).collect()
        });

        let transcription = TranscribeResponse {
            text: stt_response.text,
            language: stt_response.language.unwrap_or_else(|| "fr".to_string()),
            confidence: 0.95, // Score de confiance fixe pour Whisper
            duration_secs: stt_response.duration.unwrap_or(processing_time),
            words,
        };

        tracing::info!("✅ Transcription: '{}' ({}s)", 
                      transcription.text.chars().take(50).collect::<String>(),
                      transcription.duration_secs);

        Ok(transcription)
    }

    /// Synthétise du texte en audio (TTS)
    pub async fn synthesize_speech(
        &self,
        request: SynthesizeRequest,
    ) -> anyhow::Result<SynthesizeResponse> {
        tracing::debug!("🔊 Synthèse: '{}' ({} caractères)", 
                       request.text.chars().take(50).collect::<String>(),
                       request.text.len());

        // Validation du texte
        if request.text.trim().is_empty() {
            return Err(VoiceError::TTSError("Texte vide".to_string()).into());
        }

        // Préparer la requête pour le service TTS
        let tts_request = TTSServiceRequest {
            text: request.text.clone(),
            voice: request.voice.clone(),
            speed: request.speed,
            output_format: format!("{:?}", request.format.as_ref().unwrap_or(&AudioFormat::Wav)).to_lowercase(),
        };

        let url = format!("{}/v1/audio/speech", self.tts_url);
        
        let start_time = std::time::Instant::now();

        let response = self.client
            .post(&url)
            .json(&tts_request)
            .send()
            .await
            .map_err(|e| {
                if e.is_timeout() {
                    VoiceError::Timeout
                } else {
                    VoiceError::ServiceUnavailable(e.to_string())
                }
            })?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(VoiceError::TTSError(error_text).into());
        }

        let tts_response: TTSServiceResponse = response.json().await
            .map_err(|e| VoiceError::TTSError(e.to_string()))?;

        let processing_time = start_time.elapsed().as_millis() as f32 / 1000.0;

        // Convertir la réponse au format Jarvis
        let format = match tts_response.format.as_str() {
            "wav" => AudioFormat::Wav,
            "mp3" => AudioFormat::Mp3,
            "ogg" => AudioFormat::Ogg,
            "flac" => AudioFormat::Flac,
            _ => AudioFormat::Wav,
        };

        let synthesis = SynthesizeResponse {
            audio_data: tts_response.audio_data,
            format,
            duration_secs: tts_response.duration,
            sample_rate: tts_response.sample_rate,
        };

        tracing::info!("✅ Synthèse: {:.1}s audio généré en {:.1}s", 
                      synthesis.duration_secs, processing_time);

        Ok(synthesis)
    }

    /// Récupère la liste des voix disponibles
    pub async fn get_available_voices(&self) -> anyhow::Result<Vec<VoiceInfo>> {
        let url = format!("{}/v1/voices", self.tts_url);
        
        match self.client.get(&url).send().await {
            Ok(response) => {
                if response.status().is_success() {
                    let voices: Vec<VoiceInfo> = response.json().await
                        .map_err(|e| VoiceError::TTSError(e.to_string()))?;
                    Ok(voices)
                } else {
                    // Retourner des voix par défaut si le service ne supporte pas cette route
                    Ok(self.get_default_voices())
                }
            }
            Err(_) => {
                // Service non disponible, retourner des voix par défaut
                Ok(self.get_default_voices())
            }
        }
    }

    /// Voix par défaut si le service ne répond pas
    fn get_default_voices(&self) -> Vec<VoiceInfo> {
        vec![
            VoiceInfo {
                id: "fr_FR-upmc-medium".to_string(),
                name: "French UPMC Medium".to_string(),
                language: "fr-FR".to_string(),
                gender: "neutral".to_string(),
                quality: "medium".to_string(),
            },
            VoiceInfo {
                id: "fr_FR-siwis-medium".to_string(),
                name: "French SIWIS Medium".to_string(),
                language: "fr-FR".to_string(),
                gender: "female".to_string(),
                quality: "medium".to_string(),
            },
            VoiceInfo {
                id: "en_US-lessac-medium".to_string(),
                name: "English Lessac Medium".to_string(),
                language: "en-US".to_string(),
                gender: "female".to_string(),
                quality: "medium".to_string(),
            },
        ]
    }

    /// Vérifie la santé des services vocaux
    pub async fn health_check(&self) -> anyhow::Result<serde_json::Value> {
        let mut status = serde_json::json!({
            "stt": { "status": "unknown" },
            "tts": { "status": "unknown" }
        });

        // Test STT
        let stt_start = std::time::Instant::now();
        match self.client.get(&format!("{}/health", self.stt_url)).send().await {
            Ok(response) => {
                let response_time = stt_start.elapsed().as_millis() as u64;
                status["stt"] = serde_json::json!({
                    "status": if response.status().is_success() { "healthy" } else { "unhealthy" },
                    "response_time_ms": response_time,
                    "url": self.stt_url
                });
            }
            Err(e) => {
                status["stt"] = serde_json::json!({
                    "status": "unhealthy",
                    "error": e.to_string(),
                    "url": self.stt_url
                });
            }
        }

        // Test TTS
        let tts_start = std::time::Instant::now();
        match self.client.get(&format!("{}/health", self.tts_url)).send().await {
            Ok(response) => {
                let response_time = tts_start.elapsed().as_millis() as u64;
                status["tts"] = serde_json::json!({
                    "status": if response.status().is_success() { "healthy" } else { "unhealthy" },
                    "response_time_ms": response_time,
                    "url": self.tts_url
                });
            }
            Err(e) => {
                status["tts"] = serde_json::json!({
                    "status": "unhealthy",
                    "error": e.to_string(),
                    "url": self.tts_url
                });
            }
        }

        Ok(status)
    }
}