from dataclasses import dataclass

@dataclass
class OptimizerConfig:
    """Class to store configuration."""
    max_width: int
    jpg_quality: int
    png_colors: int
    audio_bitrate: str
    audio_sample_rate: str

class ProfileFactory:
    """Factory Pattern: Create config based on profile level."""
    @staticmethod
    def get_profile(level: str):
        level = level.lower()
        if level == "high":
            # PC/Console: High quality
            return OptimizerConfig(
                max_width=4096, jpg_quality=85, png_colors=256, 
                audio_bitrate="192k", audio_sample_rate="44100"
            )
        elif level == "medium":
            # Mobile Standard (Default)
            return OptimizerConfig(
                max_width=2048, jpg_quality=70, png_colors=64, 
                audio_bitrate="128k", audio_sample_rate="44100"
            )
        elif level == "low":
            # Web Game / Low-end device: High compression
            return OptimizerConfig(
                max_width=1024, jpg_quality=50, png_colors=32, 
                audio_bitrate="32k", audio_sample_rate="16000"
            )
        else:
            raise ValueError("Invalid Level. Choose: low, medium, high")
