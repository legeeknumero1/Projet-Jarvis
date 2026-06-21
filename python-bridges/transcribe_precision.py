import sys
from faster_whisper import WhisperModel

file_path = "/Volumes/legeek/legeek/Projet-Jarvis/jarvis-voice/New folder/1_1_Cinéma en Français - Iron Man 2008 - Scène Culte N5 Le premier v_1_(Vocals)_(No Reverb).wav"

print("Chargement du modèle Whisper Large-v3 (haute précision)...")
# Run on CPU for guaranteed compatibility, or auto. "cpu" with int8 is fast enough for 15s audio.
# Explicitly limiting cpu_threads to avoid CPU thrashing on concurrent script executions
model = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)

print("Analyse milliseconde par milliseconde de l'audio en cours...")
try:
    segments, info = model.transcribe(file_path, beam_size=5, language="fr", word_timestamps=True)

    print("\n--- TRANSCRIPTION HAUTE PRÉCISION ---")
    full_text = ""
    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
        full_text += segment.text + " "

    print("\nTexte final combiné :")
    print(full_text.strip())
    print("-------------------------------------\n")
except (FileNotFoundError, OSError) as e:
    import logging
    logging.error(f"Erreur d'accès au fichier (NAS non monté ?) : {e}")
except Exception as e:
    import logging
    logging.error(f"Erreur inattendue lors de la transcription : {e}")
