import os
import time
from groq import Groq

class LLMPipeline:
    def __init__(self):
        print("Initializing Groq API client...")
        # Make sure to set your GROQ_API_KEY in the environment variables before running
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY environment variable is not set. LLM calls will fail.")
            
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        # Using the available hackathon endpoint model
        self.model_name = "qwen/qwen3.6-27b" 
        print("LLM API initialized successfully.")

    def generate_response(self, text: str, language: str, recommendation: dict = None) -> tuple[str, float]:
        """
        Generates a farming assistant response to the given text using Groq.
        If a recommendation dict is provided, the LLM will explain it faithfully without inventing new facts.
        Returns the text response and the elapsed time.
        """
        start_time = time.time()
        
        if not self.client:
            return "Error: GROQ_API_KEY not configured.", 0.0
            
        system_prompt = (
            "You are KrishiVaani, an AI agricultural assistant for Indian farmers. "
            "You diagnose crop problems, explain government subsidies simply, and provide weather/market updates. "
            "You must keep your responses short, practical, and conversational. "
            f"Please respond directly in the {language} language without any English translation unless asked. "
            "IMPORTANT: When responding in Kannada (kn), you MUST use the native Kannada script (ಕನ್ನಡ ಲಿಪಿ). "
            "When responding in Hindi (hi), use the native Devanagari script. "
            "CRITICAL: Do not output any <think> tags or reasoning steps. Start your output directly with the conversational response."
        )
        
        user_content = text
        if recommendation:
            system_prompt += (
                "\n\nIMPORTANT: A verified crop disease diagnosis and recommendation has been provided below. "
                "Do NOT invent new agricultural facts, dosages, or treatments. "
                "Only explain the provided structured data conversationally and simply to the farmer in their language."
            )
            rec_text = f"Condition: {recommendation.get('condition')}\n"
            rec_text += f"What to do now: {', '.join(recommendation.get('what_to_do_now', []))}\n"
            rec_text += f"Treatment options: {', '.join(recommendation.get('treatment_options', []))}\n"
            rec_text += f"Prevention: {', '.join(recommendation.get('prevention', []))}\n"
            rec_text += f"Recommended inputs: {', '.join(recommendation.get('recommended_inputs', []))}\n"
            user_content = f"Farmer asks: {text}\n\nDiagnosis Data to explain:\n{rec_text}"
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    }
                ],
                model=self.model_name,
                temperature=0.3,
                max_tokens=4096,
            )
            response = chat_completion.choices[0].message.content
            raw_response = response
            
            # Remove <think>...</think> blocks if a reasoning model is used
            import re
            response = re.sub(r'<think>.*?(?:</think>|$)', '', response, flags=re.DOTALL).strip()
            
            # If the response is completely empty (e.g. max_tokens cut off before closing think), use the raw string
            if not response:
                response = raw_response.replace("<think>", "").replace("</think>", "").strip()
            
        except Exception as e:
            print(f"Groq API Error: {e}")
            response = "Error calling Groq API."
            
        elapsed = time.time() - start_time
        return response.strip(), elapsed

# Singleton instance to avoid reloading
_pipeline_instance = None

def get_llm_pipeline():
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = LLMPipeline()
    return _pipeline_instance
