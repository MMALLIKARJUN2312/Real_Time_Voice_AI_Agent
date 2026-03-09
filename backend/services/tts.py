from gtts import gTTS
import io

LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "ta": "ta"
}

async def synthesize_speech(text: str, lang: str) -> bytes:
    """
    Synthesizes speech using gTTS (No credentials required).
    Returns audio content as bytes.
    """
    target_lang = LANG_CODES.get(lang, "en")

    mp3_fp = io.BytesIO()
    
    tts = gTTS(text=text, lang=target_lang, slow=False)
    
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    return mp3_fp.read()