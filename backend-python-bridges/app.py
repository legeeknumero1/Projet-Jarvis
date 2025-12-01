"""
API Flask - Phase 3 Python Bridges
Services IA : Ollama LLM, Whisper STT, Piper TTS, Embeddings
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import numpy as np
import base64
from typing import Dict, Any
from loguru import logger
import os
import traceback
from functools import wraps
import jwt
from datetime import datetime, timedelta

# Clients IA
from ollama_client import get_ollama_client
from whisper_client import get_whisper_client
from piper_client import get_piper_client
from embeddings_service import get_embeddings_service

# Input Validators - SECURITY FIX C7-C11
from validators import (
    PromptValidator,
    TTSValidator,
    STTValidator,
    LoginValidator,
    EmbeddingsValidator,
    sanitize_text
)

# Rate Limiting - SECURITY FIX C14
from rate_limiter import (
    create_limiter,
    rate_limit_auth_login,
    rate_limit_auth_verify,
    rate_limit_llm_generate,
    rate_limit_stt_transcribe,
    rate_limit_tts_synthesize,
    rate_limit_embeddings,
    RateLimitMonitor,
    handle_rate_limit_exceeded
)

# Configuration
app = Flask(__name__)
# CORS configuration - restrict to allowed origins
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8100").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize Rate Limiting - SECURITY FIX C14
limiter = create_limiter(app)
handle_rate_limit_exceeded(limiter, app)

# JWT Configuration - SECURITY FIX C1
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Logger
logger.add("logs/bridges.log", rotation="500 MB", level="INFO")
os.makedirs("logs", exist_ok=True)

# ============================================================================
# JWT Authentication Helper Functions
# ============================================================================

def generate_token(user_id: str, username: str) -> str:
    """Générer un token JWT"""
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "username": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "permissions": ["llm", "stt", "tts", "embeddings"],
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """Vérifier un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Décorateur pour protéger les endpoints avec JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Extract token from Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid authorization header"}), 401

        if not token:
            return jsonify({"error": "Missing authorization token"}), 401

        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Store user info in request context
        request.user = payload

        return f(*args, **kwargs)

    return decorated


# ============================================================================
# HEALTH CHECKS
# ============================================================================

@app.route("/health", methods=["GET"])
def health():
    """Vérifier la santé du service"""
    try:
        ollama_ok = get_ollama_client().health_check()
        whisper_ok = True  # Whisper est en mémoire
        piper_ok = True    # Piper est en mémoire
        embeddings_ok = True

        status = "healthy" if all([ollama_ok, whisper_ok, piper_ok, embeddings_ok]) else "degraded"

        return jsonify({
            "status": status,
            "service": "python-bridges",
            "version": "1.3.0",
            "services": {
                "ollama_llm": "" if ollama_ok else "",
                "whisper_stt": "" if whisper_ok else "",
                "piper_tts": "" if piper_ok else "",
                "embeddings": "" if embeddings_ok else ""
            }
        })
    except Exception as e:
        logger.error(f" Health check error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/ready", methods=["GET"])
def ready():
    """Readiness probe pour Kubernetes"""
    try:
        return jsonify({
            "status": "ready",
            "version": "1.3.0"
        })
    except Exception as e:
        return jsonify({"status": "not_ready", "error": str(e)}), 503


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route("/api/auth/login", methods=["POST"])
@rate_limit_auth_login(limiter)
def login():
    """Générer un token JWT pour l'authentification - SECURITY FIX C7 (Input Validation) + C14 (Rate Limiting)"""
    try:
        data = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")

        # Input Validation - SECURITY FIX C7
        validator = LoginValidator(username, password)
        is_valid, error_msg = validator.validate()
        if not is_valid:
            logger.warning(f" LOGIN VALIDATION FAILED: {error_msg} from {request.remote_addr}")
            return jsonify({"error": "Invalid credentials"}), 400

        # TODO: In production, validate against real user database
        # For now, accept any username with valid format
        user_id = f"user-{username}"
        token = generate_token(user_id, username)

        logger.info(f" Login successful for user: {username}")

        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,
            "user_id": user_id,
            "username": username,
        }), 200

    except Exception as e:
        logger.error(f" Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/auth/verify", methods=["POST"])
