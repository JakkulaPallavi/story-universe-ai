"""
Exporter — saves generated universes to JSON or Markdown files.
"""
import json
import os
from datetime import datetime
from src.models.schemas import Universe
from src.utils.universe_graph import UniverseGraph


class UniverseExporter:

    def __init__(self, output_dir: str = "data/outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(
        self,
        universe: Universe,
        graph: UniverseGraph,
        name: str,
        fmt: str = "json",
    ) -> str:
        """Export universe to file. Returns the output path."""
        slug = name.lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}_{timestamp}"

        if fmt == "json":
            return self._export_json(universe, graph, filename)
        elif fmt == "markdown":
            return self._export_markdown(universe, filename)
        else:
            raise ValueError(f"Unknown format: {fmt}. Use 'json' or 'markdown'.")

    def _export_json(self, universe: Universe, graph: UniverseGraph, filename: str) -> str:
        path = os.path.join(self.output_dir, f"{filename}.json")
        data = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
            },
            "universe": universe.model_dump(),
            "graph": graph.to_dict(),
            "graph_stats": graph.stats(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path

    def _export_markdown(self, universe: Universe, filename: str) -> str:
        path = os.path.join(self.output_dir, f"{filename}.md")
        w = universe.world
        lines = [
            f"# 🌌 {w.name}",
            "",
            f"> *{w.tagline}*",
            "",
            f"**Genre:** {w.genre}  ",
            f"**Tone:** {w.tone}  ",
            f"**Unique Mechanic:** {w.unique_mechanic}",
            "",
            "---",
            "",
            "## 🗺️ The World",
            "",
            w.geography,
            "",
            "### World Rules",
            "",
        ]
        for rule in w.rules:
            lines += [f"#### {rule.name}", rule.description, f"*Impact: {rule.impact}*", ""]

        lines += ["### History", ""]
        for era in w.history:
            lines += [f"**{era.era}** ({era.years})", era.summary, ""]

        lines += ["---", "", "## ⚔️ Factions", ""]
        for f in universe.factions:
            lines += [
                f"### {f.name} `[{f.alignment.value.upper()}]`",
                "",
                f"**Ideology:** {f.ideology}  ",
                f"**Goal:** {f.goal}  ",
                f"**Methods:** {f.methods}  ",
                f"**Symbol:** {f.symbol}  ",
                f"**Strength:** {f.strength}  ",
                f"**Weakness:** {f.weakness}",
                "",
            ]

        lines += ["---", "", "## 👤 Characters", ""]
        for c in universe.characters:
            faction_name = next(
                (f.name for f in universe.factions if f.id == c.faction_id),
                "Unaffiliated"
            )
            lines += [
                f"### {c.name} `[{c.role.value.upper()}]`",
                "",
                f"**Faction:** {faction_name}  ",
                f"**Age:** {c.age}  ",
                f"**Appearance:** {c.appearance}",
                "",
                f"**Backstory:** {c.backstory}",
                "",
                f"**Motivation:** {c.motivation}  ",
                f"**Secret:** {c.secret}  ",
                f"**Flaw:** {c.flaw}  ",
                f"**Skill:** {c.skill}",
                "",
            ]
            if c.relationships:
                lines.append("**Relationships:**")
                for rel in c.relationships:
                    char_name = next(
                        (ch.name for ch in universe.characters if ch.id == rel.character_id),
                        rel.character_id
                    )
                    lines.append(f"- {rel.relationship_type} of **{char_name}**: {rel.description}")
                lines.append("")

        lines += ["---", "", "## 📜 Lore & Codex", ""]
        for lore in universe.lore:
            lines += [
                f"### {lore.title} `[{lore.lore_type.value.replace('_', ' ').upper()}]`",
                "",
                lore.full_text,
                "",
                f"*Importance: {lore.importance}*",
                "",
            ]

        lines += ["---", "", "## 🔀 Plot Threads", ""]
        for thread in universe.plot_threads:
            lines += [
                f"### {thread.title} `[{thread.status.value.upper()}]`",
                "",
                f"**Hook:** {thread.hook}",
                "",
                f"**Stakes:** {thread.stakes}",
                "",
            ]
            if thread.beats:
                lines.append("**Story Beats:**")
                for beat in thread.beats:
                    lines.append(f"{beat.beat_number}. **{beat.title}** — {beat.description}")
                lines.append("")
            lines.append(f"**Convergence:** {thread.convergence_point}")
            lines.append("")

        lines += [
            "---",
            "",
            f"*Generated by Story Universe AI — {datetime.now().strftime('%Y-%m-%d')}*",
        ]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path
