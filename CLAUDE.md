# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Neurona v3.0** is an interactive visual simulator of a biological neuron using the **Leaky Integrate-and-Fire (LIF)** model, enhanced with **real-time AI learning** from internet sources. The simulator combines artificial biology with cognitive AI to create an educational system that learns about computer science in real-time.

### Transformation Timeline
- **v1**: Single neuron simulator (LIF + oscilloscope)
- **v2**: Dual neuron network with synapsis + SFA
- **v3** (CURRENT): Cognitive neuron with Claude AI + memory + web learning

## Stack & Architecture

### Technology Stack
- **Language**: Python 3.8+
- **Rendering**: pygame >= 2.5.0 (1600×900, 60 FPS)
- **AI Motor**: Anthropic Claude API (claude-haiku-4-5-20251001)
- **Memory**: Local JSON vector store + TF-IDF manual search
- **Web Scraping**: requests + beautifulsoup4 (APIs: Stack Overflow, Wikipedia, GitHub, HackerNews, DEV.to)
- **Visual Style**: Strict minimalism — black (#000000) + white (#FFFFFF) + grayscale only

### Module Architecture

```
┌─────────────────────────────────────────────┐
│         NEURONA v3.0 - Modular Stack        │
├─────────────────────────────────────────────┤
│  main.py            → Pygame UI orchestration
│  brain.py           → Claude API + orchestration
│  memory.py          → Local JSON vector store
│  crawler.py         → Web scraping (5 sources)
│  neurona_lif.py     → Biological LIF model
│  config.py          → Centralized configuration
└─────────────────────────────────────────────┘
```

## Core Modules (v3.0)

### 1. `neurona_lif.py` — LIF Model with SFA
**Purpose**: Simulate biological neuron dynamics.

**Key Parameters**:
- `v_rest=0.0`: Resting potential
- `v_thresh=1.0`: Firing threshold
- `v_reset=-0.2`: Post-spike hyperpolarization
- `tau_m=25.0`: Membrane time constant
- `tau_adap=150.0`: Adaptation time constant
- `delta_adap=0.25`: Adaptation increment per spike
- `t_ref=8.0`: Refractory period (ms)

**Features**:
- Spike Frequency Adaptation (SFA) — causes neuron "fatigue"
- Real-time statistics: `firing_rate` (Hz), `spike_count`, `isi_history`
- Separate excitatory/inhibitory inputs: `update(I_excit, I_inhib=0.0)`
- 400-sample voltage history for visualization

**Methods**:
- `update(I_excit, I_inhib=0.0)` → returns spike boolean
- `get_voltage()` → current membrane potential
- `get_stats()` → dict of `{voltage, firing_rate, spike_count, refractory_pct, adaptation}`
- `reset()` → full state reset to baseline

### 2. `memory.py` — Local Vector Store
**Purpose**: Store and retrieve learned knowledge using manual TF-IDF.

**Data Structure** (memory.json):
```json
{
  "nodes": [
    {
      "id": "uuid",
      "topic": "Python recursion",
      "content": "Full text...",
      "source": "stackoverflow.com",
      "keywords": ["recursion", "function", "python"],
      "timestamp": "2026-04-10T...",
      "access_count": 3,
      "weight": 0.85
    }
  ],
  "connections": [
    {"from": "uuid1", "to": "uuid2", "strength": 0.72}
  ]
}
```

**Methods**:
- `add_node(topic, content, source, keywords)` → add knowledge, returns node_id
- `search(query, top_k=5)` → TF-IDF cosine similarity search, returns `[{node, score}, ...]`
- `strengthen(node_id)` → increment weight when accessed
- `get_visual_layout(max_nodes=80)` → spring-layout positions for visualization
- `get_stats()` → `{total_nodes, unique_topics, sources, avg_weight, total_accesses}`

**Search Algorithm**:
1. Tokenize query → TF dict
2. For each node: tokenize content → TF dict
3. Compute cosine similarity
4. Boost by node weight (frequently used = higher score)
5. Return top-K by score

### 3. `crawler.py` — Web Scraping
**Purpose**: Fetch real-time technical content from 5 free sources (no authentication).

**Sources**:
- **Stack Overflow**: Top Q&A by relevance
- **Wikipedia**: Article summaries
- **GitHub**: Trending repositories
- **HackerNews**: Top stories
- **DEV.to**: Recent articles

**Methods**:
- `search_topic(query, sources=None)` → multi-source search, returns `[{source, title, content, url}, ...]`
- `fetch_stackoverflow(query, max_results=3)`
- `fetch_wikipedia(query)`
- `fetch_github(query, max_results=3)`
- `fetch_hackernews(query, max_results=3)`
- `fetch_devto(query, max_results=3)`

**Return Format**:
```python
{
    "source": "stackoverflow.com",
    "title": "How to write recursive functions",
    "content": "...",
    "url": "https://..."
}
```

### 4. `brain.py` — Cognitive Engine
**Purpose**: Orchestrate memory → web → Claude pipeline.

**State Machine**:
- `idle` → `searching` → `processing` → `responding` → `learning` → `idle`

**Key Methods**:
- `ask(question, callback=None)` → start thinking in background thread
- `get_output()` → get next event from output queue (non-blocking)
- `get_stats()` → memory statistics
- `get_layout()` → node positions for visualization

**Process Flow**:
```
User asks question
  ↓
Search memory local (TF-IDF)
  ├─ score > 0.3 → use local context
  └─ score ≤ 0.3 → crawl web (SO, Wiki, GH)
  ↓
Build prompt with context
  ↓
Claude API (streaming)
  ├─ Process with system prompt (SYSTEM_PROMPT from config)
  └─ Stream response character by character
  ↓
Save to memory.json (new node)
  ↓
Emit events: state, thought, chunk, complete
```

**Threading Model**:
- Main thread: pygame loop at 60 FPS
- Background thread: `brain.ask()` runs in separate thread
- Communication: Thread-safe `queue.Queue` for events
- Non-blocking UI: `get_output()` never blocks main loop

### 5. `main.py` — Pygame UI
**Purpose**: Render neuron visualization + interactive chat.

**Layout** (1600×900):
```
LEFT PANEL (750px)              RIGHT PANEL (850px)
├─ Memory nodes network         ├─ Status panel
├─ LIF neuron (soma+dendrites)  ├─ Chat history
├─ Axon with spikes             ├─ Input box
└─ Oscilloscope                 └─ Help text
```

**Visual States**:
- **IDLE** (normal): Slow neuron oscillation, dim dendrites
- **SEARCHING** (web): Fast dendritic signals, status "BUSCANDO..."
- **PROCESSING** (Claude): Rapid soma pulsing, "PROCESANDO..."
- **RESPONDING**: Axon illuminated, text streaming, "RESPONDIENDO..."
- **LEARNING**: New nodes fade in, "APRENDIENDO..."

**Memory Node Visualization**:
- Spring-layout positioning (circular, force-directed)
- Size ∝ weight (frequently accessed = larger)
- Brightness ∝ recency (recent = brighter)
- Lines connect related nodes (minimal connection pattern)
- Max 80 nodes displayed

**Chat System**:
- Scrollable history (last 30 messages)
- User messages (">") in white
- Neurona responses ("NEURONA:") in light gray
- Input box with cursor animation
- Streaming response: character-by-character append

### 6. `config.py` — Configuration Hub
**Purpose**: Centralize all constants and settings.

**Key Configs**:
```python
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # Fast + cost-effective
MEMORY_FILE = "memory.json"
MAX_MEMORY_NODES = 500
MIN_LOCAL_SCORE = 0.3  # Threshold to search web
WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 900
LEFT_PANEL_WIDTH = 750
```

## Development Workflow

### Run the System
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Testing Individual Modules
```python
# Test memory search
from memory import Memory
m = Memory()
m.add_node("Python", "Functions...", "wikipedia")
results = m.search("Python functions")

# Test web scraping
from crawler import WebCrawler
results = WebCrawler.search_topic("recursion")

# Test brain
from brain import NeuronBrain
brain = NeuronBrain()
brain.ask("What is recursion?")
```

## Learning Flow (Example)

### First Question: "What is recursion?"
1. User types and hits ENTER
2. UI: STATUS = "BUSCANDO...", soma pulsing
3. Brain searches memory: score = 0.0 (empty)
4. Brain crawls web: finds Stack Overflow, Wikipedia
5. Shows progress: "Buscando en Stack Overflow..."
6. Claude processes with fetched content
7. Response streams character-by-character
8. New node saved: `{"topic": "recursion", "content": "...", "source": "web-search"}`
9. Node appears in network visualization

### Second Question: "Show me recursion in Python"
1. Brain searches memory: score = 0.82 (FOUND)
2. Uses local context (no web search)
3. Response is instant (no web delay)
4. Node access_count incremented
5. Node weight increased (0.85 → 0.87)

### Result
Over time, the neuron's memory grows and responses become faster for repeated topics.

## Design Constraints

1. **No Heavy ML**: Manual TF-IDF for search, no scikit-learn/spacy
2. **Visual Minimalism**: Black/white/gray only, no colors beyond extremes
3. **API-Free Scraping**: Use public APIs (Stack Overflow, Wikipedia, etc.) without auth
4. **Thread Safety**: Queue-based communication to avoid pygame freezes
5. **Streaming**: Claude response appears incrementally for immersion

## Key Implementation Details

### TF-IDF Cosine Similarity (Manual)
```python
def cosine_similarity(tf1, tf2):
    dot_product = sum(tf1.get(k,0) * tf2.get(k,0) for k in all_keys)
    mag1 = sqrt(sum(v**2 for v in tf1.values()))
    mag2 = sqrt(sum(v**2 for v in tf2.values()))
    return dot_product / (mag1 * mag2)
```

### Spring Layout for Nodes
Position nodes in circular pattern with force-directed adjustment:
```python
angle = (2 * π * i) / num_nodes
radius = 100 + 30 * node.weight
x = center_x + radius * cos(angle)
y = center_y + radius * sin(angle)
```

### LIF Equation with Adaptation
```
dI_adap/dt = -I_adap / tau_adap
dv/dt = (-(v - v_rest) + R_m * (I_excit - I_inhib - I_adap)) / tau_m
On spike: I_adap += delta_adap, then v := v_reset
```

## Performance Notes

- **Memory**: 500 nodes ≈ 5-10 MB (memory.json)
- **Search**: TF-IDF local search is O(n*m) where n=nodes, m=query terms
- **Web crawling**: ~2-5 seconds per source (Stack Overflow slowest)
- **Claude streaming**: ~100-500ms first token, then ~50-100ms per token
- **FPS**: 60 FPS maintained during brain activity (non-blocking threads)

## File Structure

```
Neurona/
├── config.py              # Centralized config (IMPORTANT: edit ANTHROPIC_API_KEY here)
├── neurona_lif.py         # LIF model (240 lines)
├── memory.py              # Vector store (200 lines)
├── crawler.py             # Web scraper (150 lines)
├── brain.py               # Claude orchestration (180 lines)
├── main.py                # Pygame UI (400+ lines)
├── memory.json            # Persisted memory (generated at runtime)
├── requirements.txt       # Dependencies
├── CLAUDE.md              # This file
└── README.md              # User documentation
```

## Future Enhancements

- [ ] Multi-neuron network with synaptic plasticity (Hebbian learning)
- [ ] Speech output via text-to-speech
- [ ] Import knowledge from URLs or PDF files
- [ ] Visualization of embedding space (if using sentence-transformers)
- [ ] Save/load conversation sessions
- [ ] Different persona modes (researcher, teacher, debugger)
- [ ] Rate limiting for Claude API costs

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
python main.py
```

### Memory file gets too large
Delete `memory.json` to reset (brain will rebuild on next session).

### Web scraping is slow
- Stack Overflow API has rate limits (try later)
- Increase `MIN_LOCAL_SCORE` in config.py to rely more on local memory
- Use `claude-haiku` model (faster) instead of other models

### Responses are incomplete or garbled
- Check Claude API quota/credits
- Reduce `max_tokens` in `brain.py` (default 1024)
- Try shorter questions

## References & Links

- **LIF Neuron**: https://en.wikipedia.org/wiki/Leaky_integrate-and-fire
- **Claude API Docs**: https://docs.anthropic.com/
- **Pygame**: https://www.pygame.org/
- **Stack Overflow API**: https://api.stackexchange.com/docs/
- **RAG Pattern**: https://huggingface.co/docs/transformers/rag/
