"""
Character Forge Agent — creates characters aware of the world and its factions.
Runs AFTER the Faction Engine so characters can belong to and be shaped by factions.
"""
from src.utils.llm_client import LLMClient
from src.models.schemas import World, Faction, Character, CharacterRelationship


SYSTEM_PROMPT = """You are the Character Forge — you breathe life into fictional characters.
Every character must feel human: contradictory, flawed, surprising.
Characters should be shaped by their world's unique mechanics and their faction's ideology.
Give them secrets that create story potential. Make their flaws narratively interesting.
Output valid JSON exactly matching the requested schema."""


class CharacterForgeAgent:
    """Generates complex characters grounded in the world and factions."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, world: World, factions: list[Faction], n_characters: int) -> list[Character]:
        """Generate characters for the universe."""
        faction_context = "\n".join(
            f"  - {f.id}: {f.name} [{f.alignment.value}] — {f.ideology}"
            for f in factions
        )

        roles = self._plan_roles(n_characters)

        prompt = f"""World: {world.name} ({world.genre})
Unique Mechanic: {world.unique_mechanic}
Tone: {world.tone}

Factions:
{faction_context}

Create {n_characters} characters. Use these roles: {roles}

Rules:
- Assign each character to a faction_id (or null if truly unaffiliated)
- Create relationships between characters using their IDs: char_1, char_2, ..., char_{n_characters}
- Each character's motivation should relate to the world's unique mechanic
- Secrets should create potential for betrayal, revelation, or conflict
- connected_lore can be empty (lore will be generated later)

Return a JSON array:
[
  {{
    "id": "char_1",
    "name": "Character Name",
    "role": "hero",
    "faction_id": "faction_1",
    "age": "32",
    "appearance": "2-sentence physical description",
    "backstory": "3-4 sentence backstory",
    "motivation": "What drives them above all else",
    "secret": "The secret they hide",
    "flaw": "Their defining character flaw",
    "skill": "Their greatest ability",
    "relationships": [
      {{
        "character_id": "char_2",
        "relationship_type": "rival",
        "description": "Why they're rivals"
      }}
    ],
    "connected_lore": []
  }},
  ...
]"""

        data = self.llm.generate_json(SYSTEM_PROMPT, prompt)
        return [Character(**c) for c in data]

    @staticmethod
    def _plan_roles(n: int) -> list[str]:
        role_pool = ["hero", "villain", "antihero", "mentor", "trickster", "support"]
        # Always have at least one hero and one villain
        base = ["hero", "villain"]
        remaining = role_pool[2:] * ((n // len(role_pool)) + 1)
        return (base + remaining)[:n]
