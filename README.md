# 🌌 Story Universe AI — Generative World-Building Engine

> **An AI-powered multi-agent system that generates rich, interconnected fictional universes — complete with characters, factions, lore, plot threads, and a narrative graph.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![LLM](https://img.shields.io/badge/Powered%20by-Claude%20API-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🎯 What Makes This Unique

Most LLM demos generate a single story or a single character. **Story Universe AI** treats world-building as a **graph problem solved by multiple specialized AI agents**:

- 🧠 **World Architect Agent** — designs the universe's rules, physics, and history
- 👤 **Character Forge Agent** — creates characters with backstories, motivations, and relationships
- ⚔️ **Faction Engine Agent** — builds competing factions with ideologies and goals
- 📜 **Lore Weaver Agent** — generates myths, legends, and historical events
- 🔀 **Plot Thread Agent** — weaves all elements into interconnected plot arcs
- 🗺️ **Universe Graph** — stores everything as a knowledge graph (NetworkX) for consistency

The agents **talk to each other** — characters reference lore, factions shape plot threads, and everything stays consistent via a shared universe state.

---

## 📁 Project Structure

```
story-universe-ai/
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── world_architect.py      # Designs universe rules & history
│   │   ├── character_forge.py      # Generates characters
│   │   ├── faction_engine.py       # Creates factions & conflicts
│   │   ├── lore_weaver.py          # Generates lore & mythology
│   │   └── plot_thread.py          # Weaves interconnected plot arcs
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm_client.py           # Anthropic API wrapper
│   │   ├── universe_graph.py       # Knowledge graph management
│   │   └── exporter.py             # Export universe to JSON/Markdown
│   └── models/
│       ├── __init__.py
│       └── schemas.py              # Pydantic schemas for all entities
│
├── data/
│   ├── outputs/                    # Generated universes saved here
│   └── examples/                  # Pre-generated example universes
│
├── tests/
│   ├── test_agents.py
│   ├── test_graph.py
│   └── test_schemas.py
│
├── notebooks/
│   └── explore_universe.ipynb      # Jupyter notebook to explore outputs
│
├── docs/
│   └── architecture.md             # Deep-dive architecture doc
│
├── main.py                         # CLI entry point
├── config.py                       # Configuration settings
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/story-universe-ai.git
cd story-universe-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 5. Generate your first universe!
```bash
python main.py --genre "dark fantasy" --scale medium --output my_universe
```

---

## 🎮 Usage

### CLI
```bash
# Generate a sci-fi universe
python main.py --genre "space opera" --scale large

# Generate with a seed theme
python main.py --genre "mythic horror" --seed "a world where dreams are real" --scale small

# List all generated universes
python main.py --list

# Export a universe to Markdown
python main.py --export my_universe --format markdown
```

### Python API
```python
from src.agents import UniverseOrchestrator
from config import Config

orchestrator = UniverseOrchestrator(Config())

universe = orchestrator.generate(
    genre="cyberpunk",
    seed="A city where memories can be bought and sold",
    scale="medium"   # small | medium | large
)

print(universe.summary())
universe.export("my_universe", format="json")
```

### Output Example
```
🌌 Universe: The Hollow Meridian
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Genre       : Dark Fantasy
Scale       : Medium
Entities    : 12 characters, 4 factions, 23 lore entries, 7 plot threads

🧭 World Rules:
  - Magic is drawn from collective grief
  - The sun has not risen in 300 years
  - ...

👤 Characters (12):
  - Sable Vorn — The last Grief-Mage, hunted by the Hollow Court
  - Mira Ashfen — A cartographer mapping the unmappable Voidlands
  - ...

⚔️ Factions (4):
  - The Hollow Court    [Antagonist]  Controls grief-magic supply
  - The Wandering Flame [Neutral]     Nomadic scholars of the old sun
  - ...

📜 Lore Highlights:
  - The Sundering (Year 0): Event that extinguished the sun
  - The First Grief-Mage: Mythological origin of magic
  - ...

🔀 Active Plot Threads:
  - Thread 1: Sable discovers the Hollow Court killed her mentor
  - Thread 2: Mira's map leads to a sun-restoration ritual
  - ...
```

---

## 🏗️ Architecture

### Multi-Agent Pipeline

```
User Input (genre + seed)
        │
        ▼
┌──────────────────┐
│  World Architect │  ──── Generates: world rules, geography, history
└────────┬─────────┘
         │ Universe State
         ▼
┌──────────────────┐
│  Faction Engine  │  ──── Generates: factions using world rules
└────────┬─────────┘
         │ + Factions
         ▼
┌──────────────────┐
│  Character Forge │  ──── Generates: characters aware of factions & world
└────────┬─────────┘
         │ + Characters
         ▼
┌──────────────────┐
│   Lore Weaver    │  ──── Generates: myths/history referencing all above
└────────┬─────────┘
         │ + Lore
         ▼
┌──────────────────┐
│  Plot Thread     │  ──── Weaves: plot arcs connecting everything
└────────┬─────────┘
         │
         ▼
   Universe Graph (NetworkX)
   + JSON/Markdown Export
```

### Universe Graph
All entities are stored as nodes in a **NetworkX graph** with typed edges:
- `CHARACTER → BELONGS_TO → FACTION`
- `CHARACTER → KNOWS_LORE → LORE_ENTRY`
- `PLOT_THREAD → INVOLVES → CHARACTER`
- `FACTION → CONFLICTS_WITH → FACTION`

This enables consistency checks and relationship queries.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📊 Example Universes

See [`data/examples/`](data/examples/) for pre-generated universes:
- `dark_fantasy_example.json` — *The Hollow Meridian*
- `space_opera_example.json` — *Echoes of the Drift*
- `mythic_horror_example.json` — *The Dreaming Sepulcher*

---

## 🔧 Configuration

Edit `config.py` or set environment variables:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | Your Anthropic API key |
| `MODEL` | `claude-sonnet-4-6` | LLM model to use |
| `MAX_CHARACTERS` | `12` | Max characters per universe |
| `MAX_FACTIONS` | `5` | Max factions per universe |
| `MAX_LORE_ENTRIES` | `25` | Max lore entries |
| `OUTPUT_DIR` | `data/outputs` | Where universes are saved |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/new-agent`
3. Commit your changes: `git commit -m 'Add new agent'`
4. Push: `git push origin feature/new-agent`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🌟 Roadmap

- [ ] Web UI (Streamlit/Gradio)
- [ ] Visual universe graph renderer (D3.js)
- [ ] Export to Twine (interactive fiction format)
- [ ] Multi-universe crossover mode
- [ ] Voice narration via TTS

---

*Built with ❤️ and Claude AI*
