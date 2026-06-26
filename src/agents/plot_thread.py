"""
Plot Thread Agent — weaves interconnected plot arcs from all other universe elements.
The final agent: it sees everything and creates narrative threads that span the universe.
"""
from src.utils.llm_client import LLMClient
from src.models.schemas import World, Faction, Character, LoreEntry, PlotThread, PlotBeat, PlotThreadStatus


SYSTEM_PROMPT = """You are the Plot Thread Weaver — you create the dramatic tensions that tie a universe together.
You see ALL characters, factions, and lore, and you find the hidden dramatic potential.
Great plot threads are not isolated stories — they intersect, complicate each other, and share characters.
Every thread should make at least two characters or factions collide in an interesting way.
Output valid JSON exactly matching the requested schema."""


class PlotThreadAgent:
    """Generates plot threads that weave characters, factions, and lore together."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(
        self,
        world: World,
        factions: list[Faction],
        characters: list[Character],
        lore: list[LoreEntry],
        n_threads: int,
    ) -> list[PlotThread]:
        """Generate plot threads for the universe."""
        faction_summary = "\n".join(
            f"  - {f.id}: {f.name} [{f.alignment.value}] wants: {f.goal}"
            for f in factions
        )
        char_summary = "\n".join(
            f"  - {c.id}: {c.name} [{c.role.value}] motivation: {c.motivation} | secret: {c.secret}"
            for c in characters
        )
        lore_summary = "\n".join(
            f"  - {l.id}: {l.title} — {l.summary}"
            for l in lore
        )
        statuses = [s.value for s in PlotThreadStatus]

        prompt = f"""World: {world.name} ({world.genre})
Unique Mechanic: {world.unique_mechanic}
Tone: {world.tone}

Factions:
{faction_summary}

Characters:
{char_summary}

Lore:
{lore_summary}

Create {n_threads} plot threads that interconnect these elements.

Requirements:
- Each thread must involve 2+ characters and reference at least 1 lore entry
- Threads should INTERSECT — characters appear in multiple threads
- Include threads of different statuses: {statuses}
- convergence_point explains how this thread connects to OR creates tension in other threads
- Each thread has 3 story beats
- IDs: thread_1, thread_2, ..., thread_{n_threads}

Return a JSON array:
[
  {{
    "id": "thread_1",
    "title": "Thread Title",
    "status": "active",
    "hook": "The inciting incident or opening tension",
    "stakes": "What happens if this thread resolves badly",
    "characters_involved": ["char_1", "char_2"],
    "factions_involved": ["faction_1"],
    "lore_involved": ["lore_1"],
    "beats": [
      {{
        "beat_number": 1,
        "title": "Beat Title",
        "description": "What happens in this beat",
        "characters_involved": ["char_1"]
      }},
      {{
        "beat_number": 2,
        "title": "Escalation",
        "description": "How things get worse",
        "characters_involved": ["char_1", "char_2"]
      }},
      {{
        "beat_number": 3,
        "title": "Cliffhanger",
        "description": "Where this beat leaves off",
        "characters_involved": ["char_2"]
      }}
    ],
    "convergence_point": "How this thread connects to or affects other threads"
  }},
  ...
]"""

        data = self.llm.generate_json(SYSTEM_PROMPT, prompt)
        return [PlotThread(**t) for t in data]
