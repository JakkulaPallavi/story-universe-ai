"""
Pydantic schemas for all Story Universe AI entities.
These ensure consistent, validated data across all agents.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class FactionAlignment(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST  = "antagonist"
    NEUTRAL     = "neutral"
    WILDCARD    = "wildcard"


class CharacterRole(str, Enum):
    HERO        = "hero"
    VILLAIN     = "villain"
    ANTIHERO    = "antihero"
    MENTOR      = "mentor"
    TRICKSTER   = "trickster"
    SUPPORT     = "support"


class LoreType(str, Enum):
    HISTORICAL_EVENT = "historical_event"
    MYTH_LEGEND      = "myth_legend"
    ARTIFACT         = "artifact"
    LOCATION         = "location"
    PROPHECY         = "prophecy"
    RITUAL           = "ritual"


class PlotThreadStatus(str, Enum):
    DORMANT  = "dormant"
    ACTIVE   = "active"
    CLIMAX   = "climax"
    RESOLVED = "resolved"


# ── World ─────────────────────────────────────────────────────────────────────

class WorldRule(BaseModel):
    name: str = Field(..., description="Short name for the rule")
    description: str = Field(..., description="Full description of how this rule works")
    impact: str = Field(..., description="How this rule affects daily life or conflict")


class WorldHistory(BaseModel):
    era: str = Field(..., description="Name of the historical era")
    years: str = Field(..., description="Time span, e.g. '0–300 years ago'")
    summary: str = Field(..., description="What happened in this era")


class World(BaseModel):
    name: str
    genre: str
    seed_concept: str
    tagline: str = Field(..., description="One evocative sentence describing this universe")
    geography: str = Field(..., description="Description of the physical world")
    rules: list[WorldRule] = Field(default_factory=list)
    history: list[WorldHistory] = Field(default_factory=list)
    tone: str = Field(..., description="Overall narrative tone, e.g. 'grim and hopeful'")
    unique_mechanic: str = Field(..., description="The one defining mechanic that makes this world unique")


# ── Faction ───────────────────────────────────────────────────────────────────

class Faction(BaseModel):
    id: str
    name: str
    alignment: FactionAlignment
    ideology: str = Field(..., description="Core belief system of this faction")
    goal: str = Field(..., description="What this faction ultimately wants")
    methods: str = Field(..., description="How they pursue their goal")
    symbol: str = Field(..., description="Their emblem or symbol and its meaning")
    strength: str = Field(..., description="Their primary source of power")
    weakness: str = Field(..., description="Their critical vulnerability")
    enemies: list[str] = Field(default_factory=list, description="IDs of enemy factions")
    allies: list[str] = Field(default_factory=list, description="IDs of allied factions")


# ── Character ─────────────────────────────────────────────────────────────────

class CharacterRelationship(BaseModel):
    character_id: str
    relationship_type: str  # e.g. "rival", "mentor", "sibling", "betrayer"
    description: str


class Character(BaseModel):
    id: str
    name: str
    role: CharacterRole
    faction_id: Optional[str] = None
    age: str
    appearance: str
    backstory: str
    motivation: str = Field(..., description="What drives this character above all else")
    secret: str = Field(..., description="The secret they hide from the world")
    flaw: str = Field(..., description="Their defining character flaw")
    skill: str = Field(..., description="Their greatest ability or power")
    relationships: list[CharacterRelationship] = Field(default_factory=list)
    connected_lore: list[str] = Field(default_factory=list, description="IDs of lore entries they're tied to")


# ── Lore ──────────────────────────────────────────────────────────────────────

class LoreEntry(BaseModel):
    id: str
    title: str
    lore_type: LoreType
    summary: str
    full_text: str = Field(..., description="The full lore entry as it might appear in a codex")
    connected_factions: list[str] = Field(default_factory=list)
    connected_characters: list[str] = Field(default_factory=list)
    importance: str = Field(..., description="Why this lore matters to the current story")


# ── Plot Thread ───────────────────────────────────────────────────────────────

class PlotBeat(BaseModel):
    beat_number: int
    title: str
    description: str
    characters_involved: list[str]


class PlotThread(BaseModel):
    id: str
    title: str
    status: PlotThreadStatus
    hook: str = Field(..., description="The inciting incident or opening tension")
    stakes: str = Field(..., description="What happens if this thread resolves badly")
    characters_involved: list[str]
    factions_involved: list[str]
    lore_involved: list[str]
    beats: list[PlotBeat] = Field(default_factory=list)
    convergence_point: str = Field(..., description="How this thread connects to or affects other threads")


# ── Universe (top-level container) ────────────────────────────────────────────

class Universe(BaseModel):
    world: World
    factions: list[Faction] = Field(default_factory=list)
    characters: list[Character] = Field(default_factory=list)
    lore: list[LoreEntry] = Field(default_factory=list)
    plot_threads: list[PlotThread] = Field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"\n🌌 Universe: {self.world.name}",
            "━" * 40,
            f"Genre       : {self.world.genre}",
            f"Tagline     : {self.world.tagline}",
            f"Entities    : {len(self.characters)} characters, {len(self.factions)} factions, "
            f"{len(self.lore)} lore entries, {len(self.plot_threads)} plot threads",
            "",
            "🔑 Unique Mechanic:",
            f"  {self.world.unique_mechanic}",
            "",
            "⚔️  Factions:",
        ]
        for f in self.factions:
            lines.append(f"  [{f.alignment.value.upper():12}] {f.name} — {f.ideology[:60]}")
        lines.append("")
        lines.append("👤 Characters:")
        for c in self.characters:
            faction_name = next((f.name for f in self.factions if f.id == c.faction_id), "Unaffiliated")
            lines.append(f"  [{c.role.value.upper():10}] {c.name} ({faction_name})")
            lines.append(f"               ↳ {c.motivation[:70]}")
        lines.append("")
        lines.append("🔀 Plot Threads:")
        for p in self.plot_threads:
            lines.append(f"  [{p.status.value.upper():8}] {p.title}")
            lines.append(f"             ↳ {p.hook[:70]}")
        return "\n".join(lines)
