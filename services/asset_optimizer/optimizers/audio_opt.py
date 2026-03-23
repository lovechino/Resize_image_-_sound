import shutil
import subprocess
import os
from .base import BaseOptimizer
from ..config import OptimizerConfig

class AudioOptimizer(BaseOptimizer):
    def __init__(self, config: OptimizerConfig):
        super().__init__(config)
        # check if ffmpeg is available
        self.ffmpeg_available = shutil.which("ffmpeg") is not None
        if not self.ffmpeg_available:
            print("⚠️ WARNING: FFmpeg not installed. Audio files will be skipped.")

    def optimize(self, input_path: str, output_path: str) -> bool:
        if not self.ffmpeg_available:
            return False

        try:
            self.ensure_dir(output_path)
            cmd = [
                'ffmpeg', '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', self.config.audio_bitrate,
                '-ac', '1', # Force Mono
                '-ar', self.config.audio_sample_rate,
                '-map_metadata', '-1',
                '-y', output_path
            ]
            # Hide cmd window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, startupinfo=startupinfo)
            return True
        except Exception as e:
            print(f"❌ [AUDIO ERROR] {os.path.basename(input_path)}: {e}")
            return False
