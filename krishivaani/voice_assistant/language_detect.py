from langdetect import detect, DetectorFactory

# Set seed for deterministic results
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Detects language and returns ISO code expected by the backend ('kn', 'hi', or 'en').
    Defaults to 'en' if not detected.
    """
    try:
        lang = detect(text)
        if lang == 'kn':
            return 'kn'
        elif lang == 'hi':
            return 'hi'
        else:
            return 'en'
    except Exception:
        return 'en'
