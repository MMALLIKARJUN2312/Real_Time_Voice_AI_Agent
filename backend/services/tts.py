from google.cloud import texttospeech
import io

client = texttospeech.TextToSpeechClient() 

VOICE_MAP = {
    "en": texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Wavenet-D"),
    "hi": texttospeech.VoiceSelectionParams(language_code="hi-IN", name="hi-IN-Wavenet-A"),
    "ta": texttospeech.VoiceSelectionParams(language_code="ta-IN", name="ta-IN-Wavenet-A")
}

async def synthesize_speech(text: str, lang: str) -> bytes:
    voice = VOICE_MAP.get(lang, VOICE_MAP["en"])
    synthesis_input = texttospeech.SynthesisInput(text=text)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16) 
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    return response.audio_content 