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

# Clients IA
from ollama_client import get_ollama_client
from whisper_client import get_whisper_client
from piper_client import get_piper_client
from embeddings_service import get_embeddings_service

# Configuration
app = Flask(__name__)
# CORS configuration - restrict to allowed origins
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8100").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
CORS(app, origins=cors_origins, supports_credentials=True)

# Logger
logger.add("logs/bridges.log", rotation="500 MB", level="INFO")
os.makedirs("logs", exist_ok=True)


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
                "ollama_llm": "✅" if ollama_ok else "❌",
                "whisper_stt": "✅" if whisper_ok else "❌",
                "piper_tts": "✅" if piper_ok else "❌",
                "embeddings": "✅" if embeddings_ok else "❌"
            }
        })
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
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
# OLLAMA LLM ENDPOINTS
# ============================================================================

@app.route("/api/llm/generate", methods=["POST"])
def llm_generate():
    """Générer texte avec Ollama"""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        system_prompt = data.get("system_prompt")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 512)

        if not prompt:
            return jsonify({"error": "prompt required"}), 400

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
        logger.error(f"❌ LLM generation error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/llm/models", methods=["GET"])
def llm_models():
    """Lister les modèles Ollama disponibles"""
    try:
        client = get_ollama_client()
        models = client.list_models()
        return jsonify({"models": models})
    except Exception as e:
        logger.error(f"❌ Error listing models: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# WHISPER STT ENDPOINTS
# ============================================================================

@app.route("/api/stt/transcribe", methods=["POST"])
def stt_transcribe():
    """Transcrire audio Whisper"""
    try:
        data = request.get_json()
        audio_b64 = data.get("audio_data", "")
        language = data.get("language")

        if not audio_b64:
            return jsonify({"error": "audio_data required"}), 400

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
        logger.error(f"❌ Transcription error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PIPER TTS ENDPOINTS
# ============================================================================

@app.route("/api/tts/synthesize", methods=["POST"])
def tts_synthesize():
    """Synthétiser texte Piper"""
    try:
        data = request.get_json()
        text = data.get("text", "")
        voice = data.get("voice", "fr_FR-upmc-medium")
        speed = data.get("speed", 1.0)

        if not text:
            return jsonify({"error": "text required"}), 400

        client = get_piper_client()
        result = client.synthesize(
            text=text,
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
        logger.error(f"❌ Synthesis error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/tts/voices", methods=["GET"])
def tts_voices():
    """Lister les voix TTS disponibles"""
    try:
        client = get_piper_client()
        voices = client.list_voices()
        return jsonify({"voices": voices})
    except Exception as e:
        logger.error(f"❌ Error listing voices: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# EMBEDDINGS ENDPOINTS
# ============================================================================

@app.route("/api/embeddings/embed", methods=["POST"])
def embed_text():
    """Vectoriser un texte"""
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "text required"}), 400

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
        logger.error(f"❌ Embedding error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/embeddings/embed-batch", methods=["POST"])
def embed_batch():
    """Vectoriser plusieurs textes"""
    try:
        data = request.get_json()
        texts = data.get("texts", [])

        if not texts:
            return jsonify({"error": "texts required"}), 400

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
        logger.error(f"❌ Batch embedding error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"❌ Internal server error: {error}")
    return jsonify({"error": "internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting Python Bridges API v1.3.0")
    logger.info("📡 Services: Ollama LLM, Whisper STT, Piper TTS, Embeddings")

    app.run(
        host="0.0.0.0",
        port=8005,
        debug=False,
        threaded=True
    )
