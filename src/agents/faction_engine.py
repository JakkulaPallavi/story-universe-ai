"""
Faction Engine Agent — creates competing factions shaped by the world's rules.
Runs AFTER the World Architect so factions are grounded in world logic.
"""
from src.utils.llm_client import LLMClient
from src.models.schemas import World, Faction, FactionAlignment


SYSTEM_PROMPT = """You are the Faction Engine — you design the competing power groups in a fictional universe.
Every faction must feel ideologically distinct. They should have real reasons to exist and real reasons to conflict.
Avoid cartoonish evil. Even antagonist factions should have understandable motivations.
Output valid JSON exactly matching the requested schema."""


class FactionEngineAgent:
    """Generates factions grounded in the world's rules and history."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, world: World, n_factions: int) -> list[Faction]:
        """Generate a list of factions for the given world."""
        alignments = self._plan_alignments(n_factions)
        world_context = f"""
World: {world.name}
Genre: {world.genre}
Unique Mechanic: {world.unique_mechanic}
World Rules: {', '.join(r.name + ': ' + r.description for r in world.rules)}
History Summary: {' | '.join(e.era + ': ' + e.summary for e in world.history)}
"""
        prompt = f"""Given this world:
{world_context}

Create {n_factions} factions. Use these alignments: {alignments}

IDs should be: faction_1, faction_2, ..., faction_{n_factions}
Set enemies/allies using these IDs. Not all factions need enemies/allies.

Return a JSON array:
[
  {{
    "id": "faction_1",
    "name": "Faction Name",
    "alignment": "{FactionAlignment.PROTAGONIST.value}",
    "ideology": "Core belief system",
    "goal": "What they ultimately want",
    "methods": "How they pursue their goal",
    "symbol": "Their emblem and its meaning",
    "strength": "Primary source of power",
    "weakness": "Critical vulnerability",
    "enemies": ["faction_2"],
    "allies": []
  }},
  ...
]"""

        data = self.llm.generate_json(SYSTEM_PROMPT, prompt)
        return [Faction(**f) for f in data]

    @staticmethod
    def _plan_alignments(n: int) -> list[str]:
        """Distribute alignments across factions."""
        plans = {
            2: ["protagonist", "antagonist"],
            3: ["protagonist", "antagonist", "neutral"],
            4: ["protagonist", "antagonist", "neutral", "wildcard"],
            5: ["protagonist", "antagonist", "neutral", "wildcard", "antagonist"],
        }
        return plans.get(n, ["protagonist", "antagonist"] + ["neutral"] * (n - 2))
