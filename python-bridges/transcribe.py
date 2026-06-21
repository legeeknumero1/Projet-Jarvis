import speech_recognition as sr
import os

r = sr.Recognizer()
file_path = "/Volumes/legeek/legeek/Projet-Jarvis/jarvis-voice/New folder/1_1_Cinéma en Français - Iron Man 2008 - Scène Culte N5 Le premier v_1_(Vocals)_(No Reverb).wav"

print("Reading audio file...")
try:
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    print("Transcribing with Google Web Speech API...")
    try:
        text = r.recognize_google(audio, language="fr-FR")
        print("\n--- TRANSCRIPTION ---")
        print(text)
        print("---------------------\n")
    except sr.UnknownValueError:
        import logging
        logging.error("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        import logging
        logging.error("Could not request results from Google Speech Recognition service; {0}".format(e))
except (FileNotFoundError, OSError) as e:
    import logging
    logging.error(f"File not found or IO error (NAS disconnected?): {e}")
except Exception as e:
    import logging
    logging.error(f"Unexpected error: {e}")
