"""
Universe Knowledge Graph — stores all entities and their relationships
as a NetworkX directed graph for consistency checking and querying.
"""
import networkx as nx
from typing import Optional
from src.models.schemas import Universe, Character, Faction, LoreEntry, PlotThread


class UniverseGraph:
    """
    A directed knowledge graph for a generated universe.
    
    Node types: world, faction, character, lore, plot_thread
    Edge types: BELONGS_TO, KNOWS_LORE, CONFLICTS_WITH, ALLIED_WITH,
                INVOLVES, REFERENCES, CONNECTED_TO
    """

    def __init__(self):
        self.G = nx.DiGraph()

    def build_from_universe(self, universe: Universe) -> None:
        """Populate the graph from a complete Universe object."""
        self._add_world(universe)
        for faction in universe.factions:
            self._add_faction(faction)
        for character in universe.characters:
            self._add_character(character, universe.factions)
        for lore in universe.lore:
            self._add_lore(lore)
        for thread in universe.plot_threads:
            self._add_plot_thread(thread)

    # ── Node adders ──────────────────────────────────────────────────────────

    def _add_world(self, universe: Universe):
        self.G.add_node(
            "world",
            node_type="world",
            name=universe.world.name,
            genre=universe.world.genre,
        )

    def _add_faction(self, faction: Faction):
        self.G.add_node(
            faction.id,
            node_type="faction",
            name=faction.name,
            alignment=faction.alignment.value,
        )
        self.G.add_edge("world", faction.id, relation="CONTAINS")
        for enemy_id in faction.enemies:
            self.G.add_edge(faction.id, enemy_id, relation="CONFLICTS_WITH")
        for ally_id in faction.allies:
            self.G.add_edge(faction.id, ally_id, relation="ALLIED_WITH")

    def _add_character(self, character: Character, factions: list[Faction]):
        self.G.add_node(
            character.id,
            node_type="character",
            name=character.name,
            role=character.role.value,
        )
        if character.faction_id:
            self.G.add_edge(character.id, character.faction_id, relation="BELONGS_TO")
        for rel in character.relationships:
            self.G.add_edge(
                character.id,
                rel.character_id,
                relation=rel.relationship_type.upper().replace(" ", "_"),
            )
        for lore_id in character.connected_lore:
            self.G.add_edge(character.id, lore_id, relation="KNOWS_LORE")

    def _add_lore(self, lore: LoreEntry):
        self.G.add_node(
            lore.id,
            node_type="lore",
            title=lore.title,
            lore_type=lore.lore_type.value,
        )
        for faction_id in lore.connected_factions:
            self.G.add_edge(lore.id, faction_id, relation="REFERENCES")
        for char_id in lore.connected_characters:
            self.G.add_edge(lore.id, char_id, relation="REFERENCES")

    def _add_plot_thread(self, thread: PlotThread):
        self.G.add_node(
            thread.id,
            node_type="plot_thread",
            title=thread.title,
            status=thread.status.value,
        )
        for char_id in thread.characters_involved:
            self.G.add_edge(thread.id, char_id, relation="INVOLVES")
        for faction_id in thread.factions_involved:
            self.G.add_edge(thread.id, faction_id, relation="INVOLVES")
        for lore_id in thread.lore_involved:
            self.G.add_edge(thread.id, lore_id, relation="INVOLVES")

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_character_connections(self, character_id: str) -> dict:
        """Return everything a character is connected to."""
        neighbors = list(self.G.neighbors(character_id))
        result = {"character_id": character_id, "connections": []}
        for n in neighbors:
            edge_data = self.G.get_edge_data(character_id, n)
            node_data = self.G.nodes[n]
            result["connections"].append({
                "id": n,
                "type": node_data.get("node_type"),
                "name": node_data.get("name") or node_data.get("title"),
                "relation": edge_data.get("relation"),
            })
        return result

    def get_most_connected_entities(self, top_n: int = 5) -> list[dict]:
        """Return the top N most connected nodes (narrative hubs)."""
        degrees = [(node, deg) for node, deg in self.G.degree()]
        degrees.sort(key=lambda x: x[1], reverse=True)
        result = []
        for node_id, degree in degrees[:top_n]:
            data = self.G.nodes[node_id]
            result.append({
                "id": node_id,
                "type": data.get("node_type"),
                "name": data.get("name") or data.get("title", node_id),
                "connections": degree,
            })
        return result

    def stats(self) -> dict:
        return {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "node_types": {
                nt: sum(1 for _, d in self.G.nodes(data=True) if d.get("node_type") == nt)
                for nt in ["world", "faction", "character", "lore", "plot_thread"]
            },
        }

    def to_dict(self) -> dict:
        """Serialize graph for export."""
        return nx.node_link_data(self.G)
