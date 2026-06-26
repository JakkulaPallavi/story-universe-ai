"""
Lore Weaver Agent — generates myths, historical events, artifacts, and prophecies.
Runs AFTER characters are created so lore can reference specific people and factions.
"""
from src.utils.llm_client import LLMClient
from src.models.schemas import World, Faction, Character, LoreEntry, LoreType


SYSTEM_PROMPT = """You are the Lore Weaver — keeper of myths, histories, and secrets in fictional universes.
You write lore that feels ancient and lived-in, yet directly relevant to current conflicts.
Good lore creates dramatic irony: readers know things characters don't.
Lore should contradict itself slightly — history is never clean.
Output valid JSON exactly matching the requested schema."""


class LoreWeaverAgent:
    """Generates codex-style lore entries that tie together world, factions, and characters."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(
        self,
        world: World,
        factions: list[Faction],
        characters: list[Character],
        n_lore: int,
    ) -> list[LoreEntry]:
        """Generate lore entries for the universe."""
        faction_names = {f.id: f.name for f in factions}
        char_names = {c.id: c.name for c in characters}

        faction_list = "\n".join(f"  - {f.id}: {f.name}" for f in factions)
        char_list = "\n".join(f"  - {c.id}: {c.name} [{c.role.value}]" for c in characters)
        lore_types = [lt.value for lt in LoreType]

        prompt = f"""World: {world.name}
Unique Mechanic: {world.unique_mechanic}
History: {' | '.join(e.era + ': ' + e.summary for e in world.history)}

Factions:
{faction_list}

Characters:
{char_list}

Create {n_lore} lore entries. Distribute across these types: {lore_types}

Requirements:
- Reference specific faction IDs and character IDs in connected_factions / connected_characters
- Some lore should directly tie to character backstories or secrets
- Include at least one prophecy and one origin myth
- Make lore entries interconnected — reference each other
- IDs: lore_1, lore_2, ..., lore_{n_lore}

Return a JSON array:
[
  {{
    "id": "lore_1",
    "title": "Lore Entry Title",
    "lore_type": "historical_event",
    "summary": "1-sentence summary",
    "full_text": "3-5 sentences as it would appear in a codex or ancient text. First-person unreliable narrator welcome.",
    "connected_factions": ["faction_1"],
    "connected_characters": ["char_1"],
    "importance": "Why this matters to the current story"
  }},
  ...
]"""

        data = self.llm.generate_json(SYSTEM_PROMPT, prompt)
        return [LoreEntry(**entry) for entry in data]
