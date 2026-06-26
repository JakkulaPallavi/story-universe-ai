"""
Universe Orchestrator — coordinates all agents to produce a complete universe.
This is the main entry point for the generation pipeline.
"""
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Config
from src.utils.llm_client import LLMClient
from src.utils.universe_graph import UniverseGraph
from src.utils.exporter import UniverseExporter
from src.models.schemas import Universe
from src.agents.world_architect import WorldArchitectAgent
from src.agents.faction_engine import FactionEngineAgent
from src.agents.character_forge import CharacterForgeAgent
from src.agents.lore_weaver import LoreWeaverAgent
from src.agents.plot_thread import PlotThreadAgent

console = Console()


class UniverseOrchestrator:
    """
    Coordinates the multi-agent pipeline to generate a complete universe.
    Pipeline order: World → Factions → Characters → Lore → Plot Threads → Graph
    """

    def __init__(self, config: Config):
        config.validate()
        self.config = config
        self.llm = LLMClient(config)

        # Initialize all agents
        self.world_architect  = WorldArchitectAgent(self.llm)
        self.faction_engine   = FactionEngineAgent(self.llm)
        self.character_forge  = CharacterForgeAgent(self.llm)
        self.lore_weaver      = LoreWeaverAgent(self.llm)
        self.plot_thread      = PlotThreadAgent(self.llm)
        self.exporter         = UniverseExporter(config.output_dir)

    def generate(
        self,
        genre: str,
        seed: str = "",
        scale: str = "medium",
        export_name: str | None = None,
        export_format: str = "json",
        verbose: bool = True,
    ) -> Universe:
        """Run the full generation pipeline and return a Universe."""
        limits = self.config.get_scale(scale)

        if not seed:
            seed = f"A unique {genre} universe unlike any other"

        steps = [
            ("🌍 World Architect", "Designing world rules & history..."),
            ("⚔️  Faction Engine",  "Building competing factions..."),
            ("👤 Character Forge", "Forging characters..."),
            ("📜 Lore Weaver",     "Weaving myths & history..."),
            ("🔀 Plot Threads",    "Spinning plot arcs..."),
            ("🕸️  Universe Graph", "Building knowledge graph..."),
        ]

        world = factions = characters = lore = plot_threads = None
        graph = UniverseGraph()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
            transient=True,
        ) as progress:

            # Step 1: World
            task = progress.add_task(steps[0][1], total=None)
            world = self.world_architect.generate(genre, seed, limits)
            progress.update(task, description=f"✅ World: [bold]{world.name}[/bold]")
            if verbose:
                console.print(f"  [green]✓[/green] World created: [bold]{world.name}[/bold]")
                console.print(f"    {world.tagline}")

            # Step 2: Factions
            task = progress.add_task(steps[1][1], total=None)
            factions = self.faction_engine.generate(world, limits["factions"])
            if verbose:
                console.print(f"  [green]✓[/green] {len(factions)} factions created")

            # Step 3: Characters
            task = progress.add_task(steps[2][1], total=None)
            characters = self.character_forge.generate(world, factions, limits["characters"])
            if verbose:
                console.print(f"  [green]✓[/green] {len(characters)} characters forged")

            # Step 4: Lore
            task = progress.add_task(steps[3][1], total=None)
            lore = self.lore_weaver.generate(world, factions, characters, limits["lore"])
            if verbose:
                console.print(f"  [green]✓[/green] {len(lore)} lore entries woven")

            # Step 5: Plot Threads
            task = progress.add_task(steps[4][1], total=None)
            plot_threads = self.plot_thread.generate(world, factions, characters, lore, limits["plot_threads"])
            if verbose:
                console.print(f"  [green]✓[/green] {len(plot_threads)} plot threads created")

            # Step 6: Build graph
            universe = Universe(
                world=world,
                factions=factions,
                characters=characters,
                lore=lore,
                plot_threads=plot_threads,
            )
            graph.build_from_universe(universe)
            stats = graph.stats()
            if verbose:
                console.print(
                    f"  [green]✓[/green] Graph built: "
                    f"{stats['total_nodes']} nodes, {stats['total_edges']} edges"
                )

        # Export if requested
        if export_name:
            path = self.exporter.export(universe, graph, export_name, export_format)
            console.print(f"\n  [bold green]💾 Exported:[/bold green] {path}")

        console.print(universe.summary())

        # Print most connected entities
        hubs = graph.get_most_connected_entities(top_n=3)
        console.print("\n🕸️  Most Connected Entities (narrative hubs):")
        for hub in hubs:
            console.print(f"   [{hub['type'].upper():12}] {hub['name']} — {hub['connections']} connections")

        return universe
