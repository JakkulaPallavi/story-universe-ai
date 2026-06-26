"""
Story Universe AI — CLI Entry Point

Usage examples:
  python main.py --genre "dark fantasy" --scale medium --output my_universe
  python main.py --genre "cyberpunk" --seed "a city where time flows backwards" --scale large
  python main.py --genre "space opera" --output my_space_opera --format markdown
"""
import typer
from typing import Optional
from rich.console import Console
from config import Config
from src.agents import UniverseOrchestrator

app = Console()
cli = typer.Typer(
    help="🌌 Story Universe AI — Generate rich fictional universes with multi-agent AI",
    add_completion=False,
)


@cli.command()
def generate(
    genre: str = typer.Option(
        "dark fantasy",
        "--genre", "-g",
        help="Genre of the universe (e.g. 'space opera', 'cyberpunk', 'mythic horror')"
    ),
    seed: str = typer.Option(
        "",
        "--seed", "-s",
        help="Optional seed concept to anchor the universe"
    ),
    scale: str = typer.Option(
        "medium",
        "--scale",
        help="Universe scale: small | medium | large"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Name to export the universe under (no extension)"
    ),
    fmt: str = typer.Option(
        "json",
        "--format", "-f",
        help="Export format: json | markdown"
    ),
):
    """Generate a new fictional universe."""
    if scale not in ("small", "medium", "large"):
        typer.echo("❌ Scale must be: small, medium, or large")
        raise typer.Exit(1)

    try:
        config = Config()
        orchestrator = UniverseOrchestrator(config)
        orchestrator.generate(
            genre=genre,
            seed=seed,
            scale=scale,
            export_name=output,
            export_format=fmt,
            verbose=True,
        )
    except ValueError as e:
        typer.echo(f"❌ Configuration error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Generation failed: {e}")
        raise typer.Exit(1)


@cli.command()
def list_universes(
    output_dir: str = typer.Option("data/outputs", "--dir", "-d")
):
    """List all previously generated universes."""
    import os
    if not os.path.exists(output_dir):
        typer.echo("No universes generated yet.")
        return
    files = os.listdir(output_dir)
    if not files:
        typer.echo("No universes found.")
        return
    typer.echo(f"\n🌌 Generated Universes in {output_dir}/:\n")
    for f in sorted(files):
        typer.echo(f"  📄 {f}")


if __name__ == "__main__":
    cli()
