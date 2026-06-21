from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
import edge_tts
import base64
import asyncio
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SynthesizeRequest(BaseModel):
    text: str = Field(..., max_length=5000)

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    print(f"Synthesizing speech for: {request.text[:50]}...")
    
    # Voix masculine française (Majordome / IA de type Jarvis)
    voice = "fr-FR-HenriNeural"
    
    async def audio_generator():
        try:
            communicate = edge_tts.Communicate(request.text, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]
        except Exception as e:
            import logging
            logging.error(f"TTS Stream error: {e}")
            import traceback
            traceback.print_exc()
            
    # Asynchronous streaming response to improve TTFB
    return StreamingResponse(audio_generator(), media_type="audio/mpeg")

class TranscribeRequest(BaseModel):
    audio_data: str = Field(..., max_length=10000000)
    language: str = Field("fr", max_length=10)

def is_valid_audio_magic_bytes(data: bytes) -> bool:
    if len(data) < 4:
        return False
    # RIFF/WAV
    if data.startswith(b"RIFF"):
        return True
    # Ogg
    if data.startswith(b"OggS"):
        return True
    # FLAC
    if data.startswith(b"fLaC"):
        return True
    # MP3 (ID3v2)
    if data.startswith(b"ID3"):
        return True
    # MP3 (no ID3, sync word) - VERY simplified check
    if data.startswith(b"\xff\xfb") or data.startswith(b"\xff\xf3") or data.startswith(b"\xff\xfa"):
        return True
    # M4A / MP4 / AAC
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return True
    return False

# Pre-load the Whisper model at startup to prevent 3-4s latency per request
print("Loading Whisper model (large-v3) into memory. This may take a moment...")
try:
    from faster_whisper import WhisperModel
    # SecOps / Performance: explicit CPU threads limit (default intra_threads)
    whisper_model = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Warning: Failed to load WhisperModel: {e}")
    whisper_model = None

# SecOps / Performance: Prevent GIL contention and Thread Explosion.
# We limit to 2 concurrent inferences. Each uses up to 4 intra-threads.
transcription_executor = ThreadPoolExecutor(max_workers=2)

@app.post("/transcribe")
async def transcribe(request: TranscribeRequest):
    print(f"Transcribing audio...")
    if whisper_model is None:
        raise HTTPException(status_code=500, detail="Whisper model is not available.")
        
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        
        # SecOps: Magic Bytes Validation to prevent exploit via ffmpeg
        if not is_valid_audio_magic_bytes(audio_bytes):
            raise HTTPException(status_code=400, detail="Invalid audio file signature. Not a recognized audio format.")

        def run_transcription(audio_buffer, lang):
            # Pass BinaryIO directly. Avoids disk I/O and temp file leaks entirely.
            segs, info = whisper_model.transcribe(audio_buffer, language=lang)
            return " ".join([segment.text for segment in segs]), info
            
        # Create an in-memory buffer for the audio
        buf = io.BytesIO(audio_bytes)
        loop = asyncio.get_running_loop()
        
        # Async execution bounded by thread pool executor (no unbounded asyncio.to_thread)
        text, info = await loop.run_in_executor(
            transcription_executor, 
            run_transcription, 
            buf, 
            request.language
        )
        print(f"Transcription complete: {text[:50]}...")
        return {"text": text, "language": info.language}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    # Note: gc.collect() has been intentionally removed to prevent Stop-The-World (STW) pauses.

if __name__ == "__main__":
    import uvicorn
    print("Starting Jarvis Voice Server on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
