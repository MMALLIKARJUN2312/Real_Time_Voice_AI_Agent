from langdetect import detect
from typing import Optional

SUPPORTED_LANGS = {"en": "English", "hi": "Hindi", "ta": "Tamil"}

def detect_language(text: str, stt_lang: Optional[str] = None) -> str:
    """
    Detect lang from text; prefer STT if confident.
    Why: langdetect handles scripts (Devanagari/Tamil) well.
    """
    if stt_lang and stt_lang in SUPPORTED_LANGS:
        return stt_lang 
    try:
        detected = detect(text)  
        return detected if detected in SUPPORTED_LANGS else "en"  
    except:
        return "en"