@require_auth
@rate_limit_auth_verify(limiter)
def verify():
    """Vérifier la validité d'un token JWT - SECURITY FIX C14 (Rate Limiting)"""
    try:
        logger.info(f" Token verified for user: {request.user.get('username')}")
        return jsonify({
            "valid": True,
            "user_id": request.user.get("user_id"),
            "username": request.user.get("username"),
            "permissions": request.user.get("permissions"),
        }), 200
    except Exception as e:
        logger.error(f" Token verification error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OLLAMA LLM ENDPOINTS
# ============================================================================

@app.route("/api/llm/generate", methods=["POST"])
@require_auth
@rate_limit_llm_generate(limiter)
def llm_generate():
    """Générer texte avec Ollama - SECURITY FIX C7 (Input Validation) + C14 (Rate Limiting)"""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        system_prompt = data.get("system_prompt")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 512)

        # Input Validation - SECURITY FIX C7
        validator = PromptValidator(prompt, system_prompt=system_prompt,
                                   temperature=temperature, max_tokens=max_tokens)
        is_valid, error_msg = validator.validate()
        if not is_valid:
            logger.warning(f" LLM VALIDATION FAILED: {error_msg}")
            return jsonify({"error": error_msg}), 400

        client = get_ollama_client()
        result = client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return jsonify({
            "text": result.text,
            "model": result.model,
            "tokens_generated": result.tokens_generated,
            "tokens_prompt": result.tokens_prompt,
            "duration_ms": result.duration_ms
        })

    except Exception as e:
        logger.error(f" LLM generation error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/llm/models", methods=["GET"])
