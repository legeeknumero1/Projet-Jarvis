"""Tests pour les endpoints vocaux STT/TTS"""

def test_stt_endpoint(client):
    """Test endpoint transcription STT"""
    # Créer un faux fichier audio
    fake_wav_data = b"RIFF" + b"a" * 100  # Fake WAV header + data
    files = {"file": ("test.wav", fake_wav_data, "audio/wav")}
    
    r = client.post("/voice/transcribe", files=files)
    assert r.status_code == 200
    
    # Vérifier le format de réponse
    if r.headers.get("content-type", "").startswith("application/json"):
        data = r.json()
        assert data.get("transcript") == "voix transcrite"
        assert "confidence" in data
    else:
        # Si c'est du texte brut
        assert "voix transcrite" in r.text


def test_tts_endpoint(client):
    """Test endpoint synthèse TTS"""
    payload = {"text": "Bonjour le monde", "voice": "default"}
    r = client.post("/voice/synthesize", json=payload)
    assert r.status_code == 200
    
    # Vérifier qu'on reçoit des données audio
    assert len(r.content) > 0
    # Vérifier header audio ou données binaires
    content_type = r.headers.get("content-type", "")
    assert "audio" in content_type or r.content.startswith(b"FAKE_WAV_DATA") or r.content[:4] in [b"RIFF", b"OggS"]


def test_tts_empty_text(client):
    """Test TTS avec texte vide - doit être rejeté"""
    payload = {"text": "", "voice": "default"}
    r = client.post("/voice/synthesize", json=payload)
    assert r.status_code in (400, 422)


def test_tts_long_text(client):
    """Test TTS avec texte trop long - doit être rejeté"""
    long_text = "a" * 2500  # > 2000 caractères
    payload = {"text": long_text, "voice": "default"}
    r = client.post("/voice/synthesize", json=payload)
    assert r.status_code in (400, 422)