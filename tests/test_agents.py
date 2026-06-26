"""
Tests for Story Universe AI.
Run with: pytest tests/ -v
"""
import pytest
from unittest.mock import MagicMock, patch
from src.models.schemas import (
    World, WorldRule, WorldHistory, Faction, FactionAlignment,
    Character, CharacterRole, LoreEntry, LoreType,
    PlotThread, PlotThreadStatus, Universe
)
from src.utils.universe_graph import UniverseGraph


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_world():
    return World(
        name="The Hollow Meridian",
        genre="dark fantasy",
        seed_concept="a world where grief is fuel",
        tagline="The sun died three centuries ago. Grief keeps the lights on.",
        geography="A continent of perpetual twilight, lit by grief-lanterns.",
        tone="Bittersweet and mythic",
        unique_mechanic="Magic is drawn from collective grief — the more people mourn, the more power is available.",
        rules=[
            WorldRule(
                name="The Grief Tide",
                description="Collective mourning generates magical energy",
                impact="Governments manufacture tragedies to maintain power"
            )
        ],
        history=[
            WorldHistory(
                era="The Sundering",
                years="300 years ago",
                summary="The sun was extinguished in a catastrophic ritual"
            )
        ]
    )


@pytest.fixture
def sample_factions():
    return [
        Faction(
            id="faction_1",
            name="The Hollow Court",
            alignment=FactionAlignment.ANTAGONIST,
            ideology="Control grief, control power",
            goal="Maintain monopoly on grief-magic",
            methods="Manufacturing disasters",
            symbol="A black sun",
            strength="Unlimited political power",
            weakness="Cannot function without causing suffering",
            enemies=["faction_2"],
            allies=[]
        ),
        Faction(
            id="faction_2",
            name="The Wandering Flame",
            alignment=FactionAlignment.PROTAGONIST,
            ideology="Freedom from manufactured grief",
            goal="Restore the sun",
            methods="Scholarship and rebellion",
            symbol="A torch in darkness",
            strength="Knowledge",
            weakness="Too few members",
            enemies=["faction_1"],
            allies=[]
        )
    ]


@pytest.fixture
def sample_characters(sample_factions):
    return [
        Character(
            id="char_1",
            name="Sable Vorn",
            role=CharacterRole.HERO,
            faction_id="faction_2",
            age="28",
            appearance="Tall, pale, with grief-burned silver eyes.",
            backstory="Last of the Grief-Mages. Her entire village was sacrificed by the Hollow Court.",
            motivation="Expose the Hollow Court's manufactured tragedies",
            secret="She secretly loves grief-magic and fears becoming what she fights",
            flaw="Cannot trust anyone who hasn't suffered",
            skill="Can sense the origin of grief",
            relationships=[],
            connected_lore=[]
        )
    ]


@pytest.fixture
def sample_lore():
    return [
        LoreEntry(
            id="lore_1",
            title="The Sundering",
            lore_type=LoreType.HISTORICAL_EVENT,
            summary="The ritual that killed the sun",
            full_text="Three hundred years past, the Mage-Kings attempted to weaponize the sun itself...",
            connected_factions=["faction_1"],
            connected_characters=["char_1"],
            importance="Explains why the Hollow Court exists and why grief-magic is possible"
        )
    ]


@pytest.fixture
def sample_plot_thread():
    from src.models.schemas import PlotBeat
    return PlotThread(
        id="thread_1",
        title="The Last Grief-Mage",
        status=PlotThreadStatus.ACTIVE,
        hook="Sable discovers the Hollow Court killed her mentor",
        stakes="If she fails, manufactured grief becomes permanent law",
        characters_involved=["char_1"],
        factions_involved=["faction_1", "faction_2"],
        lore_involved=["lore_1"],
        beats=[
            PlotBeat(
                beat_number=1,
                title="Discovery",
                description="Sable finds evidence",
                characters_involved=["char_1"]
            )
        ],
        convergence_point="Connects to the sun-restoration thread when Sable's investigation reveals the ritual site"
    )


@pytest.fixture
def sample_universe(sample_world, sample_factions, sample_characters, sample_lore, sample_plot_thread):
    return Universe(
        world=sample_world,
        factions=sample_factions,
        characters=sample_characters,
        lore=sample_lore,
        plot_threads=[sample_plot_thread]
    )


# ── Schema Tests ──────────────────────────────────────────────────────────────

class TestSchemas:

    def test_world_creation(self, sample_world):
        assert sample_world.name == "The Hollow Meridian"
        assert len(sample_world.rules) == 1
        assert len(sample_world.history) == 1

    def test_faction_alignment_enum(self, sample_factions):
        assert sample_factions[0].alignment == FactionAlignment.ANTAGONIST
        assert sample_factions[1].alignment == FactionAlignment.PROTAGONIST

    def test_character_role_enum(self, sample_characters):
        assert sample_characters[0].role == CharacterRole.HERO

    def test_lore_type_enum(self, sample_lore):
        assert sample_lore[0].lore_type == LoreType.HISTORICAL_EVENT

    def test_universe_summary(self, sample_universe):
        summary = sample_universe.summary()
        assert "The Hollow Meridian" in summary
        assert "Sable Vorn" in summary
        assert "The Hollow Court" in summary

    def test_universe_serialization(self, sample_universe):
        data = sample_universe.model_dump()
        restored = Universe(**data)
        assert restored.world.name == sample_universe.world.name
        assert len(restored.factions) == len(sample_universe.factions)
        assert len(restored.characters) == len(sample_universe.characters)


# ── Graph Tests ───────────────────────────────────────────────────────────────

class TestUniverseGraph:

    def test_build_graph(self, sample_universe):
        graph = UniverseGraph()
        graph.build_from_universe(sample_universe)
        stats = graph.stats()
        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0

    def test_node_counts(self, sample_universe):
        graph = UniverseGraph()
        graph.build_from_universe(sample_universe)
        stats = graph.stats()
        assert stats["node_types"]["faction"] == 2
        assert stats["node_types"]["character"] == 1
        assert stats["node_types"]["lore"] == 1
        assert stats["node_types"]["plot_thread"] == 1

    def test_character_connections(self, sample_universe):
        graph = UniverseGraph()
        graph.build_from_universe(sample_universe)
        connections = graph.get_character_connections("char_1")
        assert connections["character_id"] == "char_1"
        # char_1 is in faction_2
        faction_conn = [c for c in connections["connections"] if c["id"] == "faction_2"]
        assert len(faction_conn) == 1
        assert faction_conn[0]["relation"] == "BELONGS_TO"

    def test_most_connected(self, sample_universe):
        graph = UniverseGraph()
        graph.build_from_universe(sample_universe)
        hubs = graph.get_most_connected_entities(top_n=3)
        assert len(hubs) <= 3
        assert all("name" in h for h in hubs)

    def test_graph_serialization(self, sample_universe):
        graph = UniverseGraph()
        graph.build_from_universe(sample_universe)
        data = graph.to_dict()
        assert "nodes" in data
        assert "links" in data or "edges" in data


# ── Config Tests ──────────────────────────────────────────────────────────────

class TestConfig:

    def test_scale_presets(self):
        from config import Config
        config = Config()
        small = config.get_scale("small")
        large = config.get_scale("large")
        assert small["characters"] < large["characters"]
        assert small["lore"] < large["lore"]

    def test_missing_api_key_raises(self):
        from config import Config
        config = Config(anthropic_api_key="")
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            config.validate()

    def test_valid_config(self):
        from config import Config
        config = Config(anthropic_api_key="test-key-123")
        validated = config.validate()
        assert validated.anthropic_api_key == "test-key-123"