@require_auth
def llm_models():
    """Lister les modèles Ollama disponibles"""
    try:
        client = get_ollama_client()
        models = client.list_models()
        return jsonify({"models": models})
    except Exception as e:
        logger.error(f" Error listing models: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# WHISPER STT ENDPOINTS
# ============================================================================

@app.route("/api/stt/transcribe", methods=["POST"])
@require_auth
@rate_limit_stt_transcribe(limiter)
def stt_transcribe():
    """Transcrire audio Whisper - SECURITY FIX C10 (Input Validation) + C14 (Rate Limiting)"""
    try:
        data = request.get_json()
        audio_b64 = data.get("audio_data", "")
        language = data.get("language")

        # Input Validation - SECURITY FIX C10
        validator = STTValidator(audio_b64, language=language)
        is_valid, error_msg = validator.validate()
        if not is_valid:
            logger.warning(f" STT VALIDATION FAILED: {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Décoder audio base64
        audio_bytes = base64.b64decode(audio_b64)
        audio = np.frombuffer(audio_bytes, dtype=np.float32)

        client = get_whisper_client()
        result = client.transcribe(
            audio=audio,
            sample_rate=16000,
            language=language
        )

        return jsonify({
            "text": result.text,
            "language": result.language,
            "confidence": result.confidence,
            "duration_ms": result.duration_ms,
            "segments": result.segments
        })

    except Exception as e:
        logger.error(f" Transcription error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# PIPER TTS ENDPOINTS
# ============================================================================

@app.route("/api/tts/synthesize", methods=["POST"])
@require_auth
@rate_limit_tts_synthesize(limiter)
def tts_synthesize():
    """Synthétiser texte Piper - SECURITY FIX C3 (RCE) + C8 (XSS) + C9 (Input Validation) + C14 (Rate Limiting)"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        voice = data.get("voice", "fr_FR-upmc-medium")
        speed = data.get("speed", 1.0)

        # Input Validation - SECURITY FIX C8/C9
        validator = TTSValidator(text, voice=voice, speed=speed)
        is_valid, error_msg = validator.validate()
        if not is_valid:
            logger.warning(f" TTS VALIDATION FAILED: {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Sanitize text to remove XSS attempts - SECURITY FIX C8
        clean_text = sanitize_text(text)

        # CRITICAL SECURITY FIX: Validate voice against whitelist only - SECURITY FIX C3
        ALLOWED_VOICES = [
            "fr_FR-upmc-medium",
            "fr_FR-siwis-medium",
            "fr_FR-tom-medium",
            "en_US-glow-tts",
            "en_US-bryce-medium"
        ]

        if voice not in ALLOWED_VOICES:
            return jsonify({"error": f"Invalid voice. Allowed: {', '.join(ALLOWED_VOICES)}"}), 400

        client = get_piper_client()
        result = client.synthesize(
            text=clean_text,
            voice=voice,
            speed=speed
        )

        # Encoder audio base64
        audio_bytes = result.audio_samples.astype(np.float32).tobytes()
        audio_b64 = base64.b64encode(audio_bytes).decode()

        return jsonify({
            "audio_data": audio_b64,
            "sample_rate": result.sample_rate,
            "duration_ms": result.duration_ms,
            "voice": result.voice
        })

    except Exception as e:
        logger.error(f" Synthesis error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/tts/voices", methods=["GET"])
@require_auth
def tts_voices():
    """Lister les voix TTS disponibles"""
    try:
        client = get_piper_client()
        voices = client.list_voices()
        return jsonify({"voices": voices})
    except Exception as e:
        logger.error(f" Error listing voices: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# EMBEDDINGS ENDPOINTS
# ============================================================================

@app.route("/api/embeddings/embed", methods=["POST"])
@require_auth
@rate_limit_embeddings(limiter)
def embed_text():
    """Vectoriser un texte - SECURITY FIX C11 (Input Validation) + C14 (Rate Limiting)"""
    try:
        data = request.get_json()
        text = data.get("text", "")

        # Input Validation - SECURITY FIX C11
        validator = EmbeddingsValidator(text)
        is_valid, error_msg = validator.validate()
        if not is_valid:
            logger.warning(f" EMBEDDINGS VALIDATION FAILED: {error_msg}")
            return jsonify({"error": error_msg}), 400

        service = get_embeddings_service()
        result = service.embed_text(text)

        # Encoder vecteur base64
        vector_bytes = result.vector.tobytes()
        vector_b64 = base64.b64encode(vector_bytes).decode()

        return jsonify({
            "text": result.text,
            "vector": vector_b64,
            "dimension": result.dimension
        })

    except Exception as e:
        logger.error(f" Embedding error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/embeddings/embed-batch", methods=["POST"])
@require_auth
@rate_limit_embeddings(limiter)
def embed_batch():
    """Vectoriser plusieurs textes - SECURITY FIX C11 (Input Validation) + C14 (Rate Limiting)"""
    try:
        data = request.get_json()
        texts = data.get("texts", [])

        if not texts:
            return jsonify({"error": "texts required"}), 400

        # Input Validation - SECURITY FIX C11
        # Validate each text in the batch
        for text in texts:
            validator = EmbeddingsValidator(text)
            is_valid, error_msg = validator.validate()
            if not is_valid:
                logger.warning(f" BATCH EMBEDDINGS VALIDATION FAILED: {error_msg}")
                return jsonify({"error": f"Batch validation failed: {error_msg}"}), 400

        service = get_embeddings_service()
        results = service.embed_texts(texts)

        embeddings = []
        for result in results:
            vector_bytes = result.vector.tobytes()
            vector_b64 = base64.b64encode(vector_bytes).decode()
            embeddings.append({
                "text": result.text,
                "vector": vector_b64,
                "dimension": result.dimension
            })

        return jsonify({
            "embeddings": embeddings,
            "count": len(embeddings)
        })

    except Exception as e:
        logger.error(f" Batch embedding error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f" Internal server error: {error}")
    return jsonify({"error": "internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info(" Starting Python Bridges API v1.3.0")
    logger.info(" Services: Ollama LLM, Whisper STT, Piper TTS, Embeddings")

    app.run(
        host="0.0.0.0",
        port=8005,
        debug=False,
        threaded=True
    )
