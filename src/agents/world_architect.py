"""
World Architect Agent — designs the universe's fundamental rules, geography, and history.
This is always the FIRST agent to run, as all others build on its output.
"""
from src.utils.llm_client import LLMClient
from src.models.schemas import World, WorldRule, WorldHistory


SYSTEM_PROMPT = """You are the World Architect — a master of speculative fiction world-building.
You create rich, internally consistent universe foundations that are UNIQUE and SURPRISING.
Avoid clichés. Subvert expectations. Make each world feel genuinely novel.
Always output valid JSON exactly matching the requested schema."""


class WorldArchitectAgent:
    """Generates the foundational world: rules, geography, history."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, genre: str, seed: str, scale: dict) -> World:
        """Generate the world foundation."""
        n_rules = 4 if scale.get("characters", 8) >= 8 else 2
        n_eras = 3 if scale.get("characters", 8) >= 8 else 2

        prompt = f"""Create a complete world foundation for a {genre} universe.

Seed concept: "{seed}"

Requirements:
- The world must have a UNIQUE defining mechanic that makes it stand out
- Avoid generic fantasy/sci-fi tropes — subvert them
- {n_rules} world rules (things that are fundamentally true about how this universe works)
- {n_eras} historical eras

Return this exact JSON structure:
{{
  "name": "Universe name",
  "genre": "{genre}",
  "seed_concept": "{seed}",
  "tagline": "One evocative sentence about this world",
  "geography": "2-3 sentence description of the physical world",
  "tone": "The overall narrative tone (e.g. 'bittersweet and mythic')",
  "unique_mechanic": "The one defining mechanic that makes this world unlike any other",
  "rules": [
    {{
      "name": "Rule name",
      "description": "Full explanation of this rule",
      "impact": "How it affects daily life or conflict"
    }}
  ],
  "history": [
    {{
      "era": "Era name",
      "years": "Time span",
      "summary": "What defined this era"
    }}
  ]
}}"""

        data = self.llm.generate_json(SYSTEM_PROMPT, prompt)
        return World(**data)
