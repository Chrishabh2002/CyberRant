import abc
import os
import asyncio
import cv2
import numpy as np
from typing import List, Optional

class VideoRenderer(abc.ABC):
    @abc.abstractmethod
    def render_briefing(self, title: str, bullet_points: List[str], output_path: str, severity: str = "LOW") -> bool:
        pass

class OpenCVRenderer(VideoRenderer):
    def render_briefing(self, title: str, bullet_points: List[str], output_path: str, severity: str = "LOW") -> bool:
        try:
            # Severity Color Theme (BGR format) - Strictly no red flashing
            themes = {
                "LOW": (180, 180, 180),      # Neutral Gray
                "MEDIUM": (50, 200, 255),   # Informative Gold/Yellow
                "HIGH": (0, 140, 255),      # Focused Orange
                "CRITICAL": (120, 0, 80)    # Executive Purple/Navy
            }
            theme_color = themes.get(severity.upper(), themes["LOW"])

            width, height = 1280, 720
            fps = 2
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            def draw_text(img, text, pos, size, color, thickness=2):
                cv2.putText(img, text, pos, cv2.FONT_HERSHEY_DUPLEX, size, color, thickness, cv2.LINE_AA)

            # 1. Title Slide
            for _ in range(fps * 3):
                frame = np.zeros((height, width, 3), np.uint8)
                frame[:] = (20, 20, 20)
                cv2.rectangle(frame, (0, 0), (width, 80), theme_color, -1)
                draw_text(frame, "CYBERRANT INTEL // ADVISORY", (40, 50), 1, (255, 255, 255), 2)
                draw_text(frame, title.upper(), (100, 350), 2, theme_color, 3)
                draw_text(frame, "ENTERPRISE RISK GOVERNANCE", (100, 420), 0.8, (150, 150, 150), 1)
                out.write(frame)

            # 2. Detail Slides
            for point in bullet_points:
                for _ in range(fps * 3):
                    frame = np.zeros((height, width, 3), np.uint8)
                    frame[:] = (25, 25, 25)
                    cv2.rectangle(frame, (20, 20), (width-20, height-20), (50, 50, 50), 2)
                    draw_text(frame, "THREAT CONTEXT: " + severity.upper(), (60, 100), 1.2, theme_color, 2)
                    cv2.line(frame, (60, 120), (500, 120), theme_color, 3)
                    
                    words = point.split()
                    lines = []
                    curr_line = ""
                    for w in words:
                        if len(curr_line + w) < 50:
                            curr_line += w + " "
                        else:
                            lines.append(curr_line)
                            curr_line = w + " "
                    lines.append(curr_line)
                    
                    for i, line in enumerate(lines):
                        draw_text(frame, line.strip(), (100, 250 + (i * 60)), 1.1, (230, 230, 230), 2)
                    out.write(frame)

            out.release()
            return True
        except Exception:
            return False

import shutil

class VideoService:
    def __init__(self):
        self.renderer = OpenCVRenderer()
        self.ffmpeg_available = shutil.which("ffmpeg") is not None

    async def create_briefing(self, text: str, job_id: str, severity: str = "LOW") -> Optional[str]:
        if not self.ffmpeg_available:
            return None

        output_dir = "media/video"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{job_id}.mp4"
        filepath = os.path.join(output_dir, filename)
        
        mock_bullets = [
            "Comprehensive Risk Assessment synchronized.",
            f"Severity analyzed as {severity.upper()}.",
            "Strategic defensive alignment active.",
            "Operational briefing finalized."
        ]
        
        loop = asyncio.get_event_loop()
        try:
            success = await loop.run_in_executor(None, self.renderer.render_briefing, "Operational Briefing", mock_bullets, filepath, severity)
            
            if success and os.path.exists(filepath):
                if os.path.getsize(filepath) > 0:
                    return f"/media/video/{filename}"
        except Exception:
            # Log internally, return None to trigger fallback in orchestrator
            pass
        return None
