# Architecture Deep-Dive

## Overview

Story Universe AI is a **multi-agent generative pipeline** built on top of the Anthropic Claude API. Each agent has a specialized role and receives the output of all previous agents as context, ensuring the final universe is internally consistent.

---

## Agent Pipeline

### 1. World Architect Agent
**File:** `src/agents/world_architect.py`  
**Input:** genre, seed concept, scale  
**Output:** `World` schema  

The first agent. Establishes the universe's foundational rules. The key output is the `unique_mechanic` — a single defining feature that makes the world unlike any other. All subsequent agents are aware of this mechanic.

### 2. Faction Engine Agent
**File:** `src/agents/faction_engine.py`  
**Input:** `World` + scale  
**Output:** `List[Faction]`  

Generates competing power groups. Each faction's ideology, goals, and methods are grounded in the world's unique mechanic. Alignment distribution is pre-planned (protagonist/antagonist/neutral/wildcard) to ensure narrative tension.

### 3. Character Forge Agent
**File:** `src/agents/character_forge.py`  
**Input:** `World` + `List[Faction]` + scale  
**Output:** `List[Character]`  

Characters know about factions and the world's mechanics. Each character is assigned to a faction, given relationships with other characters, and designed with motivations that tie to the world's unique mechanic.

### 4. Lore Weaver Agent
**File:** `src/agents/lore_weaver.py`  
**Input:** `World` + `List[Faction]` + `List[Character]` + scale  
**Output:** `List[LoreEntry]`  

The lore agent sees everything that came before. It creates myths, historical events, artifacts, locations, and prophecies that reference specific characters and factions. Lore entries are designed to create dramatic irony.

### 5. Plot Thread Agent
**File:** `src/agents/plot_thread.py`  
**Input:** all of the above + scale  
**Output:** `List[PlotThread]`  

The final agent sees the entire universe. It identifies narrative potential and creates intersecting plot arcs. Key constraint: threads must involve multiple characters and factions, and must reference lore.

### 6. Universe Graph
**File:** `src/utils/universe_graph.py`  

After all agents complete, the full universe is converted into a **NetworkX directed graph**. This enables:
- Consistency checking (are all referenced IDs valid?)
- Relationship queries (who is most connected?)
- Visual rendering (planned feature)
- Cross-universe analysis

---

## Data Flow

```
Config (genre, seed, scale)
         │
         ▼
  WorldArchitectAgent → World
         │
         ▼
  FactionEngineAgent(World) → [Faction, ...]
         │
         ▼
  CharacterForgeAgent(World, Factions) → [Character, ...]
         │
         ▼
  LoreWeaverAgent(World, Factions, Characters) → [LoreEntry, ...]
         │
         ▼
  PlotThreadAgent(World, Factions, Characters, Lore) → [PlotThread, ...]
         │
         ▼
  Universe(world, factions, characters, lore, plot_threads)
         │
         ├─► UniverseGraph (NetworkX)
         └─► UniverseExporter (JSON / Markdown)
```

---

## Schemas (Pydantic)

All entities are validated with Pydantic v2. Key schemas:

| Schema | Key Fields |
|---|---|
| `World` | name, genre, unique_mechanic, rules[], history[] |
| `Faction` | id, name, alignment, ideology, goal, enemies[], allies[] |
| `Character` | id, name, role, faction_id, motivation, secret, relationships[] |
| `LoreEntry` | id, title, lore_type, full_text, connected_factions[], connected_characters[] |
| `PlotThread` | id, title, status, hook, stakes, beats[], convergence_point |
| `Universe` | world, factions[], characters[], lore[], plot_threads[] |

---

## LLM Strategy

The `LLMClient` wrapper always requests **raw JSON output** — no markdown, no preamble. Each agent's system prompt:
1. Establishes the agent's identity and role
2. Enforces subversion of clichés
3. Demands raw JSON

JSON is parsed with error handling that strips accidental markdown fences.

---

## Extending the System

### Adding a new agent
1. Create `src/agents/my_agent.py` with a class that takes `LLMClient`
2. Add a `generate()` method returning a Pydantic model
3. Add the model to `src/models/schemas.py`
4. Wire it into `UniverseOrchestrator` in `src/agents/__init__.py`

### Adding a new export format
1. Add a new method to `UniverseExporter` in `src/utils/exporter.py`
2. Add the format option to the CLI in `main.py`
