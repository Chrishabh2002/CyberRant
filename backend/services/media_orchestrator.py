import asyncio
from typing import Dict, Any, Optional
from .tts_service import TTSService
from .video_service import VideoService

class MediaOrchestrator:
    # In-memory job store
    _job_states: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        self.tts = TTSService()
        self.video = VideoService()

    @classmethod
    def get_job_status(cls, trace_id: str) -> Dict[str, Any]:
        return cls._job_states.get(trace_id, {
            "audio_status": "NONE",
            "video_status": "NONE"
        })

    @classmethod
    def update_job(cls, trace_id: str, **kwargs):
        if trace_id not in cls._job_states:
            cls._job_states[trace_id] = {
                "audio_status": "NONE", 
                "video_status": "NONE",
                "audio_url": None,
                "video_url": None,
                "error": None,
                "overall_state": "TEXT READY"
            }
        cls._job_states[trace_id].update(kwargs)

    async def generate_media_pack(self, trace_id: str, text: str, include_video: bool = False, severity: str = "LOW"):
        """Asynchronous background task to generate audio and video packs."""
        # Step 1: Initialize states to PROCESSING
        self.update_job(trace_id, 
            audio_status="PROCESSING", 
            video_status="PROCESSING" if include_video else "NONE",
            overall_state="PROCESSING"
        )

        try:
            # Step 2: Parallel Generation
            tasks = [self.tts.speak(text, trace_id, severity=severity)]
            if include_video:
                tasks.append(self.video.create_briefing(text, trace_id, severity=severity))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Step 3: Handle Audio Result
            audio_res = results[0]
            if isinstance(audio_res, Exception) or not audio_res:
                self.update_job(trace_id, audio_status="FAILED", error="Audio briefing unavailable.")
            else:
                self.update_job(trace_id, audio_status="MEDIA READY", audio_url=audio_res)

            # Step 4: Handle Video Result
            if include_video:
                video_res = results[1]
                if isinstance(video_res, Exception) or not video_res:
                    self.update_job(trace_id, video_status="FAILED", error="Video summary unavailable.")
                else:
                    self.update_job(trace_id, video_status="MEDIA READY", video_url=video_res)
            
            # Final state update for UI convenience
            final_state = "COMPLETED"
            # If everything failed, it's still technically 'COMPLETED' (Text briefing is complete)
            # but we use 'TEXT READY' as the fallback if media is missing
            self.update_job(trace_id, overall_state=final_state)

        except Exception as e:
            # Log silently, report TEXT READY
            self.update_job(trace_id, overall_state="TEXT READY", error="Subsystem error.")
