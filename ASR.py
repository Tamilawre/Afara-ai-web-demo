from transformers import pipeline
import librosa
import os

def transcribe_audio(audio_file_path): 
    # Initialize the ASR pipeline
    asr = pipeline("automatic-speech-recognition", 
    model="NCAIR1/Yoruba-ASR",
    token=os.environ.get("HF_TOKEN")
    )

    # Load audio file (16kHz recommended)
    audio, sr = librosa.load(audio_file_path, sr=16000)

    # Transcribe
    result = asr(audio)
    return result["text"]