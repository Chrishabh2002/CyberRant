import abc
import os
import asyncio
from gtts import gTTS
from typing import Optional

class TTSProvider(abc.ABC):
    @abc.abstractmethod
    def generate_audio(self, text: str, output_path: str) -> bool:
        pass

class GTTSProvider(TTSProvider):
    def generate_audio(self, text: str, output_path: str) -> bool:
        try:
            # gTTS is blocking, so we'll run it in a thread/executor
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False

class TTSService:
    def __init__(self):
        # Using gTTS for real, playable audio fallback
        self.provider = GTTSProvider()

    async def speak(self, text: str, job_id: str, severity: str = "LOW") -> Optional[str]:
        output_dir = "media/audio"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{job_id}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        # Tone Governance: Prepend calmness cues to text for v3.1 stability
        clean_text = text[:800] 
        
        # Run synchronous gTTS in a thread to prevent blocking the event loop
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, self.provider.generate_audio, clean_text, filepath)
        
        if success and os.path.exists(filepath):
            # Check file size to ensure it's not a 0-byte ghost
            if os.path.getsize(filepath) > 0:
                return f"/media/audio/{filename}"
        return None
