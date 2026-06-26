"""
Configuration for Story Universe AI.
All settings can be overridden via environment variables or .env file.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # API
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("MODEL", "claude-sonnet-4-6"))

    # Generation limits
    max_characters: int = int(os.getenv("MAX_CHARACTERS", "12"))
    max_factions: int = int(os.getenv("MAX_FACTIONS", "5"))
    max_lore_entries: int = int(os.getenv("MAX_LORE_ENTRIES", "25"))
    max_plot_threads: int = int(os.getenv("MAX_PLOT_THREADS", "8"))

    # Scales map to how many entities are generated
    scale_presets: dict = field(default_factory=lambda: {
        "small":  {"characters": 4,  "factions": 2, "lore": 8,  "plot_threads": 3},
        "medium": {"characters": 8,  "factions": 3, "lore": 15, "plot_threads": 5},
        "large":  {"characters": 12, "factions": 5, "lore": 25, "plot_threads": 8},
    })

    # Output
    output_dir: str = field(default_factory=lambda: os.getenv("OUTPUT_DIR", "data/outputs"))

    def get_scale(self, scale: str) -> dict:
        return self.scale_presets.get(scale, self.scale_presets["medium"])

    def validate(self):
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set.\n"
                "Please copy .env.example to .env and add your key."
            )
        return self
