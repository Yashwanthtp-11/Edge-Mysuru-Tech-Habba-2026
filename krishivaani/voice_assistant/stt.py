import os
import time
import wave
import numpy as np
import sherpa_onnx

def transcribe_audio(audio_path: str, language: str) -> tuple[str, float]:
    """
    Transcribes audio using sherpa-onnx.
    Returns the transcript and the time taken.
    """
    start_time = time.time()
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    asr_dir = os.path.join(base_dir, 'models', 'asr')
    
    model_path = os.path.join(asr_dir, language, 'model.int8.onnx')
    tokens_path = os.path.join(asr_dir, 'tokens.txt')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"ASR model not found at {model_path}")
        
    # The model is ai4bharat/indic-conformer, which is a NeMo CTC model
    try:
        recognizer = sherpa_onnx.OfflineRecognizer.from_nemo_ctc(
            model=model_path,
            tokens=tokens_path,
            num_threads=4
        )
    except Exception as e:
        print(f"Warning: NeMo CTC config failed. Error: {e}")

    # Read and resample WAV to 16kHz mono automatically using librosa
    import librosa
    samples, sr = librosa.load(audio_path, sr=16000, mono=True)
    # librosa returns float32 by default, which sherpa expects.

    stream = recognizer.create_stream()
    stream.accept_waveform(16000, samples)
    recognizer.decode_stream(stream)
    
    transcript = stream.result.text
    elapsed = time.time() - start_time
    
    return transcript, elapsed
