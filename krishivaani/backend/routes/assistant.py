import os
import sys
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# Add the root directory to path to import voice_assistant
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from voice_assistant.stt import transcribe_audio
from voice_assistant.language_detect import detect_language
from voice_assistant.llm_pipeline import generate_response
from voice_assistant.tts import get_tts_pipeline

router = APIRouter()
tts_pipeline = get_tts_pipeline()

@router.post("/chat")
async def chat_with_assistant(audio: UploadFile = File(...)):
    """
    Endpoint for Voice Assistant. 
    Accepts an audio file from the frontend, processes it through STT -> LangDetect -> LLM -> TTS,
    and returns the synthesized audio file.
    """
    try:
        # Save the uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_in:
            shutil.copyfileobj(audio.file, temp_in)
            input_audio_path = temp_in.name
            
        # 1. Speech-to-Text
        transcript, _ = transcribe_audio(input_audio_path, language="kn") # Fallback to kn for init
        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Could not transcribe audio.")
            
        # 2. Language Detection
        detected_lang = detect_language(transcript)
        if not detected_lang:
            detected_lang = "kn"
            
        # 3. LLM Generation
        response_text, _ = generate_response(transcript, detected_lang)
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate response.")
            
        # 4. Text-to-Speech
        output_audio_path = os.path.join(tempfile.gettempdir(), "output_response.wav")
        tts_pipeline.synthesize(response_text, output_audio_path)
        
        # Cleanup input
        os.remove(input_audio_path)
        
        # Return the generated audio file
        return FileResponse(output_audio_path, media_type="audio/wav", filename="response.wav")
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
