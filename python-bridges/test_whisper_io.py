import sys
try:
    from faster_whisper import WhisperModel
    import io

    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    
    # Generate a dummy wav file in memory
    import wave
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b'\x00\x00' * 16000) # 1 sec silence
    buf.seek(0)
    
    segments, info = model.transcribe(buf, language="fr")
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
