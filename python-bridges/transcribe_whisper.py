from faster_whisper import WhisperModel
import warnings

warnings.filterwarnings("ignore")

file_path = "/Volumes/legeek/legeek/Projet-Jarvis/jarvis-voice/New folder/1_1_Cinéma en Français - Iron Man 2008 - Scène Culte N5 Le premier v_1_(Vocals)_(No Reverb).wav"

print("Loading Whisper model...")
model = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=4)

print("Transcribing audio...")
try:
    segments, info = model.transcribe(file_path, language="fr")

    print("\n--- EXACT TRANSCRIPTION ---")
    for segment in segments:
        print(segment.text)
    print("---------------------------\n")
except (FileNotFoundError, OSError) as e:
    import logging
    logging.error(f"Error accessing file (NAS unmounted?): {e}")
except Exception as e:
    import logging
    logging.error(f"Unexpected transcription error: {e}")
