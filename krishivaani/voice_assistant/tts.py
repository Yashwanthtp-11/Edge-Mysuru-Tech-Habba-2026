import os
import time
import numpy as np
import soundfile as sf
import torch
from transformers import AutoModel

class TTSPipeline:
    def __init__(self):
        print("Loading IndicF5 TTS model...")
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.model_path = os.path.join(base_dir, 'models', 'IndicF5')
        
        # IndicF5 is loaded via AutoModel with trust_remote_code
        try:
            self.model = AutoModel.from_pretrained(
                self.model_path, 
                trust_remote_code=True, 
                local_files_only=True
            )
            print("TTS Loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load IndicF5. Error: {e}")
            self.model = None
            
        # We need a reference audio for the TTS to clone the voice.
        # For this hackathon demo, we will look for a default_ref.wav in models/IndicF5
        self.default_ref_audio = os.path.join(self.model_path, "default_ref.wav")
        self.default_ref_text = "नमस्कार, मैं कृषि वाणी हूँ। मैं आपकी सहायता कैसे कर सकती हूँ?" # Dummy reference text

    def synthesize(self, text: str, output_path: str) -> float:
        """
        Synthesizes text into speech and saves it to output_path.
        Returns the elapsed time.
        """
        start_time = time.time()
        
        if not self.model:
            print("TTS model not loaded. Using edge-tts fallback.")
            self._edge_tts_fallback(text, output_path)
            return time.time() - start_time
            
        if not os.path.exists(self.default_ref_audio):
            print(f"Warning: Reference audio not found at {self.default_ref_audio}. TTS might fail.")
            # Create a silent dummy wav just in case the API crashes without it
            sf.write(self.default_ref_audio, np.zeros(24000, dtype=np.float32), samplerate=24000)
            
        # Run inference using the reference audio
        try:
            audio_data = self.model(
                text, 
                ref_audio_path=self.default_ref_audio, 
                ref_text=self.default_ref_text
            )
            
            # Normalize and save output
            if getattr(audio_data, "dtype", None) == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
                
            sf.write(output_path, np.array(audio_data, dtype=np.float32), samplerate=24000)
        except Exception as e:
            print(f"TTS Synthesis failed: {e}. Falling back to edge-tts.")
            self._edge_tts_fallback(text, output_path)
            
        elapsed = time.time() - start_time
        return elapsed

    def _edge_tts_fallback(self, text: str, output_path: str):
        import subprocess
        # Detect language loosely based on characters, or assume Kannada/Hindi based on user config.
        # Since this is a quick hackathon fallback, we will use a Kannada voice if Kannada chars are present,
        # else Hindi if Devanagari is present, else English.
        if any('\u0C80' <= c <= '\u0CFF' for c in text):
            voice = "kn-IN-GaganNeural"
        elif any('\u0900' <= c <= '\u097F' for c in text):
            voice = "hi-IN-MadhurNeural"
        else:
            voice = "en-IN-PrabhatNeural"
            
        print(f"Running edge-tts fallback with voice: {voice}")
        subprocess.run(["py", "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media", output_path], check=True)

# Singleton instance
_tts_instance = None

def get_tts_pipeline():
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSPipeline()
    return _tts_instance
