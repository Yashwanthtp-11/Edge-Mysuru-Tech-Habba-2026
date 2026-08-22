import os
import argparse
import sys

# Fix Windows console unicode printing error
sys.stdout.reconfigure(encoding='utf-8')

from voice_assistant.stt import transcribe_audio
from voice_assistant.language_detect import detect_language
from voice_assistant.llm_pipeline import get_llm_pipeline
from voice_assistant.tts import get_tts_pipeline

def run_pipeline(audio_path: str, language_override: str = None):
    print(f"--- Starting Pipeline for {audio_path} ---")
    
    # 1. STT
    lang = language_override or 'en'
    print(f"[STT] Transcribing audio with language: {lang}...")
    try:
        transcript, stt_time = transcribe_audio(audio_path, lang)
        print(f"[STT] Transcript: '{transcript}'")
        print(f"[STT] Time elapsed: {stt_time:.2f} seconds\n")
    except Exception as e:
        print(f"[STT] Failed: {e}")
        return
    
    # 2. Language Detection
    detected_lang = detect_language(transcript)
    print(f"[LangDetect] Detected language from text: {detected_lang}\n")
    final_lang = language_override if language_override else detected_lang
    
    # 3. LLM
    print(f"[LLM] Generating response in {final_lang}...")
    try:
        llm = get_llm_pipeline()
        response, llm_time = llm.generate_response(transcript, final_lang)
        print(f"[LLM] Response: '{response}'")
        print(f"[LLM] Time elapsed: {llm_time:.2f} seconds\n")
    except Exception as e:
        print(f"[LLM] Failed: {e}")
        return
    
    # 4. TTS
    print(f"[TTS] Synthesizing speech...")
    output_audio_path = os.path.join(os.path.dirname(os.path.abspath(audio_path)), "output_response.wav")
    try:
        tts = get_tts_pipeline()
        tts_time = tts.synthesize(response, output_audio_path)
        print(f"[TTS] Audio saved to: {output_audio_path}")
        print(f"[TTS] Time elapsed: {tts_time:.2f} seconds\n")
    except Exception as e:
        print(f"[TTS] Failed: {e}")
        return
    
    print("--- Pipeline Complete ---")
    print(f"Total time: {stt_time + llm_time + tts_time:.2f} seconds")

def test_recommendation_explanation(language: str = 'en'):
    print(f"--- Starting Recommendation Explanation Test (Language: {language}) ---")
    
    # Simulate a recommendation object from cv_model
    mock_recommendation = {
        "condition": "Late Blight",
        "confidence": 0.95,
        "what_to_do_now": ["Remove infected leaves immediately", "Do not water from above"],
        "prevention": ["Ensure good air circulation", "Use resistant varieties"],
        "treatment_options": ["Apply copper-based fungicide", "Apply Mancozeb 75% WP"],
        "recommended_inputs": ["Copper Oxychloride 50 WP", "Mancozeb"],
        "sources": ["PlantVillage", "ICAR"]
    }
    
    user_query = "What is wrong with my potato plant and how do I fix it?"
    
    print(f"[LLM] Generating explanation for {mock_recommendation['condition']}...")
    try:
        llm = get_llm_pipeline()
        response, llm_time = llm.generate_response(user_query, language, recommendation=mock_recommendation)
        print(f"[LLM] Response:\n{response}\n")
        print(f"[LLM] Time elapsed: {llm_time:.2f} seconds\n")
    except Exception as e:
        print(f"[LLM] Failed: {e}")
        return
        
    print("--- Recommendation Explanation Test Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Voice Assistant Pipeline")
    parser.add_argument("--audio", help="Path to input WAV file")
    parser.add_argument("--lang", default="kn", help="Language code (kn/hi/en). Default is kn.")
    parser.add_argument("--test-rec", action="store_true", help="Run the recommendation explanation test instead of audio pipeline.")
    args = parser.parse_args()
    
    if args.test_rec:
        test_recommendation_explanation(args.lang)
    elif args.audio:
        if not os.path.exists(args.audio):
            print(f"Error: File {args.audio} not found.")
        else:
            run_pipeline(args.audio, args.lang)
    else:
        print("Error: Must provide either --audio path or use --test-rec.")
