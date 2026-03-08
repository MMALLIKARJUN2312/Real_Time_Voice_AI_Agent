import whisper
import io
from typing import Optional

model = whisper.load_model("base") 

async def transcribe_audio(audio_bytes: bytes) -> Optional[tuple[str, str]]:
    """
    Transcribe audio to text and detect language.
    Why async: Non-blocking for pipeline.
    """
    try:
        audio = whisper.load_audio(io.BytesIO(audio_bytes))
        result = model.transcribe(audio, language=None)  
        text = result["text"].strip()
        detected_lang = result["language"]  
        return text, detected_lang
    except Exception as e:
        print(f"STT Error: {e}")
        return None, None